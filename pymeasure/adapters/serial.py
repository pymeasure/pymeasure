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

from adapter import Adapter

import serial
import numpy as np


class SerialAdapter(Adapter):
    """ Wrapper class for the Python Serial package to treat it as an
    adapter
    """

    def __init__(self, port, **kwargs):
        self.connection = serial.Serial(port, **kwargs)

    def __del__(self):
        self.connection.close()

    def write(self, command):
        self.connection.write(command)

    def read(self):
        return "\n".join(self.connection.readlines())

    def values(self, command):
        result = self.ask(command)
        try:
            return [float(x) for x in result.split(",")]
        except:
            return result.strip()

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        self.connection.write(command)
        binary = self.connection.read()
        header, data = binary[:header_bytes], binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def __repr__(self):
        return "<SerialAdapter(port='%s')>" % self.connection.port
