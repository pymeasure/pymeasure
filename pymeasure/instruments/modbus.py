#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

"""Building blocks shared by instruments communicating via Modbus."""

#: Modbus function code to read holding registers.
READ_REGISTERS = 0x03
#: Modbus function code to write multiple registers.
WRITE_REGISTERS = 0x10

#: Description of the standard Modbus exception codes.
MODBUS_ERRORS = {
    0x01: "Illegal function.",
    0x02: "Illegal data address.",
    0x03: "Illegal data value.",
    0x04: "Slave device failure.",
}


def crc16(data: bytes | bytearray) -> bytes:
    """Calculate the Modbus RTU CRC16 of `data`, returned low byte first."""
    crc = 0xFFFF
    for octet in data:
        crc ^= octet
        for _ in range(8):
            lsb = crc & 0x1
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc.to_bytes(2, "little")
