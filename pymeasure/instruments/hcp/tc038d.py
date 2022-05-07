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

import logging

from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TC038D(Instrument):
    """
    Communication with the HCP TC038D oven.

    This is the newer version with DC heating.

    The oven expects raw bytes written, no ascii code, and sends raw bytes.
    For the variables are two or four-byte modes available. We use the
    four-byte mode addresses, so do we. In that case element count has to be
    double the variables read.
    """

    functions = {'read': 0x03, 'writeMultiple': 0x10,
                 'writeSingle': 0x06, 'echo': 0x08}

    def __init__(self, resourceName, address=1, timeout=1000):
        """Initialize the device."""
        super().__init__(resourceName, "TC038D", timeout=timeout)
        self.address = address

    def CRC16(self, data):
        """Calculate the CRC16 checksum for the data byte array."""
        CRC = 0xFFFF
        for octet in data:
            CRC ^= octet
            for j in range(8):
                lsb = CRC & 0x1  # least significant bit
                CRC = CRC >> 1
                if lsb:
                    CRC ^= 0xA001
        return [CRC & 0xFF, CRC >> 8]

    def readRegister(self, address, count=2):
        """Read count variables from start address on."""
        # Count has to be double the number of elements in 4-byte-mode.
        data = [self.address]
        data.append(0x03)  # function code
        data += [address >> 8, address & 0xFF]  # 2B address
        data += [count >> 8, count & 0xFF]  # 2B number of elements
        data += self.CRC16(data)
        self.adapter.connection.write_raw(bytes(data))
        got = self.adapter.connection.read_bytes(3)
        # Slave address, function, length
        if got[1] == 0x03:
            length = got[2]
            read = self.adapter.connection.read_bytes(length + 2)
            # data, CRC
            return read[:-2]
        else:  # an error occurred
            end = self.adapter.connection.read_bytes(2)  # empty the buffer
            if got[2] == 0x02:
                raise ValueError("The read start address is incorrect.")
            if got[2] == 0x03:
                raise ValueError("The number of elements exceeds the allowed range")
            raise ConnectionError(f"Unknown read error. Received: {got} {end}")

    def writeMultiple(self, address, values, byteMode=4):
        """Write multiple variables."""
        data = [self.address]
        data.append(0x10)  # function code
        data += [address >> 8, address & 0xFF]  # 2B address
        if isinstance(values, int):
            data += [0x0, byteMode // 2]  # 2B number of elements
            data.append(byteMode)  # 1B number of write data
            for i in range(byteMode - 1, -1, -1):
                data.append(values >> i * 8 & 0xFF)
        elif hasattr(values, "__iter__"):
            data += [len(values) >> 8, len(values) & 0xFF]  # 2B number of elements
            data.append(len(values) * byteMode)  # 1B number of write data
            for element in values:
                for i in range(byteMode - 1, -1, -1):
                    data.append(element >> i * 8 & 0xFF)
        else:
            raise ValueError(("Values has to be an integer or an iterable of "
                              f"integers. values: {values}"))
        data += self.CRC16(data)
        self.adapter.connection.write_raw(bytes(data))
        got = self.adapter.connection.read_bytes(2)
        # slave address, function
        if got[1] == 0x10:
            return self.adapter.connection.read_bytes(2 + 2 + 2)
            # start address, number elements, CRC
        else:
            end = self.adapter.connection.read_bytes(3)  # error code and CRC
            errors = {0x02: "Wrong start address",
                      0x03: "Variable data error",
                      0x04: "Operation error"}
            raise ValueError(errors[end[0]])

    @property
    def setpoint(self):
        """Get the current setpoint in °C."""
        return int.from_bytes(self.readRegister(0x106), byteorder='big') / 10

    @setpoint.setter
    def setpoint(self, value):
        """Set the setpoint in °C."""
        value = int(round(value * 10, 0))
        self.writeMultiple(0x106, value)

    @property
    def temperature(self):
        """Get the current temperature in °C."""
        return int.from_bytes(self.readRegister(0x0), byteorder='big') / 10
