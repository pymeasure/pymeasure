#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

from pymeasure.instruments import Instrument, RangeException


class Sprout(Instrument):
    """Represents Lighthouse Photonics Sprout G12W laser"""

    # version = Instrument.measurement("VERSION?", 'Software Version')
    # serialnumber = Instrument.measurement("SERIALNUMBER?", 'Laser Serial Number ')
    # shutter = Instrument.measurement('SHUTTER?', 'Shutter Status')
    # warning = Instrument.measurement('WARNING?', 'Warning Messages')
    # interlock = Instrument.measurement('INTERLOCK?', 'Interlock Messages')

    op_mode = Instrument.control(
        "OPMODE?", "OPMODE=%s",
        """
        A string property that controls the operation mode of
        the laser. Strings allowed 'ON','OFF','IDLE','CALIBRATE'.
        Remember to open shutter for laser on.
        It takes 3-5 minutes for laser to turn on.
        e.g. Laser on `OPMODE=ON`, Laser off `OPMODE=OFF`.
        """
    )

    power = Instrument.control(
        "POWER?", "POWER SET=%.2g",
        """
        A float property that controls the laser power output.
        e.g. `my_instr.power=1.0` sets laser to 1.0 W.
        Remember to open shutter for laser on.
        It takes 3-5 minutes for laser to turn on.
        e.g. Laser on `OPMODE=ON`, Laser off `OPMODE=OFF`.
        """
    )

    def __init__(self, adapter, **kwargs):
        super(Sprout, self).__init__(
            adapter, "SproutG12W 532 nm laser", **kwargs)
        self.timout = 3000
        # self.sensor()

    def sensor(self):
        "Get laser info"
        self.version = self.ask('VERSION?').split('=')
        self.ser_num = self.ask('SERIALNUMBER?').split('=')
        self.shutter = self.ask('SHUTTER?').split('=')
        self.warning = self.ask('WARNING?').split('=')
        self.interlock = self.ask('INTERLOCK?').split('=')
        # self.power = self.ask('POWER?').split('=')
        # self.op_mode = self.ask('OPMODE?').split('=')

