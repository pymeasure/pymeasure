#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep

import numpy as np


class FWBell5080(SCPIMixin, Instrument):
    """ Represents the F.W. Bell 5080 Handheld Gaussmeter and
    provides a high-level interface for interacting with the
    instrument

    :param port: The serial port of the instrument

    .. code-block:: python

        meter = FWBell5080('/dev/ttyUSB0')  # Connects over serial port /dev/ttyUSB0 (Linux)

        meter.units = 'gauss'               # Sets the measurement units to Gauss
        meter.range = 1                     # Sets the range to 3 kG
        print(meter.field)                  # Reads and prints a field measurement in G

        fields = meter.fields(100)          # Samples 100 field measurements
        print(fields.mean(), fields.std())  # Prints the mean and standard deviation of the samples

    """

    def __init__(self, adapter, name="F.W. Bell 5080 Handheld Gaussmeter", **kwargs):
        kwargs.setdefault('timeout', 500)
        kwargs.setdefault('baudrate', 2400)
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    field = Instrument.measurement(
        ":MEASure:FLUX?",
        """ Measure the field in the appropriate units (float).
        """,
        # Remove units
        get_process=lambda v: float(v.replace('T', '').replace('G', '').replace('Am', ''))

    )

    UNITS = {
        'gauss': 'DC:GAUSS', 'gauss ac': 'AC:GAUSS',
        'tesla': 'DC:TESLA', 'tesla ac': 'AC:TESLA',
        'amp-meter': 'DC:AM', 'amp-meter ac': 'AC:AM'
    }

    units = Instrument.control(
        ":UNIT:FLUX?", ":UNIT:FLUX:%s",
        """ Get the field units (str), which can take the
        values: 'gauss', 'gauss ac', 'tesla', 'tesla ac', 'amp-meter', and
        'amp-meter ac'. The AC versions configure the instrument to measure AC.
        """,
        validator=strict_discrete_set,
        values=UNITS,
        map_values=True
    )

    range = Instrument.control(
        ":SENS:FLUX:RANG?", ":SENS:FLUX:RANG %d",
        """ Control the maximum field range in the active units (int).
        The range unit is dependent on the current units mode (gauss, tesla, amp-meter). Value
        sets an equivalent range across units that increases in magnitude (1, 10, 100).

        +--------+--------+---------+-----------+
        | Value  | gauss  |  tesla  | amp-meter |
        +--------+--------+---------+-----------+
        | 0      | 300 G  |  30  mT | 23.88 kAm |
        +--------+--------+---------+-----------+
        | 1      | 3 kG   |  300 mT | 238.8 kAm |
        +--------+--------+---------+-----------+
        | 2      | 30 kG  |  3 T    | 2388  kAm |
        +--------+--------+---------+-----------+
        """,
        validator=strict_discrete_set,
        values=[0, 1, 2],
        cast=int
    )

    def read(self):
        """ Overwrites the :meth:`Instrument.read <pymeasure.instruments.Instrument.read>`
        method to remove semicolons and replace spaces with colons.
        """
        # To set the unit mode to DC Tesla you need to write(':UNIT:FLUX:DC:TESLA')
        # However the response from ask(':UNIT:FLUX?') is "DC TESLA", with no colon.
        # We replace space with colon to preserve the mapping in UNITS.
        # Semicolons may be appended to end of response from FW Bell 5080, and are removed
        return super().read().replace(' ', ':').replace(';', '')

    def reset(self):
        """ Resets the instrument. """
        self.clear()

    def fields(self, samples=1):
        """ Returns a numpy array of field samples for a given sample number.

        :param samples: The number of samples to preform
        """
        if samples < 1:
            raise Exception("F.W. Bell 5080 does not support samples less than 1.")
        else:
            data = [self.field for i in range(int(samples))]
            return np.array(data, dtype=np.float64)

    def auto_range(self):
        """ Enables the auto range functionality. """
        self.write(":SENS:FLUX:RANG:AUTO")
        # Instrument needs a delay before next command
        sleep(2)
