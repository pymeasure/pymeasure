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

from unittest import mock

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments import Channel


class ChannelWithPlaceholder(Channel):
    """A test channel with a different placeholder"""

    placeholder = "fn"

    test = Channel.control("{fn}test?", "test{fn} %i", """Control test.""")


class TestChannelCommunication:
    @pytest.fixture()
    def ch(self):
        a = mock.MagicMock(return_value="5")
        return Channel(a, "A")

    def test_write(self, ch):
        ch.write("abc")
        assert ch.parent.method_calls == [mock.call.write('abc')]

    def test_read(self, ch):
        ch.read()
        assert ch.parent.method_calls == [mock.call.read()]

    def test_write_bytes(self, ch):
        ch.write_bytes(b"abc")
        assert ch.parent.method_calls == [mock.call.write_bytes(b"abc")]

    def test_read_bytes(self, ch):
        ch.read_bytes(5)
        assert ch.parent.method_calls == [mock.call.read_bytes(5)]

    def test_write_binary_values(self, ch):
        ch.write_binary_values("abc", [5, 6, 7])
        assert ch.parent.method_calls == [mock.call.write_binary_values("abc", [5, 6, 7])]


def test_channel_with_different_prefix():
    c = ChannelWithPlaceholder(None, "A")
    assert c.insert_id("id:{fn}") == "id:A"
