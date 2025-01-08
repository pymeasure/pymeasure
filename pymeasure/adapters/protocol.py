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
from unittest.mock import MagicMock
from warnings import warn

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def to_bytes(command):
    """Change `command` to a bytes object"""
    if isinstance(command, (bytes, bytearray)):
        return command
    elif command is None:
        return None
    elif isinstance(command, str):
        return command.encode("utf-8")
    elif isinstance(command, (list, tuple)):
        return bytes(command)
    elif isinstance(command, (int, float)):
        return str(command).encode("utf-8")
    raise TypeError(f"Invalid input of type {type(command).__name__}.")


class ProtocolAdapter(Adapter):
    """ Adapter class for testing the command exchange protocol without instrument hardware.

    This adapter is primarily meant for use within :func:`pymeasure.test.expected_protocol()`.

    The :attr:`connection` attribute is a :class:`unittest.mock.MagicMock` such
    that every call returns. If you want to set a return value, you can use
    :code:`adapter.connection.some_method.return_value = 7`,
    such that a call to :code:`adapter.connection.some_method()` will return `7`.
    Similarly, you can verify that this call to the connection method happened
    with :code:`assert adapter.connection.some_method.called is True`.
    You can specify dictionaries with return values of attributes and methods.

    :param list comm_pairs: List of "reference" message pair tuples. The first element is
        what is sent to the instrument, the second one is the returned message.
        'None' indicates that a pair member (write or read) does not exist.
        The messages do **not** include the termination characters.
    :param connection_attributes: Dictionary of connection attributes and their values.
    :param connection_methods: Dictionary of method names of the connection and their return values.
    """

    def __init__(self, comm_pairs=None, preprocess_reply=None,
                 connection_attributes=None,
                 connection_methods=None,
                 **kwargs):
        """Generate the adapter and initialize internal buffers."""
        super().__init__(preprocess_reply=preprocess_reply, **kwargs)
        # Setup communication
        if comm_pairs is None:
            comm_pairs = []
        assert isinstance(comm_pairs, (list, tuple)), (
            "Parameter comm_pairs has to be a list or tuple.")
        for pair in comm_pairs:
            if len(pair) != 2:
                raise ValueError(f'Comm_pairs element {pair} does not have two elements!')
        self._read_buffer = None
        self._write_buffer = None
        self.comm_pairs = comm_pairs
        self._index = 0
        # Setup attributes
        self._setup_connection(connection_attributes, connection_methods)

    def _setup_connection(self, connection_attributes, connection_methods):
        self.connection = MagicMock()
        if connection_attributes is not None:
            for key, value in connection_attributes.items():
                setattr(self.connection, key, value)
        if connection_methods is not None:
            for key, value in connection_methods.items():
                getattr(self.connection, key).return_value = value

    def _write(self, command, **kwargs):
        """Compare the command with the expected one and fill the read."""
        self._write_bytes(to_bytes(command))
        assert self._write_buffer is None, (
            f"Written bytes '{self._write_buffer}' do not match expected "
            f"'{self.comm_pairs[self._index][0]}'.")

    def _write_bytes(self, content, **kwargs):
        """Write the bytes `content`. If a command is full, fill the read."""
        if self._write_buffer is None:
            self._write_buffer = content
        else:
            self._write_buffer += content
        try:
            p_write, p_read = self.comm_pairs[self._index]
        except IndexError:
            raise ValueError(f"No communication pair left to write {content}.")
        if self._write_buffer == to_bytes(p_write):
            assert self._read_buffer is None, (
                f"Unread response '{self._read_buffer}' present when writing. "
                "Maybe a property's 'check_set_errors' is not accounted for, "
                "a read() call is missing in a method, or the defined protocol is incorrect?"
            )
            # Clear the write buffer
            self._write_buffer = None
            self._read_buffer = to_bytes(p_read)
            self._index += 1
        # If _write_buffer does _not_ agree with p_write, this is not cause for
        # concern, because you can in principle compose a message over several writes.
        # It's not clear how relevant this is in real-world use, but it's analogous
        # to the possibility to fetch a (binary) message over several reads.

    def _read(self, **kwargs):
        """Return an already present or freshly fetched read buffer as a string."""
        return self._read_bytes(-1).decode("utf-8")

    def _read_bytes(self, count, break_on_termchar=False, **kwargs):
        """Read `count` number of bytes from the buffer.

        :param int count: Number of bytes to read. If -1, return the buffer.
        """
        if break_on_termchar:
            warn(("Breaking on termination character in `read_bytes` cannot be tested. "
                  "You have to separate the message parts in the com_pairs."),
                 UserWarning)
        if self._read_buffer is not None:
            if count == -1 or count >= len(self._read_buffer):
                read = self._read_buffer
                self._read_buffer = None
            else:
                read = self._read_buffer[:count]
                self._read_buffer = self._read_buffer[count:]
            return read
        else:
            try:
                p_write, p_read = self.comm_pairs[self._index]
            except IndexError:
                raise ValueError("No communication pair left for reading.")
            assert p_write is None, (
                f"Written {self._write_buffer} do not match expected {p_write} prior to read."
                if self._write_buffer
                else "Unexpected read without prior write.")
            assert p_read is not None, "Communication pair cannot be (None, None)."
            self._index += 1
            p_read = to_bytes(p_read)
            if count == -1 or count >= len(p_read):
                # _read_buffer is already empty, no action required.
                return p_read
            else:
                self._read_buffer = p_read[count:]
                return p_read[:count]

    def flush_read_buffer(self):
        """ Flush and discard the input buffer

        As detailed by pyvisa, discard the read buffer contents and if data was present
        in the read buffer and no END-indicator was present, read from the device until
        encountering an END indicator (which causes loss of data).
        """
        self.connection.flush("pyvisa.constants.BufferOperation.discard_read_buffer")
