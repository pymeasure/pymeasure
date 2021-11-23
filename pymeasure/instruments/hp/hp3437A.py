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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32

# classes for the decoding of the 5-byte status word
class Status_bytes(ctypes.Structure):
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


class Status_bits(ctypes.BigEndianStructure):
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
        ("Delay", c_uint32, 32),
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
        Returns a pretty formatted (human readable) string showing the status of the instrument

        """
        return "format: {}, SRQ Mask:  {}, Trigger: {}, Range: {} \n".format(
            self.Format,
            self.SRQ,
            self.trigger,
            self.range,
        )


class Status(ctypes.Union):
    """Union type element for the decoding of the status bit-fields"""

    _fields_ = [("B", Status_bytes), ("b", Status_bits)]


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
            **kwargs
        )

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

    def get_status(self):
        """Method to read the status bytes from the instrument
        :return current_status: a byte array representing the instrument status
        :rtype current_status: bytes
        """
        self.write("B")
        current_status = self.adapter.read_bytes(7)
        # current_status = self.adapter.read()

        return current_status

    # decoder functions
    # decimal to BCD & BCD to decimal conversion copied from
    # https://pymodbus.readthedocs.io/en/latest/source/example/bcd_payload.html
    @classmethod
    def convert_to_bcd(cls, decimal):
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
    def convert_from_bcd(cls, bcd):
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
    def decode_status(cls, status_bytes, field=None):
        """Method to handle the decoding of the status bytes into something meaningfull

        :param status_bytes: list of bytes to be decoded
        :param field: name of field to be returned
        :return ret_val: int status value

        """
        ret_val = Status(Status_bytes(*status_bytes))
        if field is None:
            return ret_val.b

        if field == "SRQ":
            return cls.SRQ(getattr(ret_val.b, field))

        if field == "Number":
            bcd_nr = struct.pack(">I", getattr(ret_val.b, field))
            print(bcd_nr)
            return cls.convert_from_bcd(bcd_nr)

        if field == "Delay":
            bcd_delay = struct.pack(">I", getattr(ret_val.b, field))
            print(bcd_delay)
            delay_value = (
                cls.convert_from_bcd(bcd_delay) / 1.0e7
            )  # delay resolution is 100ns
            return delay_value
        return getattr(ret_val.b, field)

    @staticmethod
    def decode_range(status_bytes):
        """Method to decode current range

        :param range_undecoded: int to be decoded
        :return cur_range: float value repesenting the active measurment range
        :rtype cur_range: float

        """
        cur_stat = Status(Status_bytes(*status_bytes))
        range_undecoded = cur_stat.b.range
        print(range_undecoded)
        cur_range = math.pow(10, (range_undecoded - 1))  # TODO verify on actual system
        return cur_range

    @staticmethod
    def decode_trigger(status_bytes):
        """Method to decode trigger mode

        :param status_bytes: list of bytes to be decoded
        :return trigger_mode: string with the current trigger mode
        :rtype trigger_mode: str

        """
        cur_stat = Status(Status_bytes(*status_bytes))
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

    # commands/properties for instrument control

    # TODO: find a way to check for invalid program

    # def check_errors(self):
    #     """
    #     Method to read the error status register

    #     :return error_status: one byte with the error status register content
    #     :rtype error_status: int
    #     """
    #     # Read the error status reigster only one time for this method, as
    #     # the manual states that reading the error status register also clears it.
    #     current_errors = self.error_status
    #     if current_errors != 0:
    #         log.error("HP3437A error detected: %s", self.ERRORS(current_errors))
    #     return self.ERRORS(current_errors)

    @property
    def talk_ascii(self):
        """Return True if the instrument is set to ASCII communciation,
        this property can be set.

        _Note:_

        ASCII communciation is slower then the (packed) BCD based communication,
        this may cause problems with measurment with short delay values.

        """
        return self.decode_status(self.get_status(), "Format")-1

    @talk_ascii.setter
    def talk_ascii(self, value):
        if value is True:
            self.write("F1")
        else:
            self.write("F2")

    @property
    def delay(self):
        """Return the current value for the delay between two measurements programmed in the unit.
        This value can be set,
        valid range: 100ns - 0.999999s

        """
        delay = self.decode_status(self.get_status(), "Delay")
        return delay

    @delay.setter
    def delay(self, value):
        delay_str = (
            "D." + format(strict_range(value, [0, 0.999999]) * 10e6, "06.0f") + "S"
        )
        self.write(delay_str)

    @property
    def number_readings(self):
        """Return current value for the number of consecutive measurements programmed.
        This value can be set,
        valid range: 0 - 9999

        """
        number = self.decode_status(self.get_status(), "Number")
        return number

    @number_readings.setter
    def number_readings(self, value):
        number_str = "N" + str(strict_range(value, [0, 9999])) + "S"
        self.write(number_str)

    @property
    def range(self):
        """Return the current measurement voltage range.
        This value can be set,
        valid values: 0.1,1,10 (V)

        _Note:_

        THis instrument does not have autorange functionality
        """
        range_decoded = self.decode_range(self.get_status())
        return range_decoded

    @range.setter
    def range(self, value):
        range_str = "R" + format(
            round(math.log10(strict_discrete_set(value, [0.1, 1, 10])) + 2), "d"
        )
        self.write(range_str)

    @property
    def status(self):
        """
        Returns an object representing the current status of the unit.

        """
        current_status = self.decode_status(self.get_status())
        return current_status

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
        mask = self.decode_status(self.get_status(), "SRQ")
        return mask

    @SRQ_mask.setter
    def SRQ_mask(self, value):
        mask_str = "E" + format(strict_range(value, [0, 7]), "o") + "S"
        self.write(mask_str)

    @property
    def trigger(self):
        """Return current selected trigger mode, this property can be set

        Possibe values are:

        ========  ===========================================
        Value     Meaning
        ========  ===========================================
        internal  automatic trigger (internal)
        external  external trigger (connector on back or GET)
        hold/man  holds the measurement/issues a manual trigger
        ========  ===========================================

        """
        trigger = self.decode_trigger(self.get_status())
        return trigger

    @trigger.setter
    def trigger(self, value):
        trig_set = self.TRIGGERS[strict_discrete_set(value, self.TRIGGERS)]
        self.write(trig_set)

    # Functions using low-level access via instrument.adapter.connection methods

    def GPIB_trigger(self):
        """
        Initate trigger via low-level GPIB-command (aka GET - group execute trigger)

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
