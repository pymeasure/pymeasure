#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from pymeasure.adapters import TelnetAdapter

# compiled regular expression for finding numerical values in reply strings
_reg_value = re.compile(r"\w+\s+=\s+([-+]?[0-9]*\.?[0-9]+)")


def extract_value(reply):
    """ get_process function for the Attocube console which for numerical
    values typically return 'name = X.YZ unit'

    :param reply: reply string
    :returns: string with only the numerical value
    """
    r = _reg_value.search(reply)
    if r:
        return r.groups()[0]
    else:
        return reply


def extract_float(reply):
    """ get_process function for the Attocube console to obtain a float from
    the reply

    :param reply: reply string
    :returns: string with only the numerical value
    """
    return float(extract_value(reply))


def extract_int(reply):
    """ get_process function for the Attocube console to obtain an integer from
    the reply

    :param reply: reply string
    :returns: string with only the numerical value
    """
    return int(extract_value(reply))


class AttocubeConsoleAdapter(TelnetAdapter):
    """ Adapter class for connecting to the Attocube Standard Console. This
    console is a Telnet prompt with password authentication.

    :param host: host address of the instrument
    :param port: TCPIP port
    :param passwd: password required to open the connection
    :param kwargs: Any valid key-word argument for TelnetAdapter
    """
    def __init__(self, host, port, passwd, **kwargs):
        self.read_termination = '\r\n'
        self.write_termination = self.read_termination
        super().__init__(host, port, **kwargs)
        time.sleep(self.query_delay)
        super().read()  # clear messages sent upon opening the connection
        # send password and check authorization
        self.write(passwd, check_ack=False)
        time.sleep(self.query_delay)
        ret = super().read()
        authmsg = ret.split(self.read_termination)[1]
        if authmsg != 'Authorization success':
            raise Exception("Attocube authorization failed ('%s')" % authmsg)
        # switch console echo off
        _ = self.ask('echo off')

    def check_acknowledgement(self, reply, msg=""):
        """ checks the last reply of the instrument to be 'OK', otherwise a
        ValueError is raised.

        :param reply: last reply string of the instrument
        :param msg: optional message for the eventual error
        """
        if reply != 'OK':
            if msg == "":  # clear buffer
                msg = reply
                super().read()
            raise ValueError("AttocubeConsoleAdapter: Error after command '%s'"
                             " with message '%s'" % (self.lastcommand, msg))

    def read(self):
        """ Reads a reply of the instrument which consists of two or more
        lines. The first ones are the reply to the command while the last one
        is 'OK' or 'ERROR' to indicate any problem. In case the reply is not OK
        a ValueError is raised.

        :returns: String ASCII response of the instrument.
        """
        raw = super().read().strip(self.read_termination)
        # one would want to use self.read_termination as 'sep' below, but this
        # is not possible because of a firmware bug resulting in inconsistent
        # line endings
        ret, ack = raw.rsplit(sep='\n', maxsplit=1)
        ret = ret.strip('\r')  # strip possible CR char
        self.check_acknowledgement(ack, ret)
        return ret

    def write(self, command, check_ack=True):
        """ Writes a command to the instrument

        :param command: command string to be sent to the instrument
        :param check_ack: boolean flag to decide if the acknowledgement is read
        back from the instrument. This should be True for set pure commands and
        False otherwise.
        """
        self.lastcommand = command
        super().write(command + self.write_termination)
        if check_ack:
            reply = self.connection.read_until(self.read_termination.encode())
            msg = reply.decode().strip(self.read_termination)
            self.check_acknowledgement(msg)

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command, check_ack=False)
        time.sleep(self.query_delay)
        return self.read()
