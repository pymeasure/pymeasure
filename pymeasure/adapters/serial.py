#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
import time
import serial
import numpy as np

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SerialAdapter(Adapter):
    """ Adapter class for using the Python Serial package to allow
    serial communication to instrument

    :param port: Serial port
    :param kwargs: Any valid key-word argument for serial.Serial
    """

    def __init__(self, port, terminator="\n", **kwargs):
        self.terminator = terminator
        if isinstance(port, serial.Serial):
            self.connection = port
        else:
            self.connection = serial.Serial(port, **kwargs)

    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        self.connection.close()
        
    def reset(self):
        """ Flush input and output buffer to prevent side effects for example
        when the user interacts locally with the device while the serial connection 
        is kept open
        """
        self.connection.reset_input_buffer()
        self.connection.reset_output_buffer()

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        command = command + self.terminator
        self.connection.write(command.encode())  # encode added for Python 3
        time.sleep(0.1) # give the device time to process the commands

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII respone

        :returns: String ASCII response of the instrument.
        """
        buff = []
        while self.connection.in_waiting > 0:
            tmp = self.connection.readline().decode() # readlines replaces with readline
            buff.append(tmp)
        if len(buff) > 1:
            return buff
        if len(buff) == 1:
            return buff[0]


    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data 

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        command = command + self.terminator
        self.connection.write(command.encode())
        binary = self.connection.read().decode()
        header, data = binary[:header_bytes], binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def __repr__(self):
        return "<SerialAdapter(port='%s')>" % self.connection.port
