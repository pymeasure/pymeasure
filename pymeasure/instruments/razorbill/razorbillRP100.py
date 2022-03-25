#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.validators import (strict_discrete_set,
                                              strict_range)


class razorbillRP100(Instrument):
    """Represents Razorbill RP100 strain cell controller

    .. code-block:: python

        scontrol = razorbillRP100("ASRL/dev/ttyACM0::INSTR")

        scontrol.output_1 = True      # turns output on
        scontrol.slew_rate_1 = 1      # sets slew rate to 1V/s
        scontrol.voltage_1 = 10       # sets voltage on output 1 to 10V

    """

    output_1 = Instrument.control("OUTP1?", "OUTP1 %d",
                                  """Turns output of channel 1 on or off""",
                                  validator=strict_discrete_set,
                                  values={True: 1, False: 0},
                                  map_values=True)

    output_2 = Instrument.control("OUTP2?", "OUTP2 %d",
                                  """Turns output of channel 2 on or off""",
                                  validator=strict_discrete_set,
                                  values={True: 1, False: 0},
                                  map_values=True)

    voltage_1 = Instrument.control("SOUR1:VOLT?", "SOUR1:VOLT %g",
                                   """Sets or queries the output voltage of channel 1""",
                                   validator=strict_range,
                                   values=[-230, 230])

    voltage_2 = Instrument.control("SOUR2:VOLT?", "SOUR2:VOLT %g",
                                   """Sets or queries the output voltage of channel 2""",
                                   validator=strict_range,
                                   values=[-230, 230])

    slew_rate_1 = Instrument.control(
        "SOUR1:VOLT:SLEW?", "SOUR1:VOLT:SLEW %g",
        """Sets or queries the source slew rate in volts/sec of channel 1""",
        validator=strict_range,
        values=[0.1 * 10e-3, 100 * 10e3]
    )

    slew_rate_2 = Instrument.control(
        "SOUR2:VOLT:SLEW?", "SOUR2:VOLT:SLEW %g",
        """Sets or queries the source slew rate in volts/sec of channel 2""",
        validator=strict_range,
        values=[0.1 * 10e-3, 100 * 10e3]
    )

    instant_voltage_1 = Instrument.measurement(
        "SOUR1:VOLT:NOW?",
        """Returns the instantaneous output of source one in volts"""
    )

    instant_voltage_2 = Instrument.measurement(
        "SOUR2:VOLT:NOW?",
        """Returns the instanteneous output of source two in volts"""
    )

    contact_voltage_1 = Instrument.measurement(
        "MEAS1:VOLT?",
        """Returns the Voltage in volts present at the front panel output of channel 1"""
    )

    contact_voltage_2 = Instrument.measurement(
        "MEAS2:VOLT?",
        """Returns the Voltage in volts present at the front panel output of channel 2"""
    )

    contact_current_1 = Instrument.measurement(
        "MEAS1:CURR?",
        """Returns the current in amps present at the front panel output of channel 1"""
    )

    contact_current_2 = Instrument.measurement(
        "MEAS2:CURR?",
        """Returns the current in amps present at the front panel output of channel 2"""
    )

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Razorbill RP100 Piezo Stack Powersupply", **kwargs
        )
        self.timeout = 20
