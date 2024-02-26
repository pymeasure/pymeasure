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

import enum
from typing import Union

from pymeasure.instruments import Instrument

from pyvisa import VisaIOError


class Capabilities(enum.IntFlag):
    # Bit 0 is lit if sensor can measure power.
    # Bit 1 is lit if sensor can measure energy.
    # Bit 18 is lit if head can measure temperature.
    # Bit 31 is lit if head can measure frequency.
    # All other bits are reserved and are not guaranteed to be 0 or 1
    POWER = 1
    ENERGY = 2
    TEMPERATURE = 1 << 18
    FREQUENCY = 1 << 31


class Modes(enum.IntEnum):
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


class LegacyModes(enum.StrEnum):
    POWER = "FP"
    ENERGY = "FE"
    POSITION = "FB"
    EXPOSURE = "FX"


class Keys(enum.IntEnum):
    LEFT_LEFT = 0
    MIDDLE_LEFT = 1
    MIDDLE_RIGHT = 2
    RIGHT_RIGHT = 3
    ARROW_RIGHT = 4
    ARROW_LEFT = 5
    ARROW_UP = 6
    ARROW_DOWN = 7
    ENTER = 8


class ScreenModes(enum.IntEnum):
    POWER = 0
    ENERGY = 1
    NON_MEASUREMENT = 2
    NO_SENSOR = 3
    POSITION = 5


class OphirCommunication(Instrument):
    """
    Base class for serial communication with Ophir devices, does not contain properties.

    This communication is ASCII based and suitable for RS-232 and USB
    communication.
    For USB exists a COM (win32) object as well.
    """

    def __init__(self, adapter, name="Ophir", **kwargs):
        """
        Initialize the communication with the device.

        Parameters
        ----------
        number : int
            Number of the COM-Port or USB device.
        connection : str, optional
            Type of connection, either "COM" or "USB". The default is "COM".
        baud_rate : int, optional
            The serial COM baud rate. The default is 9600.
        """
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            asrl={
                "write_termination": "\r\n",
                "read_termination": "\r\n",
                "baud_rate": 9600,
            },
            usb={"write_termination": "\n", "read_termination": "\n"},
            **kwargs,
        )
        # TODO verify and test USB communication
        try:
            self.device_name = self.id[0]
        except VisaIOError:  # timeout
            raise
        # self.getHeadInformation()

    """
    The device expects a command and always responds.
    - Commands start with "$" and end with \n. Mainly two letter commands
    - Response to successful command starts with "*" and ends with \n.
    - Response to an invalid command starts with "?" and ends with \n.
        It contains the original command.
    - RS-232 requires additionally carriage return before \n.
    """

    def write(self, command):
        """Send a command to the device."""
        super().write("$" + command)

    def read(self):
        """Read a response."""
        reply = super().read()
        if reply[0] == "*":
            # Turn overrange into an inf float.
            return reply[1:].replace("OVER", "inf")
        else:
            raise ConnectionError(reply[1:])

    def values(self, command, **kwargs):
        """Read values."""
        kwargs["separator"] = None
        return super().values(command, **kwargs)

    def check_errors(self):
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

    # INFORMATION ABOUT DEVICE AND HEAD
    id = Instrument.measurement(
        "II",  # Instrument Information
        """Get information about the instrument.
        List with 'instrument', 'serialNumber', 'name'.""",
        cast=str,
        separator=None,
    )

    software_version = Instrument.measurement(
        "VE",  # VErsion
        """Get the current software version.""",
        cast=str,
    )

    @property
    def head_information(self):
        """Get information about the sensor head."""
        got = self.ask("HI")  # Head Information
        sensortype, serialnumber, name, capabilitiesString = got.split(maxsplit=3)
        # got is of type: sensortype serialnumber capabilities_byte
        capabilitiesInt = int(capabilitiesString, base=16)
        capabilities = Capabilities(capabilitiesInt)
        self.headInfo = {
            "sensortype": sensortype,
            "serialnumber": serialnumber,
            "name": name,
            "capabilities": capabilities,
        }
        return self.headInfo

    head_type = Instrument.measurement(
        "HT",
        """Get the more specific head type.""",
        cast=str,  # Head Type
        # not Pulsar
    )

    baud_rate = Instrument.control(
        "BR0",
        "BR%i",  # Baud Rate
        """Get the communication baud rate.""",
        check_set_errors=True,
        values={9600: 1, 19200: 2, 38400: 3, 300: 4, 1200: 5, 4800: 6},
        map_values=True,
        get_process=lambda v: v[v[0]],
    )

    def reset(self):
        """Reset the device, for example after head change."""
        return self.ask("RE")

    # TODO streaming mode:
    def startStreaming(self, downsampling=0):
        """Start streaming mode, where the device sends every `downsampling` measurement."""
        RS232 = True  # TODO make the check
        if RS232:
            # only for RS232 kommunication. Only needed once.
            self.ask("DU")  # full DUplex, necessary for streaming mode
        self.ask("CS1{downsampling if downsampling else ''}")
        # Continuous Send. CS {int(on/off)} {every X measurement} {response format}

    def stopStreaming(self):
        """Stop streaming mode."""
        self.ask("CS0")

    # CONFIG
    # Measurement in general
    mode = Instrument.control(
        "MM0",
        "MM%i",  # Measurement Mode
        """Control the measurement mode of the device, use :class:`Modes`.""",
        values=Modes,
        check_set_errors=True,
        get_process=Modes,
        dynamic=True,
        # not USBI, not Pulsar
    )

    mode_legacy = Instrument.setting(
        "%s",
        """Set the measurement mode with one of :class:`LegacyModes`,
        if possible, use :attr:`mode` instead.""",
        values=LegacyModes,
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
        """Control the current range setting.""",
        cast=int,
        check_set_errors=True,
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

    def getAllRanges(self):
        """
        Get all possible ranges.

        Auto is, if present, -1. The range with the highest numeric value is 0.
        """
        # doesn't work with NOVA I
        ranges = self.values("AR", separator=None, cast=str)
        index = -1 if ranges[1] == "AUTO" else 0
        values = {}
        for range in ranges[1:]:
            values[range] = index
            index += 1
        self.range_values = values
        self.range_map_values = True
        return values

    # Wavelength
    # TODO all the wavelength suff. How to implement it well?
    @property
    def wavelength_options(self):
        """Get a list of all wavelengths or a list of the wavelength limits."""
        values = self.values("AW", cast=str)  # All Wavelengths
        if values[0] == "CONTINUOUS":
            options = [
                values[0],
                [float(v) for v in values[4:]],
                [float(values[1], float(values[2]))],
            ]
        else:
            options = [values[0], values[2:]]
        self.wavelength_values = [None] + options[1]
        return options

    wavelength = Instrument.control(
        "AW",
        "WI%i",
        """Control the selected wavelength range""",
        # AW, WI not available for NOVA I
        cast=str,
        map_values=True,
        get_process=lambda v: v[int(v[1]) + 1]
        if v[0] == "DISCRETE"
        else v[int(v[3] + 3)],
        check_set_errors=True,
        dynamic=True,
    )

    wavelength_value = Instrument.setting(
        "WL %i", """Set the wavelength of the currently selected index in nm (int)."""
    )

    def get_all_wavelengths(self):
        """Get all possible wavelengths."""
        # doesn't work with NOVA I
        return self.ask("AW")  # All Wavelengths

    """
        TODO
        WE erase a wavelength from the list
        WI set the wavelength to index
        WL set currently active wavelength to value
        WW set to discrete wavelenth
        WD Add a wavelength to the list
    """

    # Specific measurement
    diffuser = Instrument.control(
        "DQ",
        "DQ%i",  # Diffuser Query
        """Control pyroelectric sensors diffuser.""",
        get_process=lambda v: v[int(v[0])],
        cast=str,
        values={"IN": 2, "OUT": 1},
        map_values=True,
        check_set_errors=True,
        # not Pulsar
    )

    filter = Instrument.control(
        "FQ",
        "FQ%i",  # Filter Query
        """Control photodiode sensors filter.""",
        get_process=lambda v: v[int(v[0])],
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
        get_process=lambda v: v[int(v[0])],
    )

    bc20_mode = Instrument.control(
        "BQ",
        "BQ%i",  # Bc20 Query
        """Control BC20 sensor mode. Some devices can use `mode` as well.""",
        cast=str,
        get_process=lambda v: v[int(v[0])],
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
        get_process=lambda vs: [v / 10000 for v in vs],
        set_process=lambda v: round(v * 10000),
        check_set_errors=True,
        # not Pulsar
    )

    # Other settings
    screen_mode = Instrument.setting(
        "FS%i",  # Force Screen
        """Set the device to a specific screen mode, use :class:`ScreenModes`.""",
        values=ScreenModes,
        check_set_errors=True,
        # not Pulsar
    )

    def save_head_configuration(self, config):
        """
        Save selected sensor configuration.

        - 'S' for startup
        - 'C' for calibration
        - 'R' for Responsive for thermopile sensors

        Response is "*SAVED" or "*UNCHANGED" or "?FAILED".
        """
        self.ask(f"HC{config}")  # Head Configuration

    def save_instrument_configuration(self):
        """
        Save instrument configuration.

        Response is "*SAVED" or "*UNCHANGED" or "?FAILED".
        """
        self.ask("IC")  # Instrument Configuration

    def zero(self):
        """Zero the measurement circuitry. Recommended once every two months."""
        self.ask("ZE")  # ZEro

    def zero_abort(self):
        """Abort a zeroing, if underway and return the status as string."""
        return self.ask("ZA")  # Zero Abort

    zero_status = Instrument.measurement(
        "ZQ",  # Zero Query
        """Get the status of the zeroing process.""",
        cast=str,
        get_process=lambda v: " ".join(v),
    )

    def save_zero(self):
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
        get_process=lambda v: (v[int(v[0])], v[1:]),
        check_set_errors=True,
        dynamic=True,
        # not Pulsar
    )

    energy_threshold = Instrument.control(
        "ET",
        "ET%i",
        """Control the energy threshold of the sensor, returns a list of possible values.""",
        get_process=lambda v: (v[int(v[0])], v[1:]),
        cast=str,
        values={"LOW": 1, "MEDIUM": 2, "HIGH": 3},
        map_values=True,
        check_get_errors=True,
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
        """Return the most recent energy measurement in J.""",
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
        get_process=lambda v: [*v[:2], v[2] / 10],
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
        get_process=lambda v: [float(v[3]), float(v[5]), float(v[7])],
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


class KeyMixin:
    """Mixin for pressing keys remotely."""

    Keys = Keys

    def key_legends(self):
        """Return the legends of the keys. A tilde '~' indicates active key."""
        return self.ask("KL")  # Key Legends
        # Nova, Vega, NovaII, LaserStar

    def press_key(self, key: Union[str, int, Keys]):
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
        return self.ask(f"SK{key}")  # Simulate Key-press
