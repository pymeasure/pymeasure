#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

import numpy as np
from copy import copy
from pyvisa.util import to_ieee_block, to_hp_block, to_binary_block


class Adapter:
    """ Base class for Adapter child classes, which adapt between the Instrument
    object and the connection, to allow flexible use of different connection
    techniques.

    This class should only be inherited from.

    :param log: Parent logger of the 'Adapter' logger.
    :param \\**kwargs: Keyword arguments just to be cooperative.
    """

    def __init__(self, log=None, **kwargs):
        super().__init__(**kwargs)
        self.connection = None
        if log is None:
            self.log = logging.getLogger("Adapter")
        else:
            self.log = log.getChild("Adapter")
        self.log.addHandler(logging.NullHandler())

    def __del__(self):
        """Close connection upon garbage collection of the device."""
        self.close()

    def close(self):
        """Close the connection."""
        if self.connection is not None:
            self.connection.close()

    # Directly called methods, which ensure proper logging of the communication
    # without the termination characters added by the particular adapters.
    # DO NOT OVERRIDE IN SUBCLASS!
    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        Do not override in a subclass!

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param \\**kwargs: Keyword arguments for the connection itself.
        """
        self.log.debug("WRITE:%s", command)
        self._write(command, **kwargs)

    def write_bytes(self, content, **kwargs):
        """Write the bytes `content` to the instrument.

        Do not override in a subclass!

        :param bytes content: The bytes to write to the instrument.
        :param \\**kwargs: Keyword arguments for the connection itself.
        """
        self.log.debug("WRITE:%s", content)
        self._write_bytes(content, **kwargs)

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        Do not override in a subclass!

        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        read = self._read(**kwargs)
        self.log.debug("READ:%s", read)
        return read

    def read_bytes(self, count=-1, break_on_termchar=False, **kwargs):
        """Read a certain number of bytes from the instrument.

        Do not override in a subclass!

        :param int count: Number of bytes to read. A value of -1 indicates to
            read from the whole read buffer.
        :param bool break_on_termchar: Stop reading at a termination character.
        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        read = self._read_bytes(count, break_on_termchar, **kwargs)
        self.log.debug("READ:%s", read)
        return read

    # Methods to implement in the subclasses.
    def _write(self, command, **kwargs):
        """Write string to the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented writing.")

    def _write_bytes(self, content, **kwargs):
        """Write bytes to the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented writing bytes.")

    def _read(self, **kwargs):
        """Read string from the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented reading.")

    def _read_bytes(self, count, break_on_termchar, **kwargs):
        """Read bytes from the instrument. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented reading bytes.")

    def flush_read_buffer(self):
        """Flush and discard the input buffer. Implement in subclass."""
        raise NotImplementedError("Adapter class has not implemented input flush.")

    # Binary format methods
    def read_binary_values(self, header_bytes=0, termination_bytes=None,
                           dtype=np.float32, sep="", **kwargs):
        """ Returns a numpy array from a query for binary data

        :param int header_bytes: Number of bytes to ignore in header.
        :param int termination_bytes: Number of bytes to strip at end of message or None.
        :param dtype: The NumPy data type to format the values with.
        :param string sep: Separator between chars. If given, use fromstring, otherwise frombytes.
        :param \\**kwargs: Further arguments for the NumPy fromstring / frombytes method.
        :returns: NumPy array of values
        :raises ValueError: if the data buffer is empty or malformed
        """
        binary = self.read_bytes(-1)
        # header = binary[:header_bytes]
        data = binary[header_bytes:termination_bytes]
        if sep == "":
            return np.frombuffer(data, dtype=dtype, **kwargs)
        else:
            return np.fromstring(data, dtype=dtype, sep=sep, **kwargs)

    def _format_binary_values(self, values, datatype='f', is_big_endian=False, header_fmt="ieee"):
        """Format values in binary format, used internally in :meth:`Adapter.write_binary_values`.

        :param values: data to be written to the device.
        :param datatype: the format string for a single element. See struct module.
        :param is_big_endian: boolean indicating endianness.
        :param header_fmt: Format of the header prefixing the data ("ieee", "hp", "empty").
        :return: binary string.
        :rtype: bytes
        """
        if header_fmt == "ieee":
            block = to_ieee_block(values, datatype, is_big_endian)
        elif header_fmt == "hp":
            block = to_hp_block(values, datatype, is_big_endian)
        elif header_fmt == "empty":
            block = to_binary_block(values, b"", datatype, is_big_endian)
        else:
            raise ValueError("Unsupported header_fmt: %s" % header_fmt)
        return block

    def write_binary_values(self, command, values, termination="", **kwargs):
        """ Write binary data to the instrument, e.g. waveform for signal generators

        :param command: command string to be sent to the instrument
        :param values: iterable representing the binary values
        :param termination: String added afterwards to terminate the message.
        :param \\**kwargs: Key-word arguments to pass onto :meth:`Adapter._format_binary_values`
        :returns: number of bytes written
        """
        block = self._format_binary_values(values, **kwargs)
        return self.write_bytes(command.encode() + block + termination.encode())


class FakeAdapter(Adapter):
    """Provides a fake adapter for debugging purposes,
    which bounces back the command so that arbitrary values
    testing is possible.

    .. code-block:: python

        a = FakeAdapter()
        assert a.read() == ""
        a.write("5")
        assert a.read() == "5"
        assert a.read() == ""
        assert a.ask("10") == "10"
        assert a.values("10") == [10]

    """

    _buffer = ""

    def _read(self):
        """ Return the last commands given after the
        last read call.
        """
        result = copy(self._buffer)
        # Reset the buffer
        self._buffer = ""
        return result

    def _read_bytes(self, count, break_on_termchar):
        """ Return the last commands given after the
        last read call.
        """
        result = copy(self._buffer)
        # Reset the buffer
        self._buffer = ""
        return result[:count].encode()

    def _write(self, command):
        """ Write the command to a buffer, so that it can
        be read back.
        """
        self._buffer += command

    def _write_bytes(self, command):
        """ Write the command to a buffer, so that it can
        be read back.
        """
        self._buffer += command.decode()

    def __repr__(self):
        return "<FakeAdapter>"
