from pycomedi.subdevice import StreamingSubdevice
from pycomedi.constant import *
from pycomedi.constant import _NamedInt
from pycomedi.channel import AnalogChannel
from pycomedi.utility import inttrig_insn, Reader, CallbackReader
import numpy as np
from time import time
from PyQt4.QtCore import QThread, pyqtSignal
from threading import Event

def getAI(device, channel, range=None):
    """ Returns the analog input channel as specified for a given device    
    """
    ai = device.find_subdevice_by_type(
                SUBDEVICE_TYPE.ai, factory=StreamingSubdevice
           ).channel(channel, factory=AnalogChannel, aref=AREF.diff)
    if range is not None:
        ai.range = ai.find_range(unit=UNIT.volt, min=range[0], max=range[1])
    return ai
        
def getAO(device, channel, range=None):
    """ Returns the analog output channel as specified for a given device    
    """
    ao = device.find_subdevice_by_type(
                SUBDEVICE_TYPE.ao, factory=StreamingSubdevice
           ).channel(channel, factory=AnalogChannel, aref=AREF.diff)
    if range is not None:
        ao.range = ao.find_range(unit=UNIT.volt, min=range[0], max=range[1])
    return ao
    
def readAI(device, channel, range=None, count=1):
    """ Reads a single measurement (count==1) from the analog input channel 
    of the device specified. Multiple readings can be preformed with count
    not equal to one, which are seperated by an arbitrary time   
    """
    ai = getAI(device, channel, range)
    converter = ai.get_converter()
    if count is 1:
        return converter.to_physical(ai.data_read())
    else:
        return converter.to_physical(ai.data_read_n(count))
    
def writeAO(device, channel, voltage, range=None):
    """ Writes a single voltage to the analog output channel of the
    device specified    
    """
    ao = getAO(device, channel, range)
    converter = ao.get_converter()
    ao.data_write(converter.from_physical(voltage))
    

class SignalAI(QThread):
    
    data = pyqtSignal(np.ndarray)
    progress = pyqtSignal(float)
    
    def __init__(self, channels, period, samples):
        QThread.__init__(self)
        self.alive = Event()
        self.alive.set()    
        self.channels = channels
        self.samples = samples
        self.period = period
        self.scanPeriod = int(1e9*float(period)/float(samples)) # nano-seconds
        
        self.subdevice = self.channels[0].subdevice
        self.subdevice.cmd = self._command()

    def isAlive(self):
        """ Returns True if the measurement thread is alive """
        return self.alive.isSet()
        
    def isBuffering(self):
        """ Returns True if the measurement is running
        """
        return self.subdevice.get_flags().running
        
    def abort(self, delay=100):
        """ Aborts the execution of the thread and waits for a specific
        time in milliseconds for the procedure to catch the abort and finish
        """
        if delay < 0:
            raise ValueError("MeasurementThread abort delay time must be "
                             "positive")
        self.alive.clear()        
        if self.isBuffering():
            self.subdevice.cancel()
        self.wait(int(delay))
    
    def _command(self):
        """ Returns the command used to initiate and end the sampling
        """
        command = self.subdevice.get_cmd_generic_timed(len(self.channels), 
                        self.scanPeriod)
        command.start_src = TRIG_SRC.int
        command.start_arg = 0
        command.stop_src = TRIG_SRC.count
        command.stop_arg = self.samples
        command.chanlist = self.channels
        # Adding to remove chunk transfers (TRIG_WAKE_EOS)
        wake_eos = _NamedInt('wake_eos', 32)
        if wake_eos not in CMDF:
            CMDF.append(wake_eos)
        command.flags = CMDF.wake_eos
        return command
    
    def _verifyCommand(self):
        """ Checks the command over three times and allows comedi to correct
        the command given any device specific conflicts       
        """
        for i in range(3):
            rc = self.subdevice.command_test() # Verify command is correct
            if rc == None: break
        
    def run(self):
        """ Initiates the scan after first checking the command
        and does not block, returns the starting timestamp
        """
        self._verifyCommand()  
        self.subdevice.command()
        
        length = len(self.channels)
        dtype = self.subdevice.get_dtype()
        converters = [c.get_converter() for c in self.channels]

        self.physical = np.zeros((self.samples, length), dtype=np.float32)

        # Trigger AI
        self.subdevice.device.do_insn(inttrig_insn(self.subdevice))
                
        # Measurement loop
        count = 0
        while self.isAlive() and self.samples > count:
            slice = np.fromfile(
                        self.subdevice.device.file, 
                        dtype=dtype,
                        count=length
                    )
            if len(slice) != length: # Reading finished
                break
                                
            # Convert to physical values
            for i, c in enumerate(converters):
                self.physical[count,i] = c.to_physical(slice[i])
            
            self.progress.emit(100.*count/self.samples)                
            self.data.emit(self.physical[count])
            count += 1
                                 
        
    
class SynchronousAI(object):
    """ Encapsulates the synchronous measurement of multiple analog
    channels over a certain period and number of samples
    """
    
    def __init__(self, channels, period, samples, callback=None):
        """ Constructs the SynchronousAI object by taking a list of
        channel objects with the desired ranges set, the period of the
        total scan, and the number of samples
        """
        self.reader = None
        self.callback = callback
        self.channels = channels
        self.period = period
        self.samples = samples
        self.scanPeriod = int(1e9*float(period)/float(samples)) # nano-seconds
        
        self.subdevice = self.channels[0].subdevice
        self.subdevice.cmd = self._command()
    
    def _command(self):
        """ Returns the command used to initiate and end the sampling
        """
        command = self.subdevice.get_cmd_generic_timed(len(self.channels), 
                        self.scanPeriod)
        command.start_src = TRIG_SRC.int
        command.start_arg = 0
        command.stop_src = TRIG_SRC.count
        command.stop_arg = self.samples
        command.chanlist = self.channels
        return command
    
    def _verifyCommand(self):
        """ Checks the command over three times and allows comedi to correct
        the command given any device specific conflicts       
        """
        for i in range(3):
            rc = self.subdevice.command_test() # Verify command is correct
            if rc == None: break
        
    def start(self):
        """ Initiates the scan after first checking the command
        and does not block, returns the starting timestamp
        """
        self._verifyCommand()  
        self.subdevice.command()         
        self.buffer = np.zeros((self.samples, len(self.channels)), 
                                dtype=self.subdevice.get_dtype())
        self.reader = Reader(self.subdevice, self.buffer)
        self.reader.start()
        # Trigger AI
        self.subdevice.device.do_insn(inttrig_insn(self.subdevice))
        self.startTime = time()
        return self.startTime
        
    def wait(self):
        """ Blocks until the data is read completely
        """
        if self.reader is None:
            raise Exception("Wait method can only be called after sampling has "
                            " started")
        else:
            self.reader.join()
    
    def data(self):
        """ Returns the measured data in volts in the channel order
        as specified during construction
        """
        if self.reader is not None and not self.isRunning():
            data = np.zeros(self.buffer.shape, dtype=np.float32)
            for i, c in enumerate([c.get_converter() for c in self.channels]):
                data[:,i] = c.to_physical(self.buffer[:,i])
            return data
        
    def isRunning(self):
        """ Returns True if the measurement is running
        """
        return self.subdevice.get_flags().running
        
    def progress(self):
        """ Returns the precent finished by keeping track of time,
        where 1. is 100%
        """
        elapsed = time() - self.startTime
        if self.period > elapsed:
            return elapsed/self.period
        else:
            return 1.
        
    def abort(self):
        """ Aborts a current running measurement
        """
        if self.isRunning():
            self.subdevice.cancel()
        else:
            raise Exception("Can not abort AI measurements when they are not "
                            "running")
        
class ContinousAI(SynchronousAI):
    """ Extends the SynchronousAI class to allow continous sampling with
    a callback function for receiving the data
    """
    
    def __init__(self, channels, frequency, callback):
        """ Constructs the SynchronousAI object by taking a list of
        channel objects with the desired ranges set, the frequency of the sampling
        and the callback function to be called with the data
        """
        super(ContinousAI, self).__init__(channels, 1./frequency, 1)
    
    def _command(self):
        """ Overwrites the SynchronousIO command, so that continous sampling
        occurs
        """
        command = self.subdevice.get_cmd_generic_timed(len(self.channels), self.scanPeriod)
        command.start_src = TRIG_SRC.int
        command.start_arg = 0
        command.stop_src = TRIG_SRC.none
        command.stop_arg = 0
        command.chanlist = self.channels
        return command
        
    def start(self):
        """ Initiates the scan after first checking the command
        and does not block
        """
        self._verifyCommand()
        self.subdevice.command()
        self.buffer = np.zeros((len(self.channels),), 
                                dtype=self.subdevice.get_dtype())
        sleep(0.01)
        self.reader = CallbackReader(subdevice=self.subdevice, buffer=self.buffer,
                                callback=self.callback, count=self.buffer.shape[0])
        self.reader.start()
        # Trigger AI
        self.subdevice.device.do_insn(inttrig_insn(self.subdevice))
        self.startTime = time()
        return self.startTime
        
    def progress(self):
        """ Overwrites the SynchronousAI method to return 0, as the sampling
        has no defined endpoint
        """
        return 0
        
    def data(self):
        """ Overwrites the SynchronousAI method to return None, as a callback
        should be used for continous sampling
        """
        return None
