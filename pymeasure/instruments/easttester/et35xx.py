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

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set

import enum


class BiasSource(enum.Enum):
    """Supported bias voltage sources."""
    INTERNAL = enum.auto()
    EXTERNAL = enum.auto()


class MeasurementRange(enum.Enum):
    """Supported measurement ranges."""
    RANGE_30 = enum.auto()
    RANGE_100 = enum.auto()
    RANGE_300 = enum.auto()
    RANGE_1k = enum.auto()
    RANGE_3k = enum.auto()
    # RANGE_10k = enum.auto()
    RANGE_30k = enum.auto()
    # RANGE_100k = enum.auto()
    RANGE_300k = enum.auto()
    RANGE_1M = enum.auto()


class MeasurementSpeed(enum.Enum):
    """Supported measurement speeds."""
    FAST = enum.auto()
    MEDIUM = enum.auto()
    SLOW = enum.auto()
    CUSTOM = enum.auto()


class MeasurementType(enum.Enum):
    """Supported measurement types."""
    CpD = enum.auto()
    CpQ = enum.auto()
    CpG = enum.auto()
    CpRp = enum.auto()
    CsD = enum.auto()
    CsQ = enum.auto()
    CsRs = enum.auto()
    LpD = enum.auto()
    LpQ = enum.auto()
    LpG = enum.auto()
    LpRp = enum.auto()
    LsD = enum.auto()
    LsQ = enum.auto()
    LsRs = enum.auto()
    RX = enum.auto()
    ZDeg = enum.auto()
    ZRad = enum.auto()
    GB = enum.auto()
    YDeg = enum.auto()
    YRad = enum.auto()


class TriggerSource(enum.Enum):
    """Supported trigger sources."""
    INTERNAL = enum.auto()
    MANUAL = enum.auto()
    EXTERNAL = enum.auto()
    BUS = enum.auto()


class ET3510(SCPIMixin, Instrument):
    """Control an East Tester ET3510 LCR meter."""

    def __init__(self, adapter, name="East Tester ET3510", **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination='\n',
            **kwargs
        )

    BiasSource = BiasSource
    MeasurementRange = MeasurementRange
    MeasurementSpeed = MeasurementSpeed
    MeasurementType = MeasurementType
    TriggerSource = TriggerSource

    BOOL_TO_ON_OFF = {True: "ON", False: "OFF"}

    #
    # AMPLitude subsystem
    #
    automatic_level_control = Instrument.control(
        "AMPL:ALC?", "AMPL:ALC %s",
        """Get or set automatic level control.""",
        map_values=True,
        validator=strict_discrete_set,
        values=BOOL_TO_ON_OFF,
    )

    #
    # APERture subsystem
    #
    measurement_speed = Instrument.control(
        "APER?", "APER %s",
        """Get or set the measurement speed.""",
        map_values=True,
        validator=strict_discrete_set,
        values={
            MeasurementSpeed.FAST: "FAST",
            MeasurementSpeed.MEDIUM: "MEDium",
            MeasurementSpeed.SLOW: "SLOW",
        },
        maxsplit=0,
        get_process=lambda v: ET3510._process_response_APER(v),
    )

    def _process_response_APER(resp):
        return resp.split(',')[0]

    #
    # BIAS subsystem
    #
    bias_source = Instrument.control(
        "BIAS:STAT?", "BIAS:STAT %d",
        """Get or set the type of bias.""",
        map_values=True,
        validator=strict_discrete_set,
        values={
            BiasSource.INTERNAL: 1,
            BiasSource.EXTERNAL: 2,
        },
    )

    bias_voltage = Instrument.control(
        "BIAS:VOLT:LEV?", "BIAS:VOLT:LEV %f",
        """Get or set the internal bias voltage.""",
        validator=strict_range,
        values=[-2, 2],
    )

    #
    # FETCh subsystem
    #
    impedance = Instrument.measurement(
        "FETC:IMP:FORM?",
        """Get the formatted impedance.""",
    )
    monitor_voltage_ac = Instrument.measurement(
        "FETC:SMON:VAC?",
        """Get the latest AC voltage monitor value.""",
    )
    monitor_current_ac = Instrument.measurement(
        "FETC:SMON:IAC?",
        """Get the latest AC current monitor value.""",
    )
    monitor_voltage_dc_bias = Instrument.measurement(
        "FETC:SMON:EBV?",
        """Get the latest DC bias voltage monitor value.""",
    )

    #
    # FREQuency subsystem
    #
    frequency = Instrument.control(
        "FREQ?", "FREQ %f",
        """Get or set the frequency.""",
        validator=strict_range,
        values=[10, 10001000]
    )

    #
    # FUNCtion subsystem
    #
    measurement_type = Instrument.control(
        "FUNC:IMP:TYPE?", "FUNC:IMP:TYPE %s",
        """Get or set the type of measurement.""",
        map_values=True,
        validator=strict_discrete_set,
        values={
            MeasurementType.CpD: "CPD",
            MeasurementType.CpQ: "CPQ",
            MeasurementType.CpG: "CPG",
            MeasurementType.CpRp: "CPRP",
            MeasurementType.CsD: "CSD",
            MeasurementType.CsQ: "CSQ",
            MeasurementType.CsRs: "CSRS",
            MeasurementType.LpD: "LPD",
            MeasurementType.LpQ: "LPQ",
            MeasurementType.LpG: "LPG",
            MeasurementType.LpRp: "LPRP",
            MeasurementType.LsD: "LSD",
            MeasurementType.LsQ: "LSQ",
            MeasurementType.LsRs: "LSRS",
            MeasurementType.RX: "RX",
            MeasurementType.ZDeg: "ZTD",
            MeasurementType.ZRad: "ZTR",
            MeasurementType.GB: "GB",
            MeasurementType.YDeg: "YTD",
            MeasurementType.YRad: "YTR",
        },
    )
    measurement_auto_range = Instrument.control(
        "FUNC:IMP:RANG:AUTO?", "FUNC:IMP:RANG:AUTO %s",
        """Get or set the state of auto ranging.""",
        map_values=True,
        validator=strict_discrete_set,
        values=BOOL_TO_ON_OFF,
    )
    # FIXME(kpet): Manually setting the 10k or 100k range does not work for me.
    measurement_range = Instrument.control(
        "FUNC:IMP:RANG?", "FUNC:IMP:RANG %d",
        """Get or set the measurement range.""",
        map_values=True,
        validator=strict_discrete_set,
        values={
            MeasurementRange.RANGE_30: 30,
            MeasurementRange.RANGE_100: 100,
            MeasurementRange.RANGE_300: 300,
            MeasurementRange.RANGE_1k: 1000,
            MeasurementRange.RANGE_3k: 3000,
            # MeasurementRange.RANGE_10k: 10000,
            MeasurementRange.RANGE_30k: 30000,
            # MeasurementRange.RANGE_100k: 100000,
            MeasurementRange.RANGE_300k: 300000,
            MeasurementRange.RANGE_1M: 1000000,
        },
    )

    #
    # SYSTtem subsystem
    #
    beeper_enabled = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %s",
        """Get or set the state of the beeper.""",
        map_values=True,
        validator=strict_discrete_set,
        values=BOOL_TO_ON_OFF,
    )

    keypad_lock = Instrument.control(
        "SYST:KLOC?", "SYST:KLOC %s",
        """Get or set the keypad lock.""",
        map_values=True,
        validator=strict_discrete_set,
        values=BOOL_TO_ON_OFF,
    )

    def beep(self):
        self.write("SYST:BEEP:IMM")

    #
    # TRIGger subsystem
    #
    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """Get or set the trigger source.""",
        map_values=True,
        validator=strict_discrete_set,
        values={
            TriggerSource.INTERNAL: "INTernal",
            TriggerSource.MANUAL: "HOLD",
            TriggerSource.EXTERNAL: "EXTernal",
            TriggerSource.BUS: "BUS",
        },
    )

    trigger_delay = Instrument.control(
        "TRIG:TDEL?", "TRIG:TDEL %d",
        """Get or set the trigger delay time.""",
        validator=strict_range,
        values=[0, 10],
    )

    def trigger(self):
        self.write("TRIG:IMM")

    #
    # VOLTage subsystem
    #
    voltage = Instrument.control(
        "VOLT?", "VOLT %f",
        """Get or set the stimulus voltage.""",
        validator=strict_range,
        values=[10e-03, 2],
    )
