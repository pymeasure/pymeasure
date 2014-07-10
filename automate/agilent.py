# Agilent Instrument Classes
#
# Authors: Colin Jermain
# Copyright: 2012 Cornell University
#

from automate.gpib import GPIBInstrument
from automate import RangeException, discreteTruncate

class Agilent8722ES(GPIBInstrument):
    """ Represents the Agilent8722ES Vector Network Analyzer
    and provides a high-level interface for taking scans of the
    scattering parameters.   
    """

    def __init__(self, adapter, address):
        super(Agilent8722ES, self).__init__(adapter, address)
    
    def setFixedFrequency(self, frequency):
        """ Sets the scan to be of only one frequency in Hz """
        self.setStartFrequency(frequency)
        self.setStopFrequency(frequency)
        self.setScanPoints(3)
        
    def setScatteringParameter(self, element):
        """" Sets which scattering parameter to be measured based on the
        matrix element notation
        """
        if element == "11":
            self.write("S11")
        elif element == "12":
            self.write("S12")
        elif element == "21":
            self.write("S21")
        elif element == "22":
            self.write("S22")
        else:
            raise Exception("Invalid matrix element provided for Agilent 8722ES"
                            " scattering parameter")
        
    def setScanPoints(self, points):
        """ Sets the number of scan points, truncating to an allowed
        value if not properly provided       
        """
        allowedPoints = [3, 11, 21, 26, 51, 101, 201, 401, 801, 1601]
        points = discreteTruncate(points, allowedPoints)
        if points:
            self.write("POIN%d" % points)
        else:
            raise RangeException("Maximum scan points (1601) for Agilent 8722ES"
                                 " exceeded")
                                 
    def setSweepTime(self, time):
        """ Sets the time over which the scan takes place in seconds """
        self.write("SWET%.2e" % time)
                                 
    def setStartFrequency(self, frequency):
        """ Sets the start frequency for the scan in Hz """
        self.write("STAR%.3e" % frequency)
        
    def setStopFrequency(self, frequency):
        """ Sets the stop frequency for the scan in Hz """
        self.write("STOP%.3e" % frequency)        
                                 
    def setIFBandwidth(self, bandwidth):
        """ Sets the resolution bandwidth (IF bandwidth) """
        allowedBandwidth = [10, 30, 100, 300, 1000, 3000, 3700, 6000]
        bandwidth = discreteTruncate(bandwidth, allowedBandwidth)
        if bandwidth:
            self.write("IFBW%d" % bandwidth)
        else:
            raise RangeException("Maximum IF bandwidth (6000) for Agilent "
                                 "8722ES exceeded")
    
    def setAveraging(self, averages):
        """ Turns on averaging of a specific number between 0 and 999        
        """
        if int(averages) > 999 or int(averages) < 0:
            raise RangeException("Averaging must be in the range 0 to 999")
        else:
            self.write("AVERO1")
            self.write("AVERFACT%d" % int(averages))
            
    def disableAveraging(self):
        """ Disables averaging """
        self.write("AVERO0")
        
    def isAveraging(self):
        """ Returns True if averaging is enabled """
        return self.ask("AVERO?") == '1\n'
            
    def restartAveraging(self, averages):
        if int(averages) > 999 or int(averages) < 0:
            raise RangeException("Averaging must be in the range 0 to 999")
        else:
            self.write("NUMG%d" % averages)
            
    def scan(self, averages=1, blocking=True, timeout=0.1, abortEvent=None):
        """ Initiates a scan with the number of averages specified and
        blocks until the operation is complete if blocking is True
        """
        if averages == 1:
            self.disableAveraging()
            self.setSingleSweep()
        else:
            self.setAveraging(averages)
            self.restartAveraging(averages)
            if blocking:
                self.waitForScan(abortEvent)
    
    def scanSingle(self):
        """ Initiates a single scan """
        self.write("SING")
        
    def scanContinuous(self):
        """ Initiates a continuous scan """
        self.write("CONT")
        
    def waitForScan(self, timeout=0.1, abortEvent=None):
        """ Blocks until the scan returns a operation complete signal
        or an abort event is set        
        """
        from time import sleep
        while not abortEvent.isSet() and self.ask("OPC?") != '1\n':
            sleep(timeout)
        
    def getData(self):
        """ Returns the real and imaginary data from the last scan        
        """
        import numpy as np
        data = self.ask("FORM4;OUTPDATA")[2:-2].split("\n\n  ")
        real = np.zeros(len(data), np.float64)
        imag = np.zeros(len(data), np.float64)
        for i, point in enumerate(data):
            pair = point.split(",  ", 1)
            real[i] = float(pair[0])
            imag[i] = float(pair[1])
        return real, imag
        


class AgilentE8257D(GPIBInstrument):
    """ Represents the Agilent E8257D PSG Signal Generator and
    provides a high-level interface for interacting with the
    instrument    
    """

    def __init__(self, adapter, address):
        super(AgilentE8257D, self).__init__(adapter, address)
        
    def enable(self):
        """ Enables the RF output """
        self.write(":OUTP:STAT ON")
        
    def disable(self):
        """ Disables the RF output """
        self.write(":OUTP:STAT OFF")
        
    def isEnabled(self):
        """ Returns True if the RF output is enabled """
        return int(self.ask(":OUTP:STAT?")) is 1
    
    def setPower(self, power):
        """ Sets the output power in dBm """
        self.write(":SOUR:POW:LEV:IMM:AMPL %eDBM" % power)
        
    def setFrequency(self, frequency):
        """ Sets the frequency in Hz """
        self.write(":SOUR:FREQ:CW %e" % frequency)
        
    def getFrequency(self):
        """ Returns the set frequency in Hz """
        return float(self.ask(":SOUR:FREQ:CW?"))
        
    def setCenterFrequency(self, frequency):
        """ Sets the center frequency in Hz """
        self.write(":SOUR:FREQ:CENT %e" % frequency)
        
    def getCenterFrequency(self):
        """ Returns the set center frequency in Hz """
        return float(self.ask(":SOUR:FREQ:CENT?"))
        
    def setStepSweep(self):
        """ Sets up for a step sweep through frequency """
        self.write(":SOUR:FREQ:MODE SWE;:SOUR:SWE:GEN STEP;:SOUR:SWE:MODE AUTO;")
        
    def setRetrace(self, enable=True):
        self.write(":SOUR:LIST:RETR %d" % enable)
        
    def singleSweep(self):
        self.write(":SOUR:TSW")
        
    def setStartFrequency(self, frequency):
        """ Sets the start frequency in Hz of the sweep """
        self.write(":SOUR:FREQ:STAR %eHZ" % frequency)
        
    def getStartFrequency(self):
        """ Returns the start frequency in Hz """
        return float(self.ask(":SOUR:FREQ:STAR?"))
        
    def setStopFrequency(self, frequency):
        """ Sets the stop frequency in Hz of the sweep """
        self.write(":SOUR:FREQ:STOP %eHZ" % frequency)
            
    def getStopFrequency(self):
        """ Returns the stop frequency in Hz of the sweep """
        return float(self.ask(":SOUR:FREQ:STOP?"))
        
    def setStartPower(self, power):
        """ Sets the start power in dBm of the sweep """
        self.write(":SOUR:POW:STAR %eDBM" % power)
        
    def getStartPower(self):
        """ Returns the start power in dBm of the sweep """
        return float(self.ask(":SOUR:POW:STAR?"))
        
    def setStopPower(self, power):
        """ Sets the stop power in dBm of the sweep """
        self.write(":SOUR:POW:STOP %eDBM" % power)
        
    def getStopPower(self):
        """ Returns the stop power in dBm of the sweep """
        return float(self.ask(":SOUR:POW:STOP?"))
        
    def setDwellTime(self, time):
        """ Sets the time in seconds between each step point """
        self.write(":SOUR:SWE:DWEL1 %.3f" % time)
    
    def getDwellTime(self):
        """ Returns the time in seconds between each step point """
        return float(self.ask(":SOUR:SWE:DWEL1?"))
        
    def startStepSweep(self):
        """ Initiates a step sweep """
        self.write(":SOUR:SWE:CONT:STAT ON")
        
    def stopStepSweep(self):
        """ Stops a step sweep """
        self.write(":SOUR:SWE:CONT:STAT OFF")
        
    def isStepSweeping(self):
        """ Returns True if a step sweep is currently in progress """
        return int(self.ask("SOUR:SWE:CONT:STAT?")) is 1
        
    def setStepPoints(self, points):
        """ Sets the number of points in the step sweep """
        self.write(":SOUR:SWE:POIN %d" % points)
        
    def getStepPoints(self):
        """ Returns the number of points in the step sweep """
        return int(self.ask(":SOUR:SWE:POIN?"))
        
    def setAmplitudeDepth(self, depth):
        """ Sets the depth of amplitude modulation which corresponds
        to the precentage of the signal modulated to
        """
        if depth > 0 and depth <= 100:
            self.write(":SOUR:AM %d" % depth)
        else:
            raise RangeException("Agilent E8257D amplitude modulation out of range")
            
    def setAmplitudeSource(self, source='INT'):
        """ Sets the source of the trigger for amplitude modulation """
        self.write(":SOUR:AM:SOUR %s" % source)
        
    def setAmplitudeModulation(self, enable=True):
        """ Enables (True) or disables (False) the amplitude modulation """
        self.write(":SOUR:AM:STAT %d" % enable)
        
