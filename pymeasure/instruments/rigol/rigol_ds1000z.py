#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from collections.abc import Callable

import numpy as np
from pyvisa.constants import StatusCode
from pyvisa.errors import VisaIOError

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments._strenum import StrEnum
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

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


def _parse_waveform_preamble(reply: str) -> dict[str, int | float]:
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
        raise RuntimeError("Invalid binary block header.")
    length_digits = int(header[1:2].decode("ascii"))
    length = int(read_bytes_func(length_digits).decode("ascii"))
    payload = read_bytes_func(length)
    # The trailing terminator is not sent by every firmware revision.
    try:
        read_bytes_func(1, break_on_termchar=True)
    except VisaIOError as exc:
        if exc.error_code != StatusCode.error_timeout:
            raise
        log.debug("No trailing terminator after binary block.")
    return payload


def _normalize_memory_depth_value(
    value: str | int,
    *,
    allowed_values: set[int] | None = None,
    allowed_values_factory: Callable[[], set[int]] | None = None,
) -> tuple[str, int | None]:
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

    if allowed_values is None and allowed_values_factory is not None:
        allowed_values = allowed_values_factory()
    if allowed_values is not None and numeric not in allowed_values:
        raise ValueError(
            f"Memory depth {numeric} pts is not permitted for the current "
            f"channel configuration. Allowed values: {sorted(allowed_values)} or 'AUTO'."
        )
    return str(numeric), numeric


def _parse_memory_depth(reply: str) -> int | str:
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
        cast=str,
    )

    bandwidth_limit_enabled = Channel.control(
        ":CHAN{ch}:BWL?",
        ":CHAN{ch}:BWL %s",
        "Control the 20 MHz bandwidth limit filter (bool).",
        validator=strict_discrete_set,
        values={True: "20M", False: "OFF"},
        map_values=True,
        cast=str,
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
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
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
        "Control the probe attenuation ratio (float strictly between 0.0001 and 1000).",
        validator=strict_range,
        values=[0.0001, 1000],
    )

    unit = Channel.control(
        ":CHAN{ch}:UNIT?",
        ":CHAN{ch}:UNIT %s",
        "Control the channel unit (str): 'VOLT', 'WATT', 'AMP', or 'UNKN'.",
        validator=strict_discrete_set,
        values=["VOLT", "WATT", "AMP", "UNKN"],
        cast=str,
    )


class RigolDS1000ZDisplay(Channel):
    """Display subsystem for Rigol DS/MSO 1000Z (:DISPlay.*)."""

    def insert_id(self, command):
        """Hand on the command without inserting an id."""
        return command

    def clear(self) -> None:
        """Clear all waveforms on the screen (equiv. front-panel CLEAR)."""
        self.write(":DISP:CLE")

    def grab_image(
        self,
        color: bool = True,
        invert: bool = False,
        image_format: DisplayImageFormat | str = DisplayImageFormat.BMP24,
    ) -> bytes:
        """Return the current screen image bytes (payload only, TMC header removed).

        :param bool color: True for color, False for intensity graded color. Defaults to True.
        :param bool invert: True to invert the colors, False for normal colors. Defaults to False.
        :param DisplayImageFormat | str image_format: One of BMP24, BMP8, PNG, JPEG, TIFF.
            Defaults to BMP24.
        :return bytes: Image file bytes (e.g. PNG, BMP, …), without the TMC header.
        """
        if isinstance(image_format, DisplayImageFormat):
            fmt = image_format.value
        else:
            fmt = str(image_format).upper()
            if fmt not in {f.value for f in DisplayImageFormat}:
                raise ValueError(f"Unsupported image format: {image_format}")

        # The brackets in the manual's syntax ":DISP:DATA? [<color>,<invert>,<format>]" mark the
        # arguments as optional; they must not be sent. The bare query keeps working on firmware
        # that does not accept the arguments.
        if color and not invert and fmt == DisplayImageFormat.BMP24.value:
            cmd = ":DISP:DATA?"
        else:
            col = "ON" if color else "OFF"
            inv = "ON" if invert else "OFF"
            cmd = f":DISP:DATA? {col},{inv},{fmt}"
        self.write(cmd)
        return _parse_tmc_block(self.read_bytes)

    type = Channel.control(
        ":DISP:TYPE?",
        ":DISP:TYPE %s",
        "Control the display type (str): 'VECT' (vectors) or 'DOTS'.",
        validator=strict_discrete_set,
        values=[DisplayType.VECTORS.value, DisplayType.DOTS.value],
        cast=str,
    )

    persistence = Channel.control(
        ":DISP:GRAD:TIME?",
        ":DISP:GRAD:TIME %s",
        "Control persistence time (float): 0 for minimum, 0.1, 0.2, 0.5, 1, 5, 10, "
        "or inf.",
        validator=strict_discrete_set,
        values={
            0: "MIN", 0.1: "0.1", 0.2: "0.2", 0.5: "0.5",
            1: "1", 5: "5", 10: "10", float("inf"): "INF",
        },
        map_values=True,
        get_process=lambda v: str(v).upper(),
        cast=str,
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
        cast=str,
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
            scope.clear()

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
    (0, 8, or 16). The hint is required before setting a numeric memory depth; without it the
    setter raises :class:`ValueError`. ``"AUTO"`` does not require the hint.

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

        image = scope.display.grab_image(image_format="PNG")
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
        self._digital_channel_hint: int | None = None

    channel_1 = Instrument.ChannelCreator(RigolDS1000ZChannel, "1")
    channel_2 = Instrument.ChannelCreator(RigolDS1000ZChannel, "2")
    channel_3 = Instrument.ChannelCreator(RigolDS1000ZChannel, "3")
    channel_4 = Instrument.ChannelCreator(RigolDS1000ZChannel, "4")
    display = Instrument.ChannelCreator(RigolDS1000ZDisplay, "")

    acquisition_type = Instrument.control(
        ":ACQ:TYPE?",
        ":ACQ:TYPE %s",
        "Control the acquisition type (str): 'NORM', 'AVER', 'PEAK', or 'HRES'.",
        validator=strict_discrete_set,
        values=[mode.value for mode in AcquireType],
        cast=str,
    )

    average_count = Instrument.control(
        ":ACQ:AVE?",
        ":ACQ:AVE %d",
        "Control the number of waveforms averaged when the acquisition type is 'AVER' "
        "(int, power of two strictly from 2 to 1024).",
        validator=strict_discrete_set,
        values=[2**n for n in range(1, 11)],
        cast=int,
    )

    sample_rate = Instrument.measurement(
        ":ACQ:SRAT?",
        "Measure the current sample rate in samples per second (float).",
        cast=float,
    )

    @property
    def memory_depth(self) -> int | str:
        """Control the acquisition memory depth in points or 'AUTO'.

        The allowable discrete values depend on how many analogue and digital
        channels are currently enabled. The driver counts the active analogue
        inputs and uses :meth:`set_digital_channel_hint` for the digital pod state
        before applying validation.

        Digital pod activity cannot be queried reliably across all models, so you must set the
        hint before setting a numeric memory depth. ``"AUTO"`` does not require the hint.
        """

        reply = self.ask(":ACQ:MDEP?")
        return _parse_memory_depth(reply)

    @memory_depth.setter
    def memory_depth(self, value: str | int) -> None:
        target, _ = _normalize_memory_depth_value(
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
        cast=str,
    )

    trigger_slope_positive = Instrument.control(
        ":TRIG:EDGE:SLOP?",
        ":TRIG:EDGE:SLOP %s",
        "Control whether the trigger slope is positive (bool).",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "POS", False: "NEG"},
        cast=str,
    )

    trigger_coupling = Instrument.control(
        ":TRIG:COUP?",
        ":TRIG:COUP %s",
        "Control the trigger coupling mode (str strictly 'AC', 'DC', 'LFR', or 'HFR').",
        validator=strict_discrete_set,
        values=["AC", "DC", "LFR", "HFR"],
        cast=str,
    )

    trigger_sweep = Instrument.control(
        ":TRIG:SWE?",
        ":TRIG:SWE %s",
        "Control the trigger sweep mode (str): 'AUTO', 'NORM', or 'SING'.",
        validator=strict_discrete_set,
        values=["AUTO", "NORM", "SING"],
        cast=str,
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
        cast=str,
    )

    waveform_mode = Instrument.control(
        ":WAV:MODE?",
        ":WAV:MODE %s",
        "Control the waveform acquisition mode for transfer (:class:`WaveformMode`).",
        validator=_validate_enum_member,
        values=WaveformMode,
        get_process=WaveformMode,
        set_process=lambda mode: mode.value,
        cast=str,
    )

    waveform_format = Instrument.control(
        ":WAV:FORM?",
        ":WAV:FORM %s",
        "Control the waveform data format for transfer (:class:`WaveformFormat`).",
        validator=_validate_enum_member,
        values=WaveformFormat,
        get_process=WaveformFormat,
        set_process=lambda fmt: fmt.value,
        cast=str,
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

    def clear_waveforms(self):
        """Clear all the waveforms on the screen."""
        self.write(":CLE")

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

    def abort_calibration(self):
        """Exit the self-calibration at any time."""
        self.write(":CAL:QUIT")

    def configure_edge_trigger(
        self,
        source: str | int,
        level: float = 0.0,
        slope_positive: bool = True,
        coupling: str = "DC",
        sweep: str = "AUTO",
    ):
        """Configure the edge trigger settings in a single call.

        :param source: Channel index (1-based int) or SCPI source name (e.g. ``"CHAN1"``).
        :param float level: Trigger level in volts.
        :param bool slope_positive: True for rising edge, False for falling edge.
        :param str coupling: Trigger coupling mode (e.g. ``"DC"``, ``"AC"``).
        :param str sweep: Trigger sweep mode (``"AUTO"``, ``"NORM"``, or ``"SING"``).
        """

        if isinstance(source, int):
            if not 1 <= source <= self._channel_count:
                raise ValueError("Invalid channel index for trigger source.")
            source_value = f"CHAN{source}"
        else:
            source_value = str(source).upper()
        self.trigger_source = source_value
        self.trigger_level = level
        self.trigger_slope_positive = slope_positive
        self.trigger_coupling = coupling
        self.trigger_sweep = sweep

    def force_trigger(self):
        """Generate a trigger signal regardless of the current trigger conditions.

        This command is only applicable to the normal and single trigger modes.
        """
        self.write(":TFOR")

    def get_waveform_preamble(self) -> dict[str, int | float]:
        """Return the parsed contents of `:WAVeform:PREamble?`."""
        reply = self.ask(":WAV:PRE?")
        return _parse_waveform_preamble(reply)

    def read_waveform(
        self,
        source: str | int = "CHAN1",
        mode: WaveformMode | str = WaveformMode.NORMAL,
        data_format: WaveformFormat | str = WaveformFormat.BYTE,
        start: int | None = None,
        stop: int | None = None,
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
        total_points = int(preamble["points"])
        if total_points <= 0:
            empty = np.array([], dtype=float)
            return empty, empty

        start, stop = self._derive_waveform_window(total_points, start, stop)

        raw_data = self._collect_waveform_data(format_enum, start, stop)
        voltage = self._scale_waveform_data(format_enum, raw_data, preamble)
        time = self._generate_time_axis(preamble, start, voltage.size)

        return time, voltage

    def _resolve_waveform_source(self, source: str | int) -> str:
        if isinstance(source, int):
            if not 1 <= source <= self._channel_count:
                raise ValueError("Invalid channel index for waveform read.")
            return f"CHAN{source}"
        return str(source).upper()

    @staticmethod
    def _resolve_waveform_mode(mode: WaveformMode | str) -> WaveformMode:
        if isinstance(mode, WaveformMode):
            return mode
        mode_value = str(mode).upper()
        try:
            return WaveformMode(mode_value)
        except ValueError as exc:
            raise ValueError(f"Unsupported waveform mode: {mode}") from exc

    @staticmethod
    def _resolve_waveform_format(data_format: WaveformFormat | str) -> WaveformFormat:
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
        start: int | None,
        stop: int | None,
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
        payload = _parse_tmc_block(self.read_bytes)
        dtype = np.uint8 if format_enum == WaveformFormat.BYTE else np.uint16
        return np.frombuffer(payload, dtype=dtype).astype(np.float64)

    @staticmethod
    def _scale_waveform_data(
        format_enum: WaveformFormat,
        raw_data: np.ndarray,
        preamble: dict[str, int | float],
    ) -> np.ndarray:
        if format_enum == WaveformFormat.ASCII:
            return raw_data
        y_origin = preamble["y_origin"]
        y_reference = preamble["y_reference"]
        y_increment = preamble["y_increment"]
        return (raw_data - y_origin - y_reference) * y_increment

    @staticmethod
    def _generate_time_axis(
        preamble: dict[str, int | float],
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
    def set_digital_channel_hint(self, active_lines: int | None) -> None:
        """Hint the number of enabled digital lines for memory-depth validation.

        :param int active_lines: Use 0 when the MSO pod is disabled, 8 or 16 when the
            corresponding digital groups are enabled. ``None`` clears the hint; numeric
            memory depths are then rejected until a new hint is set.
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
            except ValueError:
                # If the reply cannot be parsed, assume the channel is active to keep the
                # validation conservative.
                log.debug("Could not read display state of channel %d.", index)
                count += 1
        return count

    def _active_digital_channel_count(self) -> int:
        if self._digital_channel_hint is not None:
            return self._digital_channel_hint
        raise ValueError(
            "Digital channel state is unknown. Call set_digital_channel_hint() "
            "to specify the number of active digital lines (0, 8, or 16) "
            "before setting a numeric memory depth."
        )
