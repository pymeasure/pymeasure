#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class AgilentE3640A(Instrument):
    """
    Represents the Agilent E3640A power supply.

    .. code-block:: python

        psu = AgilentE3640A("GPIB::...")
        psu.reset()
        psu.voltage = 15  # Volts
        print(psu.voltage)
        psu.current_limit = 0.5  # Amps
        psu.output = "ON"
    """

    voltage = Instrument.control(
        "VOLT?",
        "VOLT %g",
        "DC voltage, in Volts",
        validator=strict_range,
        values=[0, 20]
    )

    current_limit = Instrument.control(
        "CURR?",
        "CURR %g",
        "DC current, in Amps",
        validator=strict_range,
        values=[0, 1.5]
    )

    output = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """ A boolean property that turns on (True, 'on') or off (False, 'off')
        the output of the function generator. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0},
    )

    def __init__(self, resourceName, **kwargs):
        super(AgilentE3640A, self).__init__(
            resourceName,
            "Agilent E3640A",
            **kwargs
        )
