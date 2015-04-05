"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import numpy as np


class Adapter(object):
    """ Adapts between the Instrument object and the connection, to allow
    flexible use of different connection methods
    """

    def write(self, command):
        """ Writes a command """
        raise NameError("Adapter (sub)class has not implemented writing")

    def ask(self, command):
        """ Writes the command and returns the read result """
        self.write(command)
        return self.read()

    def read(self):
        """ Reads until the buffer is empty and returns the result """
        raise NameError("Adapter (sub)class has not implemented reading")

    def values(self, command):
        """ Returns a list of values from the string read """
        raise NameError("Adapter (sub)class has not implemented the "
                        "values method")

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data """
        raise NameError("Adapter (sub)class has not implemented the "
                        "binary_values method")


class FakeAdapter(Adapter):
    """Fake adapter for debugging purposes"""

    def read(self):
        return "Fake string!"

    def write(self, command):
        pass

    def values(self, command):
        return [1.0, 2.0, 3.0]

    def binary_values(self, command):
        return np.array([2, 3, 7, 8, 1])

    def __repr__(self):
        return "<FakeAdapter>"
