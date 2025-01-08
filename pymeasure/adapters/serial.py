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

import serial
from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SerialAdapter(Adapter):
    """ Adapter class for using the Python Serial package to allow
    serial communication to instrument

    :param port: Serial port
    :param preprocess_reply: An optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.

    :param write_termination: String appended to messages before writing them.
    :param read_termination: String expected at end of read message and removed.
    :param \\**kwargs: Any valid key-word argument for serial.Serial
    """

    def __init__(self, port, preprocess_reply=None,
                 write_termination="", read_termination="",
                 **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        if isinstance(port, serial.SerialBase):
            self.connection = port
        else:
            self.connection = serial.Serial(port, **kwargs)
        self.write_termination = write_termination
        self.read_termination = read_termination

    def _write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param \\**kwargs: Keyword arguments for the connection itself.
        """
        command += self.write_termination
        self._write_bytes(command.encode(), **kwargs)

    def _write_bytes(self, content, **kwargs):
        """Write the bytes `content` to the instrument.

        :param bytes content: The bytes to write to the instrument.
        :param \\**kwargs: Keyword arguments for the connection itself.
        """
        self.connection.write(content, **kwargs)

    def _read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (read_termination is removed first).
        """
        read = self._read_bytes(-1, break_on_termchar=True, **kwargs).decode()
        # Python>3.8 this shorter form is possible:
        # self._read_bytes(-1).decode().removesuffix(self.read_termination)
        if self.read_termination:
            return read.split(self.read_termination)[0]
        else:
            return read

    def _read_bytes(self, count, break_on_termchar, **kwargs):
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read from the whole read buffer (waits for timeout).
        :param bool break_on_termchar: Stop reading at a termination character.
        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        if break_on_termchar and self.read_termination:
            return self.connection.read_until(self.read_termination.encode(),
                                              count if count > 0 else None,
                                              **kwargs)
        elif count >= 0:
            return self.connection.read(count, **kwargs)
        else:
            # For -1 we empty the buffer completely
            return self._read_bytes_until_timeout()

    def _read_bytes_until_timeout(self, chunk_size=256, **kwargs):
        """Read from the serial until a timeout occurs, regardless of the number of bytes.

        :chunk_size: The number of bytes attempted to in a single transaction.
            Multiple of these transactions will occur.
        """
        # `Serial.readlines()` has an unpredictable timeout, see PR #866
        data = bytes()
        while True:
            chunk = self.connection.read(chunk_size, **kwargs)
            data += chunk
            if len(chunk) < chunk_size:  # If fewer bytes got returned, we had a timeout
                return data

    def flush_read_buffer(self):
        """Flush and discard the input buffer."""
        self.connection.reset_input_buffer()

    def __repr__(self):
        return "<SerialAdapter(port='%s')>" % self.connection.port
