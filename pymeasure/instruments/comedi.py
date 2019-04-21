#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.experiment import Procedure, Parameter, FloatParameter, IntegerParameter
import numpy as np
from time import time, sleep
from threading import Event
from importlib.util import find_spec

if find_spec('pycomedi'):  # Guard against pycomedi not being installed
    from pycomedi.subdevice import StreamingSubdevice
    from pycomedi.constant import *
    from pycomedi.constant import _NamedInt
    from pycomedi.channel import AnalogChannel
    from pycomedi.utility import inttrig_insn, Reader, CallbackReader


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


class SynchronousAI(object):
        
    def __init__(self, channels, period, samples): 
        self.channels = channels
        self.samples = samples
        self.period = period
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
        
    def measure(self, hasAborted=lambda:False):
        """ Initiates the scan after first checking the command
        and does not block, returns the starting timestamp
        """
        self._verifyCommand()
        sleep(0.01)
        self.subdevice.command()
        
        length = len(self.channels)
        dtype = self.subdevice.get_dtype()
        converters = [c.get_converter() for c in self.channels]

        self.data = np.zeros((self.samples, length), dtype=np.float32)

        # Trigger AI
        self.subdevice.device.do_insn(inttrig_insn(self.subdevice))
                
        # Measurement loop
        count = 0
        size = int(self.data.itemsize/2)*length
        previous_bin_slice = b''
        
        while not hasAborted() and self.samples > count:
            bin_slice = previous_bin_slice
            while len(bin_slice) < size:
                bin_slice += self.subdevice.device.file.read(size)
            previous_bin_slice = bin_slice[size:]
            bin_slice = bin_slice[:size]
            slice = np.fromstring(
                bin_slice,
                dtype=dtype,
                count=length
            )

            if len(slice) != length: # Reading finished
                break

            # Convert to physical values
            for i, c in enumerate(converters):
                self.data[count,i] = c.to_physical(slice[i])
            
            self.emit_progress(100.*count/self.samples)
            self.emit_data(self.data[count])
            count += 1
            
        # Cancel measurement if it is still running (abort event)
        if self.subdevice.get_flags().running:             
            self.subdevice.cancel()
                                

""" Command for limited samples

command = self.subdevice.get_cmd_generic_timed(len(self.channels), 
                self.scanPeriod)
command.start_src = TRIG_SRC.int
command.start_arg = 0
command.stop_src = TRIG_SRC.count
command.stop_arg = self.samples
command.chanlist = self.channels

    Command for continuous AI

command = self.subdevice.get_cmd_generic_timed(len(self.channels), self.scanPeriod)
command.start_src = TRIG_SRC.int
command.start_arg = 0
command.stop_src = TRIG_SRC.none
command.stop_arg = 0
command.chanlist = self.channels
"""
