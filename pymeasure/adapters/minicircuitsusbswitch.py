#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
import logging
import clr
import os

try:
    clr.AddReference('mcl_SolidStateSwitch_NET45')
    from mcl_SolidStateSwitch_NET45 import USB_Digital_Switch
except:
    print("import failed of mcl_SolidStateSwitch_NET45 DLL, can't find mcl DLL?")
    print(os.listdir())


from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

DEFAULT_BUFFER_SIZE = 1000


class MinicircuitsUSBSwitch(Adapter):
    """
    Adapter for the minicircuits net45 dll switch matrix interface. Requires pythonnet to be installed and only works on windows.

    :param SN: string or integer representation of the device serial number, if given.
    """

    def __init__(self, SN=None, preprocess_reply=None, **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        """The constructor.
            initialize and configure dll class
        """
        self.connection = USB_Digital_Switch()
        ret = 0
        if SN is not None:
            if isinstance(SN, str):
                ret = self.connection.Connect(SN)
            elif isinstance(SN, int):
                ret = self.connection.ConnectByAddress(SN)
            else:
                raise TypeError(f'got type {type(SN)} which is not allowed')
        else:
            ret = self.connection.Connect()
        if ret == 0:
            raise ValueError('Failed to connect')

    def ask(self, query):
        status = self.connection.Send_SCPI(query, "")
        if status[0] == 1:
            return str(status[-1])
        else:
            raise ValueError('Query was not successful, got 0 status')

    def write(self, cmd):
        status = self.connection.Send_SCPI(cmd, "")
        if status == 0:
            raise ValueError('Command was not successful, got 0 status')


    def __del__(self):
        """Close connection upon garbage collection of the device"""
        try:
            self.connection.Disconnect()
        except TypeError:
            print('Ctrl + C can mess with the Disconnect function, switch ungracely disconnected')
            