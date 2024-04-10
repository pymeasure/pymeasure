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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_range

OPERATING_MODES = ['VOLT', 'CURR']


class KepcoBOP3612(SCPIMixin, Instrument):
    """
    Represents the Kepco BOP 36-12 (M or D) 400 W bipolar power supply
    fitted with BIT 4886 digital interface card (minimal implementation)
    and provides a high-level interface for interacting with the instrument.
    """
    _Vmax = 36
    _Imax = 12

    def __init__(self, adapter, name="Kepco BOP 36-12 Bipolar Power Supply",
                 read_termination="\n", write_termination="\n", **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            write_termination=write_termination,
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
        """Causes the unit to emit a brief audible tone."""
        self.write("SYSTem:BEEP")

    confidence_test = Instrument.measurement(
        "*TST?",
        """
        Power supply interface self-test procedure.
        Returns 0 if all tests passed,
        otherwise corresponding error code.
        """,
        cast=int
    )

    bop_test = Instrument.measurement(
        "DIAG:TST?",
        """
        Power supply self-test (includes interface plus BOP operation).
        Caution: Output will switch on and swing to maximum values.
        Disconnect any load before testing.
        Reutnrs 0 if all tests passed,
        otherwise corresponding error code.
        """,
        cast=int
    )

    def wait_to_continue(self):
        """ Causes the power supply to wait until all previously issued
        commands and queries are complete before executing subsequent
        commands or queries. """
        self.write("*WAI")

    voltage_measure = Instrument.measurement(
        "MEASure:VOLTage?",
        """
        Measures actual voltage that is across the output terminals.
        """,
        cast=float
    )

    current_measure = Instrument.measurement(
        "MEASure:CURRent?",
        """
        Measures the actual current through the output terminals.
        """,
        cast=float
    )

    operating_mode = Instrument.control(
        "FUNCtion:MODE?", "FUNCtion:MODE %s",
        """
        A string property that controls the operating mode of the BOP.
        As a command, a string, VOLT or CURR, is sent.
        As a query, a 0 or 1 is returned, corresponding to (VOLT, CURR) respectively.
        This is mapped to corresponding string.
        """,
        validator=strict_discrete_set,
        values=OPERATING_MODES,
        get_process=lambda x: OPERATING_MODES[int(x)]
    )

    current = Instrument.control(
        "CURRent?", "CURRent %g",
        """
        Sets the output current setpoint, depending on the operating mode.
        If power supply in current mode, this sets the output current,
        depending on the voltage compliance and load conditions.
        If power supply in voltage mode, this sets the compliance current
        for the corresponding voltage set point.
        Query returns corresponding programmed value, meaning of which
        is dependent on power supply operating context (see: `operating_mode`).
        Set current not same as actual current (see: `current_measure`).
        Output must be enabled separately (see: `output_enabled`)
        """,
        validator=truncated_range,
        values=[-1*_Imax, _Imax]
    )

    voltage = Instrument.control(
        "VOLTage?", "VOLTage %g",
        """
        Sets the output voltage setpoint, depending on the operating mode.
        If power supply in voltage mode, this sets the output voltage,
        depending on the current compliance and load conditions.
        If power supply in current mode, this sets the compliance voltage
        for the corresponding current set point.
        Query returns corresponding programmed value, meaning of which
        is dependent on power supply operating context (see: `operating_mode`).
        Set voltage not same as actual voltage (see: `voltage_measure`).
        Output must be enabled separately (see: `output_enabled`)
        """,
        validator=truncated_range,
        values=[-1*_Vmax, _Vmax]
    )
