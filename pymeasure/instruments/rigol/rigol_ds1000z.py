#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to do so, subject to the
# following conditions:
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
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


_ANALOG_SOURCES: Tuple[str, ...] = ("CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH")
_DIGITAL_SOURCES: Tuple[str, ...] = tuple(f"D{idx}" for idx in range(16))
_WAVEFORM_SOURCES: Tuple[str, ...] = _ANALOG_SOURCES + _DIGITAL_SOURCES
_MEMORY_DEPTH_VALUES: Tuple[int, ...] = (
    3000,
    6000,
    12000,
    30000,
    60000,
    120000,
    300000,
    600000,
    1200000,
    3000000,
    6000000,
    12000000,
    24000000,
)
_ANALOG_MEMORY_DEPTH_OPTIONS: Dict[int, Set[int]] = {
    0: set(_MEMORY_DEPTH_VALUES),
    1: {12000, 120000, 1200000, 12000000, 24000000},
    2: {6000, 60000, 600000, 6000000, 12000000},
    3: {3000, 30000, 300000, 3000000, 6000000},
    4: {3000, 30000, 300000, 3000000, 6000000},
}
_DIGITAL_MEMORY_DEPTH_OPTIONS: Dict[int, Set[int]] = {
    0: set(_MEMORY_DEPTH_VALUES),
    8: {12000, 120000, 1200000, 12000000, 24000000},
    16: {6000, 60000, 600000, 6000000, 12000000},
}


class AcquireType(str, Enum):
    """Supported acquisition types for the scope."""
    # In this mode, the oscilloscope samples the signal at equal time interval to rebuild the
    # waveform. For most of the waveforms, the best display effect can be obtained using this mode.
    NORMAL = "NORM"
    # In this mode, the oscilloscope averages the waveforms from multiple samples to reduce the
    # random noise of the input signal and improve the vertical resolution. The number of averages
    # can be set by the `average_count` property. Greater number of averages can lower the noise
    # and increase the vertical resolution, but will also slow the response of the displayed
    # waveform to the waveform changes.
    AVERAGE = "AVER"
    # In this mode, the oscilloscope acquires the maximum and minimum values of the signal within
    # the sample interval to get the envelope of the signal or the narrow pulse of the signal
    # that might be lost. In this mode, signal confusion can be prevented but the noise displayed
    # would be larger.
    PEAK = "PEAK"
    # This mode uses a kind of ultra-sample technique to average the neighboring points of the
    # sample waveform to reduce the random noise on the input signal and generate much smoother
    # waveforms on the screen. This is generally used when the sample rate of the digital
    # converter is higher than the storage rate of the acquisition memory.
    HIGH_RESOLUTION = "HRES"


class WaveformMode(str, Enum):
    """Waveform acquisition modes supported by the scope."""
    NORMAL = "NORM"
    MAXIMUM = "MAX"
    RAW = "RAW"


class WaveformFormat(str, Enum):
    """Waveform data formats supported by the scope."""
    BYTE = "BYTE"
    WORD = "WORD"
    ASCII = "ASC"


# Display enums

class DisplayType(str, Enum):
    VECTORS = "VECT"
    DOTS = "DOTS"


class DisplayGrid(str, Enum):
    FULL = "FULL"
    HALF = "HALF"
    NONE = "NONE"


class DisplayImageFormat(str, Enum):
    BMP24 = "BMP24"
    BMP8 = "BMP8"
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"


def _parse_waveform_preamble(reply: str) -> Dict[str, Union[int, float]]:
    """Parse the `:WAV:PRE?` reply into a structured dictionary."""

    fields = reply.strip().split(",")
    if len(fields) != 10:
        raise RuntimeError(f"Unexpected waveform preamble: {reply!r}")

    fmt_code, acquisition_type, points, averages = map(int, fields[:4])
    (x_increment, x_origin, x_reference,
     y_increment, y_origin, y_reference) = map(float, fields[4:])

    return {
        "format_code": fmt_code,
        "acquisition_type": acquisition_type,
        "points": points,
        "averages": averages,
        "x_increment": x_increment,
        "x_origin": x_origin,
        "x_reference": x_reference,
        "y_increment": y_increment,
        "y_origin": y_origin,
        "y_reference": y_reference,
    }


def _parse_tmc_block(read_bytes_func) -> bytes:
    """Read and return the payload of a SCPI binary block (#Nxxxx...payload)."""
    header = read_bytes_func(2)
    if len(header) != 2 or not header.startswith(b"#"):
        raise RuntimeError("Invalid binary block header for display data.")
    length_digits = int(header[1:2].decode("ascii"))
    length = int(read_bytes_func(length_digits).decode("ascii"))
    payload = read_bytes_func(length)
    # consume optional trailing terminator without failing if absent
    try:
        read_bytes_func(1, break_on_termchar=True)
    except Exception:
        pass
    return payload


def _normalize_memory_depth_value(value: Union[str, int]) -> Tuple[str, Optional[int]]:
    """Normalise memory depth input, returning the SCPI text and numeric form.

    Returns
    -------
    tuple
        (value_as_string, numeric_points or None if AUTO)
    """

    if isinstance(value, str):
        candidate = value.strip().upper()
        if candidate == "AUTO":
            return "AUTO", None
        try:
            numeric = int(candidate)
        except ValueError as exc:
            raise ValueError(f"Unsupported memory depth: {value!r}") from exc
    else:
        numeric = int(value)
        candidate = str(numeric)

    if numeric not in _MEMORY_DEPTH_VALUES:
        raise ValueError(
            f"Unsupported memory depth: {numeric}. "
            f"Valid values are {_MEMORY_DEPTH_VALUES} or 'AUTO'."
        )
    return candidate, numeric


def _parse_memory_depth(reply: str) -> Union[int, str]:
    """Parse the `:ACQ:MDEP?` reply into `AUTO` or an integer."""

    cleaned = reply.strip().upper()
    if cleaned == "AUTO":
        return "AUTO"
    try:
        return int(cleaned)
    except ValueError as exc:
        raise RuntimeError(f"Unexpected memory depth reply: {reply!r}") from exc


class RigolDS1000ZChannel(Channel):
    """Analog input channel for the Rigol DS/MSO 1000Z series."""

    coupling = Channel.control(
        ":CHAN{ch}:COUP?",
        ":CHAN{ch}:COUP %s",
        "Control the channel coupling mode (str): 'DC', 'AC', or 'GND'.",
        validator=strict_discrete_set,
        values=["DC", "AC", "GND"],
        preprocess_reply=lambda v: v.strip(),
    )

    bandwidth_limit_enabled = Channel.control(
        ":CHAN{ch}:BWL?",
        ":CHAN{ch}:BWL %s",
        "Control the 20 MHz bandwidth limit filter (bool).",
        validator=strict_discrete_set,
        values={True: "20M", False: "OFF"},
        map_values=True,
        preprocess_reply=lambda v: v.strip(),
    )

    display_enabled = Channel.control(
        ":CHAN{ch}:DISP?",
        ":CHAN{ch}:DISP %d",
        "Control whether the channel is displayed (bool).",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    invert = Channel.control(
        ":CHAN{ch}:INV?",
        ":CHAN{ch}:INV %s",
        "Control signal inversion (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        preprocess_reply=lambda v: v.strip(),
    )

    scale = Channel.control(
        ":CHAN{ch}:SCAL?",
        ":CHAN{ch}:SCAL %.6f",
        "Control the vertical scale in volts per division (float).",
        cast=float,
    )

    offset = Channel.control(
        ":CHAN{ch}:OFFS?",
        ":CHAN{ch}:OFFS %.6f",
        "Control the vertical offset in volts (float).",
        cast=float,
    )

    probe_ratio = Channel.control(
        ":CHAN{ch}:PROB?",
        ":CHAN{ch}:PROB %f",
        "Control the probe attenuation ratio (float).",
        validator=strict_range,
        values=[0.0001, 1000],
        cast=float,
    )

    unit = Channel.control(
        ":CHAN{ch}:UNIT?",
        ":CHAN{ch}:UNIT %s",
        "Control the channel unit (str).",
        validator=strict_discrete_set,
        values=["VOLT", "WATT", "AMP", "UNKN"],
        preprocess_reply=lambda v: v.strip(),
    )


# TODO: add Cursor object


class RigolDS1000ZDisplay:
    """Display subsystem for Rigol DS/MSO 1000Z (:DISPlay.*)."""

    def __init__(self, parent: "RigolDS1000Z"):
        self._parent = parent

    def clear(self) -> None:
        """Clear all waveforms on the screen (equiv. front-panel CLEAR)."""
        self._parent.write(":DISP:CLE")

    def grab_image(
        self,
        color: Optional[bool] = None,
        invert: Optional[bool] = None,
        image_format: Union[DisplayImageFormat, str] = DisplayImageFormat.BMP24,
    ) -> bytes:
        """
        Return the current screen image bytes (payload only, TMC header removed).

        Parameters
        ----------
        color : bool | None
            True=color, False=intensity graded color, None=use current setting.
        invert : bool | None
            True to invert, False normal, None=use current setting.
        image_format : DisplayImageFormat | str
            One of BMP24, BMP8, PNG, JPEG, TIFF. Defaults to BMP24.

        Returns
        -------
        bytes
            Image file bytes (e.g. PNG, BMP, …), without the TMC header.
        """
        if isinstance(image_format, DisplayImageFormat):
            fmt = image_format.value
        else:
            fmt = str(image_format).upper()
            if fmt not in {f.value for f in DisplayImageFormat}:
                raise ValueError(f"Unsupported image format: {image_format}")

        # Build optional argument block [<color>,<invert>,<format>]
        if color is not None or invert is not None:
            col = "ON" if bool(color) else "OFF" if color is not None else ""
            inv = "ON" if bool(invert) else "OFF" if invert is not None else ""
            # If either color or invert is specified, include both positions; empty slots allowed
            args = f"[{col},{inv},{fmt}]"
        else:
            # Caller supplied neither color nor invert; only supply format if non-default BMP24?
            # Spec says default is BMP24 when omitted, so omit entirely to use instrument defaults.
            args = ""

        cmd = f":DISP:DATA? {args}".rstrip()
        self._parent.write(cmd)
        return _parse_tmc_block(self._parent.read_bytes)

    @property
    def type(self) -> DisplayType:
        reply = self._parent.ask(":DISP:TYPE?")
        val = reply.strip().upper()
        # Instrument replies "VECT" or "DOTS"
        return DisplayType(val)

    @type.setter
    def type(self, mode: Union[DisplayType, str]) -> None:
        if isinstance(mode, DisplayType):
            val = mode.value
        else:
            val = str(mode).upper()
            if val == "VECTORS":  # accept friendly alias
                val = "VECT"
            if val not in (DisplayType.VECTORS.value, DisplayType.DOTS.value):
                raise ValueError("Display type must be 'VECTors' or 'DOTS'.")
        self._parent.write(f":DISP:TYPE {val}")

    @property
    def persistence(self) -> str:
        """Return persistence time: MIN, 0.1, 0.2, 0.5, 1, 5, 10, or INF."""
        return self._parent.ask(":DISP:GRAD:TIME?").strip().upper()

    @persistence.setter
    def persistence(self, value: Union[str, float]) -> None:
        allowed = {"MIN", "0.1", "0.2", "0.5", "1", "5", "10", "INF", "INFINITE"}
        if isinstance(value, (int, float)):
            value = str(value)
        val = str(value).strip().upper()
        if val == "INFINITE":
            val = "INF"
        if val not in allowed:
            raise ValueError(f"Invalid persistence '{value}'. Allowed: {sorted(allowed)}")
        self._parent.write(f":DISP:GRAD:TIME {val}")

    @property
    def waveform_brightness(self) -> int:
        return int(float(self._parent.ask(":DISP:WBR?")))

    @waveform_brightness.setter
    def waveform_brightness(self, pct: int) -> None:
        if not (0 <= int(pct) <= 100):
            raise ValueError("Waveform brightness must be 0..100")
        self._parent.write(f":DISP:WBR {int(pct)}")

    @property
    def grid(self) -> DisplayGrid:
        return DisplayGrid(self._parent.ask(":DISP:GRID?").strip().upper())

    @grid.setter
    def grid(self, mode: Union[DisplayGrid, str]) -> None:
        val = mode.value if isinstance(mode, DisplayGrid) else str(mode).upper()
        if val not in {g.value for g in DisplayGrid}:
            raise ValueError("Grid must be FULL, HALF, or NONE.")
        self._parent.write(f":DISP:GRID {val}")

    @property
    def grid_brightness(self) -> int:
        return int(float(self._parent.ask(":DISP:GBR?")))

    @grid_brightness.setter
    def grid_brightness(self, pct: int) -> None:
        if not (0 <= int(pct) <= 100):
            raise ValueError("Grid brightness must be 0..100")
        self._parent.write(f":DISP:GBR {int(pct)}")


class RigolDS1000Z(SCPIMixin, Instrument):
    """Driver for the Rigol DS/MSO 1000Z series oscilloscopes."""

    channel_1 = Instrument.ChannelCreator(RigolDS1000ZChannel, "1")
    channel_2 = Instrument.ChannelCreator(RigolDS1000ZChannel, "2")
    channel_3 = Instrument.ChannelCreator(RigolDS1000ZChannel, "3")
    channel_4 = Instrument.ChannelCreator(RigolDS1000ZChannel, "4")

    acquisition_type = Instrument.control(
        ":ACQ:TYPE?",
        ":ACQ:TYPE %s",
        "Control the acquisition type (str): 'NORM', 'AVER', 'PEAK', or 'HRES'.",
        validator=strict_discrete_set,
        values=[mode.value for mode in AcquireType],
    )

    average_count = Instrument.control(
        ":ACQ:AVE?",
        ":ACQ:AVE %d",
        "Control the number of waveforms averaged when the acquisition type is 'AVER'.",
        validator=strict_range,
        values=[2, 1024],
        cast=int,
    )

    sample_rate = Instrument.measurement(
        ":ACQ:SRAT?",
        "Measure the current sample rate in samples per second (float).",
        cast=float,
    )

    @property
    def memory_depth(self) -> Union[int, str]:
        """Control the acquisition memory depth in points or 'AUTO'.

        The allowable discrete values depend on how many analogue and digital
        channels are currently enabled. The driver counts the active analogue
        inputs and uses :meth:`set_digital_channel_hint` as an optional cue for
        the digital pod state before applying validation.
        """

        reply = self.ask(":ACQ:MDEP?")
        return _parse_memory_depth(reply)

    @memory_depth.setter
    def memory_depth(self, value: Union[str, int]) -> None:
        target, numeric = _normalize_memory_depth_value(value)
        if numeric is not None:
            allowed = self._allowed_memory_depth_values()
            if numeric not in allowed:
                raise ValueError(
                    f"Memory depth {numeric} pts is not permitted for the current "
                    f"channel configuration. Allowed values: {sorted(allowed)} or 'AUTO'."
                )
        self.write(f":ACQ:MDEP {target}")

    trigger_source = Instrument.control(
        ":TRIG:EDGE:SOUR?",
        ":TRIG:EDGE:SOUR %s",
        "Control the trigger source selection (str).",
        validator=strict_discrete_set,
        values=_WAVEFORM_SOURCES,
    )

    trigger_slope = Instrument.control(
        ":TRIG:EDGE:SLOP?",
        ":TRIG:EDGE:SLOP %s",
        "Control the trigger slope (str): 'POS' or 'NEG'.",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
    )

    trigger_coupling = Instrument.control(
        ":TRIG:COUP?",
        ":TRIG:COUP %s",
        "Control the trigger coupling mode (str).",
        validator=strict_discrete_set,
        values=["AC", "DC", "HFRej", "LFRej", "NOIS"],
    )

    trigger_sweep = Instrument.control(
        ":TRIG:SWE?",
        ":TRIG:SWE %s",
        "Control the trigger sweep mode (str): 'AUTO', 'NORM', or 'SING'.",
        validator=strict_discrete_set,
        values=["AUTO", "NORM", "SING"],
    )

    trigger_level = Instrument.control(
        ":TRIG:LEV?",
        ":TRIG:LEV %f",
        "Control the trigger level in volts (float).",
        cast=float,
    )

    waveform_source = Instrument.control(
        ":WAV:SOUR?",
        ":WAV:SOUR %s",
        "Control the waveform source used for data transfers (str).",
        validator=strict_discrete_set,
        values=_WAVEFORM_SOURCES,
    )

    waveform_mode = Instrument.control(
        ":WAV:MODE?",
        ":WAV:MODE %s",
        "Control the waveform acquisition mode for transfer (str).",
        validator=strict_discrete_set,
        values=[mode.value for mode in WaveformMode],
    )

    waveform_format = Instrument.control(
        ":WAV:FORM?",
        ":WAV:FORM %s",
        "Control the waveform data format for transfer (str).",
        validator=strict_discrete_set,
        values=[fmt.value for fmt in WaveformFormat],
    )

    waveform_start = Instrument.control(
        ":WAV:STAR?",
        ":WAV:STAR %d",
        "Control the first data point index for waveform transfer (int).",
        cast=int,
    )

    waveform_stop = Instrument.control(
        ":WAV:STOP?",
        ":WAV:STOP %d",
        "Control the last data point index for waveform transfer (int).",
        cast=int,
    )

    def __init__(self, adapter, name="Rigol DS1000Z/MSO1000Z Oscilloscope",
                 channel_count=4, **kwargs):
        """Initialise the driver.

        Parameters
        ----------
        adapter : Adapter or str
            PyMeasure adapter or VISA resource name.
        name : str, optional
            Readable instrument name reported to PyMeasure.
        channel_count : int, optional
            Number of *physical* analogue channels fitted to the scope (typically 2 or 4).
            Must be between 1 and 4; only determines how many channel interfaces
            are exposed via :pyattr:`channels`. The SCPI properties still allow
            enabling or disabling any individual channel regardless of that entry
            count.
        **kwargs :
            Forwarded to :class:`~pymeasure.instruments.Instrument`.
        """
        super().__init__(adapter, name, **kwargs)
        if not 1 <= channel_count <= 4:
            raise ValueError("channel_count must be between 1 and 4")
        self._channel_count = channel_count
        self._channel_map = {
            index: getattr(self, f"channel_{index}")
            for index in range(1, channel_count + 1)
        }
        self._digital_channel_hint: Optional[int] = None
        self.display = RigolDS1000ZDisplay(self)

    def run(self):
        """Start waveform acquisition."""
        self.write(":RUN")

    def stop(self):
        """Stop waveform acquisition."""
        self.write(":STOP")

    def single(self):
        """Arm the scope for a single acquisition."""
        self.write(":SING")

    def autoscale(self):
        """Perform automatic scaling (vertical and timebase)."""
        self.write(":AUT")

    def clear_status(self):
        """Clear the instrument status register."""
        self.write("*CLS")

    def clear(self):
        """Clear all the waveforms on the screen."""
        self.write(":CLE")

    def clear_registers(self):
        """Clear all the event registers and clear the error queue."""
        self.write(":CLS")

    def reset(self):
        """Reset the instrument to factory defaults."""
        self.write("*RST")

    def calibrate_start(self):
        """Calibrate the start of the instrument.

        The self-calibration operation can make the oscilloscope quickly reach its optimum working
        state to obtain the most accurate measurement values.

        During the self-calibration, all the channels of the oscilloscope must be disconnected
        from the inputs.

        The functions of most of the keys are disabled during the self-calibration. You can call
        the calibrate_quit method to quit the self-calibration.
        """
        self.write(":CAL:STAR")

    def calibrate_quit(self):
        """Exit the self-calibration at any time."""
        self.write(":CAL:QUIT")

    def configure_edge_trigger(
        self,
        source: Union[str, int],
        level: float = 0.0,
        slope: str = "POS",
        coupling: str = "DC",
        sweep: str = "AUTO",
    ):
        """Configure the edge trigger settings in a single call."""

        if isinstance(source, int):
            if not 1 <= source <= self._channel_count:
                raise ValueError("Invalid channel index for trigger source.")
            source_value = f"CHAN{source}"
        else:
            source_value = str(source).upper()
        self.trigger_source = source_value
        self.trigger_level = level
        self.trigger_slope = slope
        self.trigger_coupling = coupling
        self.trigger_sweep = sweep

    def tforce(self):
        """Generate a trigger signal forcefully. This command is only applicable to the normal
        and single trigger modes."""
        self.write(":TFOR")

    def get_waveform_preamble(self) -> Dict[str, Union[int, float]]:
        """Return the parsed contents of `:WAVeform:PREamble?`."""
        reply = self.ask(":WAV:PRE?")
        return _parse_waveform_preamble(reply)

    def read_waveform(
        self,
        source: Union[str, int] = "CHAN1",
        mode: Union[WaveformMode, str] = WaveformMode.NORMAL,
        data_format: Union[WaveformFormat, str] = WaveformFormat.BYTE,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        force_stop_for_raw: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Read a waveform and return time and voltage arrays."""

        if isinstance(source, int):
            if not 1 <= source <= self._channel_count:
                raise ValueError("Invalid channel index for waveform read.")
            source_value = f"CHAN{source}"
        else:
            source_value = str(source).upper()

        if isinstance(mode, WaveformMode):
            mode_value = mode.value
        else:
            mode_value = str(mode).upper()
        try:
            mode_enum = WaveformMode(mode_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported waveform mode: {mode}") from exc

        if isinstance(data_format, WaveformFormat):
            format_value = data_format.value
        else:
            format_value = str(data_format).upper()
        try:
            format_enum = WaveformFormat(format_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported waveform format: {data_format}") from exc

        if force_stop_for_raw and mode_enum == WaveformMode.RAW:
            self.stop()

        self.waveform_source = source_value
        self.waveform_mode = mode_enum.value
        self.waveform_format = format_enum.value

        preamble = self.get_waveform_preamble()
        total_points = preamble["points"]
        if start is None:
            start = 1
        if stop is None:
            stop = total_points
        if total_points <= 0:
            return np.array([], dtype=float), np.array([], dtype=float)
        if stop < start:
            raise ValueError("Invalid start/stop points for waveform acquisition.")
        if start < 1:
            raise ValueError("Invalid start/stop points for waveform acquisition.")

        chunk_limits = {
            WaveformFormat.BYTE: 250_000,
            WaveformFormat.WORD: 125_000,
            WaveformFormat.ASCII: 15_625,
        }
        chunk_size = chunk_limits[format_enum]

        raw_chunks: List[np.ndarray] = []
        index = start
        while index <= stop:
            chunk_stop = min(index + chunk_size - 1, stop)
            self.write(f":WAV:STAR {index}")
            self.write(f":WAV:STOP {chunk_stop}")
            if format_enum == WaveformFormat.ASCII:
                text = self.ask(":WAV:DATA?")
                raw = np.fromstring(text, sep=",", dtype=float)
            else:
                self.write(":WAV:DATA?")
                header = self.read_bytes(2)
                if len(header) != 2 or not header.startswith(b"#"):
                    raise RuntimeError("Invalid binary block header.")
                length_digits = int(header[1:2].decode("ascii"))
                length = int(self.read_bytes(length_digits).decode("ascii"))
                payload = self.read_bytes(length)
                # consume trailing terminator if present
                try:
                    self.read_bytes(1, break_on_termchar=True)
                except Exception:
                    pass
                dtype = np.uint8 if format_enum == WaveformFormat.BYTE else np.uint16
                raw = np.frombuffer(payload, dtype=dtype).astype(np.float64)
            raw_chunks.append(raw)
            index = chunk_stop + 1

        if raw_chunks:
            raw_data = np.concatenate(raw_chunks)
        else:
            raw_data = np.array([], dtype=float)

        if format_enum == WaveformFormat.ASCII:
            voltage = raw_data
        else:
            y_origin = preamble["y_origin"]
            y_reference = preamble["y_reference"]
            y_increment = preamble["y_increment"]
            voltage = (raw_data - y_origin - y_reference) * y_increment

        start_index = start - 1
        sample_count = voltage.size
        x_origin = preamble["x_origin"]
        x_reference = preamble["x_reference"]
        x_increment = preamble["x_increment"]
        time = x_origin + (np.arange(start_index, start_index + sample_count) - x_reference) * x_increment

        return time, voltage

    def save_screen_to_usb(self, filename: str = "rigol.png"):
        """Save a PNG screenshot to the USB storage device."""

        self.write(":STOR:IMAG:TYPE PNG")
        self.write(":STOR:IMAG:COL ON")
        self.write(f':STOR:IMAG "USB:\\{filename}"')

    # --- Helpers ---
    def set_digital_channel_hint(self, active_lines: Optional[int]) -> None:
        """Hint the number of enabled digital lines for memory-depth validation.

        Parameters
        ----------
        active_lines : int or None
            Use 0 when the MSO pod is disabled, 8 or 16 when the corresponding
            digital groups are enabled. ``None`` clears the hint and reverts to
            the default assumption (no digital channels enabled).
        """

        if active_lines is None:
            self._digital_channel_hint = None
            return
        if active_lines not in (0, 8, 16):
            raise ValueError("active_lines must be one of 0, 8, 16, or None")
        self._digital_channel_hint = active_lines

    def _allowed_memory_depth_values(self) -> Set[int]:
        analog_active = self._active_analog_channel_count()
        analog_key = min(max(analog_active, 0), 4)
        analog_options = _ANALOG_MEMORY_DEPTH_OPTIONS.get(
            analog_key, _ANALOG_MEMORY_DEPTH_OPTIONS[0]
        )

        digital_active = self._active_digital_channel_count()
        digital_options = _DIGITAL_MEMORY_DEPTH_OPTIONS.get(
            digital_active, _DIGITAL_MEMORY_DEPTH_OPTIONS[0]
        )
        return analog_options & digital_options

    def _active_analog_channel_count(self) -> int:
        count = 0
        for index in range(1, self._channel_count + 1):
            channel = self._channel_map.get(index)
            if channel is None:
                continue
            try:
                if bool(channel.display_enabled):
                    count += 1
            except Exception:
                # If the query fails, assume the channel is active to keep the
                # validation conservative.
                count += 1
        return count

    def _active_digital_channel_count(self) -> int:
        if self._digital_channel_hint is not None:
            return self._digital_channel_hint
        # Without a reliable SCPI query across all models, default to assuming
        # the digital pod is currently disabled.
        return 0
