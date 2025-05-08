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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Fluke7341(Instrument):
    """ Represents the compact constant temperature bath from Fluke.
    """

    def __init__(self, adapter, name="Fluke 7341", **kwargs):
        kwargs.setdefault('timeout', 2000)
        kwargs.setdefault('write_termination', '\r\n')
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            asrl={'baud_rate': 2400},
            **kwargs
        )

    def read(self):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        Extract the value from the response string.

        Responses are in the format "`type`: `value` `optional information`".
        Optional information is for example the unit (degree centigrade or Fahrenheit).
        """
        return super().read().split(":")[-1]

    set_point = Instrument.control("s", "s=%g",
                                   """Control the temperature setpoint (float from -40 to 150 °C)
                                   The unit is as defined in property :attr:`~.unit`.""",
                                   validator=strict_range,
                                   values=(-40, 150),
                                   preprocess_reply=lambda x: x.split()[0],
                                   )

    unit = Instrument.control(
        "u", "u=%s",
        """Control the temperature unit: `c` for Celsius and `f` for Fahrenheit`.""",
        validator=strict_discrete_set,
        values=('c', 'f'),
    )

    temperature = Instrument.measurement("t",
                                         """Measure the current bath temperature.
                                         The unit is as defined in property :attr:`unit`.""",
                                         preprocess_reply=lambda x: x.split()[0],
                                         )

    id = Instrument.measurement("*ver",
                                """Get the instrument model.""",
                                cast=str,
                                get_process=lambda x: f"Fluke,{x[0][4:]},NA,{x[1]}",
                                )
