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

import time

from pymeasure.adapters import TelnetAdapter


class AttocubeConsoleAdapter(TelnetAdapter):
    """ Adapter class for connecting to the Attocube Standard Console. This
    console is a Telnet prompt with password authentication.

    :param host: host address of the instrument
    :param port: TCPIP port
    :param passwd: password required to open the connection
    :param kwargs: Any valid key-word argument for TelnetAdapter
    """
    def __init__(self, host, port, passwd, **kwargs):
        self.terminator = '\r\n'
        super(AttocubeConsoleAdapter, self).__init__(host, port, **kwargs)
        # clear the initial messages from the controller
        time.sleep(self.query_delay)
        super(AttocubeConsoleAdapter, self).read()
        # send password and check authorization
        self.write(passwd, checkAck=False)
        time.sleep(self.query_delay)
        ret = super(AttocubeConsoleAdapter, self).read()
        authmsg = ret.split(self.terminator)[1]
        if authmsg != 'Authorization success':
            raise Exception("Attocube authorization failed ('%s')" % authmsg)
        # switch console echo off
        self.ask('echo off')

    def check_acknowledgement(self, reply, msg=""):
        """ Reads the reply of the instrument until the termination sequence.
        The returned string is check to be 'OK' and otherwise a ValueError is
        raised.

        :param msg: optional message for the eventual error
        :returns: String ASCII response of the instrument.
        """
        if reply.strip() != 'OK':
            if msg == "":  # clear buffer
                msg = reply.strip()
                super(AttocubeConsoleAdapter, self).read()
            raise ValueError("AttocubeConsoleAdapter: Error after command '%s'"
                             " with message '%s'" % (self.lastcommand, msg))

    def read(self):
        """ Reads a reply of the instrument which consists of two or more
        lines. The first ones are the reply to the command while the last one
        is 'OK' or 'ERROR' to indicate any problem. In case the reply is not OK
        a ValueError is raised.

        :returns: String ASCII response of the instrument.
        """
        raw = super(AttocubeConsoleAdapter, self).read().strip()
        lines = raw.split('\n')  # line endings inconsistent '\n', or '\r\n'
        ret = '\n'.join(line.strip() for line in lines[:-1])
        self.check_acknowledgement(lines[-1], ret)
        return ret

    def write(self, command, checkAck=True):
        """ Writes a command to the instrument

        :param command: command string to be sent to the instrument
        """
        self.lastcommand = command
        super(AttocubeConsoleAdapter, self).write(command + self.terminator)
        if checkAck:
            reply = self.connection.read_until(self.terminator.encode())
            self.check_acknowledgement(reply.decode())

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command, checkAck=False)
        time.sleep(self.query_delay)
        return self.read()
