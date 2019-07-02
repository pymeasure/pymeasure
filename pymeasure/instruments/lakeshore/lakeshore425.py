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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set
from .adapters import LakeShoreUSBAdapter

from time import sleep
import numpy as np


class LakeShore425(Instrument):
    """ Represents the LakeShore 425 Gaussmeter and provides
    a high-level interface for interacting with the instrument

    To allow user access to the LakeShore 425 Gaussmeter in Linux,
    create the file:
    :code:`/etc/udev/rules.d/52-lakeshore425.rules`, with contents:

    .. code-block:: none

        SUBSYSTEMS=="usb",ATTRS{idVendor}=="1fb9",ATTRS{idProduct}=="0401",MODE="0666",SYMLINK+="lakeshore425"

    Then reload the udev rules with:

    .. code-block:: bash

        sudo udevadm control --reload-rules
        sudo udevadm trigger

    The device will be accessible through :code:`/dev/lakeshore425`.
    """

    field = Instrument.measurement(
        "RDGFIELD?",
        """ Returns the field in the current units """
    )
    unit = Instrument.control(
        "UNIT?", "UNIT %d",
        """ A string property that controls the units of the instrument,
        which can take the values of G, T, Oe, or A/m. """,
        validator=strict_discrete_set,
        values={'G':1, 'T':2, 'Oe':3, 'A/m':4},
        map_values=True
    )
    range = Instrument.control(
        "RANGE?", "RANGE %d",
        """ A floating point property that controls the field range in
        units of Gauss, which can take the values 35, 350, 3500, and
        35,000 G. """,
        validator=truncated_discrete_set,
        values={35:1, 350:2, 3500:3, 35000:4},
        map_values=True
    )

    def __init__(self, port):
        super(LakeShore425, self).__init__(
            LakeShoreUSBAdapter(port),
            "LakeShore 425 Gaussmeter",
        )
        
    def auto_range(self):
        """ Sets the field range to automatically adjust """
        self.write("AUTO")

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
