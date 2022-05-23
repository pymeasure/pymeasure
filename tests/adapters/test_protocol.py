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

from pytest import mark, raises


@mark.parametrize("input, output", (("superXY", b"superXY"),
                                    ([1, 2, 3, 4], b"\x01\x02\x03\x04"),
                                    (5, b"\x05"),
                                    ))
def test_to_bytes(input, output):
    assert to_bytes(input) == output


def test_to_bytes_invalid():
    with raises(TypeError):
        to_bytes(5.5)


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
        assert a.read_buffer == b"\x05"

    def test_write_without_response(self):
        a = ProtocolAdapter([("Hey ho",)])
        a.write("Hey ho")
        assert a.read_buffer == b""

    def test_wrong_command(self):
        a = ProtocolAdapter([("Hey ho",)])
        with raises(AssertionError):
            a.write("Something different")

    def test_not_enough_pairs(self):
        a = ProtocolAdapter([("a",)])
        a.index = 1
        with raises(IndexError):
            a.write("b")


class Test_read:
    @mark.parametrize("buffer, returned", ((b"\x03\x65", "\x03e"),
                                           (b"Bytes", "Bytes"),
                                           ))
    def test_works(self, buffer, returned):
        a = ProtocolAdapter([])
        a.read_buffer = buffer
        assert a.read() == returned

    def test_unsolicited_response(self):
        a = ProtocolAdapter([(None, "Response")])
        assert a.read() == "Response"

    def test_not_enough_pairs(self):
        a = ProtocolAdapter([("a",)])
        a.index = 1
        with raises(IndexError):
            a.read()

    def test_read_with_missing_write(self):
        a = ProtocolAdapter([("a", "b")])
        with raises(AssertionError):
            a.read()


def test_read_write_sequence():
    a = ProtocolAdapter([("c1", "a1"), ("c2",), (None, "a3"), ("c4", "a4")])
    a.write("c1")
    assert a.read() == "a1"
    a.write("c2")
    assert a.read() == "a3"
    a.write("c4")
    assert a.read() == "a4"
    