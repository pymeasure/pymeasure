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

from datetime import date as Date

import numpy as np

from pymeasure.instruments import AdapterType, Channel, Instrument
from pymeasure.instruments.common_base import InstrumentProperty, cast_or_str, identity
from pymeasure.instruments.validators import strict_discrete_set, strict_range

from .rigol_oscilloscope import (
    RigolOscilloscope,
    RigolOscilloscopeChannel,
    _parse_ieee_block,
)

PROBE_ATTENUATIONS = [
    0.0001,
    0.0002,
    0.0005,
    0.001,
    0.002,
    0.005,
    0.01,
    0.02,
    0.05,
    0.1,
    0.2,
    0.5,
    1,
    2,
    5,
    10,
    20,
    50,
    100,
    200,
    500,
    1_000,
    2_000,
    5_000,
    10_000,
    20_000,
    50_000,
]

WAVEFORM_SOURCES = [
    *[f"D{number}" for number in range(16)],
    *[f"CHAN{number}" for number in range(1, 5)],
    *[f"MATH{number}" for number in range(1, 5)],
]

MEASUREMENT_THRESHOLD_SOURCES = [
    *[f"CHAN{number}" for number in range(1, 5)],
    *[f"MATH{number}" for number in range(1, 5)],
]

MEASUREMENT_ITEMS = {
    "VMAX": "VMAX",
    "VMIN": "VMIN",
    "VPP": "VPP",
    "VTOP": "VTOP",
    "VBASE": "VBASE",
    "VAMP": "VAMP",
    "VAVG": "VAVG",
    "VRMS": "VRMS",
    "OVER": "OVERSHOOT",
    "PRES": "PRESHOOT",
    "MAR": "MAREA",
    "MPAR": "MPAREA",
    "PER": "PERIOD",
    "FREQ": "FREQUENCY",
    "RTIM": "RTIME",
    "FTIM": "FTIME",
    "PWID": "PWIDTH",
    "NWID": "NWIDTH",
    "PDUT": "PDUTY",
    "NDUT": "NDUTY",
    "TVMAX": "TVMAX",
    "TVMIN": "TVMIN",
    "PSL": "PSLEWRATE",
    "NSL": "NSLEWRATE",
    "VUPP": "VUPPER",
    "VMID": "VMID",
    "VLOW": "VLOWER",
    "VAR": "VARIANCE",
    "PVRMS": "PVRMS",
    "PPUL": "PPULSES",
    "NPUL": "NPULSES",
    "PEDG": "PEDGES",
    "NEDG": "NEDGES",
    "RRD": "RRDELAY",
    "RFD": "RFDELAY",
    "FRD": "FRDELAY",
    "FFD": "FFDELAY",
    "RRP": "RRPHASE",
    "RFP": "RFPHASE",
    "FRP": "FRPHASE",
    "FFP": "FFPHASE",
}

MEASUREMENT_STATISTIC_TYPES = {
    "MAX": "MAXIMUM",
    "MIN": "MINIMUM",
    "CURR": "CURRENT",
    "AVER": "AVERAGES",
    "DEV": "DEVIATION",
    "CNT": "CNT",
}

ANALOG_SOURCES = [f"CHAN{number}" for number in range(1, 5)]
CURSOR_MANUAL_SOURCES = [
    *ANALOG_SOURCES,
    *[f"MATH{number}" for number in range(1, 5)],
    "LA",
    "NONE",
]
CURSOR_TRACK_SOURCES = [
    *ANALOG_SOURCES,
    *[f"MATH{number}" for number in range(1, 5)],
    "NONE",
]
MATH_SOURCES = [
    *ANALOG_SOURCES,
    *[f"REF{number}" for number in range(1, 11)],
    *[f"MATH{number}" for number in range(1, 4)],
]
LOGIC_SOURCES = [*[f"D{number}" for number in range(16)], *ANALOG_SOURCES]
REFERENCE_SOURCES = [
    *[f"D{number}" for number in range(16)],
    *ANALOG_SOURCES,
    *[f"MATH{number}" for number in range(1, 5)],
]

TRIGGER_SOURCES = [
    *[f"D{number}" for number in range(16)],
    *[f"CHAN{number}" for number in range(1, 5)],
]

CSV_CHANNELS = ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "POD1", "POD2"]


DIGITAL_SOURCES = [f"D{number}" for number in range(16)]
PROTOCOL_SOURCES = [*DIGITAL_SOURCES, *ANALOG_SOURCES]
PROTOCOL_SOURCES_WITH_OFF = [*PROTOCOL_SOURCES, "OFF"]
LOGIC_DISPLAY_SOURCES = [
    *DIGITAL_SOURCES,
    *[f"GRO{number}" for number in range(1, 5)],
    "POD1",
    "POD2",
]
LOGIC_GROUPS = [f"GRO{number}" for number in range(1, 5)]
BUS_THRESHOLD_TYPES = [
    "PAL",
    "TX",
    "RX",
    "SCL",
    "SDA",
    "CS",
    "CLK",
    "MISO",
    "MOSI",
    "LIN",
    "CAN",
    "CANSUB1",
    "FLEX",
    "1553",
]

SYSTEM_KEYS = [
    "CH1",
    "CH2",
    "CH3",
    "CH4",
    "MATH",
    "REF",
    "LA",
    "DECODE",
    "MOFF",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "NPREVIOUS",
    "NNEXT",
    "NSTOP",
    "VOFFSET1",
    "VOFFSET2",
    "VOFFSET3",
    "VOFFSET4",
    "VSCALE1",
    "VSCALE2",
    "VSCALE3",
    "VSCALE4",
    "HSCALE",
    "HPOSITION",
    "KFUNCTION",
    "TLEVEL",
    "TMENU",
    "TMODE",
    "DEFAULT",
    "CLEAR",
    "AUTO",
    "RSTOP",
    "SINGLE",
    "QUICK",
    "MEASURE",
    "ACQUIRE",
    "STORAGE",
    "CURSOR",
    "DISPLAY",
    "UTILITY",
    "FORCE",
    "GENERATOR1",
    "GENERATOR2",
    "BACK",
    "TOUCH",
    "ZOOM",
    "SEARCH",
]

SYSTEM_KNOBS = [
    "VOFFSET1",
    "VOFFSET2",
    "VOFFSET3",
    "VOFFSET4",
    "VSCALE1",
    "VSCALE2",
    "VSCALE3",
    "VSCALE4",
    "HSCALE",
    "HPOSITION",
    "KFUNCTION",
    "TLEVEL",
]

OPTION_TYPES = [
    "BW071",
    "BW072",
    "BW073",
    "BW12",
    "BW13",
    "BW23",
    "RL2",
    "4CH",
    "BND",
    "COMP",
    "EMBD",
    "AUTO",
    "FLEX",
    "AUDIO",
    "AERO",
    "AWG",
    "PWR",
]


def _validate_system_date(value: tuple[int, int, int], _values: None) -> str:
    """Validate and serialize a system date."""
    try:
        year, month, day = value
        parsed = Date(year, month, day)
    except (TypeError, ValueError) as exc:
        raise ValueError("System date must be a valid (year, month, day) tuple.") from exc
    if not 2017 <= parsed.year <= 2099:
        raise ValueError("System date year must be from 2017 to 2099.")
    return f"{parsed.year},{parsed.month},{parsed.day}"


def _validate_system_time(value: tuple[int, int, int], _values: None) -> str:
    """Validate and serialize a system time."""
    try:
        hours, minutes, seconds = value
    except (TypeError, ValueError) as exc:
        raise ValueError("System time must be an (hours, minutes, seconds) tuple.") from exc
    if not all(isinstance(item, int) for item in (hours, minutes, seconds)):
        raise ValueError("System time values must be integers.")
    if not (0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59):
        raise ValueError("System time must be within 00:00:00 and 23:59:59.")
    return f"{hours},{minutes},{seconds}"


def _validate_trigger_pattern(
    pattern: list[str] | tuple[str, ...], constraints: tuple[frozenset[str], int]
) -> str:
    """Validate and serialize a complete 20-channel trigger pattern."""
    allowed_values, maximum_edges = constraints
    if not isinstance(pattern, (list, tuple)) or len(pattern) != 20:
        raise ValueError("A trigger pattern must contain exactly 20 channel values.")
    if any(value not in allowed_values for value in pattern):
        raise ValueError(f"Trigger pattern values must belong to {sorted(allowed_values)}.")
    if sum(value in {"R", "F"} for value in pattern) > maximum_edges:
        raise ValueError("A Pattern-trigger pattern can contain at most one edge.")
    return ",".join(pattern)


def _validate_scpi_keyword(value: str, keywords: dict[str, str], name: str) -> str:
    """Validate a SCPI keyword in any documented short-to-long form."""
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    value = value.upper()
    if any(full.startswith(value) and len(value) >= len(short) for short, full in keywords.items()):
        return value
    raise ValueError(f"{name} must be a documented SCPI value.")


def _validate_nonnegative_integer(value: int, _values: None) -> int:
    """Validate an integer whose upper limit depends on current instrument state."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("Value must be a non-negative integer.")
    return value


def _validate_positive_integer(value: int, _values: None) -> int:
    """Validate a positive integer whose upper limit depends on instrument state."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError("Value must be a positive integer.")
    return value


class MeasurementSubsystem(Channel):
    """Represent automatic-measurement configuration and results."""

    source = Channel.control(
        ":MEAS:SOUR?",
        ":MEAS:SOUR %s",
        """Control the source of the current measurement parameter (str).""",
        validator=strict_discrete_set,
        values=WAVEFORM_SOURCES,
        cast=str,
    )

    threshold_source = Channel.setting(
        ":MEAS:THR:SOUR %s",
        """Set the analog or math source whose measurement thresholds are configured.""",
        validator=strict_discrete_set,
        values=MEASUREMENT_THRESHOLD_SOURCES,
    )

    mode = Channel.control(
        ":MEAS:MODE?",
        ":MEAS:MODE %s",
        """Control the measurement mode: ``"NORM"`` or ``"PREC"``.""",
        validator=strict_discrete_set,
        values=["NORM", "PREC"],
        cast=str,
    )

    am_source = Channel.control(
        ":MEAS:AMS?",
        ":MEAS:AMS %s",
        """Control the source for displaying all measurement values (str).""",
        validator=strict_discrete_set,
        values=[*[f"CHAN{number}" for number in range(1, 5)], "OFF"],
        cast=str,
    )

    setup_max = Channel.control(
        ":MEAS:SET:MAX?",
        ":MEAS:SET:MAX %d",
        """Control the upper measurement threshold (int from -100 to 100).

        The instrument interprets the value according to its percentage or absolute
        threshold type.
        """,
        validator=strict_range,
        values=[-100, 100],
        cast=int,
    )

    setup_mid = Channel.control(
        ":MEAS:SET:MID?",
        ":MEAS:SET:MID %d",
        """Control the middle measurement threshold (int from -100 to 100).""",
        validator=strict_range,
        values=[-100, 100],
        cast=int,
    )

    setup_min = Channel.control(
        ":MEAS:SET:MIN?",
        ":MEAS:SET:MIN %d",
        """Control the lower measurement threshold (int from -100 to 100).""",
        validator=strict_range,
        values=[-100, 100],
        cast=int,
    )

    setup_primary_source_a = Channel.control(
        ":MEAS:SET:PSA?",
        ":MEAS:SET:PSA %s",
        """Control source A for phase or delay measurement (str).""",
        validator=strict_discrete_set,
        values=WAVEFORM_SOURCES,
        cast=str,
    )

    setup_primary_source_b = Channel.control(
        ":MEAS:SET:PSB?",
        ":MEAS:SET:PSB %s",
        """Control source B for phase or delay measurement (str).""",
        validator=strict_discrete_set,
        values=WAVEFORM_SOURCES,
        cast=str,
    )

    setup_digital_source_a = Channel.control(
        ":MEAS:SET:DSA?",
        ":MEAS:SET:DSA %s",
        """Control source A for phase or delay measurement (str).""",
        validator=strict_discrete_set,
        values=WAVEFORM_SOURCES,
        cast=str,
    )

    setup_digital_source_b = Channel.control(
        ":MEAS:SET:DSB?",
        ":MEAS:SET:DSB %s",
        """Control source B for phase or delay measurement (str).""",
        validator=strict_discrete_set,
        values=WAVEFORM_SOURCES,
        cast=str,
    )

    statistics_display_enabled = Channel.control(
        ":MEAS:STAT:DISP?",
        ":MEAS:STAT:DISP %d",
        """Control whether measurement statistics are displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    area = Channel.control(
        ":MEAS:AREA?",
        ":MEAS:AREA %s",
        """Control the measurement range: ``"MAIN"``, ``"ZOOM"``, or ``"CURS"``.""",
        validator=strict_discrete_set,
        values=["MAIN", "ZOOM", "CURS"],
        cast=str,
    )

    cregion_cursor_a_x = Channel.control(
        ":MEAS:CREG:CAX?",
        ":MEAS:CREG:CAX %d",
        """Control Cursor A's horizontal pixel coordinate (int from 0 to 1000).""",
        validator=strict_range,
        values=[0, 1000],
        cast=int,
    )

    cregion_cursor_b_x = Channel.control(
        ":MEAS:CREG:CBX?",
        ":MEAS:CREG:CBX %d",
        """Control Cursor B's horizontal pixel coordinate (int from 0 to 1000).""",
        validator=strict_range,
        values=[0, 1000],
        cast=int,
    )

    category = Channel.control(
        ":MEAS:CAT?",
        ":MEAS:CAT %d",
        """Control the measurement category: 0 horizontal, 1 vertical, or 2 other.""",
        validator=strict_range,
        values=[0, 2],
        cast=int,
    )

    @staticmethod
    def _item_arguments(item: str, source_a: str | None, source_b: str | None) -> str:
        item = _validate_scpi_keyword(item, MEASUREMENT_ITEMS, "Measurement item")
        if source_b is not None and source_a is None:
            raise ValueError("Source B requires source A.")
        arguments = [item]
        if source_a is not None:
            arguments.append(strict_discrete_set(source_a, WAVEFORM_SOURCES))
        if source_b is not None:
            arguments.append(strict_discrete_set(source_b, WAVEFORM_SOURCES))
        return ",".join(arguments)

    @staticmethod
    def _parse_result(result: str) -> float:
        try:
            return float(result.strip())
        except ValueError:
            return float("nan")

    def clear(self, item: str = "ALL") -> None:
        """Clear a displayed measurement item, from ``"ITEM1"`` to ``"ITEM10"``, or all.

        :param item: Measurement display slot to clear, or ``"ALL"``.
        """
        item = strict_discrete_set(item, [*[f"ITEM{number}" for number in range(1, 11)], "ALL"])
        self.write(f":MEAS:CLE {item}")

    def reset_thresholds(self) -> None:
        """Restore the automatic-measurement threshold levels to their defaults."""
        self.write(":MEAS:THR:DEF")

    def reset_statistics(self) -> None:
        """Clear accumulated measurement statistics and start them again."""
        self.write(":MEAS:STAT:RES")

    def enable_item(
        self, item: str, source_a: str | None = None, source_b: str | None = None
    ) -> None:
        """Enable a measurement item for one or two optional sources.

        :param item: Documented automatic-measurement item.
        :param source_a: Optional first waveform source.
        :param source_b: Optional second waveform source for dual-source measurements.
        """
        self.write(f":MEAS:ITEM {self._item_arguments(item, source_a, source_b)}")

    def item(self, item: str, source_a: str | None = None, source_b: str | None = None) -> float:
        """Return the current value of a measurement item for optional sources.

        :param item: Documented automatic-measurement item.
        :param source_a: Optional first waveform source.
        :param source_b: Optional second waveform source for dual-source measurements.
        """
        arguments = self._item_arguments(item, source_a, source_b)
        return self._parse_result(self.ask(f":MEAS:ITEM? {arguments}"))

    def enable_statistic_item(
        self, item: str, source_a: str | None = None, source_b: str | None = None
    ) -> None:
        """Enable statistics for a measurement item and optional sources.

        :param item: Documented automatic-measurement item.
        :param source_a: Optional first waveform source.
        :param source_b: Optional second waveform source for dual-source measurements.
        """
        self.write(f":MEAS:STAT:ITEM {self._item_arguments(item, source_a, source_b)}")

    def statistic_item(
        self,
        statistic_type: str,
        item: str,
        source_a: str | None = None,
        source_b: str | None = None,
    ) -> float:
        """Return one statistic for a measurement item and optional sources.

        :param statistic_type: Statistic type such as ``"CURR"``, ``"MAX"``, or ``"DEV"``.
        :param item: Documented automatic-measurement item.
        :param source_a: Optional first waveform source.
        :param source_b: Optional second waveform source for dual-source measurements.
        """
        statistic_type = _validate_scpi_keyword(
            statistic_type, MEASUREMENT_STATISTIC_TYPES, "Statistic type"
        )
        arguments = self._item_arguments(item, source_a, source_b)
        return self._parse_result(self.ask(f":MEAS:STAT:ITEM? {statistic_type},{arguments}"))


class CursorSubsystem(Channel):
    """Represent cursor configuration and cursor measurement results."""

    measurement_indicator_enabled = Channel.control(
        ":CURS:MEAS:IND?",
        ":CURS:MEAS:IND %d",
        """Control whether the automatic-measurement cursor is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    mode = Channel.control(
        ":CURS:MODE?",
        ":CURS:MODE %s",
        """Control the cursor mode: OFF, MAN, TRAC, XY, or MEAS.""",
        validator=strict_discrete_set,
        values=["OFF", "MAN", "TRAC", "XY", "MEAS"],
        cast=str,
    )

    manual_type = Channel.control(
        ":CURS:MAN:TYPE?",
        ":CURS:MAN:TYPE %s",
        """Control the manual cursor type: TIME or AMPL.""",
        validator=strict_discrete_set,
        values=["TIME", "AMPL"],
        cast=str,
    )

    manual_source = Channel.control(
        ":CURS:MAN:SOUR?",
        ":CURS:MAN:SOUR %s",
        """Control the source for manual cursor measurements (str).""",
        validator=strict_discrete_set,
        values=CURSOR_MANUAL_SOURCES,
        cast=str,
    )

    manual_time_unit = Channel.control(
        ":CURS:MAN:TUN?",
        ":CURS:MAN:TUN %s",
        """Control the manual cursor horizontal unit: SEC, HZ, DEGR, or PERC.""",
        validator=strict_discrete_set,
        values=["SEC", "HZ", "DEGR", "PERC"],
        cast=str,
    )

    manual_vertical_unit = Channel.control(
        ":CURS:MAN:VUN?",
        ":CURS:MAN:VUN %s",
        """Control the manual cursor vertical unit: SOUR or PERC.""",
        validator=strict_discrete_set,
        values=["SOUR", "PERC"],
        cast=str,
    )

    manual_cursor_a_x = Channel.control(
        ":CURS:MAN:CAX?",
        ":CURS:MAN:CAX %d",
        """Control Cursor A's horizontal screen coordinate (int from 0 to 999).""",
        validator=strict_range,
        values=[0, 999],
        cast=int,
    )

    manual_cursor_b_x = Channel.control(
        ":CURS:MAN:CBX?",
        ":CURS:MAN:CBX %d",
        """Control Cursor B's horizontal screen coordinate (int from 0 to 999).""",
        validator=strict_range,
        values=[0, 999],
        cast=int,
    )

    manual_cursor_a_y = Channel.control(
        ":CURS:MAN:CAY?",
        ":CURS:MAN:CAY %d",
        """Control Cursor A's vertical screen coordinate (int from 0 to 479).""",
        validator=strict_range,
        values=[0, 479],
        cast=int,
    )

    manual_cursor_b_y = Channel.control(
        ":CURS:MAN:CBY?",
        ":CURS:MAN:CBY %d",
        """Control Cursor B's vertical screen coordinate (int from 0 to 479).""",
        validator=strict_range,
        values=[0, 479],
        cast=int,
    )

    manual_cursor_a_x_value = Channel.measurement(
        ":CURS:MAN:AXV?",
        """Measure Cursor A's horizontal value in the selected unit (float).""",
        cast=float,
    )

    manual_cursor_a_y_value = Channel.measurement(
        ":CURS:MAN:AYV?",
        """Measure Cursor A's vertical value in the selected unit (float).""",
        cast=float,
    )

    manual_cursor_b_x_value = Channel.measurement(
        ":CURS:MAN:BXV?",
        """Measure Cursor B's horizontal value in the selected unit (float).""",
        cast=float,
    )

    manual_cursor_b_y_value = Channel.measurement(
        ":CURS:MAN:BYV?",
        """Measure Cursor B's vertical value in the selected unit (float).""",
        cast=float,
    )

    manual_x_delta = Channel.measurement(
        ":CURS:MAN:XDEL?",
        """Measure the manual cursor horizontal difference (float).""",
        cast=float,
    )

    manual_inverse_x_delta = Channel.measurement(
        ":CURS:MAN:IXD?",
        """Measure the reciprocal absolute manual cursor horizontal difference (float).""",
        cast=float,
    )

    manual_y_delta = Channel.measurement(
        ":CURS:MAN:YDEL?",
        """Measure the manual cursor vertical difference (float).""",
        cast=float,
    )

    track_source1 = Channel.control(
        ":CURS:TRAC:SOUR1?",
        ":CURS:TRAC:SOUR1 %s",
        """Control the track-mode source for Cursor A (str).""",
        validator=strict_discrete_set,
        values=CURSOR_TRACK_SOURCES,
        cast=str,
    )

    track_source2 = Channel.control(
        ":CURS:TRAC:SOUR2?",
        ":CURS:TRAC:SOUR2 %s",
        """Control the track-mode source for Cursor B (str).""",
        validator=strict_discrete_set,
        values=CURSOR_TRACK_SOURCES,
        cast=str,
    )

    track_cursor_a_x = Channel.control(
        ":CURS:TRAC:CAX?",
        ":CURS:TRAC:CAX %d",
        """Control Cursor A's horizontal screen coordinate (int from 0 to 999).""",
        validator=strict_range,
        values=[0, 999],
        cast=int,
    )

    track_cursor_b_x = Channel.control(
        ":CURS:TRAC:CBX?",
        ":CURS:TRAC:CBX %d",
        """Control Cursor B's horizontal screen coordinate (int from 0 to 999).""",
        validator=strict_range,
        values=[0, 999],
        cast=int,
    )

    track_cursor_a_y = Channel.measurement(
        ":CURS:TRAC:CAY?",
        """Measure Cursor A's vertical screen coordinate (int).""",
        cast=int,
    )

    track_cursor_b_y = Channel.measurement(
        ":CURS:TRAC:CBY?",
        """Measure Cursor B's vertical screen coordinate (int).""",
        cast=int,
    )

    track_cursor_a_x_value = Channel.measurement(
        ":CURS:TRAC:AXV?",
        """Measure Cursor A's horizontal track value (float).""",
        cast=float,
    )

    track_cursor_a_y_value = Channel.measurement(
        ":CURS:TRAC:AYV?",
        """Measure Cursor A's vertical track value (float).""",
        cast=float,
    )

    track_cursor_b_x_value = Channel.measurement(
        ":CURS:TRAC:BXV?",
        """Measure Cursor B's horizontal track value (float).""",
        cast=float,
    )

    track_cursor_b_y_value = Channel.measurement(
        ":CURS:TRAC:BYV?",
        """Measure Cursor B's vertical track value (float).""",
        cast=float,
    )

    track_x_delta = Channel.measurement(
        ":CURS:TRAC:XDEL?",
        """Measure the track cursor horizontal difference (float).""",
        cast=float,
    )

    track_y_delta = Channel.measurement(
        ":CURS:TRAC:YDEL?",
        """Measure the track cursor vertical difference (float).""",
        cast=float,
    )

    track_inverse_x_delta = Channel.measurement(
        ":CURS:TRAC:IXD?",
        """Measure the reciprocal absolute track cursor horizontal difference (float).""",
        cast=float,
    )

    xy_ax = Channel.control(
        ":CURS:XY:AX?",
        ":CURS:XY:AX %d",
        """Control Cursor A's horizontal XY coordinate (int from 0 to 479).""",
        validator=strict_range,
        values=[0, 479],
        cast=int,
    )

    xy_bx = Channel.control(
        ":CURS:XY:BX?",
        ":CURS:XY:BX %d",
        """Control Cursor B's horizontal XY coordinate (int from 0 to 479).""",
        validator=strict_range,
        values=[0, 479],
        cast=int,
    )

    xy_ay = Channel.control(
        ":CURS:XY:AY?",
        ":CURS:XY:AY %d",
        """Control Cursor A's vertical XY coordinate (int from 0 to 479).""",
        validator=strict_range,
        values=[0, 479],
        cast=int,
    )

    xy_by = Channel.control(
        ":CURS:XY:BY?",
        ":CURS:XY:BY %d",
        """Control Cursor B's vertical XY coordinate (int from 0 to 479).""",
        validator=strict_range,
        values=[0, 479],
        cast=int,
    )

    xy_cursor_a_x_value = Channel.measurement(
        ":CURS:XY:AXV?",
        """Measure Cursor A's horizontal XY value (float).""",
        cast=float,
    )

    xy_cursor_a_y_value = Channel.measurement(
        ":CURS:XY:AYV?",
        """Measure Cursor A's vertical XY value (float).""",
        cast=float,
    )

    xy_cursor_b_x_value = Channel.measurement(
        ":CURS:XY:BXV?",
        """Measure Cursor B's horizontal XY value (float).""",
        cast=float,
    )

    xy_cursor_b_y_value = Channel.measurement(
        ":CURS:XY:BYV?",
        """Measure Cursor B's vertical XY value (float).""",
        cast=float,
    )


class DisplaySubsystem(Channel):
    """Represent waveform display configuration."""

    type = Channel.control(
        ":DISP:TYPE?",
        ":DISP:TYPE %s",
        """Control the waveform display type: VECT or DOTS.""",
        validator=strict_discrete_set,
        values=["VECT", "DOTS"],
        cast=str,
    )

    grading_time = Channel.control(
        ":DISP:GRAD:TIME?",
        ":DISP:GRAD:TIME %s",
        """Control persistence time in seconds, MIN, or INF (str).""",
        validator=strict_discrete_set,
        values=["MIN", "0.1", "0.2", "0.5", "1", "2", "5", "10", "INF"],
        cast=str,
    )

    waveform_brightness = Channel.control(
        ":DISP:WBR?",
        ":DISP:WBR %d",
        """Control waveform brightness in percent (int from 1 to 100).""",
        validator=strict_range,
        values=[1, 100],
        cast=int,
    )

    grid = Channel.control(
        ":DISP:GRID?",
        ":DISP:GRID %s",
        """Control the screen grid type: FULL, HALF, NONE, or IRE.""",
        validator=strict_discrete_set,
        values=["FULL", "HALF", "NONE", "IRE"],
        cast=str,
    )

    grid_brightness = Channel.control(
        ":DISP:GBR?",
        ":DISP:GBR %d",
        """Control screen grid brightness in percent (int from 1 to 100).""",
        validator=strict_range,
        values=[1, 100],
        cast=int,
    )

    rulers_enabled = Channel.control(
        ":DISP:RUL?",
        ":DISP:RUL %d",
        """Control whether rulers are displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    color_grading_enabled = Channel.control(
        ":DISP:COL?",
        ":DISP:COL %d",
        """Control whether color grading is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    def clear(self) -> None:
        """Clear all waveforms currently shown on the screen."""
        self.write(":DISP:CLE")


class HistogramSubsystem(Channel):
    """Represent waveform histogram configuration and boundaries."""

    enabled = Channel.control(
        ":HIST:DISP?",
        ":HIST:DISP %d",
        """Control whether the histogram function is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    type = Channel.control(
        ":HIST:TYPE?",
        ":HIST:TYPE %s",
        """Control the histogram type: HOR, VERT, or MEAS.""",
        validator=strict_discrete_set,
        values=["HOR", "VERT", "MEAS"],
        cast=str,
    )

    source = Channel.control(
        ":HIST:SOUR?",
        ":HIST:SOUR %s",
        """Control the histogram source: CHAN1 to CHAN4, or OFF.""",
        validator=strict_discrete_set,
        values=[*ANALOG_SOURCES, "OFF"],
        cast=str,
    )

    size = Channel.control(
        ":HIST:SIZE?",
        ":HIST:SIZE %d",
        """Control histogram height (int from 1 to 4).""",
        validator=strict_range,
        values=[1, 4],
        cast=int,
    )

    statistics_enabled = Channel.control(
        ":HIST:STAT?",
        ":HIST:STAT %d",
        """Control whether histogram statistics are enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    bottom_limit = Channel.control(
        ":HIST:BLIM?",
        ":HIST:BLIM %g",
        """Control the histogram bottom boundary in source units (float).""",
        cast=float,
    )

    left_limit = Channel.control(
        ":HIST:LLIM?",
        ":HIST:LLIM %g",
        """Control the histogram left boundary in seconds (float).""",
        cast=float,
    )

    right_limit = Channel.control(
        ":HIST:RLIM?",
        ":HIST:RLIM %g",
        """Control the histogram right boundary in seconds (float).""",
        cast=float,
    )

    top_limit = Channel.control(
        ":HIST:TLIM?",
        ":HIST:TLIM %g",
        """Control the histogram top boundary in source units (float).""",
        cast=float,
    )

    def reset(self) -> None:
        """Reset accumulated histogram statistics."""
        self.write(":HIST:RES")


class MaskSubsystem(Channel):
    """Represent pass/fail mask-test configuration and counters."""

    enabled = Channel.control(
        ":MASK:ENAB?",
        ":MASK:ENAB %d",
        """Control whether the pass/fail mask test is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    source = Channel.control(
        ":MASK:SOUR?",
        ":MASK:SOUR %s",
        """Control the enabled analog source used for mask testing (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    operate = Channel.control(
        ":MASK:OPER?",
        ":MASK:OPER %s",
        """Control mask-test operation: RUN or STOP.""",
        validator=strict_discrete_set,
        values=["RUN", "STOP"],
        cast=str,
    )

    statistics_display_enabled = Channel.control(
        ":MASK:MDIS?",
        ":MASK:MDIS %d",
        """Control whether mask-test statistics are displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    x = Channel.control(
        ":MASK:X?",
        ":MASK:X %g",
        """Control horizontal mask adjustment in divisions (float from 0.01 to 2).""",
        validator=strict_range,
        values=[0.01, 2],
        cast=float,
    )

    y = Channel.control(
        ":MASK:Y?",
        ":MASK:Y %g",
        """Control vertical mask adjustment in divisions (float from 0.04 to 2).""",
        validator=strict_range,
        values=[0.04, 2],
        cast=float,
    )

    passed = Channel.measurement(
        ":MASK:PASS?",
        """Measure the number of frames that passed the mask test (int).""",
        cast=int,
    )

    failed = Channel.measurement(
        ":MASK:FAIL?",
        """Measure the number of frames that failed the mask test (int).""",
        cast=int,
    )

    total = Channel.measurement(
        ":MASK:TOT?",
        """Measure the total number of mask-test frames (int).""",
        cast=int,
    )

    def create(self) -> None:
        """Create a mask from the current horizontal and vertical adjustments."""
        self.write(":MASK:CRE")

    def reset(self) -> None:
        """Reset the pass, fail, and total frame counters."""
        self.write(":MASK:RES")


class RecordingSubsystem(Channel):
    """Represent waveform recording and playback configuration."""

    enabled = Channel.control(
        ":REC:ENAB?",
        ":REC:ENAB %d",
        """Control whether waveform recording is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    recording_running = Channel.control(
        ":REC:STAR?",
        ":REC:STAR %d",
        """Control whether waveform recording is running (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    playback_running = Channel.control(
        ":REC:PLAY?",
        ":REC:PLAY %d",
        """Control whether waveform playback is running (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    current = Channel.control(
        ":REC:CURR?",
        ":REC:CURR %d",
        """Control the current playback frame (positive int within recorded frames).""",
        validator=_validate_positive_integer,
        values=None,
        cast=int,
    )

    frames = Channel.control(
        ":REC:FRAM?",
        ":REC:FRAM %d",
        """Control the requested recording frame count (positive int within capacity).""",
        validator=_validate_positive_integer,
        values=None,
        cast=int,
    )


class ReferenceSubsystem(Channel):
    """Represent global and per-slot reference-waveform configuration."""

    display_enabled = Channel.control(
        ":REF:DISP?",
        ":REF:DISP %d",
        """Control whether the reference-waveform function is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    label_enabled = Channel.control(
        ":REF:LAB:ENAB?",
        ":REF:LAB:ENAB %d",
        """Control whether all reference labels are displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    @staticmethod
    def _reference(reference: int) -> int:
        return strict_range(reference, [1, 10])

    def set_source(self, reference: int, source: str) -> None:
        """Set the source of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        :param source: Waveform source to copy into the reference slot.
        """
        reference = self._reference(reference)
        source = strict_discrete_set(source, REFERENCE_SOURCES)
        self.write(f":REF:SOUR {reference},{source}")

    def source(self, reference: int) -> str:
        """Return the source of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        return self.ask(f":REF:SOUR? {reference}").strip()

    def set_vertical_scale(self, reference: int, scale: float) -> None:
        """Set the vertical scale of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        :param scale: Vertical scale in the selected source unit per division.
        """
        reference = self._reference(reference)
        self.write(f":REF:VSC {reference},{scale:g}")

    def vertical_scale(self, reference: int) -> float:
        """Return the vertical scale of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        return float(self.ask(f":REF:VSC? {reference}"))

    def set_vertical_offset(self, reference: int, offset: float) -> None:
        """Set the vertical offset of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        :param offset: Vertical offset in the selected source unit.
        """
        reference = self._reference(reference)
        self.write(f":REF:VOFF {reference},{offset:g}")

    def vertical_offset(self, reference: int) -> float:
        """Return the vertical offset of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        return float(self.ask(f":REF:VOFF? {reference}"))

    def reset(self, reference: int) -> None:
        """Reset vertical scale and offset for reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        self.write(f":REF:RES {reference}")

    def select_current(self, reference: int) -> None:
        """Select the current reference slot from 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        self.write(f":REF:CURR {reference}")

    def set_color(self, reference: int, color: str) -> None:
        """Set the display color of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        :param color: Display color: ``"GRAY"``, ``"GRE"``, ``"BLUE"``, ``"RED"``, or ``"ORAN"``.
        """
        reference = self._reference(reference)
        color = strict_discrete_set(color, ["GRAY", "GRE", "BLUE", "RED", "ORAN"])
        self.write(f":REF:COL {reference},{color}")

    def color(self, reference: int) -> str:
        """Return the display color of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        return self.ask(f":REF:COL? {reference}").strip()

    def set_label_content(self, reference: int, content: str) -> None:
        """Set the label content of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        :param content: Label text sent to the instrument.
        """
        reference = self._reference(reference)
        if not isinstance(content, str):
            raise TypeError("Reference label content must be a string.")
        self.write(f":REF:LAB:CONT {reference},{content}")

    def label_content(self, reference: int) -> str:
        """Return the label content of reference slot 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = self._reference(reference)
        return self.ask(f":REF:LAB:CONT? {reference}").strip()


class MathChannel(Channel):
    """Represent one of the four math waveform channels."""

    display_enabled = Channel.control(
        ":MATH{ch}:DISP?",
        ":MATH{ch}:DISP %d",
        """Control whether this math waveform is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    operator = Channel.control(
        ":MATH{ch}:OPER?",
        ":MATH{ch}:OPER %s",
        """Control the math operator (str).""",
        validator=strict_discrete_set,
        values=[
            "ADD",
            "SUBT",
            "MULT",
            "DIV",
            "AND",
            "OR",
            "XOR",
            "NOT",
            "FFT",
            "INTG",
            "DIFF",
            "SQRT",
            "LOG",
            "LN",
            "EXP",
            "ABS",
            "LPAS",
            "HPAS",
            "BPAS",
            "BST",
            "AXB",
        ],
        cast=str,
    )

    source1 = Channel.control(
        ":MATH{ch}:SOUR1?",
        ":MATH{ch}:SOUR1 %s",
        """Control Source A, or the sole source, for arithmetic and function operations.""",
        validator=strict_discrete_set,
        values=MATH_SOURCES,
        cast=str,
    )

    source2 = Channel.control(
        ":MATH{ch}:SOUR2?",
        ":MATH{ch}:SOUR2 %s",
        """Control Source B for two-source arithmetic operations.""",
        validator=strict_discrete_set,
        values=MATH_SOURCES,
        cast=str,
    )

    left_source_1 = Channel.control(
        ":MATH{ch}:LSOU1?",
        ":MATH{ch}:LSOU1 %s",
        """Control Source A for logic operations (str).""",
        validator=strict_discrete_set,
        values=LOGIC_SOURCES,
        cast=str,
    )

    left_source_2 = Channel.control(
        ":MATH{ch}:LSOU2?",
        ":MATH{ch}:LSOU2 %s",
        """Control Source B for two-source logic operations (str).""",
        validator=strict_discrete_set,
        values=LOGIC_SOURCES,
        cast=str,
    )

    scale = Channel.control(
        ":MATH{ch}:SCAL?",
        ":MATH{ch}:SCAL %g",
        """Control the vertical scale in operator-dependent units (float).""",
        cast=float,
    )

    offset = Channel.control(
        ":MATH{ch}:OFFS?",
        ":MATH{ch}:OFFS %g",
        """Control vertical offset in operator-dependent units (float from -1e9 to 1e9).""",
        validator=strict_range,
        values=[-1e9, 1e9],
        cast=float,
    )

    inverted = Channel.control(
        ":MATH{ch}:INV?",
        ":MATH{ch}:INV %d",
        """Control whether non-FFT math results are displayed inverted (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    fft_source = Channel.control(
        ":MATH{ch}:FFT:SOUR?",
        ":MATH{ch}:FFT:SOUR %s",
        """Control the analog source for FFT operation (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    fft_window = Channel.control(
        ":MATH{ch}:FFT:WIND?",
        ":MATH{ch}:FFT:WIND %s",
        """Control the FFT window: RECT, BLAC, HANN, HAMM, FLAT, or TRI.""",
        validator=strict_discrete_set,
        values=["RECT", "BLAC", "HANN", "HAMM", "FLAT", "TRI"],
        cast=str,
    )

    fft_unit = Channel.control(
        ":MATH{ch}:FFT:UNIT?",
        ":MATH{ch}:FFT:UNIT %s",
        """Control the FFT vertical unit: VRMS or DB.""",
        validator=strict_discrete_set,
        values=["VRMS", "DB"],
        cast=str,
    )

    fft_scale = Channel.control(
        ":MATH{ch}:FFT:SCAL?",
        ":MATH{ch}:FFT:SCAL %g",
        """Control FFT vertical scale (float from 1e-9 to 5e9).""",
        validator=strict_range,
        values=[1e-9, 5e9],
        cast=float,
    )

    fft_offset = Channel.control(
        ":MATH{ch}:FFT:OFFS?",
        ":MATH{ch}:FFT:OFFS %g",
        """Control FFT vertical offset (float from -1e9 to 1e9).""",
        validator=strict_range,
        values=[-1e9, 1e9],
        cast=float,
    )

    fft_horizontal_scale = Channel.control(
        ":MATH{ch}:FFT:HSC?",
        ":MATH{ch}:FFT:HSC %g",
        """Control FFT frequency range in Hz (float from 10 to 5e9).""",
        validator=strict_range,
        values=[10, 5e9],
        cast=float,
    )

    fft_horizontal_center = Channel.control(
        ":MATH{ch}:FFT:HCEN?",
        ":MATH{ch}:FFT:HCEN %g",
        """Control FFT center frequency in Hz (float from -2.5e9 to 2.5e9).""",
        validator=strict_range,
        values=[-2.5e9, 2.5e9],
        cast=float,
    )

    fft_frequency_start = Channel.control(
        ":MATH{ch}:FFT:FREQ:STAR?",
        ":MATH{ch}:FFT:FREQ:STAR %g",
        """Control FFT start frequency in Hz (float from -2.5e9 to 2.5e9).""",
        validator=strict_range,
        values=[-2.5e9, 2.5e9],
        cast=float,
    )

    fft_frequency_end = Channel.control(
        ":MATH{ch}:FFT:FREQ:END?",
        ":MATH{ch}:FFT:FREQ:END %g",
        """Control FFT stop frequency in Hz (float from -2.5e9 to 2.5e9).""",
        validator=strict_range,
        values=[-2.5e9, 2.5e9],
        cast=float,
    )

    fft_search_enabled = Channel.control(
        ":MATH{ch}:FFT:SEAR:ENAB?",
        ":MATH{ch}:FFT:SEAR:ENAB %d",
        """Control whether FFT peak search is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    fft_search_num = Channel.control(
        ":MATH{ch}:FFT:SEAR:NUM?",
        ":MATH{ch}:FFT:SEAR:NUM %d",
        """Control the maximum FFT peak count (int from 1 to 15).""",
        validator=strict_range,
        values=[1, 15],
        cast=int,
    )

    fft_search_threshold = Channel.control(
        ":MATH{ch}:FFT:SEAR:THR?",
        ":MATH{ch}:FFT:SEAR:THR %g",
        """Control the FFT peak-search threshold in current FFT units (float).""",
        cast=float,
    )

    fft_search_excursion = Channel.control(
        ":MATH{ch}:FFT:SEAR:EXC?",
        ":MATH{ch}:FFT:SEAR:EXC %g",
        """Control FFT peak-search excursion in current FFT units (float).""",
        cast=float,
    )

    fft_search_order = Channel.control(
        ":MATH{ch}:FFT:SEAR:ORD?",
        ":MATH{ch}:FFT:SEAR:ORD %s",
        """Control FFT peak-search ordering: AMP or FREQ.""",
        validator=strict_discrete_set,
        values=["AMP", "FREQ"],
        cast=str,
    )

    filter_type = Channel.control(
        ":MATH{ch}:FILT:TYPE?",
        ":MATH{ch}:FILT:TYPE %s",
        """Control the filter type: LPAS, HPAS, BPAS, or BST.""",
        validator=strict_discrete_set,
        values=["LPAS", "HPAS", "BPAS", "BST"],
        cast=str,
    )

    filter_w1 = Channel.control(
        ":MATH{ch}:FILT:W1?",
        ":MATH{ch}:FILT:W1 %g",
        """Control filter cutoff frequency 1 in Hz (float within the dynamic range).""",
        cast=float,
    )

    filter_w2 = Channel.control(
        ":MATH{ch}:FILT:W2?",
        ":MATH{ch}:FILT:W2 %g",
        """Control filter cutoff frequency 2 in Hz (float within the dynamic range).""",
        cast=float,
    )

    sensitivity = Channel.control(
        ":MATH{ch}:SENS?",
        ":MATH{ch}:SENS %g",
        """Control logic-operation sensitivity in divisions (float from 0.1 to 1).""",
        validator=strict_range,
        values=[0.1, 1],
        cast=float,
    )

    distance = Channel.control(
        ":MATH{ch}:DIST?",
        ":MATH{ch}:DIST %d",
        """Control differential smoothing window width (int from 5 to 10000).""",
        validator=strict_range,
        values=[5, 10_000],
        cast=int,
    )

    threshold1 = Channel.control(
        ":MATH{ch}:THR1?",
        ":MATH{ch}:THR1 %g",
        """Control the Channel 1 logic threshold in Volts (float within the dynamic range).""",
        cast=float,
    )

    threshold2 = Channel.control(
        ":MATH{ch}:THR2?",
        ":MATH{ch}:THR2 %g",
        """Control the Channel 2 logic threshold in Volts (float within the dynamic range).""",
        cast=float,
    )

    threshold3 = Channel.control(
        ":MATH{ch}:THR3?",
        ":MATH{ch}:THR3 %g",
        """Control the Channel 3 logic threshold in Volts (float within the dynamic range).""",
        cast=float,
    )

    threshold4 = Channel.control(
        ":MATH{ch}:THR4?",
        ":MATH{ch}:THR4 %g",
        """Control the Channel 4 logic threshold in Volts (float within the dynamic range).""",
        cast=float,
    )

    def reset(self) -> None:
        """Adjust this math waveform's vertical scale to an optimal value."""
        self.write(":MATH{ch}:RES")


class SearchSubsystem(Channel):
    """Represent waveform event-search configuration and results."""

    count = Channel.measurement(
        ":SEAR:COUN?",
        """Measure the total number of search events (int).""",
        cast=int,
    )

    enabled = Channel.control(
        ":SEAR:STAT?",
        ":SEAR:STAT %d",
        """Control whether waveform search is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    mode = Channel.control(
        ":SEAR:MODE?",
        ":SEAR:MODE %s",
        """Control search type: EDGE, PULS, RUNT, SLOP, RS232, I2C, or SPI.""",
        validator=strict_discrete_set,
        values=["EDGE", "PULS", "RUNT", "SLOP", "RS232", "I2C", "SPI"],
        cast=str,
    )

    event = Channel.control(
        ":SEAR:EVEN?",
        ":SEAR:EVEN %d",
        """Control the selected search event (non-negative int within current results).""",
        validator=_validate_nonnegative_integer,
        values=None,
        cast=int,
    )

    edge_slope = Channel.control(
        ":SEAR:EDGE:SLOP?",
        ":SEAR:EDGE:SLOP %s",
        """Control edge-search slope: POS, NEG, or EITH.""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "EITH"],
        cast=str,
    )

    edge_source = Channel.control(
        ":SEAR:EDGE:SOUR?",
        ":SEAR:EDGE:SOUR %s",
        """Control the analog source for edge search (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    edge_threshold = Channel.control(
        ":SEAR:EDGE:THR?",
        ":SEAR:EDGE:THR %g",
        """Control the edge-search threshold in Volts (float within the dynamic range).""",
        cast=float,
    )

    pulse_polarity = Channel.control(
        ":SEAR:PULS:POL?",
        ":SEAR:PULS:POL %s",
        """Control pulse-search polarity: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    pulse_qualifier = Channel.control(
        ":SEAR:PULS:QUAL?",
        ":SEAR:PULS:QUAL %s",
        """Control pulse-search qualifier: GRE, LESS, or GLES.""",
        validator=strict_discrete_set,
        values=["GRE", "LESS", "GLES"],
        cast=str,
    )

    pulse_source = Channel.control(
        ":SEAR:PULS:SOUR?",
        ":SEAR:PULS:SOUR %s",
        """Control the analog source for pulse search (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    pulse_upper_width = Channel.control(
        ":SEAR:PULS:UWID?",
        ":SEAR:PULS:UWID %g",
        """Control pulse-search upper width in seconds (float from 800e-12 to 10).""",
        validator=strict_range,
        values=[800e-12, 10],
        cast=float,
    )

    pulse_lower_width = Channel.control(
        ":SEAR:PULS:LWID?",
        ":SEAR:PULS:LWID %g",
        """Control pulse-search lower width in seconds (float from 800e-12 to 10).""",
        validator=strict_range,
        values=[800e-12, 10],
        cast=float,
    )

    pulse_threshold = Channel.control(
        ":SEAR:PULS:THR?",
        ":SEAR:PULS:THR %g",
        """Control the pulse-search threshold in Volts (float within the dynamic range).""",
        cast=float,
    )

    runt_polarity = Channel.control(
        ":SEAR:RUNT:POL?",
        ":SEAR:RUNT:POL %s",
        """Control runt-search polarity: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    runt_qualifier = Channel.control(
        ":SEAR:RUNT:QUAL?",
        ":SEAR:RUNT:QUAL %s",
        """Control runt-search qualifier: NONE, GRE, LESS, or GLES.""",
        validator=strict_discrete_set,
        values=["NONE", "GRE", "LESS", "GLES"],
        cast=str,
    )

    runt_source = Channel.control(
        ":SEAR:RUNT:SOUR?",
        ":SEAR:RUNT:SOUR %s",
        """Control the analog source for runt search (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    runt_width_upper = Channel.control(
        ":SEAR:RUNT:WUPP?",
        ":SEAR:RUNT:WUPP %g",
        """Control runt-search upper width in seconds (float from 800e-12 to 10).""",
        validator=strict_range,
        values=[800e-12, 10],
        cast=float,
    )

    runt_width_lower = Channel.control(
        ":SEAR:RUNT:WLOW?",
        ":SEAR:RUNT:WLOW %g",
        """Control runt-search lower width in seconds (float from 800e-12 to 10).""",
        validator=strict_range,
        values=[800e-12, 10],
        cast=float,
    )

    runt_threshold1 = Channel.control(
        ":SEAR:RUNT:THR1?",
        ":SEAR:RUNT:THR1 %g",
        """Control runt-search Threshold A in Volts (float within the dynamic range).""",
        cast=float,
    )

    runt_threshold2 = Channel.control(
        ":SEAR:RUNT:THR2?",
        ":SEAR:RUNT:THR2 %g",
        """Control runt-search Threshold B in Volts (float within the dynamic range).""",
        cast=float,
    )

    slope_polarity = Channel.control(
        ":SEAR:SLOP:POL?",
        ":SEAR:SLOP:POL %s",
        """Control slope-search polarity: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    slope_qualifier = Channel.control(
        ":SEAR:SLOP:QUAL?",
        ":SEAR:SLOP:QUAL %s",
        """Control slope-search qualifier: GRE, LESS, or GLES.""",
        validator=strict_discrete_set,
        values=["GRE", "LESS", "GLES"],
        cast=str,
    )

    slope_source = Channel.control(
        ":SEAR:SLOP:SOUR?",
        ":SEAR:SLOP:SOUR %s",
        """Control the analog source for slope search (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    slope_time_upper = Channel.control(
        ":SEAR:SLOP:TUPP?",
        ":SEAR:SLOP:TUPP %g",
        """Control slope-search upper time in seconds (float from 800e-12 to 10).""",
        validator=strict_range,
        values=[800e-12, 10],
        cast=float,
    )

    slope_time_lower = Channel.control(
        ":SEAR:SLOP:TLOW?",
        ":SEAR:SLOP:TLOW %g",
        """Control slope-search lower time in seconds (float from 800e-12 to 10).""",
        validator=strict_range,
        values=[800e-12, 10],
        cast=float,
    )

    slope_threshold1 = Channel.control(
        ":SEAR:SLOP:THR1?",
        ":SEAR:SLOP:THR1 %g",
        """Control slope-search Threshold A in Volts (float within the dynamic range).""",
        cast=float,
    )

    slope_threshold2 = Channel.control(
        ":SEAR:SLOP:THR2?",
        ":SEAR:SLOP:THR2 %g",
        """Control slope-search Threshold B in Volts (float within the dynamic range).""",
        cast=float,
    )

    def value(self, event: int) -> float:
        """Return the time in seconds corresponding to search event 0 to 1000.

        :param event: Search-event index from 0 to 1000.
        """
        event = strict_range(event, [0, 1000])
        return float(self.ask(f":SEAR:VAL? {event}"))


class BodePlotSubsystem(Channel):
    """Represent MSO5000 Bode-plot configuration and results."""

    enabled = Channel.control(
        ":BODE:ENAB?",
        ":BODE:ENAB %d",
        """Control the Bode-plot state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    display_type = Channel.control(
        ":BODE:DISP?",
        ":BODE:DISP %s",
        """Control the display type (str).""",
        validator=strict_discrete_set,
        values=["DISP_WAVE", "DISP_CHART"],
        cast=str,
    )

    source = Channel.control(
        ":BODE:SOUR?",
        ":BODE:SOUR %s",
        """Control the generator source (str).""",
        validator=strict_discrete_set,
        values=["SOURCE1"],
        cast=str,
    )

    sweep_type = Channel.control(
        ":BODE:SWEE?",
        ":BODE:SWEE %s",
        """Control the sweep type (str).""",
        validator=strict_discrete_set,
        values=["LOG_SWEEP", "LINE_SWEEP"],
        cast=str,
    )

    reference_input = Channel.control(
        ":BODE:REFI?",
        ":BODE:REFI %s",
        """Control the reference input (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    reference_output = Channel.control(
        ":BODE:REFO?",
        ":BODE:REFO %s",
        """Control the reference output (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    impedance = Channel.control(
        ":BODE:IMP?",
        ":BODE:IMP %s",
        """Control the output impedance (str).""",
        validator=strict_discrete_set,
        values=["OMEG", "FIFT"],
        cast=str,
    )

    start = Channel.control(
        ":BODE:STAR?",
        ":BODE:STAR %g",
        """Control the start frequency in Hertz (float).""",
        validator=strict_range,
        values=[10, 25e6],
        cast=float,
    )

    stop = Channel.control(
        ":BODE:STOP?",
        ":BODE:STOP %g",
        """Control the stop frequency in Hertz (float).""",
        validator=strict_range,
        values=[100, 25e6],
        cast=float,
    )

    point = Channel.control(
        ":BODE:POIN?",
        ":BODE:POIN %d",
        """Control the point count (int).""",
        validator=strict_range,
        values=[10, 300],
        cast=int,
    )

    voltage_profile_enabled = Channel.control(
        ":BODE:VOLT:PROF?",
        ":BODE:VOLT:PROF %d",
        """Control the voltage profile state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    gain_margin = Channel.measurement(":BODE:GMAR?", """Measure gain margin (float).""", cast=float)
    gain_margin_frequency = Channel.measurement(
        ":BODE:GMAR:FREQ?", """Measure gain-margin frequency in Hertz (float).""", cast=float
    )
    phase_margin = Channel.measurement(
        ":BODE:PMAR?", """Measure phase margin (float).""", cast=float
    )
    phase_margin_frequency = Channel.measurement(
        ":BODE:PMAR:FREQ?", """Measure phase-margin frequency in Hertz (float).""", cast=float
    )

    voltage_ranges = [
        "ALL",
        "F10HZ",
        "F100HZ",
        "F1KHZ",
        "F10KHZ",
        "F100KHZ",
        "F1MHZ",
        "F10MHZ",
        "F25MHZ",
    ]

    def set_voltage(self, frequency_range: str, amplitude: float) -> None:
        """Set sweep amplitude in Volts for one documented frequency range.

        :param frequency_range: Frequency-range selector such as ``"ALL"`` or ``"F1KHZ"``.
        :param amplitude: Sweep amplitude in Volts.
        """
        frequency_range = strict_discrete_set(frequency_range, self.voltage_ranges)
        self.write(f":BODE:VOLT {amplitude:g},{frequency_range}")

    def voltage(self, frequency_range: str) -> float:
        """Return sweep amplitude in Volts for one documented frequency range.

        :param frequency_range: Frequency-range selector such as ``"ALL"`` or ``"F1KHZ"``.
        """
        frequency_range = strict_discrete_set(frequency_range, self.voltage_ranges)
        return float(self.ask(f":BODE:VOLT? {frequency_range}"))


class CounterSubsystem(Channel):
    """Represent the MSO5000 hardware counter."""

    current = Channel.measurement(
        ":COUN:CURR?", """Measure the current counter value (float).""", cast=float
    )

    enabled = Channel.control(
        ":COUN:ENAB?",
        ":COUN:ENAB %d",
        """Control the counter state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    source = Channel.control(
        ":COUN:SOUR?",
        ":COUN:SOUR %s",
        """Control the counter source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    mode = Channel.control(
        ":COUN:MODE?",
        ":COUN:MODE %s",
        """Control the counter mode (str).""",
        validator=strict_discrete_set,
        values=["FREQ", "PER", "TOT"],
        cast=str,
    )

    digits = Channel.control(
        ":COUN:NDIG?",
        ":COUN:NDIG %d",
        """Control the displayed digit count (int).""",
        validator=strict_range,
        values=[3, 6],
        cast=int,
    )

    totalize_enabled = Channel.control(
        ":COUN:TOT:ENAB?",
        ":COUN:TOT:ENAB %d",
        """Control the totalizer state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    def clear_totalizer(self) -> None:
        """Clear the accumulated totalizer value."""
        self.write(":COUN:TOT:CLE")


class DVMSubsystem(Channel):
    """Represent the MSO5000 digital voltmeter."""

    current = Channel.measurement(
        ":DVM:CURR?", """Measure the current voltage in Volts (float).""", cast=float
    )

    enabled = Channel.control(
        ":DVM:ENAB?",
        ":DVM:ENAB %d",
        """Control the DVM state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    source = Channel.control(
        ":DVM:SOUR?",
        ":DVM:SOUR %s",
        """Control the DVM source (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    mode = Channel.control(
        ":DVM:MODE?",
        ":DVM:MODE %s",
        """Control the DVM mode (str).""",
        validator=strict_discrete_set,
        values=["ACRM", "DC", "DCRM"],
        cast=str,
    )


class PowerAnalysisSubsystem(Channel):
    """Represent MSO5000 power-analysis configuration."""

    type = Channel.control(
        ":POW:TYPE?",
        ":POW:TYPE %s",
        """Control the analysis type (str).""",
        validator=strict_discrete_set,
        values=["QUAL", "RIPP"],
        cast=str,
    )

    current_source = Channel.control(
        ":POW:CURR?",
        ":POW:CURR %s",
        """Control the current source (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    voltage_source = Channel.control(
        ":POW:VOLT?",
        ":POW:VOLT %s",
        """Control the voltage source (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    quality_frequency_reference = Channel.control(
        ":POW:QUAL:FREQ?",
        ":POW:QUAL:FREQ %s",
        """Control the quality frequency reference (str).""",
        validator=strict_discrete_set,
        values=["VOLT", "CURR"],
        cast=str,
    )

    reference_level_method = Channel.control(
        ":POW:REFL:METH?",
        ":POW:REFL:METH %s",
        """Control the reference-level method (str).""",
        validator=strict_discrete_set,
        values=["ABS", "PERC"],
        cast=str,
    )

    reference_level_percent_high = Channel.control(
        ":POW:REFL:PERC:HIGH?",
        ":POW:REFL:PERC:HIGH %d",
        """Control the high reference level in percent (int from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    reference_level_percent_low = Channel.control(
        ":POW:REFL:PERC:LOW?",
        ":POW:REFL:PERC:LOW %d",
        """Control the low reference level in percent (int from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    reference_level_percent_mid = Channel.control(
        ":POW:REFL:PERC:MID?",
        ":POW:REFL:PERC:MID %d",
        """Control the middle reference level in percent (int from 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )


class AWGChannel(Channel):
    """Represent one optional MSO5000 arbitrary waveform generator channel."""

    frequency_fixed = Channel.control(
        ":SOUR{ch}:FREQ?",
        ":SOUR{ch}:FREQ %g",
        """Control the output frequency in Hertz (float).

        The valid range depends on :attr:`function_shape`.
        """,
        cast=float,
    )

    phase_adjust = Channel.control(
        ":SOUR{ch}:PHAS?",
        ":SOUR{ch}:PHAS %g",
        """Control the start phase in degrees (float).""",
        validator=strict_range,
        values=[0, 360],
        cast=float,
    )

    function_shape = Channel.control(
        ":SOUR{ch}:FUNC?",
        ":SOUR{ch}:FUNC %s",
        """Control the waveform shape (str).""",
        validator=strict_discrete_set,
        values=[
            "SIN",
            "SQU",
            "RAMP",
            "PULS",
            "NOIS",
            "DC",
            "SINC",
            "EXPR",
            "EXPF",
            "ECG",
            "GAUS",
            "LOR",
            "HAV",
            "ARB",
        ],
        cast=str,
    )

    function_ramp_symmetry = Channel.control(
        ":SOUR{ch}:FUNC:RAMP:SYMM?",
        ":SOUR{ch}:FUNC:RAMP:SYMM %g",
        """Control the ramp symmetry in percent (float).""",
        validator=strict_range,
        values=[1, 100],
        cast=float,
    )

    voltage_level_immediate_amplitude = Channel.control(
        ":SOUR{ch}:VOLT?",
        ":SOUR{ch}:VOLT %g",
        """Control the amplitude in Volts peak-to-peak (float).""",
        cast=float,
    )

    voltage_level_immediate_offset = Channel.control(
        ":SOUR{ch}:VOLT:OFFS?",
        ":SOUR{ch}:VOLT:OFFS %g",
        """Control the DC offset in Volts (float).""",
        cast=float,
    )

    pulse_duty_cycle = Channel.control(
        ":SOUR{ch}:PULS:DCYC?",
        ":SOUR{ch}:PULS:DCYC %g",
        """Control the pulse duty cycle in percent (float).""",
        validator=strict_range,
        values=[10, 90],
        cast=float,
    )

    type = Channel.control(
        ":SOUR{ch}:TYPE?",
        ":SOUR{ch}:TYPE %s",
        """Control the operating type (str).""",
        validator=strict_discrete_set,
        values=["NONE", "MOD", "SWE", "BURS"],
        cast=str,
    )

    mod_type = Channel.control(
        ":SOUR{ch}:MOD:TYPE?",
        ":SOUR{ch}:MOD:TYPE %s",
        """Control the modulation type (str).""",
        validator=strict_discrete_set,
        values=["AM", "FM", "FSK"],
        cast=str,
    )

    mod_am_depth = Channel.control(
        ":SOUR{ch}:MOD:AM?",
        ":SOUR{ch}:MOD:AM %d",
        """Control the AM depth in percent (int).""",
        validator=strict_range,
        values=[0, 120],
        cast=int,
    )

    mod_am_internal_frequency = Channel.control(
        ":SOUR{ch}:MOD:AM:INT:FREQ?",
        ":SOUR{ch}:MOD:AM:INT:FREQ %d",
        """Control the AM internal frequency in Hertz (int).""",
        validator=strict_range,
        values=[1, 50_000],
        cast=int,
    )

    mod_fm_internal_frequency = Channel.control(
        ":SOUR{ch}:MOD:FM:INT:FREQ?",
        ":SOUR{ch}:MOD:FM:INT:FREQ %d",
        """Control the FM internal frequency in Hertz (int).""",
        validator=strict_range,
        values=[1, 50_000],
        cast=int,
    )

    mod_am_internal_function = Channel.control(
        ":SOUR{ch}:MOD:AM:INT:FUNC?",
        ":SOUR{ch}:MOD:AM:INT:FUNC %s",
        """Control the AM internal waveform (str).""",
        validator=strict_discrete_set,
        values=["SIN", "SQU", "RAMP", "NOIS"],
        cast=str,
    )

    mod_fm_internal_function = Channel.control(
        ":SOUR{ch}:MOD:FM:INT:FUNC?",
        ":SOUR{ch}:MOD:FM:INT:FUNC %s",
        """Control the FM internal waveform (str).""",
        validator=strict_discrete_set,
        values=["SIN", "SQU", "RAMP", "NOIS"],
        cast=str,
    )

    mod_fm_deviation = Channel.control(
        ":SOUR{ch}:MOD:FM:DEV?",
        ":SOUR{ch}:MOD:FM:DEV %g",
        """Control the FM deviation in Hertz (float).""",
        cast=float,
    )

    sweep_type = Channel.control(
        ":SOUR{ch}:SWE:TYPE?",
        ":SOUR{ch}:SWE:TYPE %s",
        """Control the sweep type (str).""",
        validator=strict_discrete_set,
        values=["LIN", "LOG", "STEP"],
        cast=str,
    )

    sweep_time = Channel.control(
        ":SOUR{ch}:SWE:STIM?",
        ":SOUR{ch}:SWE:STIM %g",
        """Control the sweep time in seconds (float).""",
        validator=strict_range,
        values=[0.001, 500],
        cast=float,
    )

    sweep_back_time = Channel.control(
        ":SOUR{ch}:SWE:BTIM?",
        ":SOUR{ch}:SWE:BTIM %g",
        """Control the sweep return time in seconds (float).""",
        validator=strict_range,
        values=[0, 500],
        cast=float,
    )

    burst_type = Channel.control(
        ":SOUR{ch}:BURS:TYPE?",
        ":SOUR{ch}:BURS:TYPE %s",
        """Control the burst type (str).""",
        validator=strict_discrete_set,
        values=["NCYC", "INF"],
        cast=str,
    )

    burst_cycles = Channel.control(
        ":SOUR{ch}:BURS:CYCL?",
        ":SOUR{ch}:BURS:CYCL %d",
        """Control the burst cycle count (int).""",
        validator=strict_range,
        values=[1, 1_000_000],
        cast=int,
    )

    burst_delay = Channel.control(
        ":SOUR{ch}:BURS:DEL?",
        ":SOUR{ch}:BURS:DEL %g",
        """Control the burst delay in seconds (float).""",
        cast=float,
    )

    output_enabled = Channel.control(
        ":SOUR{ch}:OUTP{ch}?",
        ":SOUR{ch}:OUTP{ch} %d",
        """Control the output state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    output_impedance = Channel.control(
        ":SOUR{ch}:OUTP{ch}:IMP?",
        ":SOUR{ch}:OUTP{ch}:IMP %s",
        """Control the output impedance (str).""",
        validator=strict_discrete_set,
        values=["OMEG", "FIFT"],
        cast=str,
    )

    def reset_phase(self) -> None:
        """Synchronize the phases of both generator channels."""
        self.write(":SOUR{ch}:PHAS:INIT")

    def get_applied_waveform(self) -> tuple[str, ...]:
        """Return the current waveform configuration fields without lossy conversion."""
        return tuple(value.strip() for value in self.ask(":SOUR{ch}:APPL?").split(","))

    @staticmethod
    def _apply_arguments(values: tuple[float | None, ...]) -> str:
        first_missing = next(
            (index for index, value in enumerate(values) if value is None), len(values)
        )
        if any(value is not None for value in values[first_missing:]):
            raise ValueError("Generator apply parameters cannot skip an earlier parameter.")
        return ",".join(f"{value:g}" for value in values[:first_missing] if value is not None)

    def _apply(self, shape: str, *values: float | None) -> None:
        arguments = self._apply_arguments(values)
        suffix = f" {arguments}" if arguments else ""
        self.write(f":SOUR{self.id}:APPL:{shape}{suffix}")

    def _apply_periodic(
        self,
        shape: str,
        maximum_frequency: float,
        frequency: float | None,
        amplitude: float | None,
        offset: float | None,
        phase: float | None,
    ) -> None:
        if frequency is not None:
            frequency = strict_range(frequency, [0.1, maximum_frequency])
        if phase is not None:
            phase = strict_range(phase, [0, 360])
        self._apply(shape, frequency, amplitude, offset, phase)

    def apply_noise(self, amplitude: float | None = None, offset: float | None = None) -> None:
        """Apply noise with optional sequential parameters.

        :param amplitude: Optional amplitude in Volts peak-to-peak; the valid range depends on
            output impedance.
        :param offset: Optional DC offset in Volts; the valid range depends on impedance and
            amplitude.
        """
        self._apply("NOIS", amplitude, offset)

    def apply_pulse(
        self,
        frequency: float | None = None,
        amplitude: float | None = None,
        offset: float | None = None,
        phase: float | None = None,
    ) -> None:
        """Apply a pulse waveform with sequential optional parameters.

        :param frequency: Optional frequency in Hertz from 0.1 to 1 MHz, inclusive.
        :param amplitude: Optional amplitude in Volts peak-to-peak; range depends on impedance.
        :param offset: Optional DC offset in Volts; range depends on impedance and amplitude.
        :param phase: Optional start phase in degrees from 0 to 360, inclusive.
        """
        self._apply_periodic("PULS", 1e6, frequency, amplitude, offset, phase)

    def apply_ramp(
        self,
        frequency: float | None = None,
        amplitude: float | None = None,
        offset: float | None = None,
        phase: float | None = None,
    ) -> None:
        """Apply a ramp waveform with sequential optional parameters.

        :param frequency: Optional frequency in Hertz from 0.1 to 100 kHz, inclusive.
        :param amplitude: Optional amplitude in Volts peak-to-peak; range depends on impedance.
        :param offset: Optional DC offset in Volts; range depends on impedance and amplitude.
        :param phase: Optional start phase in degrees from 0 to 360, inclusive.
        """
        self._apply_periodic("RAMP", 100e3, frequency, amplitude, offset, phase)

    def apply_sine(
        self,
        frequency: float | None = None,
        amplitude: float | None = None,
        offset: float | None = None,
        phase: float | None = None,
    ) -> None:
        """Apply a sine waveform with sequential optional parameters.

        :param frequency: Optional frequency in Hertz from 0.1 to 25 MHz, inclusive.
        :param amplitude: Optional amplitude in Volts peak-to-peak; range depends on impedance.
        :param offset: Optional DC offset in Volts; range depends on impedance and amplitude.
        :param phase: Optional start phase in degrees from 0 to 360, inclusive.
        """
        self._apply_periodic("SIN", 25e6, frequency, amplitude, offset, phase)

    def apply_square(
        self,
        frequency: float | None = None,
        amplitude: float | None = None,
        offset: float | None = None,
        phase: float | None = None,
    ) -> None:
        """Apply a square waveform with sequential optional parameters.

        :param frequency: Optional frequency in Hertz from 0.1 to 15 MHz, inclusive.
        :param amplitude: Optional amplitude in Volts peak-to-peak; range depends on impedance.
        :param offset: Optional DC offset in Volts; range depends on impedance and amplitude.
        :param phase: Optional start phase in degrees from 0 to 360, inclusive.
        """
        self._apply_periodic("SQU", 15e6, frequency, amplitude, offset, phase)

    def apply_user(
        self,
        frequency: float | None = None,
        amplitude: float | None = None,
        offset: float | None = None,
        phase: float | None = None,
    ) -> None:
        """Apply the selected arbitrary waveform with sequential optional parameters.

        :param frequency: Optional frequency in Hertz from 0.1 to 10 MHz, inclusive.
        :param amplitude: Optional amplitude in Volts peak-to-peak; range depends on impedance.
        :param offset: Optional DC offset in Volts; range depends on impedance and amplitude.
        :param phase: Optional start phase in degrees from 0 to 360, inclusive.
        """
        self._apply_periodic("USER", 10e6, frequency, amplitude, offset, phase)

    def upload_waveform(self, data: bytes) -> None:
        """Upload 4 to 32768 raw DAC16 bytes with definite-block framing.

        :param data: Even-length raw DAC16 payload containing 4 to 32768 bytes.
        """
        if not isinstance(data, bytes):
            raise TypeError("Waveform data must be bytes.")
        if not 4 <= len(data) <= 32768 or len(data) % 2:
            raise ValueError("Waveform data must contain an even 4 to 32768 bytes.")
        count = str(len(data))
        prefix = f":TRAC{self.id}:DATA:DAC16 volatile,END,#{len(count)}{count}".encode()
        self.write_bytes(prefix + data)


class QuickSubsystem(Channel):
    """Represent the configurable front-panel shortcut operation."""

    operation = Channel.control(
        ":QUIC:OPER?",
        ":QUIC:OPER %s",
        """Control the shortcut operation: SIM, SWAV, SSET, AME, or SRES.""",
        validator=strict_discrete_set,
        values=["SIM", "SWAV", "SSET", "AME", "SRES"],
        cast=str,
    )


class DigitalChannel(Channel):
    """Represent one MSO5000 digital input channel."""

    display_enabled = Channel.control(
        ":LA:DIG:DISP? D{ch}",
        ":LA:DIG:DISP D{ch},%d",
        """Control whether this digital channel is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    position = Channel.control(
        ":LA:DIG:POS? D{ch}",
        ":LA:DIG:POS D{ch},%d",
        """Control this digital channel position (int from 0 to 31).""",
        validator=strict_range,
        values=[0, 31],
        cast=int,
    )

    label = Channel.control(
        ":LA:DIG:LAB? D{ch}",
        ":LA:DIG:LAB D{ch},%s",
        """Control this digital channel label (str).""",
        cast=str,
    )


class LogicPod(Channel):
    """Represent one eight-channel MSO5000 logic pod."""

    display_enabled = Channel.control(
        ":LA:POD{ch}:DISP?",
        ":LA:POD{ch}:DISP %d",
        """Control whether this logic pod is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    threshold = Channel.control(
        ":LA:POD{ch}:THR?",
        ":LA:POD{ch}:THR %g",
        """Control this logic pod threshold in Volts (float from -15 to 15).""",
        validator=strict_range,
        values=[-15, 15],
        cast=float,
    )


class LogicAnalyzerSubsystem(Channel):
    """Represent global MSO5000 logic-analyzer configuration."""

    enabled = Channel.control(
        ":LA:STAT?",
        ":LA:STAT %d",
        """Control whether logic-analyzer acquisition is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    active_channel = Channel.control(
        ":LA:ACT?",
        ":LA:ACT %s",
        """Control the active digital channel, or NONE (str).""",
        validator=strict_discrete_set,
        values=[*DIGITAL_SOURCES, "NONE"],
        cast=str,
    )

    auto_sort_enabled = Channel.setting(
        ":LA:AUTOS %d",
        """Set whether new logic groups are sorted automatically (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    size = Channel.control(
        ":LA:SIZE?",
        ":LA:SIZE %s",
        """Control the digital waveform display size: SMAL, MED, or LARG.""",
        validator=strict_discrete_set,
        values=["SMAL", "MED", "LARG"],
        cast=str,
    )

    time_calibration = Channel.measurement(
        ":LA:TCAL?",
        """Measure the logic-analyzer delay calibration in seconds (float).

        The corresponding write command is intentionally not exposed because it changes
        calibration state.
        """,
        cast=float,
    )

    def set_display(self, source: str, enabled: bool) -> None:
        """Set whether a digital channel, group, or pod is displayed.

        :param source: Digital channel, user-defined group, or logic-pod name.
        :param enabled: Whether the selected source is displayed.
        """
        source = strict_discrete_set(source, LOGIC_DISPLAY_SOURCES)
        strict_discrete_set(enabled, [True, False])
        self.write(f":LA:DISP {source},{int(enabled)}")

    def is_displayed(self, source: str) -> bool:
        """Return whether a digital channel, group, or pod is displayed.

        :param source: Digital channel, user-defined group, or logic-pod name.
        """
        source = strict_discrete_set(source, LOGIC_DISPLAY_SOURCES)
        return bool(int(self.ask(f":LA:DISP? {source}")))

    def delete_group(self, group: str) -> None:
        """Delete one user-defined logic group.

        :param group: User-defined group from ``"GRO1"`` to ``"GRO4"``.
        """
        group = strict_discrete_set(group, LOGIC_GROUPS)
        self.write(f":LA:DEL {group}")

    def append_group(self, group: str, *digital_channels: str) -> None:
        """Append one to sixteen digital channels to a user-defined group.

        :param group: User-defined group from ``"GRO1"`` to ``"GRO4"``.
        :param digital_channels: One to sixteen channel names from ``"D0"`` to ``"D15"``.
        """
        group = strict_discrete_set(group, LOGIC_GROUPS)
        if not 1 <= len(digital_channels) <= 16:
            raise ValueError("A logic group append requires one to sixteen digital channels.")
        channels = [strict_discrete_set(channel, DIGITAL_SOURCES) for channel in digital_channels]
        self.write(f":LA:GRO:APP {group},{','.join(channels)}")


class BusChannel(Channel):
    """Represent one MSO5000 serial or parallel decoding bus."""

    mode = Channel.control(
        ":BUS{ch}:MODE?",
        ":BUS{ch}:MODE %s",
        """Control the decoding mode (str).""",
        validator=strict_discrete_set,
        values=["PAR", "RS232", "SPI", "IIC", "IIS", "LIN", "CAN", "FLEX", "M1553"],
        cast=str,
    )

    display_enabled = Channel.control(
        ":BUS{ch}:DISP?",
        ":BUS{ch}:DISP %d",
        """Control the display state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    format = Channel.control(
        ":BUS{ch}:FORM?",
        ":BUS{ch}:FORM %s",
        """Control the display format (str).""",
        validator=strict_discrete_set,
        values=["HEX", "ASC", "DEC", "BIN"],
        cast=str,
    )

    event_table_enabled = Channel.control(
        ":BUS{ch}:EVEN?",
        ":BUS{ch}:EVEN %d",
        """Control the event-table display state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    event_format = Channel.control(
        ":BUS{ch}:EVEN:FORM?",
        ":BUS{ch}:EVEN:FORM %s",
        """Control the event-table format (str).""",
        validator=strict_discrete_set,
        values=["HEX", "ASC", "DEC", "BIN"],
        cast=str,
    )

    event_view = Channel.control(
        ":BUS{ch}:EVEN:VIEW?",
        ":BUS{ch}:EVEN:VIEW %s",
        """Control the event-table view (str).""",
        validator=strict_discrete_set,
        values=["PACK", "DET", "PAYL"],
        cast=str,
    )

    label_enabled = Channel.control(
        ":BUS{ch}:LAB?",
        ":BUS{ch}:LAB %d",
        """Control the label display state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    position = Channel.control(
        ":BUS{ch}:POS?",
        ":BUS{ch}:POS %d",
        """Control the vertical position (int).""",
        validator=strict_range,
        values=[-250, 250],
        cast=int,
    )

    parallel_bus = Channel.control(
        ":BUS{ch}:PAR:BUS?",
        ":BUS{ch}:PAR:BUS %s",
        """Control the parallel bus source (str).""",
        validator=strict_discrete_set,
        values=[
            "CH1",
            "CH2",
            "CH3",
            "CH4",
            "D7D0",
            "D15D8",
            "D15D0",
            "D0D7",
            "D8D15",
            "D0D15",
            "USER",
        ],
        cast=str,
    )

    parallel_clk = Channel.control(
        ":BUS{ch}:PAR:CLK?",
        ":BUS{ch}:PAR:CLK %s",
        """Control the parallel clock source (str).""",
        validator=strict_discrete_set,
        values=[*PROTOCOL_SOURCES, "OFF"],
        cast=str,
    )

    parallel_slope = Channel.control(
        ":BUS{ch}:PAR:SLOP?",
        ":BUS{ch}:PAR:SLOP %s",
        """Control the parallel clock slope (str).""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "BOTH"],
        cast=str,
    )

    parallel_width = Channel.control(
        ":BUS{ch}:PAR:WIDT?",
        ":BUS{ch}:PAR:WIDT %d",
        """Control the parallel data width (int).""",
        validator=strict_range,
        values=[0, 20],
        cast=int,
    )

    parallel_bitx = Channel.control(
        ":BUS{ch}:PAR:BITX?",
        ":BUS{ch}:PAR:BITX %d",
        """Control the selected parallel bit (int).""",
        cast=int,
    )

    parallel_source = Channel.control(
        ":BUS{ch}:PAR:SOUR?",
        ":BUS{ch}:PAR:SOUR %s",
        """Control the parallel bit source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    parallel_polarity = Channel.control(
        ":BUS{ch}:PAR:POL?",
        ":BUS{ch}:PAR:POL %s",
        """Control the parallel polarity (str).""",
        validator=strict_discrete_set,
        values=["NEG", "POS"],
        cast=str,
    )

    parallel_noise_rejection_enabled = Channel.control(
        ":BUS{ch}:PAR:NREJ?",
        ":BUS{ch}:PAR:NREJ %d",
        """Control the parallel noise rejection state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    parallel_noise_reject_time = Channel.control(
        ":BUS{ch}:PAR:NRT?",
        ":BUS{ch}:PAR:NRT %g",
        """Control the parallel noise rejection time in seconds (float).""",
        validator=strict_range,
        values=[0, 1],
        cast=float,
    )

    rs232_tx = Channel.control(
        ":BUS{ch}:RS232:TX?",
        ":BUS{ch}:RS232:TX %s",
        """Control the RS232 transmit source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES_WITH_OFF,
        cast=str,
    )

    rs232_rx = Channel.control(
        ":BUS{ch}:RS232:RX?",
        ":BUS{ch}:RS232:RX %s",
        """Control the RS232 receive source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES_WITH_OFF,
        cast=str,
    )

    rs232_polarity = Channel.control(
        ":BUS{ch}:RS232:POL?",
        ":BUS{ch}:RS232:POL %s",
        """Control the RS232 polarity (str).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    rs232_endian = Channel.control(
        ":BUS{ch}:RS232:END?",
        ":BUS{ch}:RS232:END %s",
        """Control the RS232 bit order (str).""",
        validator=strict_discrete_set,
        values=["MSB", "LSB"],
        cast=str,
    )

    rs232_baud = Channel.control(
        ":BUS{ch}:RS232:BAUD?",
        ":BUS{ch}:RS232:BAUD %d",
        """Control the RS232 baud rate in bits per second (int).""",
        validator=strict_range,
        values=[1, 20_000_000],
        cast=int,
    )

    rs232_data_bits = Channel.control(
        ":BUS{ch}:RS232:DBIT?",
        ":BUS{ch}:RS232:DBIT %d",
        """Control the RS232 data-bit count (int).""",
        validator=strict_discrete_set,
        values=[5, 6, 7, 8, 9],
        cast=int,
    )

    rs232_stop_bits = Channel.control(
        ":BUS{ch}:RS232:SBIT?",
        ":BUS{ch}:RS232:SBIT %g",
        """Control the RS232 stop-bit count (float).""",
        validator=strict_discrete_set,
        values=[1, 1.5, 2],
        cast=float,
    )

    rs232_parity = Channel.control(
        ":BUS{ch}:RS232:PAR?",
        ":BUS{ch}:RS232:PAR %s",
        """Control the RS232 parity (str).""",
        validator=strict_discrete_set,
        values=["NONE", "ODD", "EVEN"],
        cast=str,
    )

    rs232_packet_enabled = Channel.control(
        ":BUS{ch}:RS232:PACK?",
        ":BUS{ch}:RS232:PACK %d",
        """Control the RS232 packet decoding state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    rs232_pend = Channel.control(
        ":BUS{ch}:RS232:PEND?",
        ":BUS{ch}:RS232:PEND %s",
        """Control the RS232 packet terminator (str).""",
        validator=strict_discrete_set,
        values=["NULL", "LF", "CR", "SP"],
        cast=str,
    )

    iic_clock_source = Channel.control(
        ":BUS{ch}:IIC:SCLK:SOUR?",
        ":BUS{ch}:IIC:SCLK:SOUR %s",
        """Control the I2C clock source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iic_data_source = Channel.control(
        ":BUS{ch}:IIC:SDA:SOUR?",
        ":BUS{ch}:IIC:SDA:SOUR %s",
        """Control the I2C data source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iic_address = Channel.control(
        ":BUS{ch}:IIC:ADDR?",
        ":BUS{ch}:IIC:ADDR %s",
        """Control the I2C address display mode (str).""",
        validator=strict_discrete_set,
        values=["NORM", "RW"],
        cast=str,
    )

    spi_clock_source = Channel.control(
        ":BUS{ch}:SPI:SCLK:SOUR?",
        ":BUS{ch}:SPI:SCLK:SOUR %s",
        """Control the SPI clock source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    spi_clock_slope = Channel.control(
        ":BUS{ch}:SPI:SCLK:SLOP?",
        ":BUS{ch}:SPI:SCLK:SLOP %s",
        """Control the SPI clock slope (str).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    spi_miso_source = Channel.control(
        ":BUS{ch}:SPI:MISO:SOUR?",
        ":BUS{ch}:SPI:MISO:SOUR %s",
        """Control the SPI MISO source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES_WITH_OFF,
        cast=str,
    )

    spi_miso_polarity = Channel.control(
        ":BUS{ch}:SPI:MISO:POL?",
        ":BUS{ch}:SPI:MISO:POL %s",
        """Control the SPI MISO polarity (str).""",
        validator=strict_discrete_set,
        values=["HIGH", "LOW"],
        cast=str,
    )

    spi_mosi_source = Channel.control(
        ":BUS{ch}:SPI:MOSI:SOUR?",
        ":BUS{ch}:SPI:MOSI:SOUR %s",
        """Control the SPI MOSI source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES_WITH_OFF,
        cast=str,
    )

    spi_mosi_polarity = Channel.control(
        ":BUS{ch}:SPI:MOSI:POL?",
        ":BUS{ch}:SPI:MOSI:POL %s",
        """Control the SPI MOSI polarity (str).""",
        validator=strict_discrete_set,
        values=["HIGH", "LOW"],
        cast=str,
    )

    spi_data_bits = Channel.control(
        ":BUS{ch}:SPI:DBIT?",
        ":BUS{ch}:SPI:DBIT %d",
        """Control the SPI data-bit count (int).""",
        validator=strict_range,
        values=[4, 32],
        cast=int,
    )

    spi_endian = Channel.control(
        ":BUS{ch}:SPI:END?",
        ":BUS{ch}:SPI:END %s",
        """Control the SPI bit order (str).""",
        validator=strict_discrete_set,
        values=["MSB", "LSB"],
        cast=str,
    )

    spi_mode = Channel.control(
        ":BUS{ch}:SPI:MODE?",
        ":BUS{ch}:SPI:MODE %s",
        """Control the SPI framing mode (str).""",
        validator=strict_discrete_set,
        values=["CS", "TIM"],
        cast=str,
    )

    spi_timeout_time = Channel.control(
        ":BUS{ch}:SPI:TIM:TIME?",
        ":BUS{ch}:SPI:TIM:TIME %g",
        """Control the SPI timeout in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 10],
        cast=float,
    )

    spi_ss_source = Channel.control(
        ":BUS{ch}:SPI:SS:SOUR?",
        ":BUS{ch}:SPI:SS:SOUR %s",
        """Control the SPI slave-select source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    spi_ss_polarity = Channel.control(
        ":BUS{ch}:SPI:SS:POL?",
        ":BUS{ch}:SPI:SS:POL %s",
        """Control the SPI slave-select polarity (str).""",
        validator=strict_discrete_set,
        values=["HIGH", "LOW"],
        cast=str,
    )

    can_source = Channel.control(
        ":BUS{ch}:CAN:SOUR?",
        ":BUS{ch}:CAN:SOUR %s",
        """Control the CAN source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    can_source_type = Channel.control(
        ":BUS{ch}:CAN:STYP?",
        ":BUS{ch}:CAN:STYP %s",
        """Control the CAN source type (str).""",
        validator=strict_discrete_set,
        values=["TX", "RX", "CANH", "CANL", "DIFF"],
        cast=str,
    )

    can_baud = Channel.control(
        ":BUS{ch}:CAN:BAUD?",
        ":BUS{ch}:CAN:BAUD %d",
        """Control the CAN baud rate in bits per second (int).""",
        validator=strict_range,
        values=[10_000, 5_000_000],
        cast=int,
    )

    can_sample_point = Channel.control(
        ":BUS{ch}:CAN:SPO?",
        ":BUS{ch}:CAN:SPO %d",
        """Control the CAN sample point in percent (int).""",
        validator=strict_range,
        values=[10, 90],
        cast=int,
    )

    flexray_baud = Channel.control(
        ":BUS{ch}:FLEX:BAUD?",
        ":BUS{ch}:FLEX:BAUD %d",
        """Control the FlexRay baud rate in bits per second (int).""",
        validator=strict_discrete_set,
        values=[2_500_000, 5_000_000, 10_000_000],
        cast=int,
    )

    flexray_source = Channel.control(
        ":BUS{ch}:FLEX:SOUR?",
        ":BUS{ch}:FLEX:SOUR %s",
        """Control the FlexRay source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    flexray_sample_point = Channel.control(
        ":BUS{ch}:FLEX:SPO?",
        ":BUS{ch}:FLEX:SPO %d",
        """Control the FlexRay sample point in percent (int).""",
        validator=strict_range,
        values=[10, 90],
        cast=int,
    )

    flexray_source_type = Channel.control(
        ":BUS{ch}:FLEX:STYP?",
        ":BUS{ch}:FLEX:STYP %s",
        """Control the FlexRay source type (str).""",
        validator=strict_discrete_set,
        values=["BP", "BM", "RT"],
        cast=str,
    )

    lin_baud = Channel.control(
        ":BUS{ch}:LIN:BAUD?",
        ":BUS{ch}:LIN:BAUD %d",
        """Control the LIN baud rate in bits per second (int).""",
        validator=strict_range,
        values=[2_400, 20_000_000],
        cast=int,
    )

    lin_polarity = Channel.control(
        ":BUS{ch}:LIN:POL?",
        ":BUS{ch}:LIN:POL %d",
        """Control the LIN polarity state (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    lin_source = Channel.control(
        ":BUS{ch}:LIN:SOUR?",
        ":BUS{ch}:LIN:SOUR %s",
        """Control the LIN source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    lin_standard = Channel.control(
        ":BUS{ch}:LIN:STAN?",
        ":BUS{ch}:LIN:STAN %s",
        """Control the LIN standard (str).""",
        validator=strict_discrete_set,
        values=["V1X", "V2X", "MIX"],
        cast=str,
    )

    iis_source_clock = Channel.control(
        ":BUS{ch}:IIS:SOUR:CLOC?",
        ":BUS{ch}:IIS:SOUR:CLOC %s",
        """Control the I2S clock source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iis_source_word_select = Channel.control(
        ":BUS{ch}:IIS:SOUR:WSEL?",
        ":BUS{ch}:IIS:SOUR:WSEL %s",
        """Control the I2S word-select source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iis_alignment = Channel.control(
        ":BUS{ch}:IIS:ALIG?",
        ":BUS{ch}:IIS:ALIG %s",
        """Control the I2S alignment (str).""",
        validator=strict_discrete_set,
        values=["IIS", "RJ", "LJ"],
        cast=str,
    )

    iis_clock_slope = Channel.control(
        ":BUS{ch}:IIS:CLOC:SLOP?",
        ":BUS{ch}:IIS:CLOC:SLOP %s",
        """Control the I2S clock slope (str).""",
        validator=strict_discrete_set,
        values=["NEG", "POS"],
        cast=str,
    )

    iis_right_width = Channel.control(
        ":BUS{ch}:IIS:RWID?",
        ":BUS{ch}:IIS:RWID %d",
        """Control the I2S right-channel width (int).""",
        validator=strict_range,
        values=[4, 32],
        cast=int,
    )

    m1553_source = Channel.control(
        ":BUS{ch}:M1553:SOUR?",
        ":BUS{ch}:M1553:SOUR %s",
        """Control the MIL-STD-1553 source (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    iis_source_data = Channel.control(
        ":BUS{ch}:IIS:SOUR:DATA?",
        ":BUS{ch}:IIS:SOUR:DATA %s",
        """Control the I2S data source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    def set_threshold(self, threshold_type: str, value: float) -> None:
        """Set the threshold in Volts for one documented decoding source type.

        :param threshold_type: Documented bus threshold source type.
        :param value: Threshold in Volts.
        """
        threshold_type = strict_discrete_set(threshold_type, BUS_THRESHOLD_TYPES)
        self.write(f":BUS{self.id}:THR {value:g},{threshold_type}")

    def threshold(self, threshold_type: str) -> float:
        """Return the threshold in Volts for one documented decoding source type.

        :param threshold_type: Documented bus threshold source type.
        """
        threshold_type = strict_discrete_set(threshold_type, BUS_THRESHOLD_TYPES)
        return float(self.ask(f":BUS{self.id}:THR? {threshold_type}"))

    def read_events(self) -> str:
        """Return the decoded event table with its decoding-type prefix."""
        response = self.ask(f":BUS{self.id}:DATA?")
        return _parse_ieee_block(response.encode(), "Bus event table response").decode()

    def export_events(self, path: str) -> None:
        """Export the decoded event table to an instrument file path.

        :param path: Destination path on the instrument filesystem.
        """
        if not isinstance(path, str):
            raise TypeError("Event export path must be a string.")
        self.write(f":BUS{self.id}:EEXP {path}")


class NetworkSubsystem(Channel):
    """Represent MSO5000 network configuration and status."""

    dhcp_enabled = Channel.control(
        ":LAN:DHCP?",
        ":LAN:DHCP %d",
        """Control whether DHCP configuration is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    auto_ip_enabled = Channel.control(
        ":LAN:AUT?",
        ":LAN:AUT %d",
        """Control whether automatic IP configuration is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    gateway = Channel.control(
        ":LAN:GAT?",
        ":LAN:GAT %s",
        """Control the default gateway address (str).""",
        cast=str,
    )

    dns = Channel.control(
        ":LAN:DNS?",
        ":LAN:DNS %s",
        """Control the DNS server address (str).""",
        cast=str,
    )

    mac_address = Channel.measurement(
        ":LAN:MAC?",
        """Measure the instrument MAC address (str).""",
        cast=str,
    )

    dhcp_server = Channel.measurement(
        ":LAN:DSE?",
        """Measure the DHCP server address (str).""",
        cast=str,
    )

    static_ip_enabled = Channel.control(
        ":LAN:MAN?",
        ":LAN:MAN %d",
        """Control whether static IP configuration is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    ip_address = Channel.control(
        ":LAN:IPAD?",
        ":LAN:IPAD %s",
        """Control the instrument IP address (str).""",
        cast=str,
    )

    subnet_mask = Channel.control(
        ":LAN:SMAS?",
        ":LAN:SMAS %s",
        """Control the subnet mask (str).""",
        cast=str,
    )

    status = Channel.measurement(
        ":LAN:STAT?",
        """Measure the current network configuration status (str).""",
        cast=str,
    )

    visa_address = Channel.measurement(
        ":LAN:VISA?",
        """Measure the instrument VISA address (str).""",
        cast=str,
    )

    mdns_enabled = Channel.control(
        ":LAN:MDNS?",
        ":LAN:MDNS %d",
        """Control whether multicast DNS is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    host_name = Channel.control(
        ":LAN:HOST:NAME?",
        ":LAN:HOST:NAME %s",
        """Control the network host name (str).""",
        cast=str,
    )

    description = Channel.control(
        ":LAN:DESC?",
        ":LAN:DESC %s",
        """Control the network description (str).""",
        cast=str,
    )

    def apply(self) -> None:
        """Apply the pending network configuration.

        This may interrupt the current connection if an address or configuration mode changes.
        """
        self.write(":LAN:APPL")


class TriggerSubsystem(Channel):
    """Represent MSO5000 serial-protocol trigger configuration."""

    rs232_source = Channel.control(
        ":TRIG:RS232:SOUR?",
        ":TRIG:RS232:SOUR %s",
        """Control the RS232 source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    rs232_when = Channel.control(
        ":TRIG:RS232:WHEN?",
        ":TRIG:RS232:WHEN %s",
        """Control the RS232 trigger condition (str).""",
        validator=strict_discrete_set,
        values=["STAR", "ERR", "CERR", "DATA"],
        cast=str,
    )

    rs232_parity = Channel.control(
        ":TRIG:RS232:PAR?",
        ":TRIG:RS232:PAR %s",
        """Control the RS232 parity (str).""",
        validator=strict_discrete_set,
        values=["EVEN", "ODD", "NONE"],
        cast=str,
    )

    rs232_stop = Channel.control(
        ":TRIG:RS232:STOP?",
        ":TRIG:RS232:STOP %g",
        """Control the RS232 stop-bit count (float).""",
        validator=strict_discrete_set,
        values=[1, 1.5, 2],
        cast=float,
    )

    rs232_data = Channel.control(
        ":TRIG:RS232:DATA?",
        ":TRIG:RS232:DATA %d",
        """Control the RS232 trigger data (int).""",
        validator=strict_range,
        values=[0, 255],
        cast=int,
    )

    rs232_width = Channel.control(
        ":TRIG:RS232:WIDT?",
        ":TRIG:RS232:WIDT %d",
        """Control the RS232 data width (int).""",
        validator=strict_discrete_set,
        values=[5, 6, 7, 8],
        cast=int,
    )

    rs232_baud = Channel.control(
        ":TRIG:RS232:BAUD?",
        ":TRIG:RS232:BAUD %d",
        """Control the RS232 baud rate in bits per second (int).""",
        validator=strict_range,
        values=[1, 20_000_000],
        cast=int,
    )

    rs232_level = Channel.control(
        ":TRIG:RS232:LEV?",
        ":TRIG:RS232:LEV %g",
        """Control the RS232 trigger level in Volts (float).""",
        cast=float,
    )

    iic_clock_source = Channel.control(
        ":TRIG:IIC:SCL?",
        ":TRIG:IIC:SCL %s",
        """Control the I2C clock source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iic_data_source = Channel.control(
        ":TRIG:IIC:SDA?",
        ":TRIG:IIC:SDA %s",
        """Control the I2C data source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iic_when = Channel.control(
        ":TRIG:IIC:WHEN?",
        ":TRIG:IIC:WHEN %s",
        """Control the I2C trigger condition (str).""",
        validator=strict_discrete_set,
        values=["STAR", "REST", "STOP", "NACK", "ADDR", "DATA", "ADAT"],
        cast=str,
    )

    iic_address_width = Channel.control(
        ":TRIG:IIC:AWID?",
        ":TRIG:IIC:AWID %d",
        """Control the I2C address width (int).""",
        validator=strict_discrete_set,
        values=[7, 8, 10],
        cast=int,
    )

    iic_address = Channel.control(
        ":TRIG:IIC:ADDR?",
        ":TRIG:IIC:ADDR %d",
        """Control the I2C address (int).""",
        validator=strict_range,
        values=[0, 1023],
        cast=int,
    )

    iic_direction = Channel.control(
        ":TRIG:IIC:DIR?",
        ":TRIG:IIC:DIR %s",
        """Control the I2C transfer direction (str).""",
        validator=strict_discrete_set,
        values=["READ", "WRIT", "RWR"],
        cast=str,
    )

    iic_data = Channel.control(
        ":TRIG:IIC:DATA?",
        ":TRIG:IIC:DATA %d",
        """Control the I2C trigger data (int).""",
        validator=strict_range,
        values=[0, 2**40 - 1],
        cast=int,
    )

    iic_clock_level = Channel.control(
        ":TRIG:IIC:CLEV?",
        ":TRIG:IIC:CLEV %g",
        """Control the I2C clock trigger level in Volts (float).""",
        cast=float,
    )

    iic_data_level = Channel.control(
        ":TRIG:IIC:DLEV?",
        ":TRIG:IIC:DLEV %g",
        """Control the I2C data trigger level in Volts (float).""",
        cast=float,
    )

    iic_data_bytes = Channel.control(
        ":TRIG:IIC:DBYT?",
        ":TRIG:IIC:DBYT %d",
        """Control the I2C trigger data-byte count (int).""",
        validator=strict_range,
        values=[1, 5],
        cast=int,
    )

    can_baud = Channel.control(
        ":TRIG:CAN:BAUD?",
        ":TRIG:CAN:BAUD %d",
        """Control the CAN baud rate in bits per second (int).""",
        validator=strict_range,
        values=[10_000, 5_000_000],
        cast=int,
    )

    can_source = Channel.control(
        ":TRIG:CAN:SOUR?",
        ":TRIG:CAN:SOUR %s",
        """Control the CAN source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    can_source_type = Channel.control(
        ":TRIG:CAN:STYP?",
        ":TRIG:CAN:STYP %s",
        """Control the CAN source type (str).""",
        validator=strict_discrete_set,
        values=["H", "L", "RXTX", "DIFF"],
        cast=str,
    )

    can_when = Channel.control(
        ":TRIG:CAN:WHEN?",
        ":TRIG:CAN:WHEN %s",
        """Control the CAN trigger condition (str).""",
        validator=strict_discrete_set,
        values=[
            "SOF",
            "EOF",
            "IDR",
            "OVER",
            "IDFR",
            "DAT",
            "IDD",
            "ERFR",
            "ERAN",
            "ERCH",
            "ERF",
            "ERR",
            "ERB",
        ],
        cast=str,
    )

    can_sample_point = Channel.control(
        ":TRIG:CAN:SPO?",
        ":TRIG:CAN:SPO %d",
        """Control the CAN sample point in percent (int).""",
        validator=strict_range,
        values=[10, 90],
        cast=int,
    )

    can_level = Channel.control(
        ":TRIG:CAN:LEV?",
        ":TRIG:CAN:LEV %g",
        """Control the CAN trigger level in Volts (float).""",
        cast=float,
    )

    spi_clock_source = Channel.control(
        ":TRIG:SPI:SCL?",
        ":TRIG:SPI:SCL %s",
        """Control the SPI clock source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    spi_data_source = Channel.control(
        ":TRIG:SPI:SDA?",
        ":TRIG:SPI:SDA %s",
        """Control the SPI data source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    spi_when = Channel.control(
        ":TRIG:SPI:WHEN?",
        ":TRIG:SPI:WHEN %s",
        """Control the SPI trigger condition (str).""",
        validator=strict_discrete_set,
        values=["CS", "TIM"],
        cast=str,
    )

    spi_width = Channel.control(
        ":TRIG:SPI:WIDT?",
        ":TRIG:SPI:WIDT %d",
        """Control the SPI data width (int).""",
        validator=strict_range,
        values=[4, 32],
        cast=int,
    )

    spi_data = Channel.control(
        ":TRIG:SPI:DATA?",
        ":TRIG:SPI:DATA %d",
        """Control the SPI trigger data (int).""",
        validator=strict_range,
        values=[0, 2**32 - 1],
        cast=int,
    )

    spi_timeout = Channel.control(
        ":TRIG:SPI:TIM?",
        ":TRIG:SPI:TIM %g",
        """Control the SPI timeout in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 10],
        cast=float,
    )

    spi_slope = Channel.control(
        ":TRIG:SPI:SLOP?",
        ":TRIG:SPI:SLOP %s",
        """Control the SPI clock slope (str).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    spi_clock_level = Channel.control(
        ":TRIG:SPI:CLEV?",
        ":TRIG:SPI:CLEV %g",
        """Control the SPI clock trigger level in Volts (float).""",
        cast=float,
    )

    spi_data_level = Channel.control(
        ":TRIG:SPI:DLEV?",
        ":TRIG:SPI:DLEV %g",
        """Control the SPI data trigger level in Volts (float).""",
        cast=float,
    )

    spi_select_level = Channel.control(
        ":TRIG:SPI:SLEV?",
        ":TRIG:SPI:SLEV %g",
        """Control the SPI slave-select trigger level in Volts (float).""",
        cast=float,
    )

    spi_mode = Channel.control(
        ":TRIG:SPI:MODE?",
        ":TRIG:SPI:MODE %s",
        """Control the SPI slave-select polarity (str).""",
        validator=strict_discrete_set,
        values=["HIGH", "LOW"],
        cast=str,
    )

    spi_cs = Channel.control(
        ":TRIG:SPI:CS?",
        ":TRIG:SPI:CS %s",
        """Control the SPI slave-select source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    flexray_baud = Channel.control(
        ":TRIG:FLEX:BAUD?",
        ":TRIG:FLEX:BAUD %d",
        """Control the FlexRay baud rate in bits per second (int).""",
        validator=strict_discrete_set,
        values=[2_500_000, 5_000_000, 10_000_000],
        cast=int,
    )

    flexray_level = Channel.control(
        ":TRIG:FLEX:LEV?",
        ":TRIG:FLEX:LEV %g",
        """Control the FlexRay trigger level in Volts (float).""",
        cast=float,
    )

    flexray_source = Channel.control(
        ":TRIG:FLEX:SOUR?",
        ":TRIG:FLEX:SOUR %s",
        """Control the FlexRay source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    flexray_when = Channel.control(
        ":TRIG:FLEX:WHEN?",
        ":TRIG:FLEX:WHEN %s",
        """Control the FlexRay trigger condition (str).""",
        validator=strict_discrete_set,
        values=["FRAM", "SYMB", "ERR", "TSS"],
        cast=str,
    )

    iis_alignment = Channel.control(
        ":TRIG:IIS:ALIG?",
        ":TRIG:IIS:ALIG %s",
        """Control the I2S alignment (str).""",
        validator=strict_discrete_set,
        values=["LJ", "RJ", "IIS"],
        cast=str,
    )

    iis_clock_slope = Channel.control(
        ":TRIG:IIS:CLOC:SLOP?",
        ":TRIG:IIS:CLOC:SLOP %s",
        """Control the I2S clock slope (str).""",
        validator=strict_discrete_set,
        values=["NEG", "POS"],
        cast=str,
    )

    iis_source_clock = Channel.control(
        ":TRIG:IIS:SOUR:CLOC?",
        ":TRIG:IIS:SOUR:CLOC %s",
        """Control the I2S clock source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iis_source_data = Channel.control(
        ":TRIG:IIS:SOUR:DATA?",
        ":TRIG:IIS:SOUR:DATA %s",
        """Control the I2S data source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iis_source_word_select = Channel.control(
        ":TRIG:IIS:SOUR:WSEL?",
        ":TRIG:IIS:SOUR:WSEL %s",
        """Control the I2S word-select source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    iis_when = Channel.control(
        ":TRIG:IIS:WHEN?",
        ":TRIG:IIS:WHEN %s",
        """Control the I2S trigger comparison (str).""",
        validator=strict_discrete_set,
        values=["EQU", "NOT", "LESS", "GRE", "INR", "OUTR"],
        cast=str,
    )

    iis_audio = Channel.control(
        ":TRIG:IIS:AUD?",
        ":TRIG:IIS:AUD %s",
        """Control the I2S audio channel (str).""",
        validator=strict_discrete_set,
        values=["RIGH", "LEFT", "EITH"],
        cast=str,
    )

    iis_data = Channel.control(
        ":TRIG:IIS:DATA?",
        ":TRIG:IIS:DATA %d",
        """Control the I2S trigger data (int).""",
        validator=strict_range,
        values=[0, 2**32 - 1],
        cast=int,
    )

    lin_source = Channel.control(
        ":TRIG:LIN:SOUR?",
        ":TRIG:LIN:SOUR %s",
        """Control the LIN source (str).""",
        validator=strict_discrete_set,
        values=PROTOCOL_SOURCES,
        cast=str,
    )

    lin_id = Channel.control(
        ":TRIG:LIN:ID?",
        ":TRIG:LIN:ID %d",
        """Control the LIN identifier (int).""",
        validator=strict_range,
        values=[0, 63],
        cast=int,
    )

    lin_baud = Channel.control(
        ":TRIG:LIN:BAUD?",
        ":TRIG:LIN:BAUD %d",
        """Control the LIN baud rate in bits per second (int).""",
        validator=strict_range,
        values=[1_000, 20_000_000],
        cast=int,
    )

    lin_standard = Channel.control(
        ":TRIG:LIN:STAN?",
        ":TRIG:LIN:STAN %s",
        """Control the LIN standard (str).""",
        validator=strict_discrete_set,
        values=["1X", "2X", "BOTH"],
        cast=str,
    )

    lin_sample_point = Channel.control(
        ":TRIG:LIN:SAMP?",
        ":TRIG:LIN:SAMP %d",
        """Control the LIN sample point in percent (int).""",
        validator=strict_range,
        values=[10, 90],
        cast=int,
    )

    lin_when = Channel.control(
        ":TRIG:LIN:WHEN?",
        ":TRIG:LIN:WHEN %s",
        """Control the LIN trigger condition (str).""",
        validator=strict_discrete_set,
        values=["SYNC", "ID", "DATA", "IDD", "SLE", "WAK", "ERR"],
        cast=str,
    )

    lin_level = Channel.control(
        ":TRIG:LIN:LEV?",
        ":TRIG:LIN:LEV %g",
        """Control the LIN trigger level in Volts (float).""",
        cast=float,
    )

    m1553_source = Channel.control(
        ":TRIG:M1553:SOUR?",
        ":TRIG:M1553:SOUR %s",
        """Control the MIL-STD-1553 source (str).""",
        validator=strict_discrete_set,
        values=ANALOG_SOURCES,
        cast=str,
    )

    m1553_when = Channel.control(
        ":TRIG:M1553:WHEN?",
        ":TRIG:M1553:WHEN %s",
        """Control the MIL-STD-1553 trigger condition (str).""",
        validator=strict_discrete_set,
        values=["SYNC", "DATA", "CMD", "STAT", "ERR"],
        cast=str,
    )

    m1553_polarity = Channel.control(
        ":TRIG:M1553:POL?",
        ":TRIG:M1553:POL %s",
        """Control the MIL-STD-1553 polarity (str).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    m1553_alevel = Channel.control(
        ":TRIG:M1553:ALEV?",
        ":TRIG:M1553:ALEV %g",
        """Control the MIL-STD-1553 upper trigger level in Volts (float).""",
        cast=float,
    )

    m1553_blevel = Channel.control(
        ":TRIG:M1553:BLEV?",
        ":TRIG:M1553:BLEV %g",
        """Control the MIL-STD-1553 lower trigger level in Volts (float).""",
        cast=float,
    )


class MSO5000Channel(RigolOscilloscopeChannel):
    """Represent an analog input channel of a Rigol MSO5000 oscilloscope."""

    bandwidth_limit_values = ["20M", "100M", "200M", "OFF"]
    probe_values = PROBE_ATTENUATIONS

    vernier_enabled = Channel.control(
        ":CHAN{ch}:VERN?",
        ":CHAN{ch}:VERN %d",
        """Control whether fine vertical-scale adjustment is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )


class MSO5000(RigolOscilloscope):
    """Control the Rigol MSO5000 series oscilloscopes.

    This driver supports the MSO5072, MSO5074, MSO5102, MSO5104, MSO5204,
    and MSO5354 models. It provides analog-channel, acquisition, measurement,
    timebase, trigger, waveform-transfer, network, system, and storage controls.

    :param adapter: VISA resource name or adapter object used to communicate with the instrument.
    :param name: Human-readable instrument name.
    :param kwargs: Connection settings forwarded to the adapter.
    """

    def __init__(self, adapter: AdapterType, name: str = "Rigol MSO5000", **kwargs):
        super().__init__(adapter, name, **kwargs)

    ch_1 = Instrument.ChannelCreator(MSO5000Channel, 1)
    ch_2 = Instrument.ChannelCreator(MSO5000Channel, 2)
    ch_3 = Instrument.ChannelCreator(MSO5000Channel, 3)
    ch_4 = Instrument.ChannelCreator(MSO5000Channel, 4)
    measurements = Instrument.ChannelCreator(MeasurementSubsystem)
    cursor = Instrument.ChannelCreator(CursorSubsystem)
    display = Instrument.ChannelCreator(DisplaySubsystem)
    histogram = Instrument.ChannelCreator(HistogramSubsystem)
    mask = Instrument.ChannelCreator(MaskSubsystem)
    math_1 = Instrument.ChannelCreator(MathChannel, 1)
    math_2 = Instrument.ChannelCreator(MathChannel, 2)
    math_3 = Instrument.ChannelCreator(MathChannel, 3)
    math_4 = Instrument.ChannelCreator(MathChannel, 4)
    recording = Instrument.ChannelCreator(RecordingSubsystem)
    references = Instrument.ChannelCreator(ReferenceSubsystem)
    search = Instrument.ChannelCreator(SearchSubsystem)
    quick = Instrument.ChannelCreator(QuickSubsystem)
    bode_plot = Instrument.ChannelCreator(BodePlotSubsystem)
    counter = Instrument.ChannelCreator(CounterSubsystem)
    dvm = Instrument.ChannelCreator(DVMSubsystem)
    power_analysis = Instrument.ChannelCreator(PowerAnalysisSubsystem)
    awg_1 = Instrument.ChannelCreator(AWGChannel, 1)
    awg_2 = Instrument.ChannelCreator(AWGChannel, 2)
    logic_analyzer = Instrument.ChannelCreator(LogicAnalyzerSubsystem)
    network = Instrument.ChannelCreator(NetworkSubsystem)
    digital_channels = Instrument.MultiChannelCreator(DigitalChannel, list(range(16)), prefix="d_")
    pod_1 = Instrument.ChannelCreator(LogicPod, 1)
    pod_2 = Instrument.ChannelCreator(LogicPod, 2)
    bus_1 = Instrument.ChannelCreator(BusChannel, 1)
    bus_2 = Instrument.ChannelCreator(BusChannel, 2)
    bus_3 = Instrument.ChannelCreator(BusChannel, 3)
    bus_4 = Instrument.ChannelCreator(BusChannel, 4)
    protocol_trigger = Instrument.ChannelCreator(TriggerSubsystem)

    acquisition_memory_depth_values = [
        "AUTO",
        1_000,
        10_000,
        100_000,
        1_000_000,
        10_000_000,
        25_000_000,
        50_000_000,
        100_000_000,
        200_000_000,
    ]
    acquisition_type_values = ["NORM", "AVER", "PEAK", "HRES"]
    trigger_holdoff_validator = strict_range
    trigger_holdoff_values = [8e-9, 10]
    edge_trigger_source_values = [*TRIGGER_SOURCES, "ACL"]
    waveform_source_values = WAVEFORM_SOURCES

    event_status_enable_bits = Instrument.control(
        "*ESE?",
        "*ESE %d",
        """Control the Standard Event Status Enable Register (int from 0 to 255).""",
        validator=strict_range,
        values=[0, 255],
        cast=int,
    )

    service_request_enable_bits = Instrument.control(
        "*SRE?",
        "*SRE %d",
        """Control the Service Request Enable Register (int from 0 to 255).""",
        validator=strict_range,
        values=[0, 255],
        cast=int,
    )

    csv_length = Instrument.control(
        ":SAVE:CSV:LENG?",
        ":SAVE:CSV:LENG %s",
        """Control CSV storage length: ``"DISP"`` or ``"MAX"``.""",
        validator=strict_discrete_set,
        values=["DISP", "MAX"],
        cast=str,
    )

    image_type = Instrument.control(
        ":SAVE:IMAG:TYPE?",
        ":SAVE:IMAG:TYPE %s",
        """Control the stored image type: BMP24, JPEG, PNG, or TIFF.""",
        validator=strict_discrete_set,
        values=["BMP24", "JPEG", "PNG", "TIFF"],
        cast=str,
    )

    image_inverted = Instrument.control(
        ":SAVE:IMAG:INV?",
        ":SAVE:IMAG:INV %d",
        """Control whether stored images are inverted (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    image_color = Instrument.control(
        ":SAVE:IMAG:COL?",
        ":SAVE:IMAG:COL %s",
        """Control whether stored images use color (``"COL"``) or grayscale (``"GRAY"``).""",
        validator=strict_discrete_set,
        values=["COL", "GRAY"],
        cast=str,
    )

    save_complete = Instrument.measurement(
        ":SAVE:STAT?",
        """Measure whether the current save operation is complete (bool).""",
        cast=bool,
    )

    auxiliary_output = Instrument.control(
        ":SYST:AOUT?",
        ":SYST:AOUT %s",
        """Control the rear-panel trigger output function: TOUT or PFA.""",
        validator=strict_discrete_set,
        values=["TOUT", "PFA"],
        cast=str,
    )

    autoscale_enabled = Instrument.control(
        ":SYST:AUT?",
        ":SYST:AUT %d",
        """Control whether the front-panel AUTO function is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    beeper_enabled = Instrument.control(
        ":SYST:BEEP?",
        ":SYST:BEEP %d",
        """Control whether the beeper is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    system_date = Instrument.control(
        ":SYST:DATE?",
        ":SYST:DATE %s",
        """Control the system date as a ``(year, month, day)`` tuple.""",
        validator=_validate_system_date,
        values=None,
        cast=int,
        get_process_list=tuple,
    )

    horizontal_grid_count = Instrument.measurement(
        ":SYST:GAM?",
        """Measure the fixed number of horizontal screen divisions (int).""",
        cast=int,
    )

    gpib_address = Instrument.control(
        ":SYST:GPIB?",
        ":SYST:GPIB %d",
        """Control the GPIB address (int from 1 to 30).""",
        validator=strict_range,
        values=[1, 30],
        cast=int,
    )

    system_language = Instrument.control(
        ":SYST:LANG?",
        ":SYST:LANG %s",
        """Control the user-interface language (str).""",
        validator=strict_discrete_set,
        values=[
            "SCH",
            "TCH",
            "KOR",
            "JAP",
            "ENGL",
            "GERM",
            "PORT",
            "POL",
            "FREN",
            "RUSS",
            "SPAN",
            "THAI",
            "IND",
        ],
        cast=str,
    )

    power_on_configuration = Instrument.control(
        ":SYST:PON?",
        ":SYST:PON %s",
        """Control the power-on configuration: LAT or DEF.""",
        validator=strict_discrete_set,
        values=["LAT", "DEF"],
        cast=str,
    )

    analog_channel_count = Instrument.measurement(
        ":SYST:RAM?",
        """Measure the number of analog channels (int).""",
        cast=int,
    )

    screen_saver_time = Instrument.control(
        ":SYST:SSAV:TIME?",
        ":SYST:SSAV:TIME %d",
        """Control the screen-saver delay in minutes (int from 1 to 999).

        The getter may also return ``"OFF"`` on firmware that supports disabling it.
        """,
        validator=strict_range,
        values=[1, 999],
        cast=cast_or_str(int),
    )

    system_time = Instrument.control(
        ":SYST:TIME?",
        ":SYST:TIME %s",
        """Control the system time as an ``(hours, minutes, seconds)`` tuple.""",
        validator=_validate_system_time,
        values=None,
        cast=int,
        get_process_list=tuple,
    )

    front_panel_locked = Instrument.control(
        ":SYST:LOCK?",
        ":SYST:LOCK %d",
        """Control whether the front-panel controls are locked (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    hardware_modules = Instrument.measurement(
        ":SYST:MOD?",
        """Measure the five hardware-module presence flags (list[int]).""",
        cast=int,
        get_process_list=list,
    )

    logic_analyzer_sample_rate = Instrument.measurement(
        ":ACQ:LA:SRAT?",
        """Measure the logic-analyzer sample rate in samples per second (float).""",
    )

    logic_analyzer_memory_depth = Instrument.measurement(
        ":ACQ:LA:MDEP?",
        """Measure the logic-analyzer memory depth in points (float).""",
    )

    anti_aliasing_enabled = Instrument.control(
        ":ACQ:AAL?",
        ":ACQ:AAL %d",
        """Control whether anti-aliasing is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    delayed_sweep_enabled = Instrument.control(
        ":TIM:DEL:ENAB?",
        ":TIM:DEL:ENAB %d",
        """Control whether delayed sweep is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    delayed_timebase_offset = Instrument.control(
        ":TIM:DEL:OFFS?",
        ":TIM:DEL:OFFS %g",
        """Control the delayed-timebase offset in seconds (float).

        The valid range depends on the main timebase and delayed-timebase scale.
        """,
    )

    delayed_timebase_scale = Instrument.control(
        ":TIM:DEL:SCAL?",
        ":TIM:DEL:SCAL %g",
        """Control the delayed-timebase scale in seconds per division (float).

        The maximum is the current main timebase scale. With vernier disabled,
        the instrument uses discrete 1-2-5 steps.
        """,
    )

    horizontal_reference_mode = Instrument.control(
        ":TIM:HREF:MODE?",
        ":TIM:HREF:MODE %s",
        """Control the horizontal reference mode.

        Valid values are CENT, LB, RB, TRIG, and USER.
        """,
        validator=strict_discrete_set,
        values=["CENT", "LB", "RB", "TRIG", "USER"],
        cast=str,
    )

    horizontal_reference_position = Instrument.control(
        ":TIM:HREF:POS?",
        ":TIM:HREF:POS %d",
        """Control the user-defined horizontal reference position (-500 to 500).""",
        validator=strict_range,
        values=[-500, 500],
        cast=int,
    )

    timebase_vernier_enabled = Instrument.control(
        ":TIM:VERN?",
        ":TIM:VERN %d",
        """Control whether fine timebase-scale adjustment is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    trigger_noise_rejection_enabled = Instrument.control(
        ":TRIG:NREJ?",
        ":TRIG:NREJ %d",
        """Control whether trigger noise rejection is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    pulse_trigger_source = Instrument.control(
        ":TRIG:PULS:SOUR?",
        ":TRIG:PULS:SOUR %s",
        """Control the Pulse-trigger source (str).""",
        validator=strict_discrete_set,
        values=[
            *[f"D{number}" for number in range(16)],
            *[f"CHAN{number}" for number in range(1, 5)],
        ],
        cast=str,
    )

    pulse_trigger_condition = Instrument.control(
        ":TRIG:PULS:WHEN?",
        ":TRIG:PULS:WHEN %s",
        """Control the Pulse-trigger condition: GRE, LESS, or GLES.""",
        validator=strict_discrete_set,
        values=["GRE", "LESS", "GLES"],
        cast=str,
    )

    pulse_trigger_upper_width = Instrument.control(
        ":TRIG:PULS:UWID?",
        ":TRIG:PULS:UWID %g",
        """Control the Pulse-trigger upper width limit in seconds (float).

        The valid range extends from the current lower width limit to 10 seconds.
        """,
    )

    pulse_trigger_lower_width = Instrument.control(
        ":TRIG:PULS:LWID?",
        ":TRIG:PULS:LWID %g",
        """Control the Pulse-trigger lower width limit in seconds (float).

        The valid range extends from 800 ps to the current upper width limit.
        """,
    )

    pulse_trigger_level = Instrument.control(
        ":TRIG:PULS:LEV?",
        ":TRIG:PULS:LEV %g",
        """Control the Pulse-trigger level (float).

        The valid range depends on the selected trigger source, channel scale, and offset.
        """,
    )

    slope_trigger_source = Instrument.control(
        ":TRIG:SLOP:SOUR?",
        ":TRIG:SLOP:SOUR %s",
        """Control the Slope-trigger source (str).""",
        validator=strict_discrete_set,
        values=[f"CHAN{number}" for number in range(1, 5)],
        cast=str,
    )

    slope_trigger_condition = Instrument.control(
        ":TRIG:SLOP:WHEN?",
        ":TRIG:SLOP:WHEN %s",
        """Control the Slope-trigger condition: GRE, LESS, or GLES.""",
        validator=strict_discrete_set,
        values=["GRE", "LESS", "GLES"],
        cast=str,
    )

    slope_trigger_upper_time = Instrument.control(
        ":TRIG:SLOP:TUPP?",
        ":TRIG:SLOP:TUPP %g",
        """Control the Slope-trigger upper time limit in seconds (float).

        The valid range extends from the current lower time limit to 10 seconds.
        """,
    )

    slope_trigger_lower_time = Instrument.control(
        ":TRIG:SLOP:TLOW?",
        ":TRIG:SLOP:TLOW %g",
        """Control the Slope-trigger lower time limit in seconds (float).

        The valid range extends from 800 ps to the current upper time limit.
        """,
    )

    slope_trigger_window = Instrument.control(
        ":TRIG:SLOP:WIND?",
        ":TRIG:SLOP:WIND %s",
        """Control the Slope-trigger vertical window: TA, TB, or TAB.""",
        validator=strict_discrete_set,
        values=["TA", "TB", "TAB"],
        cast=str,
    )

    slope_trigger_upper_level = Instrument.control(
        ":TRIG:SLOP:ALEV?",
        ":TRIG:SLOP:ALEV %g",
        """Control the Slope-trigger upper level (float).

        The valid range depends on the lower level, channel scale, and offset.
        """,
    )

    slope_trigger_lower_level = Instrument.control(
        ":TRIG:SLOP:BLEV?",
        ":TRIG:SLOP:BLEV %g",
        """Control the Slope-trigger lower level (float).

        The valid range depends on the upper level, channel scale, and offset.
        """,
    )

    video_trigger_source = Instrument.control(
        ":TRIG:VID:SOUR?",
        ":TRIG:VID:SOUR %s",
        """Control the Video-trigger source (str).""",
        validator=strict_discrete_set,
        values=[f"CHAN{number}" for number in range(1, 5)],
        cast=str,
    )

    video_trigger_polarity = Instrument.control(
        ":TRIG:VID:POL?",
        ":TRIG:VID:POL %s",
        """Control the Video-trigger polarity: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    video_trigger_mode = Instrument.control(
        ":TRIG:VID:MODE?",
        ":TRIG:VID:MODE %s",
        """Control the Video-trigger sync mode: ODDF, EVEN, LINE, or ALIN.""",
        validator=strict_discrete_set,
        values=["ODDF", "EVEN", "LINE", "ALIN"],
        cast=str,
    )

    video_trigger_line = Instrument.control(
        ":TRIG:VID:LINE?",
        ":TRIG:VID:LINE %d",
        """Control the Video-trigger line number (int).

        The valid range depends on the selected video standard.
        """,
        cast=int,
    )

    video_trigger_standard = Instrument.control(
        ":TRIG:VID:STAN?",
        ":TRIG:VID:STAN %s",
        """Control the Video-trigger standard (str).""",
        validator=strict_discrete_set,
        values=[
            "PALS",
            "NTSC",
            "480P",
            "576P",
            "720P60",
            "720P50",
            "720P30",
            "720P25",
            "720P24",
            "1080P60",
            "1080P50",
            "1080P30",
            "1080P25",
            "1080P24",
            "1080I60",
            "1080I50",
        ],
        cast=str,
    )

    video_trigger_level = Instrument.control(
        ":TRIG:VID:LEV?",
        ":TRIG:VID:LEV %g",
        """Control the Video-trigger level (float).

        The valid range depends on the selected channel scale and offset.
        """,
    )

    timeout_trigger_source = Instrument.control(
        ":TRIG:TIM:SOUR?",
        ":TRIG:TIM:SOUR %s",
        """Control the Timeout-trigger source (str).""",
        validator=strict_discrete_set,
        values=[
            *[f"D{number}" for number in range(16)],
            *[f"CHAN{number}" for number in range(1, 5)],
        ],
        cast=str,
    )

    timeout_trigger_slope = Instrument.control(
        ":TRIG:TIM:SLOP?",
        ":TRIG:TIM:SLOP %s",
        """Control the Timeout-trigger slope: POS, NEG, or RFAL.""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "RFAL"],
        cast=str,
    )

    timeout_trigger_time = Instrument.control(
        ":TRIG:TIM:TIME?",
        ":TRIG:TIM:TIME %g",
        """Control the Timeout-trigger time in seconds (float).""",
        validator=strict_range,
        values=[16e-9, 10],
    )

    timeout_trigger_level = Instrument.control(
        ":TRIG:TIM:LEV?",
        ":TRIG:TIM:LEV %g",
        """Control the Timeout-trigger level (float).

        The valid range depends on the selected source.
        """,
    )

    window_trigger_source = Instrument.control(
        ":TRIG:WIND:SOUR?",
        ":TRIG:WIND:SOUR %s",
        """Control the Window-trigger source (str).""",
        validator=strict_discrete_set,
        values=[f"CHAN{number}" for number in range(1, 5)],
        cast=str,
    )

    window_trigger_slope = Instrument.control(
        ":TRIG:WIND:SLOP?",
        ":TRIG:WIND:SLOP %s",
        """Control the Window-trigger slope: POS, NEG, or RFAL.""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "RFAL"],
        cast=str,
    )

    window_trigger_position = Instrument.control(
        ":TRIG:WIND:POS?",
        ":TRIG:WIND:POS %s",
        """Control the Window-trigger position: EXIT, ENT, or TIME.""",
        validator=strict_discrete_set,
        values=["EXIT", "ENT", "TIME"],
        cast=str,
    )

    window_trigger_time = Instrument.control(
        ":TRIG:WIND:TIME?",
        ":TRIG:WIND:TIME %g",
        """Control the Window-trigger time in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 10],
    )

    window_trigger_upper_level = Instrument.control(
        ":TRIG:WIND:ALEV?",
        ":TRIG:WIND:ALEV %g",
        """Control the Window-trigger upper level (float).

        The valid range depends on the lower level, channel scale, and offset.
        """,
    )

    window_trigger_lower_level = Instrument.control(
        ":TRIG:WIND:BLEV?",
        ":TRIG:WIND:BLEV %g",
        """Control the Window-trigger lower level (float).

        The valid range depends on the upper level, channel scale, and offset.
        """,
    )

    pattern_trigger_pattern: InstrumentProperty[list[str]] = Instrument.control(
        ":TRIG:PATT:PATT?",
        ":TRIG:PATT:PATT %s",
        """Control the complete Pattern-trigger pattern as 20 channel values (list[str]).

        Values correspond to CH1-CH4 followed by D0-D15. Each value is H, L, X, R,
        or F, and at most one channel may specify an edge (R or F).
        """,
        validator=_validate_trigger_pattern,
        values=(frozenset({"H", "L", "X", "R", "F"}), 1),
        cast=str,
        get_process_list=identity,
    )

    pattern_trigger_source = Instrument.control(
        ":TRIG:PATT:SOUR?",
        ":TRIG:PATT:SOUR %s",
        """Control the source selected for Pattern-trigger level adjustment (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    duration_trigger_source = Instrument.control(
        ":TRIG:DUR:SOUR?",
        ":TRIG:DUR:SOUR %s",
        """Control the Duration-trigger source (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    duration_trigger_pattern: InstrumentProperty[list[str]] = Instrument.control(
        ":TRIG:DUR:TYPE?",
        ":TRIG:DUR:TYPE %s",
        """Control the complete Duration-trigger pattern as 20 channel values (list[str]).

        Values correspond to CH1-CH4 followed by D0-D15 and must be H, L, or X.
        """,
        validator=_validate_trigger_pattern,
        values=(frozenset({"H", "L", "X"}), 0),
        cast=str,
        get_process_list=identity,
    )

    duration_trigger_condition = Instrument.control(
        ":TRIG:DUR:WHEN?",
        ":TRIG:DUR:WHEN %s",
        """Control the Duration-trigger condition: GRE, LESS, GLES, or UNGL.""",
        validator=strict_discrete_set,
        values=["GRE", "LESS", "GLES", "UNGL"],
        cast=str,
    )

    duration_trigger_upper_time = Instrument.control(
        ":TRIG:DUR:TUPP?",
        ":TRIG:DUR:TUPP %g",
        """Control the Duration-trigger upper time limit in seconds (float).""",
        validator=strict_range,
        values=[8e-10, 10],
    )

    duration_trigger_lower_time = Instrument.control(
        ":TRIG:DUR:TLOW?",
        ":TRIG:DUR:TLOW %g",
        """Control the Duration-trigger lower time limit in seconds (float).""",
        validator=strict_range,
        values=[8e-10, 10],
    )

    runt_trigger_source = Instrument.control(
        ":TRIG:RUNT:SOUR?",
        ":TRIG:RUNT:SOUR %s",
        """Control the Runt-trigger source (str).""",
        validator=strict_discrete_set,
        values=[f"CHAN{number}" for number in range(1, 5)],
        cast=str,
    )

    runt_trigger_polarity = Instrument.control(
        ":TRIG:RUNT:POL?",
        ":TRIG:RUNT:POL %s",
        """Control the Runt-trigger polarity: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    runt_trigger_condition = Instrument.control(
        ":TRIG:RUNT:WHEN?",
        ":TRIG:RUNT:WHEN %s",
        """Control the Runt-trigger qualifier: NONE, GRE, LESS, or GLES.""",
        validator=strict_discrete_set,
        values=["NONE", "GRE", "LESS", "GLES"],
        cast=str,
    )

    runt_trigger_upper_width = Instrument.control(
        ":TRIG:RUNT:WUPP?",
        ":TRIG:RUNT:WUPP %g",
        """Control the Runt-trigger upper pulse-width limit in seconds (float).""",
        validator=strict_range,
        values=[8.01e-9, 10],
    )

    runt_trigger_lower_width = Instrument.control(
        ":TRIG:RUNT:WLOW?",
        ":TRIG:RUNT:WLOW %g",
        """Control the Runt-trigger lower pulse-width limit in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 9.9],
    )

    runt_trigger_upper_level = Instrument.control(
        ":TRIG:RUNT:ALEV?",
        ":TRIG:RUNT:ALEV %g",
        """Control the Runt-trigger upper level (float).""",
    )

    runt_trigger_lower_level = Instrument.control(
        ":TRIG:RUNT:BLEV?",
        ":TRIG:RUNT:BLEV %g",
        """Control the Runt-trigger lower level (float).""",
    )

    delay_trigger_source_a = Instrument.control(
        ":TRIG:DEL:SA?",
        ":TRIG:DEL:SA %s",
        """Control source A of the Delay trigger (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    delay_trigger_slope_a = Instrument.control(
        ":TRIG:DEL:SLOPA?",
        ":TRIG:DEL:SLOPA %s",
        """Control the edge of Delay-trigger source A: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    delay_trigger_source_b = Instrument.control(
        ":TRIG:DEL:SB?",
        ":TRIG:DEL:SB %s",
        """Control source B of the Delay trigger (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    delay_trigger_slope_b = Instrument.control(
        ":TRIG:DEL:SLOPB?",
        ":TRIG:DEL:SLOPB %s",
        """Control the edge of Delay-trigger source B: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    delay_trigger_condition = Instrument.control(
        ":TRIG:DEL:TYPE?",
        ":TRIG:DEL:TYPE %s",
        """Control the Delay-trigger condition: GRE, LESS, GLES, or GOUT.""",
        validator=strict_discrete_set,
        values=["GRE", "LESS", "GLES", "GOUT"],
        cast=str,
    )

    delay_trigger_upper_time = Instrument.control(
        ":TRIG:DEL:TUPP?",
        ":TRIG:DEL:TUPP %g",
        """Control the Delay-trigger upper time limit in seconds (float).""",
        validator=strict_range,
        values=[8.01e-9, 10],
    )

    delay_trigger_lower_time = Instrument.control(
        ":TRIG:DEL:TLOW?",
        ":TRIG:DEL:TLOW %g",
        """Control the Delay-trigger lower time limit in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 9.9],
    )

    delay_trigger_source_a_level = Instrument.control(
        ":TRIG:DEL:ALEV?",
        ":TRIG:DEL:ALEV %g",
        """Control the threshold level for Delay-trigger source A (float).

        The valid range depends on the selected source, channel scale, and offset.
        """,
    )

    delay_trigger_source_b_level = Instrument.control(
        ":TRIG:DEL:BLEV?",
        ":TRIG:DEL:BLEV %g",
        """Control the threshold level for Delay-trigger source B (float).

        The valid range depends on the selected source, channel scale, and offset.
        """,
    )

    setup_hold_data_source = Instrument.control(
        ":TRIG:SHOL:DSRC?",
        ":TRIG:SHOL:DSRC %s",
        """Control the data source of the Setup/Hold trigger (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    setup_hold_clock_source = Instrument.control(
        ":TRIG:SHOL:CSRC?",
        ":TRIG:SHOL:CSRC %s",
        """Control the clock source of the Setup/Hold trigger (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    setup_hold_clock_slope = Instrument.control(
        ":TRIG:SHOL:SLOP?",
        ":TRIG:SHOL:SLOP %s",
        """Control the Setup/Hold clock edge: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    setup_hold_data_pattern = Instrument.control(
        ":TRIG:SHOL:PATT?",
        ":TRIG:SHOL:PATT %s",
        """Control the Setup/Hold data pattern: H or L.""",
        validator=strict_discrete_set,
        values=["H", "L"],
        cast=str,
    )

    setup_hold_type = Instrument.control(
        ":TRIG:SHOL:TYPE?",
        ":TRIG:SHOL:TYPE %s",
        """Control the Setup/Hold trigger type: SET, HOLD, or SETH.""",
        validator=strict_discrete_set,
        values=["SET", "HOLD", "SETH"],
        cast=str,
    )

    setup_hold_setup_time = Instrument.control(
        ":TRIG:SHOL:STIM?",
        ":TRIG:SHOL:STIM %g",
        """Control the Setup/Hold setup time in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 1],
    )

    setup_hold_hold_time = Instrument.control(
        ":TRIG:SHOL:HTIM?",
        ":TRIG:SHOL:HTIM %g",
        """Control the Setup/Hold hold time in seconds (float).""",
        validator=strict_range,
        values=[8e-9, 1],
    )

    setup_hold_data_level = Instrument.control(
        ":TRIG:SHOL:DLEV?",
        ":TRIG:SHOL:DLEV %g",
        """Control the Setup/Hold data-source threshold level (float).""",
    )

    setup_hold_clock_level = Instrument.control(
        ":TRIG:SHOL:CLEV?",
        ":TRIG:SHOL:CLEV %g",
        """Control the Setup/Hold clock-source threshold level (float).""",
    )

    nth_edge_trigger_source = Instrument.control(
        ":TRIG:NEDG:SOUR?",
        ":TRIG:NEDG:SOUR %s",
        """Control the Nth-Edge trigger source (str).""",
        validator=strict_discrete_set,
        values=TRIGGER_SOURCES,
        cast=str,
    )

    nth_edge_trigger_slope = Instrument.control(
        ":TRIG:NEDG:SLOP?",
        ":TRIG:NEDG:SLOP %s",
        """Control the Nth-Edge trigger slope: POS or NEG.""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    nth_edge_trigger_idle_time = Instrument.control(
        ":TRIG:NEDG:IDLE?",
        ":TRIG:NEDG:IDLE %g",
        """Control the Nth-Edge trigger idle time in seconds (float).""",
        validator=strict_range,
        values=[16e-9, 10],
    )

    nth_edge_trigger_edge_count = Instrument.control(
        ":TRIG:NEDG:EDGE?",
        ":TRIG:NEDG:EDGE %d",
        """Control the Nth-Edge trigger edge count (int from 1 to 65535).""",
        validator=strict_range,
        values=[1, 65535],
        cast=int,
    )

    nth_edge_trigger_level = Instrument.control(
        ":TRIG:NEDG:LEV?",
        ":TRIG:NEDG:LEV %g",
        """Control the Nth-Edge trigger threshold level (float).""",
    )

    waveform_points = Instrument.control(
        ":WAV:POIN?",
        ":WAV:POIN %d",
        """Control the number of waveform points to read (int).

        The valid range depends on the waveform reading mode and memory depth.
        """,
        cast=int,
    )

    def get_waveform_preamble(self) -> dict[str, int | float]:
        """Return the ten waveform scaling parameters as a dictionary."""
        return self._query_waveform_preamble()

    def waveform_data(self) -> np.ndarray:
        """Read waveform points in the currently selected return format.

        BYTE and WORD return unsigned raw sample codes with the IEEE block header removed.
        ASC returns the physical values supplied by the instrument.
        """
        waveform_format = self.waveform_format
        if waveform_format == "ASC":
            response = self.ask(":WAV:DATA?").strip()
            if response.startswith("#"):
                payload = _parse_ieee_block(response.encode(), "ASCII waveform response")
                response = payload.decode()
            return np.fromstring(response.rstrip(","), dtype=float, sep=",")

        self.write(":WAV:DATA?")
        payload = self._read_ieee_block("Waveform response")

        if waveform_format == "WORD" and len(payload) % 2:
            raise ValueError("WORD waveform data contains an odd number of bytes.")

        if waveform_format == "WORD" and any(payload[1::2]):
            raise ValueError(
                "WORD waveform data contains non-zero upper bytes, contrary to the "
                "MSO5000 programming guide. Use BYTE or ASC format with this firmware."
            )

        dtype = np.dtype("<u2") if waveform_format == "WORD" else np.dtype("u1")
        return np.frombuffer(payload, dtype=dtype)

    def query_event_status_register(self) -> int:
        """Return and clear the Standard Event Status Register."""
        return int(self.ask("*ESR?"))

    def set_pattern_trigger_level(self, source: str, level: float) -> None:
        """Set the Pattern-trigger level for an analog or digital channel.

        :param source: Analog or digital trigger source.
        :param level: Trigger threshold in the source's units.
        """
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        self.write(f":TRIG:PATT:LEV {source},{level:g}")

    def get_pattern_trigger_level(self, source: str) -> float:
        """Return the Pattern-trigger level for an analog or digital channel.

        :param source: Analog or digital trigger source.
        """
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        return float(self.ask(f":TRIG:PATT:LEV? {source}"))

    def set_duration_trigger_level(self, source: str, level: float) -> None:
        """Set the Duration-trigger level for an analog or digital channel.

        :param source: Analog or digital trigger source.
        :param level: Trigger threshold in the source's units.
        """
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        self.write(f":TRIG:DUR:LEV {source},{level:g}")

    def get_duration_trigger_level(self, source: str) -> float:
        """Return the Duration-trigger level for an analog or digital channel.

        :param source: Analog or digital trigger source.
        """
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        return float(self.ask(f":TRIG:DUR:LEV? {source}"))

    def download_screenshot(self) -> bytes:
        """Download the current display as BMP data."""
        self.write(":DISP:DATA?")
        payload = self._read_ieee_block("Screenshot response")
        if not payload.startswith(b"BM"):
            raise ValueError("Screenshot response does not contain BMP data.")
        return payload

    def save_state(self, register: int) -> None:
        """Save the current instrument state to a register from 0 to 49.

        :param register: Internal state register from 0 to 49.
        """
        register = strict_range(register, [0, 49])
        self.write(f"*SAV {register}")

    def recall_state(self) -> None:
        """Recall the instrument state selected by the instrument."""
        self.write("*RCL")

    def save_reference_waveform(self, reference: int) -> None:
        """Save a reference waveform to an internal reference slot from 1 to 10.

        :param reference: Reference slot number from 1 to 10.
        """
        reference = strict_range(reference, [1, 10])
        self.write(f":REF:SAVE {reference}")

    def save_csv(self, path: str) -> None:
        """Save the displayed waveform data as a CSV file at ``path``.

        :param path: Destination path on the instrument filesystem.
        """
        self.write(f":SAVE:CSV {path}")

    def set_csv_channel_enabled(self, channel: str, enabled: bool) -> None:
        """Set whether ``channel`` is included in saved CSV files.

        :param channel: Analog-channel or logic-pod name.
        :param enabled: Whether the channel is included in CSV exports.
        """
        channel = strict_discrete_set(channel, CSV_CHANNELS)
        enabled = strict_discrete_set(enabled, [True, False])
        self.write(f":SAVE:CSV:CHAN {channel},{int(enabled)}")

    def get_csv_channel_enabled(self, channel: str) -> bool:
        """Return whether ``channel`` is included in saved CSV files.

        :param channel: Analog-channel or logic-pod name.
        """
        channel = strict_discrete_set(channel, CSV_CHANNELS)
        return bool(int(self.ask(f":SAVE:CSV:CHAN? {channel}")))

    def save_image(self, path: str) -> None:
        """Save the current display image at ``path``.

        :param path: Destination path on the instrument filesystem.
        """
        self.write(f":SAVE:IMAG {path}")

    def save_setup(self, path: str) -> None:
        """Save the current oscilloscope setup at ``path``.

        :param path: Destination path on the instrument filesystem.
        """
        self.write(f":SAVE:SET {path}")

    def save_waveform(self, path: str) -> None:
        """Save waveform data at ``path``.

        :param path: Destination path on the instrument filesystem.
        """
        self.write(f":SAVE:WAV {path}")

    def load_setup(self, path: str) -> None:
        """Load an oscilloscope setup from ``path``.

        :param path: Source path on the instrument filesystem.
        """
        self.write(f":LOAD:SET {path}")

    def download_setup(self) -> bytes:
        """Download the current setup data with its IEEE block framing removed."""
        self.write(":SYST:SET?")
        return self._read_ieee_block("Setup response")

    def upload_setup(self, setup_data: bytes) -> None:
        """Upload setup data previously returned by :meth:`download_setup`.

        :param setup_data: Raw setup payload without IEEE block framing.
        """
        if not isinstance(setup_data, bytes):
            raise TypeError("Setup data must be bytes.")
        length = str(len(setup_data))
        if len(length) > 9:
            raise ValueError("Setup data exceeds the maximum IEEE block length.")
        block_header = f"#{len(length)}{length}".encode()
        self.write_bytes(b":SYST:SET " + block_header + setup_data)

    def self_test(self) -> int:
        """Run the instrument self-test and return its integer result."""
        return int(self.ask("*TST?"))

    def option_status(self, option: str) -> bool:
        """Return whether an oscilloscope option is installed.

        :param option: Documented MSO5000 option identifier.
        """
        option = strict_discrete_set(option, OPTION_TYPES)
        return bool(int(self.ask(f":SYST:OPT:STAT? {option}")))

    def press_key(self, key: str) -> None:
        """Emulate pressing a documented front-panel key.

        :param key: Documented front-panel key name.
        """
        key = strict_discrete_set(key, SYSTEM_KEYS)
        self.write(f":SYST:KEY:PRES {key}")

    def increase_key(self, key: str, steps: int = 1) -> None:
        """Rotate a documented front-panel knob clockwise.

        :param key: Documented front-panel knob name.
        :param steps: Integer number of rotation steps; omitted on the wire when equal to 1.
        """
        key = strict_discrete_set(key, SYSTEM_KNOBS)
        if not isinstance(steps, int):
            raise TypeError("Knob steps must be an integer.")
        suffix = "" if steps == 1 else f",{steps}"
        self.write(f":SYST:KEY:INCR {key}{suffix}")

    def decrease_key(self, key: str, steps: int = 1) -> None:
        """Rotate a documented front-panel knob counterclockwise.

        :param key: Documented front-panel knob name.
        :param steps: Integer number of rotation steps; omitted on the wire when equal to 1.
        """
        key = strict_discrete_set(key, SYSTEM_KNOBS)
        if not isinstance(steps, int):
            raise TypeError("Knob steps must be an integer.")
        suffix = "" if steps == 1 else f",{steps}"
        self.write(f":SYST:KEY:DECR {key}{suffix}")

    def autoscale(self) -> None:
        """Automatically configure the vertical scale, timebase, and trigger mode."""
        self.write(":AUT")

    def measure(self, item: str, channel: int = 1) -> float:
        """Return an automatic measurement for analog channel 1 to 4.

        This convenience method delegates to :attr:`measurements`. Use the child
        interface directly for math, digital, or dual-source measurements.

        :param item: Documented automatic-measurement item.
        :param channel: Analog channel number from 1 to 4.
        """
        channel = strict_range(channel, [1, 4])
        return self.measurements.item(item, f"CHAN{channel}")

    def clear_measurements(self) -> None:
        """Clear all displayed automatic measurement items."""
        self.measurements.clear()

    def clear_waveforms(self) -> None:
        """Clear all waveforms from the display."""
        self.write(":CLE")
