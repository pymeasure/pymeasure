#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2021 PyMeasure Developers
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

from pymeasure.instruments import Instrument, validators

class HP6060B(Instrument):
    """ Represents the HP HP6060B instrument.
    """

    voltage_measured = Instrument.measurement(
        ":MEAS:VOLT?",
        "Measured DC voltage, in Volts"
    )

    current_measured = Instrument.measurement(
        ":MEAS:CURR?",
        "Measured DC current, in Amps"
    )

    power_measured = Instrument.measurement(
        ":MEAS:POW?",
        "Measured DC power, in Watts"
    )

    mode = Instrument.control(
        ":MODE?", ":MODE:%s",
        """ Regulation mode: VOLT[AGE], CURR[ENT] or RES[ISTANCE]. """,
        validator=validators.strict_discrete_set,
        values=["VOLT", "VOLTAGE", "CURR", "CURRENT", "RES", "RESISTANCE"],
    )

    input = Instrument.control(
        ":INP?", ":INP:STAT %s",
        """ Input state: ON or OFF. """,
        validator=validators.strict_discrete_set,
        values=["ON", "OFF"],
    )

    current = Instrument.control(
        ":CURR:LEVEL?", ":CURR:LEVEL:IMM %g",
        """ Current mode regulation target, in Amps. """,
        validator=validators.strict_range,
        values=[0, 60],
        check_set_errors=True,
    )

    voltage = Instrument.control(
        ":VOLT:LEVEL?", ":VOLT:LEVEL:IMM %g",
        """ Voltage mode regulation target, in Volts. """,
        validator=validators.strict_range,
        values=[0, 60],
        check_set_errors=True,
    )

    resistance = Instrument.control(
        ":RES:LEVEL?", ":RES:LEVEL:IMM %g",
        """ Resistance mode regulation target, in Ohms. """,
        validator=validators.strict_range,
        values=[1, 10000],
        check_set_errors=True,
    )

    def __init__(self, resourceName, **kwargs):
        super(HP6060B, self).__init__(
            resourceName,
            "HP 6060B",
            **kwargs
        )
