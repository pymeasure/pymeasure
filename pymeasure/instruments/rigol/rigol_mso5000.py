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

TRIGGER_SOURCES = [
    *[f"D{number}" for number in range(16)],
    *[f"CHAN{number}" for number in range(1, 5)],
]

CSV_CHANNELS = ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "POD1", "POD2"]

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

    statistic_display = Channel.control(
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
        """Clear a displayed measurement item, from ``"ITEM1"`` to ``"ITEM10"``, or all."""
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
        """Enable a measurement item for one or two optional sources."""
        self.write(f":MEAS:ITEM {self._item_arguments(item, source_a, source_b)}")

    def item(self, item: str, source_a: str | None = None, source_b: str | None = None) -> float:
        """Return the current value of a measurement item for optional sources."""
        arguments = self._item_arguments(item, source_a, source_b)
        return self._parse_result(self.ask(f":MEAS:ITEM? {arguments}"))

    def enable_statistic_item(
        self, item: str, source_a: str | None = None, source_b: str | None = None
    ) -> None:
        """Enable statistics for a measurement item and optional sources."""
        self.write(f":MEAS:STAT:ITEM {self._item_arguments(item, source_a, source_b)}")

    def statistic_item(
        self,
        statistic_type: str,
        item: str,
        source_a: str | None = None,
        source_b: str | None = None,
    ) -> float:
        """Return one statistic for a measurement item and optional sources."""
        statistic_type = _validate_scpi_keyword(
            statistic_type, MEASUREMENT_STATISTIC_TYPES, "Statistic type"
        )
        arguments = self._item_arguments(item, source_a, source_b)
        return self._parse_result(self.ask(f":MEAS:STAT:ITEM? {statistic_type},{arguments}"))


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
    timebase, trigger, waveform-transfer, system, and storage controls.

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
        """Set the Pattern-trigger level for an analog or digital channel."""
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        self.write(f":TRIG:PATT:LEV {source},{level:g}")

    def get_pattern_trigger_level(self, source: str) -> float:
        """Return the Pattern-trigger level for an analog or digital channel."""
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        return float(self.ask(f":TRIG:PATT:LEV? {source}"))

    def set_duration_trigger_level(self, source: str, level: float) -> None:
        """Set the Duration-trigger level for an analog or digital channel."""
        source = strict_discrete_set(source, TRIGGER_SOURCES)
        self.write(f":TRIG:DUR:LEV {source},{level:g}")

    def get_duration_trigger_level(self, source: str) -> float:
        """Return the Duration-trigger level for an analog or digital channel."""
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
        """Save the current instrument state to a register from 0 to 49."""
        register = strict_range(register, [0, 49])
        self.write(f"*SAV {register}")

    def recall_state(self) -> None:
        """Recall the instrument state selected by the instrument."""
        self.write("*RCL")

    def save_reference_waveform(self, reference: int) -> None:
        """Save a reference waveform to an internal reference slot from 1 to 10."""
        reference = strict_range(reference, [1, 10])
        self.write(f":REF:SAVE {reference}")

    def save_csv(self, path: str) -> None:
        """Save the displayed waveform data as a CSV file at ``path``."""
        self.write(f":SAVE:CSV {path}")

    def set_csv_channel_enabled(self, channel: str, enabled: bool) -> None:
        """Set whether ``channel`` is included in saved CSV files."""
        channel = strict_discrete_set(channel, CSV_CHANNELS)
        enabled = strict_discrete_set(enabled, [True, False])
        self.write(f":SAVE:CSV:CHAN {channel},{int(enabled)}")

    def get_csv_channel_enabled(self, channel: str) -> bool:
        """Return whether ``channel`` is included in saved CSV files."""
        channel = strict_discrete_set(channel, CSV_CHANNELS)
        return bool(int(self.ask(f":SAVE:CSV:CHAN? {channel}")))

    def save_image(self, path: str) -> None:
        """Save the current display image at ``path``."""
        self.write(f":SAVE:IMAG {path}")

    def save_setup(self, path: str) -> None:
        """Save the current oscilloscope setup at ``path``."""
        self.write(f":SAVE:SET {path}")

    def save_waveform(self, path: str) -> None:
        """Save waveform data at ``path``."""
        self.write(f":SAVE:WAV {path}")

    def load_setup(self, path: str) -> None:
        """Load an oscilloscope setup from ``path``."""
        self.write(f":LOAD:SET {path}")

    def download_setup(self) -> bytes:
        """Download the current setup data with its IEEE block framing removed."""
        self.write(":SYST:SET?")
        return self._read_ieee_block("Setup response")

    def upload_setup(self, setup_data: bytes) -> None:
        """Upload setup data previously returned by :meth:`download_setup`."""
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
        """Return whether an oscilloscope option is installed."""
        option = strict_discrete_set(option, OPTION_TYPES)
        return bool(int(self.ask(f":SYST:OPT:STAT? {option}")))

    def press_key(self, key: str) -> None:
        """Emulate pressing a documented front-panel key."""
        key = strict_discrete_set(key, SYSTEM_KEYS)
        self.write(f":SYST:KEY:PRES {key}")

    def increase_key(self, key: str, steps: int = 1) -> None:
        """Rotate a documented front-panel knob clockwise."""
        key = strict_discrete_set(key, SYSTEM_KNOBS)
        if not isinstance(steps, int):
            raise TypeError("Knob steps must be an integer.")
        suffix = "" if steps == 1 else f",{steps}"
        self.write(f":SYST:KEY:INCR {key}{suffix}")

    def decrease_key(self, key: str, steps: int = 1) -> None:
        """Rotate a documented front-panel knob counterclockwise."""
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
        """
        channel = strict_range(channel, [1, 4])
        return self.measurements.item(item, f"CHAN{channel}")

    def clear_measurements(self) -> None:
        """Clear all displayed automatic measurement items."""
        self.measurements.clear()

    def clear_waveforms(self) -> None:
        """Clear all waveforms from the display."""
        self.write(":CLE")
