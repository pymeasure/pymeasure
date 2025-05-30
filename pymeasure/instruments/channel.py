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

from .common_base import CommonBase

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Channel(CommonBase):
    """The base class for channel definitions.

    This class supports dynamic properties like :class:`Instrument`,
    but requires an :class:`Instrument` instance as a parent for communication.

    :meth:`insert_id` inserts the channel id into the command string sent to the instrument.
    The default implementation replaces the Channel's `placeholder` (default "ch")
    with the channel id in all command strings (e.g. "CHANnel{ch}:foo").

    :param parent: The instrument (an instance of :class:`~pymeasure.instruments.Instrument`)
        to which the channel belongs.
    :param id: Identifier of the channel, as it is used for the communication.
    """

    placeholder = "ch"

    def __init__(self, parent, id):
        self.parent = parent
        self.id = id
        super().__init__()

    def insert_id(self, command):
        """Insert the channel id in a command replacing `placeholder`.

        Subclass this method if you want to do something else,
        like always prepending the channel id.
        """
        return command.format_map({self.placeholder: self.id})

    # Calls to the instrument
    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param command: command string to be sent to the instrument.
            '{ch}' is replaced by the channel id.
        :param kwargs: Keyword arguments for the adapter.
        """
        self.parent.write(self.insert_id(command), **kwargs)

    def write_bytes(self, content, **kwargs):
        """Write the bytes `content` to the instrument."""
        self.parent.write_bytes(content, **kwargs)

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer."""
        return self.parent.read(**kwargs)

    def read_bytes(self, count, **kwargs):
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read the whole read buffer.
        :param kwargs: Keyword arguments for the adapter.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        return self.parent.read_bytes(count, **kwargs)

    def write_binary_values(self, command, values, *args, **kwargs):
        """Write binary values to the instrument.

        :param command: Command to send.
        :param values: The values to transmit.
        :param \\*args, \\**kwargs: Further arguments to hand to the Adapter.
        """
        self.parent.write_binary_values(self.insert_id(command),
                                        values, *args, **kwargs)

    def read_binary_values(self, **kwargs):
        """Read binary values from the instrument."""
        return self.parent.read_binary_values(**kwargs)

    def check_errors(self):
        """Read all errors from the instrument and log them.

        :return: List of error entries.
        """
        return self.parent.check_errors()

    def check_get_errors(self):
        """Check for errors after having gotten a property and log them.

        Called if :code:`check_get_errors=True` is set for that property.

        If you override this method, you may choose to raise an Exception for certain errors.

        :return: List of error entries.
        """
        return self.parent.check_get_errors()

    def check_set_errors(self):
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        If you override this method, you may choose to raise an Exception for certain errors.

        :return: List of error entries.
        """
        return self.parent.check_set_errors()

    # Communication functions
    def wait_for(self, query_delay=None):
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds. None is default delay.
        """
        self.parent.wait_for(query_delay)
