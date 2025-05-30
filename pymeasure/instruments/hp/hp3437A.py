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

import ctypes
import logging
import math
from enum import IntFlag
import numpy as np
from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument, StatusBitsBase

from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32


class Status(StatusBitsBase):
    """
    A bitfield structure containing the assignments for the status decoding
    """
    _pack_ = 1
    _fields_ = [
        # Byte 0: Function, Range and Number of Digits
        ("Format", c_uint8, 1),  # Bit 7
        ("SRQ", c_uint8, 3),  # bit 4..6
        ("Trigger", c_uint8, 2),  # bit 2..3
        ("Range", c_uint8, 2),  # bit 0..1
        # Byte 1 & 2:
        ("Number", c_uint16, 16),
        # Byte 1:
        # ("NRDGS_MSD", c_uint8, 4),
        # ("NRDGS_2SD", c_uint8, 4),
        # Byte 2:
        # ("NRDGS_3SD", c_uint8, 4),
        # ("NRDGS_LSD", c_uint8, 4),
        ("not_used", c_uint8, 4),
        ("Delay", c_uint32, 28),
        # Byte 3:
        # ("Not_Used", c_uint8, 4),
        # ("Delay_MSD", c_uint8, 4),
        # Byte 4:
        # ("Delay_2SD", c_uint8, 4),
        # ("Delay_3SD", c_uint8, 4),
        # Byte 5:
        # ("Delay_4SD", c_uint8, 4),
        # ("Delay_5SD", c_uint8, 4),
        # Byte 6:
        # ("Delay_6SD", c_uint8, 4),
        # ("Delay_LSD", c_uint8, 4),
        ]

    @staticmethod
    def _decode_range(r):
        """Method to decode current range

        :param range_undecoded: int to be decoded
        :return cur_range: float value representing the active measurement range
        :rtype cur_range: float

        """
        # range decoding
        # (cf table 3-2, page 3-5 of the manual, HPAK document 9018-05946)
        decode_map = {
           0: math.nan,
           1: 0.1,
           2: 10.0,
           3: 1.0,
        }
        return decode_map[r]

    @staticmethod
    def _decode_trigger(t):
        """Method to decode trigger mode

        :param status_bytes: list of bytes to be decoded
        :return trigger_mode: string with the current trigger mode
        :rtype trigger_mode: str

        """
        decode_map = {
           0: "INVALID",
           1: "internal",
           2: "external",
           3: "hold/manual"
        }
        return decode_map[t]

    _get_process_ = {
        "Number": StatusBitsBase._convert_from_bcd,
        "Delay": StatusBitsBase._convert_from_bcd,
        "Range": _decode_range,
        "Trigger": _decode_trigger,
        }

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument
        """
        ret_str = ""
        for field in self._fields_:
            ret_str = ret_str + f"{field[0]}: {getattr(self, field[0])}\n"

        return ret_str


class PackedBits(ctypes.BigEndianStructure):
    """
    A bitfield structure containing the assignments for the data transfer in packed/binary mode
    """
    _pack_ = 1
    _fields_ = [
        ("range", c_uint8, 2),  # bit 0..1
        ("sign_bit", c_uint8, 1),
        ("MSD", c_uint8, 1),
        ("SSD", c_uint8, 4),
        ("TSD", c_uint8, 4),
        ("LSD", c_uint8, 4), ]

    def __float__(self):
        """
        Return a float value from the packed data of the HP3437A

        """
        # range decoding
        # (cf table 3-2, page 3-5 of the manual, HPAK document 9018-05946)
        decode_map = {
           1: 0.1,
           2: 10.0,
           3: 1.0,
        }
        cur_range = decode_map[self.range]

        signbit = 1
        if self.sign_bit == 0:
            signbit = -1

        return (
            cur_range * signbit * (
                self.MSD + self.SSD / 10 + self.TSD / 100 + self.LSD / 1000
            )
        )


class HP3437A(HPLegacyInstrument):
    """Represents the Hewlett Packard 3737A system voltmeter
    and provides a high-level interface for interacting
    with the instrument.
    """
    status_desc = Status
    pb_desc = PackedBits

    def __init__(self, adapter, name="Hewlett-Packard HP3437A", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
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

    def _unpack_data(self, data):
        """
        Method to unpack the data from the returned bytes in packed mode

        :param data: list of bytes to be decoded
        :return ret_data: float value

        """
        ret_data = PackedBits.from_buffer(bytearray(data))
        return float(ret_data)

    # commands overwriting the base implementation
    def read_data(self):
        """
        Reads measured data from instrument, returns a np.array.

        (This function also takes care of unpacking the data if required)

        :return data: np.array containing the data
        """
        # Adjusting the timeout to match the number of counts and the delay

        current_timeout = self.adapter.connection.timeout
        time_needed = self.number_readings * self.delay
        new_timeout = min(1e6, time_needed * 3 * 1000)  # safety factor 3
        if new_timeout > current_timeout:
            if new_timeout >= 1e6:
                # Disables timeout if measurement would take more then 1000 sec
                log.info("HP3437A: timeout deactivated")
            self.adapter.connection.timeout = new_timeout
            log.info("HP3437A: timeout changed to %g", new_timeout)
        read_data = self.read_bytes(-1)
        # check if data is in packed format format
        if self.talk_ascii:
            return_value = np.array(read_data[:-2].decode("ASCII").split(","),
                                    dtype=float)
        else:
            processed_data = []
            for i in range(0, len(read_data), 2):
                processed_data.append(self._unpack_data(read_data[i : i + 2]))  # noqa: E203
            return_value = np.array(processed_data)
        self.adapter.connection.timeout = current_timeout
        return return_value

    # commands/properties for instrument control
    def check_errors(self):
        """
        As this instrument does not have a error indication bit,
        this function always returns an empty list.

        """
        return []

    @property
    def talk_ascii(self):
        """
        A boolean property, True if the instrument is set to ASCII-based communication.
        This property can be set.
        """
        return bool(self.status.Format)

    @talk_ascii.setter
    def talk_ascii(self, value):
        if value:
            self.write("F1")
        else:
            self.write("F2")

    @property
    def delay(self):
        """Return the value (float) for the delay between two measurements,
        this property can be set,

        valid range: 100ns - 0.999999s

        """
        return self.status.Delay * 1e-7

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
        return self.status.Number

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
        return self.status.Range

    @range.setter
    def range(self, value):
        range_str = "R" + format(
            round(math.log10(strict_discrete_set(value, [0.1, 1, 10])) + 2), "d"
        )
        self.write(range_str)

    @property
    def SRQ_mask(self):
        """Return current SRQ mask, this property can be set,

        bit assignment for SRQ:

        =========  ==========================
        Bit (dec)  Description
        =========  ==========================
         1         SRQ when invalid program
         2         SRQ when trigger is ignored
         4         SRQ when data ready
        =========  ==========================

        """
        mask = self.status.SRQ
        return self.SRQ(mask)

    @SRQ_mask.setter
    def SRQ_mask(self, value):
        mask_str = "E" + format(strict_range(value, [0, 7]), "o") + "S"
        self.write(mask_str)

    @property
    def trigger(self):
        """Return current selected trigger mode, this property can be set,

        Possible values are:

        ===========  ===========================================
        Value        Explanation
        ===========  ===========================================
        internal     automatic trigger (internal)
        external     external trigger (connector on back or GET)
        hold/manual  holds the measurement/issues a manual trigger
        ===========  ===========================================

        """
        return self.status.Trigger

    @trigger.setter
    def trigger(self, value):
        trig_set = self.TRIGGERS[strict_discrete_set(value, self.TRIGGERS)]
        self.write(trig_set)
