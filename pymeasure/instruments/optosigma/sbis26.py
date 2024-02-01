#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from time import sleep
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AxisError(Exception):
    """
    Raised when a particular axis causes an error for OptoSigma SBIS26.


    """
    MESSAGE_ACK1 = {
        'X': 'Error of command',
        'K': 'Command received normally'
    }

    MESSAGE_ACK2 = {
        'C': 'Stopped by clockwise limit sensor detected',
        'W': 'Stopped by counter-clockwise limit sensor detected',
        'E': 'Stopped by both of limit sensors detected',
        'K': 'Normal stop'
    }

    MESSAGE_ACK3 = {
        'K': 'No alarm',
        'E': 'Alarm on the hardware',
        'C': 'Alarm on the communication',
    }

    MESSAGE_ACK4 = {
        'B': 'Busy',
        'R': 'Ready',
    }

    def __init__(self, code1, code2, code3, code4):
        self.message1 = self.MESSAGE_ACK1[code1]
        self.message2 = self.MESSAGE_ACK2[code2]
        self.message3 = self.MESSAGE_ACK3[code3]
        self.message4 = self.MESSAGE_ACK4[code4]

    def __str__(self):
        return "OptoSigma SBIS26 Error: %s, %s, %s, %s" % (self.message1, self.message2, self.message3, self.message4)


class Axis(Channel):
    """FIXME"""

    # position = Instrument.control()

    # speed = Instrument.control()

    # status = Instrument.measurement()

    # divider = Instrument.control()

    def move(self):
        pass

    def move_relative(self):
        pass

    def home(self):
        pass

    def stop(self):
        pass


class SBIS26(Instrument):
    """Represents the OptoSigma SBIS26 Motorized Stage."""

    def __init__(self,
                 adapter,
                 name="OptoSigma SBIS26 Motorized Stage",
                 **kwargs
                 ):
        self.termination_str = "\r\n"

        super().__init__(
            adapter,
            name,
            write_termination=self.termination_str,
            read_termination=self.termination_str,
            **kwargs
        )

    ch_1 = Instrument.ChannelCreator(Axis, 1)
    ch_2 = Instrument.ChannelCreator(Axis, 2)
    ch_3 = Instrument.ChannelCreator(Axis, 3)
