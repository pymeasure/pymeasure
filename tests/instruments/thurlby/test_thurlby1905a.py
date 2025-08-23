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

from pymeasure.errors import Error, RangeError
from pymeasure.test import expected_protocol
from pymeasure.instruments.thurlby import Thurlby1905a


@pytest.mark.parametrize(
    "reading,expected",
    [
        ("R  000.000", 0.0),
        ("R  997.628", 997.628),
        ("R  097.550", 97.55),
        ("R  045.970", 45.97),
    ],
)
def test_translate_positive_reading(reading, expected):
    assert Thurlby1905a._parse(reading) == expected


@pytest.mark.parametrize(
    "reading,expected",
    [
        ("R- 000.000", -0.0),
        ("R- 997.628", -997.628),
        ("R- 097.550", -97.55),
        ("R- 001.8  ", -1.8),
    ],
)
def test_translate_negative_reading(reading, expected):
    assert Thurlby1905a._parse(reading) == expected


def test_measurement_too_short():
    """all meaurements must be exactly 10 bytes long"""
    with pytest.raises(ValueError):
        # 9 bytes long
        _ = Thurlby1905a._parse("R- 0.6   ")


def test_measurement_too_long():
    """all meaurements must be exactly 10 bytes long"""
    with pytest.raises(ValueError):
        # 11 bytes long
        _ = Thurlby1905a._parse("R  1.655500")


def test_overrange():
    with pytest.raises(RangeError):
        _ = Thurlby1905a._parse("M   OR    ")


def test_general_error():
    with pytest.raises(Error):
        _ = Thurlby1905a._parse("M   ERROR ")


def test_unknown_message():
    """only recognised messages are 'OR' and 'ERROR'"""
    with pytest.raises(Error):
        _ = Thurlby1905a._parse("M   T56   ")


def test_unknown_measurement_type():
    """only allowed measurement types are 'M' (Message) or 'R' (Reading)"""
    with pytest.raises(Error):
        _ = Thurlby1905a._parse("Q   T56   ")


@pytest.mark.parametrize(
    "serial_out, expected",
    [
        ("R  997.40 ", 997.4),
        ("R- 1.0008 ", -1.0008),
    ],
)
def test_measurement_direct(serial_out, expected):
    with expected_protocol(
        Thurlby1905a,
        [
            (None, serial_out),
        ],
    ) as instr:
        assert instr.measurement == expected


@pytest.mark.parametrize(
    "serial_out, exception",
    [
        ("M   OR    ", RangeError),
        ("M   ERROR ", Error),
        ("M   JUNK  ", Error),
        ("N   MGH   ", Error),
        ("R 123.40", ValueError),  # Too short: 8 bytes, must be 10 bytes long
        ("R-  555.40 ", ValueError),  # Too long: 12 bytes, must be 10 bytes long
    ],
)
def test_raises_exception_on_measurement(serial_out, exception):
    with pytest.raises(exception):
        with expected_protocol(
            Thurlby1905a,
            [
                (None, serial_out),
            ],
        ) as instr:
            _ = instr.measurement
