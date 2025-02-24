#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments import SCPIMixin, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class KeysightE3642A(SCPIMixin, Instrument):
    """Represents the Keysight E3642A DC Power Supply interface for interacting with
    the instrument."""

    def __init__(self, adapter, name="Keysight E3642A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    output_enabled = Instrument.control(
        "OUTPUT:STATE?",
        "OUTPUT:STATE %d",
        """Control whether output state is enabled.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %f",
        """Control the output voltage setpoint in Volts.""",
        validator=strict_range,
        values=[0, 20],
        dynamic=True,
    )

    current_limit = Instrument.control(
        "CURR?",
        "CURR %f",
        """Control the output current limit in Amperes.""",
        validator=strict_range,
        values=[0, 5],
        dynamic=True,
    )

    def apply(self, voltage_setpoint, current_limit):
        self.voltage_setpoint = voltage_setpoint
        self.current_limit = current_limit
