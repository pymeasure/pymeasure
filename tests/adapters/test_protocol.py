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

from unittest.mock import call
import pytest

from pymeasure.adapters.protocol import to_bytes, ProtocolAdapter

from pytest import mark, raises, fixture, warns


@pytest.fixture
def adapter():
    return ProtocolAdapter()


@mark.parametrize("input, output", (("superXY", b"superXY"),
                                    ([1, 2, 3, 4], b"\x01\x02\x03\x04"),
                                    (5, b"5"),
                                    (4.6, b"4.6"),
                                    (None, None),
                                    ))
def test_to_bytes(input, output):
    assert to_bytes(input) == output


def test_to_bytes_invalid():
    with raises(TypeError):
        to_bytes(5.5j)


def test_protocol_instantiation():
    a = ProtocolAdapter([("write", "read"), ("write_only", None)])
    assert a.comm_pairs == [("write", "read"), ("write_only", None)]


@pytest.fixture
def mockAdapter():
    adapter = ProtocolAdapter(connection_attributes={'timeout': 100},
                              connection_methods={'stb': 17})
    return adapter


def test_connection_call(mockAdapter):
    """Test whether a call to the connection is registered."""
    mockAdapter.connection.clear(7)
    assert mockAdapter.connection.clear.call_args_list == [call(7)]


def test_connection_attribute(mockAdapter):
    assert mockAdapter.connection.timeout == 100


def test_connection_method(mockAdapter):
    assert mockAdapter.connection.stb() == 17


class Test_write:
    def test_write(self):
        a = ProtocolAdapter([("written 5", 5)])
        a.write("written 5")
        assert a._read_buffer == b"5"

    def test_write_without_response(self):
        a = ProtocolAdapter([("Hey ho", None)])
        a.write("Hey ho")
        assert a._read_buffer is None

    def test_wrong_command(self):
        a = ProtocolAdapter([("Hey ho", None)])
        with raises(AssertionError, match="do not match"):
            a.write("Something different")


class Test_write_bytes:
    @fixture(scope="class", params=[1, 2])
    def written(self, request):
        """Write in a single turn."""
        a = ProtocolAdapter([("written", 5)])
        if request.param == 1:
            a.write_bytes(b"written")
        else:
            a.write_bytes(b"writ")
            a.write_bytes(b"ten")
        return a

    def test_write_write_buffer(self, written):
        assert written._write_buffer is None

    def test_write_index(self, written):
        assert written._index == 1

    def test_write_read_buffer(self, written):
        assert written._read_buffer == b"5"

    def test_partial_write(self):
        a = ProtocolAdapter([("written", 5)])
        a.write_bytes(b"writ")
        assert a._index == 0

    def test_leftover_response(self):
        a = ProtocolAdapter([("written", 5)])
        a._read_buffer = b"5"
        with raises(AssertionError):
            a.write_bytes(b"written")

    def test_no_response(self):
        a = ProtocolAdapter([("written", None)])
        a.write_bytes(b"writ")
        assert a._read_buffer is None

    def test_not_enough_pairs(self):
        a = ProtocolAdapter([("a", None)])
        a.write_bytes(b"a")
        with raises(ValueError):
            a.write_bytes(b"b")


class Test_read:
    @mark.parametrize("buffer, returned", ((b"\x03\x65", "\x03e"),
                                           (b"Bytes", "Bytes"),
                                           ))
    def test_works(self, buffer, returned):
        a = ProtocolAdapter()
        a._read_buffer = buffer
        assert a.read() == returned

    def test_read_empties_read_buffer(self):
        a = ProtocolAdapter()
        a._read_buffer = b"jklasdf"
        a.read()
        assert a._read_buffer is None

    def test_read_empty_message(self):
        a = ProtocolAdapter()
        a._read_buffer = b""
        assert a.read() == ""
        assert a._read_buffer is None


class Test_read_bytes:
    def test_read_full_buffer(self):
        a = ProtocolAdapter()
        a._read_buffer = b"Super 5"
        assert a.read_bytes(3) == b"Sup"
        assert a._read_buffer == b"er 5"

    def test_read_empty_buffer(self):
        a = ProtocolAdapter([(None, "Super 5")])
        assert a.read_bytes(3) == b"Sup"
        assert a._index == 1
        assert a._read_buffer == b"er 5"

    def test_read_without_write(self):
        a = ProtocolAdapter([("written", 5)])
        with raises(AssertionError):
            a.read_bytes(3)

    def test_read_all_bytes_empties_read_buffer(self):
        a = ProtocolAdapter()
        a._read_buffer = b"jklasdf"
        a.read_bytes(7)
        assert a._read_buffer is None

    def test_read_all_bytes_from_pairs_empties_read_buffer(self):
        a = ProtocolAdapter([(None, b"jklasdf")])
        a.read_bytes(7)
        assert a._read_buffer is None

    def test_no_messages(self):
        a = ProtocolAdapter()
        with raises(ValueError):
            a.read_bytes(3)

    def test_not_enough_pairs(self):
        a = ProtocolAdapter([(b"a", None)])
        a.write_bytes(b"a")
        with raises(ValueError):
            a.read_bytes(10)

    def test_unsolicited_response(self):
        a = ProtocolAdapter([(None, b"Response")])
        assert a.read_bytes(10) == b"Response"

    def test_read_with_missing_write(self):
        a = ProtocolAdapter([(b"a", b"b")])
        with raises(AssertionError):
            a.read_bytes(10)

    def test_catch_None_None_pair(self):
        a = ProtocolAdapter([(None, None)])
        with raises(AssertionError, match="None, None"):
            a.read_bytes(1)

    def test_break_on_termchar_raises_warning(self):
        a = ProtocolAdapter([(None, b"Response")])
        with warns(UserWarning, match="cannot be tested"):
            assert a.read_bytes(10, break_on_termchar=True) == b"Response"


def test_read_write_sequence():
    """Test several consecutive writes and reads, including ask."""
    a = ProtocolAdapter(
        [("c1", "a1"), ("c2", None), (None, "a3"), ("c4", "a4")])
    a.write("c1")
    assert a.read() == "a1"
    a.write("c2")
    assert a.read_bytes(-1) == b"a3"
    a.write_bytes(b"c4")
    assert a.read_bytes(2) == b"a4"


def test_write_and_read_with_and_without_bytes():
    """Test writing and reading, normal and bytes in combination."""
    a = ProtocolAdapter([("c1", "a1")])
    a.write_bytes(b"c")
    a.write("1")
    assert a.read_bytes(1) == b"a"
    assert a.read() == "1"


@mark.parametrize("pairs", ([("c2",)],
                            [(None, "a3", "c4")],
                            [("c1", None), ("c2",)],
                            [(None, "a3", "c4"), (None, None)],
                            ))
def test_comm_pairs_are_all_length_2(pairs):
    with raises(ValueError):
        ProtocolAdapter(pairs)
