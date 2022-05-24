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

from pymeasure.adapters.protocol import to_bytes, ProtocolAdapter

from pytest import mark, raises, fixture


@mark.parametrize("input, output", (("superXY", b"superXY"),
                                    ([1, 2, 3, 4], b"\x01\x02\x03\x04"),
                                    (5, b"5"),
                                    (4.6, b"4.6")
                                    ))
def test_to_bytes(input, output):
    assert to_bytes(input) == output


def test_to_bytes_invalid():
    with raises(TypeError):
        to_bytes(5.5j)


def test_protocol_instantiation():
    a = ProtocolAdapter([("write", "read"), ("write_only",)])
    assert a.comm_pairs == [("write", "read"), ("write_only",)]
    # TODO: Make this first test assert something useful


class Test_write:
    @mark.parametrize("command, written", (("hey Ho", b"hey Ho"),
                                           (b"superX", "superX")
                                           ))
    def test_write(self, command, written):
        a = ProtocolAdapter([(written, 5)])
        a.write(command)
        assert a._read_buffer == b"5"

    def test_write_without_response(self):
        a = ProtocolAdapter([("Hey ho",)])
        a.write("Hey ho")
        assert a._read_buffer == b""

    def test_wrong_command(self):
        a = ProtocolAdapter([("Hey ho",)])
        with raises(AssertionError):
            a.write("Something different")

    def test_not_enough_pairs(self):
        a = ProtocolAdapter([("a",)])
        a._index = 1
        with raises(IndexError):
            a.write("b")


class Test_write_bytes:
    @fixture(scope="class")
    def written1(self):
        """Write in a single turn."""
        a = ProtocolAdapter([("written", 5)])
        a.write_bytes(b"written")
        return a

    @fixture(scope="class")
    def written2(self):
        """Write in two turns."""
        a = ProtocolAdapter([("written", 5)])
        a.write_bytes(b"writ")
        a.write_bytes(b"ten")
        return a

    def test_write_write_buffer1(self, written1):
        assert written1._write_buffer == b""

    def test_write_write_buffer2(self, written2):
        assert written2._write_buffer == b""

    def test_write_index1(self, written1):
        assert written1._index == 1

    def test_write_index2(self, written2):
        assert written2._index == 1

    def test_write_read_buffer1(self, written1):
        assert written1._read_buffer == b"5"

    def test_write_read_buffer2(self, written2):
        assert written2._read_buffer == b"5"

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
        a = ProtocolAdapter([("written",)])
        a.write_bytes(b"writ")
        assert a._read_buffer == b""


class Test_read:
    @mark.parametrize("buffer, returned", ((b"\x03\x65", "\x03e"),
                                           (b"Bytes", "Bytes"),
                                           ))
    def test_works(self, buffer, returned):
        a = ProtocolAdapter([])
        a._read_buffer = buffer
        assert a.read() == returned

    def test_unsolicited_response(self):
        a = ProtocolAdapter([(None, "Response")])
        assert a.read() == "Response"

    def test_not_enough_pairs(self):
        a = ProtocolAdapter([("a",)])
        a._index = 1
        with raises(IndexError):
            a.read()

    def test_read_with_missing_write(self):
        a = ProtocolAdapter([("a", "b")])
        with raises(AssertionError):
            a.read()


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

    def test_no_messages(self):
        a = ProtocolAdapter([])
        with raises(IndexError):
            a.read_bytes(3)


def test_read_write_sequence():
    """Test several consecutive writes and reads, including ask."""
    a = ProtocolAdapter([("c1", "a1"), ("c2",), (None, "a3"), ("c4", "a4")])
    a.write("c1")
    assert a.read() == "a1"
    a.write("c2")
    assert a.read() == "a3"
    assert a.ask("c4") == "a4"


def test_write_and_read_with_and_without_bytes():
    """Test writing and reading, normal and bytes in combination."""
    a = ProtocolAdapter([("c1", "a1"), ("c4", "a4")])
    a.write_bytes(b"c")
    a.write("1")
    assert a.read_bytes(1) == b"a"
    assert a.read() == "1"
