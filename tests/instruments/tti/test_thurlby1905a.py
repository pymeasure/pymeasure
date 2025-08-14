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
from pymeasure.instruments.tti import Thurlby1905a


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
    assert Thurlby1905a._translate(reading) == expected


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
    assert Thurlby1905a._translate(reading) == expected


def test_measurement_too_short():
    """all meaurements must be exactly 10 bytes long"""
    with pytest.raises(ValueError):
        # 9 bytes long
        _ = Thurlby1905a._translate("R- 0.6   ")


def test_measurement_too_long():
    """all meaurements must be exactly 10 bytes long"""
    with pytest.raises(ValueError):
        # 11 bytes long
        _ = Thurlby1905a._translate("R  1.655500")


def test_overrange():
    with pytest.raises(RangeError):
        _ = Thurlby1905a._translate("M   OR    ")


def test_general_error():
    with pytest.raises(Error):
        _ = Thurlby1905a._translate("M   ERROR ")


def test_unknown_message():
    """only recognised messages are 'OR' and 'ERROR'"""
    with pytest.raises(Error):
        _ = Thurlby1905a._translate("M   T56   ")


def test_unknown_measurement_type():
    """only allowed measurement types are 'M' (Message) or 'R' (Reading)"""
    with pytest.raises(Error):
        _ = Thurlby1905a._translate("Q   T56   ")
