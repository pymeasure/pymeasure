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

from pymeasure.instruments import Channel, Instrument


def calculate_checksum(msg):
    """calculate a two byte Cyclic Redundancy Check based on 14 bits

    Parameters
    ----------
    msg: bytes
    Message of the device without the sync character
    """
    # check if message contains data
    if not msg:
        return chr(0) + chr(0)
    # initialize CRC
    crc = 0x3fff
    # loop over characters in message
    for char in msg:
        crc ^= char
        for i in range(8):
            tmpcrc = crc
            crc = crc >> 1
            if tmpcrc & 1 == 1:
                crc ^= 0x2001
        crc &= 0x3fff
    # separate 14 significant bits in two byte checksum
    return bytes(((crc & 0x7f) + 34, ((crc >> 7) & 0x7f) + 34))


class SensorChannel(Channel):
    """Sensor channel for individual rate measurements."""

    rate = Channel.measurement(
        "L{ch}?", """Get the current rate for a sensor in Angstrom per second""",
        cast=float,
    )

    thickness = Channel.measurement(
        "N{ch}", """Get the current thickness for a sensor in Angstrom""",
        cast=float,
    )

    frequency = Channel.measurement(
        "P{ch}", """Get the current frequency for a sensor in Hz""",
        cast=float,
    )

    crystal_life = Channel.measurement(
        "R{ch}", """Get the crystal life value in percent""",
        cast=float,
    )


class SQM160(Instrument):
    """Inficon SQM-160 multi-film rate/thickness monitor.

    Uses a quartz crystal sensor to measure rate and thickness in a thin
    film deposition process. Connection to the device is commonly made through
    a serial connection (RS232) or optionally via USB or Ethernet.

    A command packet always consists of the following:
     - 1 Byte: Sync character ('!' appears only at the start of a message).
     - 1 Byte: length character obtained from the message length without CRC.
               A value of 34 is added so that no '!' can occur.
     - Command message with variable length.
     - 2 Byte: Cyclic Redundancy Check (CRC) checksum.

    A response packet always consists of:
     - 1 Byte: Sync character ('!' appears only at the start of a message).
     - 1 Byte: length character obtained from the message length without CRC.
               A value of 35 is added.
     - 1 Byte: Response status character indicating the status of the command.
     - Response message with variable length.
     - 2 Byte: Cyclic Redundancy Check (CRC) checksum.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param string name: Name of the instrument.
    :param string baud_rate: Baud rate used by the serial connection.
    :param kwargs: Any valid key-word argument for Instrument

    """
    sensor_1 = Instrument.ChannelCreator(SensorChannel, 1)
    sensor_2 = Instrument.ChannelCreator(SensorChannel, 2)
    sensor_3 = Instrument.ChannelCreator(SensorChannel, 3)
    sensor_4 = Instrument.ChannelCreator(SensorChannel, 4)
    sensor_5 = Instrument.ChannelCreator(SensorChannel, 5)
    sensor_6 = Instrument.ChannelCreator(SensorChannel, 6)

    def __init__(self, adapter, name="Inficon SQM-160 thickness monitor",
                 baud_rate=19200, **kwargs):
        super().__init__(adapter,
                         name,
                         includeSCPI=False,
                         write_termination="",
                         read_termination="",
                         asrl=dict(baud_rate=baud_rate),
                         timeout=3000,
                         **kwargs)

    def read(self):
        """Reads a response message from the instrument.

        This method also checks for a correct checksum.

        :returns: the response packet
        :rtype: string
        :raises ConnectionError: if a checksum error is detected or a wrong
                                 response status is detected.
        """
        header = self.read_bytes(2)
        # check valid header
        if header[0] != 33:  # b"!"
            raise ConnectionError(f"invalid header start byte '{header[0]}' received")
        length = header[1] - 35
        if length <= 0:
            raise ConnectionError(f"invalid message length '{header[1]}' -> length {length}")

        response_status = self.read_bytes(1)
        if response_status == b"C":
            raise ConnectionError("invalid command response received")
        elif response_status == b"D":
            raise ConnectionError("Problem with data in command")
        elif response_status != b"A":
            raise ConnectionError(f"unknown response status character '{response_status}'")

        if length - 1 > 0:
            data = self.read_bytes(length - 1)
        else:
            data = b""
        chksum = self.read_bytes(2)
        calculated_checksum = calculate_checksum(
            header[1].to_bytes(length=1, byteorder='big') + response_status + data)
        if chksum == calculated_checksum:
            return data.decode()
        else:
            raise ConnectionError(
                f"checksum error in received message '{header + response_status + data}' "
                f"with checksum '{calculated_checksum}' but received '{chksum}'")

    def write(self, command):
        """Write a command to the device."""
        length = chr(len(command) + 34)
        message = f"{length}{command}".encode()
        self.write_bytes(b"!" + message + calculate_checksum(message))

    def check_set_errors(self):
        """Check the errors after setting a property."""
        self.read()
        return []  # no error happened

    firmware_version = Instrument.measurement(
        "@", """Get the firmware version.""",
        cast=str,
    )

    number_of_channels = Instrument.measurement(
        "J", """Get the number of installed channels""",
        cast=int,
    )

    average_rate = Instrument.measurement(
        "M", """Get the current average rate in Angstrom per second""",
        cast=float,
    )

    average_thickness = Instrument.measurement(
        "O", """Get the current average thickness in Angstrom""",
        cast=float,
    )

    all_values = Instrument.measurement(
        "W", """Get the current rate (Angstrom/s), Thickness (Angstrom), and frequency (Hz)
                for each sensor""",
        cast=float,
        preprocess_reply=lambda msg: msg[5:],  # ingore first '00.00'
    )

    reset_flag = Instrument.measurement(
        "Y", """Get the power-up reset flag.
                It is True only when read first after a power cycle.""",
        cast=int,
        values={True: 1, False: 0},
        map_values=True,
    )

    def reset_system_parameters(self):
        """Reset all film and system parameters."""
        self.write("Z")
        self.read()  # read obligatory response message

    def reset_thickness_rate(self):
        """Reset the average thickness and rate.

        This also sets all active Sensor Rates and Thicknesses to zero
        """
        self.write("S")
        self.read()  # read obligatory response message

    def reset_time(self):
        """Reset the time of the monitor to zero.
        """
        self.write("T")
        self.read()  # read obligatory response message
