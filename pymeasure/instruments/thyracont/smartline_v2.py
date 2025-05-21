#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from enum import IntEnum

from pymeasure.instruments import Instrument, Channel, validators
from pyvisa.constants import Parity, StopBits

from .smartline_v1 import calculate_checksum


def compose_data(value):
    """Generate a string with the length of `value` and the `value` itself afterwards.

    :param value: Value to send to the device.
    """
    value = f"{value}"
    return f"{len(value):02}{value}"


class Sources(IntEnum):
    COMBINATION = 0
    PIRANI = 1
    PIEZO = 2
    HOT_CATHODE = 3
    COLD_CATHODE = 4
    AMBIENT = 6
    RELATIVE = 7


def str_to_source(source_string):
    """Turn a string with a source number to a `Sources` enum. Useful for `cast` parameter."""
    return Sources(int(source_string))


gas_factor = Channel.control(
    "0C{ch}00", "0C{ch}%s", "Control the gas correction factor.",
    values=(0.2, 8),
    validator=validators.strict_range,
    set_process=compose_data,
)


class SensorChannel(Channel):
    """Generic channel for individual pressure sensors of a Transmitter."""

    _id = -1  # obligatory channel number, define in channel types

    def __init__(self, parent, id=None, **kwargs):
        # id parameter is necessary for usage with `ChannelCreator`.
        if id is None or id == self._id:
            super().__init__(parent, id=self._id, **kwargs)
        else:
            raise ValueError(f"Pirani ID has to be {self._id} for that channel type.")

    pressure = Channel.measurement(
        "0M{ch}00", """Get the current pressure in mbar.""",
        preprocess_reply=lambda r: r.replace("UR", "0").replace("OR", "inf"),
    )


class Pirani(SensorChannel):
    """Pirani sensor channel.

    A Pirani sensor measures the heat transfer in the gas. The reading depends on the gas type.
    The sensor reading is linear to the real pressure below some threshold, around 1 mbar.
    You may control a gas factor with :attr:`gas_factor`.
    """

    _id = Sources.PIRANI

    gas_factor = gas_factor

    statistics = Channel.measurement(
        "0PM011",
        """Get the sensor statistics as a tuple: wear in percent (negative: corrosion,
            positive: contamination), time since last adjustment in hours.""",
        preprocess_reply=lambda msg: msg.strip("W"),
        separator="A",
        cast=int,
        get_process=lambda vals: (vals[0], vals[1] / 4),
    )


class Piezo(SensorChannel):
    """Piezo sensor channel. A piezo sensor is independent of the gas present."""

    _id = Sources.PIEZO


class HotCathode(SensorChannel):
    """Hot cathode sensor channel."""

    _id = Sources.HOT_CATHODE

    filament_mode = Instrument.control(
        "0FC00", "2FC01%i",
        docs="""Control which hot cathode filament to use.
        ("2 if 1 defect", "Filament1", "Filament2", "toggle>1mbar")
        """,
        values={"2 if 1 defect": 0,
                "Filament1": 1,
                "Filament2": 2,
                "toggle>1mbar": 3},
        validator=validators.strict_discrete_set,
        map_values=True,
        cast=int,
        check_set_errors=True,
    )

    degas = Instrument.control(
        "0DG00", "2DG01%i",
        """Control the degas mode.""",
        values={True: 1, False: 0},
        map_values=True,
        validator=validators.strict_discrete_set,
        check_set_errors=True,
    )

    sensor_enabled = Instrument.control(
        "0CC00", "2CC01%i",
        """Control the state of the cathode.""",
        values={True: 1, False: 0},
        map_values=True,
        validator=validators.strict_discrete_set,
        check_set_errors=True,
    )
    active_filament = Instrument.measurement(
        "0FN00", "Get the current filament number.",
        cast=int,
    )

    filament_status = Instrument.measurement(
        "0FS00", """Get the status of the hot cathode filaments.""",
        values=["Filament 1 and 2 ok",
                "Filament 1 defective",
                "Filament 2 defective",
                "Filament 1 and 2 defective"],
        map_values=True,
    )

    gas_factor = gas_factor

    statistics = Channel.measurement(
        "0PM013",
        """Get the wear levels in percent as a tuple: filament 1, filament 2.""",
        preprocess_reply=lambda msg: msg.strip("F"),
        separator="S",
        cast=int,
    )

    # cathode status CA, cathode control mode CM


class ColdCathode(SensorChannel):
    """Cold cathode sensor channel."""

    _id = Sources.COLD_CATHODE

    gas_factor = gas_factor


class Ambient(SensorChannel):

    _id = Sources.AMBIENT


class Relative(SensorChannel):

    _id = Sources.RELATIVE


class SmartlineV2(Instrument):
    """
    A Thyracont vacuum sensor transmitter of the Smartline V2 series.

    You may subclass this Instrument and add the appropriate channels, see the following example.

    .. doctest::

        from pymeasure.instruments import Instrument
        from pymeasure.instruments.thyractont import SmartlineV2

        PiezoAndPiraniInstrument(SmartlineV2):
            piezo = Instrument.ChannelCreator(Piezo)
            pirani = Instrument.ChannelCreator(Pirani)

    Communication Protocol v2 via RS485:
        - Everything is sent as ASCII characters
        - Package (bytes and usage):
            - 0-2 address, 3 access code, 4-5 command, 6-7 data length.
            - if data: 8-n data to be sent, n+1 checksum, n+2 carriage return
            - if no data: 8 checksum, 9 carriage return
        - Access codes (request: master->transmitter, response: transmitter->master):
            - read: 0, 1
            - write: 2, 3
            - factory default: 4,5
            - error: -, 7
            - binary 8, 9
        - Data length is number of data in bytes (padding with zeroes on left)
        - Checksum: Add the decimal numbers of the characters before, mod 64, add 64, show as ASCII.

    :param adress: The device address in the range 1-16.
    """

    Sources = Sources

    errors = {'NO_DEF': "Invalid command for this device.",
              '_LOGIC': "Access Code is invalid or illogical command.",
              '_RANGE': "Value sent is out of range.",
              'ERROR1': "Sensor defect or stacked out.",
              'SYNTAX': "Wrong syntax or mode in data is invalid for this device.",
              'LENGTH': "Length of data is out of expected range.",
              '_CD_RE': "Calibration Data Read Error.",
              '_EP_RE': "EEPROM Read Error.",
              '_UNSUP': "Unsupported Data for that command.",
              '_SEDIS': "Sensor element disabled."}

    def __init__(self, adapter, name="Thyracont SmartlineV2 Transmitter", baud_rate=115200,
                 address=1, timeout=250,
                 **kwargs):
        super().__init__(adapter, name=name, includeSCPI=False,
                         write_termination="\r",
                         read_termination="\r",
                         timeout=timeout,
                         asrl={'baud_rate': baud_rate,
                               'parity': Parity.none,
                               'stop_bits': StopBits.one,
                               },
                         **kwargs
                         )
        self.address = address  # 1-16

    def write(self, command):
        """Write a command to the device."""
        message = f"{self.address:03}{command}"
        super().write(f"{message}{calculate_checksum(message)}")

    def write_composition(self, accessCode, command, data=""):
        """Write a command with an accessCode and optional data to the device.

        :param accessCode: How to access the device.
        :param command: Two char command string to send to the device.
        :param data: Data for the command.
        """
        self.write(f"{accessCode}{command}{compose_data(data)}")

    def ask(self, command_message, query_delay=None):
        """Ask for some value and check that the response matches the original command.

        :param str command_message: Access code, command, length, and content.
            The command sent is compared to the response command.
        """
        self.write(command_message)
        self.wait_for(query_delay)
        return self.read(command_message[1:3])

    def ask_manually(self, accessCode, command, data="", query_delay=None):
        """
        Send a message to the transmitter and return its answer.

        :param accessCode: How to access the device.
        :param command: Command to send to the device.
        :param data: Data for the command.
        :param float query_delay: Time to wait between writing and reading in seconds.
        :return str: Response from the device after error checking.
        """
        self.write(f"{accessCode}{command}{compose_data(data)}")
        self.wait_for(query_delay)
        return self.read(command)

    def read(self, command=None):
        """Read from the device and do error checking.

        :param str command: Original command sent to the device to compare it with the response.
            None deactivates the check.
        """
        # Sometimes the answer contains 0x00 or values above 127, such that
        # decoding fails.
        response = self.read_bytes(-1, break_on_termchar=True)
        response = response.replace(b"\x00", b"")

        # b"\r" is the termination character
        got = response.rstrip(b"\r").decode('ascii', errors="ignore")
        # Error checking
        if got[3] == "7":
            raise ConnectionError(self.errors[got[8:-1]])
        if command is not None and got[4:6] != command:
            raise ConnectionError(f"Wrong response to {command}: '{got}'.")
        if calculate_checksum(got[:-1]) != got[-1]:
            raise ConnectionError("Response checksum is wrong.")
        return got[8:-1]

    def check_set_errors(self):
        """Check the errors after setting a property."""
        self.read()
        return []  # no error happened

    " Main commands"

    range = Instrument.measurement(
        "0MR00", """Get the measurement range in mbar.""",
        preprocess_reply=lambda r: r[1:], separator="L")

    pressure = Instrument.measurement(
        "0MV00", """Get the current pressure of the default sensor in mbar""",
        preprocess_reply=lambda r: r.replace("UR", "0").replace("OR", "inf"),
    )

    # def Relays

    display_unit = Instrument.control(
        get_command="0DU00",
        set_command="2DU%s",
        docs="""Control the unit shown in the display. ('mbar', 'Torr', 'hPa')""",
        values=['mbar', 'Torr', 'hPa'],
        validator=validators.strict_discrete_set,
        set_process=compose_data,
        check_set_errors=True,
    )

    display_orientation = Instrument.control(
        "0DO00", "2DO01%i",
        """Control the orientation of the display in relation to the pipe ('top', 'bottom').""",
        values={"top": 0, "bottom": 1},
        map_values=True,
        validator=validators.strict_discrete_set,
        check_set_errors=True,
    )

    display_data = Instrument.control(
        "0DD00", "2DD01%i",
        """Control the display data source (strict SOURCES).""",
        values=Sources,
        cast=str_to_source,
        validator=validators.strict_discrete_set,
        check_set_errors=True,
    )

    def set_high(self, high=""):
        """Set the high pressure to `high` pressure in mbar."""
        self.ask_manually(2, "AH", high)

    def set_low(self, low=""):
        """Set the low pressure to `low` pressure in mbar."""
        self.ask_manually(2, "AL", low)

    " Sensor parameters"

    def get_sensor_transition(self):
        """
        Get the current sensor transition between sensors.

        return interpretation:
            - direct
                switch at 1 mbar.
            - continuous
                switch between 5 and 15 mbar.
            - F[float]T[float]
                switch between low and high value.
            - D[float]
                switch at value.
        """
        got = self.ask_manually(0, "ST")
        # VSR/VSL: 0 direct switch at 1 mbar, 1 continuous between 5 to 15 mbar
        # VSH: 0 direct switch at 4e-4 mbar, 1 continuous between 1e-3 to 2e-3 mbar,
        #      2 continuous between 2e-3 to 5e-3 mbar
        mapping = {
            "0": "direct",
            "1": "continuous",
            "2": "continuous 2",
        }
        return mapping.get(got, got)

    def set_default_sensor_transition(self):
        """Set the senstor transition mode to the default value, depends on the device."""
        self.ask_manually(2, "ST", "1")

    def set_continuous_sensor_transition(self, low, high):
        """Set the sensor transition mode to "continuous" mode between `low` and `high` (floats)."""
        self.ask_manually(2, "ST", f"F{low}T{high}")

    def set_direct_sensor_transition(self, transition_point):
        """Set the sensor transition to "direct" mode.

        :param float transition_point: Switch between the sensors at that value.
        """
        self.ask_manually(2, "ST", f"D{transition_point}")

    " Device Information"
    # def response delay

    device_type = Instrument.measurement(
        "0TD00", """Get the device type, like 'VSR205'.""", cast=str)

    product_name = Instrument.measurement(
        "0PN00", """Get the product name (article number).""", cast=str)

    device_serial = Instrument.measurement(
        "0SD00", """Get the transmitter device serial number.""", cast=str)

    sensor_serial = Instrument.measurement(
        "0SH00", """Get the sensor head serial number.""", cast=str)

    baud_rate = Instrument.setting(
        "2BR%s", """Set the device baud rate.""",
        set_process=compose_data,
        check_set_errors=True,
    )

    device_address = Instrument.setting(
        "2DA%s", "Set the device address.",
        set_process=compose_data,
        check_set_errors=True,
    )

    device_version = Instrument.measurement(
        "0VD00", """Get the device hardware version.""", cast=str)

    firmware_version = Instrument.measurement(
        "0VF00", """Get the firmware version.""", cast=str)

    bootloader_version = Instrument.measurement(
        "0VB00", """Get the bootloader version.""", cast=str)

    analog_output_setting = Instrument.measurement(
        "0OC00", "Get current analog output setting. See manual.", cast=str)

    operating_hours = Instrument.measurement(
        "0OH00", "Measure the operating hours.",
        separator="C",
        cast=int,
        get_process=lambda vals: vals / 4 if isinstance(vals, int) else [v / 4 for v in vals],
        # TODO simplify once #740 is merged.
    )


class VSH(SmartlineV2):
    """Vacuum transmitter of VSH series with both a pirani and a hot cathode sensor."""

    pirani = Instrument.ChannelCreator(Pirani)
    hotcathode = Instrument.ChannelCreator(HotCathode)


class VSM(SmartlineV2):
    """Vacuum transmitter of VSM series with both piece and cold cathode sensor."""

    piezo = Instrument.ChannelCreator(Piezo)
    coldcathode = Instrument.ChannelCreator(ColdCathode)


class VSR(SmartlineV2):
    """Vacuum transmitter of VSR/VCR series with both a piezo and a pirani sensor."""

    piezo = Instrument.ChannelCreator(Piezo)
    pirani = Instrument.ChannelCreator(Pirani)


class VSP(SmartlineV2):
    """Vacuum transmitter of VSP/VCP series with a piezo sensor."""

    piezo = Instrument.ChannelCreator(Piezo)
