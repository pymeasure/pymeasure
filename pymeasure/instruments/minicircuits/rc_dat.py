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
from pymeasure.adapters.minicircuitsusbattentuator import MinicircuitsUSBAttentuator

import numpy as np
import time


class RC_DAT(Instrument):
    """ Represents the RC_DAT programmable attenuator and provides a high level
    interface to the SCPI commands. Requires that the mcl_RUDAT_NET45 be in the path
    or same directory as the running code. You may need to unblock the dll by right clicking
    and opening the properties.

    """

    def __init__(self, adapter, **kwargs):
        if isinstance(adapter, (str, int)) or adapter is None:
            adapter = MinicircuitsUSBAttentuator(adapter)
        super(RC_DAT, self).__init__(
            adapter, "RC_DAT switch", **kwargs
        )

        model = ['RCDAT-18G-63',]
        actual = self.adapter.connection.Read_ModelName("")[1]
        if actual not in model:
            raise ValueError(f'Got different model {actual}')

    def disconnect(self):
        self.adapter.connection.Disconnect()

    @property
    def serial_number(self):
        """ Returns the serial number of the connected switch """
        return self.adapter.connection.Read_SN("")[1]

    @property
    def attenuation(self):
        return float(self.adapter.connection.Send_SCPI(':ATT?',"")[1])

    @attenuation.setter
    def attenuation(self, val):
        self.adapter.connection.Send_SCPI(':SETATT=%.2E' % val,"")