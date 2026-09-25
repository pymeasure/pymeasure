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

import logging
from csv import reader
from io import StringIO
from typing import Optional

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


SOURCE_FUNCTIONS = {
    "sine": "SIN",
    "random": "RAND",
    "burst_random": "BRAN",
    "periodic_chirp": "PCH",
    "burst_chirp": "BCH",
    "pink": "PINK",
    "user": "USER",
    "capture": "CAPT",
}

SOURCE_USER_REGISTERS = {
    1: "D1",
    2: "D2",
    3: "D3",
    4: "D4",
    5: "D5",
    6: "D6",
    7: "D7",
    8: "D8",
}

SOURCE_REFERENCE_CHANNELS = {
    1: "INP1",
    2: "INP2",
    3: "INP3",
    4: "INP4",
}

INSTRUMENT_MODES = {
    "fft": "FFT",
    "correlation": "CORR",
    "histogram": "HIST",
    "octave": "OCT",
    "order": "ORD",
    "swept_sine": "SINE",
}

TRACE_FEEDS = {
    "data_register_1": "D1",
    "data_register_2": "D2",
    "data_register_3": "D3",
    "data_register_4": "D4",
    "power_spectrum_ch1": "XFR:POW 1",
    "power_spectrum_ch2": "XFR:POW 2",
    "linear_spectrum_ch1": "XFR:POW:LIN 1",
    "linear_spectrum_ch2": "XFR:POW:LIN 2",
    "frequency_response_2_1": "XFR:POW:RAT 2,1",
    "coherence_1_2": "XFR:POW:COH 1,2",
    "cross_spectrum_1_2": "XFR:POW:CROS 1,2",
    "time_ch1": "XTIM:VOLT 1",
    "time_ch2": "XTIM:VOLT 2",
    "windowed_time_ch1": "XTIM:VOLT:WIND 1",
    "windowed_time_ch2": "XTIM:VOLT:WIND 2",
}

TRACE_ACTIVE_VALUES = {
    "a": "A",
    "b": "B",
    "c": "C",
    "d": "D",
    "ab": "AB",
    "cd": "CD",
    "abcd": "ABCD",
}

TRACE_DISPLAY_FORMATS = {
    "linear_magnitude": "MLIN",
    "log_magnitude": "MLOG",
    "phase": "PHAS",
    "real": "REAL",
    "imaginary": "IMAG",
    "nyquist": "NYQ",
    "unwrapped_phase": "UPH",
    "group_delay": "GDEL",
    "polar": "POL",
}

AVERAGE_TYPES = {
    "maximum": "MAX",
    "rms": "RMS",
    "time": "TIME",
    "vector": "VECT",
    "equal_confidence": "ECON",
}

AVERAGE_TCONTROLS = {
    "freeze": "FREE",
    "repeat": "REP",
    "exponential": "EXP",
}

AVERAGE_HOLD_VALUES = {
    "off": "OFF",
    "maximum": "MAX",
    "minimum": "MIN",
}

AVERAGE_PREVIEW_VALUES = {
    "off": "OFF",
    "manual": "MAN",
    "timed": "TIM",
}

REFERENCE_CHANNEL_VALUES = {
    "single": "SING",
    "pair": "PAIR",
}

WINDOW_TYPES = {
    "hanning": "HANN",
    "flattop": "FLAT",
    "uniform": "UNIF",
    "force": "FORC",
    "exponential": "EXP",
    "lag": "LAG",
    "llag": "LLAG",
}

TRIGGER_SOURCES = {
    "immediate": "IMM",
    "external": "EXT",
    "internal1": "INT1",
    "internal2": "INT2",
    "internal3": "INT3",
    "internal4": "INT4",
    "output": "OUTP",
    "bus": "BUS",
}

TRIGGER_SLOPES = {
    "positive": "POS",
    "negative": "NEG",
}

TACHOMETER_SLOPES = {
    "positive": "POS",
    "negative": "NEG",
}

ARM_SOURCES = {
    "immediate": "IMM",
    "manual": "MAN",
    "rpm": "RPM",
    "timer": "TIM",
}

ARM_RPM_MODES = {
    "off": "OFF",
    "up": "UP",
    "down": "DOWN",
}

EXTERNAL_TRIGGER_RANGES = {
    "high": "HIGH",
    "low": "LOW",
}

TACHOMETER_TRIGGER_RANGES = {
    "high": "HIGH",
    "low": "LOW",
}

DISPLAY_FORMATS = {
    "single": "SING",
    "upper_lower": "ULOW",
    "feedback": "FBAC",
    "subl": "SUBL",
    "upper_lower_feedback": "ULFB",
    "quad": "QUAD",
}

DISPLAY_VIEWS = {
    "trace": "TRAC",
    "measurement_state": "MSTAT",
    "mass_memory": "MMEM",
    "state_table": "STAB",
    "calc_table": "CTAB",
    "frequency_table": "FTAB",
    "time_table": "TTAB",
    "memory": "MEM",
    "option": "OPT",
    "capture": "CAPT",
    "instrument_state": "IST",
    "message": "MESS",
}

DISPLAY_PROGRAM_MODES = {
    "off": "OFF",
    "full": "FULL",
    "upper": "UPP",
    "lower": "LOW",
}

TRACE_X_AUTOSCALE = {
    "off": "OFF",
    "once": "ONCE",
}

TRACE_Y_AUTOSCALE = {
    "off": "OFF",
    "on": "ON",
    "once": "ONCE",
}

DISPLAY_AXIS_SPACING_VALUES = {
    "linear": "LIN",
    "logarithmic": "LOG",
}

DISPLAY_TRACE_Y_REFERENCE_VALUES = {
    "top": "TOP",
    "center": "CENT",
    "bottom": "BOTT",
    "range": "RANG",
}

TRACE_AMPLITUDE_UNITS = ("PEAK", "PP", "RMS")

TRACE_ANGLE_UNITS = {
    "degree": "DEG",
    "radian": "RAD",
}

TRACE_X_UNITS = {
    "hertz": "HZ",
    "cycles_per_minute": "CPM",
    "orders": "ORD",
    "user": "USER",
}

DB_REFERENCE_UNITS = {
    "dbv": "DBV",
    "dbm": "DBM",
    "dbspl": "DBSPL",
    "dbuser": "DBUSER",
    "user": "USER",
}

TRACE_MECHANICAL_UNITS = (
    "G",
    "M/S2",
    "M/S",
    "M",
    "INCH/S2",
    "INCH/S",
    "INCH",
    "MILS",
)

TRACE_VOLTAGE_UNITS = (
    "V",
    "V2",
    "V/RTHZ",
    "V2/HZ",
    "V2S/HZ",
)

MARKER_FUNCTION_VALUES = {
    "off": "OFF",
    "harmonic_power": "HPOW",
    "thd": "THD",
    "band_power": "BPOW",
    "band_rms": "BRMS",
    "spectrum_power": "SPOW",
    "overshoot": "OVER",
    "rise_time": "RTIM",
    "settling_time": "STIM",
    "delay_time": "DTIM",
    "steady_state_level": "SSL",
    "gain_margin": "GMAR",
    "phase_margin": "PMAR",
    "gain_crossover": "GCR",
    "phase_crossover": "PCR",
    "frequency": "FREQ",
    "damping": "DAMP",
    "s_info": "SINF",
    "weight": "WEIG",
    "total_power": "TPOW",
    "weighted_power": "WPOW",
}

MARKER_MODE_VALUES = {
    "absolute": "ABS",
    "relative": "REL",
}

MATH_SELECTED_FUNCTION_VALUES = ("F1", "F2", "F3", "F4", "F5")
SYNTHESIS_SPACING_VALUES = {
    "linear": "LIN",
    "logarithmic": "LOG",
}
SYNTHESIS_TABLE_TYPE_VALUES = {
    "pole_zero": "PZER",
    "pole_fraction": "PFR",
    "polynomial": "POLY",
}

BOOL_VALUES = {True: 1, False: 0}
STATUS_MASK_VALUES = [0, 32767]
DATA_RANGE_VALUES = [1.0e-20, 1.0e20]
LIMIT_VALUE_RANGE = [-9.9e37, 9.9e37]
SENSE_FEED_VALUES = {
    "input": "INP",
    "time_capture": "TCAP",
}
FREQUENCY_RESOLUTION_OCTAVE_VALUES = {
    "third": "THIR",
    "full": "FULL",
    "twelfth": "TWEL",
}
FREQUENCY_SPAN_LINK_VALUES = {
    "start": "STAR",
    "center": "CENT",
}
SWEEP_DIRECTION_VALUES = {
    "up": "UP",
    "down": "DOWN",
}
SWEEP_MODE_VALUES = {
    "auto": "AUTO",
    "manual": "MAN",
}
SWEEP_SPACING_VALUES = {
    "linear": "LIN",
    "logarithmic": "LOG",
}
AUTORANGE_DIRECTION_VALUES = {
    "up": "UP",
    "either": "EITH",
}
INPUT_RANGE_TRANSDUCER_LABELS = (
    "PA",
    "G",
    "M/S2",
    "M/S",
    "M",
    "KG",
    "N",
    "DYN",
    "INCH/S2",
    "INCH/S",
    "INCH",
    "MIL",
    "LB",
    "USER",
)
SERIAL_BAUD_RATES = (300, 1200, 2400, 4800, 9600)
SERIAL_BITS = (5, 6, 7, 8)
SERIAL_STOP_BITS = (1, 2)
SERIAL_RECEIVE_PACE_VALUES = {
    "none": "NONE",
    "xon": "XON",
}
SERIAL_PARITY_VALUES = {
    "none": "NONE",
    "even": "EVEN",
    "odd": "ODD",
}
SERIAL_TRANSMIT_PACE_VALUES = {
    "none": "NONE",
    "xon": "XON",
    "dsr": "DSR",
}
DATA_FORMAT_VALUES = {
    "ascii": "ASC",
    "real": "REAL",
}
FAN_STATE_VALUES = {
    "off": "OFF",
    "full": "FULL",
    "auto": "AUTO",
}
SYSTEM_DATE_VALUES = ([0, 9999], [1, 12], [1, 31])
SYSTEM_TIME_VALUES = ([0, 23], [0, 59], [0, 60])
HARDCOPY_DEVICE_LANGUAGE_VALUES = ("HPGL", "PCL", "PHPGL")
HARDCOPY_PAGE_POINT_VALUES = ([-32767, 32767], [-32767, 32767])
HARDCOPY_DESTINATION_VALUES = ("MMEM", "SYST:COMM:GPIB:RDEV", "SYST:COMM:CENT", "SYST:COMM:SER")
HARDCOPY_SOURCE_VALUES = ("ALL", "TRAC", "MARK", "REF", "GRID")
HARDCOPY_LINE_TYPE_STYLE_RANGE = [0, 12]
HARDCOPY_LABEL_COLOR_RANGE = [0, 16]
HARDCOPY_TIMESTAMP_FORMAT_VALUES = ("FORM1", "FORM2", "FORM3", "FORM4", "FORM5")
MEMORY_CATALOG_ITEM_VALUES = {
    "time_capture": "TCAPture",
    "waterfall": "WATerfall",
    "waterfall_register": "WREGister",
    "program": "PROGram",
    "ram_disk": "RDISk",
    "limits": "LIMits",
}
MASS_MEMORY_STORE_PROGRAM_FORMAT_VALUES = {
    "ascii": "ASC",
    "binary": "BIN",
}
MASS_MEMORY_STORE_TRACE_FORMAT_VALUES = ("SDF", "ASCII")
PROGRAM_STATE_VALUES = {
    "stop": "STOP",
    "pause": "PAUSe",
    "run": "RUN",
    "continue": "CONTinue",
}


def _parse_ascii_floats(reply: str) -> list[float]:
    """Parse a comma-separated ASCII response into a list of floats."""
    if reply.strip() == "":
        return []
    values = []
    for token in reply.split(","):
        stripped = token.strip()
        if stripped == "":
            continue
        values.append(float(stripped))
    return values


def _parse_ascii_ints(reply: str) -> list[int]:
    """Parse a comma-separated ASCII response into a list of ints."""
    if reply.strip() == "":
        return []
    values = []
    for token in reply.split(","):
        stripped = token.strip()
        if stripped == "":
            continue
        values.append(int(stripped))
    return values


def _parse_csv_strings(reply: str) -> list[str]:
    """Parse a CSV response into a list of unquoted strings."""
    if reply.strip() == "":
        return []
    row = next(reader(StringIO(reply), skipinitialspace=True))
    return [_strip_quotes(item.strip()) for item in row]


def _strip_quotes(reply: str) -> str:
    """Strip matching single or double quotes from string boundaries."""
    value = reply.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _quote_string(value: str) -> str:
    """Quote a string for SCPI arguments unless already quoted."""
    if not isinstance(value, str):
        raise TypeError("SCPI string arguments must be of type str.")
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return stripped
    escaped = value.replace('"', '""')
    return f'"{escaped}"'


def _require_confirmation(action: str, confirmed: bool):
    """Require explicit confirmation for risky actions."""
    if confirmed is not True:
        raise ValueError(
            f"Action '{action}' requires explicit confirmation. "
            "Pass confirmed=True to execute."
        )


def _trace_selector(trace):
    """Return a valid TRACe selector token."""
    if isinstance(trace, int):
        if trace not in (1, 2, 3, 4):
            raise ValueError("Trace index must be in the range 1..4.")
        return f"TRACe{trace}"
    return str(trace)


def _tcap_selector(capture_channel):
    """Return a valid TCAP selector token."""
    if isinstance(capture_channel, int):
        if capture_channel not in (1, 2, 3, 4):
            raise ValueError("Capture channel index must be in the range 1..4.")
        return f"TCAP{capture_channel}"

    token = str(capture_channel).strip().upper()
    if token in {"TCAP1", "TCAP2", "TCAP3", "TCAP4"}:
        return token
    raise ValueError("Capture channel must be 1..4 or one of TCAP1..TCAP4.")


def _data_register_selector(register):
    """Return a valid data-register selector token."""
    if isinstance(register, int):
        index = int(strict_range(int(register), [1, 8]))
        return SOURCE_USER_REGISTERS[index]

    token = _strip_quotes(str(register)).strip().upper()
    if token in SOURCE_USER_REGISTERS.values():
        return token
    raise ValueError("Data register must be 1..8 or one of D1..D8.")


def _math_register_selector(register):
    """Return a valid math register index."""
    return int(strict_range(int(register), [1, 5]))


def _strict_nonzero_range(value, values):
    """Validate an inclusive range while excluding zero."""
    validated = strict_range(value, values)
    if float(validated) == 0.0:
        raise ValueError("Value must not be 0.")
    return validated


def _normalize_on_off_once(value: str) -> str:
    """Normalize ON/OFF/ONCE tokens returned as symbolic or numeric values."""
    token = _strip_quotes(str(value)).strip().upper()
    return {"0": "OFF", "1": "ON"}.get(token, token)


def _normalize_data_format_token(reply: str) -> str:
    """Normalize FORMat:DATA reply to the first mode token."""
    token = _strip_quotes(str(reply)).strip()
    if "," in token:
        token = token.split(",", 1)[0]
    return token.strip().upper()


def _trace_data_register_selector(register):
    """Return a valid TRACe data-register selector token."""
    if isinstance(register, int):
        index = int(strict_range(int(register), [1, 8]))
        return f"D{index}"

    token = _strip_quotes(str(register)).strip().upper()
    if token in {f"D{i}" for i in range(1, 9)}:
        return token
    raise ValueError("Trace register must be 1..8 or one of D1..D8.")


def _trace_waterfall_register_selector(register):
    """Return a valid TRACe waterfall-register selector token."""
    if isinstance(register, int):
        index = int(strict_range(int(register), [1, 8]))
        return f"W{index}"

    token = _strip_quotes(str(register)).strip().upper()
    if token in {f"W{i}" for i in range(1, 9)}:
        return token
    raise ValueError("Waterfall register must be 1..8 or one of W1..W8.")


def _validate_int_triplet(value, values):
    """Validate a triplet of integers against three inclusive [min, max] ranges."""
    if isinstance(value, str):
        tokens = _parse_ascii_ints(value)
    elif isinstance(value, (list, tuple)):
        tokens = [int(item) for item in value]
    else:
        raise ValueError("Value must be a 3-item tuple/list or CSV string.")

    if len(tokens) != 3:
        raise ValueError("Value must contain exactly 3 integers.")

    validated = []
    for item, limits in zip(tokens, values):
        validated.append(int(strict_range(item, limits)))
    return tuple(validated)


def _validate_int_pair(value, values):
    """Validate a pair of integers against two inclusive [min, max] ranges."""
    if isinstance(value, str):
        tokens = _parse_ascii_ints(value)
    elif isinstance(value, (list, tuple)):
        tokens = [int(item) for item in value]
    else:
        raise ValueError("Value must be a 2-item tuple/list or CSV string.")

    if len(tokens) != 2:
        raise ValueError("Value must contain exactly 2 integers.")

    validated = []
    for item, limits in zip(tokens, values):
        validated.append(int(strict_range(item, limits)))
    return tuple(validated)


def _normalize_hardcopy_destination(value: str) -> str:
    """Normalize hardcopy destination tokens to canonical short-form strings."""
    token = _strip_quotes(str(value)).strip().upper().replace(" ", "")
    if token in {"MMEM", "MMEMORY"}:
        return "MMEM"
    if "GPIB" in token and "RDEV" in token:
        return "SYST:COMM:GPIB:RDEV"
    if "CENT" in token:
        return "SYST:COMM:CENT"
    if "SER" in token:
        return "SYST:COMM:SER"
    raise ValueError(f"Invalid hardcopy destination '{value}'.")


def _validate_hardcopy_destination(value, values):
    """Validate hardcopy destination token."""
    del values
    return _normalize_hardcopy_destination(value)


def _normalize_hardcopy_timestamp_format(value: str) -> str:
    """Normalize hardcopy timestamp format tokens to FORM1..FORM5."""
    token = _strip_quotes(str(value)).strip().upper()
    if token.startswith("FORMAT"):
        suffix = token[6:]
    elif token.startswith("FORM"):
        suffix = token[4:]
    else:
        raise ValueError(f"Invalid hardcopy timestamp format '{value}'.")

    if suffix not in {"1", "2", "3", "4", "5"}:
        raise ValueError(f"Invalid hardcopy timestamp format '{value}'.")
    return f"FORM{suffix}"


def _validate_hardcopy_timestamp_format(value, values):
    """Validate hardcopy timestamp format token."""
    del values
    return _normalize_hardcopy_timestamp_format(value)


def _normalize_hardcopy_source(value: str) -> str:
    """Normalize hardcopy source token to canonical short-form strings."""
    token = _strip_quotes(str(value)).strip().upper()
    if token.startswith("ALL"):
        return "ALL"
    if token.startswith("TRAC"):
        return "TRAC"
    if token.startswith("MARK"):
        return "MARK"
    if token.startswith("REF"):
        return "REF"
    if token.startswith("GRID"):
        return "GRID"
    raise ValueError(f"Invalid hardcopy source '{value}'.")


def _validate_hardcopy_source(value, values):
    """Validate hardcopy source token."""
    del values
    return _normalize_hardcopy_source(value)


def _normalize_hardcopy_line_type(value: str) -> str:
    """Normalize hardcopy line-type token to SOL, DASH, DOTT, or STYL<n>."""
    token = _strip_quotes(str(value)).strip().upper()
    if token in {"SOL", "SOLID"}:
        return "SOL"
    if token in {"DASH", "DASHED"}:
        return "DASH"
    if token in {"DOTT", "DOTTED", "DOT"}:
        return "DOTT"

    if token.startswith("STYLE"):
        suffix = token[5:]
    elif token.startswith("STYL"):
        suffix = token[4:]
    else:
        raise ValueError(f"Invalid hardcopy line type '{value}'.")

    try:
        style_index = int(suffix)
    except ValueError as exc:
        raise ValueError(f"Invalid hardcopy line type '{value}'.") from exc

    strict_range(style_index, HARDCOPY_LINE_TYPE_STYLE_RANGE)
    if style_index not in {0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}:
        raise ValueError("Hardcopy style line type must be STYL0 or STYL3..STYL12.")
    return f"STYL{style_index}"


def _validate_hardcopy_line_type(value, values):
    """Validate hardcopy line-type token."""
    del values
    return _normalize_hardcopy_line_type(value)


def _normalize_memory_catalog_item(value: str) -> str:
    """Normalize memory catalog/delete item selector token."""
    token = _strip_quotes(str(value)).strip().upper()
    if token.startswith("TCAP"):
        return "TCAPture"
    if token.startswith("WATERFALL") or token == "WAT":
        return "WATerfall"
    if token.startswith("WREG"):
        return "WREGister"
    if token.startswith("PROG"):
        return "PROGram"
    if token.startswith("RDIS"):
        return "RDISk"
    if token.startswith("LIM"):
        return "LIMits"
    raise ValueError(f"Invalid memory item selector '{value}'.")


def _validate_memory_catalog_item(value, values):
    """Validate memory catalog/delete item selector token."""
    del values
    return _normalize_memory_catalog_item(value)


def _normalize_mass_memory_disk(value: str) -> str:
    """Normalize mass-memory disk selector token."""
    token = _strip_quotes(str(value)).strip().upper()
    if token in {"RAM", "RAM:"}:
        return "RAM:"
    if token in {"NVRAM", "NVRAM:"}:
        return "NVRAM:"
    if token in {"INT", "INT:"}:
        return "INT:"
    if token in {"EXT", "EXT:"}:
        return "EXT:"
    if token.startswith("EXT,"):
        return token if token.endswith(":") else token + ":"
    raise ValueError(f"Invalid mass-memory disk selector '{value}'.")


def _normalize_mass_memory_trace_selector(trace) -> str:
    """Normalize trace selector for MMEMory trace-specific operations."""
    index = int(strict_range(int(trace), [1, 4]))
    return f"TRACe{index}"


def _normalize_mass_memory_program_format(value: str) -> str:
    """Normalize MMEMory:STORe:PROGram:FORMat token."""
    token = _strip_quotes(str(value)).strip().upper()
    if token.startswith("ASC"):
        return "ASC"
    if token.startswith("BIN"):
        return "BIN"
    raise ValueError(f"Invalid mass-memory program format '{value}'.")


def _normalize_program_name(value: str) -> str:
    """Normalize Instrument BASIC program-buffer selector token."""
    token = _strip_quotes(str(value)).strip().upper()
    if token in {"1", "PROG1", "PROGRAM1"}:
        return "PROGram1"
    if token in {"2", "PROG2", "PROGRAM2"}:
        return "PROGram2"
    if token in {"3", "PROG3", "PROGRAM3"}:
        return "PROGram3"
    if token in {"4", "PROG4", "PROGRAM4"}:
        return "PROGram4"
    if token in {"5", "PROG5", "PROGRAM5"}:
        return "PROGram5"
    raise ValueError(f"Invalid program selector '{value}'.")


def _normalize_program_state(value: str) -> str:
    """Normalize Instrument BASIC program state token."""
    token = _strip_quotes(str(value)).strip().upper()
    if token.startswith("STOP"):
        return "STOP"
    if token.startswith("PAUS"):
        return "PAUSe"
    if token.startswith("RUN"):
        return "RUN"
    if token.startswith("CONT"):
        return "CONTinue"
    raise ValueError(f"Invalid program state '{value}'.")


def _normalize_program_variable_name(index, string_variable=False) -> str:
    """Normalize Instrument BASIC variable identifier for SCPI program-variable commands."""
    token = _strip_quotes(str(index)).strip()
    if token == "":
        raise ValueError("Program variable identifier must not be empty.")

    if string_variable:
        if token.endswith("$"):
            return token
        if token.isdigit():
            return f"S{token}$"
        return token + "$"

    return token


def _parse_ascii_or_definite_block_text(reply) -> str:
    """Parse ASCII text or definite-block text reply into a Python string."""
    if isinstance(reply, (bytes, bytearray)):
        raw = bytes(reply)
    else:
        raw = str(reply).encode("latin1")

    if raw == b"":
        return ""

    if raw.startswith(b"#"):
        payload = _parse_definite_block(raw)
        return payload.decode("latin1")

    return raw.decode("latin1").strip()


def _encode_program_block(text, raw=False) -> bytes:
    """Encode Instrument BASIC program text for PROGram:*:DEFine commands."""
    payload = _coerce_bytes(text)
    if raw:
        return payload
    return _encode_definite_block(payload)


def _encode_definite_block(payload: bytes) -> bytes:
    """Encode payload bytes as an IEEE definite-length SCPI block."""
    length = len(payload)
    length_ascii = str(length).encode("ascii")
    return b"#" + str(len(length_ascii)).encode("ascii") + length_ascii + payload


def _parse_definite_block(block: bytes) -> bytes:
    """Parse an IEEE definite-length SCPI block and return the payload bytes."""
    if not block:
        raise ValueError("Definite block is empty.")
    if block[0:1] != b"#":
        raise ValueError("Definite block must start with '#'.")

    header_len_char = block[1:2]
    if not header_len_char or not header_len_char.isdigit():
        raise ValueError("Definite block header is malformed.")

    header_len = int(header_len_char.decode("ascii"))
    if header_len == 0:
        return block[2:]

    header_start = 2
    header_end = header_start + header_len
    if len(block) < header_end:
        raise ValueError("Definite block length header is incomplete.")

    length_ascii = block[header_start:header_end]
    if not length_ascii.isdigit():
        raise ValueError("Definite block byte count is malformed.")

    payload_length = int(length_ascii.decode("ascii"))
    payload_end = header_end + payload_length
    if len(block) < payload_end:
        raise ValueError("Definite block payload is incomplete.")

    return block[header_end:payload_end]


def _coerce_bytes(value) -> bytes:
    """Convert supported system-state payload input to bytes."""
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("latin1")
    raise TypeError("System state data must be bytes, bytearray, or str.")


def _parse_ascii_or_definite_block_floats(reply) -> list[float]:
    """Parse ASCII CSV float data or an ASCII definite block with CSV float payload."""
    if isinstance(reply, (bytes, bytearray)):
        raw = bytes(reply)
    else:
        raw = str(reply).strip().encode("latin1")

    if raw == b"":
        return []

    if raw.startswith(b"#"):
        payload = _parse_definite_block(raw)
        try:
            decoded = payload.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "Binary definite blocks are not supported by this ASCII parser."
            ) from exc
        return _parse_ascii_floats(decoded)

    return _parse_ascii_floats(raw.decode("ascii"))


def _parse_limit_segment_data(reply) -> list[tuple[float, float, float, float]]:
    """Parse limit-segment data into a list of 4-value (x0, y0, x1, y1) tuples."""
    values = _parse_ascii_or_definite_block_floats(reply)
    if len(values) % 4 != 0:
        raise ValueError("Limit segment data must contain 4 values per segment.")
    segments = []
    for i in range(0, len(values), 4):
        segments.append((values[i], values[i + 1], values[i + 2], values[i + 3]))
    return segments


def _format_limit_segment_data(value) -> str:
    """Format limit-segment input as ASCII CSV for SCPI segment commands."""
    if isinstance(value, str):
        return value

    if not isinstance(value, (list, tuple)):
        raise ValueError("Limit segment data must be a sequence or CSV string.")

    flat_values = []
    if value and isinstance(value[0], (list, tuple)):
        for segment in value:
            if not isinstance(segment, (list, tuple)) or len(segment) != 4:
                raise ValueError("Each limit segment must contain 4 values.")
            for item in segment:
                flat_values.append(float(strict_range(float(item), LIMIT_VALUE_RANGE)))
    else:
        for item in value:
            flat_values.append(float(strict_range(float(item), LIMIT_VALUE_RANGE)))
        if len(flat_values) % 4 != 0:
            raise ValueError("Flat limit segment data must contain a multiple of 4 values.")

    return ",".join(f"{item:g}" for item in flat_values)


class Keysight35670AInputChannel(Channel):
    """Represent an input channel of the Keysight 35670A."""

    _state = Channel.control(
        "INPut{ch}:STATe?",
        "INPut{ch}:STATe %d",
        """Control whether the input channel is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    @property
    def state(self):
        """Control whether the input channel is enabled."""
        return type(self)._state.fget(self)

    @state.setter
    def state(self, value):
        enabled = bool(strict_discrete_set(value, BOOL_VALUES))
        if self.id == 1 and not enabled:
            raise ValueError("Input channel 1 cannot be disabled.")
        type(self)._state.fset(self, enabled)

    enabled = state

    bias_enabled = Channel.control(
        "INPut{ch}:BIAS:STATe?",
        "INPut{ch}:BIAS:STATe %d",
        """Control whether the ICP bias supply is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    coupling = Channel.control(
        "INPut{ch}:COUPling?",
        "INPut{ch}:COUPling %s",
        """Control the input coupling.""",
        values=("AC", "DC"),
        validator=strict_discrete_set,
    )

    a_weighting_enabled = Channel.control(
        "INPut{ch}:FILTer:AWEighting:STATe?",
        "INPut{ch}:FILTer:AWEighting:STATe %d",
        """Control whether the A-weighting filter is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    anti_alias_filter_enabled = Channel.control(
        "INPut{ch}:FILTer:LPASs:STATe?",
        "INPut{ch}:FILTer:LPASs:STATe %d",
        """Control whether the anti-alias low-pass filter is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    shield = Channel.control(
        "INPut{ch}:LOW?",
        "INPut{ch}:LOW %s",
        """Control whether the input shield is grounded or floating.""",
        values={"ground": "GRO", "float": "FLO"},
        map_values=True,
        validator=strict_discrete_set,
    )

    reference_direction = Channel.control(
        "INPut{ch}:REFerence:DIRection?",
        "INPut{ch}:REFerence:DIRection %d",
        """Control the transducer reference direction code.""",
        values=[0, 32767],
        validator=strict_range,
        cast=int,
    )

    reference_point = Channel.control(
        "INPut{ch}:REFerence:POINt?",
        "INPut{ch}:REFerence:POINt %d",
        """Control the transducer reference point number.""",
        values=[0, 32767],
        validator=strict_range,
        cast=int,
    )

    autorange_enabled = Channel.control(
        "SENSe:VOLTage{ch}:RANGe:AUTO?",
        "SENSe:VOLTage{ch}:RANGe:AUTO %d",
        """Control whether input autoranging is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    autorange_direction = Channel.control(
        "SENSe:VOLTage{ch}:RANGe:AUTO:DIRection?",
        "SENSe:VOLTage{ch}:RANGe:AUTO:DIRection %s",
        """Control whether autoranging moves upward only or in both directions.""",
        values=AUTORANGE_DIRECTION_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    range_unit_user_label = Channel.control(
        "SENSe:VOLTage{ch}:RANGe:UNIT:USER:LABel?",
        "SENSe:VOLTage{ch}:RANGe:UNIT:USER:LABel %s",
        """Control custom transducer unit label (string up to 4 characters).""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    range_unit_user_scale_factor = Channel.control(
        "SENSe:VOLTage{ch}:RANGe:UNIT:USER:SFACtor?",
        "SENSe:VOLTage{ch}:RANGe:UNIT:USER:SFACtor %g",
        """Control custom transducer sensitivity scale factor.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    range_unit_user_enabled = Channel.control(
        "SENSe:VOLTage{ch}:RANGe:UNIT:USER:STATe?",
        "SENSe:VOLTage{ch}:RANGe:UNIT:USER:STATe %d",
        """Control whether transducer units are enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    range_unit_transducer_label = Channel.control(
        "SENSe:VOLTage{ch}:RANGe:UNIT:XDCR:LABel?",
        "SENSe:VOLTage{ch}:RANGe:UNIT:XDCR:LABel %s",
        """Control transducer unit label selection.""",
        values=INPUT_RANGE_TRANSDUCER_LABELS,
        validator=strict_discrete_set,
        cast=str,
    )

    range_dbvrms = Channel.control(
        "SENSe:VOLTage{ch}:RANGe?",
        "SENSe:VOLTage{ch}:RANGe %g",
        """Control the input range in dBVrms.""",
        values=tuple(range(-51, 28, 2)),
        validator=strict_discrete_set,
        cast=float,
    )

    range_upper = Channel.control(
        "SENSe:VOLTage{ch}:RANGe?",
        "SENSe:VOLTage{ch}:RANGe %g",
        """Control the upper input range value.""",
        values=[-51.0, 31.66],
        validator=strict_range,
        cast=float,
    )


class Keysight35670ASenseWindow(Channel):
    """Represent a measurement SENSE window of the Keysight 35670A."""

    window_type = Channel.control(
        "SENSe:WINDow{ch}:TYPE?",
        "SENSe:WINDow{ch}:TYPE %s",
        """Control the time-window type.""",
        values=WINDOW_TYPES,
        map_values=True,
        validator=strict_discrete_set,
    )

    exponential_window_time_constant = Channel.control(
        "SENSe:WINDow{ch}:EXPonential?",
        "SENSe:WINDow{ch}:EXPonential %g",
        """Control the exponential-window time constant in seconds.""",
        values=[3.8147e-06, 9.9999e06],
        validator=strict_range,
        cast=float,
    )

    force_window_width = Channel.control(
        "SENSe:WINDow{ch}:FORCe?",
        "SENSe:WINDow{ch}:FORCe %g",
        """Control the force-window width in seconds.""",
        values=[3.8147e-06, 9.9999e06],
        validator=strict_range,
        cast=float,
    )

    force_window = force_window_width

    order_dc_included = Channel.control(
        "SENSe:WINDow{ch}:ORDer:DC?",
        "SENSe:WINDow{ch}:ORDer:DC %d",
        """Control whether the DC bin is included in order composite power.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )


class Keysight35670ADisplayWindow(Keysight35670ASenseWindow):
    """Represent a DISPlay window of the Keysight 35670A."""

    data_table_marker_enabled = Channel.control(
        "DISPlay:WINDow{ch}:DTABle:MARKer:STATe?",
        "DISPlay:WINDow{ch}:DTABle:MARKer:STATe %d",
        """Control whether data-table markers are shown for the window.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    data_table_enabled = Channel.control(
        "DISPlay:WINDow{ch}:DTABle:STATe?",
        "DISPlay:WINDow{ch}:DTABle:STATe %d",
        """Control whether the data table is displayed for the window.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    limit_display_enabled = Channel.control(
        "DISPlay:WINDow{ch}:LIMit:STATe?",
        "DISPlay:WINDow{ch}:LIMit:STATe %d",
        """Control whether limit lines are displayed for the window.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    polar_clockwise = Channel.control(
        "DISPlay:WINDow{ch}:POLar:CLOCkwise?",
        "DISPlay:WINDow{ch}:POLar:CLOCkwise %d",
        """Control clockwise direction for polar diagrams.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    polar_rotation = Channel.control(
        "DISPlay:WINDow{ch}:POLar:ROTation?",
        "DISPlay:WINDow{ch}:POLar:ROTation %g",
        """Control polar rotation angle in degrees.""",
        values=[-360.0, 360.0],
        validator=strict_range,
        cast=float,
    )

    trace_a_power_enabled = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:APOWer:STATe?",
        "DISPlay:WINDow{ch}:TRACe:APOWer:STATe %d",
        """Control whether A-weighted overall power is displayed.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    trace_b_power_enabled = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:BPOWer:STATe?",
        "DISPlay:WINDow{ch}:TRACe:BPOWer:STATe %d",
        """Control whether overall power is displayed.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    trace_graticule_grid_enabled = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:GRATicule:GRID:STATe?",
        "DISPlay:WINDow{ch}:TRACe:GRATicule:GRID:STATe %d",
        """Control whether the trace graticule grid is displayed.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    trace_label = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:LABel?",
        "DISPlay:WINDow{ch}:TRACe:LABel %s",
        """Control the custom trace label for the window.""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    trace_label_default_enabled = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:LABel:DEFault:STATe?",
        "DISPlay:WINDow{ch}:TRACe:LABel:DEFault:STATe %d",
        """Control whether default trace labels are displayed.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    hardcopy_trace_color = Channel.control(
        "HCOPy:ITEM:WINDow{ch}:TRACe:COLor?",
        "HCOPy:ITEM:WINDow{ch}:TRACe:COLor %d",
        """Control the hardcopy pen number used for the window trace.""",
        values=HARDCOPY_LABEL_COLOR_RANGE,
        validator=strict_range,
        cast=int,
    )

    hardcopy_trace_graticule_color = Channel.control(
        "HCOPy:ITEM:WINDow{ch}:TRACe:GRATicule:COLor?",
        "HCOPy:ITEM:WINDow{ch}:TRACe:GRATicule:COLor %d",
        """Control the hardcopy pen number used for the trace graticule.""",
        values=HARDCOPY_LABEL_COLOR_RANGE,
        validator=strict_range,
        cast=int,
    )

    hardcopy_trace_limit_line_type = Channel.control(
        "HCOPy:ITEM:WINDow{ch}:TRACe:LIMit:LTYPe?",
        "HCOPy:ITEM:WINDow{ch}:TRACe:LIMit:LTYPe %s",
        """Control the hardcopy line type used for limit lines.""",
        values=(),
        validator=_validate_hardcopy_line_type,
        get_process=_normalize_hardcopy_line_type,
        set_process=_normalize_hardcopy_line_type,
        cast=str,
        maxsplit=0,
    )

    hardcopy_trace_line_type = Channel.control(
        "HCOPy:ITEM:WINDow{ch}:TRACe:LTYPe?",
        "HCOPy:ITEM:WINDow{ch}:TRACe:LTYPe %s",
        """Control the hardcopy line type used for the window trace.""",
        values=(),
        validator=_validate_hardcopy_line_type,
        get_process=_normalize_hardcopy_line_type,
        set_process=_normalize_hardcopy_line_type,
        cast=str,
        maxsplit=0,
    )

    hardcopy_trace_marker_color = Channel.control(
        "HCOPy:ITEM:WINDow{ch}:TRACe:MARKer:COLor?",
        "HCOPy:ITEM:WINDow{ch}:TRACe:MARKer:COLor %d",
        """Control the hardcopy pen number used for window markers.""",
        values=HARDCOPY_LABEL_COLOR_RANGE,
        validator=strict_range,
        cast=int,
    )

    trace_x_autoscale = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:X:SCALe:AUTO?",
        "DISPlay:WINDow{ch}:TRACe:X:SCALe:AUTO %s",
        """Control trace X autoscaling mode.""",
        values=TRACE_X_AUTOSCALE,
        map_values=True,
        validator=strict_discrete_set,
    )

    trace_x_left = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:X:SCALe:LEFT?",
        "DISPlay:WINDow{ch}:TRACe:X:SCALe:LEFT %g",
        """Control the left X-axis scale value.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    trace_x_right = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:X:SCALe:RIGHt?",
        "DISPlay:WINDow{ch}:TRACe:X:SCALe:RIGHt %g",
        """Control the right X-axis scale value.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    trace_x_spacing = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:X:SPACing?",
        "DISPlay:WINDow{ch}:TRACe:X:SPACing %s",
        """Control the X-axis spacing mode.""",
        values=DISPLAY_AXIS_SPACING_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    trace_y_autoscale = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:AUTO?",
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:AUTO %s",
        """Control trace Y autoscaling mode.""",
        values=TRACE_Y_AUTOSCALE,
        map_values=True,
        validator=strict_discrete_set,
    )

    trace_y_bottom = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:BOTTom?",
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:BOTTom %g",
        """Control the Y-axis bottom reference value.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    trace_y_center = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:CENTer?",
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:CENTer %g",
        """Control the Y-axis center reference value.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    trace_y_per_division = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:PDIVision?",
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:PDIVision %g",
        """Control the Y-axis height per vertical division.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    trace_y_reference = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:REFerence?",
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:REFerence %s",
        """Control the Y-axis reference anchor mode.""",
        values=DISPLAY_TRACE_Y_REFERENCE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    trace_y_top = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:TOP?",
        "DISPlay:WINDow{ch}:TRACe:Y:SCALe:TOP %g",
        """Control the Y-axis top reference value.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    trace_y_spacing = Channel.control(
        "DISPlay:WINDow{ch}:TRACe:Y:SPACing?",
        "DISPlay:WINDow{ch}:TRACe:Y:SPACing %s",
        """Control the Y-axis spacing mode for linear magnitude traces.""",
        values=DISPLAY_AXIS_SPACING_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    waterfall_baseline = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:BASeline?",
        "DISPlay:WINDow{ch}:WATerfall:BASeline %g",
        """Control the concealed baseline fraction in percent.""",
        values=[0.0, 100.0],
        validator=strict_range,
        cast=float,
    )

    waterfall_bottom = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:BOTTom?",
        "DISPlay:WINDow{ch}:WATerfall:BOTTom %g",
        """Control the waterfall Z-axis bottom value.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    waterfall_count = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:COUNt?",
        "DISPlay:WINDow{ch}:WATerfall:COUNt %g",
        """Control the displayed waterfall Z-axis span/count value.""",
        values=[1e-6, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    waterfall_height = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:HEIGht?",
        "DISPlay:WINDow{ch}:WATerfall:HEIGht %g",
        """Control the waterfall trace-box height in percent.""",
        values=[1.0, 100.0],
        validator=strict_range,
        cast=float,
    )

    waterfall_hidden_enabled = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:HIDDen?",
        "DISPlay:WINDow{ch}:WATerfall:HIDDen %d",
        """Control whether hidden waterfall segments are removed.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    waterfall_skew_enabled = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:SKEW?",
        "DISPlay:WINDow{ch}:WATerfall:SKEW %d",
        """Control whether waterfall skew is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    waterfall_skew_angle = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:SKEW:ANGLe?",
        "DISPlay:WINDow{ch}:WATerfall:SKEW:ANGLe %g",
        """Control the waterfall skew angle in degrees.""",
        values=[-45.0, 45.0],
        validator=strict_range,
        cast=float,
    )

    waterfall_enabled = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:STATe?",
        "DISPlay:WINDow{ch}:WATerfall:STATe %d",
        """Control whether waterfall display is enabled for the window.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    waterfall_top = Channel.control(
        "DISPlay:WINDow{ch}:WATerfall:TOP?",
        "DISPlay:WINDow{ch}:WATerfall:TOP %g",
        """Control the waterfall Z-axis top value.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    def x_match(self, source_window) -> None:
        """Match this window X-axis scaling to another display window."""
        source = int(strict_range(int(source_window), [1, 4]))
        self.write(f"DISPlay:WINDow{{ch}}:TRACe:X:MATCh{source}")

    def y_match(self, source_window) -> None:
        """Match this window Y-axis scaling to another display window."""
        source = int(strict_range(int(source_window), [1, 4]))
        self.write(f"DISPlay:WINDow{{ch}}:TRACe:Y:MATCh{source}")


class Keysight35670AWindow(Keysight35670ADisplayWindow):
    """Represent a measurement/display window of the Keysight 35670A."""


class Keysight35670AOrderTrack(Channel):
    """Represent an order-track configuration channel of the Keysight 35670A."""

    order = Channel.control(
        "SENSe:ORDer:TRACk{ch}?",
        "SENSe:ORDer:TRACk{ch} %g",
        """Control the order number assigned to this order track.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    enabled = Channel.control(
        "SENSe:ORDer:TRACk{ch}:STATe?",
        "SENSe:ORDer:TRACk{ch}:STATe %d",
        """Control whether order-track mode is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )


class Keysight35670ATrace(Channel):
    """Represent a trace box of the Keysight 35670A."""

    active = Channel.control(
        "CALCulate{ch}:ACTive?",
        "CALCulate{ch}:ACTive %s",
        """Control which traces are active in the selected display group.""",
        values=TRACE_ACTIVE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    feed = Channel.control(
        "CALCulate{ch}:FEED?",
        "CALCulate{ch}:FEED '%s'",
        """Control the measurement data fed to the trace.""",
        values=TRACE_FEEDS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
        maxsplit=0,
    )

    display_format = Channel.control(
        "CALCulate{ch}:FORMat?",
        "CALCulate{ch}:FORMat %s",
        """Control the display coordinate format for the trace.""",
        values=TRACE_DISPLAY_FORMATS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    group_delay_aperture = Channel.control(
        "CALCulate{ch}:GDAPerture:APERture?",
        "CALCulate{ch}:GDAPerture:APERture %g",
        """Control the group-delay smoothing aperture in percent (float from 0 to 20).""",
        values=[0.0, 20.0],
        validator=strict_range,
        cast=float,
    )

    amplitude_unit = Channel.control(
        "CALCulate{ch}:UNIT:AMPLitude?",
        "CALCulate{ch}:UNIT:AMPLitude %s",
        """Control the trace amplitude unit.""",
        values=TRACE_AMPLITUDE_UNITS,
        validator=strict_discrete_set,
        cast=str,
    )

    angle_unit = Channel.control(
        "CALCulate{ch}:UNIT:ANGLe?",
        "CALCulate{ch}:UNIT:ANGLe %s",
        """Control the trace angle unit.""",
        values=TRACE_ANGLE_UNITS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    x_unit = Channel.control(
        "CALCulate{ch}:UNIT:X?",
        "CALCulate{ch}:UNIT:X %s",
        """Control the trace x-axis unit.""",
        values=TRACE_X_UNITS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    db_reference = Channel.control(
        "CALCulate{ch}:UNIT:DBReference?",
        "CALCulate{ch}:UNIT:DBReference %s",
        """Control the dB reference unit family.""",
        values=DB_REFERENCE_UNITS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    db_reference_impedance = Channel.control(
        "CALCulate{ch}:UNIT:DBReference:IMPedance?",
        "CALCulate{ch}:UNIT:DBReference:IMPedance %g",
        """Control the dBm reference impedance in ohms (float from 1e-15 to 1e15).""",
        values=[1e-15, 1e15],
        validator=strict_range,
        cast=float,
    )

    db_reference_user_label = Channel.control(
        "CALCulate{ch}:UNIT:DBReference:USER:LABel?",
        "CALCulate{ch}:UNIT:DBReference:USER:LABel %s",
        """Control the user label for dB reference units.""",
        validator=lambda v, vs: v,
        values=(),
        cast=str,
        set_process=_quote_string,
        get_process=_strip_quotes,
    )

    db_reference_user_reference = Channel.control(
        "CALCulate{ch}:UNIT:DBReference:USER:REFerence?",
        "CALCulate{ch}:UNIT:DBReference:USER:REFerence %g",
        """Control the reference level used for user dB units (float from 1e-15 to 1e15).""",
        values=[1e-15, 1e15],
        validator=strict_range,
        cast=float,
    )

    mechanical_unit = Channel.control(
        "CALCulate{ch}:UNIT:MECHanical?",
        "CALCulate{ch}:UNIT:MECHanical %s",
        """Control the mechanical engineering unit for the trace.""",
        values=TRACE_MECHANICAL_UNITS,
        validator=strict_discrete_set,
        cast=str,
    )

    voltage_unit = Channel.control(
        "CALCulate{ch}:UNIT:VOLTage?",
        "CALCulate{ch}:UNIT:VOLTage %s",
        """Control the voltage-derived vertical unit for the trace.""",
        values=TRACE_VOLTAGE_UNITS,
        validator=strict_discrete_set,
        cast=str,
    )

    x_order_factor = Channel.control(
        "CALCulate{ch}:UNIT:X:ORDer:FACTor?",
        "CALCulate{ch}:UNIT:X:ORDer:FACTor %g",
        """Control the X-axis order conversion factor (float from 1e-15 to 1e15).""",
        values=[1e-15, 1e15],
        validator=strict_range,
        cast=float,
    )

    x_user_frequency_factor = Channel.control(
        "CALCulate{ch}:UNIT:X:USER:FREQuency:FACTor?",
        "CALCulate{ch}:UNIT:X:USER:FREQuency:FACTor %g",
        (
            """Control the user frequency-domain X-axis conversion factor """
            """(float from 1e-15 to 1e15)."""
        ),
        values=[1e-15, 1e15],
        validator=strict_range,
        cast=float,
    )

    x_user_frequency_label = Channel.control(
        "CALCulate{ch}:UNIT:X:USER:FREQuency:LABel?",
        "CALCulate{ch}:UNIT:X:USER:FREQuency:LABel %s",
        """Control the user frequency-domain X-axis unit label.""",
        validator=lambda v, vs: v,
        values=(),
        cast=str,
        set_process=_quote_string,
        get_process=_strip_quotes,
    )

    x_user_time_factor = Channel.control(
        "CALCulate{ch}:UNIT:X:USER:TIME:FACTor?",
        "CALCulate{ch}:UNIT:X:USER:TIME:FACTor %g",
        """Control the user time-domain X-axis conversion factor (float from 1e-15 to 1e15).""",
        values=[1e-15, 1e15],
        validator=strict_range,
        cast=float,
    )

    x_user_time_label = Channel.control(
        "CALCulate{ch}:UNIT:X:USER:TIME:LABel?",
        "CALCulate{ch}:UNIT:X:USER:TIME:LABel %s",
        """Control the user time-domain X-axis unit label.""",
        validator=lambda v, vs: v,
        values=(),
        cast=str,
        set_process=_quote_string,
        get_process=_strip_quotes,
    )

    limit_beeper_enabled = Channel.control(
        "CALCulate{ch}:LIMit:BEEP:STATe?",
        "CALCulate{ch}:LIMit:BEEP:STATe %d",
        """Control whether the limit-fail beeper is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    limit_failed = Channel.measurement(
        "CALCulate{ch}:LIMit:FAIL?",
        """Measure whether the last limit test failed.""",
        cast=int,
        get_process=bool,
    )

    lower_limit_segment = Channel.control(
        "CALCulate{ch}:LIMit:LOWer:SEGMent?",
        "CALCulate{ch}:LIMit:LOWer:SEGMent %s",
        """Control lower limit line segments as (x0, y0, x1, y1) tuples.""",
        validator=lambda v, vs: v,
        values=(),
        set_process=_format_limit_segment_data,
        get_process=_parse_limit_segment_data,
        cast=str,
        maxsplit=0,
    )

    limit_enabled = Channel.control(
        "CALCulate{ch}:LIMit:STATe?",
        "CALCulate{ch}:LIMit:STATe %d",
        """Control whether limit testing is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    upper_limit_segment = Channel.control(
        "CALCulate{ch}:LIMit:UPPer:SEGMent?",
        "CALCulate{ch}:LIMit:UPPer:SEGMent %s",
        """Control upper limit line segments as (x0, y0, x1, y1) tuples.""",
        validator=lambda v, vs: v,
        values=(),
        set_process=_format_limit_segment_data,
        get_process=_parse_limit_segment_data,
        cast=str,
        maxsplit=0,
    )

    marker_band_start = Channel.control(
        "CALCulate{ch}:MARKer:BAND:STARt?",
        "CALCulate{ch}:MARKer:BAND:STARt %g",
        """Control the start value of the marker band (float from -9.9e37 to 9.9e37).""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_band_stop = Channel.control(
        "CALCulate{ch}:MARKer:BAND:STOP?",
        "CALCulate{ch}:MARKer:BAND:STOP %g",
        """Control the stop value of the marker band (float from -9.9e37 to 9.9e37).""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    markers_coupled = Channel.control(
        "CALCulate{ch}:MARKer:COUpled:STATe?",
        "CALCulate{ch}:MARKer:COUpled:STATe %d",
        """Control whether markers are coupled across traces.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    marker_data_table_insert_x = Channel.control(
        "CALCulate{ch}:MARKer:DTABle:X:INSert?",
        "CALCulate{ch}:MARKer:DTABle:X:INSert %g",
        """Control the inserted X-axis entry value in the marker data table.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_data_table_label = Channel.control(
        "CALCulate{ch}:MARKer:DTABle:X:LABel?",
        "CALCulate{ch}:MARKer:DTABle:X:LABel %s",
        """Control the label of the selected marker data-table entry.""",
        validator=lambda v, vs: v,
        values=(),
        cast=str,
        set_process=_quote_string,
        get_process=_strip_quotes,
    )

    marker_data_table_selected_point = Channel.control(
        "CALCulate{ch}:MARKer:DTABle:X:SELect:POINt?",
        "CALCulate{ch}:MARKer:DTABle:X:SELect:POINt %d",
        """Control the selected marker data-table entry index (integer from 1 to 50).""",
        values=[1, 50],
        validator=strict_range,
        cast=int,
    )

    marker_function = Channel.control(
        "CALCulate{ch}:MARKer:FUNCtion?",
        "CALCulate{ch}:MARKer:FUNCtion %s",
        """Control the active marker function.""",
        values=MARKER_FUNCTION_VALUES,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    marker_function_result = Channel.measurement(
        "CALCulate{ch}:MARKer:FUNCtion:RESult?",
        """Measure the currently selected marker function result.""",
        cast=float,
    )

    marker_harmonic_count = Channel.control(
        "CALCulate{ch}:MARKer:HARMonic:COUNt?",
        "CALCulate{ch}:MARKer:HARMonic:COUNt %d",
        """Control the number of harmonic markers (integer from 0 to 400).""",
        values=[0, 400],
        validator=strict_range,
        cast=int,
    )

    marker_harmonic_fundamental = Channel.control(
        "CALCulate{ch}:MARKer:HARMonic:FUNDamental?",
        "CALCulate{ch}:MARKer:HARMonic:FUNDamental %g",
        """Control the fundamental frequency used for harmonic markers.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_global_maximum_tracking_enabled = Channel.control(
        "CALCulate{ch}:MARKer:MAXimum:GLOBal:TRACk?",
        "CALCulate{ch}:MARKer:MAXimum:GLOBal:TRACk %d",
        """Control whether global-maximum marker tracking is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    marker_mode = Channel.control(
        "CALCulate{ch}:MARKer:MODE?",
        "CALCulate{ch}:MARKer:MODE %s",
        """Control absolute or relative marker mode.""",
        values=MARKER_MODE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    marker_position = Channel.control(
        "CALCulate{ch}:MARKer:POSition?",
        "CALCulate{ch}:MARKer:POSition %g",
        """Control the main marker position along the independent axis.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_position_point = Channel.control(
        "CALCulate{ch}:MARKer:POSition:POINt?",
        "CALCulate{ch}:MARKer:POSition:POINt %d",
        """Control the main marker position as an integer trace point index.""",
        values=[0, 2047],
        validator=strict_range,
        cast=int,
    )

    marker_reference_x = Channel.control(
        "CALCulate{ch}:MARKer:REFerence:X?",
        "CALCulate{ch}:MARKer:REFerence:X %g",
        """Control the marker reference X-axis position.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_reference_y = Channel.control(
        "CALCulate{ch}:MARKer:REFerence:Y?",
        "CALCulate{ch}:MARKer:REFerence:Y %g",
        """Control the marker reference Y-axis position.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_sideband_carrier = Channel.control(
        "CALCulate{ch}:MARKer:SIDeband:CARRier?",
        "CALCulate{ch}:MARKer:SIDeband:CARRier %g",
        """Control the carrier value used by sideband markers.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_sideband_count = Channel.control(
        "CALCulate{ch}:MARKer:SIDeband:COUNt?",
        "CALCulate{ch}:MARKer:SIDeband:COUNt %d",
        """Control the number of sideband markers (integer from 0 to 200).""",
        values=[0, 200],
        validator=strict_range,
        cast=int,
    )

    marker_sideband_increment = Channel.control(
        "CALCulate{ch}:MARKer:SIDeband:INCRement?",
        "CALCulate{ch}:MARKer:SIDeband:INCRement %g",
        """Control the increment between sideband markers.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_enabled = Channel.control(
        "CALCulate{ch}:MARKer:STATe?",
        "CALCulate{ch}:MARKer:STATe %d",
        """Control whether the trace marker is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    marker_x = Channel.control(
        "CALCulate{ch}:MARKer:X?",
        "CALCulate{ch}:MARKer:X %g",
        """Control the marker x-axis position.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    marker_x_relative = Channel.control(
        "CALCulate{ch}:MARKer:X:RELative?",
        "CALCulate{ch}:MARKer:X:RELative %g",
        """Control the marker X-axis position relative to the reference.""",
        values=[-102400.0, 102400.0],
        validator=strict_range,
        cast=float,
    )

    marker_y = Channel.measurement(
        "CALCulate{ch}:MARKer:Y?",
        """Measure the marker y-axis value.""",
        cast=float,
    )

    marker_y_relative = Channel.control(
        "CALCulate{ch}:MARKer:Y:RELative?",
        "CALCulate{ch}:MARKer:Y:RELative %g",
        """Control the marker Y-axis position relative to the reference.""",
        values=[-150.0, 150.0],
        validator=strict_range,
        cast=float,
    )

    math_selected_function = Channel.control(
        "CALCulate{ch}:MATH:SELect?",
        "CALCulate{ch}:MATH:SELect %s",
        """Control the selected math function register.""",
        values=MATH_SELECTED_FUNCTION_VALUES,
        validator=strict_discrete_set,
        cast=str,
    )

    math_enabled = Channel.control(
        "CALCulate{ch}:MATH:STATe?",
        "CALCulate{ch}:MATH:STATe %d",
        """Control whether the selected math function is evaluated.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    cfit_destination_register = Channel.control(
        "CALCulate{ch}:CFIT:DESTination?",
        "CALCulate{ch}:CFIT:DESTination %s",
        """Control the destination data register for curve-fit results.""",
        values=SOURCE_USER_REGISTERS,
        map_values=True,
        cast=str,
        validator=strict_discrete_set,
    )

    cfit_frequency_auto_enabled = Channel.control(
        "CALCulate{ch}:CFIT:FREQuency:AUTO?",
        "CALCulate{ch}:CFIT:FREQuency:AUTO %d",
        """Control whether curve fit uses the full-span frequency region.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    cfit_frequency_start = Channel.control(
        "CALCulate{ch}:CFIT:FREQuency:STARt?",
        "CALCulate{ch}:CFIT:FREQuency:STARt %g",
        """Control the curve-fit start frequency in hertz.""",
        values=[0.0, 114999.9023],
        validator=strict_range,
        cast=float,
    )

    cfit_frequency_stop = Channel.control(
        "CALCulate{ch}:CFIT:FREQuency:STOP?",
        "CALCulate{ch}:CFIT:FREQuency:STOP %g",
        """Control the curve-fit stop frequency in hertz.""",
        values=[0.390625, 115000.0],
        validator=strict_range,
        cast=float,
    )

    cfit_frequency_scale = Channel.control(
        "CALCulate{ch}:CFIT:FSCale?",
        "CALCulate{ch}:CFIT:FSCale %g",
        """Control the curve-fit frequency scaling factor.""",
        values=[1e-6, 1e6],
        validator=strict_range,
        cast=float,
    )

    cfit_order_auto_enabled = Channel.control(
        "CALCulate{ch}:CFIT:ORDer:AUTO?",
        "CALCulate{ch}:CFIT:ORDer:AUTO %d",
        """Control whether curve fit uses automatic model-order selection.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    cfit_order_poles = Channel.control(
        "CALCulate{ch}:CFIT:ORDer:POLes?",
        "CALCulate{ch}:CFIT:ORDer:POLes %d",
        """Control the curve-fit pole-count upper bound.""",
        values=[0, 20],
        validator=strict_range,
        cast=int,
    )

    cfit_order_zeros = Channel.control(
        "CALCulate{ch}:CFIT:ORDer:ZERos?",
        "CALCulate{ch}:CFIT:ORDer:ZERos %d",
        """Control the curve-fit zero-count upper bound.""",
        values=[0, 20],
        validator=strict_range,
        cast=int,
    )

    cfit_time_delay = Channel.control(
        "CALCulate{ch}:CFIT:TDELay?",
        "CALCulate{ch}:CFIT:TDELay %g",
        """Control the curve-fit time-delay value in seconds.""",
        values=[-100.0, 100.0],
        validator=strict_range,
        cast=float,
    )

    cfit_weight_auto_enabled = Channel.control(
        "CALCulate{ch}:CFIT:WEIGht:AUTO?",
        "CALCulate{ch}:CFIT:WEIGht:AUTO %d",
        """Control whether curve-fit weighting is generated automatically.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    cfit_weight_register = Channel.control(
        "CALCulate{ch}:CFIT:WEIGht:REGister?",
        "CALCulate{ch}:CFIT:WEIGht:REGister %s",
        """Control the data register used as curve-fit weighting input.""",
        values=SOURCE_USER_REGISTERS,
        map_values=True,
        cast=str,
        validator=strict_discrete_set,
    )

    synthesis_destination_register = Channel.control(
        "CALCulate{ch}:SYNThesis:DESTination?",
        "CALCulate{ch}:SYNThesis:DESTination %s",
        """Control the destination data register for synthesis results.""",
        values=SOURCE_USER_REGISTERS,
        map_values=True,
        cast=str,
        validator=strict_discrete_set,
    )

    synthesis_frequency_scale = Channel.control(
        "CALCulate{ch}:SYNThesis:FSCale?",
        "CALCulate{ch}:SYNThesis:FSCale %g",
        """Control the synthesis frequency scaling factor.""",
        values=[1e-6, 1e6],
        validator=strict_range,
        cast=float,
    )

    synthesis_gain = Channel.control(
        "CALCulate{ch}:SYNThesis:GAIN?",
        "CALCulate{ch}:SYNThesis:GAIN %g",
        """Control the synthesis gain constant (float from -9.9e37 to 9.9e37, excluding 0).""",
        values=LIMIT_VALUE_RANGE,
        validator=_strict_nonzero_range,
        cast=float,
    )

    synthesis_spacing = Channel.control(
        "CALCulate{ch}:SYNThesis:SPACing?",
        "CALCulate{ch}:SYNThesis:SPACing %s",
        """Control the synthesis X-axis spacing mode.""",
        values=SYNTHESIS_SPACING_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    synthesis_time_delay = Channel.control(
        "CALCulate{ch}:SYNThesis:TDELay?",
        "CALCulate{ch}:SYNThesis:TDELay %g",
        """Control the synthesis time-delay value in seconds.""",
        values=[-100.0, 100.0],
        validator=strict_range,
        cast=float,
    )

    synthesis_table_type = Channel.control(
        "CALCulate{ch}:SYNThesis:TTYPe?",
        "CALCulate{ch}:SYNThesis:TTYPe %s",
        """Control the synthesis table representation type.""",
        values=SYNTHESIS_TABLE_TYPE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    waterfall_count = Channel.control(
        "CALCulate{ch}:WATerfall:COUNt?",
        "CALCulate{ch}:WATerfall:COUNt %d",
        """Control the stored waterfall trace count.""",
        values=[1, 32767],
        validator=strict_range,
        cast=int,
    )

    waterfall_slice_select = Channel.control(
        "CALCulate{ch}:WATerfall:SLICe:SELect?",
        "CALCulate{ch}:WATerfall:SLICe:SELect %g",
        """Control the waterfall slice X-axis selection value.""",
        values=[-16382.0, 1e6],
        validator=strict_range,
        cast=float,
    )

    waterfall_slice_select_point = Channel.control(
        "CALCulate{ch}:WATerfall:SLICe:SELect:POINt?",
        "CALCulate{ch}:WATerfall:SLICe:SELect:POINt %d",
        """Control the waterfall slice selection by display point index.""",
        values=[0, 2048],
        validator=strict_range,
        cast=int,
    )

    waterfall_trace_select = Channel.control(
        "CALCulate{ch}:WATerfall:TRACe:SELect?",
        "CALCulate{ch}:WATerfall:TRACe:SELect %g",
        """Control the waterfall trace selection by Z-axis value.""",
        values=LIMIT_VALUE_RANGE,
        validator=strict_range,
        cast=float,
    )

    waterfall_trace_select_point = Channel.control(
        "CALCulate{ch}:WATerfall:TRACe:SELect:POINt?",
        "CALCulate{ch}:WATerfall:TRACe:SELect:POINt %d",
        """Control the waterfall trace selection by step index.""",
        values=[0, 32767],
        validator=strict_range,
        cast=int,
    )

    def set_math_constant(
        self,
        constant_register: int,
        real_part: float,
        imaginary_part: Optional[float] = None,
    ) -> None:
        """Set a math constant register value."""
        index = _math_register_selector(constant_register)
        real_value = float(strict_range(float(real_part), LIMIT_VALUE_RANGE))
        if imaginary_part is None:
            self.write(f"CALCulate{{ch}}:MATH:CONStant{index} {real_value:g}")
            return

        imaginary_value = float(strict_range(float(imaginary_part), LIMIT_VALUE_RANGE))
        self.write(
            f"CALCulate{{ch}}:MATH:CONStant{index} {real_value:g},{imaginary_value:g}"
        )

    def math_constant(self, constant_register: int) -> tuple[float, float]:
        """Read a math constant register as (real, imaginary)."""
        index = _math_register_selector(constant_register)
        values = _parse_ascii_floats(self.ask(f"CALCulate{{ch}}:MATH:CONStant{index}?"))
        if not values:
            raise ValueError("Math constant query returned no values.")
        if len(values) == 1:
            return values[0], 0.0
        return values[0], values[1]

    def set_math_expression(self, expression: str, function_register: int = 1) -> None:
        """Set a math expression in the selected function register."""
        index = _math_register_selector(function_register)
        self.write(
            f"CALCulate{{ch}}:MATH:EXPRession{index} {_quote_string(str(expression))}"
        )

    def math_expression(self, function_register: int = 1) -> str:
        """Read the math expression in the selected function register."""
        index = _math_register_selector(function_register)
        return _strip_quotes(self.ask(f"CALCulate{{ch}}:MATH:EXPRession{index}?"))

    def math_data(self, raw=False):
        """Read the complete math table block data."""
        self.write("CALCulate{ch}:MATH:DATA?")
        block = self.read_bytes(-1)
        if raw:
            return block
        if block.startswith(b"#"):
            return _parse_definite_block(block)
        return block.decode("latin1")

    def load_math_data(self, data, raw=False) -> None:
        """Load complete math table block data."""
        payload = _coerce_bytes(data)
        block = payload if raw else _encode_definite_block(payload)
        prefix = self.insert_id("CALCulate{ch}:MATH:DATA ").encode("ascii")
        self.write_bytes(prefix + block)

    def abort_curve_fit(self) -> None:
        """Abort the curve-fit operation."""
        self.write("CALCulate{ch}:CFIT:ABORt")

    def copy_synthesis_to_curve_fit(self) -> None:
        """Copy the synthesis table into the curve-fit table."""
        self.write("CALCulate{ch}:CFIT:COPY SYNThesis")

    def cfit_data(self, raw=False):
        """Read the complete curve-fit table block data."""
        self.write("CALCulate{ch}:CFIT:DATA?")
        block = self.read_bytes(-1)
        if raw:
            return block
        if block.startswith(b"#"):
            return _parse_definite_block(block)
        return block.decode("latin1")

    def load_cfit_data(self, data, raw=False) -> None:
        """Load complete curve-fit table block data."""
        payload = _coerce_bytes(data)
        block = payload if raw else _encode_definite_block(payload)
        prefix = self.insert_id("CALCulate{ch}:CFIT:DATA ").encode("ascii")
        self.write_bytes(prefix + block)

    def run_curve_fit(self) -> None:
        """Start a curve-fit operation and use wait_for_completion() to synchronize."""
        self.write("CALCulate{ch}:CFIT:IMMediate")

    def copy_curve_fit_to_synthesis(self) -> None:
        """Copy the curve-fit table into the synthesis table."""
        self.write("CALCulate{ch}:SYNThesis:COPY CFIT")

    def synthesis_data(self, raw=False):
        """Read the complete synthesis table block data."""
        self.write("CALCulate{ch}:SYNThesis:DATA?")
        block = self.read_bytes(-1)
        if raw:
            return block
        if block.startswith(b"#"):
            return _parse_definite_block(block)
        return block.decode("latin1")

    def load_synthesis_data(self, data, raw=False) -> None:
        """Load complete synthesis table block data."""
        payload = _coerce_bytes(data)
        block = payload if raw else _encode_definite_block(payload)
        prefix = self.insert_id("CALCulate{ch}:SYNThesis:DATA ").encode("ascii")
        self.write_bytes(prefix + block)

    def run_synthesis(self) -> None:
        """Start synthesis and use wait_for_completion() to synchronize."""
        self.write("CALCulate{ch}:SYNThesis:IMMediate")

    def waterfall_data(self, raw=False):
        """Read transformed waterfall data for the selected trace box."""
        if raw:
            self.write("CALCulate{ch}:WATerfall:DATA?")
            return self.read_bytes(-1)
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:WATerfall:DATA?")
        )

    def copy_waterfall_slice_to_register(self, register) -> None:
        """Copy the selected waterfall slice to a data register."""
        selector = _data_register_selector(register)
        self.write(f"CALCulate{{ch}}:WATerfall:SLICe:COPY {selector}")

    def copy_waterfall_trace_to_register(self, register) -> None:
        """Copy the selected waterfall trace to a data register."""
        selector = _data_register_selector(register)
        self.write(f"CALCulate{{ch}}:WATerfall:TRACe:COPY {selector}")

    def data_points(self) -> int:
        """Get the number of data points in the trace data block."""
        return int(self.ask("CALCulate{ch}:DATA:HEADer:POINts?"))

    def read_data(self) -> list[float]:
        """Read the trace data values."""
        return _parse_ascii_floats(self.ask("CALCulate{ch}:DATA?"))

    def read_x_data(self) -> list[float]:
        """Read the trace x-axis data values."""
        return _parse_ascii_floats(self.ask("CALCulate{ch}:X:DATA?"))

    def clear_marker_data_table(self, confirmed=False) -> None:
        """Clear the marker data table after explicit confirmation."""
        _require_confirmation("clear marker data table", confirmed)
        self.write("CALCulate{ch}:MARKer:DTABle:CLEar:IMMediate")

    def copy_marker_data_table_from(self, source_trace) -> None:
        """Copy marker data-table entries from another trace index."""
        source = int(strict_range(int(source_trace), [1, 4]))
        self.write(f"CALCulate{{ch}}:MARKer:DTABle:COPY{source}")

    def read_marker_data_table_y(self) -> list[float]:
        """Read dependent-axis values from the marker data table."""
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:MARKer:DTABle:DATA?")
        )

    def read_marker_data_table_x(self) -> list[float]:
        """Read independent-axis values from the marker data table."""
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:MARKer:DTABle:X:DATA?")
        )

    def delete_marker_data_table_entry(self, confirmed=False) -> None:
        """Delete the selected marker data-table entry after explicit confirmation."""
        _require_confirmation("delete marker data-table entry", confirmed)
        self.write("CALCulate{ch}:MARKer:DTABle:X:DELete")

    def clear_lower_limit(self, confirmed=False) -> None:
        """Clear the complete lower limit line after explicit confirmation."""
        _require_confirmation("clear lower limit line", confirmed)
        self.write("CALCulate{ch}:LIMit:LOWer:CLEar:IMMediate")

    def move_lower_limit_y(self, delta) -> None:
        """Move the lower limit line by the specified Y-axis delta."""
        value = float(strict_range(float(delta), LIMIT_VALUE_RANGE))
        self.write(f"CALCulate{{ch}}:LIMit:LOWer:MOVE:Y {value:g}")

    def read_lower_limit_report_x(self) -> list[float]:
        """Read X-axis values of failed lower-limit points."""
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:LIMit:LOWer:REPort:DATA?")
        )

    def read_lower_limit_report_y(self) -> list[float]:
        """Read Y-axis values of failed lower-limit points."""
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:LIMit:LOWer:REPort:YDATa?")
        )

    def clear_lower_limit_segment(self, segment, confirmed=False) -> None:
        """Clear the lower-limit segment containing the selected X-axis value."""
        _require_confirmation("clear lower limit segment", confirmed)
        value = float(strict_range(float(segment), LIMIT_VALUE_RANGE))
        self.write(f"CALCulate{{ch}}:LIMit:LOWer:SEGMent:CLEar {value:g}")

    def make_lower_limit_from_trace(self, confirmed=False) -> None:
        """Convert the current trace into a lower limit line after explicit confirmation."""
        _require_confirmation("convert trace to lower limit line", confirmed)
        self.write("CALCulate{ch}:LIMit:LOWer:TRACe:IMMediate")

    def clear_upper_limit(self, confirmed=False) -> None:
        """Clear the complete upper limit line after explicit confirmation."""
        _require_confirmation("clear upper limit line", confirmed)
        self.write("CALCulate{ch}:LIMit:UPPer:CLEar:IMMediate")

    def move_upper_limit_y(self, delta) -> None:
        """Move the upper limit line by the specified Y-axis delta."""
        value = float(strict_range(float(delta), LIMIT_VALUE_RANGE))
        self.write(f"CALCulate{{ch}}:LIMit:UPPer:MOVE:Y {value:g}")

    def read_upper_limit_report_x(self) -> list[float]:
        """Read X-axis values of failed upper-limit points."""
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:LIMit:UPPer:REPort:DATA?")
        )

    def read_upper_limit_report_y(self) -> list[float]:
        """Read Y-axis values of failed upper-limit points."""
        return _parse_ascii_or_definite_block_floats(
            self.ask("CALCulate{ch}:LIMit:UPPer:REPort:YDATa?")
        )

    def clear_upper_limit_segment(self, segment, confirmed=False) -> None:
        """Clear the upper-limit segment containing the selected X-axis value."""
        _require_confirmation("clear upper limit segment", confirmed)
        value = float(strict_range(float(segment), LIMIT_VALUE_RANGE))
        self.write(f"CALCulate{{ch}}:LIMit:UPPer:SEGMent:CLEar {value:g}")

    def make_upper_limit_from_trace(self, confirmed=False) -> None:
        """Convert the current trace into an upper limit line after explicit confirmation."""
        _require_confirmation("convert trace to upper limit line", confirmed)
        self.write("CALCulate{ch}:LIMit:UPPer:TRACe:IMMediate")

    def marker_to_left_maximum(self) -> None:
        """Move the marker to the next peak on the left."""
        self.write("CALCulate{ch}:MARKer:MAXimum:LEFT")

    def marker_to_right_maximum(self) -> None:
        """Move the marker to the next peak on the right."""
        self.write("CALCulate{ch}:MARKer:MAXimum:RIGHt")

    def marker_to_global_maximum(self) -> None:
        """Move the marker to the global maximum."""
        self.write("CALCulate{ch}:MARKer:MAXimum:GLOBAL")


class Keysight35670A(SCPIMixin, Instrument):
    """Represent the Keysight 35670A Dynamic Signal Analyzer."""

    ch1 = Instrument.ChannelCreator(Keysight35670AInputChannel, 1)
    ch2 = Instrument.ChannelCreator(Keysight35670AInputChannel, 2)
    ch3 = Instrument.ChannelCreator(Keysight35670AInputChannel, 3)
    ch4 = Instrument.ChannelCreator(Keysight35670AInputChannel, 4)

    trace1 = Instrument.ChannelCreator(Keysight35670ATrace, 1)
    trace2 = Instrument.ChannelCreator(Keysight35670ATrace, 2)
    trace3 = Instrument.ChannelCreator(Keysight35670ATrace, 3)
    trace4 = Instrument.ChannelCreator(Keysight35670ATrace, 4)

    order_track1 = Instrument.ChannelCreator(Keysight35670AOrderTrack, 1)
    order_track2 = Instrument.ChannelCreator(Keysight35670AOrderTrack, 2)
    order_track3 = Instrument.ChannelCreator(Keysight35670AOrderTrack, 3)
    order_track4 = Instrument.ChannelCreator(Keysight35670AOrderTrack, 4)
    order_track5 = Instrument.ChannelCreator(Keysight35670AOrderTrack, 5)

    sense_window1 = Instrument.ChannelCreator(Keysight35670ASenseWindow, 1)
    sense_window2 = Instrument.ChannelCreator(Keysight35670ASenseWindow, 2)
    sense_window3 = Instrument.ChannelCreator(Keysight35670ASenseWindow, 3)
    sense_window4 = Instrument.ChannelCreator(Keysight35670ASenseWindow, 4)

    display1 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 1)
    display2 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 2)
    display3 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 3)
    display4 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 4)

    window1 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 1)
    window2 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 2)
    window3 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 3)
    window4 = Instrument.ChannelCreator(Keysight35670ADisplayWindow, 4)

    def __init__(self, adapter, name="Keysight 35670A Dynamic Signal Analyzer", **kwargs):
        kwargs.setdefault("timeout", 10000)
        kwargs.setdefault("read_termination", "\n")
        kwargs.setdefault("write_termination", "\n")
        super().__init__(adapter, name, **kwargs)

    instrument_mode = Instrument.control(
        "INSTrument:SELect?",
        "INSTrument:SELect %s",
        """Control the instrument mode.""",
        values=INSTRUMENT_MODES,
        map_values=True,
        validator=strict_discrete_set,
    )

    selected_instrument_number = Instrument.control(
        "INSTrument:NSELect?",
        "INSTrument:NSELect %d",
        """Control the selected instrument mode by number.""",
        values=[0, 5],
        validator=strict_range,
        cast=int,
    )

    _selected_instrument_number_setting = Instrument.setting(
        "INSTrument:NSELect %d",
        """Set the selected instrument mode by number.""",
        values=[0, 5],
        validator=strict_range,
    )

    continuous_initiation_enabled = Instrument.control(
        "INITiate:CONTinuous?",
        "INITiate:CONTinuous %d",
        """Control whether measurements are continuously initiated.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    averaging_enabled = Instrument.control(
        "SENSe:AVERage:STATe?",
        "SENSe:AVERage:STATe %d",
        """Control whether averaging is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    average_confidence = Instrument.control(
        "SENSe:AVERage:CONFidence?",
        "SENSe:AVERage:CONFidence %g",
        """Control equal-confidence averaging level in dB.""",
        values=[0.25, 2.0],
        validator=strict_range,
        cast=float,
    )

    average_count = Instrument.control(
        "SENSe:AVERage:COUNt?",
        "SENSe:AVERage:COUNt %d",
        """Control the averaging count.""",
        values=[1, 9999999],
        validator=strict_range,
        cast=int,
    )

    average_hold = Instrument.control(
        "SENSe:AVERage:HOLD?",
        "SENSe:AVERage:HOLD %s",
        """Control the averaging hold mode for octave measurements.""",
        values=AVERAGE_HOLD_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    average_impulse_enabled = Instrument.control(
        "SENSe:AVERage:IMPulse?",
        "SENSe:AVERage:IMPulse %d",
        """Control whether octave impulse detection is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    average_iresult_rate = Instrument.control(
        "SENSe:AVERage:IRESult:RATE?",
        "SENSe:AVERage:IRESult:RATE %d",
        """Control fast-average display update rate in averages.""",
        values=[1, 9999999],
        validator=strict_range,
        cast=int,
    )

    average_iresult_enabled = Instrument.control(
        "SENSe:AVERage:IRESult:STATe?",
        "SENSe:AVERage:IRESult:STATe %d",
        """Control whether fast-average display mode is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    average_preview = Instrument.control(
        "SENSe:AVERage:PREView?",
        "SENSe:AVERage:PREView %s",
        """Control preview averaging mode.""",
        values=AVERAGE_PREVIEW_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    average_preview_time = Instrument.control(
        "SENSe:AVERage:PREView:TIME?",
        "SENSe:AVERage:PREView:TIME %g",
        """Control timed-preview wait duration in seconds.""",
        values=[0.1, 3600.0],
        validator=strict_range,
        cast=float,
    )

    average_type = Instrument.control(
        "SENSe:AVERage:TYPE?",
        "SENSe:AVERage:TYPE %s",
        """Control the averaging type.""",
        values=AVERAGE_TYPES,
        map_values=True,
        validator=strict_discrete_set,
    )

    average_time = Instrument.control(
        "SENSe:AVERage:TIME?",
        "SENSe:AVERage:TIME %g",
        """Control averaging time in seconds.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    average_tcontrol = Instrument.control(
        "SENSe:AVERage:TCONtrol?",
        "SENSe:AVERage:TCONtrol %s",
        """Control averaging time-control behavior.""",
        values=AVERAGE_TCONTROLS,
        map_values=True,
        validator=strict_discrete_set,
    )

    source_output_enabled = Instrument.control(
        "OUTPut:STATe?",
        "OUTPut:STATe %d",
        """Control whether the source output is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    output_low_pass_filter_enabled = Instrument.control(
        "OUTPut:FILTer:LPASs:STATe?",
        "OUTPut:FILTer:LPASs:STATe %d",
        """Control whether the source output low-pass filter is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    source_function = Instrument.control(
        "SOURce:FUNCtion:SHAPe?",
        "SOURce:FUNCtion:SHAPe %s",
        """Control the source waveform shape.""",
        values=SOURCE_FUNCTIONS,
        map_values=True,
        validator=strict_discrete_set,
    )

    source_frequency_cw = Instrument.control(
        "SOURce:FREQuency?",
        "SOURce:FREQuency %g",
        """Control the sine source frequency in Hz using SOURce:FREQuency[:CW].""",
        values=[0.0, 115000.0],
        validator=strict_range,
        cast=float,
    )

    source_frequency_fixed = Instrument.control(
        "SOURce:FREQuency:FIXed?",
        "SOURce:FREQuency:FIXed %g",
        """Control the sine source frequency in Hz using SOURce:FREQuency:FIXed.""",
        values=[0.0, 115000.0],
        validator=strict_range,
        cast=float,
    )

    source_frequency = source_frequency_fixed

    source_burst_percent = Instrument.control(
        "SOURce:BURSt?",
        "SOURce:BURSt %g",
        """Control the burst length as a percentage of the time record.""",
        values=[0.0, 100.0],
        validator=strict_range,
        cast=float,
    )

    source_user_capture_channel = Instrument.control(
        "SOURce:USER:CAPTure?",
        "SOURce:USER:CAPTure %d",
        """Control the time-capture channel used by the CAPTure source waveform.""",
        values=[1, 4],
        validator=strict_range,
        cast=int,
    )

    source_user_register = Instrument.control(
        "SOURce:USER:REGister?",
        "SOURce:USER:REGister %s",
        """Control which data register index is used by the USER source waveform.""",
        values=SOURCE_USER_REGISTERS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    source_user_repeat_enabled = Instrument.control(
        "SOURce:USER:REPeat?",
        "SOURce:USER:REPeat %d",
        """Control whether USER/CAPTure source playback repeats.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    source_voltage_autolevel_enabled = Instrument.control(
        "SOURce:VOLTage:LEVel:AUTO?",
        "SOURce:VOLTage:LEVel:AUTO %d",
        """Control whether swept-sine source autolevel is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    source_voltage_amplitude = Instrument.control(
        "SOURce:VOLTage:LEVel:IMMediate:AMPLitude?",
        "SOURce:VOLTage:LEVel:IMMediate:AMPLitude %g",
        """Control source amplitude in the active level unit (range -9.9e37 to 13.9794).""",
        values=[-9.9e37, 13.9794],
        validator=strict_range,
        cast=float,
    )

    source_voltage_offset = Instrument.control(
        "SOURce:VOLTage:LEVel:IMMediate:OFFSet?",
        "SOURce:VOLTage:LEVel:IMMediate:OFFSet %g",
        """Control the source DC offset in volts.""",
        values=[-10.0, 10.0],
        validator=strict_range,
        cast=float,
    )

    source_voltage_reference = Instrument.control(
        "SOURce:VOLTage:LEVel:REFerence?",
        "SOURce:VOLTage:LEVel:REFerence %g",
        """Control the source autolevel reference amplitude in dB.""",
        values=[-69.276, 31.66],
        validator=strict_range,
        cast=float,
    )

    source_voltage_reference_channel = Instrument.control(
        "SOURce:VOLTage:LEVel:REFerence:CHANnel?",
        "SOURce:VOLTage:LEVel:REFerence:CHANnel %s",
        """Control the autolevel reference input channel index.""",
        values=SOURCE_REFERENCE_CHANNELS,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
    )

    source_voltage_reference_tolerance = Instrument.control(
        "SOURce:VOLTage:LEVel:REFerence:TOLerance?",
        "SOURce:VOLTage:LEVel:REFerence:TOLerance %g",
        """Control the source autolevel sensitivity in dB.""",
        values=[0.1, 20.0],
        validator=strict_range,
        cast=float,
    )

    source_voltage_limit_amplitude = Instrument.control(
        "SOURce:VOLTage:LIMit:AMPLitude?",
        "SOURce:VOLTage:LIMit:AMPLitude %g",
        """Control the source autolevel maximum source amplitude limit.""",
        values=[-9.9e37, 13.9794],
        validator=strict_range,
        cast=float,
    )

    source_voltage_limit_input = Instrument.control(
        "SOURce:VOLTage:LIMit:INPut?",
        "SOURce:VOLTage:LIMit:INPut %g",
        """Control the autolevel maximum non-reference input amplitude limit in dB.""",
        values=[-69.276, 31.66],
        validator=strict_range,
        cast=float,
    )

    source_voltage_slew = Instrument.control(
        "SOURce:VOLTage:SLEW?",
        "SOURce:VOLTage:SLEW %g",
        """Control the source amplitude ramp rate in V/s.""",
        values=[0.0, 10000.0],
        validator=strict_range,
        cast=float,
    )

    trigger_source = Instrument.control(
        "TRIGger:SOURce?",
        "TRIGger:SOURce %s",
        """Control the trigger source.""",
        values=TRIGGER_SOURCES,
        map_values=True,
        validator=strict_discrete_set,
    )

    trigger_slope = Instrument.control(
        "TRIGger:SLOPe?",
        "TRIGger:SLOPe %s",
        """Control the trigger slope.""",
        values=TRIGGER_SLOPES,
        map_values=True,
        validator=strict_discrete_set,
    )

    trigger_level = Instrument.control(
        "TRIGger:LEVel?",
        "TRIGger:LEVel %g",
        """Control the trigger level.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    external_trigger_filter_enabled = Instrument.control(
        "TRIGger:EXTernal:FILTer:LPAS:STATe?",
        "TRIGger:EXTernal:FILTer:LPAS:STATe %d",
        """Control whether external-trigger low-pass filtering is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    external_trigger_level = Instrument.control(
        "TRIGger:EXTernal:LEVel?",
        "TRIGger:EXTernal:LEVel %g",
        """Control the external trigger level.""",
        values=[-10.0, 10.0],
        validator=strict_range,
        cast=float,
    )

    external_trigger_range = Instrument.control(
        "TRIGger:EXTernal:RANGe?",
        "TRIGger:EXTernal:RANGe %s",
        """Control external trigger input range.""",
        values=EXTERNAL_TRIGGER_RANGES,
        map_values=True,
        validator=strict_discrete_set,
    )

    trigger_start1 = Instrument.control(
        "TRIGger:STARt1?",
        "TRIGger:STARt1 %g",
        """Control channel 1 trigger start delay in seconds.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    trigger_start2 = Instrument.control(
        "TRIGger:STARt2?",
        "TRIGger:STARt2 %g",
        """Control channel 2 trigger start delay in seconds.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    trigger_start3 = Instrument.control(
        "TRIGger:STARt3?",
        "TRIGger:STARt3 %g",
        """Control channel 3 trigger start delay in seconds.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    trigger_start4 = Instrument.control(
        "TRIGger:STARt4?",
        "TRIGger:STARt4 %g",
        """Control channel 4 trigger start delay in seconds.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    tachometer_holdoff = Instrument.control(
        "TRIGger:TACHometer:HOLDoff?",
        "TRIGger:TACHometer:HOLDoff %g",
        """Control the tachometer trigger holdoff interval in seconds.""",
        values=[0.0, 0.052224],
        validator=strict_range,
        cast=float,
    )

    tachometer_level = Instrument.control(
        "TRIGger:TACHometer:LEVel?",
        "TRIGger:TACHometer:LEVel %g",
        """Control the tachometer trigger level in Volts."""
        """ The valid range depends on tachometer_range.""",
        values=[-20.0, 20.0],
        validator=strict_range,
        cast=float,
    )

    tachometer_pulse_count = Instrument.control(
        "TRIGger:TACHometer:PCOunt?",
        "TRIGger:TACHometer:PCOunt %g",
        """Control tachometer pulses per revolution.""",
        values=[0.5, 2048.0],
        validator=strict_range,
        cast=float,
    )

    tachometer_range = Instrument.control(
        "TRIGger:TACHometer:RANGe?",
        "TRIGger:TACHometer:RANGe %s",
        """Control the tachometer input range.""",
        values=TACHOMETER_TRIGGER_RANGES,
        map_values=True,
        validator=strict_discrete_set,
    )

    tachometer_slope = Instrument.control(
        "TRIGger:TACHometer:SLOPe?",
        "TRIGger:TACHometer:SLOPe %s",
        """Control the tachometer trigger slope.""",
        values=TACHOMETER_SLOPES,
        map_values=True,
        validator=strict_discrete_set,
    )

    tachometer_rpm = Instrument.measurement(
        "TRIGger:TACHometer:RPM?",
        """Measure the tachometer speed in RPM.""",
        cast=float,
    )

    display_annotation_enabled = Instrument.control(
        "DISPlay:ANNotation:ALL?",
        "DISPlay:ANNotation:ALL %d",
        """Control whether display annotations are shown.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_brightness = Instrument.control(
        "DISPlay:BRIGhtness?",
        "DISPlay:BRIGhtness %g",
        """Control display brightness (float from 0.5 to 1).""",
        values=[0.5, 1.0],
        validator=strict_range,
        cast=float,
    )

    display_external_enabled = Instrument.control(
        "DISPlay:EXTernal:STATe?",
        "DISPlay:EXTernal:STATe %d",
        """Control whether the external monitor output is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_enabled = Instrument.control(
        "DISPlay:STATe?",
        "DISPlay:STATe %d",
        """Control display enabled state.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_format = Instrument.control(
        "DISPlay:FORMat?",
        "DISPlay:FORMat %s",
        """Control display format layout.""",
        values=DISPLAY_FORMATS,
        map_values=True,
        validator=strict_discrete_set,
    )

    display_gpib_echo_enabled = Instrument.control(
        "DISPlay:GPIB:ECHO?",
        "DISPlay:GPIB:ECHO %d",
        """Control whether front-panel GPIB mnemonic echo is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_program_mode = Instrument.control(
        "DISPlay:PROGram:MODE?",
        "DISPlay:PROGram:MODE %s",
        """Control which display region is allocated to Instrument BASIC output.""",
        values=DISPLAY_PROGRAM_MODES,
        map_values=True,
        validator=strict_discrete_set,
    )

    display_program_vector_buffer_enabled = Instrument.control(
        "DISPlay:PROGram:VECTor:BUFFer:STATe?",
        "DISPlay:PROGram:VECTor:BUFFer:STATe %d",
        """Control buffering of vectors drawn by Instrument BASIC graphics.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    program_edit_enabled = Instrument.control(
        "PROGram:EDIT:ENABle?",
        "PROGram:EDIT:ENABle %d",
        """Control whether the Instrument BASIC editor is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    program_name = Instrument.control(
        "PROGram:NAME?",
        "PROGram:NAME %s",
        """Control the active Instrument BASIC program buffer.""",
        values=(),
        validator=lambda value, values: _normalize_program_name(value),
        set_process=lambda value: _normalize_program_name(value),
        get_process=lambda value: _normalize_program_name(value),
        cast=str,
        maxsplit=0,
    )

    program_label = Instrument.control(
        "PROGram:LABel?",
        "PROGram:LABel %s",
        """Control the softkey label of the active Instrument BASIC program.""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    program_state = Instrument.control(
        "PROGram:STATe?",
        "PROGram:STATe %s",
        """Control the run state of the active Instrument BASIC program.""",
        values=PROGRAM_STATE_VALUES,
        validator=lambda value, values: _normalize_program_state(value),
        set_process=lambda value: _normalize_program_state(value),
        get_process=lambda value: _normalize_program_state(value),
        cast=str,
        maxsplit=0,
    )

    program_allocated_memory = Instrument.measurement(
        "PROGram:MALLocate?",
        """Measure the allocated Instrument BASIC program memory in bytes.""",
        cast=int,
    )

    display_rpm_enabled = Instrument.control(
        "DISPlay:RPM:STATe?",
        "DISPlay:RPM:STATe %d",
        """Control whether the RPM indicator is shown.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_show_all_enabled = Instrument.control(
        "DISPlay:SHOWall:STATe?",
        "DISPlay:SHOWall:STATe %d",
        """Control whether all FFT lines are shown when available.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_time_capture_envelope_enabled = Instrument.control(
        "DISPlay:TCAPture:ENVelope:STATe?",
        "DISPlay:TCAPture:ENVelope:STATe %d",
        """Control whether time-capture envelope is displayed.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    display_view = Instrument.control(
        "DISPlay:VIEW?",
        "DISPlay:VIEW %s",
        """Control display view selection.""",
        values=DISPLAY_VIEWS,
        map_values=True,
        validator=strict_discrete_set,
    )

    hardcopy_destination = Instrument.control(
        "HCOPy:DESTination?",
        "HCOPy:DESTination %s",
        """Control the hardcopy destination handler.""",
        values=HARDCOPY_DESTINATION_VALUES,
        validator=_validate_hardcopy_destination,
        get_process=_normalize_hardcopy_destination,
        set_process=_quote_string,
        cast=str,
        maxsplit=0,
    )

    hardcopy_device_language = Instrument.control(
        "HCOPy:DEVice:LANGuage?",
        "HCOPy:DEVice:LANGuage %s",
        """Control the hardcopy output language.""",
        values=HARDCOPY_DEVICE_LANGUAGE_VALUES,
        validator=strict_discrete_set,
        cast=str,
        get_process=lambda value: _strip_quotes(str(value)).upper(),
        set_process=lambda value: _strip_quotes(str(value)).upper(),
        maxsplit=0,
    )

    hardcopy_device_resolution = Instrument.control(
        "HCOPy:DEVice:RESolution?",
        "HCOPy:DEVice:RESolution %d",
        """Control the hardcopy output resolution in dots per inch.""",
        values=[0, 32767],
        validator=strict_range,
        cast=int,
    )

    hardcopy_device_speed = Instrument.control(
        "HCOPy:DEVice:SPEed?",
        "HCOPy:DEVice:SPEed %d",
        """Control the hardcopy plotting speed in centimeters per second.""",
        values=[0, 100],
        validator=strict_range,
        cast=int,
    )

    hardcopy_form_feed_enabled = Instrument.control(
        "HCOPy:ITEM:FFEed:STATe?",
        "HCOPy:ITEM:FFEed:STATe %d",
        """Control whether hardcopy page-eject is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    hardcopy_label_color = Instrument.control(
        "HCOPy:ITEM:LABel:COLor?",
        "HCOPy:ITEM:LABel:COLor %d",
        """Control the hardcopy pen number used for labels and annotations.""",
        values=HARDCOPY_LABEL_COLOR_RANGE,
        validator=strict_range,
        cast=int,
    )

    hardcopy_label_enabled = Instrument.control(
        "HCOPy:ITEM:LABel:STATe?",
        "HCOPy:ITEM:LABel:STATe %d",
        """Control whether the hardcopy label text is shown.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    hardcopy_label_text = Instrument.control(
        "HCOPy:ITEM:LABel:TEXT?",
        "HCOPy:ITEM:LABel:TEXT %s",
        """Control the hardcopy label text.""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    hardcopy_timestamp_format = Instrument.control(
        "HCOPy:ITEM:TDSTamp:FORMat?",
        "HCOPy:ITEM:TDSTamp:FORMat %s",
        """Control the hardcopy date/time stamp format.""",
        values=HARDCOPY_TIMESTAMP_FORMAT_VALUES,
        validator=_validate_hardcopy_timestamp_format,
        get_process=_normalize_hardcopy_timestamp_format,
        set_process=_normalize_hardcopy_timestamp_format,
        cast=str,
        maxsplit=0,
    )

    hardcopy_timestamp_enabled = Instrument.control(
        "HCOPy:ITEM:TDSTamp:STATe?",
        "HCOPy:ITEM:TDSTamp:STATe %d",
        """Control whether hardcopy time stamp output is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    hardcopy_page_dimensions_auto_enabled = Instrument.control(
        "HCOPy:PAGE:DIMensions:AUTO?",
        "HCOPy:PAGE:DIMensions:AUTO %d",
        """Control whether hardcopy page dimensions are auto-configured.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    hardcopy_page_user_lower_left = Instrument.control(
        "HCOPy:PAGE:DIMensions:USER:LLEFt?",
        "HCOPy:PAGE:DIMensions:USER:LLEFt %d,%d",
        """Control the hardcopy P1 page point as (x, y).""",
        values=HARDCOPY_PAGE_POINT_VALUES,
        validator=_validate_int_pair,
        cast=int,
        get_process_list=tuple,
    )

    hardcopy_page_user_upper_right = Instrument.control(
        "HCOPy:PAGE:DIMensions:USER:URIGht?",
        "HCOPy:PAGE:DIMensions:USER:URIGht %d,%d",
        """Control the hardcopy P2 page point as (x, y).""",
        values=HARDCOPY_PAGE_POINT_VALUES,
        validator=_validate_int_pair,
        cast=int,
        get_process_list=tuple,
    )

    hardcopy_plot_address = Instrument.control(
        "HCOPy:PLOT:ADDRess?",
        "HCOPy:PLOT:ADDRess %d",
        """Control the GPIB address used for plotter output.""",
        values=[0, 30],
        validator=strict_range,
        cast=int,
    )

    hardcopy_print_address = Instrument.control(
        "HCOPy:PRINt:ADDRess?",
        "HCOPy:PRINt:ADDRess %d",
        """Control the GPIB address used for printer output.""",
        values=[0, 30],
        validator=strict_range,
        cast=int,
    )

    hardcopy_title1 = Instrument.control(
        "HCOPy:TITLe1?",
        "HCOPy:TITLe1 %s",
        """Control the first hardcopy title line.""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    hardcopy_title2 = Instrument.control(
        "HCOPy:TITLe2?",
        "HCOPy:TITLe2 %s",
        """Control the second hardcopy title line.""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    hardcopy_source = Instrument.control(
        "HCOPy:SOURce?",
        "HCOPy:SOURce %s",
        """Control which screen content is selected for hardcopy output.""",
        values=HARDCOPY_SOURCE_VALUES,
        validator=_validate_hardcopy_source,
        get_process=_normalize_hardcopy_source,
        set_process=_normalize_hardcopy_source,
        cast=str,
        maxsplit=0,
    )

    mass_memory_disk_address = Instrument.control(
        "MMEMory:DISK:ADDRess?",
        "MMEMory:DISK:ADDRess %d",
        """Control the GPIB address assigned to the external mass-memory device.""",
        values=[0, 30],
        validator=strict_range,
        cast=int,
    )

    mass_memory_disk_unit = Instrument.control(
        "MMEMory:DISK:UNIT?",
        "MMEMory:DISK:UNIT %d",
        """Control the unit number assigned to the external mass-memory device.""",
        values=[0, 10],
        validator=strict_range,
        cast=int,
    )

    mass_memory_filesystem = Instrument.measurement(
        "MMEMory:FSYStem?",
        """Measure the file-system type of the default mass-memory disk.""",
        cast=str,
        get_process=lambda value: _strip_quotes(str(value)).strip().upper(),
        maxsplit=0,
    )

    mass_memory_default_disk = Instrument.control(
        "MMEMory:MSIS?",
        "MMEMory:MSIS %s",
        """Control the default mass-memory disk selector.""",
        values=(),
        validator=lambda value, values: _normalize_mass_memory_disk(value),
        set_process=_quote_string,
        get_process=lambda value: _normalize_mass_memory_disk(value),
        cast=str,
        maxsplit=0,
    )

    mass_memory_name = Instrument.control(
        "MMEMory:NAME?",
        "MMEMory:NAME %s",
        """Control the default mass-memory file name used by print/plot operations.""",
        cast=str,
        get_process=_strip_quotes,
        set_process=_quote_string,
        maxsplit=0,
    )

    mass_memory_load_continue_status = Instrument.measurement(
        "MMEMory:LOAD:CONTinue?",
        """Measure whether multi-disk mass-memory load continuation is requested.""",
        cast=int,
    )

    mass_memory_store_continue_status = Instrument.measurement(
        "MMEMory:STORe:CONTinue?",
        """Measure whether multi-disk mass-memory store continuation is requested.""",
        cast=int,
    )

    mass_memory_store_program_format = Instrument.control(
        "MMEMory:STORe:PROGram:FORMat?",
        "MMEMory:STORe:PROGram:FORMat %s",
        """Control the file format used for storing Instrument BASIC programs.""",
        values=MASS_MEMORY_STORE_PROGRAM_FORMAT_VALUES,
        validator=lambda value, values: _normalize_mass_memory_program_format(value),
        set_process=lambda value: _normalize_mass_memory_program_format(value),
        get_process=lambda value: _normalize_mass_memory_program_format(value),
        cast=str,
        maxsplit=0,
    )

    mass_memory_store_trace_format = Instrument.control(
        "MMEM:STORe:TRACe:FORMat?",
        "MMEM:STORe:TRACe:FORMat %s",
        """Control the file format used for storing trace files.""",
        values=MASS_MEMORY_STORE_TRACE_FORMAT_VALUES,
        validator=strict_discrete_set,
        cast=str,
        get_process=lambda value: _strip_quotes(str(value)).strip().upper(),
        set_process=lambda value: _strip_quotes(str(value)).strip().upper(),
        maxsplit=0,
    )

    data_format = Instrument.control(
        "FORMat:DATA?",
        "FORMat:DATA %s",
        """Control numeric transfer format for block-data queries and uploads.""",
        values=DATA_FORMAT_VALUES,
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
        preprocess_reply=_normalize_data_format_token,
        maxsplit=0,
    )

    sense_feed = Instrument.control(
        "SENSe:FEED?",
        "SENSe:FEED %s",
        """Control whether measurements use input channels or time-capture data.""",
        values=SENSE_FEED_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    sense_data_frequency_start = Instrument.measurement(
        "SENSe:DATA:HEADer:FREQuency:STARt?",
        """Measure the start frequency metadata for the active time-capture buffer.""",
        cast=float,
    )

    sense_data_frequency_stop = Instrument.measurement(
        "SENSe:DATA:HEADer:FREQuency:STOP?",
        """Measure the stop frequency metadata for the active time-capture buffer.""",
        cast=float,
    )

    frequency_block_size = Instrument.control(
        "SENSe:FREQuency:BLOCksize?",
        "SENSe:FREQuency:BLOCksize %d",
        """Control the real-time data block size in points.""",
        values=[256, 2048],
        validator=strict_range,
        cast=int,
    )

    frequency_center = Instrument.control(
        "SENSe:FREQuency:CENTer?",
        "SENSe:FREQuency:CENTer %g",
        """Control the center frequency in Hz.""",
        values=[0.0234375, 115000.0],
        validator=strict_range,
        cast=float,
    )

    frequency_manual = Instrument.control(
        "SENSe:FREQuency:MANual?",
        "SENSe:FREQuency:MANual %g",
        """Control manual swept-sine frequency in Hz.""",
        values=[0.015625, 51200.0],
        validator=strict_range,
        cast=float,
    )

    frequency_resolution = Instrument.control(
        "SENSe:FREQuency:RESolution?",
        "SENSe:FREQuency:RESolution %g",
        """Control frequency resolution value for active measurement mode.""",
        values=[0.015625, 51200.0],
        validator=strict_range,
        cast=float,
    )

    frequency_resolution_auto_enabled = Instrument.control(
        "SENSe:FREQuency:RESolution:AUTO?",
        "SENSe:FREQuency:RESolution:AUTO %d",
        """Control whether swept-sine automatic resolution is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    frequency_resolution_auto_max_change = Instrument.control(
        "SENSe:FREQuency:RESolution:AUTO:MCHange?",
        "SENSe:FREQuency:RESolution:AUTO:MCHange %g",
        """Control swept-sine maximum auto-resolution response change in percent.""",
        values=[0.00391, 100.0],
        validator=strict_range,
        cast=float,
    )

    frequency_resolution_auto_minimum = Instrument.control(
        "SENSe:FREQuency:RESolution:AUTO:MINimum?",
        "SENSe:FREQuency:RESolution:AUTO:MINimum %g",
        """Control swept-sine minimum automatic resolution value.""",
        values=[0.015625, 51200.0],
        validator=strict_range,
        cast=float,
    )

    frequency_resolution_octave = Instrument.control(
        "SENSe:FREQuency:RESolution:OCTave?",
        "SENSe:FREQuency:RESolution:OCTave %s",
        """Control the octave resolution family.""",
        values=FREQUENCY_RESOLUTION_OCTAVE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    frequency_span = Instrument.control(
        "SENSe:FREQuency:SPAN?",
        "SENSe:FREQuency:SPAN %g",
        """Control the frequency span in Hz.""",
        values=[0.015625, 102400.0],
        validator=strict_range,
        cast=float,
    )

    frequency_span_link = Instrument.control(
        "SENSe:FREQuency:SPAN:LINK?",
        "SENSe:FREQuency:SPAN:LINK %s",
        """Control which frequency reference remains fixed when span changes.""",
        values=FREQUENCY_SPAN_LINK_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    frequency_start = Instrument.control(
        "SENSe:FREQuency:STARt?",
        "SENSe:FREQuency:STARt %g",
        """Control the start frequency in Hz.""",
        values=[0.0, 114999.9023],
        validator=strict_range,
        cast=float,
    )

    frequency_step_increment = Instrument.control(
        "SENSe:FREQuency:STEP:INCRement?",
        "SENSe:FREQuency:STEP:INCRement %g",
        """Control the frequency increment used for manual stepping.""",
        values=[0.015625, 102400.0],
        validator=strict_range,
        cast=float,
    )

    frequency_stop = Instrument.control(
        "SENSe:FREQuency:STOP?",
        "SENSe:FREQuency:STOP %g",
        """Control the stop frequency in Hz.""",
        values=[0.03125, 115000.0],
        validator=strict_range,
        cast=float,
    )

    sweep_direction = Instrument.control(
        "SENSe:SWEep:DIRection?",
        "SENSe:SWEep:DIRection %s",
        """Control swept-sine sweep direction.""",
        values=SWEEP_DIRECTION_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    sweep_dwell = Instrument.control(
        "SENSe:SWEep:DWELl?",
        "SENSe:SWEep:DWELl %g",
        """Control swept-sine integration dwell time.""",
        values=[250e-6, 32768.0],
        validator=strict_range,
        cast=float,
    )

    sweep_mode = Instrument.control(
        "SENSe:SWEep:MODE?",
        "SENSe:SWEep:MODE %s",
        """Control swept-sine sweep mode.""",
        values=SWEEP_MODE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    sweep_overlap = Instrument.control(
        "SENSe:SWEep:OVERlap?",
        "SENSe:SWEep:OVERlap %d",
        """Control maximum overlap percentage between time records.""",
        values=[0, 99],
        validator=strict_range,
        cast=int,
    )

    sweep_spacing = Instrument.control(
        "SENSe:SWEep:SPACing?",
        "SENSe:SWEep:SPACing %s",
        """Control swept-sine point spacing.""",
        values=SWEEP_SPACING_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    sweep_settling_time = Instrument.control(
        "SENSe:SWEep:STIMe?",
        "SENSe:SWEep:STIMe %g",
        """Control swept-sine settling time before integration.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    sweep_time = Instrument.control(
        "SENSe:SWEep:TIME?",
        "SENSe:SWEep:TIME %g",
        """Control time-record length in seconds.""",
        values=[976.5625e-6, 8192.0],
        validator=strict_range,
        cast=float,
    )

    histogram_bins = Instrument.control(
        "SENSe:HISTogram:BINS?",
        "SENSe:HISTogram:BINS %d",
        """Control the number of bins in histogram measurements.""",
        values=[4, 1024],
        validator=strict_range,
        cast=int,
    )

    order_maximum = Instrument.control(
        "SENSe:ORDer:MAXimum?",
        "SENSe:ORDer:MAXimum %g",
        """Control the maximum analyzed order.""",
        values=[3.125, 200.0],
        validator=strict_range,
        cast=float,
    )

    order_resolution = Instrument.control(
        "SENSe:ORDer:RESolution?",
        "SENSe:ORDer:RESolution %g",
        """Control order-spectrum resolution in orders.""",
        values=[0.0078125, 1.0],
        validator=strict_range,
        cast=float,
    )

    order_track_resolution = Instrument.control(
        "SENSe:ORDer:RESolution:TRACk?",
        "SENSe:ORDer:RESolution:TRACk %d",
        """Control points per order track.""",
        values=[1, 2048],
        validator=strict_range,
        cast=int,
    )

    order_rpm_maximum = Instrument.control(
        "SENSe:ORDer:RPM:MAXimum?",
        "SENSe:ORDer:RPM:MAXimum %g",
        """Control maximum RPM for order measurements.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    order_rpm_minimum = Instrument.control(
        "SENSe:ORDer:RPM:MINimum?",
        "SENSe:ORDer:RPM:MINimum %g",
        """Control minimum RPM for order measurements.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    reference_channels = Instrument.control(
        "SENSe:REFerence?",
        "SENSe:REFerence %s",
        """Control reference-channel pairing mode.""",
        values=REFERENCE_CHANNEL_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    overload_rejection_enabled = Instrument.control(
        "SENSe:REJect:STATe?",
        "SENSe:REJect:STATe %d",
        """Control whether overloaded time records are rejected.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    time_capture_length = Instrument.control(
        "SENSe:TCAPture:LENGth?",
        "SENSe:TCAPture:LENGth %g",
        """Control the time-capture buffer length.""",
        values=[0.0, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_start1 = Instrument.control(
        "SENSe:TCAPture:STARt1?",
        "SENSe:TCAPture:STARt1 %g",
        """Control time-capture start position for channel 1.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_start2 = Instrument.control(
        "SENSe:TCAPture:STARt2?",
        "SENSe:TCAPture:STARt2 %g",
        """Control time-capture start position for channel 2.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_start3 = Instrument.control(
        "SENSe:TCAPture:STARt3?",
        "SENSe:TCAPture:STARt3 %g",
        """Control time-capture start position for channel 3.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_start4 = Instrument.control(
        "SENSe:TCAPture:STARt4?",
        "SENSe:TCAPture:STARt4 %g",
        """Control time-capture start position for channel 4.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_stop1 = Instrument.control(
        "SENSe:TCAPture:STOP1?",
        "SENSe:TCAPture:STOP1 %g",
        """Control time-capture stop position for channel 1.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_stop2 = Instrument.control(
        "SENSe:TCAPture:STOP2?",
        "SENSe:TCAPture:STOP2 %g",
        """Control time-capture stop position for channel 2.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_stop3 = Instrument.control(
        "SENSe:TCAPture:STOP3?",
        "SENSe:TCAPture:STOP3 %g",
        """Control time-capture stop position for channel 3.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_stop4 = Instrument.control(
        "SENSe:TCAPture:STOP4?",
        "SENSe:TCAPture:STOP4 %g",
        """Control time-capture stop position for channel 4.""",
        values=[-9.9e37, 9.9e37],
        validator=strict_range,
        cast=float,
    )

    time_capture_tachometer_rpm_maximum = Instrument.control(
        "SENSe:TCAPture:TACHometer:RPM:MAXimum?",
        "SENSe:TCAPture:TACHometer:RPM:MAXimum %g",
        """Control maximum tachometer RPM for time-capture buffering.""",
        values=[5.0, 491519.0],
        validator=strict_range,
        cast=float,
    )

    time_capture_tachometer_enabled = Instrument.control(
        "SENSe:TCAPture:TACHometer:STATe?",
        "SENSe:TCAPture:TACHometer:STATe %d",
        """Control whether tachometer data is included in time capture.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    _installed_options = Instrument.measurement(
        "*OPT?",
        """Get the installed option configuration.""",
        cast=str,
        maxsplit=0,
    )

    _next_system_error = Instrument.measurement(
        "SYSTem:ERRor?",
        """Get the next system error.""",
        cast=str,
        maxsplit=0,
    )

    self_test_result = Instrument.measurement(
        "*TST?",
        """Measure the self-test result.""",
        cast=int,
    )

    long_test_result = Instrument.measurement(
        "TEST:LONG:RESult?",
        """Measure the overall result of the long confidence test.""",
        cast=int,
    )

    event_status_enable = Instrument.control(
        "*ESE?",
        "*ESE %d",
        """Control the Standard Event enable register.""",
        values=[0, 255],
        validator=strict_range,
        cast=int,
    )

    standard_event_status = Instrument.measurement(
        "*ESR?",
        """Measure the Standard Event status register.""",
        cast=int,
    )

    power_on_status_clear = Instrument.control(
        "*PSC?",
        "*PSC %d",
        """Control the Power-on Status Clear flag.""",
        values=[-32767, 32767],
        validator=strict_range,
        cast=int,
    )

    service_request_enable = Instrument.control(
        "*SRE?",
        "*SRE %d",
        """Control the Service Request enable register.""",
        values=[0, 255],
        validator=strict_range,
        cast=int,
    )

    status_byte = Instrument.measurement(
        "*STB?",
        """Measure the status byte register.""",
        cast=int,
    )

    arm_rpm_increment = Instrument.control(
        "ARM:RPM:INCRement?",
        "ARM:RPM:INCRement %g",
        """Control the RPM step increment for RPM-step arming.""",
        values=[1.0, 500000.0],
        validator=strict_range,
        cast=float,
    )

    arm_rpm_mode = Instrument.control(
        "ARM:RPM:MODE?",
        "ARM:RPM:MODE %s",
        """Control the Start RPM arming qualifier mode.""",
        values=ARM_RPM_MODES,
        map_values=True,
        validator=strict_discrete_set,
    )

    arm_rpm_threshold = Instrument.control(
        "ARM:RPM:THReshold?",
        "ARM:RPM:THReshold %g",
        """Control the starting RPM threshold for RPM-step arming.""",
        values=[5.0, 491520.0],
        validator=strict_range,
        cast=float,
    )

    arm_source = Instrument.control(
        "ARM:SOURce?",
        "ARM:SOURce %s",
        """Control the arming source.""",
        values=ARM_SOURCES,
        map_values=True,
        validator=strict_discrete_set,
    )

    arm_timer = Instrument.control(
        "ARM:TIMer?",
        "ARM:TIMer %g",
        """Control the time-step arming interval in seconds.""",
        values=[0.0, 500000.0],
        validator=strict_range,
        cast=float,
    )

    calibration_auto = Instrument.control(
        "CALibration:AUTO?",
        "CALibration:AUTO %s",
        """Control the autocalibration mode.""",
        values={"off": "OFF", "on": "ON", "once": "ONCE"},
        map_values=True,
        validator=strict_discrete_set,
        cast=str,
        get_process=_normalize_on_off_once,
    )

    operation_condition = Instrument.measurement(
        "STATus:OPERation:CONDition?",
        """Measure the operation status condition register.""",
        cast=int,
    )

    questionable_condition = Instrument.measurement(
        "STATus:QUEStionable:CONDition?",
        """Measure the questionable status condition register.""",
        cast=int,
    )

    device_condition = Instrument.measurement(
        "STATus:DEVice:CONDition?",
        """Measure the device status condition register.""",
        cast=int,
    )

    device_enable = Instrument.control(
        "STATus:DEVice:ENABle?",
        "STATus:DEVice:ENABle %d",
        """Control the device status enable register mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    device_event = Instrument.measurement(
        "STATus:DEVice:EVENt?",
        """Measure the device status event register.""",
        cast=int,
    )

    device_negative_transition = Instrument.control(
        "STATus:DEVice:NTRansition?",
        "STATus:DEVice:NTRansition %d",
        """Control the device status negative transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    device_positive_transition = Instrument.control(
        "STATus:DEVice:PTRansition?",
        "STATus:DEVice:PTRansition %d",
        """Control the device status positive transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    operation_enable = Instrument.control(
        "STATus:OPERation:ENABle?",
        "STATus:OPERation:ENABle %d",
        """Control the operation status enable register mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    operation_event = Instrument.measurement(
        "STATus:OPERation:EVENt?",
        """Measure the operation status event register.""",
        cast=int,
    )

    operation_negative_transition = Instrument.control(
        "STATus:OPERation:NTRansition?",
        "STATus:OPERation:NTRansition %d",
        """Control the operation status negative transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    operation_positive_transition = Instrument.control(
        "STATus:OPERation:PTRansition?",
        "STATus:OPERation:PTRansition %d",
        """Control the operation status positive transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_enable = Instrument.control(
        "STATus:QUEStionable:ENABle?",
        "STATus:QUEStionable:ENABle %d",
        """Control the questionable status enable register mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_event = Instrument.measurement(
        "STATus:QUEStionable:EVENt?",
        """Measure the questionable status event register.""",
        cast=int,
    )

    questionable_limit_condition = Instrument.measurement(
        "STATus:QUEStionable:LIMit:CONDition?",
        """Measure the questionable limit condition register.""",
        cast=int,
    )

    questionable_limit_enable = Instrument.control(
        "STATus:QUEStionable:LIMit:ENABle?",
        "STATus:QUEStionable:LIMit:ENABle %d",
        """Control the questionable limit enable register mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_limit_event = Instrument.measurement(
        "STATus:QUEStionable:LIMit:EVENt?",
        """Measure the questionable limit event register.""",
        cast=int,
    )

    questionable_limit_negative_transition = Instrument.control(
        "STATus:QUEStionable:LIMit:NTRansition?",
        "STATus:QUEStionable:LIMit:NTRansition %d",
        """Control the questionable limit negative transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_limit_positive_transition = Instrument.control(
        "STATus:QUEStionable:LIMit:PTRansition?",
        "STATus:QUEStionable:LIMit:PTRansition %d",
        """Control the questionable limit positive transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_negative_transition = Instrument.control(
        "STATus:QUEStionable:NTRansition?",
        "STATus:QUEStionable:NTRansition %d",
        """Control the questionable status negative transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_positive_transition = Instrument.control(
        "STATus:QUEStionable:PTRansition?",
        "STATus:QUEStionable:PTRansition %d",
        """Control the questionable status positive transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_voltage_condition = Instrument.measurement(
        "STATus:QUEStionable:VOLTage:CONDition?",
        """Measure the questionable voltage condition register.""",
        cast=int,
    )

    questionable_voltage_enable = Instrument.control(
        "STATus:QUEStionable:VOLTage:ENABle?",
        "STATus:QUEStionable:VOLTage:ENABle %d",
        """Control the questionable voltage enable register mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_voltage_event = Instrument.measurement(
        "STATus:QUEStionable:VOLTage:EVENt?",
        """Measure the questionable voltage event register.""",
        cast=int,
    )

    questionable_voltage_negative_transition = Instrument.control(
        "STATus:QUEStionable:VOLTage:NTRansition?",
        "STATus:QUEStionable:VOLTage:NTRansition %d",
        """Control the questionable voltage negative transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    questionable_voltage_positive_transition = Instrument.control(
        "STATus:QUEStionable:VOLTage:PTRansition?",
        "STATus:QUEStionable:VOLTage:PTRansition %d",
        """Control the questionable voltage positive transition mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    user_status_enable = Instrument.control(
        "STATus:USER:ENABle?",
        "STATus:USER:ENABle %d",
        """Control the user status enable register mask.""",
        values=STATUS_MASK_VALUES,
        validator=strict_range,
        cast=int,
    )

    user_status_event = Instrument.measurement(
        "STATus:USER:EVENt?",
        """Measure the user status event register.""",
        cast=int,
    )

    beeper_enabled = Instrument.control(
        "SYSTem:BEEPer:STATe?",
        "SYSTem:BEEPer:STATe %d",
        """Control whether the beeper is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    gpib_address = Instrument.control(
        "SYSTem:COMMunicate:GPIB:ADDRess?",
        "SYSTem:COMMunicate:GPIB:ADDRess %d",
        """Control the GPIB address.""",
        values=[0, 30],
        validator=strict_range,
        cast=int,
    )

    serial_receive_baud = Instrument.control(
        "SYSTem:COMMunicate:SERial:RECeive:BAUD?",
        "SYSTem:COMMunicate:SERial:RECeive:BAUD %d",
        """Control the RS-232 receive baud rate.""",
        values=SERIAL_BAUD_RATES,
        validator=strict_discrete_set,
        cast=int,
    )

    serial_receive_bits = Instrument.control(
        "SYSTem:COMMunicate:SERial:RECeive:BITS?",
        "SYSTem:COMMunicate:SERial:RECeive:BITS %d",
        """Control the RS-232 receive bits per character.""",
        values=SERIAL_BITS,
        validator=strict_discrete_set,
        cast=int,
    )

    serial_receive_pace = Instrument.control(
        "SYSTem:COMMunicate:SERial:RECeive:PACE?",
        "SYSTem:COMMunicate:SERial:RECeive:PACE %s",
        """Control the RS-232 receive pacing mode.""",
        values=SERIAL_RECEIVE_PACE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    serial_receive_parity_check_enabled = Instrument.control(
        "SYSTem:COMMunicate:SERial:RECeive:PARity:CHECk?",
        "SYSTem:COMMunicate:SERial:RECeive:PARity:CHECk %d",
        """Control whether RS-232 receive parity checking is enabled.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    serial_receive_parity = Instrument.control(
        "SYSTem:COMMunicate:SERial:RECeive:PARity?",
        "SYSTem:COMMunicate:SERial:RECeive:PARity %s",
        """Control the RS-232 receive parity type.""",
        values=SERIAL_PARITY_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    serial_receive_stop_bits = Instrument.control(
        "SYSTem:COMMunicate:SERial:RECeive:SBITs?",
        "SYSTem:COMMunicate:SERial:RECeive:SBITs %d",
        """Control the RS-232 receive stop bits.""",
        values=SERIAL_STOP_BITS,
        validator=strict_discrete_set,
        cast=int,
    )

    serial_transmit_pace = Instrument.control(
        "SYSTem:COMMunicate:SERial:TRANsmit:PACE?",
        "SYSTem:COMMunicate:SERial:TRANsmit:PACE %s",
        """Control the RS-232 transmit pacing mode.""",
        values=SERIAL_TRANSMIT_PACE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    system_date = Instrument.control(
        "SYSTem:DATE?",
        "SYSTem:DATE %d,%d,%d",
        """Control the system date as (year, month, day).""",
        validator=_validate_int_triplet,
        values=SYSTEM_DATE_VALUES,
        cast=int,
        get_process_list=tuple,
    )

    system_time = Instrument.control(
        "SYSTem:TIME?",
        "SYSTem:TIME %d,%d,%d",
        """Control the system time as (hour, minute, second).""",
        validator=_validate_int_triplet,
        values=SYSTEM_TIME_VALUES,
        cast=int,
        get_process_list=tuple,
    )

    fan_state = Instrument.control(
        "SYSTem:FAN:STATe?",
        "SYSTem:FAN:STATe %s",
        """Control the analyzer fan operating mode.""",
        values=FAN_STATE_VALUES,
        map_values=True,
        validator=strict_discrete_set,
    )

    key_code = Instrument.control(
        "SYSTem:KEY?",
        "SYSTem:KEY %d",
        """Control or query front-panel key codes.""",
        cast=int,
    )

    keyboard_locked = Instrument.control(
        "SYSTem:KLOCk?",
        "SYSTem:KLOCk %d",
        """Control whether the front-panel keyboard is locked.""",
        values=BOOL_VALUES,
        map_values=True,
        cast=int,
        validator=strict_discrete_set,
    )

    key_lock_enabled = keyboard_locked

    power_source = Instrument.measurement(
        "SYSTem:POWer:SOURce?",
        """Measure the active power source.""",
        cast=str,
    )

    power_state = Instrument.measurement(
        "SYSTem:POWer:STATe?",
        """Measure the analyzer power state.""",
        cast=int,
    )

    system_version = Instrument.measurement(
        "SYSTem:VERSion?",
        """Measure the SCPI system version.""",
        cast=str,
    )

    def abort(self) -> None:
        """Abort the measurement in progress."""
        self.write("ABORt")

    def initiate(self) -> None:
        """Initiate a measurement."""
        self.write("INITiate:IMMediate")

    def restart_measurement(self) -> None:
        """Abort and restart a measurement."""
        self.write("ABORt;:INITiate:IMMediate")

    def wait_for_completion(self) -> int:
        """Wait for pending operations to complete."""
        return self.operation_complete()

    def arm(self) -> None:
        """Arm the trigger when manual arming is selected."""
        self.write("ARM:IMMediate")

    def pass_control_back_address(
            self, primary_address: int, secondary_address: Optional[int] = None):
        """Set the pass-control-back address."""
        if secondary_address is None:
            self.write(f"*PCB {int(primary_address)}")
        else:
            self.write(f"*PCB {int(primary_address)}, {int(secondary_address)}")

    def wait(self) -> None:
        """Wait until all preceding commands have been processed."""
        self.write("*WAI")

    def operation_complete(self) -> int:
        """Get the operation-complete synchronization value."""
        return int(self.ask("*OPC?"))

    def trigger_immediate(self) -> None:
        """Trigger immediately when trigger_source is BUS; otherwise this command is ignored."""
        self.write("TRIGger:IMMediate")

    def trigger(self) -> None:
        """Trigger the analyzer."""
        self.write("*TRG")

    def bode(self) -> None:
        """Display a Bode diagram layout."""
        self.write("DISPlay:BODE")

    def display_error(self, text: str) -> None:
        """Display analyzer-style text in the message area."""
        self.write(f"DISPlay:ERRor {_quote_string(str(text))}")

    def hardcopy_color_default(self) -> None:
        """Reset hardcopy color assignments to analyzer defaults."""
        self.write("HCOPy:COLor:DEFault")

    def hardcopy(self, confirmed=False) -> None:
        """Start a hardcopy print or plot operation after explicit confirmation."""
        _require_confirmation("start hardcopy output", confirmed)
        self.write("HCOPy:IMMediate")

    def print_or_plot(self, confirmed=False) -> None:
        """Start a hardcopy print or plot operation after explicit confirmation."""
        self.hardcopy(confirmed=confirmed)

    def define_program(self, text, raw=False) -> None:
        """Define the active Instrument BASIC program from controller-provided block data."""
        block = _encode_program_block(text, raw=raw)
        self.write_bytes(b"PROGram:DEFine " + block)

    def read_program_definition(self, raw=False):
        """Read the active Instrument BASIC program definition as text or raw block bytes."""
        self.write("PROGram:DEFine?")
        reply = self.read_bytes(-1)
        if raw:
            return reply
        return _parse_ascii_or_definite_block_text(reply)

    def define_explicit_program(self, text, program="program1", raw=False) -> None:
        """Define a selected Instrument BASIC program buffer from controller-provided block data."""
        program_selector = _normalize_program_name(program)
        block = _encode_program_block(text, raw=raw)
        prefix = f"PROGram:EXPLicit:DEFine {program_selector},".encode("ascii")
        self.write_bytes(prefix + block)

    def read_explicit_program_definition(self, raw=False):
        """Read an Instrument BASIC program definition via PROGram:EXPLicit:DEFine?."""
        self.write("PROGram:EXPLicit:DEFine?")
        reply = self.read_bytes(-1)
        if raw:
            return reply
        return _parse_ascii_or_definite_block_text(reply)

    def set_explicit_program_label(self, label: str, program="program1") -> None:
        """Set the softkey label for a specific Instrument BASIC program buffer."""
        program_selector = _normalize_program_name(program)
        self.write(f"PROGram:EXPLicit:LABel {program_selector}, {_quote_string(str(label))}")

    def read_explicit_program_label(self):
        """Read the softkey label via PROGram:EXPLicit:LABel?."""
        return _strip_quotes(str(self.ask("PROGram:EXPLicit:LABel?")))

    def delete_all_programs(self, confirmed=False) -> None:
        """Delete all Instrument BASIC programs and variables after explicit confirmation."""
        _require_confirmation("delete all Instrument BASIC programs", confirmed)
        self.write("PROGram:DELete:ALL")

    def delete_selected_program(self, confirmed=False) -> None:
        """Delete the active Instrument BASIC program and variables after explicit confirmation."""
        _require_confirmation("delete selected Instrument BASIC program", confirmed)
        self.write("PROGram:DELete")

    def allocate_program_memory(self, size) -> None:
        """Allocate Instrument BASIC program memory in bytes."""
        token = _strip_quotes(str(size)).strip().upper()
        if token == "DEFAULT":
            self.write("PROGram:MALLocate DEFault")
            return
        if token in {"MAX", "MIN"}:
            self.write(f"PROGram:MALLocate {token}")
            return
        validated = int(strict_range(int(size), [1200, 500000]))
        self.write(f"PROGram:MALLocate {validated}")

    def set_program_number_variable(self, index, value) -> None:
        """Set a numeric Instrument BASIC variable in the active program."""
        variable = _normalize_program_variable_name(index, string_variable=False)
        if isinstance(value, (list, tuple)):
            payload = ",".join(f"{float(item):g}" for item in value)
        else:
            payload = f"{float(value):g}"
        self.write(f"PROGram:NUMBer {_quote_string(variable)}, {payload}")

    def read_program_number_variable(self, index, raw=False):
        """Read a numeric Instrument BASIC variable from the active program."""
        variable = _normalize_program_variable_name(index, string_variable=False)
        self.write(f"PROGram:NUMBer? {_quote_string(variable)}")
        reply = self.read_bytes(-1)
        if raw:
            return reply
        return _parse_ascii_or_definite_block_floats(reply)

    def set_program_string_variable(self, index, value: str) -> None:
        """Set a string Instrument BASIC variable in the active program."""
        variable = _normalize_program_variable_name(index, string_variable=True)
        self.write(
            f"PROGram:STRing {_quote_string(variable)}, {_quote_string(str(value))}"
        )

    def read_program_string_variable(self, index) -> str:
        """Read a string Instrument BASIC variable from the active program."""
        variable = _normalize_program_variable_name(index, string_variable=True)
        return _strip_quotes(str(self.ask(f"PROGram:STRing? {_quote_string(variable)}")))

    def memory_catalog(self, all_entries=False) -> str:
        """Get volatile memory catalog information."""
        command = "MEMory:CATalog:ALL?" if all_entries else "MEMory:CATalog?"
        return str(self.ask(command))

    def memory_catalog_name(self, item) -> str:
        """Get volatile memory allocation information for one item class."""
        selector = _validate_memory_catalog_item(item, MEMORY_CATALOG_ITEM_VALUES)
        return str(self.ask(f"MEMory:CATalog:NAME? {selector}"))

    def memory_free(self, all_entries=False) -> str:
        """Get available and allocated volatile memory information."""
        command = "MEMory:FREE:ALL?" if all_entries else "MEMory:FREE?"
        return str(self.ask(command))

    def memory_delete_all(self, confirmed=False) -> None:
        """Delete all volatile memory allocations after explicit confirmation."""
        _require_confirmation("delete all volatile memory allocations", confirmed)
        self.write("MEMory:DELete:ALL")

    def memory_delete(self, item, confirmed=False) -> None:
        """Delete a volatile memory allocation item after explicit confirmation."""
        _require_confirmation("delete volatile memory allocation item", confirmed)
        selector = _validate_memory_catalog_item(item, MEMORY_CATALOG_ITEM_VALUES)
        self.write(f"MEMory:DELete {selector}")

    def mass_memory_copy(self, source: str, destination: str, confirmed=False) -> None:
        """Copy one mass-memory file or disk target after explicit confirmation."""
        _require_confirmation("copy mass-memory file or disk target", confirmed)
        self.write(f"MMEMory:COPY {_quote_string(source)}, {_quote_string(destination)}")

    def mass_memory_delete(self, path: str, confirmed=False) -> None:
        """Delete a mass-memory file or directory target after explicit confirmation."""
        _require_confirmation("delete mass-memory file or directory target", confirmed)
        self.write(f"MMEMory:DELete {_quote_string(path)}")

    def mass_memory_initialize(
            self, disk: Optional[str] = None, filesystem: Optional[str] = None,
            format_option: Optional[int] = None, interleave_factor: Optional[int] = None,
            confirmed=False) -> None:
        """Initialize a mass-memory disk after explicit confirmation."""
        _require_confirmation("initialize mass-memory disk", confirmed)
        parts = ["MMEMory:INITialize"]
        if disk is not None:
            parts.append(_quote_string(disk))
        if filesystem is not None:
            parts.append(_strip_quotes(str(filesystem)).strip().upper())
        if format_option is not None:
            parts.append(str(int(format_option)))
        if interleave_factor is not None:
            parts.append(str(int(interleave_factor)))
        self.write(" ".join(parts))

    def mass_memory_make_directory(self, directory: str, confirmed=False) -> None:
        """Create a DOS directory on mass memory after explicit confirmation."""
        _require_confirmation("create mass-memory directory", confirmed)
        self.write(f"MMEMory:MDIRectory {_quote_string(directory)}")

    def mass_memory_move(self, source: str, destination: str, confirmed=False) -> None:
        """Rename or move a mass-memory file after explicit confirmation."""
        _require_confirmation("move or rename mass-memory file", confirmed)
        self.write(f"MMEMory:MOVE {_quote_string(source)}, {_quote_string(destination)}")

    def mass_memory_load_continue(self, confirmed=False) -> None:
        """Continue a multi-disk mass-memory load operation after explicit confirmation."""
        _require_confirmation("continue mass-memory load operation", confirmed)
        self.write("MMEMory:LOAD:CONTinue")

    def mass_memory_store_continue(self, confirmed=False) -> None:
        """Continue a multi-disk mass-memory store operation after explicit confirmation."""
        _require_confirmation("continue mass-memory store operation", confirmed)
        self.write("MMEMory:STORe:CONTinue")

    def mass_memory_load_cfit(self, filename: str, confirmed=False) -> None:
        """Load a curve-fit table file after explicit confirmation."""
        _require_confirmation("load curve-fit table from mass memory", confirmed)
        self.write(f"MMEMory:LOAD:CFIT {_quote_string(filename)}")

    def mass_memory_load_data_table_trace(self, trace, filename: str, confirmed=False) -> None:
        """Load a data-table trace file after explicit confirmation."""
        _require_confirmation("load data-table trace from mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:LOAD:DTABle:{trace_selector} {_quote_string(filename)}")

    def mass_memory_load_lower_limit_trace(self, trace, filename: str, confirmed=False) -> None:
        """Load a lower limit-line trace file after explicit confirmation."""
        _require_confirmation("load lower limit trace from mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:LOAD:LIMit:LOWer:{trace_selector} {_quote_string(filename)}")

    def mass_memory_load_upper_limit_trace(self, trace, filename: str, confirmed=False) -> None:
        """Load an upper limit-line trace file after explicit confirmation."""
        _require_confirmation("load upper limit trace from mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:LOAD:LIMit:UPPer:{trace_selector} {_quote_string(filename)}")

    def mass_memory_load_math(self, filename: str, confirmed=False) -> None:
        """Load a math-definition file after explicit confirmation."""
        _require_confirmation("load math definitions from mass memory", confirmed)
        self.write(f"MMEMory:LOAD:MATH {_quote_string(filename)}")

    def mass_memory_load_program(self, filename: str, confirmed=False) -> None:
        """Load an Instrument BASIC program file after explicit confirmation."""
        _require_confirmation("load Instrument BASIC program from mass memory", confirmed)
        self.write(f"MMEMory:LOAD:PROGram {_quote_string(filename)}")

    def mass_memory_load_state(self, filename: str, slot=1, confirmed=False) -> None:
        """Load an instrument state file after explicit confirmation."""
        _require_confirmation("load instrument state from mass memory", confirmed)
        slot_number = int(strict_range(int(slot), [1, 1]))
        self.write(f"MMEMory:LOAD:STATe {slot_number}, {_quote_string(filename)}")

    def mass_memory_load_synthesis(self, filename: str, confirmed=False) -> None:
        """Load a synthesis-table file after explicit confirmation."""
        _require_confirmation("load synthesis table from mass memory", confirmed)
        self.write(f"MMEMory:LOAD:SYNThesis {_quote_string(filename)}")

    def mass_memory_load_time_capture(self, filename: str, confirmed=False) -> None:
        """Load a time-capture file after explicit confirmation."""
        _require_confirmation("load time-capture file from mass memory", confirmed)
        self.write(f"MMEMory:LOAD:TCAPture {_quote_string(filename)}")

    def mass_memory_load_trace(
            self, register, filename: str, no_scale: Optional[bool] = None,
            confirmed=False) -> None:
        """Load a trace register file after explicit confirmation."""
        _require_confirmation("load trace register from mass memory", confirmed)
        register_token = _data_register_selector(register)
        command = f"MMEMory:LOAD:TRACe {register_token}, {_quote_string(filename)}"
        if no_scale is not None:
            command += f", {1 if bool(no_scale) else 0}"
        self.write(command)

    def mass_memory_load_waterfall(self, register, filename: str, confirmed=False) -> None:
        """Load a waterfall register file after explicit confirmation."""
        _require_confirmation("load waterfall register from mass memory", confirmed)
        register_token = _trace_waterfall_register_selector(register)
        self.write(f"MMEMory:LOAD:WATerfall {register_token}, {_quote_string(filename)}")

    def mass_memory_store_cfit(self, filename: str, confirmed=False) -> None:
        """Store a curve-fit table file after explicit confirmation."""
        _require_confirmation("store curve-fit table to mass memory", confirmed)
        self.write(f"MMEMory:STORe:CFIT {_quote_string(filename)}")

    def mass_memory_store_data_table_trace(self, trace, filename: str, confirmed=False) -> None:
        """Store a data-table trace file after explicit confirmation."""
        _require_confirmation("store data-table trace to mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:STORe:DTABle:{trace_selector} {_quote_string(filename)}")

    def mass_memory_store_lower_limit_trace(self, trace, filename: str, confirmed=False) -> None:
        """Store a lower limit-line trace file after explicit confirmation."""
        _require_confirmation("store lower limit trace to mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:STORe:LIMit:LOWer:{trace_selector} {_quote_string(filename)}")

    def mass_memory_store_upper_limit_trace(self, trace, filename: str, confirmed=False) -> None:
        """Store an upper limit-line trace file after explicit confirmation."""
        _require_confirmation("store upper limit trace to mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:STORe:LIMit:UPPer:{trace_selector} {_quote_string(filename)}")

    def mass_memory_store_math(self, filename: str, confirmed=False) -> None:
        """Store a math-definition file after explicit confirmation."""
        _require_confirmation("store math definitions to mass memory", confirmed)
        self.write(f"MMEMory:STORe:MATH {_quote_string(filename)}")

    def mass_memory_store_program(self, filename: str, confirmed=False) -> None:
        """Store an Instrument BASIC program file after explicit confirmation."""
        _require_confirmation("store Instrument BASIC program to mass memory", confirmed)
        self.write(f"MMEMory:STORe:PROGram {_quote_string(filename)}")

    def mass_memory_store_state(self, filename: str, slot=1, confirmed=False) -> None:
        """Store an instrument state file after explicit confirmation."""
        _require_confirmation("store instrument state to mass memory", confirmed)
        slot_number = int(strict_range(int(slot), [1, 1]))
        self.write(f"MMEMory:STORe:STATe {slot_number}, {_quote_string(filename)}")

    def mass_memory_store_synthesis(self, filename: str, confirmed=False) -> None:
        """Store a synthesis-table file after explicit confirmation."""
        _require_confirmation("store synthesis table to mass memory", confirmed)
        self.write(f"MMEMory:STORe:SYNThesis {_quote_string(filename)}")

    def mass_memory_store_time_capture(self, filename: str, confirmed=False) -> None:
        """Store a time-capture file after explicit confirmation."""
        _require_confirmation("store time-capture file to mass memory", confirmed)
        self.write(f"MMEMory:STORe:TCAPture {_quote_string(filename)}")

    def mass_memory_store_trace(self, trace, filename: str, confirmed=False) -> None:
        """Store a trace file after explicit confirmation."""
        _require_confirmation("store trace file to mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:STORe:TRACe {trace_selector}, {_quote_string(filename)}")

    def mass_memory_store_waterfall(self, trace, filename: str, confirmed=False) -> None:
        """Store a waterfall display file after explicit confirmation."""
        _require_confirmation("store waterfall file to mass memory", confirmed)
        trace_selector = _normalize_mass_memory_trace_selector(trace)
        self.write(f"MMEMory:STORe:WATerfall {trace_selector}, {_quote_string(filename)}")

    def program_key_box(self, key_number: int, enabled: Optional[bool] = None) -> Optional[bool]:
        """Control or query a boxed softkey indicator for Instrument BASIC output."""
        key = int(strict_range(int(key_number), [0, 8]))
        if enabled is None:
            values = _parse_ascii_ints(self.ask(f"DISPlay:PROGram:KEY:BOX? {key}"))
            if not values:
                raise ValueError("Program key box query returned no values.")
            return bool(values[-1])

        state = int(strict_discrete_set(bool(enabled), BOOL_VALUES))
        self.write(f"DISPlay:PROGram:KEY:BOX {key},{state}")
        return None

    def program_key_bracket(
            self, first_key_number: int, last_key_number: int,
            enabled: Optional[bool] = None) -> Optional[bool]:
        """Control or query a bracket indicator spanning a softkey range."""
        first = int(strict_range(int(first_key_number), [0, 8]))
        last = int(strict_range(int(last_key_number), [0, 8]))
        if enabled is None:
            values = _parse_ascii_ints(
                self.ask(f"DISPlay:PROGram:KEY:BRACket? {first},{last}")
            )
            if not values:
                raise ValueError("Program key bracket query returned no values.")
            return bool(values[-1])

        state = int(strict_discrete_set(bool(enabled), BOOL_VALUES))
        self.write(f"DISPlay:PROGram:KEY:BRACket {first},{last},{state}")
        return None

    def status_preset(self) -> None:
        """Preset the status register masks."""
        self.write("STATus:PRESet")

    def pulse_user_status(self, mask: int) -> None:
        """Pulse selected bits in the user status condition register."""
        validated_mask = strict_range(mask, STATUS_MASK_VALUES)
        self.write(f"STATus:USER:PULSe {int(validated_mask)}")

    def user_status_pulse(self, mask: int) -> None:
        """Pulse selected bits in the user status condition register."""
        self.pulse_user_status(mask)

    def beep(self) -> None:
        """Sound the beeper."""
        self.write("SYSTem:BEEPer:IMMediate")

    def clear_fault_log(self, confirmed=False) -> None:
        """Clear the analyzer fault log after explicit confirmation."""
        _require_confirmation("clear fault log", confirmed)
        self.write("SYSTem:FLOG:CLEar")

    def clear_test_log(self, confirmed=False) -> None:
        """Clear the long confidence test log after explicit confirmation."""
        _require_confirmation("clear test log", confirmed)
        self.write("TEST:LOG:CLEar")

    def run_long_test(self, confirmed=False) -> None:
        """Run the long confidence test after explicit confirmation."""
        _require_confirmation("run long confidence test", confirmed)
        self.write("TEST:LONG")

    def power_off(self, confirmed=False) -> None:
        """Turn off analyzer power after explicit confirmation."""
        _require_confirmation("power off", confirmed)
        self.write("SYSTem:POWer:STATe OFF")

    def system_preset(self, confirmed=False) -> None:
        """Preset the analyzer system state after explicit confirmation."""
        _require_confirmation("system preset", confirmed)
        self.write("SYSTem:PRESet")

    def system_state_data(self, raw=False) -> bytes:
        """Read system state block data."""
        self.write("SYSTem:SET?")
        block = self.read_bytes(-1)
        if raw:
            return block
        return _parse_definite_block(block)

    def load_system_state(self, data, raw=False) -> None:
        """Load system state block data."""
        payload = _coerce_bytes(data)
        block = payload if raw else _encode_definite_block(payload)
        self.write_bytes(b"SYSTem:SET " + block)

    def run_self_calibration(self, confirmed=False) -> int:
        """Run full self-calibration and return the result code."""
        _require_confirmation("run self calibration", confirmed)
        return int(self.ask("*CAL?"))

    def run_calibration(self, confirmed=False) -> int:
        """Run CALibration:ALL and return the result code."""
        _require_confirmation("run full calibration", confirmed)
        return int(self.ask("CALibration:ALL?"))

    def accept_average_preview(self) -> None:
        """Accept the current time record during preview averaging."""
        self.write("SENSe:AVERage:PREView:ACCept")

    def reject_average_preview(self) -> None:
        """Reject the current time record during preview averaging."""
        self.write("SENSe:AVERage:PREView:REJect")

    def abort_time_capture(self) -> None:
        """Abort the time-capture acquisition process."""
        self.write("SENSe:TCAPture:ABORt")

    def delete_time_capture(self, confirmed=False) -> None:
        """Delete the time-capture buffer after explicit confirmation."""
        _require_confirmation("delete time capture buffer", confirmed)
        self.write("SENSe:TCAPture:DELete")

    def time_capture_file(self, raw=False) -> bytes:
        """Read the time-capture SDF file transfer block."""
        self.write("SENSe:TCAPture:FILE?")
        block = self.read_bytes(-1)
        if raw:
            return block
        return _parse_definite_block(block)

    def load_time_capture_file(self, data, raw=False) -> None:
        """Load a time-capture SDF file transfer block."""
        payload = _coerce_bytes(data)
        block = payload if raw else _encode_definite_block(payload)
        self.write_bytes(b"SENSe:TCAPture:FILE " + block)

    def start_time_capture(self) -> None:
        """Start time-capture data acquisition."""
        self.write("SENSe:TCAPture:IMMediate")

    def allocate_time_capture_memory(self) -> None:
        """Allocate memory for the time-capture buffer."""
        self.write("SENSe:TCAPture:MALLocate")

    def sense_data(self, capture_channel=1, raw=False) -> bytes:
        """Read time-capture data block from the selected capture channel."""
        selector = _tcap_selector(capture_channel)
        self.write(f"SENSe:DATA? {selector}")
        block = self.read_bytes(-1)
        if raw:
            return block
        return _parse_definite_block(block)

    def set_sense_data(self, data, capture_channel=1, raw=False) -> None:
        """Write time-capture data block to the selected capture channel."""
        selector = _tcap_selector(capture_channel)
        payload = _coerce_bytes(data)
        block = payload if raw else _encode_definite_block(payload)
        prefix = f"SENSe:DATA {selector},".encode("ascii")
        self.write_bytes(prefix + block)

    def sense_data_points(self, capture_channel=1) -> int:
        """Measure the number of points available in a time-capture buffer."""
        selector = _tcap_selector(capture_channel)
        return int(self.ask(f"SENSe:DATA:HEADer:POINts? {selector}"))

    def sense_data_range(self, capture_channel=1) -> float:
        """Measure the configured range metadata for a time-capture buffer."""
        selector = _tcap_selector(capture_channel)
        return float(self.ask(f"SENSe:DATA:RANGe? {selector}"))

    def set_sense_data_range(self, capture_channel, value) -> None:
        """Set range metadata for a time-capture buffer before data upload."""
        selector = _tcap_selector(capture_channel)
        validated = strict_range(float(value), DATA_RANGE_VALUES)
        self.write(f"SENSe:DATA:RANGe {selector}, {validated:g}")

    def set_full_frequency_span(self) -> None:
        """Set frequency span to full range for the active mode."""
        self.write("SENSe:FREQuency:SPAN:FULL")

    def read_trace_raw_data(self, register=None, raw=False):
        """Read data from a TRACe data register as parsed values or raw bytes."""
        selector = _trace_data_register_selector(1 if register is None else register)
        command = f"TRACe:DATA? {selector}"
        if raw:
            self.write(command)
            return self.read_bytes(-1)
        return _parse_ascii_or_definite_block_floats(self.ask(command))

    def write_trace_raw_data(self, data, register=None, raw=False) -> None:
        """Write data to a TRACe data register using ASCII or block payloads."""
        selector = _trace_data_register_selector(1 if register is None else register)
        prefix = f"TRACe:DATA {selector},"

        if raw:
            payload = _coerce_bytes(data)
            self.write_bytes(prefix.encode("ascii") + payload)
            return

        if isinstance(data, (bytes, bytearray)):
            block = _encode_definite_block(bytes(data))
            self.write_bytes(prefix.encode("ascii") + block)
            return

        if isinstance(data, str):
            self.write(f"{prefix} {data}")
            return

        if isinstance(data, (list, tuple)):
            values = ",".join(f"{float(item):g}" for item in data)
            self.write(f"{prefix} {values}")
            return

        if isinstance(data, (int, float)):
            self.write(f"{prefix} {data:g}")
            return

        raise TypeError("Trace data must be bytes, str, sequence, int, or float.")

    def read_trace_x_data(self, raw=False):
        """Read X-axis values for trace displays."""
        if raw:
            self.write("TRACe:X:DATA?")
            return self.read_bytes(-1)
        return _parse_ascii_or_definite_block_floats(self.ask("TRACe:X:DATA?"))

    def read_trace_x_unit(self) -> str:
        """Read the X-axis unit token for trace displays."""
        return _strip_quotes(str(self.ask("TRACe:X:UNIT?")).strip())

    def read_trace_z_data(self, raw=False):
        """Read Z-axis values for waterfall displays."""
        if raw:
            self.write("TRACe:Z:DATA?")
            return self.read_bytes(-1)
        return _parse_ascii_or_definite_block_floats(self.ask("TRACe:Z:DATA?"))

    def read_trace_z_unit(self) -> str:
        """Read the Z-axis unit token for waterfall displays."""
        return _strip_quotes(str(self.ask("TRACe:Z:UNIT?")).strip())

    def read_trace_waterfall_data(self, raw=False):
        """Read data from the active waterfall register set."""
        if raw:
            self.write("TRACe:WATerfall:DATA?")
            return self.read_bytes(-1)
        return _parse_ascii_or_definite_block_floats(self.ask("TRACe:WATerfall:DATA?"))

    def write_trace_waterfall_data(self, data, register=None, raw=False) -> None:
        """Write data to a TRACe waterfall register using ASCII or block payloads."""
        selector = _trace_waterfall_register_selector(1 if register is None else register)
        prefix = f"TRACe:WATerfall:DATA {selector},"

        if raw:
            payload = _coerce_bytes(data)
            self.write_bytes(prefix.encode("ascii") + payload)
            return

        if isinstance(data, (bytes, bytearray)):
            block = _encode_definite_block(bytes(data))
            self.write_bytes(prefix.encode("ascii") + block)
            return

        if isinstance(data, str):
            self.write(f"{prefix} {data}")
            return

        if isinstance(data, (list, tuple)):
            values = ",".join(f"{float(item):g}" for item in data)
            self.write(f"{prefix} {values}")
            return

        if isinstance(data, (int, float)):
            self.write(f"{prefix} {data:g}")
            return

        raise TypeError("Waterfall data must be bytes, str, sequence, int, or float.")

    def trace_data(self, trace=1) -> list[float]:
        """Read trace data from a data register (compatibility wrapper)."""
        return self.read_trace_raw_data(register=trace, raw=False)

    def trace_x_data(self, trace=1) -> list[float]:
        """Read trace X-axis data (compatibility wrapper)."""
        del trace
        return self.read_trace_x_data(raw=False)

    def trace_z_data(self, trace=1) -> list[float]:
        """Read trace Z-axis data (compatibility wrapper)."""
        del trace
        return self.read_trace_z_data(raw=False)

    def trace_x_unit(self, trace=1) -> str:
        """Read trace X-axis unit (compatibility wrapper)."""
        del trace
        return self.read_trace_x_unit()

    def trace_z_unit(self, trace=1) -> str:
        """Read trace Z-axis unit (compatibility wrapper)."""
        del trace
        return self.read_trace_z_unit()

    def options(self) -> str:
        """Get the installed option configuration."""
        return self._installed_options

    def system_error(self) -> str:
        """Get the next system error."""
        return self._next_system_error

    def _raise_if_errors(self, max_errors=10) -> None:
        """Raise runtime errors if the system error queue contains failures."""
        if max_errors < 1:
            raise ValueError("max_errors must be >= 1.")

        errors = []
        for _ in range(max_errors):
            reply = self.ask("SYSTem:ERRor?")
            tokens = _parse_csv_strings(reply)
            if not tokens:
                break
            code_token = tokens[0]
            try:
                code = int(code_token)
            except ValueError:
                try:
                    code = int(float(code_token))
                except ValueError:
                    code = None

            message = ",".join(tokens[1:]).strip() if len(tokens) > 1 else ""
            if code == 0 and "NO ERROR" in message.upper():
                break

            errors.append(reply)

        if errors:
            raise RuntimeError(f"Instrument error queue is not empty: {errors}")

    def drain_errors(self, max_errors=10) -> None:
        """Drain the error queue and raise if any error is reported."""
        self._raise_if_errors(max_errors=max_errors)

    def check_id(self) -> None:
        """Check that the connected instrument is a 35670A."""
        idn = self.id
        parts = [part.strip() for part in idn.split(",")]
        if len(parts) < 2:
            raise ValueError(f"Unexpected instrument IDN response: '{idn}'.")

        manufacturer = parts[0].upper()
        model = parts[1].upper()

        accepted_manufacturers = ("HEWLETT-PACKARD", "HP", "AGILENT", "KEYSIGHT")
        is_supported_manufacturer = any(
            token in manufacturer for token in accepted_manufacturers
        )
        is_supported_model = model == "35670A"

        if not (is_supported_manufacturer and is_supported_model):
            raise ValueError(
                f"Instrument ID '{idn}' is not a supported 35670A "
                "from Hewlett-Packard, HP, Agilent, or Keysight."
            )
