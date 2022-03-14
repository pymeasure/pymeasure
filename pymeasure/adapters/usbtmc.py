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

import logging

import usbtmc
import numpy as np
from pkg_resources import parse_version

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class USBTMCAdapter(Adapter):
    """ Adapter class for the python-usbtmc library to allow communication to instruments.
    
    :param resource_name: A
        `python-usbtmc (visa-like) resource string <https://alexforencich.com/wiki/en/python-usbtmc/readme>`__
        that identifies the target of the connection. The alternative way offered by python-usbtmc
        to identify the target with idVendor, idProduct, and Serial Number given as separate arguments
        is currently not supported in this implementation.
    :param preprocess_reply: optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.
    :param kwargs: Valid keyword arguments for usbtmc.Instrument class. See the `python-usbtmc documentation <https://alexforencich.com/wiki/en/python-usbtmc/start>`__
    """

    def __init__(self, resource_name, preprocess_reply=None, **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        if not USBTMCAdapter.has_supported_version():
            raise NotImplementedError("Please upgrade python-usbtmc to version 0.8 or later.")

        self.resource_name = resource_name
        self.connection = usbtmc.Instrument(resource_name, **kwargs)

    @staticmethod
    def has_supported_version():
        """ Returns True if the python-usbtmc version is greater than 0.8 """
        if hasattr(usbtmc, '__version__'):
            return parse_version(usbtmc.__version__) >= parse_version('0.8')
        else:
            return False

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        self.connection.write(command)

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII response

        :returns: String ASCII response of the instrument.
        """
        return self.connection.read()

    def ask(self, command):
        """ Writes the command to the instrument and returns the resulting
        ASCII response

        :param command: SCPI command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        return self.connection.ask(command)

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        self.connection.write(command)
        binary = self.connection.read_raw()
        # header = binary[:header_bytes]
        data = binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def __repr__(self):
        return "<USBTMCAdapter(resource='%s')>" % self.connection.resource_name
