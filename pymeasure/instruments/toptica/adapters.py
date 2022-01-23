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

from pymeasure.adapters import VISAAdapter
from pyvisa.errors import VisaIOError


class TopticaAdapter(VISAAdapter):
    """ Adapter class for connecting to Toptica Console via a serial
    connection.

    :param port: pyvisa resource name of the instrument
    :param baud_rate: communication speed
    :param kwargs: Any valid key-word argument for VISAAdapter
    """
    # compiled regular expression for finding numerical values in reply strings
    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    def __init__(self, port, baud_rate, **kwargs):
        kwargs.setdefault('preprocess_reply', self.extract_value)
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('write_termination', '\r\n')
        super().__init__(port,
                         asrl=dict(baud_rate=baud_rate),
                         **kwargs)
        # configure communication mode
        super().write('echo off')
        super().write('prom off')
        time.sleep(0.04)
        # clear the initial messages from the controller
        self.flush_read_buffer()
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

    def read(self):
        """ Reads a reply of the instrument which consists of at least two
        lines. The initial ones are the reply to the command while the last one
        should be '[OK]' which acknowledges that the device is ready to receive
        more commands.

        Note: '[OK]' is always returned as last message even in case of an
        invalid command, where a message indicating the error is returned
        before the '[OK]'

        :returns: string containing the ASCII response of the instrument.
        """
        reply = super().read()  # read back the LF+CR which is always sent back
        if reply != "":
            raise ValueError(
                "TopticaAdapter.read(1): Error after command "
                f"'{self.lastcommand}' with message '{reply}'")
        msg = []
        try:
            while True:
                line = super().read()
                if line == '[OK]':
                    break
                msg.append(line)
        except VisaIOError:
            reply = '\n'.join(msg)
            self.flush_read_buffer()
            raise ValueError(
                "TopticaAdapter.read(2): Error after command "
                f"'{self.lastcommand}' with message '{reply}'")
        return '\n'.join(msg)

    def write(self, command, check_ack=True):
        """ Writes a command to the instrument. Also reads back a LF+CR which
        is always sent back.

        :param command: command string to be sent to the instrument
        :param check_ack: flag to decide if also an acknowledgement from the
          device is expected. This is the case for set commands.
        """
        self.lastcommand = command
        super().write(command)
        # The following lines are used in order to avoid the need of a
        # complicated Instrument where every property would need to use
        # check_set/get_errors and many Adapter functions would need to be
        # reimplemented in the Instrument. See discussion in PR #352
        if check_ack:
            reply = self.read()
            if reply != "":
                # if any message is returned here this indicates some misuse
                raise ValueError(
                    f"TopticaAdapter.write: Error after command '{command}'"
                    f"with message '{reply}'")

    def ask(self, command):
        """ Writes a command to the instrument and returns the resulting ASCII
        response

        :param command: command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command, check_ack=False)
        time.sleep(self.connection.query_delay)
        return self.read()
