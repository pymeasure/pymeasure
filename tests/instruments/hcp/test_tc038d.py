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

import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.hcp import TC038D


# Testing the 'write multiple values' method of the device.
def test_write_multiple_values():
    # Communication from manual.
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x0A\x00\x04\x08\x00\x00\x03\xE8\xFF\xFF\xFC\x18\x8D\xE9",
          b"\x01\x10\x01\x0A\x00\x04\xE0\x34")]
    ) as inst:
        inst.write("W,0x010A,1000,-1000")
        inst.read()


def test_write_multiple_values_decimal_address():
    # Communication from manual.
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x0A\x00\x04\x08\x00\x00\x03\xE8\xFF\xFF\xFC\x18\x8D\xE9",
          b"\x01\x10\x01\x0A\x00\x04\xE0\x34")]
    ) as inst:
        inst.write("W,266,1000,-1000")
        inst.read()


def test_write_values_CRC_error():
    """Test whether an invalid response CRC code raises an Exception."""
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x06\x00\x02\x04\x00\x00\x01A\xbf\xb5",
          b"\x01\x10\x01\x06\x00\x02\x01\x02")],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.setpoint = 32.1


def test_write_multiple_handle_wrong_start_address():
    """Test whether the error code (byte 2) of 2 raises the right error."""
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x06\x00\x02\x04\x00\x00\x01A\xbf\xb5",
          b"\x01\x90\x02\xcd\xc1")],
    ) as inst:
        with pytest.raises(ValueError, match="Wrong start address"):
            inst.setpoint = 32.1


# Test the 'read register' method of the device
def test_read_CRC_error():
    """Test whether an invalid response CRC code raises an Exception."""
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
          b"\x01\x03\x04\x00\x00\x03\xE8\x01\x02")],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.temperature


def test_read_address_error():
    """Test whether the error code (byte 2) of 2 raises the right error."""
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
          b"\x01\x83\x02\xc0\xf1")],
    ) as inst:
        with pytest.raises(ValueError, match="start address"):
            inst.temperature


def test_read_elements_error():
    """Test whether the error code (byte 2) of 3 raises the right error."""
    with expected_protocol(
            TC038D,
            [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
              b"\x01\x83\x03\x011")],
    ) as inst:
        with pytest.raises(ValueError, match="Variable data"):
            inst.temperature


def test_read_any_error():
    """Test whether any wrong message (byte 1 is not 3) raises an error."""
    with expected_protocol(
            TC038D,
            [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
              b"\x01\x43\x05\xd13")],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.temperature


# Test properties
def test_setpoint():
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x01\x06\x00\x02\x25\xf6",
          b"\x01\x03\x04\x00\x00\x00\x99:Y")],
    ) as inst:
        assert inst.setpoint == 15.3


def test_setpoint_setter():
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x06\x00\x02\x04\x00\x00\x01A\xbf\xb5",
          b"\x01\x10\x01\x06\x00\x02\xa0\x35")],
    ) as inst:
        inst.setpoint = 32.1


def test_temperature():
    # Communication from manual.
    # Tests readRegister as well.
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
         b"\x01\x03\x04\x00\x00\x03\xE8\xFA\x8D")],
    ) as inst:
        assert inst.temperature == 100


def test_ping():
    # Communication from manual.
    with expected_protocol(
        TC038D,
        [(b"\x01\x08\x00\x00\x12\x34\xed\x7c", b"\x01\x08\x00\x00\x12\x34\xed\x7c")],
    ) as inst:
        inst.ping(4660)
