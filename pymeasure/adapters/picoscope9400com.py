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


class COMAdapter(Adapter):
    """
    Adapter for the Picosope 9400 COM (component object model)-based windows drivers that expose a method akin to a
    read, write, and query. Large portions of this adapter are adapted from  tinix84 (Riccardo Tinivella)'s
    implementation for the lecroy waverunner. The GUI must be running to register the COM object (it is a headless
    scope, afterall).

    :param COMobject: string representing the COM object to instance.
    """

    def __init__(self, COMobject=None, preprocess_reply=None, **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        """The constructor.
            initialize and configure activeX port class
        """
        self.connection = win32com.client.Dispatch(COMobject)

    def _execcommand(self, command):
        out = self.connection.ExecCommand(command)
        if out == 'Error':
            raise ValueError(f'Command {command} returned Error. Something was wrong')
        return out

    def ask(self, command):
        """ Ask the method.
        """
        out = self._execcommand(command)
        if out == '':
            raise ValueError('Nothing returned, did you forget a ?')
        return out


    def write(self, command):
        """ Writes method
        """
        returned = self._execcommand(command)
        if returned != '':
            raise ValueError(f'Write command {command} returned {returned} not empty string. This is inconsistent.')

    def read(self):
        """ Reads method
        """
        raise ValueError("Picoscope 9400 doesn't implement a read method. All asks/queries immediately return.")

    def __del__(self):
        """Close connection upon garbage collection of the device"""
        if self.connection is not None:
            del self.connection