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

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_discrete_set
from pymeasure.adapters import SerialAdapter
from numpy import array, float64


class FWBell5080(Instrument):
    """ Represents the F.W. Bell 5080 Handheld Gaussmeter and
    provides a high-level interface for interacting with the
    instrument

    :param port: The serial port of the instrument
    """

    id = Instrument.measurement(
        "*IDN?", """ Reads the idenfitication information. """
    )
    units = Instrument.measurement(
        ":UNIT:FLUX?",
        """ Reads the units being used
        """
    )
    range = Instrument.control(
        ":SENS:FLUX:RANG?", ":SENS:FLUX:RANG %d",
        """ A floating point property that controls the maximum field
        range in Gauss, which can take the values 300, 3,000, and 
        30,000 G. Values outside these are truncated to the closest
        valid value. This property can be set. """,
        validator=truncated_discrete_set,
        values={300:0, 3000:1, 30000:2},
        map_values=True
    )

    def __init__(self, port):
        super(FWBell5080, self).__init__(
            SerialAdapter(port, 2400, timeout=0.5),
            "F.W. Bell 5080 Handheld Gaussmeter"
        )

    def read(self):
        """ Overwrites the standard read method to remove the last
        2 characters from the output
        """
        return super(FWBell5080, self).read()[:-2]

    def ask(self):
        """ Overwrites the standard ask method to remove the last
        2 characters from the output
        """
        return super(FWBell5080, self).ask()[:-2]

    def reset(self):
        """ Resets the instrument.
        """
        self.write("*OPC")

    def measure(self, averages=1):
        """ Returns the measured field over a certain number of averages
        in Gauss and the standard deviation in the averages if measured in
        Gauss or Tesla. Raise an exception if set in Ampere meter units.

        :param averages: The number of averages to preform
        """
        if averages == 1:
            value = self.ask(":MEAS:FLUX?")
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

    def use_DC_gauss(self):
        """ Sets the meter to measure DC fields in Gauss. """
        self.write(":UNIT:FLUX:DC:GAUS")

    def use_AC_gauss(self):
        """ Sets the meter to measure AC fields in Gauss. """
        self.write(":UNIT:FLUX:AC:GAUS")

    def use_DC_tesla(self):
        """ Sets the meter to measure DC fields in Tesla. """
        self.write(":UNIT:FLUX:DC:TESL")

    def use_AC_tesla(self):
        """ Sets the meter to measure AC fields in Tesla. """
        self.write(":UNIT:FLUX:AC:TESL")

    def auto_range(self):
        """ Enables the auto range functionality. """
        self.write(":SENS:FLUX:RANG:AUTO")
