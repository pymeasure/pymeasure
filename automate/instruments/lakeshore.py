#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Lakeshore classes -- Gaussmeter
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate import interfaces, Instrument, RangeException
from zope.interface import implementer
from serial import Serial
from time import sleep
import numpy as np

# Ensure that the Serial object gets treated as an IConnection
Serial = implementer(interfaces.IConnection)(Serial)

class LakeShore425(Instrument):
    """ Represents the LakeShore 425 Gaussmeter and provides
    a high-level interface for interacting with the instrument    
    """

    units = ['Gauss', 'Tesla', 'Oersted', 'Ampere/meter']
    
    def __init__(self, port):
        super(LakeShore425, self).__init__(Serial(port, 57600, timeout=0.5, parity='O', bytesize=7))

    def write(self, command):
        """ Write a command ensuring proper line termination """
        self.connection.write(command + "\n")

    def identify(self):
        return self.ask("*IDN?")
        
    def setAutoRange(self):
        """ Sets the field range to automatically adjust """
        self.write("AUTO")
        
    def setRange(self, range):
        """ Sets the range based on the manual values """
        self.write("RANGE %d" % range)
        
    def getRange(self):
        """ Returns the range given the units being used """
        return self.ask("RANGE?")
        
    def getField(self):
        """ Returns the field given the units being used """
        return float(self.ask("RDGFIELD?"))
        
    def setDC(self, wideBand=True):
        """ Sets up a steady-state (DC) measurement of the field """
        if wideBand:
            self.setMode(1, 0, 1)
        else:
            self.setMode(1, 0, 2)
    
    def setAC(self, wideBand=True):
        """ Sets up a measurement of an oscillating (AC) field """
        if wideBand:
            self.setMode(2, 1, 1)
        else:
            self.setMode(2, 1, 2)
            
    def setMode(self, mode, filter, band):
        """ Provides access to directly setting the mode, filter, and
        bandwidth settings
        """
        self.write("RDGMODE %d,%d,%d" % (mode, filter, band))
            
    def getMode(self):
        """ Returns a tuple of the mode settings """
        return tuple(self.ask("RDGMODE?").split(','))
        
    def setUnit(self, unit):
        """ Sets the units from the avalible: Gauss, Tesla, Oersted, and
        Ampere/meter to be called as a string
        """
        assert unit in self.units
        self.write("UNIT %d" % (self.units.index(unit)+1))
        
    def getUnit(self):
        """ Returns the full name of the unit in use as a string """
        return self.units[int(self.ask("UNIT?"))]
        
    def zeroProbe(self):
        """ Initiates the zero field sequence to calibrate the probe """
        self.write("ZPROBE")
        
    def measure(self, points, abortEvent=None, delay=1e-3):
        """Returns the mean and standard deviation of a given number
        of points while blocking
        """
        data = np.zeros(points, dtype=np.float32)
        for i in range(points):
            if abortEvent is not None:
                if abortEvent.isSet():
                    break
            data[i] = self.getField()
            sleep(delay)
        return data.mean(), data.std()

