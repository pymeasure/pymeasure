#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.instruments import AdapterType, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class UNITUDP6933B(SCPIMixin, Instrument):
    """Control the UNI-T UDP6933B programmable DC power supply.

    The supply supports SCPI communication over USB, LAN, RS-232, and RS-485.
    """

    def __init__(
        self,
        adapter: AdapterType,
        name: str = "UNI-T UDP6933B DC power supply",
        **kwargs,
    ):
        super().__init__(adapter, name, **kwargs)

    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """Measure the actual output voltage in volts.""",
    )

    current = Instrument.measurement(
        "MEAS:CURR?",
        """Measure the actual output current in amperes.""",
    )

    # Use the full keyword because hardware testing showed that the shorter MEAS:POW? form is
    # rejected by firmware 1.01.0301, even though the other measurement abbreviations work.
    power = Instrument.measurement(
        "MEASure:POWer?",
        """Measure the actual output power in watts.""",
    )

    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %g",
        """Control the output voltage setpoint in volts (float strictly from 0 to 150).""",
        validator=strict_range,
        values=(0, 150),
    )

    current_limit = Instrument.control(
        "CURR?",
        "CURR %g",
        """Control the output current limit in amperes (float strictly from 0 to 5).""",
        validator=strict_range,
        values=(0, 5),
    )

    # Hardware returns ON/OFF strings, so cast=str prevents numeric response parsing.
    output_enabled = Instrument.control(
        "OUTP?",
        "OUTP %s",
        """Control whether the power output is enabled (boolean).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    def apply(self, voltage: float, current_limit: float) -> None:
        """Set the output voltage and current limit.

        :param voltage: Output voltage setpoint in volts.
        :param current_limit: Output current limit in amperes.
        """
        # Validate both values first to avoid applying only part of the requested configuration.
        strict_range(voltage, (0, 150))
        strict_range(current_limit, (0, 5))

        # Unlike the GW Instek example, the UDP6933B has no general two-argument APPLy
        # command. Its documented APPLy command recalls stored presets, so voltage and
        # current are sent separately.
        self.voltage_setpoint = voltage
        self.current_limit = current_limit
