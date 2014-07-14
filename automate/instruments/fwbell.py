#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# FW Bell classes -- Gaussmeter
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate import Instrument, RangeException
from zope.interface import implementer
from numpy import array, float64

from serial import Serial
# Ensure that the Serial object gets treated as an IConnection
Serial = implementer(interfaces.IConnection)(Serial)

class FWBell5080(Instrument):
    """ Represents the F.W. Bell 5080 Handheld Gaussmeter and
    provides a high-level interface for interacting with the
    instrument    
    """
    
    def __init__(self, port):
        super(FWBell5080, self).__init__(Serial(port, 2400, timeout=0.5))

    def identify(self):
        return self.ask("*IDN?")
        
    def reset(self):
        self.write("*OPC")
    
    def measure(self, averages=1):
        """ Returns the measured field over a certain number of averages
        in Gauss and the standard deviation in the averages if measured in 
        Gauss or Tesla. Raise an exception if set in Ampere meter units.        
        """ 
        if averages == 1:
            value = self.ask(":MEAS:FLUX?")[:-2]
            if value[-1] == "G": # Field in gauss
                return (float(value[:-1]), 0)
            elif value[-1] == "T": # Field in tesla
                return (float(value[:-1])*1e4, 0)
            elif value[-2:] == "Am": # Field in Ampere meters
                raise Exception("Field is being measured in Ampere meters "
                                  "instead of guass and measure() should not "
                                  "be used")
        else:
            data = [self.measure()[0] for point in range(averages)]
            data = array(data, dtype=float64)
            return (data.mean(), data.std())
                
                              
    def setDCGaussUnits(self):
        """ Sets the meter to measure DC field in Gauss """
        self.write(":UNIT:FLUX:DC:GAUS")
        
    def setDCTeslaUnits(self):
        """ Sets the meter to measure DC field in Tesla """
        self.write(":UNIT:FLUX:DC:TESL")
        
    def setACGaussUnits(self):
        """ Sets the meter to measure AC field in Gauss """
        self.write(":UNIT:FLUX:AC:GAUS")
        
    def setACTeslaUnits(self):
        """ Sets the meter to measure AC field in Telsa """
        self.write(":UNIT:FLUX:AC:TESL")
        
    def getUnits(self):
        """ Returns the units being used """
        return self.ask(":UNIT:FLUX?")[:-2]
        
    def setAutoRange(self):
        """ Enables the auto range functionality """
        self.write(":SENS:FLUX:RANG:AUTO")
        
    def setRange(self, maxGauss):
        """ Manually sets the range in Gauss and truncates to
        an allowed range value
        """
        if maxGauss < 3e2:
            self.write(":SENS:FLUX:RANG 0")
        elif maxGauss < 3e3:
            self.write(":SENS:FLUX:RANG 1")
        elif maxGauss < 3e4:
            self.write(":SENS:FLUX:RANG 2")
        else:
            raise RangeException("F.W. Bell 5080 is not capable of field "
                                  "measurements above 30 kGauss")
                                  
    def getRange(self):
        """ Returns the range in Gauss """
        value = int(self.ask(":SENS:FLUX:RANG?")[:-2])
        if value == 0:
            return 3e2
        elif value == 1:
            return 3e3
        elif value == 2:
            return 3e4
            
        
        
