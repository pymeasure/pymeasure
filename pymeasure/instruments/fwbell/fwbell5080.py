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

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_discrete_set, strict_discrete_set
from pymeasure.adapters import SerialAdapter
from numpy import array, float64


class FWBell5080(Instrument):
    """ Represents the F.W. Bell 5080 Handheld Gaussmeter and
    provides a high-level interface for interacting with the
    instrument

    :param port: The serial port of the instrument

    .. code-block:: python

        meter = FWBell5080('/dev/ttyUSB0')      # Connects over serial port /dev/ttyUSB0 (Linux)

        meter.units = 'gauss'                   # Sets the measurement units to Gauss
        meter.range = 3e3                       # Sets the range to 3 kG
        print(meter.field)                      # Reads and prints a field measurement in G

        fields = meter.fields(100)              # Samples 100 field measurements
        print(fields.mean(), fields.std())      # Prints the mean and standard deviation of the samples

    """

    id = Instrument.measurement(
        "*IDN?", """ Reads the idenfitication information. """
    )
    field = Instrument.measurement(
        ":MEAS:FLUX?",
        """ Reads a floating point value of the field in the appropriate units.
        """,
        get_process=lambda v: v.split(' ')[0] # Remove units
    )
    UNITS = {
        'gauss':'DC:GAUSS', 'gauss ac':'AC:GAUSS',
        'tesla':'DC:TESLA', 'tesla ac':'AC:TESLA',
        'amp-meter':'DC:AM', 'amp-meter ac':'AC:AM'
    }
    units = Instrument.control(
        ":UNIT:FLUX?", ":UNIT:FLUX%s",
        """ A string property that controls the field units, which can take the
        values: 'gauss', 'gauss ac', 'tesla', 'tesla ac', 'amp-meter', and
        'amp-meter ac'. The AC versions configure the instrument to measure AC.
        """,
        validator=strict_discrete_set,
        values=UNITS,
        map_values=True,
        get_process=lambda v: v.replace(' ', ':') # Make output consistent with input
    )

    def __init__(self, port):
        super(FWBell5080, self).__init__(
            SerialAdapter(port, 2400, timeout=0.5),
            "F.W. Bell 5080 Handheld Gaussmeter"
        )

    @property
    def range(self):
        """ A floating point property that controls the maximum field
        range in the active units. This can take the values of 300 G,
        3 kG, and 30 kG for Gauss, 30 mT, 300 mT, and 3 T for Tesla,
        and 23.88 kAm, 238.8 kAm, and 2388 kAm for Amp-meter. """
        i = self.values(":SENS:FLUX:RANG?", cast=int)
        units = self.units
        if 'gauss' in self.units:
            return [300, 3e3, 30e3][i]
        elif 'tesla' in self.units:
            return [30e-3, 300e-3, 3][i]
        elif 'amp-meter' in self.units:
            return [23.88e3, 238.8e3, 2388e3][i]

    @range.setter
    def range(self, value):
        units = self.units
        if 'gauss' in self.units:
            i = truncated_discrete_set(value, [300, 3e3, 30e3])
        elif 'tesla' in self.units:
            i = truncated_discrete_set(value, [30e-3, 300e-3, 3])
        elif 'amp-meter' in self.units:
            i = truncated_discrete_set(value, [23.88e3, 238.8e3, 2388e3])
        self.write(":SENS:FLUX:RANG %d" % i)

    def read(self):
        """ Overwrites the :meth:`Instrument.read <pymeasure.instruments.Instrument.read>` 
        method to remove the last 2 characters from the output.
        """
        return super(FWBell5080, self).read()[:-2]

    def ask(self, command):
        """ Overwrites the :meth:`Instrument.ask <pymeasure.instruments.Instrument.ask>`
        method to remove the last 2 characters from the output.
        """
        return super(FWBell5080, self).ask()[:-2]

    def values(self, command):
        """ Overwrites the :meth:`Instrument.values <pymeasure.instruments.Instrument.values>` 
        method to remove the lastv2 characters from the output.
        """
        return super(FWBell5080, self).values()[:-2]

    def reset(self):
        """ Resets the instrument. """
        self.write("*OPC")

    def fields(self, samples=1):
        """ Returns a numpy array of field samples for a given sample number.

        :param samples: The number of samples to preform
        """
        if samples < 1:
            raise Exception("F.W. Bell 5080 does not support samples less than 1.")
        else:
            data = [self.field for i in range(int(samples))]
            return array(data, dtype=float64)

    def auto_range(self):
        """ Enables the auto range functionality. """
        self.write(":SENS:FLUX:RANG:AUTO")
