#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from .adapters import LakeShoreUSBAdapter

from time import sleep
import numpy as np


class LakeShore425(Instrument):
    """ Represents the LakeShore 425 Gaussmeter and provides
    a high-level interface for interacting with the instrument

    To allow user access to the LakeShore 425 Gaussmeter in Linux,
    create the file:
    /etc/udev/rules.d/52-lakeshore425.rules, with contents:

    SUBSYSTEMS=="usb",ATTRS{idVendor}=="1fb9",ATTRS{idProduct}=="0401",MODE="0666",SYMLINK+="lakeshore425"

    Then reload the udev rules with:
    sudo udevadm control --reload-rules
    sudo udevadm trigger

    The device will be accessible through /dev/lakeshore425
    """

    UNIT_VALUES = ('Gauss', 'Tesla', 'Oersted', 'Ampere/meter')
    GAUSS, TESLA, OERSTED, AMP_METER = UNIT_VALUES
    RANGES_HSE = ('35G', '350G', '3.5kG', '35kG')

    def __init__(self, port):
        super(LakeShore425, self).__init__(
            LakeShoreUSBAdapter(port),
            "LakeShore 425 Gaussmeter",
        )
        #self.add_control("range", "RANGE?", "RANGE %d")
        
    @property
    def range(self):
        """ Get the current range."""
        range_id = int(self.values("RANGE?")[0])
        return LakeShore425.RANGES_HSE[range_id - 1]

    @range.setter
    def range(self, maxvalue):
        """ Set an appropriate range.
        
        :param maxvalue: Maximum limit of input field, in Gauss.
        """
        range_id = 0
        while maxvalue > 35*(10**range_id):
            range_id += 1
        self.write("RANGE %d" % (range_id+1) )
        
    def auto_range(self):
        """ Sets the field range to automatically adjust """
        self.write("AUTO")

    @property
    def field(self):
        """ Returns the field given the units being used """
        return self.values("RDGFIELD?")[0]

    def dc_mode(self, wideband=True):
        """ Sets up a steady-state (DC) measurement of the field """
        if wideband:
            self.mode = (1, 0, 1)
        else:
            self.mode(1, 0, 2)

    def ac_mode(self, wideband=True):
        """ Sets up a measurement of an oscillating (AC) field """
        if wideband:
            self.mode = (2, 1, 1)
        else:
            self.mode = (2, 1, 2)

    @property
    def mode(self):
        return tuple(self.values("RDGMODE?"))

    @mode.setter
    def mode(self, value):
        """ Provides access to directly setting the mode, filter, and
        bandwidth settings
        """
        mode, filter, band = value
        self.write("RDGMODE %d,%d,%d" % (mode, filter, band))

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

    def zero_probe(self):
        """ Initiates the zero field sequence to calibrate the probe """
        self.write("ZPROBE")

    def measure(self, points, has_aborted=lambda: False, delay=1e-3):
        """Returns the mean and standard deviation of a given number
        of points while blocking
        """
        data = np.zeros(points, dtype=np.float32)
        for i in range(points):
            if has_aborted():
                break
            data[i] = self.field
            sleep(delay)
        return data.mean(), data.std()
