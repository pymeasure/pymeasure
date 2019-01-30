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

import logging

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

    def __init__(self, port, **kwargs):
        if isinstance(port, serial.Serial):
            self.connection = port
        else:
            self.connection = serial.Serial(port, **kwargs)

    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        self.connection.close()

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        self.connection.write(command.encode())  # encode added for Python 3

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII respone

        :returns: String ASCII response of the instrument.
        """
        return b"\n".join(self.connection.readlines()).decode()

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data 

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        self.connection.write(command.encode())
        binary = self.connection.read().decode()
        header, data = binary[:header_bytes], binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def __repr__(self):
        return "<SerialAdapter(port='%s')>" % self.connection.port


class ActiveXLeCroyAdapter():
"""
Only TCP implemntend for the moment, ActiveX can be extended to GPIB
"""
    def __init__(self, protocol = "TCPIP", address = None, port = None,
                 timeout = DEFAULT_TIMEOUT):
        """The constructor.
            initialize and configure activeX port class
        """
        self.protocol = protocol
        self.address = address
        self.port = port
        self.timeout = timeout
        # Load ActiveDSO control
        self.tty = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")
        self.set_timeout(timeout)
    def about_port(self):
        """ Present the ActiveX control's About box"""
        self.tty.AboutBox()
    def is_open(self):
        """Documentation for a method."""
        print(debug_msg.TBD_MSG)
    def get_address(self):
        """Documentation for a method."""
        return self.address
    def get_timeout(self):
        """Documentation for a method."""
        return self.timeout
    def set_timeout(self, timeout):
        """Documentation for a method."""
        print(timeout)
        print(debug_msg.TBD_MSG)
    def open_stream(self):
        """Substitute your choice of IP address here"""
        self.tty.MakeConnection("IP:"+self.address)
    def close_stream(self):
        """Documentation for a method."""
        self.tty.Disconnect()
    def set_timeout_ms(self, timeout):
        """Documentation for a method."""
        print(timeout)
        print(debug_msg.TBD_MSG)
    def read_block(self, block_size):
        """Documentation for a method."""
        stream = self.tty.ReadString(block_size)
        return stream
    def write_string(self, stream):
        """Documentation for a method."""
        self.tty.WriteString(stream, 1)
        time.sleep(DEFAULT_WAIT_TIME)
    def query(self, cmd, read_buffer_size = DEFAULT_BUFFER_SIZE):
        """Documentation for a method."""
        self.write_string(cmd)
        return self.read_block(read_buffer_size)