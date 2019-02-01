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

import win32com.client  # imports the pywin32 library

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

DEFAULT_BUFFER_SIZE = 1000


class ActiveDSOAdapter(Adapter):
    """
    Adapter for LeCroy scope implementations, it use and activeX layers for Visa communication
    Only TCP implemented for the moment, ActiveX can be extended to GPIB

    :param address: IP address
    :param rw_delay: read/write delay
    """

    def __init__(self, address=None, rw_delay=None):
        """The constructor.
            initialize and configure activeX port class
        """
        self.connection = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")  # Load ActiveDSO control
        self.address = address
        if rw_delay:
            self.rw_delay = rw_delay
        else:
            self.rw_delay = 0.1

    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        self.connection.Disconnect()

    def __repr__(self):
        if self.address is not None:
            return "<ActiveXLeCroyAdapter(address=%d)>" % (self.address)
        else:
            return False

    def connect(self):
        if self.address:
            self.connection.MakeConnection("IP:" + self.address)  # open the stream
        else:
            return False

    def disconnect(self):
        if self.address:
            self.connection.Disconnect()  # close the stream
        else:
            return False

    def ask(self, command):
        """ Ask the method.
        """
        self.write(command)
        if self.rw_delay is not None:
            time.sleep(self.rw_delay)
        return self.read()

    def write(self, command):
        """ Writes method
        """
        if self.address is not None:
            self.connection.WriteString(command, 1)

    def read(self):
        """ Reads method
        """
        if self.address is not None:
            stream = self.connection.ReadString(DEFAULT_BUFFER_SIZE)
        return stream

    def aboutbox(self):
        """ The AboutBox method displays a dialog showing the ActiveDSO version number..
        """
        self.connection.AboutBox()
        return True
