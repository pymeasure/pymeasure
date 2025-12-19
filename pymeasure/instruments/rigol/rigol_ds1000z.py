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
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        """Until StrEnum is broadly available from the standard library"""
        # Python>3.10 remove it.

from typing import Union, Optional

import numpy as np

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


_ANALOG_SOURCES: tuple[str, ...] = ("CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH")
_DIGITAL_SOURCES: tuple[str, ...] = tuple(f"D{idx}" for idx in range(16))
_WAVEFORM_SOURCES: tuple[str, ...] = _ANALOG_SOURCES + _DIGITAL_SOURCES
_MEMORY_DEPTH_VALUES: tuple[int, ...] = (
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
_ANALOG_MEMORY_DEPTH_OPTIONS: dict[int, set[int]] = {
    0: set(_MEMORY_DEPTH_VALUES),
    1: {12000, 120000, 1200000, 12000000, 24000000},
    2: {6000, 60000, 600000, 6000000, 12000000},
    3: {3000, 30000, 300000, 3000000, 6000000},
    4: {3000, 30000, 300000, 3000000, 6000000},
}
_DIGITAL_MEMORY_DEPTH_OPTIONS: dict[int, set[int]] = {
    0: set(_MEMORY_DEPTH_VALUES),
    8: {12000, 120000, 1200000, 12000000, 24000000},
    16: {6000, 60000, 600000, 6000000, 12000000},
}


class AcquireType(StrEnum):
    """Supported acquisition types for the scope.

    - ``NORMAL`` (``NORM``): Samples at equal time intervals to rebuild the waveform.
    - ``AVERAGE`` (``AVER``): Averages multiple acquisitions to reduce noise (see
      :attr:`~RigolDS1000Z.average_count`).
    - ``PEAK`` (``PEAK``): Captures min/max values per interval to preserve narrow pulses.
    - ``HIGH_RESOLUTION`` (``HRES``): Ultra-sample technique that smooths waveforms by averaging
      neighboring points.
    """
    NORMAL = "NORM"
    AVERAGE = "AVER"
    PEAK = "PEAK"
    HIGH_RESOLUTION = "HRES"


class WaveformMode(StrEnum):
    """Waveform acquisition modes supported by the scope."""
    NORMAL = "NORM"
    MAXIMUM = "MAX"
    RAW = "RAW"


class WaveformFormat(StrEnum):
    """Waveform data formats supported by the scope."""
    BYTE = "BYTE"
    WORD = "WORD"
    ASCII = "ASC"


_WAVEFORM_CHUNK_LIMITS: dict[WaveformFormat, int] = {
    WaveformFormat.BYTE: 250_000,
    WaveformFormat.WORD: 125_000,
    WaveformFormat.ASCII: 15_625,
}


# Display enums

class DisplayType(StrEnum):
    VECTORS = "VECT"
    DOTS = "DOTS"


class DisplayGrid(StrEnum):
    FULL = "FULL"
    HALF = "HALF"
    NONE = "NONE"


class DisplayImageFormat(StrEnum):
    BMP24 = "BMP24"
    BMP8 = "BMP8"
    PNG = "PNG"
    JPEG = "JPEG"
    TIFF = "TIFF"


def _parse_waveform_preamble(reply: str) -> dict[str, Union[int, float]]:
    """Parse the `:WAV:PRE?` reply into a structured dictionary."""

    fields = reply.split(",")
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


def _normalize_memory_depth_value(
    value: Union[str, int],
    *,
    allowed_values: Optional[set[int]] = None,
    allowed_values_factory=None,
) -> tuple[str, Optional[int]]:
    """Normalise memory depth input, returning the SCPI text and numeric form.

    :param value: Either ``"AUTO"`` (case-insensitive) or an integer number of points.
    :param allowed_values: Optional set of allowed numeric values for the current scope
        configuration.
    :param allowed_values_factory: Optional callable returning the allowed numeric values. This is
        only called when a numeric depth is requested (not for ``"AUTO"``).
    :return: ``(value_as_string, numeric_points_or_None_if_AUTO)``
    """

    if isinstance(value, str):
        cleaned = value.strip().upper()
        if cleaned == "AUTO":
            return "AUTO", None
        try:
            numeric = int(cleaned)
        except ValueError as exc:
            raise ValueError(f"Unsupported memory depth: {value!r}") from exc
    else:
        numeric = int(value)

    if numeric not in _MEMORY_DEPTH_VALUES:
        raise ValueError(
            f"Unsupported memory depth: {numeric}. "
            f"Valid values are {_MEMORY_DEPTH_VALUES} or 'AUTO'."
        )

    if allowed_values is None and callable(allowed_values_factory):
        allowed_values = allowed_values_factory()
    if allowed_values is not None and numeric not in allowed_values:
        raise ValueError(
            f"Memory depth {numeric} pts is not permitted for the current "
            f"channel configuration. Allowed values: {sorted(allowed_values)} or 'AUTO'."
        )
    return str(numeric), numeric


def _parse_memory_depth(reply: str) -> Union[int, str]:
    """Parse the `:ACQ:MDEP?` reply into `AUTO` or an integer."""

    cleaned = reply.strip().upper()
    if cleaned == "AUTO":
        return "AUTO"
    try:
        return int(cleaned)
    except ValueError as exc:
        raise RuntimeError(f"Unexpected memory depth reply: {reply!r}") from exc


def _validate_enum_member(value, values):
    """Accept either an enum member or its SCPI value (case-insensitive)."""
    if isinstance(value, values):
        return value
    try:
        return values(str(value).upper())
    except ValueError as exc:
        raise ValueError(f"Unsupported value: {value!r}") from exc


class RigolDS1000ZChannel(Channel):
    """Analog input channel for the Rigol DS/MSO 1000Z series."""

    coupling = Channel.control(
        ":CHAN{ch}:COUP?",
        ":CHAN{ch}:COUP %s",
        "Control the channel coupling mode (str): 'DC', 'AC', or 'GND'.",
        validator=strict_discrete_set,
        values=["DC", "AC", "GND"],
    )

    bandwidth_limit_enabled = Channel.control(
        ":CHAN{ch}:BWL?",
        ":CHAN{ch}:BWL %s",
        "Control the 20 MHz bandwidth limit filter (bool).",
        validator=strict_discrete_set,
        values={True: "20M", False: "OFF"},
        map_values=True,
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
    )

    scale = Channel.control(
        ":CHAN{ch}:SCAL?",
        ":CHAN{ch}:SCAL %.6f",
        "Control the vertical scale in volts per division (float).",
    )

    offset = Channel.control(
        ":CHAN{ch}:OFFS?",
        ":CHAN{ch}:OFFS %.6f",
        "Control the vertical offset in volts (float).",
    )

    probe_ratio = Channel.control(
        ":CHAN{ch}:PROB?",
        ":CHAN{ch}:PROB %f",
        "Control the probe attenuation ratio (float).",
        validator=strict_range,
        values=[0.0001, 1000],
    )

    unit = Channel.control(
        ":CHAN{ch}:UNIT?",
        ":CHAN{ch}:UNIT %s",
        "Control the channel unit (str): 'VOLT', 'WATT', 'AMP', or 'UNKN'.",
        validator=strict_discrete_set,
        values=["VOLT", "WATT", "AMP", "UNKN"],
    )


class RigolDS1000ZDisplay(Channel):
    """Display subsystem for Rigol DS/MSO 1000Z (:DISPlay.*)."""

    def insert_id(self, command):
        """We treat the Display as a channel so we can use channel control, but we don't
        need to insert an ID.
        """
        return command

    def clear(self) -> None:
        """Clear all waveforms on the screen (equiv. front-panel CLEAR)."""
        self.write(":DISP:CLE")

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
        self.write(cmd)
        return _parse_tmc_block(self.read_bytes)

    type = Channel.control(
        ":DISP:TYPE?",
        ":DISP:TYPE %s",
        "Control the display type (str): 'VECT' (vectors) or 'DOTS'.",
        validator=strict_discrete_set,
        values=[DisplayType.VECTORS.value, DisplayType.DOTS.value],
    )

    persistence = Channel.control(
        ":DISP:GRAD:TIME?",
        ":DISP:GRAD:TIME %s",
        "Control persistence time (str): one of 'MIN','0.1','0.2','0.5','1','5','10','INF'.",
        validator=strict_discrete_set,
        values=["MIN", "0.1", "0.2", "0.5", "1", "5", "10", "INF"],
    )

    waveform_brightness = Channel.control(
        ":DISP:WBR?",
        ":DISP:WBR %d",
        "Control the waveform brightness (int 0..100).",
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    grid = Channel.control(
        ":DISP:GRID?",
        ":DISP:GRID %s",
        "Control the display grid (str): 'FULL','HALF','NONE'.",
        validator=strict_discrete_set,
        values=[g.value for g in DisplayGrid],
    )

    grid_brightness = Channel.control(
        ":DISP:GBR?",
        ":DISP:GBR %d",
        "Control the grid brightness (int 0..100).",
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )


class RigolDS1000Z(SCPIMixin, Instrument):
    """Driver for the Rigol DS/MSO 1000Z series oscilloscopes.

    Quick start
    -----------

    .. code-block:: python

        from pymeasure.instruments.rigol import RigolDS1000Z

        with RigolDS1000Z("TCPIP0::10.0.0.5::INSTR") as scope:
            scope.reset()
            scope.clear_status()

            # Configure analogue channel 1
            scope.channel_1.display_enabled = True
            scope.channel_1.coupling = "DC"
            scope.channel_1.scale = 0.5  # volts/div

            # Pull the waveform
            time_axis, voltage = scope.read_waveform(source=1)

    Memory depth handling
    ---------------------

    Rigol scopes restrict memory depth to discrete values that depend on the number of enabled
    analogue inputs and, on MSO models, digital pod lines. The driver automatically queries the
    display state of each analogue channel before accepting a depth change and raises
    :class:`ValueError` if the requested value does not fit the current configuration.

    Digital pod usage varies between models, so the driver exposes
    :meth:`set_digital_channel_hint` for callers to provide the number of active digital lines
    (0, 8, or 16). This hint is optional—if omitted, the logic assumes the pod is disabled—but it
    enables strict validation when logic channels are in use.

    Waveform acquisition
    --------------------

    :meth:`read_waveform` wraps the SCPI ``:WAV`` commands, handling chunked reads, binary block
    parsing, and scaling the returned data to physical units. The method accepts either integer
    channel indices or the standard Rigol source names (for example ``"CHAN1"``, ``"MATH"``, or
    ``"D0"``), and it supports all Rigol formats via :class:`WaveformFormat`.

    Display capture
    ---------------

    The :class:`RigolDS1000ZDisplay` helper contains front-panel display controls, including
    :meth:`RigolDS1000ZDisplay.grab_image`. Calling ``grab_image`` issues ``:DISP:DATA?`` and
    returns the raw image bytes (PNG, BMP, JPEG, or TIFF) so you can save them directly to disk:

    .. code-block:: python

        from pathlib import Path

        image = scope.display.grab_image(color=True, image_format="PNG")
        Path("screenshot.png").write_bytes(image)

    Optional ``color`` and ``invert`` parameters map to the oscilloscope arguments, allowing
    monochrome or inverted captures without halting acquisition.

    :param adapter: PyMeasure adapter or VISA resource name.
    :param name: Readable instrument name reported to PyMeasure.
    :param channel_count: Number of *physical* analogue channels fitted to the scope (typically 2
        or 4). Must be between 1 and 4; only determines how many channel interfaces are exposed via
        channels. The SCPI properties still allow enabling or disabling any individual channel
        regardless of that entry count.
    :param kwargs: Forwarded to :class:`~pymeasure.instruments.Instrument`.
    """

    def __init__(self, adapter, name="Rigol DS1000Z/MSO1000Z Oscilloscope",
                 channel_count=4, **kwargs):
        super().__init__(adapter, name, **kwargs)
        if not 1 <= channel_count <= 4:
            raise ValueError("channel_count must be between 1 and 4")
        self._channel_count = channel_count
        self._channel_map = {
            index: getattr(self, f"channel_{index}")
            for index in range(1, channel_count + 1)
        }
        self._digital_channel_hint: Optional[int] = None

    channel_1 = Instrument.ChannelCreator(RigolDS1000ZChannel, "1")
    channel_2 = Instrument.ChannelCreator(RigolDS1000ZChannel, "2")
    channel_3 = Instrument.ChannelCreator(RigolDS1000ZChannel, "3")
    channel_4 = Instrument.ChannelCreator(RigolDS1000ZChannel, "4")
    display: RigolDS1000ZDisplay = Instrument.ChannelCreator(RigolDS1000ZDisplay, "")

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

        Digital pod activity cannot be queried reliably across all models, so you must set the
        hint manually when using logic channels.
        """

        reply = self.ask(":ACQ:MDEP?")
        return _parse_memory_depth(reply)

    @memory_depth.setter
    def memory_depth(self, value: Union[str, int]) -> None:
        target, numeric = _normalize_memory_depth_value(
            value,
            allowed_values_factory=self._allowed_memory_depth_values,
        )
        self.write(f":ACQ:MDEP {target}")

    trigger_source = Instrument.control(
        ":TRIG:EDGE:SOUR?",
        ":TRIG:EDGE:SOUR %s",
        "Control the trigger source selection (str): e.g. 'CHAN1'..'CHAN4', 'MATH', or "
        "'D0'..'D15'.",
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

    @property
    def trigger_slope_positive(self) -> bool:
        """Control whether the edge trigger slope is positive (bool)."""
        return self.trigger_slope == "POS"

    @trigger_slope_positive.setter
    def trigger_slope_positive(self, value: bool) -> None:
        self.trigger_slope = "POS" if bool(value) else "NEG"

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
        "Control the waveform acquisition mode for transfer (:class:`WaveformMode`).",
        validator=_validate_enum_member,
        values=WaveformMode,
        get_process=WaveformMode,
        set_process=lambda mode: mode.value,
    )

    waveform_format = Instrument.control(
        ":WAV:FORM?",
        ":WAV:FORM %s",
        "Control the waveform data format for transfer (:class:`WaveformFormat`).",
        validator=_validate_enum_member,
        values=WaveformFormat,
        get_process=WaveformFormat,
        set_process=lambda fmt: fmt.value,
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
        """Alias for :meth:`clear_waveforms`."""
        self.clear_waveforms()

    def clear_waveforms(self):
        """Clear all the waveforms on the screen."""
        self.write(":CLE")

    def clear_registers(self):
        """Clear all the event registers and clear the error queue."""
        self.write(":CLS")

    def reset(self):
        """Reset the instrument to factory defaults."""
        self.write("*RST")

    def calibrate_start(self):
        """Alias for :meth:`start_calibration`."""
        self.start_calibration()

    def start_calibration(self):
        """Run the self-calibration procedure.

        The self-calibration operation can make the oscilloscope quickly reach its optimum working
        state to obtain the most accurate measurement values.

        During the self-calibration, all the channels of the oscilloscope must be disconnected
        from the inputs.

        The functions of most of the keys are disabled during the self-calibration. You can call
        the :meth:`abort_calibration` method to quit the self-calibration.
        """
        self.write(":CAL:STAR")

    def calibrate_quit(self):
        """Alias for :meth:`abort_calibration`."""
        self.abort_calibration()

    def abort_calibration(self):
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
        """Alias for :meth:`force_trigger`."""
        self.force_trigger()

    def force_trigger(self):
        """Generate a trigger signal forcefully.

        This command is only applicable to the normal and single trigger modes.
        """
        self.write(":TFOR")

    def get_waveform_preamble(self) -> dict[str, Union[int, float]]:
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
    ) -> tuple[np.ndarray, np.ndarray]:
        """Read a waveform and return time and voltage arrays."""

        source_value = self._resolve_waveform_source(source)
        mode_enum = self._resolve_waveform_mode(mode)
        format_enum = self._resolve_waveform_format(data_format)

        if force_stop_for_raw and mode_enum == WaveformMode.RAW:
            self.stop()

        self._configure_waveform_transfer(source_value, mode_enum, format_enum)

        preamble = self.get_waveform_preamble()
        total_points = preamble["points"]
        if total_points <= 0:
            empty = np.array([], dtype=float)
            return empty, empty

        start, stop = self._derive_waveform_window(total_points, start, stop)

        raw_data = self._collect_waveform_data(format_enum, start, stop)
        voltage = self._scale_waveform_data(format_enum, raw_data, preamble)
        time = self._generate_time_axis(preamble, start, voltage.size)

        return time, voltage

    def _resolve_waveform_source(self, source: Union[str, int]) -> str:
        if isinstance(source, int):
            if not 1 <= source <= self._channel_count:
                raise ValueError("Invalid channel index for waveform read.")
            return f"CHAN{source}"
        return str(source).upper()

    @staticmethod
    def _resolve_waveform_mode(mode: Union[WaveformMode, str]) -> WaveformMode:
        if isinstance(mode, WaveformMode):
            return mode
        mode_value = str(mode).upper()
        try:
            return WaveformMode(mode_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported waveform mode: {mode}") from exc

    @staticmethod
    def _resolve_waveform_format(data_format: Union[WaveformFormat, str]) -> WaveformFormat:
        if isinstance(data_format, WaveformFormat):
            return data_format
        format_value = str(data_format).upper()
        try:
            return WaveformFormat(format_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported waveform format: {data_format}") from exc

    def _configure_waveform_transfer(
        self,
        source_value: str,
        mode_enum: WaveformMode,
        format_enum: WaveformFormat,
    ) -> None:
        self.waveform_source = source_value
        self.waveform_mode = mode_enum
        self.waveform_format = format_enum

    @staticmethod
    def _derive_waveform_window(
        total_points: int,
        start: Optional[int],
        stop: Optional[int],
    ) -> tuple[int, int]:
        start_idx = 1 if start is None else start
        stop_idx = total_points if stop is None else stop
        if stop_idx < start_idx or start_idx < 1:
            raise ValueError("Invalid start/stop points for waveform acquisition.")
        return start_idx, stop_idx

    def _collect_waveform_data(
        self,
        format_enum: WaveformFormat,
        start: int,
        stop: int,
    ) -> np.ndarray:
        chunk_size = _WAVEFORM_CHUNK_LIMITS[format_enum]
        raw_chunks: list[np.ndarray] = []
        index = start
        while index <= stop:
            chunk_stop = min(index + chunk_size - 1, stop)
            self.write(f":WAV:STAR {index}")
            self.write(f":WAV:STOP {chunk_stop}")
            if format_enum == WaveformFormat.ASCII:
                text = self.ask(":WAV:DATA?")
                raw = np.fromstring(text, sep=",", dtype=float)
            else:
                raw = self._read_binary_waveform_chunk(format_enum)
            raw_chunks.append(raw)
            index = chunk_stop + 1

        if raw_chunks:
            return np.concatenate(raw_chunks)
        return np.array([], dtype=float)

    def _read_binary_waveform_chunk(self, format_enum: WaveformFormat) -> np.ndarray:
        self.write(":WAV:DATA?")
        header = self.read_bytes(2)
        if len(header) != 2 or not header.startswith(b"#"):
            raise RuntimeError("Invalid binary block header.")
        length_digits = int(header[1:2].decode("ascii"))
        length = int(self.read_bytes(length_digits).decode("ascii"))
        payload = self.read_bytes(length)
        try:
            self.read_bytes(1, break_on_termchar=True)
        except Exception:
            pass
        dtype = np.uint8 if format_enum == WaveformFormat.BYTE else np.uint16
        return np.frombuffer(payload, dtype=dtype).astype(np.float64)

    @staticmethod
    def _scale_waveform_data(
        format_enum: WaveformFormat,
        raw_data: np.ndarray,
        preamble: dict[str, Union[int, float]],
    ) -> np.ndarray:
        if format_enum == WaveformFormat.ASCII:
            return raw_data
        y_origin = preamble["y_origin"]
        y_reference = preamble["y_reference"]
        y_increment = preamble["y_increment"]
        return (raw_data - y_origin - y_reference) * y_increment

    @staticmethod
    def _generate_time_axis(
        preamble: dict[str, Union[int, float]],
        start: int,
        sample_count: int,
    ) -> np.ndarray:
        start_index = start - 1
        x_origin = preamble["x_origin"]
        x_reference = preamble["x_reference"]
        x_increment = preamble["x_increment"]
        return x_origin + (np.arange(start_index, start_index + sample_count) -
                           x_reference) * x_increment

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

            See :attr:`memory_depth` for details on memory depth validation.
        """

        if active_lines is None:
            self._digital_channel_hint = None
            return
        if active_lines not in (0, 8, 16):
            raise ValueError("active_lines must be one of 0, 8, 16, or None")
        self._digital_channel_hint = active_lines

    def _allowed_memory_depth_values(self) -> set[int]:
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
