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

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
from pymeasure.adapters.minicircuitsusbswitch import MinicircuitsUSBSwitch

import numpy as np
import time


class Channel(object):
    """
    Represents a channel of the RC-2SP4T-26 switch from minicircuits.
    """

    @property
    def state(self):
        return self.ask('STATE?')

    @state.setter
    def state(self, cmd):
        self.write('STATE:%d' % cmd)

    def __init__(self, instrument, number, **kwargs):
        self.instrument = instrument
        self.number = number

        for key, item in kwargs.items():
            setattr(self, key, item)

    def ask(self, command):
        return self.instrument.ask("SP4T%s:%s" % (self.number, command))

    def write(self, command):
        self.instrument.write("SP4T%s:%s" % (self.number, command))


class RC_2SP4T(Instrument):
    """ Represents the RC_2SP4T_26 solid state switch and provides a high level
    interface to the SCIPI commands. Requires that the mcl_SolidStateSwitch_NET45 be in the path
    or same directory as the running code.

    """
    channels = ['A', 'B']

    def __init__(self, adapter, **kwargs):
        if isinstance(adapter, (str, int)) or adapter is None:
            adapter = MinicircuitsUSBSwitch(adapter)
        super(RC_2SP4T, self).__init__(
            adapter, "RC_2SP4T switch", **kwargs
        )

        model = ['RC-2SP4T-26', 'RC-2SP4T-A18', 'RC-2SP4T-40', 'RC-2SP4T-50']
        actual = self.adapter.connection.Read_ModelName("")[1]
        if actual not in model:
            raise ValueError(f'Got different model {actual}')

        for chan in self.channels:
            setattr(self, 'ch' + chan, Channel(self, chan))

    def disconnect(self):
        self.adapter.connection.Disconnect()

    @property
    def serial_number(self):
        """ Returns the serial number of the connected switch """
        return self.adapter.connection.Read_SN("")[1]