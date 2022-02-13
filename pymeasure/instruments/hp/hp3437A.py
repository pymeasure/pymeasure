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
from enum import IntFlag
import numpy as np
from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32

STATUS_BYTES = 7


class Status_bits(ctypes.BigEndianStructure):
    """
    A bitfield structure containing the assignments for the status decoding
    """
    _pack_ = 1
    _fields_ = [
        # Byte 0: Function, Range and Number of Digits
        ("Format", c_uint8, 1),  # Bit 7
        ("SRQ", c_uint8, 3),  # bit 4..6
        ("trigger", c_uint8, 2),  # bit 2..3
        ("range", c_uint8, 2),  # bit 0..1
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

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument

        """
        ret_str = ""
        for field in self._fields_:
            ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"

        return ret_str


PACKED_BYTES = 2


class Packed_bits(ctypes.BigEndianStructure):
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
        ("LSD", c_uint8, 4),
        ]

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument

        """
        ret_str = ""
        for field in self._fields_:
            ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"
        return ret_str

    def __float__(self):
        """
        Return a float value from the packed data of the HP3437A

        """
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


class HP3437A(HPLegacyInstrument):
    """Represents the Hewlett Packard 3737A system voltmeter
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, resourceName, **kwargs):
        super(HP3437A, self).__init__(
            resourceName,
            "Hewlett-Packard HP3437A",
            status_bytes=STATUS_BYTES,
            status_bitfield=Status_bits,
            **kwargs,
        )
        self.packed_bits = Packed_bits
        self.packed_bytes = self.bytefield_factory(PACKED_BYTES)
        self.packed_data = self.union_factory(self.packed_bytes, self.packed_bits)
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

    @staticmethod
    def _decode_range(self, status_bytes):
        """Method to decode current range

        :param range_undecoded: int to be decoded
        :return cur_range: float value repesenting the active measurment range
        :rtype cur_range: float

        """
        cur_stat = self.status_union(self.status_bytes(*status_bytes))
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
    def _decode_trigger(self, status_bytes):
        """Method to decode trigger mode

        :param status_bytes: list of bytes to be decoded
        :return trigger_mode: string with the current trigger mode
        :rtype trigger_mode: str

        """
        cur_stat = self.status_union(self.status_bytes(*status_bytes))
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
    def _unpack_data(self, data):
        """
        Method to unpack the data from the returned bytes in packed mode

        :param data: list of bytes to be decoded
        :return ret_data: float value

        """
        ret_data = self.packed_data(self.packed_bytes(*data))
        return float(ret_data.b)

    # commands overwriting the base implementaiton
    def read_data(self):
        """
        Reads measured data from instrument, returns a np.array.

        (This function also takes care of unpacking the data if required)

        :return data: np.array containing the data
        """
        # Adjusting the timeout to match the number of counts and the delay

        current_timeout = self.adapter.connection.timeout
        time_needed = self.number_readings * self.delay
        new_timeout = time_needed * 3 * 1000  # safety factor 3
        # TODO Review required! (2021/12/29)
        if new_timeout > current_timeout:
            if new_timeout >= 1e6:
                # Disables timeout if measurement would take more then 1000 sec
                new_timeout = 1000000
                log.info("HP3437A: timeout deactivated")
            self.adapter.connection.timeout = new_timeout
            log.info("HP3437A: timeout changed to %g", new_timeout)
        read_data = self.adapter.connection.read_raw()
        # check if data is in packed format format
        if self.talk_ascii is not True:
            processed_data = []
            read_data_length = int(len(read_data) / 2)
            for i in range(0, read_data_length):
                _from = i * 2
                _to = _from + 2
                processed_data.append(self._unpack_data(self, read_data[_from:_to]))
            self.adapter.connection.timeout = current_timeout
            return np.array(processed_data)
        self.adapter.connection.timeout = current_timeout
        return np.array(read_data[:-2].decode("ASCII").split(","), dtype=float)

    # commands/properties for instrument control
    def check_errors(self):
        """
        As this instrument does not have a error indication bit,
        this function alwyas returns an empty list.

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
        if value is True:
            self.write("F1")
        else:
            self.write("F2")

    # TODO: this needs more work
    # talk_ascii = HPLegacyInstrument.control(
    #     "B", "%s",
    #     """
    #     Return True if the instrument is set to ASCII communication,
    #     this property can be set.
    #     This property can be read
    #     """,
    #     values={True: "F1", False: "F2"},
    #     map_values=True,
    #     get_process= lambda x : str("F"+(str(decode_status( x, field="Format"))+1)),
    #     )
    @property
    def delay(self):
        """Return the value (float) for the delay between two measurements,
        this property can be set,

        valid range: 100ns - 0.999999s

        """
        return self.decode_status(self, self.fetch_status(), "Delay")

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
        return self.decode_status(self, self.fetch_status(), "Number")

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
        return self._decode_range(self, self.fetch_status())

    @range.setter
    def range(self, value):
        range_str = "R" + format(
            round(math.log10(strict_discrete_set(value, [0.1, 1, 10])) + 2), "d"
        )
        self.write(range_str)

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
        return self.decode_status(self, self.fetch_status(), "SRQ")

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
        return self._decode_trigger(self, self.fetch_status())

    @trigger.setter
    def trigger(self, value):
        trig_set = self.TRIGGERS[strict_discrete_set(value, self.TRIGGERS)]
        self.write(trig_set)
