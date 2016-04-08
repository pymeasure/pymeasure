#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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

import numpy as np


class Adapter(object):
    """ Base class for Adapter child classes, which adapt between the Instrument 
    object and the connection, to allow flexible use of different connection 
    techniques.

    This class should only be inhereted from.
    """

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        raise NameError("Adapter (sub)class has not implemented writing")

    def ask(self, command):
        """ Writes the command to the instrument and returns the resulting 
        ASCII response

        :param command: SCPI command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        self.write(command)
        return self.read()

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII respone

        :returns: String ASCII response of the instrument.
        """
        raise NameError("Adapter (sub)class has not implemented reading")

    def values(self, command):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result 

        :param command: SCPI command to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        raise NameError("Adapter (sub)class has not implemented the "
                        "values method")

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data 

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        raise NameError("Adapter (sub)class has not implemented the "
                        "binary_values method")


class FakeAdapter(Adapter):
    """The Fake adapter class is provided for debugging purposes,
    which returns valid data for each Adapter method"""

    def read(self):
        """ Returns a fake string for debugging purposes
        """
        return "Fake string!"

    def write(self, command):
        """ Fakes the writing of a command for debugging purposes
        """
        pass

    def values(self, command):
        """ Returns a list of fake values for debugging purposes
        """
        return [1.0, 2.0, 3.0]

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a list of fake values in a NumPy array
        """
        return np.array([2, 3, 7, 8, 1], dtype=dtype)

    def __repr__(self):
        return "<FakeAdapter>"
