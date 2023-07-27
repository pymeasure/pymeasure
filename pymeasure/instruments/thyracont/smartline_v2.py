#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import pyvisa as pv
from pyvisa import VisaIOError  # noqa: F401 for dependencies


def calculateChecksum(message):
    """Calculate the checksum for string `message`."""
    value = 0
    for i in range(len(message)):
        value += ord(message[i])
    return chr(value % 64 + 64)


def compose_data(value):
    """Generate a string with the length of `value` and the `value` itself afterwards.

    :param value: Value to send to the device.
    """
    value = f"{value}"
    return f"{len(value):02}{value}"


source = {
    'combination': 0,
    'pirani': 1,
    'piezo': 2,
    'hotCathode': 3,
    'coldCathode': 4,
    'ambient': 6,
    'relative': 7,
}


class Sources(IntEnum):
    COMBINATION = 0
    PIRANI = 1
    PIEZO = 2
    HOT_CATHODE = 3
    COLD_CATHODE = 4
    AMBIENT = 6
    RELATIVE = 7


gas_factor = Channel.control(
    "0C{ch}00", "0C{ch}%s", "Control the gas correction factor.",
    values=(0.2, 8),
    validator=validators.strict_range,
    set_process=compose_data,
)


class SensorChannel(Channel):
    """Generic channel for individual pressure sensors of a Transmitter."""
    _id = -1  # obligatory channel number, define in channel types

    def __init__(self, parent, id):
        if id is None:
            id = self._id
        assert id == self._id, f"Pirani ID has to be {self._id}."
        super().__init__(parent, id=self._id)

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

    _id = 1

    gas_factor = gas_factor

    statistics = Channel.measurement(
        "0PM011",
        """Get the sensor statistics: wear in percent (negative: corrosion,
            positive: contamination), time since last adjustment in hours.""",
        preprocess_reply=lambda msg: msg.strip("W"),
        separator="A",
        cast=int,
        get_process=lambda vals: (vals[0], vals[1] / 4),
    )


class Piezo(SensorChannel):
    """Piezo sensor channel. A piezo sensor is independent of the gas present."""

    _id = 2


class HotCathode(SensorChannel):
    """Hot cathode sensor channel."""

    _id = 3

    filament_mode = Instrument.control(
        "0FC00", "2FC01%i", """The hot cathode filament control setting.""",
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
        """Get the wear in percent: of filament 1, of filament 2.""",
        separator="A",
        cast=int,
        get_process=lambda vals: [v / 4 for v in vals],
    )

    # cathode status CA, cathode control CC, cathode control mode CM


class ColdCathode(SensorChannel):
    """Cold cathode sensor channel."""

    _id = 4

    gas_factor = gas_factor


class Ambient(SensorChannel):

    _id = 6


class Relative(SensorChannel):

    _id = 7


class SmartlineV2(Instrument):
    """A Thyracont vacuum sensor transmitter of the Smartline V2 series.

    You may subclass this Instrument and add the appropriate channels, for example:

    .. doctest::

        from pymeasure.instruments import Instrument
        from pymeasure.instruments.thyractont import SmartlineV2

        PiezoAndPiraniInstrument(SmartlineV2):
            piezo = Instrument.ChannelCreator(Piezo)
            pirani = Instrument.ChannelCreator(Pirani)

    Communication Protocol v2 via rs485.

    :param adress: The device address in the range 1-16.
    """

    source = source

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
        """
        Everything is sent as ASCII characters.
        Package (bytes and usage): 0-2 address, 3 access code, 4-5 command, 6-7
            data length.
            if data: 8-n data to be sent, n+1 checksum, n+2 carriage return
            if no data: 8 checksum, 9 carriage return
        Access code for read access: 0 (master->transmitter), 1 response
            write: 2, 3
            factory default: 4,5
            error: -, 7
            binary 8, 9
        Data length is number of data in bytes (padding with zeroes on left)
        Checksum: Add the decimal numbers of the characters before, mod 64, add
        64, show as ASCII.
        """

    def write(self, command):
        """Write a command to the device."""
        message = f"{self.address:03}{command}"
        super().write(f"{message}{calculateChecksum(message)}")

    def write_composition(self, accessCode, command, data=""):
        """Write a command with an accessCode and optional data to the device.

        :param accessCode: How to access the device.
        :param command: Command to send to the device.
        :param data: Data for the command.
        """
        self.write(f"{accessCode}{command}{compose_data(data)}")

    def ask(self, command_message, query_delay=0):
        """Ask for some value and check that the response matches the original command.

        :param str command_message: Access code, command, length, and content.
            The command sent is compared to the response command.
        """
        self.write(command_message)
        self.wait_for(query_delay)
        return self.read(command_message[1:3])

    def read(self, command=None):
        """Read from the device and do error checking.

        :param str command: Original command sent to the device to compare it with the response.
            None deactivates the check.
        """
        # Sometimes the answer contains 0x00 or values above 127, such that
        # decoding fails.
        answer = b''
        i = 0
        while True:
            try:
                got = self.adapter.read_bytes(1)
            except pv.VisaIOError as exc:
                if exc.abbreviation == 'VI_ERROR_TMO':
                    raise ConnectionResetError("Timeout.")
                i += 1
                if i > 2:
                    raise ConnectionResetError(f"Timeout at {i} tries.")
                continue
            if got == b'\r':
                break
            elif int.from_bytes(got, 'little') > 127:
                pass  # Ignore those values.
            elif got == b'\x00':
                pass  # Ignore 0 byte value.
            else:
                answer += got
        got = answer.decode('ascii')
        # Raises from time to time an UnicodeDecodeError or pyvisa.VisaIOError
        if got[3] == "7":
            raise ConnectionError(self.errors[got[8:-1]])
        if command is not None and got[4:6] != command:
            raise ConnectionError(f"Wrong response to {command}: '{got}'.")
        if calculateChecksum(got[:-1]) != got[-1]:
            raise ConnectionError("Response checksum is wrong.")
        return got[8:-1]

    def check_set_errors(self):
        """Check the errors after setting a property."""
        self.read()
        return []  # no error happened

    def check_errors(self):
        # TODO remove after update to pymeasure 0.12
        return self.check_set_errors()

    def query(self, accessCode, command, data=""):
        """
        Send a message to the transmitter and return its answer.

        :param accessCode: How to access the device.
        :param command: Command to send to the device.
        :param data: Data for the command.
        :return str: Response from the device after error checking.
        """
        self.write_composition(accessCode, command, data)
        return self.read(command)

    " Main commands"

    range = Instrument.measurement(
        "0MR00", """Get the measurement range in mbar.""",
        preprocess_reply=lambda r: r[1:], separator="L")

    pressure = Instrument.measurement(
        "0MV00", """Get the current pressure of the default sensor in mbar""",
        preprocess_reply=lambda r: r.replace("UR", "0").replace("OR", "inf"),
    )

    def getPressure(self, sensor='combination'):
        """
        Get the current pressure of the `sensor` in mbar.

        The display unit does not affect this value. Under range (UR) is
        returned as 0, over range (OR) as inf.
        """
        # TODO replace with channels
        # The general command is MV for the combined value.
        command = f"M{self.source.get(sensor, 0)}".replace('0', 'V')
        # response is "OR", "UR" or a float as a string "1.54"
        got = self.query(0, command).replace("UR", "0").replace("OR", "inf")
        return float(got)

    # def Relays

    display_unit = Instrument.control(
        "0DU00", "2DU%s", """Unit shown in the display.""",
        values=['mbar', 'Torr', 'hPa'],
        validator=validators.strict_discrete_set,
        set_process=compose_data,
        check_set_errors=True,
    )

    display_orientation = Instrument.control(
        "0DO00", "2DO01%i",
        """Orientation of the display in relation to the pipe.""",
        values={"top": 0, "bottom": 1},
        map_values=True,
        validator=validators.strict_discrete_set,
        check_set_errors=True,
    )

    display_data = Instrument.control(
        "0DD00", "2DD01%i",
        """Position of the display in relation to the pipe.""",
        values=source,
        cast=int,
        map_values=True,
        validator=validators.strict_discrete_set,
        check_set_errors=True,
    )

    def setHigh(self, high=""):
        """Set the high pressure to `high` pressure in mbar."""
        self.query(2, "AH", high)

    def setLow(self, low=""):
        """Set the low pressure to `low` pressure in mbar."""
        self.query(2, "AL", low)

    " Sensor parameters"

    def getSensorTransition(self):
        """
        Get the current sensor transition between sensors.

        return interpretation
        -------
        direct
            switch at 1 mbar.
        continuos
            switch between 5 and 15 mbar.
        F[float]T[float]
            switch between low and high value.
        D[float]
            switch at value.
        """
        got = self.query(0, "ST")
        # VSR/VSL: 0 direct switch at 1 mbar, 1 continuios between 5 to 15 mbar
        if got == "0":
            return "direct"
        elif got == "1":
            return "continuous"
        else:
            return got

    def setSensorTransition(self, mode, *values):
        """
        Set the sensor transition to `mode` with optional `values`.

        parameters
        ----------
        mode : "continuous", "direct"
            Switch continuously from one sensor to another in the interval of
            low and high. They can be set in values and default to 5, 15 for
            VCR. Alternatively switch directly at a single piezo pressure.
        values
            The lower transition value and the higher transition value, if
            applicable.
        """
        if mode == "continuous":
            if not values:
                command = "1"
            elif len(values) == 2:
                low, high = values
                command = f"F{low}T{high}"
            else:
                raise ValueError("Invalid values for continuous mode.")
        elif mode == "direct" and len(values) == 1:
            command = f"D{values[0]}"
        else:
            raise ValueError("Invalid mode combination.")
        self.query(2, "ST", command)

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
        "2BR%s", """The device baud rate.""",
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
        "0OC00", "Current analog output setting. See manual.", cast=str)

    operating_hours = Instrument.measurement(
        "0OH00", "Measure the operating hours.",
        separator="C",
        cast=int,
        get_process=lambda vals: vals / 4 if isinstance(vals, int) else [v / 4 for v in vals],
        # TODO simplify once #740 is merged.
    )


class VSR(SmartlineV2):
    """Vacuum transmitter of VSR/VCR series with both a piezo and a pirani sensor."""

    piezo = Instrument.ChannelCreator(Piezo)
    pirani = Instrument.ChannelCreator(Pirani)


class VSH(SmartlineV2):
    """Vacuum transmitter of VSH series with both a pirani and a hot cathode sensor."""

    pirani = Instrument.ChannelCreator(Pirani)
    hotcathode = Instrument.ChannelCreator(HotCathode)
