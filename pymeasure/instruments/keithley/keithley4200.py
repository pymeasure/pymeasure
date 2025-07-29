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

from pymeasure.instruments import Instrument, Channel
from enum import IntFlag


class StatusCode(IntFlag):
    """A class representing the status codes ofd the Keithley 4200.

    Status codes:
        - 0: NONE
        - 1: DATA_READY
        - 2: SYNTAX_ERROR
        - 16: BUSY
        - 64: SERVICE_REQUEST

    """
    NONE = 0
    DATA_READY = 2**0
    SYNTAX_ERROR = 2**1
    B2 = 2**2
    B3 = 2**3
    BUSY = 2**4
    B5 = 2**5
    SERVICE_REQUEST = 2**6
    B7 = 2**7


class SMU(Channel):
    """A class representing the SMU (source/measure unit) channel."""

    def disable(self):
        """Disable the SMU."""
        self.write("US;DV{ch}")
        self.check_set_errors()

    voltage_setpoint = Channel.setting(
        "US;DV{ch},%d,%g,%g",  # range, value, compliance
        """Set range, output voltage and current compliance (int, float, float).

        Voltage is in Volts and current in Amps.

        .. code::

            inst = Keithley4200("TCPIP::192.168.1.1::1225::SOCKET")
            inst.smu1.voltage_setpoint = (0, 3.3, 1e-2)  # (range, value, compliance)
            # Set SMU1 to output 3.3 V in autorange with 10 mA current compliance

        Voltage source range:
            - 0: autorange
            - 1: 20 V range
            - 2: 200 V range
            - 3: 200 V range
            - 4: 200 mV range, only with a preamplifier
            - 5: 2 V range, only with a preamplifier

        """,
        check_set_errors=True,
        )

    voltage = Channel.measurement(
        "US;TV{ch}",
        """Measure the voltage in Volts (float).""",
        get_process=lambda v: float(v[3:]),
        )

    current_setpoint = Channel.setting(
        "US;DI{ch},%d,%g,%g",  # range, value, compliance
        """Set range, output current and voltage compliance (int, float, float).

        Current is in Amps and voltage in Volts.

        .. code::

            inst = Keithley4200("TCPIP::192.168.1.1::1225::SOCKET")
            inst.smu1.current_setpoint = (9, 55e-3, 10)  # (range, value, compliance)
            # Set SMU1 to output 55 mA in 100 mA range with 10 V voltage compliance

        Current source range:
            - 0: autorange
            - 1: 1 nA range, only with a preamplifier
            - 2: 10 nA range, only with a preamplifier
            - 3: 100 nA range
            - 4: 1 µA range
            - 5: 10 µA range
            - 6: 100 µA range
            - 7: 1 mA range
            - 8: 10 mA range
            - 9: 100 mA range
            - 10: 1 A range, only with a 4210-SMU or 4211-SMU
            - 11: 1 pA range, only with a preamplifier
            - 12: 10 pA range, only with a preamplifier
            - 13: 100 pA range, only with a preamplifier

        """,
        check_set_errors=True,
        )

    current = Channel.measurement(
        "US;TI{ch}",
        """Measure the current in Amps.""",
        get_process=lambda v: float(v[3:]),
        )


class Keithley4200(Instrument):
    """A class representing the Keithley 4200A-SCS Parameter Analyzer.

    This driver only uses the user mode commands for controlling the SMUs.

    Start the 'KXCI' program on the 4200A-SCS to activate remote control. The remote interface
    is configured with the Keithley Configuration Utility 'KCon'.

    Currently, the driver is only working with the ethernet interface.
    """

    def __init__(self, adapter,
                 name="Keithley 4200A-SCS",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            tcpip={"write_termination": "\0",
                   "read_termination": "\0"},
            **kwargs
        )

        options = self.options
        for element in options:
            id = int(element[-1])
            if "SMU" in element.upper():
                self.add_smu(id)

    def add_smu(self, id):
        """Add a SMU channel to the device."""
        self.add_child(SMU,
                       id=id,
                       prefix="smu",
                       collection="smu",
                       )

    def check_set_errors(self):
        """Check for errors after sending a command.

        :raise: ValueError if response is not 'ACK'
        """
        got = self.read().strip()
        expected = "ACK"

        if expected != got:
            raise ValueError(f"Expected '{expected}', got '{got}'")

        return []

    def clear(self):
        """Clear all data from the buffer.

        It also clears bit B0 (DATA_READY) of the status byte.
        """
        self.write("BC")
        self.check_set_errors()

    id = Instrument.measurement(
        "ID",
        """Get the identification of the instrument (str).""",
        cast=str,
        maxsplit=0,
        )

    status = Instrument.measurement(
        "SP",
        """Get the status byte (IntFlag).""",
        get_process=lambda v: StatusCode(int(v)),
        )

    options = Instrument.measurement(
        "*OPT?",
        """Get the installed options (list of str).""",
        cast=str,
        )
