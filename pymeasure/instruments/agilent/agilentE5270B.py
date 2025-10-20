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

import logging

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Display(Channel):
    """A class representing the Agilent E5270B display."""

    enabled = Channel.setting(
        "RED %d",
        """Set whether the display is enabled during remote operation (bool).""",
        map_values=True,
        values={True: 1, False: 0},
        )

    engineering_format_enabled = Channel.setting(
        "DFM %d",
        """Set whether the engineering data format or the scientific data format is used (bool).

        :meth:`reset()` sets the data format to scientific.

        Example:
            - ``True`` (engineering):  +123.456mA
            - ``False`` (scientific): +1.234E-1A
        """,
        map_values=True,
        values={True: 0, False: 1},
        )

    measurement_smu = Channel.setting(
        "MCH %d",
        """Set the measurement SMU for the data displayed on the LCD
        (int, strictly from ``1`` to ``8``).
        """,
        validator=strict_range,
        values=[1, 8],
        )

    measurement_parameter = Channel.setting(
        "MPA %d",
        """Set the parameter displayed in the Measurement Data display area
        (str, strictly ``result``, ``result_and_source``, ``resistance`` or ``power``).
        """,
        map_values=True,
        values={"result": 1,
                "result_and_source": 2,
                "resistance": 3,
                "power": 4,
                },
        )

    source_smu = Channel.setting(
        "SCH %d",
        """Set the source SMU for the data displayed on the LCD.
        (int, strictly from ``1`` to ``8``).
        """,
        validator=strict_range,
        values=[1, 8],
        )

    source_parameter1 = Channel.setting(
        "SPA 1,%d",
        """Set the parameter displayed in line 1 of the Source Data display area
        (str, strictly in ``set_point``, ``compliance``, ``voltage_range``, ``current_range`` or
        ``error``).
        """,
        map_values=True,
        values={"set_point": 1,
                "compliance": 2,
                "voltage_range": 3,
                "current_range": 4,
                "error": 5,
                },
        )

    source_parameter2 = Channel.setting(
        "SPA 2,%d",
        """Set the parameter displayed in line 2 of the Source Data display area
        (str, strictly in ``set_point``, ``compliance``, ``voltage_range``, ``current_range`` or
        ``error``).
        """,
        map_values=True,
        values={"set_point": 1,
                "compliance": 2,
                "voltage_range": 3,
                "current_range": 4,
                "error": 5,
                },
        )


class SMUChannel(Channel):
    """A class representing the Agilent E5270B SMU channel."""

    enabled = Channel.setting(
        "%s",
        """Set the channel output state (bool).""",
        map_values=True,
        values={True: "CN{ch}", False: "CL{ch}"},
        check_set_errors=True,
    )

    current_setpoint = Channel.setting(
        "DI{ch},%d,%g,%g",
        """Set range, output current and voltage compliance (int, float, float).

        .. code:: python

            inst = AgilentE5270B("GPIB0::17::INSTR")
            inst.smu1.current_setpoint = (0, 1.32e-3, 0.5)  # (range, value, compliance)
            # Set SMU1 to output 1.32 mA in autorange with 0.5 V voltage compliance

        Ranges:
            - ``0``: Auto ranging
            - ``8``: 1 pA limited auto ranging for E5287A+E5288A
            - ``9``: 10 pA limited auto ranging for E5287A
            - ``10``: 100 pA limited auto ranging for E5287A
            - ``11``: 1 nA limited auto ranging
            - ``12``: 10 nA limited auto ranging
            - ``13``: 100 nA limited auto ranging
            - ``14``: 1 μA limited auto ranging
            - ``15``: 10 μA limited auto ranging
            - ``16``: 100 μA limited auto ranging
            - ``17``: 1 mA limited auto ranging
            - ``18``: 10 mA limited auto ranging
            - ``19``: 100 mA limited auto ranging
            - ``20``: 1 A limited auto ranging for E5280B

        """,
        check_set_errors=True,
    )

    current = Channel.measurement(
        "TI{ch}",
        """Measure the current in Amps (float).""",
        get_process=lambda v: float(v[3:]),
    )

    voltage_setpoint = Instrument.setting(
        "DV{ch},%d,%g,%g",
        """Set range, output voltage and current compliance (int, float, float)

        .. code:: python

            inst = AgilentE5270B("GPIB0::17::INSTR")
            inst.smu1.voltage_setpoint = (12, 14.42, 0.05)  # (range, value, compliance)
            # Set SMU1 to output 14.42 V in 20 V range with 50 mA current compliance

        Ranges:
            - ``0``: Auto ranging
            - ``5``: 0.5 V limited auto ranging for E5281B/E5287A
            - ``50``: 5 V limited auto ranging for E5281B/E5287A
            - ``11`` or ``20``: 2 V limited auto ranging
            - ``12`` or ``200``: 20 V limited auto ranging
            - ``13`` or ``400``: 40 V limited auto ranging
            - ``14`` or ``1000``: 100 V limited auto ranging
            - ``15`` or ``2000``: 200 V limited auto ranging for E5280B

        """,
        check_set_errors=True,
    )

    voltage = Instrument.measurement(
        "TV{ch}",
        """Measure the voltage in Volts (float).""",
        get_process=lambda v: float(v[3:]),
    )


class AgilentE5270B(SCPIMixin, Instrument):
    """A class representing the Agilent E5270B 8 slot SMU mainframe.

    It supports the following plug-in modules:

    +--------+-------+-------+-----------------+----------------+
    |  Name  | Type  | Slots | Range           | Resolution     |
    +========+=======+=======+=================+================+
    | E5280B | HPSMU | 2     | ±200 V, ±1 A    | 2 µV, 10 fA    |
    +--------+-------+-------+-----------------+----------------+
    | E5281B | MPSMU | 1     | ±100 V, ±100 mA | 0.5 µV, 10 fA  |
    +--------+-------+-------+-----------------+----------------+
    | E5287A | HRSMU | 1     | ±100 V, ±100 mA | 0.5 µV, 1 fA   |
    +--------+-------+-------+-----------------+----------------+
    | E5288A |  ASU  |  ---  | ±100 V, ±100 mA | 0.5 µV, 0.1 fA |
    +--------+-------+-------+-----------------+----------------+

    """

    display = Instrument.ChannelCreator(Display)

    def __init__(self, adapter,
                 name="Agilent E5270B",
                 **kwargs):
        super().__init__(adapter, name,
                         write_termination="\r\n",
                         read_termination="\r\n",
                         **kwargs
                         )

        # Add the SMU modules as channels.
        # If a SMU module uses 2 physical slots in the mainframe
        # then the higher slot number is used in the SMU name.
        for index, option in enumerate(self.options):
            if option.startswith("E52"):
                self.add_child(SMUChannel,
                               id=index+1,
                               prefix="smu",
                               )

    def clear(self):
        """:meta private:"""  # don't show in documentation
        raise NotImplementedError("'*CLS' is not supported by E5270B.")

    def get_error_message(self, error_code):
        """Return the error message for to the specified error code (str)."""
        self.write(f"EMG? {error_code}")
        return self.read()

    def check_errors(self):
        """Read all errors from the instrument.

        :return: List of error entries.

        .. E5270B does not support 'SYST:ERR?' so it's redefined as 'ERR?'.
           Returns the last 4 error codes and clears the error buffer.
        """
        errors = []
        got = self.ask("ERR?")
        for error_code in map(int, got.split(",")):
            if error_code != 0:
                error_message = self.get_error_message(error_code)
                log.error(f"{self.name}: {error_code}, {error_message}")
                errors.append(error_code)
        return errors

    options = Instrument.measurement(
        "UNT?",
        """Get the installed SMUs (list of str).

        Each list entry contains the module name and its revision, e.g. ``E5281B,0``
        An empty slot returns ``0,0``

        """,
        maxsplit=0,
        get_process=lambda v: v.split(";")
    )
