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

from enum import IntFlag

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pymeasure.instruments._strenum import StrEnum


class InstrStatus(IntFlag):
    """Instrument status flags.
    Convert an error code (int) to status with ``InstrStatus(code)``."""

    REMOTE_INHIBIT = 2**8
    FAN_FAILURE = 2**7
    MAX_SINE_WAVE_CURRENT_LIMIT = 2**6
    SYNC_TIMEOUT = 2**5
    REVERSE_VOLTAGE_ON_INPUT = 2**4
    OVER_POWER = 2**3
    OVER_CURRENT = 2**2
    OVER_VOLTAGE = 2**1
    OVER_TEMPERATURE = 2**0
    OK = 0


class InstrMode(StrEnum):
    """Instrument modes. Each mode has low (L), medium (M), and high (H) ranges,
    except for constant resistance (CR) mode, which only has L and H. The range
    is not included in this enum."""

    CONSTANT_CURRENT = "CC"
    CONSTANT_VOLTAGE = "CV"
    CONSTANT_POWER = "CP"
    CONSTANT_IMPEDANCE = "CZ"
    CONSTANT_RESISTANCE = "CR"
    CONSTANT_CURRENT_DYNAMIC = "CCD"
    SINE_WAVE_DYNAMIC = "SWD"
    TIMING_MEASUREMENT = "TIM"
    OVERCURRENT_TEST = "OCP"
    PROGRAM_SEQUENCE = "PROG"
    USER_DEFINED_WAVEFORM = "UDW"
    MAXIMUM_POWER_POINT_TRACKER = "MPPT"


class InstrModeRange(StrEnum):
    """Instrument mode ranges."""

    LOW_RANGE = "L"
    MEDIUM_RANGE = "M"
    HIGH_RANGE = "H"


class Chroma63600_Channel(Channel):
    """Represents a Chroma 63600 channel of the electronic load bank."""

    _BOOLS = {True: "ON", False: "OFF"}
    MODES = [
        "CCL",
        "CCM",
        "CCH",
        "CRL",
        "CRH",
        "CVL",
        "CRM",
        "CRH",
        "CPL",
        "CPM",
        "CPH",
        "CZL",
        "CZM",
        "CZH",
        "CCDL",
        "CCDM",
        "CCDH",
        "CCFSL",
        "CCFSM",
        "CCFSH",
        "TIML",
        "TIMM",
        "TIMH",
        "SWDL",
        "SWDM",
        "SWDH",
        "OCPL",
        "OCPM",
        "OCPH",
        "PROG",
        "MPPTL",
        "MPPTM",
        "MPPTH",
        "UDWL",
        "UDWM",
        "UDWH",
    ]

    def insert_id(self, command):
        """Set current channel before performing command."""
        return f"CHAN {self.id};{command}"

    active = Channel.control(
        "CHANNEL:ACTIVE?",
        "CHANNEL:ACTIVE %s",
        """Control whether to enable the load module (bool).""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True,
        cast=str,
    )

    enabled = Channel.control(
        "LOAD?",
        "LOAD %s",
        """Control current channel active status, can be ``True`` (ON) or ``False`` (OFF).""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True,
        cast=str,
    )

    status = Channel.measurement(
        "LOAD:PROTECTION?",  # Synonym: FETCH:STATUS?
        """
        Get the status of the electronic load.

        Returns :class:`InstrStatus`.
        """,
        get_process=lambda v: InstrStatus(v),
        cast=int,
    )

    identify = Channel.measurement(
        "CHAN:ID?",
        """Get module identification string.""",
        cast=str,
    )

    current = Channel.measurement(
        "FETCH:CURRENT?", """Measure current at electronic load input in Amps (float)."""
    )

    frequency = Channel.measurement(
        "FETCH:FREQUENCY?",
        """Measure the frequency measured in frequency sweep mode or sine wave dynamic mode.""",
    )

    power = Channel.measurement("FETCH:POWER?", """Get power measured at electronic load input.""")
    voltage = Channel.measurement(
        "FETCH:VOLTAGE?", """Get the voltage measured at the electronic load input."""
    )

    def clear_protection_state(self):
        """Set the status of the electronic load to a clear state."""
        self.write("LOAD:PROTECTION:CLEAR")

    short_circuit_enabled = Channel.control(
        "LOAD:SHORT?",
        "LOAD:SHORT %s",
        """Control short-circuit simulation, ON (True) or OFF (False).""",
        validator=strict_discrete_set,
        values=_BOOLS,
        map_values=True,
        cast=str,
    )

    mode = Channel.control(
        ":MODE?",
        ":MODE %s",
        """Control the operational mode of the electronic load.

        Basic modes include constant current (CC), constant resistance (CR), constant voltage (CV),
        constant power (CP), and constant impedance (CZ). There are low (L), middle (M), and
        high (H) ranges for most modes.

        In addition to the basic modes, the unit supports dynamic constant current (CCD), dynamic
        sine wave (SWD), timing measurement (TIM), overcurrent test (OCP), program sequences (PROG),
        user defined waveform (UDW), and maximum power point tracker (MPPT) modes.

            CCL|CCM|CCH
            CRL|CRH
            CVL|CRM|CRH
            CPL|CPM|CPH
            CZL|CZM|CZH
            CCDL|CCDM|CCDH
            CCFSL|CCFSM|CCFSH
            TIML|TIMM|TIMH
            SWDL|SWDM|SWDH
            OCPL|OCPM|OCPH
            PROG
            MPPTL|MPPTM|MPPTH
            UDWL|UDWM|UDWH
        """,
        validator=strict_discrete_set,
        values=MODES,
        get_process=lambda v: (
            (InstrMode(v),) if v == "PROG" else (InstrMode(v[:-1]), InstrModeRange(v[-1]))
        ),
        cast=str,
    )

    # TIMING MODE
    amp_hours = Channel.measurement(
        "FETCH:AH?",
        """Measure ampere-hour measured in timing mode.""",
    )

    time = Channel.measurement("FETCH:TIME?", """Get time measured in timing mode.""")
    watt_hours = Channel.measurement("FETCH:WH?", """Get the watt-hour measured in timing mode.""")


class Chroma63630_80_60(Chroma63600_Channel):
    """Represents a Chroma 63630-80-60 single load module."""

    # CONSTANT CURRENT MODE (STATIC)
    current_setpoint_1 = Channel.control(
        "CURRENT:STATIC:L1?",
        "CURRENT:STATIC:L1 %g",
        """Control the L1 static current set point in constant current mode.""",
        validator=strict_range,
        values=[0, 60],
    )

    current_setpoint_2 = Channel.control(
        "CURRENT:STATIC:L2?",
        "CURRENT:STATIC:L2 %g",
        """Control the L2 static current set point in constant current mode.""",
        validator=strict_range,
        values=[0, 60],
    )

    # CONSTANT VOLTAGE MODE
    voltage_setpoint_1 = Channel.control(
        "VOLTAGE:STATIC:L1?",
        "VOLTAGE:STATIC:L1 %g",
        """Control the L1 voltage set point in constant voltage mode.""",
        validator=strict_range,
        values=[0, 80],
    )

    voltage_setpoint_2 = Channel.control(
        "VOLTAGE:STATIC:L2?",
        "VOLTAGE:STATIC:L2 %g",
        """Control the L2 voltage set point in constant voltage mode.""",
        validator=strict_range,
        values=[0, 80],
    )

    current_limit = Channel.control(
        "VOLTAGE:STATIC:ILIMIT?",
        "VOLTAGE:STATIC:ILIMIT %g",
        """Control the current limit in constant voltage mode.""",
        validator=strict_range,
        values=[0, 60],
    )

    # CONSTANT POWER MODE
    power_setpoint_1 = Channel.control(
        "POWER:STATIC:L1?",
        "POWER:STATIC:L1 %g",
        """Control the L1 power set point in constant power mode.""",
        validator=strict_range,
        values=[0, 300],
    )

    power_setpoint_2 = Channel.control(
        "POWER:STATIC:L2?",
        "POWER:STATIC:L2 %g",
        """Control the L2 power set point in constant power mode.""",
        validator=strict_range,
        values=[0, 300],
    )

    # CONSTANT RESISTANCE MODE
    resistance_setpoint_1 = Channel.control(
        "RESISTANCE:STATIC:L1?",
        "RESISTANCE:STATIC:L1 %g",
        """Control the L1 resistance set point in constant resistance mode.""",
        validator=strict_range,
        values=[0.015, 3000],
    )

    resistance_setpoint_2 = Channel.control(
        "RESISTANCE:STATIC:L2?",
        "RESISTANCE:STATIC:L2 %g",
        """Control the L2 resistance set point in constant resistance mode.""",
        validator=strict_range,
        values=[0.015, 3000],
    )

    # CONSTANT IMPEDANCE MODE
    parallel_load_capacitance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:CL?",
        "IMPEDANCE:STATIC:CL %g",
        """Control the equivalent parallel load capacitance in constant impedance mode.""",
    )

    series_inductance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:LS?",
        "IMPEDANCE:STATIC:LS %g",
        """Control the equivalent series inductance in constant impedance mode.""",
    )

    series_resistance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:RS?",
        "IMPEDANCE:STATIC:RS %g",
        """Control the equivalent series resistance in constant impedance mode.""",
    )

    parallel_load_resistance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:RL?",
        "IMPEDANCE:STATIC:RL %g",
        """Control the equivalent parallel load resistance in constant impedance mode.""",
    )


class Chroma63610_80_20(Chroma63600_Channel):
    """Represents one channel of a Chroma 63610-80-20 double load module."""

    # CONSTANT CURRENT MODE (STATIC)
    current_setpoint_1 = Channel.control(
        "CURRENT:STATIC:L1?",
        "CURRENT:STATIC:L1 %g",
        """Control the L1 static current set point in constant current mode.""",
        validator=strict_range,
        values=[0, 20],
    )

    current_setpoint_2 = Channel.control(
        "CURRENT:STATIC:L2?",
        "CURRENT:STATIC:L2 %g",
        """Control the L2 static current set point in constant current mode.""",
        validator=strict_range,
        values=[0, 20],
    )

    # CONSTANT VOLTAGE MODE
    voltage_setpoint_1 = Channel.control(
        "VOLTAGE:STATIC:L1?",
        "VOLTAGE:STATIC:L1 %g",
        """Control the L1 voltage set point in constant voltage mode.""",
        validator=strict_range,
        values=[0, 80],
    )

    voltage_setpoint_2 = Channel.control(
        "VOLTAGE:STATIC:L2?",
        "VOLTAGE:STATIC:L2 %g",
        """Control the L2 voltage set point in constant voltage mode.""",
        validator=strict_range,
        values=[0, 80],
    )

    current_limit = Channel.control(
        "VOLTAGE:STATIC:ILIMIT?",
        "VOLTAGE:STATIC:ILIMIT %g",
        """Control the current limit in constant voltage mode.""",
        validator=strict_range,
        values=[0, 20],
    )

    # CONSTANT POWER MODE
    power_setpoint_1 = Channel.control(
        "POWER:STATIC:L1?",
        "POWER:STATIC:L1 %g",
        """Control the L1 power set point in constant power mode.""",
        validator=strict_range,
        values=[0, 100],
    )

    power_setpoint_2 = Channel.control(
        "POWER:STATIC:L2?",
        "POWER:STATIC:L2 %g",
        """Control the L2 power set point in constant power mode.""",
        validator=strict_range,
        values=[0, 100],
    )

    # CONSTANT RESISTANCE MODE
    resistance_setpoint_1 = Channel.control(
        "RESISTANCE:STATIC:L1?",
        "RESISTANCE:STATIC:L1 %g",
        """Control the L1 resistance set point in constant resistance mode.""",
        validator=strict_range,
        values=[0.04, 12000],
    )

    resistance_setpoint_2 = Channel.control(
        "RESISTANCE:STATIC:L2?",
        "RESISTANCE:STATIC:L2 %g",
        """Control the L2 resistance set point in constant resistance mode.""",
        validator=strict_range,
        values=[0.04, 12000],
    )

    # CONSTANT IMPEDANCE MODE
    parallel_load_capacitance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:CL?",
        "IMPEDANCE:STATIC:CL %g",
        """Control the equivalent parallel load capacitance in constant impedance mode.""",
    )

    series_inductance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:LS?",
        "IMPEDANCE:STATIC:LS %g",
        """Control the equivalent series inductance in constant impedance mode.""",
    )

    series_resistance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:RS?",
        "IMPEDANCE:STATIC:RS %g",
        """Control the equivalent series resistance in constant impedance mode.""",
    )

    parallel_load_resistance_setpoint = Channel.control(
        "IMPEDANCE:STATIC:RL?",
        "IMPEDANCE:STATIC:RL %g",
        """Control the equivalent parallel load resistance in constant impedance mode.""",
    )


class Chroma63600(SCPIMixin, Instrument):
    """Control the Chroma 63600-5 Electronic Load Bank.

    Programming guide is UM-63600 (this interface is based on v2.6, Jan 2021), available from the
    Chroma USA website.
    https://www.chromausa.com/document-library/manuals-63600-series/
    """

    def __init__(self, adapter, name="Chroma 63600", **kwargs):
        super().__init__(adapter, name, read_termination="\n", **kwargs)

        # Populate a default channel for fallback
        self.add_child(Chroma63630_80_60, 1)
        # Auto-discover channels
        self.discover_channels()

    def discover_channels(self, Nslots: int = 5):
        """Discover and populate channels programmatically.

        The mainframe always leaves space for two channels per load (left and right).
        The 63610-80-20 has a left and right channel. Other loads (63630-80-60,
        6363-600-16, 63640-80-80, 63640-150-60) have a single channel per load.

        Note that even if a single-channel load is added, the channel ID increases by
        _two_. For example, adding five 63630-80-60 loads would result in having channels
        1, 3, 5, 7, and 9. If the third load were a 63610-80-20 (two channel load), the
        channels would be 1, 3, 5, 6, 7, and 9.

        :param Nslots: Number of mainframe slots in the unit, either 1, 2, or 5 for the -1, -2,
                       and -5 mainframes. For N slots, there are up to 2N channels.
        """
        # Reset channels
        if self.channels:
            channels_copy = self.channels.copy()
            for i, ch in channels_copy.items():
                self.remove_child(ch)

        # Auto-discover and add channels
        for i in range(1, Nslots * 2 + 1):
            if self.ask(f"CHAN {i};CHAN?") == str(i):
                # This channel exists, get its id and add it
                chid = self.ask("CHAN:ID?").split(",")[1]
                if chid == "63630-80-60":
                    self.add_child(Chroma63630_80_60, i)
                elif chid in ["63610-80-20L", "63610-80-20R"]:
                    self.add_child(Chroma63610_80_20, i)
                else:
                    raise NotImplementedError(
                        "Only Chroma 63610-80-20 and 63630-80-60 channels are currently supported."
                    )

    def enable_all(self, state: bool = True):
        """Set all electronic loads to ON (True) or OFF (False).
        :param state: True or False, determines Enabled state of loads.
        """
        for chid, ch in self.channels.items():
            ch.enabled = state

    currents = Instrument.measurement("MEAS:ALLC?", """Get all channel currents as a list.""")

    voltages = Instrument.measurement("MEAS:ALLV?", """Get all channel voltages as a list.""")

    powers = Instrument.measurement("MEAS:ALLP?", """Get all channel powers as a list.""")
