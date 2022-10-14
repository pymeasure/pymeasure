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

import re
import time
from warnings import warn

from pymeasure.adapters import TelnetAdapter


class AttocubeConsoleAdapter(TelnetAdapter):
    """ Adapter class for connecting to the Attocube Standard Console. This
    console is a Telnet prompt with password authentication.

    :param host: host address of the instrument
    :param port: TCPIP port
    :param passwd: password required to open the connection
    :param kwargs: Any valid key-word argument for TelnetAdapter
    """
    # compiled regular expression for finding numerical values in reply strings
    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    def __init__(self, host, port, passwd, **kwargs):
        self.read_termination = '\r\n'
        self.write_termination = self.read_termination
        kwargs.setdefault('preprocess_reply', self.extract_value)
        super().__init__(host, port, **kwargs)
        time.sleep(self.query_delay)
        super().read()  # clear messages sent upon opening the connection
        # send password and check authorization
        self.write(passwd)
        time.sleep(self.query_delay)
        ret = super().read()
        authmsg = ret.split(self.read_termination)[1]
        if authmsg != 'Authorization success':
            raise Exception(f"Attocube authorization failed '{authmsg}'")
        # switch console echo off
        self.write('echo off')
        _ = self.read()

    def extract_value(self, reply):
        """ preprocess_reply function for the Attocube console. This function
        tries to extract <value> from 'name = <value> [unit]'. If <value> can
        not be identified the original string is returned.

        :param reply: reply string
        :returns: string with only the numerical value, or the original string
        """
        r = self._reg_value.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    def _read(self):
        """ Reads a reply of the instrument which consists of one or more
        lines. The first ones are the reply to the command while the last one
        is 'OK' or 'ERROR' to indicate any problem. In case the status is not OK
        a ValueError is raised.

        :returns: String ASCII response of the instrument.
        """
        # one would want to use self.read_termination as 'sep' below, but this
        # is not possible because of a firmware bug resulting in inconsistent
        # line endings
        raw = super()._read().strip(self.read_termination).rsplit(sep='\n', maxsplit=1)
        if raw[-1] != 'OK':
            if raw[0] == "" or len(raw) == 1:  # clear buffer
                super()._read()  # without error checking
            raise ValueError("AttocubeConsoleAdapter: Error after command "
                             f"{self.lastcommand} with message {raw[0]}")
        return raw[0].strip('\r')  # strip possible CR char

    def _write(self, command):
        """ Writes a command to the instrument

        :param command: command string to be sent to the instrument
        :param check_ack: boolean flag to decide if the acknowledgement is read
            back from the instrument. This should be True for set pure commands
            and False otherwise.
        """
        self.lastcommand = command
        super()._write(command + self.write_termination)

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        warn("Do not call `Adapter.ask`, but `Instrument.ask` instead.",
             FutureWarning)
        self.write(command)
        time.sleep(self.query_delay)
        return self.read()
