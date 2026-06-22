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

from enum import Enum, IntFlag, IntEnum

from typing import Any, TypedDict, TypeVar
from collections.abc import Callable, Sequence

from pymeasure.adapters import Adapter
from pymeasure.instruments.common_base import CommonBase, cast_or_str
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set


T = TypeVar("T")


class Capabilities(IntFlag):
    # Bit 0 is lit if sensor can measure power.
    # Bit 1 is lit if sensor can measure energy.
    # Bit 18 is lit if head can measure temperature.
    # Bit 31 is lit if head can measure frequency.
    # All other bits are reserved and are not guaranteed to be 0 or 1
    POWER = 1
    ENERGY = 2
    TEMPERATURE = 1 << 18
    FREQUENCY = 1 << 31


class Modes(IntEnum):
    PASSIVE = 1
    POWER = 2
    ENERGY = 3
    EXPOSURE = 4
    POSITION = 5
    LUX = 7
    FOOTCANDLES = 8
    IRRADIANCE = 9
    DOSAGE = 10
    HOLD_MODE = 11
    CONTINUOUS_MODE = 12
    PULSED_POWER = 14
    FAST_POWER = 15
    LOW_FREQUENCY_POWER = 16


class LegacyModes(Enum):
    POWER = "FP"
    ENERGY = "FE"
    POSITION = "FB"
    EXPOSURE = "FX"


class Keys(IntEnum):
    LEFT_LEFT = 0
    MIDDLE_LEFT = 1
    MIDDLE_RIGHT = 2
    RIGHT_RIGHT = 3
    ARROW_RIGHT = 4
    ARROW_LEFT = 5
    ARROW_UP = 6
    ARROW_DOWN = 7
    ENTER = 8


class ScreenModes(IntEnum):
    POWER = 0
    ENERGY = 1
    NON_MEASUREMENT = 2
    NO_SENSOR = 3
    POSITION = 5


class HeadInfo(TypedDict):
    sensortype: str
    serialnumber: str
    name: str
    capabilities: Capabilities


class OphirCommunication(Instrument):
    """
    Base class for serial communication with Ophir devices, does not contain properties.

    This communication is ASCII based and suitable for RS-232 and USB communication.

    For USB exists a COM (win32) object as well, which can be used as an alternative to this driver.
    """

    def __init__(self, adapter: Adapter | str | int, name: str = "Ophir", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={
                "write_termination": "\r\n",
                "read_termination": "\r\n",
                "baud_rate": 9600,
            },
            usb={"write_termination": "\n", "read_termination": "\n"},
            **kwargs,
        )
        try:
            from pyvisa.constants import InterfaceType

            info = self.adapter.connection.resource_info(self.adapter.resource_name) # type: ignore
            self._is_rs232 = info.interface_type == InterfaceType.asrl
        except (AttributeError, TypeError):
            self._is_rs232 = False

    """
    The device expects a command and always responds.
    - Commands start with "$" and end with "\n". Commands consist mainly in two letters.
    - Response to successful command starts with "*" and ends with "\n".
    - Response to an invalid command starts with "?" and ends with "\n".
        It contains the original command.
    - RS-232 requires additionally carriage return before "\n".
    """

    def write(self, command: str, **kwargs) -> None:
        """Send a command to the device."""
        super().write("$" + command, **kwargs)

    def read(self, **kwargs) -> str:
        """Read a response."""
        reply = super().read(**kwargs)
        if not reply:
            raise ConnectionError("Empty response from device.")
        if reply[0] == "*":
            # Turn overrange into an inf float.
            return reply[1:].replace("OVER", "inf")
        else:
            raise ConnectionError(reply[1:])

    def values(
        self,
        command: str,
        separator: str | None = ",",
        cast: Callable[[str], T] = float,  # type: ignore[assignment]
        **kwargs,
    ) -> list[T | str]:
        """Write a command to the instrument and return a list of formatted values from the result.
        """
        return super().values(command, separator=None, cast=cast, **kwargs)

    def check_errors(self) -> list[Any]:
        """Check for errors after setting a value."""
        self.read()  # which does error-checking.
        return []


class OphirBase(OphirCommunication):
    """Represents an Ophir laser power/energy meter device.

    These commands are common to the USBI, Juno, Juno+, NovaII, Vega, StarLite, StarBright, and
    Centauri devices.
    Several of these devices implement even more commands, for which Mixin classes exist as well.
    Other devices, like Nova and Pulsar, only implement a subclass of these commands.
    """

    Capabilities = Capabilities
    LegacyModes = LegacyModes
    Modes = Modes
    ScreenModes = ScreenModes

    def __init__(self, adapter: Adapter | str | int, name: str = "Ophir", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.wavelength_get_process_list = self._wavelength_get_process

    # INFORMATION ABOUT DEVICE AND HEAD
    id = Instrument.measurement(
        "II",  # Instrument Information
        """Get information about the instrument.
        It is a list with 'instrument', 'serialNumber', 'name'.""",
        cast=str,
        separator=None,
    )

    software_version = Instrument.measurement(
        "VE",  # VErsion
        """Get the current software version.""",
        cast=str,
    )

    @property
    def head_information(self) -> HeadInfo:
        """Get information about the sensor head."""
        got = self.ask("HI")  # Head Information
        sensortype, serialnumber, name, capabilitiesString = got.split(maxsplit=3)
        # got is of type: sensortype serialnumber capabilities_byte
        capabilitiesInt = int(capabilitiesString, base=16)
        capabilities = Capabilities(capabilitiesInt)
        head_info: HeadInfo = {
            "sensortype": sensortype,
            "serialnumber": serialnumber,
            "name": name,
            "capabilities": capabilities,
        }
        return head_info

    head_type = Instrument.measurement(
        "HT",
        """Get the more specific head type.""",
        cast=str,  # Head Type
        # not Pulsar
    )

    baud_rate = Instrument.control(
        "BR0",
        "BR%i",  # Baud Rate
        """Control the communication baud rate.""",
        check_set_errors=True,
        values={9600: 1, 19200: 2, 38400: 3, 300: 4, 1200: 5, 4800: 6},
        map_values=True,
        get_process_list=lambda v: v[int(v[0])],
    )

    def reset(self) -> None:
        """Reset the device, for example after a head change."""
        self.wavelength_values = None
        self.range_values = None
        self.ask("RE")

    def start_streaming(self, downsampling: int = 0) -> None:
        """Start streaming mode, where the device sends every `downsampling` measurement."""
        if self._is_rs232:
            # only for RS232 communication. Only needed once.
            self.ask("DU")  # full DUplex, necessary for streaming mode
        self.ask(f"CS1{downsampling or ''}")
        # Continuous Send. CS {int(on/off)} {every X measurement} {response format}

    def stop_streaming(self) -> None:
        """Stop streaming mode."""
        self.ask("CS0")

    # CONFIG
    # Measurement in general
    mode = Instrument.control(
        "MM0",
        "MM%i",  # Measurement Mode
        """Control the measurement mode of the device, use :class:`.Modes`.""",
        values=Modes,
        check_set_errors=True,
        get_process=Modes,
        dynamic=True,
        # not USBI, not Pulsar
    )

    mode_legacy = Instrument.setting(
        "%s",
        """Set the measurement mode with one of :class:`.LegacyModes`,
        if possible, use :attr:`mode` instead.""",
        values=LegacyModes,
        set_process=lambda v: v.value,
        check_set_errors=True,
    )

    units = Instrument.measurement(
        "SI",  # Send unIts
        """Get the current measurement unit.""",
        cast=str,
    )

    # Range
    range = Instrument.control(
        "RN",  # Read raNge
        "WN%i",  # Write raNge
        """Control the current range setting, See :attr:`range_entries` for possible values.""",
        cast=int,
        values=[],
        map_values=True,
        check_set_errors=True,
        validator=strict_discrete_set,
        dynamic=True,
    )

    range_max = Instrument.measurement(
        "SX",  # Send maX
        """Get maximum allowable reading at current range.""",
        # not Pulsar
    )

    actual_range = Instrument.measurement(
        "GU",  # Get range in Use
        """Get the actual range in use, particularly useful if :attr:`range` is 'AUTO'.""",
        # not Pulsar
    )

    def _extract_ranges(self, ranges: list[str]) -> dict[str, int]:
        index = -1 if ranges[1] == "AUTO" else 0
        indices: dict[str, int] = {}
        for rng in ranges[1:]:
            indices[rng] = index
            index += 1
        self.range_values = indices
        self.range_map_values = True
        return indices

    @property
    def range_entries(self) -> dict[str, int]:
        """
        Get all possible ranges and their index.

        Auto is, if present, -1. The range with the highest numeric value is 0.
        """
        # doesn't work with NOVA I
        ranges = self.values("AR", separator=None, cast=str)
        return self._extract_ranges(ranges)

    range_index = Instrument.control(
        "RN",
        "WN%i",
        """Control the index of the range in the list of ranges.""",
        set_process=lambda v: v + 1,
        check_set_errors=True,
        cast=int,
    )

    # Wavelength
    def _extract_wavelengths(
        self, values: list[str]
    ) -> tuple[float | None | str, tuple[float, float] | None, Sequence[float | str | None]]:
        if values[0] == "CONTINUOUS":
            limits = (float(values[1]), float(values[2]))
            entries = [None if v == "NONE" else float(v) for v in values[4:]]
            current = entries[int(values[3]) - 1]
        else:
            entries = values[2:]
            current = entries[int(values[1]) - 1]
            limits = None
        self.wavelength_values = [None] + entries  # indices start with 1
        self.wavelength_value_values = limits
        return current, limits, entries

    def _wavelength_get_process(self, values):
        return self._extract_wavelengths(values)[0]

    @property
    def wavelength_list(
        self,
    ) -> tuple[tuple[float, float] | None, Sequence[float | str | None]]:
        """Get wavelength limits for continuous sensor and wavelength list."""
        values = self.values("AW", cast=str)  # All Wavelengths
        current, limits, entries = self._extract_wavelengths(values)
        return limits, entries

    wavelength = Instrument.control(
        "AW",
        "WI%i",
        """Control the selected wavelength (range) in list of wavelengths.

        Read this attribute or :attr:`wavelength_list` to update the list of available
        wavelengths. Use :attr:`wavelength_value` to set the value of the current wavelength entry.
        """,
        # AW, WI not available for NOVA I
        cast=str,
        validator=strict_discrete_set,
        map_values=True,
        get_process_list=lambda v: v,
        check_set_errors=True,
        dynamic=True,
    )

    wavelength_value = Instrument.setting(
        "WL %i",
        """Set the wavelength of the currently selected entry in nm (continuous sensor only, int).
        """,
        values=(0, float("inf")),
        validator=strict_range,
        dynamic=True,
    )

    wavelength_index = Instrument.control(
        "AW",
        "WI%i",
        """Control the index of the wavelength in the wavelength list.""",
        cast=cast_or_str(float),
        get_process_list=lambda v: int(v[3]) if v[0] == "CONTINUOUS" else int(v[1]),
        set_process=lambda v: v + 1,
        check_set_errors=True,
    )

    def define_wavelength_entry(self, index: int, value: int) -> None:
        """Define the wavelength in nm at index (0 based) in the wavelength list.

        The slot of the wavelength list must be empty, you can clear it with
        :meth:`clear_wavelength_entry`.
        See the currently defined entries and wavelength limits with :attr:`wavelength_list`.
        """
        if not 0 <= index <= 5:
            raise ValueError("Index must be between 0 and 5.")
        self.ask(f"WD {index + 1} {value}")

    def clear_wavelength_entry(self, index: int) -> None:
        """Clear the wavelength at index (0 based) in the wavelength list.

        It must not be the currently active index.
        To set a new value use :meth:`define_wavelength_entry`.
        See the currently defined entries and wavelength limits with :attr:`wavelength_list`.
        """
        if not 0 <= index <= 5:
            raise ValueError("Index must be between 0 and 5.")
        self.ask(f"WE {index + 1}")

    """
        # Additional commands not yet implemented
        WW set to discrete wavelenth
    """

    # Specific measurement
    diffuser = Instrument.control(
        "DQ",
        "DQ%i",  # Diffuser Query
        """Control pyroelectric sensors diffuser.""",
        get_process_list=lambda v: v[int(v[0])],
        cast=str,
        values={"IN": 2, "OUT": 1},
        map_values=True,
        check_set_errors=True,
        # not Pulsar
    )

    sensor_filter = Instrument.control(
        "FQ",
        "FQ%i",  # Filter Query
        """Control photodiode sensors filter.""",
        get_process_list=lambda v: v[int(v[0])],
        cast=str,
        values={"IN": 2, "OUT": 1},
        map_values=True,
        check_set_errors=True,
    )

    mains = Instrument.control(
        "MA",
        "MA%i",  # MAins
        """Control the configured mains frequency.""",
        values={"50Hz": 1, "60Hz": 2},
        map_values=True,
        cast=str,
        check_set_errors=True,
        get_process_list=lambda v: v[int(v[0])],
    )

    bc20_mode = Instrument.control(
        "BQ",
        "BQ%i",  # Bc20 Query
        """Control BC20 sensor mode. Some devices can use `mode` as well.""",
        cast=str,
        get_process_list=lambda v: v[int(v[0])],
        values={"HOLD": 1, "CONTINUOUS": 2},
        map_values=True,
        check_set_errors=True,
        # not StarLite, Pulsar, Centauri
    )

    threshold = Instrument.control(
        "UT",  # User Threshold
        "UT%i",
        """Control the threshold of the sensor as fraction (4 decimals),
        returns current, min, and max.""",
        get_process_list=lambda vs: [v / 10000 for v in vs],
        set_process=lambda v: round(v * 10000),
        check_set_errors=True,
        # not Pulsar
    )

    # Other settings
    screen_mode = Instrument.setting(
        "FS%i",  # Force Screen
        """Set the device to a specific screen mode, use :class:`.ScreenModes`.""",
        values=ScreenModes,
        check_set_errors=True,
        # not Pulsar
    )

    def save_head_configuration(self, config: str) -> None:
        """
        Save selected sensor configuration.

        - 'S' for startup
        - 'C' for calibration
        - 'R' for Responsive for thermopile sensors

        Response is `"*SAVED"` or `"*UNCHANGED"` or `"?FAILED"`.
        """
        self.ask(f"HC{config}")  # Head Configuration

    def save_instrument_configuration(self) -> None:
        """
        Save instrument configuration.

        Response is `"*SAVED"` or `"*UNCHANGED"` or `"?FAILED"`.
        """
        self.ask("IC")  # Instrument Configuration

    def zero(self) -> None:
        """Zero the measurement circuitry. Recommended once every two months."""
        self.ask("ZE")  # ZEro

    def zero_abort(self) -> None:
        """Abort a zeroing, if underway and return the status as string."""
        self.ask("ZA")  # Zero Abort

    zero_status = Instrument.measurement(
        "ZQ",  # Zero Query
        """Get the status of the zeroing process.""",
        cast=str,
        get_process_list=lambda v: " ".join(v),
    )

    def save_zero(self) -> None:
        """Save result of zeroing process to memory."""
        self.ask("ZS")  # Zero Save

    # ENERGY
    maximum_frequency = Instrument.measurement(
        "MF",  # Maximum Frequency
        """Get the maximum sensor pulse frequency for energy pulses in Hz.""",
        # not Pulsar
    )

    pulse_length = Instrument.control(
        "PL",  # Pulse Length
        "PL%i",
        """Control the maximum pulse length for measurement.""",
        cast=str,
        get_process_list=lambda v: (v[int(v[0])], v[1:]),
        check_set_errors=True,
        dynamic=True,
        # not Pulsar
    )

    energy_threshold = Instrument.control(
        "ET",
        "ET%i",
        """Control the energy threshold of the sensor, returns a list of possible values.""",
        get_process_list=lambda v: (v[int(v[0])], v[1:]),
        cast=str,
        values={"LOW": 1, "MEDIUM": 2, "HIGH": 3},
        map_values=True,
        check_set_errors=True,
    )

    energy_ready = Instrument.measurement(
        "ER",
        """Get whether the sensor is ready for a new energy measurement.""",
        cast=bool,
    )

    energy_flag = Instrument.measurement(
        "EF",
        """Get whether a new energy measurement arrived.""",
        cast=bool,
    )

    energy = Instrument.measurement(
        "SE",
        """Get the most recent energy measurement in J.""",
        dynamic=True,  # Send Energy
    )

    frequency = Instrument.measurement(
        "SF",  # Send Frequency
        """Get latest frequency in Hz.""",
        # not Pulsar
    )

    # ENERGY EXPOSURE: only Pyro
    exposure_energy = Instrument.measurement(
        "EE",
        """Get exposure energy in J, count of pulses, and time in s.""",
        get_process_list=lambda v: [*v[:2], v[2] / 10],
        # not Pulsar
    )

    # POWER
    power = Instrument.measurement(
        "SP",
        """Get next power measurement in W.""",
        dynamic=True,  # Send Power
    )

    # BEAM TRACKING
    position = Instrument.measurement(
        "BT",  # BeamTrack
        """Get the position (x,y) and spot size in mm.""",
        cast=str,
        get_process_list=lambda v: [float(v[3]), float(v[5]), float(v[7])],
        # not Pulsar
    )


class ChannelMixin:
    """Mixin for channels.

    For Pulsar, Centauri.
    """

    channel = Instrument.control(
        "CL0",
        "CL%i",  # select Channel
        """The channel for Pulsar or Centauri devices, starts at 1.""",
        cast=int,
        check_set_errors=True,
    )


class AverageMixin:
    """Mixin for averaging methods.

    For Nova II, Vega.
    """

    average_configuration = Instrument.control(
        "AQ",
        "AQ%i",  # Average Query
        """Control the averaging of the sensor.""",
        check_set_errors=True,
    )

    average_flag = Instrument.measurement(
        "AF",
        """Get whether a new average reading has been processed.""",
        values=[False, True],
        map_values=True,
    )

    average = Instrument.measurement(
        "SG",
        """Get the latest averaged measurement.""",  # Send averaGe
    )


class KeyMixin(CommonBase):
    """Mixin for pressing keys remotely."""

    Keys = Keys

    def key_legends(self) -> str:
        """Return the legends of the keys. A tilde '~' indicates active key."""
        return self.ask("KL")  # Key Legends
        # Nova, Vega, NovaII, LaserStar

    def press_key(self, key: str | int | Keys) -> None:
        """
        Simulate a keypress.

        Below display from left to right (0 to 3)
        Arrows: right (4), left (5), up (6), down (7),
        Enter(8).
        """
        # Nova, NovaII, Vega, StarLite, StarBright, LaserStar
        keys = {
            "leftmost": 0,
            "left-ish": 1,
            "right-ish": 2,
            "rightmost": 3,
            "arrowright": 4,
            "arrowleft": 5,
            "arrowup": 6,
            "arrowdown": 7,
            "enter": 8,
        }
        if isinstance(key, str):
            key = keys[key]
        self.ask(f"SK{key}")  # Simulate Key-press
