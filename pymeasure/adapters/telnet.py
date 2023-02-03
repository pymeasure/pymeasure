#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from warnings import warn

from .adapter import Adapter


class TelnetAdapter(Adapter):
    """ Adapter class for using the Python telnetlib package to allow
    communication to instruments

    .. deprecated:: 0.11.2
        The Python telnetlib module is deprecated since Python 3.11 and will be removed
        in Python 3.13 release.
        As a result, TelnetAdapter is deprecated, use VISAAdapter instead.
        The VISAAdapter supports TCPIP socket connections. When using the VISAAdapter,
        the `resource_name` argument should be `TCPIP[board]::<host>::<port>::SOCKET`.
        see here, <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>

    :param host: host address of the instrument
    :param port: TCPIP port
    :param query_delay: delay in seconds between write and read in the ask
        method
    :param preprocess_reply: An optional callable used to preprocess
        strings received from the instrument. The callable returns the
        processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.

    :param kwargs: Valid keyword arguments for telnetlib.Telnet, currently
        this is only 'timeout'
    """

    def __init__(self, host, port=0, query_delay=0, preprocess_reply=None,
                 **kwargs):
        warn("TelnetAdapter is deprecated, use VISAAdapter instead.", FutureWarning)
        super().__init__(preprocess_reply=preprocess_reply)
        self.query_delay = query_delay
        if query_delay:
            warn("Use Instrument.ask with query_delay argument instead of Adapter.ask.",
                 FutureWarning)
        self.write_termination = kwargs.pop('write_termination', "")
        self.read_termination = kwargs.pop('read_termination', "")
        safe_keywords = ['timeout']
        for kw in kwargs:
            if kw not in safe_keywords:
                raise TypeError(
                    f"TelnetAdapter: unexpected keyword argument '{kw}', "
                    f"allowed are: {str(safe_keywords)}")
        self.connection = telnetlib.Telnet(host, port, **kwargs)

    def _write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        self.connection.write((command + self.write_termination).encode(), **kwargs)

    def _read(self, **kwargs):
        """ Read something even with blocking the I/O. After something is
        received check again to obtain a full reply.

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        read = self.connection.read_some(**kwargs).decode() + \
            self.connection.read_very_eager(**kwargs).decode()
        # Python>3.8 return read.removesuffix(self.read_termination)
        if self.read_termination:
            return read.split(self.read_termination)[0]
        else:
            return read

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        .. deprecated:: 0.11
           Call `Instrument.ask` instead.

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        warn("Do not call `Adapter.ask`, but `Instrument.ask` instead.",
             FutureWarning)
        self.write(command)
        time.sleep(self.query_delay)
        return self.read()

    def __repr__(self):
        return "<TelnetAdapter(host=%s, port=%d)>" % (self.connection.host, self.connection.port)
