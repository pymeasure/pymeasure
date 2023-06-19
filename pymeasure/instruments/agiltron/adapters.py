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

import telnetlib
import time
import re
from warnings import warn

from pymeasure.adapters import TelnetAdapter


class AgiltronConsoleAdapter(TelnetAdapter):
    """This console is a Telnet prompt with password authentication.

    :param host: host address of the instrument
    :param port: TCPIP port
    :param passwd: password required to open the connection
    :param kwargs: Any valid key-word argument for TelnetAdapter
    """

    # compiled regular expression for finding numerical values in reply strings
    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    def __init__(self, host, port=23, query_delay=0, **kwargs):
        self.read_termination = "\r\n"
        self.write_termination = self.read_termination

        super().__init__(host, port, **kwargs)

    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        Do not override in a subclass!

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.

        """
        self.write_termination = "\r\n"
        self.log.debug("WRITE:%s", command)
        self._write(command, **kwargs)

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        Do not override in a subclass!

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        self.read_termination = "\r\r\n"
        read = self._read(**kwargs)
        self.log.debug("READ:%s", read)
        return read

    def _write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        self.connection.write((command + self.write_termination).encode(), **kwargs)

    def _read(self, **kwargs):
        """Read something even with blocking the I/O. After something is
        received check again to obtain a full reply.

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        read = self.connection.read_some(**kwargs).decode() + self.connection.read_very_eager(**kwargs).decode()
        # Python>3.8 return read.removesuffix(self.read_termination)
        # if self.read_termination:
        #     return read.split(self.read_termination)[1]
        # else:
        return read
