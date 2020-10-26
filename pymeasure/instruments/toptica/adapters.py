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

from pymeasure.adapters import VISAAdapter


class TopticaAdapter(VISAAdapter):
    """ Adapter class for connecting to the Attocube Standard Console. This
    console is a Telnet prompt with password authentication.

    :param host: host address of the instrument
    :param port: TCPIP port
    :param passwd: password required to open the connection
    :param kwargs: Any valid key-word argument for TelnetAdapter
    """
    # compiled regular expression for finding numerical values in reply strings
    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    def __init__(self, port, baud_rate, **kwargs):
        kwargs.setdefault('preprocess_reply', self.extract_value)
        super().__init__(port, **kwargs)
        # hack to set baud_rate since VISAAdapter would filter it out!
        self.connection.baud_rate = baud_rate
        # configure communication mode
        super().write('echo off')
        super().write('prom off')
        time.sleep(0.04)
        # clear the initial messages from the controller
        self.flush()
        self.ask('talk usual')

    def extract_value(self, reply):
        """ preprocess_reply function which tries to extract <value> from 'name
        = <value> [unit]'. If <value> can not be identified the orignal string
        is returned.

        :param reply: reply string
        :returns: string with only the numerical value, or the original string
        """
        r = self._reg_value.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    def check_acknowledgement(self, reply):
        """ checks if reply is '[OK]', otherwise a ValueError is raised and the
        read buffer is flushed because one has to assume that some
        communication is out of sync.

        :param reply: reply string of the instrument which should be checked
        """
        if reply != '[OK]':
            self.flush()
            raise ValueError(
                f"TopticaAdapter: Error after command '{self.lastcommand}' "
                f"with message '{reply}'")

    def _read_stripped(self):
        """ read a reply from the instrument and strip the termination sequence
        """
        return super().read().strip(self.connection.read_termination)

    def read(self):
        """ Reads a reply of the instrument which consists of two lines. The
        first one is the reply to the command while the last one should be
        '[OK]' which acknowledges that the device is ready to receive more
        commands. The last line of the reply is saved in self.lastreply for
        potential error checking.

        Note: This command only understands replies with one data line. More
        complicated replies have to be parsed by using the underlying adapter
        methods!

        :returns: String ASCII response of the instrument.
        """
        reply = self._read_stripped()
        self.check_acknowledgement(self._read_stripped())
        return reply

    def write(self, command, check_ack=True):
        """ Writes a command to the instrument. Also reads back a LF+CR which
        is always sent back.

        :param command: command string to be sent to the instrument
        :param check_ack: flag to decide if also an acknowledgement from the
        device is expected. This is the case for set commands.
        """
        self.lastcommand = command
        super().write(command)
        reply = self._read_stripped()
        if reply != '':
            raise ValueError(
                f"TopticaAdapter.write: Error after command '{command}' with "
                f"message '{reply}'")
        if check_ack:
                self.check_acknowledgement(self._read_stripped())

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command, check_ack=False)
        time.sleep(self.connection.query_delay)
        return self.read()
