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
try:
    import clr
except RuntimeError:
    print('unable to load clr, install it with pythonnet or get on a windows machine')
try:
    clr.AddReference('mcl_SolidStateSwitch_NET45')
    from mcl_SolidStateSwitch_NET45 import USB_Digital_Switch
except:
    pass
import numpy as np
import time


class USB_2SP2T_DCH():
    """ Represents the USB-2SP2T-DCH solid state switch and provides a high level
    interface to the SCIPI commands. Requires that the mcl_SolidStateSwitch_NET45 be in the path
    or same directory as the running code.

    """

    def __init__(self, SN = None):
        self.connection = USB_Digital_Switch()
        if SN is not None:
            if isinstance(SN,str):
                self.connection.Connect(SN)
            elif isinstance(SN,int):
                self.connection.ConnectByAddress(SN)
            else:
                raise TypeError(f'got type {type(SN)} which is not allowed')
        else:
            self.connection.Connect()
        model = 'USB-2SP2T-DCH'
        actual = self.connection.Read_ModelName("")[1]
        if actual != model:
            raise ValueError(f'Got different model {actual}')

    def disconnect(self):
        self.connection.Disconnect()

    def ask(self, query):
        status = self.connection.Send_SCPI(query, "")
        if status[0] == 1:
            return str(status[-1])
        else:
            raise ValueError('Query was not successful, got 0 status')

    @property
    def serial_number(self):
        """ Returns the serial number of the connected switch """
        return self.connection.Read_SN("")[1]

    @property
    def CH_A_state(self):
        """ Returns the serial number of the connected switch """
        return int(self.ask(":SP2T:A:STATE?"))

    @CH_A_state.setter
    def CH_A_state(self,value):
        if value not in [1,2]:
            raise ValueError(f'Can only set state to 1 or 2, not {value}')
        else:
            self.ask(f":SP2T:A:STATE:{value}")

    @property
    def CH_B_state(self):
        """ Returns the serial number of the connected switch """
        return int(self.ask(":SP2T:B:STATE?"))

    @CH_B_state.setter
    def CH_B_state(self,value):
        if value not in [1,2]:
            raise ValueError(f'Can only set state to 1 or 2, not {value}')
        else:
            self.ask(f":SP2T:B:STATE:{value}")
