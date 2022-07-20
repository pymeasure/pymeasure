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

import serial
import numpy as np
from pyvisa.util import to_ieee_block, to_hp_block, to_binary_block
from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SerialAdapter(Adapter):
    """ Adapter class for using the Python Serial package to allow
    serial communication to instrument

    :param port: Serial port
    :param preprocess_reply: optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.
    :param kwargs: Any valid key-word argument for serial.Serial
    """

    def __init__(self, port, preprocess_reply=None, **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        if isinstance(port, serial.SerialBase):
            self.connection = port
        else:
            self.connection = serial.Serial(port, **kwargs)

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        self.connection.write(command.encode())  # encode added for Python 3

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII response

        :returns: String ASCII response of the instrument.
        """
        return b"\n".join(self.connection.readlines()).decode()

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        self.connection.write(command.encode())
        binary = self.connection.read().decode()
        # header = binary[:header_bytes]
        data = binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def _format_binary_values(self, values, datatype='f', is_big_endian=False, header_fmt="ieee"):
        """Format values in binary format, used internally in :meth:`.write_binary_values`.

        :param values: data to be written to the device.
        :param datatype: the format string for a single element. See struct module.
        :param is_big_endian: boolean indicating endianess.
        :param header_fmt: Format of the header prefixing the data ("ieee", "hp", "empty").
        :return: binary string.
        :rtype: bytes
        """

        if header_fmt == "ieee":
            block = to_ieee_block(values, datatype, is_big_endian)
        elif header_fmt == "hp":
            block = to_hp_block(values, datatype, is_big_endian)
        elif header_fmt == "empty":
            block = to_binary_block(values, b"", datatype, is_big_endian)
        else:
            raise ValueError("Unsupported header_fmt: %s" % header_fmt)

        return block

    def write_binary_values(self, command, values, **kwargs):
        """ Write binary data to the instrument, e.g. waveform for signal generators

        :param command: SCPI command to be sent to the instrument
        :param values: iterable representing the binary values
        :param kwargs: Key-word arguments to pass onto :meth:`._format_binary_values`
        :returns: number of bytes written
        """

        block = self._format_binary_values(values, **kwargs)
        return self.connection.write(command.encode() + block)

    def __repr__(self):
        return "<SerialAdapter(port='%s')>" % self.connection.port
