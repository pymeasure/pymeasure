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

import logging

from enum import IntEnum

from pymeasure.instruments import Instrument


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def CRC16(data):
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


class Functions(IntEnum):
    R = 0x03
    WRITESINGLE = 0x06
    ECHO = 0x08  # register address has to be 0
    W = 0x10  # writing multiple variables


class TC038D(Instrument):
    """
    Communication with the HCP TC038D oven.

    This is the newer version with DC heating.

    The oven expects raw bytes written, no ascii code, and sends raw bytes.
    For the variables are two or four-byte modes available. We use the
    four-byte mode addresses. In that case element count has to be
    double the variables read.
    """

    byteMode = 4

    def __init__(self, adapter, name="TC038D", address=1, timeout=1000,
                 **kwargs):
        """Initialize the device."""
        super().__init__(adapter, name, timeout=timeout,
                         includeSCPI=False,
                         **kwargs)
        self.address = address

    def write(self, command):
        """Write a command to the device.

        :param str command: comma separated string of:
            - the function: read ('R') or write ('W') or 'echo',
            - the address to write to (e.g. '0x106' or '262'),
            - the values (comma separated) to write
            - or the number of elements to read (defaults to 1).
        """
        function, address, *values = command.split(",")
        function = Functions[function]
        data = [self.address]  # 1B device address
        data.append(function)  # 1B function code
        address = int(address, 16) if "x" in address else int(address)
        data.extend(address.to_bytes(2, "big"))  # 2B register address
        if function == Functions.W:
            elements = len(values) * self.byteMode // 2
            data.extend(elements.to_bytes(2, "big"))  # 2B number of elements
            data.append(elements * 2)  # 1B number of bytes to write
            for element in values:
                data.extend(int(element).to_bytes(self.byteMode, "big", signed=True))
        elif function == Functions.R:
            count = int(values[0]) * self.byteMode // 2 if values else self.byteMode // 2
            data.extend(count.to_bytes(2, "big"))  # 2B number of elements to read
        elif function == Functions.ECHO:
            data[-2:] = [0, 0]
            if values:
                data.extend(int(values[0]).to_bytes(2, "big"))  # 2B test data
        data += CRC16(data)
        self.write_bytes(bytes(data))

    def read(self):
        """Read response and interpret the number, returning it as a string."""
        # Slave address, function
        got = self.read_bytes(2)
        if got[1] == Functions.R:
            # length of data to follow
            length = self.read_bytes(1)
            # data length, 2 Byte CRC
            read = self.read_bytes(length[0] + 2)
            if read[-2:] != bytes(CRC16(got + length + read[:-2])):
                raise ConnectionError("Response CRC does not match.")
            return str(int.from_bytes(read[:-2], byteorder="big", signed=True))
        elif got[1] == Functions.W:
            # start address, number elements, CRC; each 2 Bytes long
            got += self.read_bytes(2 + 2 + 2)
            if got[-2:] != bytes(CRC16(got[:-2])):
                raise ConnectionError("Response CRC does not match.")
        elif got[1] == Functions.ECHO:
            # start address 0, data, CRC; each 2B
            got += self.read_bytes(2 + 2 + 2)
            if got[-2:] != bytes(CRC16(got[:-2])):
                raise ConnectionError("Response CRC does not match.")
            return str(int.from_bytes(got[-4:-2], "big"))
        else:  # an error occurred
            # got[1] is functioncode + 0x80
            end = self.read_bytes(3)  # error code and CRC
            errors = {0x02: "Wrong start address.",
                      0x03: "Variable data error.",
                      0x04: "Operation error."}
            if end[0] in errors.keys():
                raise ValueError(errors[end[0]])
            else:
                raise ConnectionError(f"Unknown read error. Received: {got} {end}")

    def check_set_errors(self):
        """Check for errors after having set a property.

        Called if :code:`check_set_errors=True` is set for that property.
        """
        try:
            self.read()
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []

    def ping(self, test_data=0):
        """Test the connection sending an integer up to 65535, checks the response."""
        assert int(self.ask(f"ECHO,0,{test_data}")) == test_data

    setpoint = Instrument.control(
        "R,0x106", "W,0x106,%i",
        """Control the setpoint of the oven in °C.""",
        check_set_errors=True,
        get_process=lambda v: v / 10,
        set_process=lambda v: int(round(v * 10)),
    )

    temperature = Instrument.measurement(
        "R,0x0",
        """Measure the current oven temperature in °C.""",
        get_process=lambda v: v / 10,
    )
