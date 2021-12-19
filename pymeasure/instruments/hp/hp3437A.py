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

import ctypes
import logging
import math
import struct
from enum import IntFlag
import numpy as np


from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32


# classes for the decoding of the 5-byte status word
class StatusBytes(ctypes.Structure):
    """
    Support-Class for the 7 status bytes of the HP3437A
    """

    _fields_ = [
        ("byte1", c_uint8),
        ("byte2", c_uint8),
        ("byte3", c_uint8),
        ("byte4", c_uint8),
        ("byte5", c_uint8),
        ("byte6", c_uint8),
        ("byte7", c_uint8),
    ]


class StatusBits(ctypes.BigEndianStructure):
    """
    Support-Class with the bit assignments for the 5 status byte of the HP3437A
    """

    _pack_ = 1
    _fields_ = [
        # Byte 1: Function, Range and Number of Digits
        ("Format", c_uint8, 1),  # Bit 7
        ("SRQ", c_uint8, 3),  # bit 4..6
        ("trigger", c_uint8, 2),  # bit 2..3
        ("range", c_uint8, 2),  # bit 0..1
        # Byte 2 & 3:
        ("Number", c_uint16, 16),
        # Byte 2:
        # ("NRDGS_MSD", c_uint8, 4),
        # ("NRDGS_2SD", c_uint8, 4),
        # Byte 3:
        # ("NRDGS_3SD", c_uint8, 4),
        # ("NRDGS_LSD", c_uint8, 4),
        ("not_used", c_uint8(), 4),
        ("Delay", c_uint32, 28),
        # Byte 4:
        # ("Not_Used", c_uint8, 4),
        # ("Delay_MSD", c_uint8, 4),
        # # Byte 5:
        # ("Delay_2SD", c_uint8, 4),
        # ("Delay_3SD", c_uint8, 4),
        # # Byte 6:
        # ("Delay_4SD", c_uint8, 4),
        # ("Delay_5SD", c_uint8, 4),
        # # Byte 7:
        # ("Delay_6SD", c_uint8, 4),
        # ("Delay_LSD", c_uint8, 4),
    ]

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument

        """
        return f"format: {self.Format}, SRQ Mask:  {self.SRQ}, Trigger: {self.trigger}, Range: {self.range} \n"


class PackedBytes(ctypes.Structure):
    """
    Support-Class for the 2 bytes of the HP3437A packed data transfer
    """

    _fields_ = [
        ("byte1", c_uint8),
        ("byte2", c_uint8),
    ]


class PackedBits(ctypes.BigEndianStructure):
    """
    Support-Class for the bits in the HP3437A packed data transfer
    """

    _pack_ = 1
    _fields_ = [
        ("range", c_uint8, 2),  # bit 0..1
        ("sign_bit", c_uint8, 1),
        ("MSD", c_uint8, 1),
        ("SSD", c_uint8, 4),
        ("TSD", c_uint8, 4),
        ("LSD", c_uint8, 4),
    ]

    def __str__(self):
        return f"range: {self.range}, sign_bit: {self.sign_bit}, MSD: {self.MSD}, 2SD: {self.SSD}, 3SD: {self.TSD}, LSD: {self.LSD} \n"

    def __float__(self):
        # range decoding
        # (cf table 3-2, page 3-5 of the manual, HPAK document 9018-05946)
        # 1 indicates 0.1V range
        if self.range == 1:
            cur_range = 0.1
        # 2 indicates 10V range
        if self.range == 2:
            cur_range = 10.0
        # 3 indicates 1V range
        if self.range == 3:
            cur_range = 1.0

        signbit = 1
        if self.sign_bit == 0:
            signbit = -1

        return (
            cur_range
            * signbit
            * (
                self.MSD
                + float(self.SSD) / 10
                + float(self.TSD) / 100
                + float(self.LSD) / 1000
            )
        )


class PackedData(ctypes.Union):
    """Union type element for the decoding of the packed data bit-fields"""

    _fields_ = [("B", PackedBytes), ("b", PackedBits)]


class Status(ctypes.Union):
    """Union type element for the decoding of the status bit-fields"""

    _fields_ = [("B", StatusBytes), ("b", StatusBits)]


class HP3437A(Instrument):
    """Represents the Hewlett Packard 3737A system voltmeter
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, resourceName, **kwargs):
        super(HP3437A, self).__init__(
            resourceName,
            "Hewlett-Packard HP3437A",
            includeSCPI=False,
            send_end=True,
            read_termination="\r\n",
            write_termination="\r\n",
            **kwargs,
        )
        log.info("Initialized HP3437A")

    # Definitions for different specifics of this instrument
    RANGE = {
        1e-1: "R1",
        1: "R2",
        10: "R3",
    }

    TRIGGERS = {
        "internal": "T1",
        "external": "T2",
        "hold": "T3",
        "manual": "T3",
    }

    class SRQ(IntFlag):
        """Enum element for SRQ mask bit decoding"""

        DATA_READY = 4
        IGNORE_TRIGGER = 2
        INVALID_PROGRAM = 1

    def _get_status(self):
        """Method to read the status bytes from the instrument

        :return current_status: a byte array representing the instrument status
        :rtype current_status: bytes
        """
        self.adapter.connection.write_raw("B")
        return self.adapter.connection.read_raw()

    # decoder functions
    # decimal to BCD & BCD to decimal conversion copied from
    # https://pymodbus.readthedocs.io/en/latest/source/example/bcd_payload.html
    @classmethod
    def _convert_to_bcd(cls, decimal):
        """Converts a decimal value to a bcd value

        :param value: The decimal value to to pack into bcd
        :returns: The number in bcd form
        """
        place, bcd = 0, 0
        while decimal > 0:
            nibble = decimal % 10
            bcd += nibble << place
            decimal /= 10
            place += 4
        return bcd

    @classmethod
    def _convert_from_bcd(cls, bcd):
        """Converts a bcd value to a decimal value

        :param value: The value to unpack from bcd
        :returns: The number in decimal form
        """
        bcd = int.from_bytes(bcd, "big")
        place, decimal = 1, 0
        while bcd > 0:
            nibble = bcd & 0xF
            decimal += nibble * place
            bcd >>= 4
            place *= 10
        return decimal

    @classmethod
    def _decode_status(cls, status_bytes, field=None):
        """Method to decode the status bytes

        :param status_bytes: list of bytes to be decoded
        :param field: name of field to be returned
        :return ret_val: int status value

        """
        ret_val = Status(StatusBytes(*status_bytes))
        if field is None:
            return ret_val.b

        if field == "SRQ":
            return cls.SRQ(getattr(ret_val.b, field))

        if field == "Number":
            bcd_nr = struct.pack(">I", getattr(ret_val.b, field))
            return cls._convert_from_bcd(bcd_nr)

        if field == "Delay":
            bcd_delay = struct.pack(">I", getattr(ret_val.b, field))
            delay_value = (
                cls._convert_from_bcd(bcd_delay) / 1.0e7
            )  # delay resolution is 100ns
            return delay_value
        return getattr(ret_val.b, field)

    @staticmethod
    def _decode_range(status_bytes):
        """Method to decode current range

        :param range_undecoded: int to be decoded
        :return cur_range: float value repesenting the active measurment range
        :rtype cur_range: float

        """
        cur_stat = Status(StatusBytes(*status_bytes))
        range_undecoded = cur_stat.b.range
        # range decoding
        # (cf table 3-2, page 3-5 of the manual, HPAK document 9018-05946)
        if range_undecoded == 0:
            cur_range = math.nan
        # 1 indicates 0.1V range
        if range_undecoded == 1:
            cur_range = 0.1
        # 2 indicates 10V range
        if range_undecoded == 2:
            cur_range = 10.0
        # 3 indicates 1V range
        if range_undecoded == 3:
            cur_range = 1.0
        return cur_range

    @staticmethod
    def _decode_trigger(status_bytes):
        """Method to decode trigger mode

        :param status_bytes: list of bytes to be decoded
        :return trigger_mode: string with the current trigger mode
        :rtype trigger_mode: str

        """
        cur_stat = Status(StatusBytes(*status_bytes))
        trig = cur_stat.b.trigger
        if trig == 0:
            log.error("HP3437A invalid trigger detected!")
            trigger_mode = "INVALID"
        if trig == 1:
            trigger_mode = "Internal"
        if trig == 2:
            trigger_mode = "external"
        if trig == 3:
            trigger_mode = "hold/manual"
        return trigger_mode

    @staticmethod
    def _unpack_data(data):
        """
        Method to unpack the data from the returned bytes in packed mode

        :param data: list of bytes to be decoded
        :return ret_data: float value

        """
        ret_data = PackedData(PackedBytes(*data))
        return float(ret_data.b)

    # commands overwriting the base implementaiton
    def read(self):
        """
        Reads measured data from instrument, returns a np.array.

        (This function also takes care of unpacking the data if required)

        :return data: np.array containing the data
        """
        # Adjusting the timeout to match the number of counts and the delay
        current_timeout = self.adapter.connection.timeout
        time_needed = self.number_readings * self.delay
        new_timeout = time_needed * 3 * 1000  # safety factor 3

        if new_timeout > current_timeout:
            if new_timeout >= 1e6:
                # Disables timeout if measurement would take more then 1000 sec
                new_timeout = 0
                log.info("HP3437A: timeout deactivated")
            self.adapter.connection.timeout = new_timeout
            log.info("HP3437A: timeout changed to %g", new_timeout)
        read_data = self.adapter.connection.read_raw()
        # check if data is in packed format format
        if read_data[0] == read_data[2]:
            processed_data = []
            read_data_length = int(len(read_data) / 2)
            for i in range(0, read_data_length):
                _from = i * 2
                _to = _from + 2
                processed_data.append(self._unpack_data(read_data[_from:_to]))
            self.adapter.connection.timeout = current_timeout
            return np.array(processed_data)
        self.adapter.connection.timeout = current_timeout
        return np.array(read_data[:-2].decode("ASCII").split(","), dtype=float)

    # commands/properties for instrument control
    def check_errors(self):
        """
        As this instrument does not have a error indication bit,
        this function alwyas returns 0.

        """
        return 0

    @property
    def talk_ascii(self):
        """Return True if the instrument is set to ASCII communciation,
        this property can be set.

        .. Note::

            ASCII communciation is slower then the packed (BCD) communication,
            this may cause problems with measurments when short delays are used



        """
        return bool(self._decode_status(self._get_status(), "Format"))

    @talk_ascii.setter
    def talk_ascii(self, value):
        if value is True:
            self.write("F1")
        else:
            self.write("F2")

    @property
    def delay(self):
        """Return the value (float) for the delay between two measurements,
        this property can be set,

        valid range: 100ns - 0.999999s

        """
        return self._decode_status(self._get_status(), "Delay")

    @delay.setter
    def delay(self, value):
        delay_str = (
            "D." + format(strict_range(value, [0, 0.9999999]) * 10e6, "07.0f") + "S"
        )
        self.write(delay_str)

    @property
    def number_readings(self):
        """Return value (int) for the number of consecutive measurements,
        this property can be set,
        valid range: 0 - 9999

        """
        return self._decode_status(self._get_status(), "Number")

    @number_readings.setter
    def number_readings(self, value):
        number_str = "N" + str(strict_range(value, [0, 9999])) + "S"
        self.write(number_str)

    @property
    def range(self):
        """Return the current measurement voltage range.

        This property can be set, valid values: 0.1, 1, 10 (V).

        .. Note::

            This instrument does not have autorange capability.

            Overrange will be in indicated as 0.99,9.99 or 99.9

        """
        return self._decode_range(self._get_status())

    @range.setter
    def range(self, value):
        range_str = "R" + format(
            round(math.log10(strict_discrete_set(value, [0.1, 1, 10])) + 2), "d"
        )
        self.write(range_str)

    @property
    def status(self):
        """
        Return an object representing the current status of the unit.

        """
        return self._decode_status(self._get_status())

    @property
    def SRQ_mask(self):
        """Return current SRQ mask, this property can be set,

        bit assigment for SRQ:

        =========  ==========================
        Bit (dec)  Description
        =========  ==========================
         1         SRQ when invalid program
         2         SRQ when trigger is ignored
         4         SRQ when data ready
        =========  ==========================

        """
        return self._decode_status(self._get_status(), "SRQ")

    @SRQ_mask.setter
    def SRQ_mask(self, value):
        mask_str = "E" + format(strict_range(value, [0, 7]), "o") + "S"
        self.write(mask_str)

    @property
    def trigger(self):
        """Return current selected trigger mode, this property can be set,

        Possibe values are:

        ===========  ===========================================
        Value        Explanation
        ===========  ===========================================
        internal     automatic trigger (internal)
        external     external trigger (connector on back or GET)
        hold/manual  holds the measurement/issues a manual trigger
        ===========  ===========================================

        """
        return self._decode_trigger(self._get_status())

    @trigger.setter
    def trigger(self, value):
        trig_set = self.TRIGGERS[strict_discrete_set(value, self.TRIGGERS)]
        self.write(trig_set)

    # Functions using low-level access

    def GPIB_trigger(self):
        """
        Initate trigger via low-level GPIB-command
        (aka GET - group execute trigger)

        """
        self.adapter.connection.assert_trigger()

    def reset(self):
        """
        Initatiates a reset (like a power-on reset) of the HP3437A

        """
        self.adapter.connection.clear()

    def shutdown(self):
        """
        provides a way to gracefully close the connection to the HP3437A

        """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()
