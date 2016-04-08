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

from pymeasure.instruments import Instrument, SerialAdapter, RangeException
from numpy import array, float64


class FWBell5080(Instrument):
    """ Represents the F.W. Bell 5080 Handheld Gaussmeter and
    provides a high-level interface for interacting with the
    instrument
    """

    def __init__(self, port):
        super(FWBell5080, self).__init__(
            SerialAdapter(port, 2400, timeout=0.5),
            "F.W. Bell 5080 Handheld Gaussmeter"
        )

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
            if value[-1] == "G":  # Field in gauss
                return (float(value[:-1]), 0)
            elif value[-1] == "T":  # Field in tesla
                return (float(value[:-1])*1e4, 0)
            elif value[-2:] == "Am":  # Field in Ampere meters
                raise Exception("Field is being measured in Ampere meters "
                                "instead of guass and measure() should not "
                                "be used")
        else:
            data = [self.measure()[0] for point in range(averages)]
            data = array(data, dtype=float64)
            return (data.mean(), data.std())

    def set_DC_gauss_units(self):
        """ Sets the meter to measure DC field in Gauss """
        self.write(":UNIT:FLUX:DC:GAUS")

    def set_DC_tesla_units(self):
        """ Sets the meter to measure DC field in Tesla """
        self.write(":UNIT:FLUX:DC:TESL")

    def set_AC_gauss_units(self):
        """ Sets the meter to measure AC field in Gauss """
        self.write(":UNIT:FLUX:AC:GAUS")

    def set_AC_tesla_units(self):
        """ Sets the meter to measure AC field in Telsa """
        self.write(":UNIT:FLUX:AC:TESL")

    def get_units(self):
        """ Returns the units being used """
        return self.ask(":UNIT:FLUX?")[:-2]

    def set_auto_range(self):
        """ Enables the auto range functionality """
        self.write(":SENS:FLUX:RANG:AUTO")

    def set_range(self, max_gauss):
        """ Manually sets the range in Gauss and truncates to
        an allowed range value
        """
        if max_gauss < 3e2:
            self.write(":SENS:FLUX:RANG 0")
        elif max_gauss < 3e3:
            self.write(":SENS:FLUX:RANG 1")
        elif max_gauss < 3e4:
            self.write(":SENS:FLUX:RANG 2")
        else:
            raise RangeException("F.W. Bell 5080 is not capable of field "
                                 "measurements above 30 kGauss")

    def get_range(self):
        """ Returns the range in Gauss """
        value = int(self.ask(":SENS:FLUX:RANG?")[:-2])
        if value == 0:
            return 3e2
        elif value == 1:
            return 3e3
        elif value == 2:
            return 3e4
