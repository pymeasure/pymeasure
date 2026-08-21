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

from pymeasure.instruments import AdapterType, Channel, Instrument
from pymeasure.instruments.common_base import cast_or_str
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set

COMMON_PROBE_ATTENUATIONS = [
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

COMMON_MEMORY_DEPTHS = [
    "AUTO",
    1_000,
    10_000,
    100_000,
    1_000_000,
    10_000_000,
    25_000_000,
    50_000_000,
]

TRIGGER_MODES = [
    "EDGE",
    "PULS",
    "SLOP",
    "VID",
    "PATT",
    "DUR",
    "TIM",
    "RUNT",
    "WIND",
    "DEL",
    "SET",
    "NEDG",
    "RS232",
    "IIC",
    "SPI",
    "CAN",
    "FLEX",
    "LIN",
    "IIS",
    "M1553",
]


def _parse_ieee_block(
    response: bytes, data_name: str, *, require_terminator: bool = False
) -> bytes:
    """Remove and validate the definite-length IEEE block framing.

    :param response: Complete response including the IEEE block framing.
    :param data_name: Human-readable name used in validation errors.
    :param require_terminator: Whether the response must end with a newline.
    """
    if len(response) < 2 or response[:1] != b"#" or not response[1:2].isdigit():
        raise ValueError(f"{data_name} does not start with an IEEE block header.")
    digit_count = int(response[1:2])
    header_end = 2 + digit_count
    if digit_count == 0 or len(response) < header_end or not response[2:header_end].isdigit():
        raise ValueError(f"{data_name} contains an invalid IEEE block header.")
    byte_count = int(response[2:header_end])
    payload_end = header_end + byte_count
    payload = response[header_end:payload_end]
    if len(payload) != byte_count:
        raise ValueError(f"{data_name} declares {byte_count} data bytes, received {len(payload)}.")
    trailing_data = response[payload_end:]
    if trailing_data not in (b"", b"\n") or (require_terminator and trailing_data != b"\n"):
        raise ValueError(f"{data_name} contains data beyond its declared IEEE block length.")
    return payload


class RigolOscilloscopeChannel(Channel):
    """Represent the common analog-channel interface of Rigol oscilloscopes."""

    bandwidth_limit = Channel.control(
        ":CHAN{ch}:BWL?",
        ":CHAN{ch}:BWL %s",
        """Control the bandwidth limit (str, model-dependent discrete values).""",
        validator=strict_discrete_set,
        values=["OFF", "20M"],
        cast=str,
        dynamic=True,
    )

    coupling = Channel.control(
        ":CHAN{ch}:COUP?",
        ":CHAN{ch}:COUP %s",
        """Control the input coupling: ``"AC"``, ``"DC"``, or ``"GND"``.""",
        validator=strict_discrete_set,
        values=["AC", "DC", "GND"],
        cast=str,
    )

    display_enabled = Channel.control(
        ":CHAN{ch}:DISP?",
        ":CHAN{ch}:DISP %d",
        """Control whether the channel is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    invert = Channel.control(
        ":CHAN{ch}:INV?",
        ":CHAN{ch}:INV %d",
        """Control whether the displayed waveform is inverted (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    offset = Channel.control(
        ":CHAN{ch}:OFFS?",
        ":CHAN{ch}:OFFS %g",
        """Control the vertical offset in Volts (float, model- and scale-dependent).""",
    )

    scale = Channel.control(
        ":CHAN{ch}:SCAL?",
        ":CHAN{ch}:SCAL %g",
        """Control the vertical scale in Volts per division (float, model-dependent).""",
        dynamic=True,
    )

    probe = Channel.control(
        ":CHAN{ch}:PROB?",
        ":CHAN{ch}:PROB %g",
        """Control the probe attenuation ratio (float, model-dependent discrete values).""",
        validator=strict_discrete_set,
        values=COMMON_PROBE_ATTENUATIONS,
        dynamic=True,
    )

    units = Channel.control(
        ":CHAN{ch}:UNIT?",
        ":CHAN{ch}:UNIT %s",
        """Control the amplitude display unit: ``"VOLT"``, ``"WATT"``, ``"AMP"``, or
        ``"UNKN"``.
        """,
        validator=strict_discrete_set,
        values=["VOLT", "WATT", "AMP", "UNKN"],
        cast=str,
    )


class RigolOscilloscope(SCPIMixin, Instrument):
    """Provide the SCPI core shared by supported Rigol oscilloscope families.

    :param adapter: Adapter object or resource identifier used for communication.
    :param name: Name of the instrument.
    :param kwargs: Additional arguments passed to :class:`~pymeasure.adapters.VISAAdapter` when
        ``adapter`` is a string or integer; discarded when it is an Adapter object.
    """

    def __init__(self, adapter: AdapterType, name: str = "Rigol oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)

    acquisition_averages = Instrument.control(
        ":ACQ:AVER?",
        ":ACQ:AVER %d",
        """Control the number of acquisition averages (power of two from 2 to 65536).""",
        validator=strict_discrete_set,
        values=[2**power for power in range(1, 17)],
        cast=int,
    )

    acquisition_memory_depth = Instrument.control(
        ":ACQ:MDEP?",
        ":ACQ:MDEP %s",
        """Control the acquisition memory depth (``"AUTO"`` or model-dependent int).""",
        validator=strict_discrete_set,
        values=COMMON_MEMORY_DEPTHS,
        cast=cast_or_str(float),
        dynamic=True,
    )

    acquisition_type = Instrument.control(
        ":ACQ:TYPE?",
        ":ACQ:TYPE %s",
        """Control the acquisition type (str, model-dependent discrete values).""",
        validator=strict_discrete_set,
        values=["NORM", "AVER", "PEAK"],
        cast=str,
        dynamic=True,
    )

    sample_rate = Instrument.measurement(
        ":ACQ:SRAT?",
        """Measure the current sample rate in samples per second (float).""",
    )

    timebase_offset = Instrument.control(
        ":TIM:MAIN:OFFS?",
        ":TIM:MAIN:OFFS %g",
        """Control the main timebase offset in seconds (float, state-dependent).""",
    )

    timebase_scale = Instrument.control(
        ":TIM:MAIN:SCAL?",
        ":TIM:MAIN:SCAL %g",
        """Control the main timebase scale in seconds per division (float, model-dependent).""",
        dynamic=True,
    )

    timebase_mode = Instrument.control(
        ":TIM:MODE?",
        ":TIM:MODE %s",
        """Control the timebase mode: ``"MAIN"``, ``"XY"``, or ``"ROLL"``.""",
        validator=strict_discrete_set,
        values=["MAIN", "XY", "ROLL"],
        cast=str,
    )

    trigger_mode = Instrument.control(
        ":TRIG:MODE?",
        ":TRIG:MODE %s",
        """Control the trigger mode (str, model- and option-dependent).""",
        validator=strict_discrete_set,
        values=TRIGGER_MODES,
        cast=str,
        dynamic=True,
    )

    trigger_coupling = Instrument.control(
        ":TRIG:COUP?",
        ":TRIG:COUP %s",
        """Control Edge-trigger coupling: ``"AC"``, ``"DC"``, ``"LFR"``, or ``"HFR"``.""",
        validator=strict_discrete_set,
        values=["AC", "DC", "LFR", "HFR"],
        cast=str,
    )

    trigger_status = Instrument.measurement(
        ":TRIG:STAT?",
        """Measure the trigger status: ``"TD"``, ``"WAIT"``, ``"RUN"``, ``"AUTO"``, or
        ``"STOP"``.
        """,
        cast=str,
    )

    trigger_sweep = Instrument.control(
        ":TRIG:SWE?",
        ":TRIG:SWE %s",
        """Control the trigger sweep: ``"AUTO"``, ``"NORM"``, or ``"SING"``.""",
        validator=strict_discrete_set,
        values=["AUTO", "NORM", "SING"],
        cast=str,
    )

    trigger_holdoff = Instrument.control(
        ":TRIG:HOLD?",
        ":TRIG:HOLD %g",
        """Control the trigger holdoff time in seconds (float, model-dependent).""",
        dynamic=True,
    )

    edge_trigger_source = Instrument.control(
        ":TRIG:EDGE:SOUR?",
        ":TRIG:EDGE:SOUR %s",
        """Control the Edge-trigger source (str, model-dependent discrete values).""",
        validator=strict_discrete_set,
        values=["CHAN1", "CHAN2", "CHAN3", "CHAN4"],
        cast=str,
        dynamic=True,
    )

    edge_trigger_slope = Instrument.control(
        ":TRIG:EDGE:SLOP?",
        ":TRIG:EDGE:SLOP %s",
        """Control the Edge-trigger slope: ``"POS"``, ``"NEG"``, or ``"RFAL"``.""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "RFAL"],
        cast=str,
    )

    edge_trigger_level = Instrument.control(
        ":TRIG:EDGE:LEV?",
        ":TRIG:EDGE:LEV %g",
        """Control the Edge-trigger level (float, source-dependent).""",
    )

    waveform_source = Instrument.control(
        ":WAV:SOUR?",
        ":WAV:SOUR %s",
        """Control the source used for waveform reads (str, model-dependent).""",
        validator=strict_discrete_set,
        values=["CHAN1", "CHAN2", "CHAN3", "CHAN4"],
        cast=str,
        dynamic=True,
    )

    waveform_mode = Instrument.control(
        ":WAV:MODE?",
        ":WAV:MODE %s",
        """Control the waveform reading mode: ``"NORM"``, ``"MAX"``, or ``"RAW"``.""",
        validator=strict_discrete_set,
        values=["NORM", "MAX", "RAW"],
        cast=str,
    )

    waveform_format = Instrument.control(
        ":WAV:FORM?",
        ":WAV:FORM %s",
        """Control the waveform return format: ``"WORD"``, ``"BYTE"``, or ``"ASC"``.""",
        validator=strict_discrete_set,
        values=["WORD", "BYTE", "ASC"],
        cast=str,
    )

    waveform_start = Instrument.control(
        ":WAV:STAR?",
        ":WAV:STAR %d",
        """Control the first waveform point to read (int, mode-dependent).""",
        cast=int,
    )

    waveform_stop = Instrument.control(
        ":WAV:STOP?",
        ":WAV:STOP %d",
        """Control the last waveform point to read (int, mode-dependent).""",
        cast=int,
    )

    waveform_x_increment = Instrument.measurement(
        ":WAV:XINC?",
        """Measure the interval between adjacent waveform points (float).""",
    )

    waveform_x_origin = Instrument.measurement(
        ":WAV:XOR?",
        """Measure the waveform start time on the X axis (float).""",
    )

    waveform_x_reference = Instrument.measurement(
        ":WAV:XREF?",
        """Measure the waveform reference point on the X axis (float).""",
    )

    waveform_y_increment = Instrument.measurement(
        ":WAV:YINC?",
        """Measure the waveform step value on the Y axis (float).""",
    )

    waveform_y_origin = Instrument.measurement(
        ":WAV:YOR?",
        """Measure the waveform vertical origin (float).""",
    )

    waveform_y_reference = Instrument.measurement(
        ":WAV:YREF?",
        """Measure the waveform vertical reference position (float).""",
    )

    def _query_waveform_preamble(self) -> dict[str, int | float]:
        """Return the ten common waveform scaling parameters."""
        values = self.ask(":WAV:PRE?").strip().split(",")
        if len(values) != 10:
            raise ValueError(f"Expected 10 waveform preamble values, received {len(values)}.")
        return {
            "format": int(values[0]),
            "type": int(values[1]),
            "points": int(values[2]),
            "count": int(values[3]),
            "x_increment": float(values[4]),
            "x_origin": float(values[5]),
            "x_reference": float(values[6]),
            "y_increment": float(values[7]),
            "y_origin": int(values[8]),
            "y_reference": int(values[9]),
        }

    def _read_ieee_block(self, data_name: str) -> bytes:
        """Read and validate a definite-length IEEE block."""
        response = self.read_bytes(2)
        if len(response) != 2 or response[:1] != b"#" or not response[1:2].isdigit():
            return _parse_ieee_block(response, data_name, require_terminator=True)

        digit_count = int(response[1:2])
        if digit_count == 0:
            return _parse_ieee_block(response, data_name, require_terminator=True)

        length = self.read_bytes(digit_count)
        response += length
        if len(length) != digit_count or not length.isdigit():
            return _parse_ieee_block(response, data_name, require_terminator=True)

        byte_count = int(length)
        payload = self.read_bytes(byte_count)
        response += payload
        if len(payload) != byte_count:
            return _parse_ieee_block(response, data_name, require_terminator=True)

        response += self.read_bytes(1)
        return _parse_ieee_block(response, data_name, require_terminator=True)

    def run(self) -> None:
        """Start continuous acquisition."""
        self.write(":RUN")

    def stop(self) -> None:
        """Stop acquisition."""
        self.write(":STOP")

    def single(self) -> None:
        """Select single trigger mode."""
        self.write(":SING")

    def force_trigger(self) -> None:
        """Generate a trigger in normal or single trigger mode."""
        self.write(":TFOR")
