#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import struct

from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments import Channel, Instrument


def values(self, command, cast=int, separator=',', preprocess_reply=None, **kwargs):
    """Write a command to the instrument and return a list of formatted
    values from the result.

    This is derived from CommonBase.values and adapted here for use with bytes
    communication messages (no str conversion and strip). It is implemented as a
    general method to allow using it equally in PresetChannel and CXN. See
    Github issue #784 for details.

    :param command: SCPI command to be sent to the instrument
    :param separator: A separator character to split the string into a list
    :param cast: A type to cast the result
    :param preprocess_reply: optional callable used to preprocess values
        received from the instrument. The callable returns the processed
        string.
    :returns: A list of the desired type, or strings where the casting fails
    """
    results = self.ask(command)
    if callable(preprocess_reply):
        results = preprocess_reply(results)
    for i, result in enumerate(results):
        try:
            if cast == bool:
                # Need to cast to float first since results are usually
                # strings and bool of a non-empty string is always True
                results[i] = bool(float(result))
            else:
                results[i] = cast(result)
        except Exception:
            pass  # Keep as bytes
    return results


def int2char(value):
    """Convert an 16-bit unsigned integer to a tuple of two representing characters."""
    return tuple(int(b) for b in value.to_bytes(2, "big"))


class PresetChannel(Channel):
    values = values

    load_capacity = Instrument.control(
        "GU\x00{ch:c}\x00\x00", "TD{ch:c}\x01\x00%c",
        """Control the percentage of full-scale value of the load capacity preset.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[2:4]),
        validator=strict_discrete_set,
        values=range(101),
    )

    tune_capacity = Instrument.control(
        "GU\x00{ch:c}\x00\x00", "TD{ch:c}\x02\x00%c",
        """Control the percentage of full-scale value of the tune capacity preset.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[4:6]),
        validator=strict_discrete_set,
        values=range(101),
    )


class CXN(Instrument):
    """T&C Power Conversion AG Series Plasma Generator CXN
    (also rebranded by AJA International Inc as 0113 GTC or 0313 GTC)

    Connection to the device is made through an RS232 serial connection.
    The communication settings are fixed in the device at 38400, stopbit one,
    parity none. The device uses a command response system where every receipt
    of a command is acknowledged by returning a '*'. A '?' is returned to
    indicates the command was not recognized by the device.

    A command messages always consists of the following bytes (B):
    1B - header (always 'C'),
    1B - address (ignored),
    2B - command id,
    2B - parameter 1,
    2B - parameter,
    2B - checksum

    A response message always consists of:
    1B - header (always 'R'),
    1B - address of the device,
    2B - length of the data package,
    variable length data,
    2B - checksum
    response messages are received after the acknowledge byte.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param string name: Name of the instrument.
    :param kwargs: Any valid key-word argument for Instrument

    .. Note::

        In order to enable setting any parameters one has to request control
        and periodically (at least once per 2s) poll any value from the device.
        Failure to do so will mean loss of control and the device will reset
        certain parameters (setpoint, disable RF, ...). If no value should be polled
        but control should remain active one can also use the ping method.
    """
    # use predefined values method to allow reusing in the Channels
    values = values

    preset_1 = Instrument.ChannelCreator(PresetChannel, 1)

    preset_2 = Instrument.ChannelCreator(PresetChannel, 2)

    preset_3 = Instrument.ChannelCreator(PresetChannel, 3)

    preset_4 = Instrument.ChannelCreator(PresetChannel, 4)

    preset_5 = Instrument.ChannelCreator(PresetChannel, 5)

    preset_6 = Instrument.ChannelCreator(PresetChannel, 6)

    preset_7 = Instrument.ChannelCreator(PresetChannel, 7)

    preset_8 = Instrument.ChannelCreator(PresetChannel, 8)

    preset_9 = Instrument.ChannelCreator(PresetChannel, 9)

    def __init__(self, adapter, name="T&C RF sputtering power supply", address=0, **kwargs):
        self.address = address
        super().__init__(adapter,
                         name,
                         includeSCPI=False,
                         write_termination="",
                         read_termination="",
                         asrl=dict(baud_rate=38400),
                         **kwargs)

    @staticmethod
    def _checksum(msg):
        """Calculate a 2 bytes checksum calculated by a bytewise sum of the message.

        :param bytes msg: message content
        :returns: calculated checksum
        :rtype: bytes
        """
        return struct.pack(">H", sum(msg))

    def _prepend_cmdheader(self, cmd):
        """Prepends command start byte and address to the command.

        :param bytes msg: command message
        """
        return b"C" + self.address.to_bytes(1, "big") + cmd

    def _check_acknowledgment(self):
        """Check reply string for acknowledgement byte.

        :raises ValueError: if an invalid an invalid byte is read from the instrument
        """
        ret = super().read_bytes(1)
        if ret == b"*":
            return
        # no valid acknowledgement message found
        raise ValueError(
            f"invalid reply '{ret}' found in acknowledgement check")

    def read(self):
        """Reads a response message from the instrument.

        This method determines the length of the message from the automatically
        by reading the message header and also checks for a correct checksum.

        :returns: the data fields
        :rtype: bytes
        :raises ValueError: if a checksum error is detected
        """
        header = super().read_bytes(4)
        # check valid header
        if header[0] != 82:
            raise ValueError(f"invalid header start byte '{header[0]}' received")
        if header[1] != self.address:
            raise ValueError(f"invalid address byte '{header[1]}' received; "
                             f"should be {self.address.to_bytes(1, 'big')}")
        datalength = int.from_bytes(header[2:], "big")
        data = super().read_bytes(datalength)
        chksum = super().read_bytes(2)
        if chksum == self._checksum(header + data):
            return data
        else:
            raise ValueError(
                f"checksum error in received message {header + data} "
                f"with checksum {self._checksum(header + data)} "
                f"but received {chksum}")

    def write(self, command):
        """Writes a command to the instrument and includes needed required
        header and address.

        :param str command: command to be sent to the instrument
        """
        fullcmd = self._prepend_cmdheader(command.encode())
        super().write_bytes(fullcmd + self._checksum(fullcmd))
        self._check_acknowledgment()

    class Status(enum.IntFlag):
        """IntFlag type used to represent the CXN status.

        The used bits correspond to:
        bit 14: Analog interface enabled,
        bit 11: Interlock open,
        bit 10: Over temperature,
        bit 9: Reverse power limit,
        bit 8: Forward power limit,
        bit 6: MCG mode active,
        bit 5: load power leveling active,
        bit 4, External RF source active,
        bit 0: RF power on.

        """
        RF_ENABLED = 1
        EXTERNAL_RFSOURCE = 16
        LOAD_POWER_LEVELING = 32
        MCG_MODE = 64
        FORWARD_POWER_LIMIT = 256
        REVERSE_POWER_LIMIT = 512
        OVER_TEMPERATURE = 1024
        INTERLOCK_OPEN = 2048
        ANALOG_INTERFACE = 16384

    id = Instrument.measurement(
        "Gi\x00\x01\x00\x00",
        """Get the device identification string.""",
        cast=str,
        get_process=lambda d: d.decode()[2:-1].strip(),
    )

    serial = Instrument.measurement(
        "Gi\x00\x02\x00\x00",
        """Get the serial number of the instrument.""",
        cast=str,
        get_process=lambda d: d.decode()[2:-1].strip(),
    )

    firmware_version = Instrument.measurement(
        "Gf\x00\x00\x00\x00",
        """Get the UI-processor and RF-processor firmware version numbers.""",
        preprocess_reply=lambda d: struct.unpack("BBBB", d),
        get_process=lambda v: str.format("UI {}.{}, RF {}.{}", *v)
    )

    pulse_params = Instrument.measurement(
        "GE\x00\x00\x00\x00",
        """Get pulse on/off time of the pulse waveform.""",
        preprocess_reply=lambda d: struct.unpack(">HH", d),
    )

    frequency = Instrument.measurement(
        "GF\x00\x00\x00\x00",
        """Get operating frequency in Hz.""",
        preprocess_reply=lambda d: struct.unpack(">L", d),
    )

    power = Instrument.measurement(
        "GP\x00\x00\x00\x00",
        """Get power readings for forward/reverse/load power in watts.""",
        preprocess_reply=lambda d: struct.unpack(">HHH", d),
        get_process=lambda d: (float(d[0]) / 10, float(d[1]) / 10, float(d[2]) / 10),
    )

    status = Instrument.measurement(
        "GS\x00\x00\x00\x00",
        """Get status field. The return value is represented by the IntFlag
        type Status.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[:2]),
        get_process=lambda d: CXN.Status(d),
    )

    temperature = Instrument.measurement(
        "GS\x00\x00\x00\x00",
        """Get heat sink temperature in deg Celsius.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[2:4]),
        get_process=lambda d: float(d) / 10,
    )

    tuner = Instrument.measurement(
        "GS\x00\x00\x00\x00",
        """Get type of the used tuner.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[6:]),
        values={"none": 1, "AFT generator": 2,
                "analog tuner": 3, "digital tuner": 4},
        map_values=True,
    )

    power_limit = Instrument.measurement(
        "Gp\x00\x00\x00\x00",
        """Get maximum power of the power supply.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[2:4]),
        get_process=lambda d: float(d) / 10,
    )

    reverse_power_limit = Instrument.measurement(
        "Gp\x00\x00\x00\x00",
        """Get maximum reverse power.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[18:20]),
        get_process=lambda d: float(d) / 10,
    )

    dc_voltage = Instrument.measurement(
        "GT\x00\x00\x00\x00",
        """Get the DC voltage in volts.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[6:8]),
    )

    operation_mode = Instrument.control(
        "GS\x00\x00\x00\x00", "SO\x00%c\x00\x00",
        """Control the operation mode.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[4:6]),
        values={"normal": 1, "<invalid>": 2, "pulse": 3, "ramp": 4},
        map_values=True,
    )

    setpoint = Instrument.control(
        "GL\x00\x00\x00\x00", "SA%c%c\x00\x00",
        """Control the setpoint power level in watts.""",
        preprocess_reply=lambda d: struct.unpack(">H", d),
        get_process=lambda d: float(d) / 10,
        set_process=int2char,
        validator=strict_discrete_set,
        values=range(4001),
    )

    ramp_start_power = Instrument.control(
        "GR\x00\x00\x00\x00", "RP%c%c\x00\x00",
        """Control the ramp starting power in watts.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[:2]),
        set_process=int2char,
        validator=strict_discrete_set,
        values=range(1, 4001),
    )

    ramp_rate = Instrument.control(
        "GR\x00\x00\x00\x00", "RR%c%c\x00\x00",
        """Control the ramp rate in watts/second.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[2:]),
        set_process=int2char,
        validator=strict_discrete_set,
        values=range(1, 99),
    )

    manual_mode = Instrument.control(
        "GT\x00\x00\x00\x00", "TM\x00%c\x00\x00",
        """Control the manual tuner mode.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[:2]),
        get_process=lambda v: bool(v & 1),
        set_process=lambda v: 2 if v else 1,
        validator=strict_discrete_set,
        values=(True, False),
    )

    load_capacity = Instrument.control(
        "GT\x00\x00\x00\x00", "TC\x00\x01\x00%c",
        """Control the percentage of full-scale value of the load capacity.
           It can be set only when manual_mode is True.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[2:4]),
        get_process=lambda d: float(d) / 10,
        validator=strict_discrete_set,
        values=range(101),
    )

    tune_capacity = Instrument.control(
        "GT\x00\x00\x00\x00", "TC\x00\x02\x00%c",
        """Control the percentage of full-scale value of the tune capacity.
           It can be set only when manual_mode is True.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[4:6]),
        get_process=lambda d: float(d) / 10,
        validator=strict_discrete_set,
        values=range(101),
    )

    preset_slot = Instrument.control(
        "GT\x00\x00\x00\x00", "TP\x00%c\x00\x00",
        """Control which preset slot will be used for auto-tune mode.
           Valid values are 0 to 9. 0 means no preset will be used""",
        preprocess_reply=lambda d: struct.unpack(">H", d[8:10]),
        validator=strict_discrete_set,
        values=range(10),
    )

    rf_enabled = Instrument.control(
        "GS\x00\x00\x00\x00", "BR%c%c\x00\x00",
        """Control the RF output.""",
        preprocess_reply=lambda d: struct.unpack(">H", d[:2]),
        get_process=lambda v: bool(v & 1),
        set_process=lambda v: (85, 85) if v else (0, 0),
        validator=strict_discrete_set,
        values=(True, False),
    )

    def request_control(self):
        """Request control of the instrument.

        This is required to be able to set any properties.
        """
        self.write("BC\x55\x55\x00\x00")
        status = int(struct.unpack(">H", self.read())[0])
        if status != 1:
            print("error(CXN): control request denied!")

    def release_control(self):
        """Release instrument control.

        This will reset certain properties to safe defaults and disable the RF
        output.
        """
        self.write("BC\x00\x00\x00\x00")
        status = int(struct.unpack(">H", self.read())[0])
        if status != 0:
            print("error(CXN): release of control unsuccessful!")

    def ping(self):
        """Send a ping to the instrument."""
        self.write("BP\x00\x00\x00\x00")
