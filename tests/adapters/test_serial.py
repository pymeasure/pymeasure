#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

import pytest
import serial
from unittest.mock import patch

from pymeasure.adapters import SerialAdapter


@pytest.fixture
def adapter():
    return SerialAdapter(serial.serial_for_url("loop://", timeout=0.2))


@pytest.mark.parametrize("term", (("", "\n", "123\r")))
def test_write_termination(adapter, term):
    adapter.write_termination = term
    adapter.write("abc")
    assert adapter.read() == "abc" + term


@pytest.mark.parametrize("term", (("", "\n", "\r\n", "4.1123")))
def test_read_termination(adapter, term):
    adapter.read_termination = term
    adapter.write("abc" + term)
    assert adapter.read() == "abc"


@pytest.mark.parametrize("msg", ["OUTP\n", "POWER 22 dBm\n"])
def test_adapter_write_read(adapter, msg):
    adapter.write(msg)
    assert adapter.read() == msg


@pytest.mark.parametrize("msg", [b"OUTP\n", b"POWER 22 dBm\n"])
def test_write_bytes(adapter, msg):
    adapter.write_bytes(msg)
    assert adapter.read() == msg.decode()


def test_read_bytes(adapter):
    """Test whether `count` bytes are returned, even though a term char is defined."""
    adapter.read_termination = "\n"
    adapter.write_bytes(b"basd\x02\nfasdf\n")
    assert adapter.read_bytes(9) == b"basd\x02\nfas"


def test_read_bytes_unlimited(adapter):
    """Test whether all bytes are returned, even though a term char is defined."""
    adapter.read_termination = "\n"
    adapter.write_bytes(b"basd\x02\nfasdf\n")
    assert adapter.read_bytes(-1) == b"basd\x02\nfasdf\n"


def test_read_bytes_unlimited_long(adapter):
    """Test whether all bytes are returned when a lot of data is sent."""
    adapter.write_bytes(b"abcde" * 50)
    assert adapter.read_bytes(-1) == b"abcde" * 50


@pytest.mark.parametrize("count", (-1, 8))
def test_read_bytes_break_on_termchar(adapter, count):
    adapter.read_termination = "\n"
    adapter.write_bytes(b"basd\x02\nfasdf\n")
    assert adapter.read_bytes(count, break_on_termchar=True) == b"basd\x02\n"


def test_init_with_port_string():
    """Construct a SerialAdapter passing a port string.

    This covers the `serial.Serial(port, **kwargs)` branch. On Linux
    `serial.Serial("loop://")` would attempt `os.open` and raise
    `SerialException`, so we patch `serial.Serial` to verify the construction
    path while still obtaining a usable `loop://` connection for assertions.
    """
    real_connection = serial.serial_for_url("loop://", timeout=0.2)
    with patch(
        "pymeasure.adapters.serial.serial.Serial",
        return_value=real_connection,
    ) as mock_serial:
        adapter = SerialAdapter("loop://", timeout=0.2)
    try:
        mock_serial.assert_called_once_with("loop://", timeout=0.2)
        assert adapter.connection is real_connection
    finally:
        adapter.connection.close()


def test_flush_read_buffer(adapter):
    """Verify that `flush_read_buffer` empties the input buffer."""
    adapter.write_bytes(b"some data")
    assert adapter.connection.in_waiting > 0
    adapter.flush_read_buffer()
    assert adapter.connection.in_waiting == 0


def test_repr(adapter):
    """Verify the `repr` of a SerialAdapter includes `port=`."""
    assert repr(adapter) == "<SerialAdapter(port='loop://')>"


@pytest.mark.parametrize("test_input,expected", [([1, 2, 3], b'OUTP#13\x01\x02\x03'),
                                                 (range(100), b'OUTP#3100' + bytes(range(100)))])
def test_adapter_write_binary_values(adapter, test_input, expected):
    adapter.write_binary_values("OUTP", test_input, datatype='B')
    # Add 10 bytes more, just to check that no extra bytes are present
    assert adapter.connection.read(len(expected) + 10) == expected
