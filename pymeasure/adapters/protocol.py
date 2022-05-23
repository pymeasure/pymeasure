#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from .adapter import Adapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def to_bytes(command):
    """Change `command` to a bytes object"""
    if isinstance(command, (bytes, bytearray)):
        return command
    elif command is None:
        return b""
    elif isinstance(command, str):
        return command.encode("utf-8")
    elif isinstance(command, (list, tuple)):
        try:
            return bytes(command)
        except TypeError:
            raise
    elif isinstance(command, int):
        return bytes((command,))
    raise TypeError("Invalid input")


class ProtocolAdapter(Adapter):
    """ Adapter class testing command exchange without instrument hardware.

    :param kwargs: TBD key-word arguments
    """

    def __init__(self, comm_pairs, preprocess_reply=None, **kwargs):
        super().__init__(preprocess_reply=preprocess_reply)
        self.read_buffer = b""
        self.write_buffer = b""
        self.comm_pairs = comm_pairs
        self.index = 0
        # TODO: Make this skeleton implementation workable

    def write(self, command):
        """Compare the command with the expected one and fill the buffer."""
        pair = self.comm_pairs[self.index]
        self.index += 1
        assert to_bytes(pair[0]) == to_bytes(command), (
                f"Command '{command}' written, but {pair[0]} expected.")
        print(pair)
        try:
            self.read_buffer = to_bytes(pair[1])
        except IndexError:
            # No response in the pair.
            self.read_buffer = b""

    def write_bytes(self, content):
        """Write the bytes `content`. If a command is full, fill the read."""
        self.write_buffer += content
        pair = self.comm_pairs[self.index]
        if self.write_buffer == pair[0]:
            assert self.read_buffer == b"", "Responses have not been read yet."
            # Clear the write buffer
            self.write_buffer = b""
            self.index += 1
            try:
                self.read_buffer = pair[1]
            except IndexError:
                self.read_buffer = b""

    def read(self):
        """Read the prepared read bufferr and return it as a string."""
        if self.read_buffer:
            return self.read_buffer.decode("utf-8")
        else:
            pair = self.comm_pairs[self.index]
            assert pair[0] is None, "Unexpected read without prior write."
            self.index += 1
            return to_bytes(pair[1]).decode("utf-8")

    def read_bytes(self, count):
        """Read `count` number of bytes."""
        if self.read_buffer:
            read = self.read_buffer[:count]
            self.read_buffer = self.read_buffer[count:]
            return read
        else:
            pair = self.comm_pairs[self.index]
            assert pair[0] is None, "Unexpected read without prior write."
            self.index += 1
            read = pair[1][:count]
            self.read_buffer = pair[1][count:]
            return read

    # TODO: Harmonise ask being write+read (i.e., remove from VISAAdapter),
    #   use protocol tests to confirm it works correctly
    # TODO: Remove all now-unnecessary ask() implementations -
    #   read and write implementations should have all (test this)
    # TODO: Implement over-the-wire message-traffic logging here, first
    # TODO: Check timing impact of non-firing logging messages
    # TODO: Roll out message-traffic logging to all Adapters, try to DRY
