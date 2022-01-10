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
# import math
# import struct
# from enum import IntFlag
# import numpy as np
from pymeasure.instruments import Instrument
# from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32


class HPLegacyInstrument(Instrument):
    """
    Class for legacy HP instruments from the time before SPCI, based on pymeasure.Instrument

    more details to be entered later

    """

    def __init__(self, adapter, name, status_bytes, status_bitfield, **kwargs):
        super(HPLegacyInstrument, self).__init__(
            adapter, name,
            includeSCPI=False,
            send_end=True,
            read_termination="\r\n",
            **kwargs,
        )

        self.name = name
        self.adapter = adapter
        self.status_bytes_count = status_bytes
        self.status_bits = status_bitfield
        # print(status_bitfield)
        # self.status_bits = self.bitfield_factory(status_bitfield)
        self.status_bytes = self.bytefield_factory(status_bytes)
        self.status_union = self.union_factory(self.status_bytes, self.status_bits)

        log.info(f"Initializing {self.name}")

    def write(self, command):
        """ This is needed only if 'B' cannot be followed by a termination character (to be checked) """
        if command == "B":
            self.adapter.connection.write("B", termination="")
        else:
            # super().write(command)
            self.adapter.connection.write(command)

    def values(self, command, **kwargs):
        if command == "B":
            self.write(command)
            return self.adapter.connection.read_raw(**kwargs)
        else:
            return super().values(command, **kwargs)

    @property
    def status(self):
        """
        Returns an object representing the current status of the unit.

        """
        current_status = self.decode_status(self, self.fetch_status())
        return current_status

    def fetch_status(self):
        """Method to read the status bytes from the instrument
        :return current_status: a byte array representing the instrument status
        :rtype current_status: bytes
        """
        self.write("B")
        current_status = self.adapter.read_bytes(self.status_bytes_count)
        return current_status

    @staticmethod
    def decode_status(self, status_bytes, field=None):
        """Method to handle the decoding of the status bytes into something meaningfull

        :param status_bytes: list of bytes to be decoded
        :param field: name of field to be returned
        :return ret_val: int status value

        """
        ret_val = self.status_union(self.status_bytes(*status_bytes))
        if field is None:
            return ret_val.b
        if field == "SRQ":
            return self.SRQ(getattr(ret_val.b, field))
        return getattr(ret_val.b, field)

    # facotry components
    def bytefield_factory(self, n_bytes, type_of_entry=c_uint8):
        """
        create structure with n entries for the byte part of the structured unions

        :param n_bytes:
        :param type_of_entry: type to be used, defaults to ctypes.c_uint8
        :return byte_struct: bytefield struct
        :rtype ctypes.Structure:
        """
        listing = []
        for i in range(0, n_bytes):
            listing.append(("byte" + str(i), type_of_entry))

        class ByteStruct(ctypes.Structure):
            """
            Struct type element for the data in the bitfield expressed as bytes
            """
            _fields_ = listing

            def __str__(self):
                """
                Returns a pretty formatted string showing the status of the instrument

                """
                ret_str = ""
                for field in self._fields_:
                    ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"
                return ret_str

        return ByteStruct

    def bitfield_factory(self, field_list, bigendianess=0, packing=0):
        """
        create structure for the bit part of the structured unions

        :param field_list: list of field entries
        :param bigendianess: int set to 1 if bigendian is required (defaults to 0)
        :param packing: int
        :return byte_struct: bitfield struct
        :rtype ctypes.Structure:
        """
        used_struct = ctypes.Structure
        if bigendianess == 1:
            used_struct = ctypes.BigEndianStructure

        class BitStruct(used_struct):
            """
            Struct type element for the data in the bitfield
            """
            if packing == 1:
                _pack_ = 1
            _fields_ = field_list

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

        return BitStruct

    def union_factory(self, byte_struct, bit_struct):
        class Combined(ctypes.Union):
            """Union type element for the decoding of the bit-fields
            """
            _fields_ = [("B", byte_struct), ("b", bit_struct)]

        return Combined

    def GPIB_trigger(self):
        """
        Initate trigger via low-level GPIB-command (aka GET - group execute trigger)

        """
        self.adapter.connection.assert_trigger()

    def reset(self):
        """
        Initatiates a reset (like a power-on reset) of the HP3478A

        """
        self.adapter.connection.clear()

    def shutdown(self):
        """
        provides a way to gracefully close the connection to the HP3478A

        """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()
