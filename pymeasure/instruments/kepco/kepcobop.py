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

# List of Kepco BOP's (Vmax,Imax) [single channel output]
# 100 W:
# 5-20
# 20-5
# 50-2
# 100-1

# 200 W:
# 5-30
# 20-10
# 36-6
# 50-4
# 72-3
# 100-2
# 200-1

# 400 W:
# 20-20
# 36-12
# 50-8
# 72-6
# 100-4

from enum import IntFlag
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_range

OPERATING_MODES = ['VOLT', 'CURR']


class TestErrorCode(IntFlag):
    QUARTER_SCALE_VOLTAGE_READBACK = 512
    QUARTER_SCALE_VOLTAGE = 256
    MIN_VOLTAGE_OUTPUT = 128
    MAX_VOLTAGE_OUTPUT = 64
    LOOP_BACK_TEST = 32
    DIGITAL_POT = 16
    OPTICAL_BUFFER = 8
    FLASH = 4
    RAM = 2
    ROM = 1
    OK = 0


class KepcoBOP3612(SCPIMixin, Instrument):
    """
    Represents the Kepco BOP 36-12 (M or D) 400 W bipolar power supply
    fitted with BIT 4886 digital interface card (minimal implementation)
    and provides a high-level interface for interacting with the instrument.
    """
    _Vmax = 36
    _Imax = 12

    def __init__(self, adapter, name="Kepco BOP 36-12 Bipolar Power Supply",
                 **kwargs):
        super().__init__(
            adapter=adapter,
            name=name,
            read_termination="\n",
            write_termination="\n",
            **kwargs
        )

    output_enabled = Instrument.control(
        "OUTPut?",
        "OUTPut %d",
        """
        Control whether the source is enabled, takes values True or False (bool)
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def beep(self):
        """Cause the unit to emit a brief audible tone."""
        self.write("SYSTem:BEEP")

    confidence_test = Instrument.measurement(
        "*TST?",
        """
        Get error code after performing interface self-test procedure.

        Returns 0 if all tests passed, otherwise corresponding error code
        as detailed in manual.
        """,
        get_process=lambda v: TestErrorCode(v),
    )

    bop_test = Instrument.measurement(
        "DIAG:TST?",
        """
        Get error code after performing full power supply self-test.

        Returns 0 if all tests passed, otherwise corresponding error code
        as detailed in manual.
        Caution: Output will switch on and swing to maximum values.
        Disconnect any load before testing.
        """,
        get_process=lambda v: TestErrorCode(v),
    )

    def wait_to_continue(self):
        """ Cause the power supply to wait until all previously issued
        commands and queries are complete before executing subsequent
        commands or queries. """
        self.write("*WAI")

    voltage = Instrument.measurement(
        "MEASure:VOLTage?",
        """
        Measure voltage present across the output terminals in Volts.
        """,
        cast=float
    )

    current = Instrument.measurement(
        "MEASure:CURRent?",
        """
        Measure current through the output terminals in Amps.
        """,
        cast=float
    )

    operating_mode = Instrument.control(
        "FUNCtion:MODE?", "FUNCtion:MODE %s",
        """
        Control the operating mode of the BOP.

        As a command, a string, VOLT or CURR, is sent.
        As a query, a 0 or 1 is returned, corresponding to VOLT or CURR respectively.
        This is mapped to corresponding string.
        """,
        validator=strict_discrete_set,
        values=OPERATING_MODES,
        get_process=lambda x: OPERATING_MODES[int(x)]
    )

    current_setpoint = Instrument.control(
        "CURRent?", "CURRent %g",
        """
        Control the output current setpoint.

        Functionality depends on the operating mode.
        If power supply in current mode, this sets the output current setpoint.
        The current achieved depends on the voltage compliance and load conditions
        (see: `current`).
        If power supply in voltage mode, this sets the compliance current
        for the corresponding voltage set point.
        Query returns programmed value, meaning of which is dependent on
        power supply operating context (see: `operating_mode`).

        Output must be enabled separately (see: `output_enabled`)
        """,
        validator=truncated_range,
        values=[-1*_Imax, _Imax]
    )

    voltage_setpoint = Instrument.control(
        "VOLTage?", "VOLTage %g",
        """
        Control the output voltage setpoint.

        Functionality depends on the operating mode.
        If power supply in voltage mode, this sets the output voltage setpoint.
        The voltage achieved depends on the current compliance and load conditions
        (see: `voltage`).
        If power supply in current mode, this sets the compliance voltage
        for the corresponding current set point.
        Query returns programmed value, meaning of which is dependent on
        power supply operating context (see: `operating_mode`).

        Output must be enabled separately (see: `output_enabled`)
        """,
        validator=truncated_range,
        values=[-1*_Vmax, _Vmax]
    )
