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
from warnings import warn

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import vxi11
except ImportError:
    log.warning('Failed to import vxi11 package, which is required for the VXI11Adapter')


class VXI11Adapter(Adapter):
    """ VXI11 Adapter class. Provides a adapter object that
        wraps around the read, write and ask functionality
        of the vxi11 library.

    .. deprecated:: 0.11
        Use VISAAdapter instead.

    :param host: string containing the visa connection information.
    :param preprocess_reply: (deprecated) optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.
    """

    def __init__(self, host, preprocess_reply=None, **kwargs):
        super().__init__(preprocess_reply=preprocess_reply,
                         query_delay=kwargs.pop('query_delay', 0))
        warn("Deprecated, use VISAAdapter instead.", FutureWarning)
        # Filter valid arguments that can be passed to vxi instrument
        valid_args = ["name", "client_id", "term_char"]
        self.conn_kwargs = {}
        for key in kwargs:
            if key in valid_args:
                self.conn_kwargs[key] = kwargs[key]

        self.connection = vxi11.Instrument(host, **self.conn_kwargs)

    def _write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param str command: Command string to be sent to the instrument
            (without termination).
        :param kwargs: Keyword arguments for the connection itself.
        """
        self.connection.write(command)

    def _read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer.

        :param kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument (excluding read_termination).
        """
        return self.connection.read()

    def ask(self, command):
        """ Wrapper function for the ask command using the
        vx11 interface.

        .. deprecated:: 0.11
           Call `Instrument.ask` instead.

        :param command: string with the command that will be transmitted
                        to the instrument.

        :returns string containing a response from the device.
        """
        warn("Do not call `Adapter.ask`, but `Instrument.ask` instead.",
             FutureWarning)
        return self.connection.ask(command)

    def write_raw(self, command):
        """Write bytes to the device.

        .. deprecated:: 0.11
            Use `write_bytes` instead.
        """
        warn("Use `write_bytes` instead.", FutureWarning)
        self.write_bytes(command)

    def _write_bytes(self, command, **kwargs):
        """Write the bytes `content` to the instrument.

        :param bytes content: The bytes to write to the instrument.
        :param kwargs: Keyword arguments for the connection itself.

        .. note::
            vx11 adds the term_char even for writing_bytes.
        """
        # Note: vxi11.write_raw adds the term_char!
        self.connection.write_raw(command, **kwargs)

    def read_raw(self):
        """Read bytes from the device.

        .. deprecated:: 0.11
            Use `read_bytes` instead.
        """
        warn("Use `read_bytes` instead.", FutureWarning)
        return self.read_bytes(-1)

    def _read_bytes(self, count, break_on_termchar=False, **kwargs):
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read the whole read buffer.
        :param bool break_on_termchar: Stop reading at a termination character.
        :param kwargs: Keyword arguments for the connection itself.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        if self.connection.term_char and not break_on_termchar:
            read_termination = self.connection.term_char
            self.connection.term_char = None
            try:
                return self.connection.read_raw(count, **kwargs)
            finally:
                self.connection.term_char = read_termination
        else:
            return self.connection.read_raw(count, **kwargs)

    def ask_raw(self, command):
        """ Wrapper function for the ask_raw command using the
        vx11 interface.

        .. deprecated:: 0.11
            Use `Instrument.write_bytes` and `Instrument.read_bytes` instead.

        :param command: binary string with the command that will be
                        transmitted to the instrument

        :returns binary string containing the response from the device.
        """
        warn("Use `Instrument.write_bytes` and `Instrument.read_bytes` instead.",
             FutureWarning)
        return self.connection.ask_raw(command)

    def __repr__(self):
        return f'<VXI11Adapter(host={self.connection.host})>'
