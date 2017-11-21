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
    """
    Adapter class for using the PySerial package to allow serial communication
    to an instrument.

    ``read_term`` changes the behaviour of :meth:`read` and :meth:`ask`. If it
    is not specified, the legacy behaviour is retained, where these methods will
    wait until a timeout occurs to return the data collected so far; in this
    case, setting the ``timeout`` parameter is important!

    If it is specified, :meth:`read` and :meth:`ask` will return data up to the
    first time the termination character is found. See :meth:`.read` for
    remarks and warnings on this behaviour.

    :param port: Serial port name (str), or serial.Serial object.
    :param str|None write_term: Command termination string. This string is
        appended to all commands passed to the interface via :meth:`write` or
        :meth:`ask`.
    :param str|bytes|bytearray|None read_term: Terminator for a response
        from the device, as a byte-like. Default is ``None`` for backwards
        compatibility.
    :param kwargs: Any valid keyword argument for serial.Serial.
    """

    def __init__(self, port, write_term=None, read_term=None,
            **kwargs):
        if isinstance(port, serial.Serial):
            self.connection = port
        else:
            self.connection = serial.Serial(port, **kwargs)
        
        self.write_term = write_term
        self.read_term = read_term


    @property
    def write_term(self):
        """
        Same as the constructor :attr:`write_term` parameter. Property can be
        read and written. Always returns a ``str`` or ``None`` when read.
        """
        return self._write_term


    @write_term.setter
    def write_term(self, value):
        if value is None:
            self._write_term = None
        else:
            try: # if bytes, decode
                self._write_term = value.decode('ascii')
            except AttributeError: # anything else
                self._write_term = str(value)


    @property
    def read_term(self):
        """
        Same as the constructor :attr:`read_term` parameter. Property can be
        read and written. Always returns a ``bytes`` or ``None`` when read.
        """
        return self._read_term


    @read_term.setter
    def read_term(self, value):
        if value is None:
            self._read_term = None
        else:
            try:
                value.decode # test if already bytes/bytearray
                self._read_term = bytes(value)
            except AttributeError:
                self._read_term = str(value).encode('ascii')


    def __del__(self):
        """
        Ensures the connection is closed upon deletion
        """
        try:
            self.connection.close()
        except (AttributeError, NameError):
            pass # self.connection doesn't exist/is None (e.g. connection err)

    def write(self, command):
        """
        Writes a command to the instrument.

        :param command: SCPI command string to be sent to the instrument
        """
        if self.write_term:
            command += self.write_term
        self.connection.write(command.encode('ascii'))  # encode added for Python 3

    def read(self):
        """
        Reads until the buffer is empty and returns the resulting ASCII response.

        If a termination character ``read_term`` is specified, read up to the
        terminator (or until timeout) instead. This may be faster if a high
        rate of commands is needed (avoids waiting a full timeout period),
        but this violates the :meth:`Adapter.read` contract that states the
        entire buffer is returned: some instruments may not work, in particular
        if they pool several commands and then bulk read the result.

        :returns: Response from the instrument, as a string interpreted as ASCII
        """
        if not self.read_term:
            return b"\n".join(self.connection.readlines()).decode()
        else:
            data = bytearray()
            current = self.connection.read(1)
            # while a character has been read (i.e. not timeout)
            while current:
                if current == self.read_term:
                    # if we have data, stop read, else discard and wait for data
                    if len(data) > 0:
                        break
                else:
                    data.extend(current)
                current = self.connection.read(1)
            else:
                log.warn("Timed out reading data, no terminator received.")
            return data.decode()

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
