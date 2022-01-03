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

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32


class HPsupport():
    """
    Support module containing the bitfield & bytefield definitions for currentlly

        HP3437A
        HP3478A


    """

    def __init__(self, handle):
        self.handle = handle
        print(handle)
        if handle == 3437:
            self.status_bits = bitfield_factory(HP3437A_Status_bitfield, bigendianess=1,
                                                packing=1)
            self.status_bytes = bytefield_factory(HP3437A_STATUS_BYTES)
            self.status = union_factory(self.status_bits, self.status_bytes)

            self.packed_bits = bitfield_factory(HP3437A_Packed_bitfield, bigendianess=1,
                                                packing=1)
            self.packed_bytes = bytefield_factory(HP3437A_PACKED_BYTES)
            self.packed_data = union_factory(self.packed_bits, self.packed_bytes)
            return None

        if handle == 3478:
            self.status_bits = bitfield_factory(HP3478A_Status_bitfield)
            self.status_bytes = bytefield_factory(HP3478A_STATUS_BYTES)
            self.status = union_factory(self.status_bits, self.status_bytes)
            return None

        raise ValueError("handle not defined yet")


# definitions go here
HP3437A_STATUS_BYTES = 7
HP3437A_Status_bitfield = [
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

HP3437A_PACKED_BYTES = 2
HP3437A_Packed_bitfield = [
    ("range", c_uint8, 2),  # bit 0..1
    ("sign_bit", c_uint8, 1),
    ("MSD", c_uint8, 1),
    ("SSD", c_uint8, 4),
    ("TSD", c_uint8, 4),
    ("LSD", c_uint8, 4),
]

HP3478A_STATUS_BYTES = 5
HP3478A_Status_bitfield = [
    # Byte 1: Function, Range and Number of Digits
    ("digits",     c_uint8, 2),  # bit 0..1
    ("range",      c_uint8, 3),  # bit 2..4
    ("function",   c_uint8, 3),  # bit 5..7

    # Byte 2: Status Bits
    ("int_trig",   c_uint8, 1),
    ("auto_range", c_uint8, 1),
    ("auto_zero",  c_uint8, 1),
    ("fifty_hz",   c_uint8, 1),
    ("front_rear", c_uint8, 1),
    ("cal_enable", c_uint8, 1),
    ("ext_trig",   c_uint8, 1),
    ("res1",       c_uint8, 1),

    # Byte 3: Serial Poll Mask (SRQ)
    ("SRQ_data_rdy",         c_uint8, 1),
    ("res2",                 c_uint8, 1),
    ("SRQ_syntax_error",     c_uint8, 1),
    ("SRQ_internal_error",   c_uint8, 1),
    ("SRQ_front_panel",      c_uint8, 1),
    ("SRQ_cal_error",        c_uint8, 1),
    ("res3",                 c_uint8, 1),
    ("SRQ_PON",              c_uint8, 1),

    # Byte 4: Error Information
    ("ERR_cal",        c_uint8, 1),
    ("ERR_RAM",        c_uint8, 1),
    ("ERR_ROM",        c_uint8, 1),
    ("ERR_slope",      c_uint8, 1),
    ("ERR_AD",         c_uint8, 1),
    ("ERR_AD_Link",    c_uint8, 1),
    ("res4",           c_uint8, 1),
    ("res5",           c_uint8, 1),

    # Byte 5: DAC Value
    ("DAC_value",       c_uint8, 8),
]


def bytefield_factory(n_bytes, type_of_entry=c_uint8):
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
        _fields_ = listing

        def __str__(self):
            """
            Returns a pretty formatted string showing the status of the instrument

            """
            ret_str = ""
            for field in self._fields_:
                ret_str = ret_str + f"    {field[0]}: {getattr(self, field[0])}"
            return ret_str

    return ByteStruct


def bitfield_factory(field_list, bigendianess=0, packing=0):
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
        if packing == 1:
            _packing_ = 1
        _fields_ = field_list

        def __str__(self):
            """
            Returns a pretty formatted string showing the status of the instrument

            """
            ret_str = ""
            for field in self._fields_:
                ret_str = ret_str + f"    {field[0]}: {getattr(self, field[0])}"

            return ret_str

        def __float__(self):
            """
            Return a float value from the packed data of the HP3437A

            """
            if self.MSD:
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


def union_factory(byte_struct, bit_struct):
    class Combined(ctypes.Union):
        """Union type element for the decoding of the bit-fields
        """
        _fields_ = [("B", byte_struct), ("b", bit_struct)]

    return Combined

# definitions for the HP3437A
# # classes for the decoding of the 5-byte status word
# class HP3437A_StatusBytes(ctypes.Structure):
#     """
#     Support-Class for the 7 status bytes of the HP3437A
#     """

#     _fields_ = [
#         ("byte1", c_uint8),
#         ("byte2", c_uint8),
#         ("byte3", c_uint8),
#         ("byte4", c_uint8),
#         ("byte5", c_uint8),
#         ("byte6", c_uint8),
#         ("byte7", c_uint8),
#     ]


# class HP3437A_StatusBits(ctypes.BigEndianStructure):
#     """
#     Support-Class with the bit assignments for the 5 status byte of the HP3437A
#     """

#     _pack_ = 1
#     _fields_ = [
#         # Byte 1: Function, Range and Number of Digits
#         ("Format", c_uint8, 1),  # Bit 7
#         ("SRQ", c_uint8, 3),  # bit 4..6
#         ("trigger", c_uint8, 2),  # bit 2..3
#         ("range", c_uint8, 2),  # bit 0..1
#         # Byte 2 & 3:
#         ("Number", c_uint16, 16),
#         # Byte 2:
#         # ("NRDGS_MSD", c_uint8, 4),
#         # ("NRDGS_2SD", c_uint8, 4),
#         # Byte 3:
#         # ("NRDGS_3SD", c_uint8, 4),
#         # ("NRDGS_LSD", c_uint8, 4),
#         ("not_used", c_uint8(), 4),
#         ("Delay", c_uint32, 28),
#         # Byte 4:
#         # ("Not_Used", c_uint8, 4),
#         # ("Delay_MSD", c_uint8, 4),
#         # # Byte 5:
#         # ("Delay_2SD", c_uint8, 4),
#         # ("Delay_3SD", c_uint8, 4),
#         # # Byte 6:
#         # ("Delay_4SD", c_uint8, 4),
#         # ("Delay_5SD", c_uint8, 4),
#         # # Byte 7:
#         # ("Delay_6SD", c_uint8, 4),
#         # ("Delay_LSD", c_uint8, 4),
#     ]

#     def __str__(self):
#         """
#         Returns a pretty formatted string showing the status of the instrument

#         """
#         return f"format: {self.Format}, SRQ Mask:  {self.SRQ}, Trigger: {self.trigger}, Range: {self.range} \n"


# class HP3437A_PackedBytes(ctypes.Structure):
#     """
#     Support-Class for the 2 bytes of the HP3437A packed data transfer
#     """

#     _fields_ = [
#         ("byte1", c_uint8),
#         ("byte2", c_uint8),
#     ]


# class HP3437A_PackedBits(ctypes.BigEndianStructure):
#     """
#     Support-Class for the bits in the HP3437A packed data transfer
#     """

#     _pack_ = 1
#     _fields_ = [
#         ("range", c_uint8, 2),  # bit 0..1
#         ("sign_bit", c_uint8, 1),
#         ("MSD", c_uint8, 1),
#         ("SSD", c_uint8, 4),
#         ("TSD", c_uint8, 4),
#         ("LSD", c_uint8, 4),
#     ]

#     def __str__(self):
#         return f"range: {self.range}, sign_bit: {self.sign_bit}, MSD: {self.MSD}, 2SD: {self.SSD}, 3SD: {self.TSD}, LSD: {self.LSD} \n"

#     def __float__(self):
#         # range decoding
#         # (cf table 3-2, page 3-5 of the manual, HPAK document 9018-05946)
#         # 1 indicates 0.1V range
#         if self.range == 1:
#             cur_range = 0.1
#         # 2 indicates 10V range
#         if self.range == 2:
#             cur_range = 10.0
#         # 3 indicates 1V range
#         if self.range == 3:
#             cur_range = 1.0

#         signbit = 1
#         if self.sign_bit == 0:
#             signbit = -1

#         return (
#             cur_range
#             * signbit
#             * (
#                 self.MSD
#                 + float(self.SSD) / 10
#                 + float(self.TSD) / 100
#                 + float(self.LSD) / 1000
#             )
#         )


# class HP3437A_PackedData(ctypes.Union):
#     """Union type element for the decoding of the packed data bit-fields"""

#     _fields_ = [("B", HP3437A_PackedBytes), ("b", HP3437A_PackedBits)]


# class HP3437A_Status(ctypes.Union):
#     """Union type element for the decoding of the status bit-fields"""

#     _fields_ = [("B", HP3437A_StatusBytes), ("b", HP3437A_StatusBits)]


# # definitions for the HP3437A
# class HP3478A_StatusBytes(ctypes.Structure):
#     """
#     Support-Class for the 5 status byte of the HP3478A
#     """
#     _fields_ = [
#         ("byte1", c_uint8),
#         ("byte2", c_uint8),
#         ("byte3", c_uint8),
#         ("byte4", c_uint8),
#         ("byte5", c_uint8)
#     ]


# class HP3478A_StatusBits(ctypes.LittleEndianStructure):
#     """
#     Support-Class with the bit assignments for the 5 status byte of the HP3478A
#     """

#     _fields_ = [
#         # Byte 1: Function, Range and Number of Digits
#         ("digits",     c_uint8, 2),  # bit 0..1
#         ("range",      c_uint8, 3),  # bit 2..4
#         ("function",   c_uint8, 3),  # bit 5..7

#         # Byte 2: Status Bits
#         ("int_trig",   c_uint8, 1),
#         ("auto_range", c_uint8, 1),
#         ("auto_zero",  c_uint8, 1),
#         ("fifty_hz",   c_uint8, 1),
#         ("front_rear", c_uint8, 1),
#         ("cal_enable", c_uint8, 1),
#         ("ext_trig",   c_uint8, 1),
#         ("res1",       c_uint8, 1),

#         # Byte 3: Serial Poll Mask (SRQ)
#         ("SRQ_data_rdy",         c_uint8, 1),
#         ("res2",                 c_uint8, 1),
#         ("SRQ_syntax_error",     c_uint8, 1),
#         ("SRQ_internal_error",   c_uint8, 1),
#         ("SRQ_front_panel",      c_uint8, 1),
#         ("SRQ_cal_error",        c_uint8, 1),
#         ("res3",                 c_uint8, 1),
#         ("SRQ_PON",              c_uint8, 1),

#         # Byte 4: Error Information
#         ("ERR_cal",        c_uint8, 1),
#         ("ERR_RAM",        c_uint8, 1),
#         ("ERR_ROM",        c_uint8, 1),
#         ("ERR_slope",      c_uint8, 1),
#         ("ERR_AD",         c_uint8, 1),
#         ("ERR_AD_Link",    c_uint8, 1),
#         ("res4",           c_uint8, 1),
#         ("res5",           c_uint8, 1),

#         # Byte 5: DAC Value
#         ("DAC_value",       c_uint8, 8),
#     ]

#     def __str__(self):
#         """
#         Returns a pretty formatted (human readable) string showing the status of the instrument

#         """
#         # Definitions for different specifics of this instrument
#         MODES = {"DCV": "F1",
#                  "ACV": "F2",
#                  "R2W": "F3",
#                  "R4W": "F4",
#                  "DCI": "F5",
#                  "ACI": "F6",
#                  "Rext": "F7",
#                  }

#         INV_MODES = {v: k for k, v in MODES.items()}
#         RANGES = {"DCV": {3E-2: "R-2", 3E-1: "R-1", 3: "R0", 30: "R1", 300: "R2",
#                           "auto": "RA"},
#                   "ACV": {3E-1: "R-1", 3: "R0", 30: "R1", 300: "R2", "auto": "RA"},
#                   "R2W": {30: "R1", 300: "R2", 3E3: "R3", 3E4: "R4", 3E5: "R5",
#                           3E6: "R6", 3E7: "R7", "auto": "RA"},
#                   "R4W": {30: "R1", 300: "R2", 3E3: "R3", 3E4: "R4", 3E5: "R5",
#                           3E6: "R6", 3E7: "R7", "auto": "RA"},
#                   "DCI": {3E-1: "R-1", 3: "R0", "auto": "RA"},
#                   "ACI": {3E-1: "R-1", 3: "R0", "auto": "RA"},
#                   "Rext": {3E7: "R7", "auto": "RA"},
#                   }

#         cur_mode = INV_MODES["F" + str(self.function)]
#         cur_range = list(RANGES[cur_mode].keys())[self.range - 1]
#         if cur_range >= 1E6:
#             r_str = str(cur_range / 1E6) + ' M'
#         elif cur_range >= 1000:
#             r_str = str(cur_range / 1000) + ' k'
#         elif cur_range <= 1:
#             r_str = str(cur_range * 1000) + ' m'
#         else:
#             r_str = str(cur_range) + ' '
#         return (
#             "function: {}, range: {}, digits: {}\
#                 \nStatus:\n  internal | external trigger: {} | {}\
#                 \n  Auto ranging: {}\n  AutoZero: {}\
#                 \n  50Hz mode: {}\n  Front/Rear selection: {} \
#                 \n  Calibration enable: {}\
#                 \nSerial poll mask (SRQ):\n  SRQ for Data ready: {}\
#                 \n  SRQ for Syntax error: {}\n  SRQ for Internal error: {}\
#                 \n  SRQ Front Panel button: {}\
#                 \n  SRQ for Cal err: {}\n  SQR for Power on: {}\
#                 \nError information: \n  Calibration: {} \n  RAM: {}\n  ROM: {}\
#                 \n  AD Slope: {}\n  AD: {}\n  AD-Link: {} \
#                 \nDAC value: {}".format(
#                 cur_mode, r_str, 6 - self.digits, self.int_trig, self.ext_trig,
#                 self.auto_range, self.auto_zero, self.fifty_hz,
#                 self.front_rear, self.cal_enable, self.SRQ_data_rdy,
#                 self.SRQ_syntax_error, self.SRQ_internal_error,
#                 self.SRQ_front_panel, self.SRQ_cal_error, self.SRQ_PON,
#                 self.ERR_cal, self.ERR_RAM, self.ERR_ROM, self.ERR_slope,
#                 self.ERR_AD, self.ERR_AD_Link, self.DAC_value)
#         )


# class HP3478A_Status(ctypes.Union):
#     """Union type element for the decoding of the status bit-fields
#     """
#     _fields_ = [
#         ("B", HP3478A_StatusBytes),
#         ("b", HP3478A_StatusBits)
#     ]
