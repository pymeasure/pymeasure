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

from .adapter import Adapter


class TelnetAdapter(Adapter):
    """ Adapter class for using the Python telnetlib package to allow
    communication to instruments

    :param host: host address of the instrument
    :param port: TCPIP port
    :param query_delay: delay in seconds between write and read in the ask
        method
    :param preprocess_reply: optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.
    :param kwargs: Valid keyword arguments for telnetlib.Telnet, currently
        this is only 'timeout'
    """

    def __init__(self, host, port=0, query_delay=0, preprocess_reply=None,
                 **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        self.query_delay = query_delay
        safe_keywords = ['timeout']
        for kw in kwargs:
            if kw not in safe_keywords:
                raise TypeError(
                    f"TelnetAdapter: unexpected keyword argument '{kw}', "
                    f"allowed are: {str(safe_keywords)}")
        self.connection = telnetlib.Telnet(host, port, **kwargs)

    def write(self, command):
        """ Writes a command to the instrument

        :param command: command string to be sent to the instrument
        """
        self.connection.write(command.encode())

    def read(self):
        """ Read something even with blocking the I/O. After something is
        received check again to obtain a full reply.

        :returns: String ASCII response of the instrument.
        """
        return self.connection.read_some().decode() + \
            self.connection.read_very_eager().decode()

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command)
        time.sleep(self.query_delay)
        return self.read()

    def __repr__(self):
        return "<TelnetAdapter(host=%s, port=%d)>" % (self.connection.host, self.connection.port)
