#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Lakeshore classes -- Gaussmeter
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate.instruments import Instrument, SerialAdapter, RangeException
from time import sleep
import numpy as np

class LakeShoreUSBAdapter(SerialAdapter):
    
    def __init__(self, port):
        super(LakeShoreUSBAdapter, self).__init__(port, 
            baudrate=57600, 
            timeout=0.5, 
            parity='O', 
            bytesize=7
        )
        
    def write(self, command):
        self.connection.write(command + "\n")


class LakeShore425(Instrument):
    """ Represents the LakeShore 425 Gaussmeter and provides
    a high-level interface for interacting with the instrument
    
    To allow user access to the LakeShore 425 Gaussmeter in Linux, create the file:
    /etc/udev/rules.d/52-lakeshore425.rules, with contents:    
    
    SUBSYSTEMS=="usb",ATTRS{idVendor}=="1fb9",ATTRS{idProduct}=="0401",MODE="0666",SYMLINK+="lakeshore425"
        
    Then reload the udev rules with:
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    The device will be accessible through /dev/lakeshore425 
    
    """

    UNIT_VALUES = ('Gauss', 'Tesla', 'Oersted', 'Ampere/meter')
    GAUSS, TESLA, OERSTED, AMP_METER = UNIT_VALUES
    
    def __init__(self, port):
        super(LakeShore425, self).__init__(
            LakeShoreUSBAdapter(port),
            "LakeShore 425 Gaussmeter",
        )
        self.add_control("range", "RANGE?", "RANGE %d")
        
    def setAutoRange(self):
        """ Sets the field range to automatically adjust """
        self.write("AUTO")
        
    @property
    def field(self):
        """ Returns the field given the units being used """
        return self.values("RDGFIELD?")
        
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
            
    @property
    def unit(self):
        """ Returns the full name of the unit in use as a string """
        return LakeShore425.UNIT_VALUES[int(self.ask("UNIT?"))-1]
    @unit.setter
    def unit(self, value):
        """ Sets the units from the avalible: Gauss, Tesla, Oersted, and
        Ampere/meter to be called as a string
        """
        if value in LakeShore425.UNIT_VALUES:
            self.write("UNIT %d" % (LakeShore425.UNIT_VALUES.index(value)+1))
        else:
            raise Exception("Invalid unit provided to LakeShore 425")
        
    def zeroProbe(self):
        """ Initiates the zero field sequence to calibrate the probe """
        self.write("ZPROBE")
        
    def measure(self, points, hasAborted=lambda:False, delay=1e-3):
        """Returns the mean and standard deviation of a given number
        of points while blocking
        """
        data = np.zeros(points, dtype=np.float32)
        for i in range(points):
            if hasAborted():
                break
            data[i] = self.field
            sleep(delay)
        return data.mean(), data.std()

