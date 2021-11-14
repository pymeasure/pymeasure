#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

PACKET_LENGTH = 26

PACKET_HEADER_INDEX = 0
PACKET_ADDRESS_INDEX = 1
PACKET_COMMAND_INDEX = 2
PACKET_COMMAND_DATA_START_INDEX = 3
PACKET_CHECKSUM_INDEX = 25

PACKET_HEADER = 0xaa

PACKET_COMMAND_STATUS = 0x12
PACKET_COMMAND_REMOTE_ENABLED = 0x20
PACKET_COMMAND_ON_OFF = 0x21
PACKET_COMMAND_SET_MAXIMUM_ALLOWED_VOLTAGE = 0x22
PACKET_COMMAND_GET_MAXIMUM_ALLOWED_VOLTAGE = 0x23
PACKET_COMMAND_SET_MAXIMUM_ALLOWED_CURRENT = 0x24
PACKET_COMMAND_GET_MAXIMUM_ALLOWED_CURRENT = 0x25
PACKET_COMMAND_SET_MAXIMUM_ALLOWED_POWER = 0x26
PACKET_COMMAND_GET_MAXIMUM_ALLOWED_POWER = 0x27
PACKET_COMMAND_SET_MODE = 0x28
PACKET_COMMAND_GET_MODE = 0x29
PACKET_COMMAND_SET_CC_MODE_CURRENT = 0x2A
PACKET_COMMAND_GET_CC_MODE_CURRENT = 0x2B
PACKET_COMMAND_SET_CV_MODE_VOLTAGE = 0x2C
PACKET_COMMAND_GET_CV_MODE_VOLTAGE = 0x2D
PACKET_COMMAND_SET_CW_MODE_POWER = 0x2E
PACKET_COMMAND_GET_CW_MODE_POWER = 0x2F
PACKET_COMMAND_SET_CR_MODE_RESISTANCE = 0x30
PACKET_COMMAND_GET_CR_MODE_RESISTANCE = 0x31
PACKET_COMMAND_SET_REMOTE_SENSING_ENABLED = 0x56
PACKET_COMMAND_GET_REMOTE_SENSING_ENABLED = 0x57
PACKET_COMMAND_GET_INPUT_AND_STATE = 0x5F

PACKET_STATUS_VALID = 0x80
PACKET_STATUS_INCORRECT_CHEKSUM = 0x90
PACKET_STATUS_PARAMETER_INCORRECT = 0xA0
PACKET_STATUS_UNRECOGNIZED_COMMAND = 0xB0
PACKET_STATUS_INVALID_COMMAND = 0xC0


def calculate_checksum(packet):
    return sum(packet[0:PACKET_LENGTH - 1]) % 256


def make_packet(address, command, command_data):
    packet = bytearray(PACKET_LENGTH)
    packet[PACKET_HEADER_INDEX] = PACKET_HEADER
    packet[PACKET_ADDRESS_INDEX] = address
    packet[PACKET_COMMAND_INDEX] = command
    packet[PACKET_COMMAND_DATA_START_INDEX:PACKET_COMMAND_DATA_START_INDEX + len(command_data)] = command_data
    packet[PACKET_CHECKSUM_INDEX] = calculate_checksum(packet)
    return packet


def value_to_little_endian(value):
    return [value & 0xff,
            value >> 8 & 0xff,
            value >> 16 & 0xff,
            value >> 24 & 0xff]


def little_endian_to_value(arr):
    return arr[0] + arr[1] * 256 + arr[2] * 256 * 256 + arr[3] * 256 * 256 * 256


def make_command_data(size, scale, value):
    if size > 1:
        return value_to_little_endian(int(scale * value))
    else:
        return [int(scale * value)]


def ensure_valid_checksum(packet):
    if (calculate_checksum(packet) != packet[PACKET_CHECKSUM_INDEX]):
        raise Exception('Received packet with incorrect checksum')
    return packet


def ensure_valid_status(packet):
    assert packet[PACKET_COMMAND_INDEX] == PACKET_COMMAND_STATUS
    ensure_valid_checksum(packet)
    status = packet[PACKET_COMMAND_DATA_START_INDEX]
    if (status != PACKET_STATUS_VALID):
        status_map = {PACKET_STATUS_INCORRECT_CHEKSUM: "Checksum incorrect",
                      PACKET_STATUS_PARAMETER_INCORRECT: "Parameter incorrect",
                      PACKET_STATUS_UNRECOGNIZED_COMMAND: "Unrecognized command",
                      PACKET_STATUS_INVALID_COMMAND: "Invalid command"}
        raise Exception('Unexpected status: ' + status_map.get(status, "Unknown status"))


def make_get_str(packet_command, scale=1, size=1, offset=0):
    return "{:d} {:d} {:d} {:d}".format(packet_command, size, scale, offset)


def make_set_str(packet_command, specifier="%d", scale=1, size=1):
    return "{:d} {:s} {:d} {:d}".format(packet_command, specifier, size, scale)


class BKPrecision8500(Instrument):
    """ Represents the BK Precision 8500 Programmable DC Electronic Load and
    provides a high-level interface for interacting with the instrument.
    """

    def __init__(self, resourceName, baud_rate=4800, **kwargs):
        super().__init__(
            resourceName,
            "BK Precision 8500",
            **kwargs
        )
        # hack to set baud_rate since VISAAdapter would filter it out!
        self.adapter.connection.baud_rate = baud_rate
        self.remote_enabled = True

    def __write_raw(self, raw_bytes):
        self.adapter.connection.write_raw(raw_bytes)

    def __read_raw(self):
        return self.adapter.connection.read_bytes(PACKET_LENGTH)

    def __ask_raw(self, raw_bytes):
        self.__write_raw(raw_bytes)
        return self.__read_raw()

    def write(self, command):
        cmd, value, scale, size = command.split()
        cmd = int(cmd)
        value = float(value)
        scale = int(scale)
        size = int(size)
        ensure_valid_status(self.__ask_raw(make_packet(0, cmd, make_command_data(size, scale, value))))

    def values(self, command, **kwargs):
        cmd, scale, size, offset = command.split()
        cmd = int(cmd)
        scale = int(scale)
        size = int(size)
        offset = int(offset)
        packet = ensure_valid_checksum(self.__ask_raw(make_packet(0, cmd, [])))
        if scale > 1:
            return [little_endian_to_value(
                packet[PACKET_COMMAND_DATA_START_INDEX + offset:PACKET_COMMAND_DATA_START_INDEX + offset + size]) / scale]
        else:
            return [packet[PACKET_COMMAND_DATA_START_INDEX] / scale]

    remote_enabled = Instrument.setting(
        make_set_str(PACKET_COMMAND_REMOTE_ENABLED),
        """A boolean property that controls whether remote is enabled, takes
        values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    input_enabled = Instrument.setting(
        make_set_str(PACKET_COMMAND_ON_OFF),
        """A boolean property that controls whether the load input is enabled,
        takes values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    maximum_allowed_voltage = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_MAXIMUM_ALLOWED_VOLTAGE, 4, 1000),
        make_set_str(PACKET_COMMAND_SET_MAXIMUM_ALLOWED_VOLTAGE, "%g", 4, 1000),
        """A floating point property that sets the maximum allowed voltage in volts. """,
        validator=strict_range,
        values=[0, 120],
    )

    maximum_allowed_current = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_MAXIMUM_ALLOWED_CURRENT, 4, 10000),
        make_set_str(PACKET_COMMAND_SET_MAXIMUM_ALLOWED_CURRENT, "%g", 4, 10000),
        """A floating point property that sets the maximum allowed current in amps. """,
        validator=strict_range,
        values=[0, 30],
    )

    maximum_allowed_power = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_MAXIMUM_ALLOWED_POWER, 4, 1000),
        make_set_str(PACKET_COMMAND_SET_MAXIMUM_ALLOWED_POWER, "%g", 4, 1000),
        """A floating point property that sets the maximum allowed power in watts.""",
        validator=strict_range,
        values=[0, 300],
    )

    mode = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_MODE),
        make_set_str(PACKET_COMMAND_SET_MODE),
        """A string property that sets the DC load mode. Takes values of 'CR', 'CV',
        'CW', and 'CR'.""",
        validator=strict_discrete_set,
        values={"CC": 0, "CV": 1, "CW": 2, "CR": 3},
        map_values=True,
    )

    cc_mode_current = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_CC_MODE_CURRENT, 4, 10000),
        make_set_str(PACKET_COMMAND_SET_CC_MODE_CURRENT, "%g", 4, 10000),
        """A floating point property that sets the maximum current in amps 
        when in CC mode. """,
        validator=strict_range,
        values=[0, 30],
    )

    cv_mode_voltage = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_CV_MODE_VOLTAGE, 4, 1000),
        make_set_str(PACKET_COMMAND_SET_CV_MODE_VOLTAGE, "%g", 4, 1000),
        """A floating point property that sets the maximum voltage in volts 
        when in CV mode. """,
        validator=strict_range,
        values=[0, 120],
    )

    cw_mode_power = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_CW_MODE_POWER, 4, 1000),
        make_set_str(PACKET_COMMAND_SET_CW_MODE_POWER, "%g", 4, 1000),
        """A floating point property that sets the maximum power in watts 
        when in CW mode. """,
        validator=strict_range,
        values=[0, 300],
    )

    cr_mode_resistance = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_CR_MODE_RESISTANCE, 4, 1000),
        make_set_str(PACKET_COMMAND_SET_CR_MODE_RESISTANCE, "%g", 4, 1000),
        """A floating point property that sets the resistance in ohms 
        when in CR mode. """,
        validator=strict_range,
        values=[0, 4000],
    )

    remote_sensing_enabled = Instrument.control(
        make_get_str(PACKET_COMMAND_GET_REMOTE_SENSING_ENABLED),
        make_set_str(PACKET_COMMAND_SET_REMOTE_SENSING_ENABLED),
        """A boolean property that controls whether remote sensing is enabled, takes
        values True or False. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    input_voltage = Instrument.measurement(
        make_get_str(PACKET_COMMAND_GET_INPUT_AND_STATE, 4, 1000, 0),
        """Reads the input voltage in volts. """
    )

    input_current = Instrument.measurement(
        make_get_str(PACKET_COMMAND_GET_INPUT_AND_STATE, 4, 10000, 4),
        """Reads the input current in amps. """
    )

    input_power = Instrument.measurement(
        make_get_str(PACKET_COMMAND_GET_INPUT_AND_STATE, 4, 1000, 8),
        """Reads the input power in watts. """
    )
