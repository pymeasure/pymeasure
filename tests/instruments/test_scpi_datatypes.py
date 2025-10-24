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

from contextlib import nullcontext
import pytest

from pymeasure.instruments import SCPIKeyword


@pytest.mark.parametrize(
    "input_value, shortform, exception",
    (
        ("PYMeasure", "PYM", None),
        ("PYM", "PYM", None),
        ("PYMeasure1", "PYM1", None),
        (SCPIKeyword("PYMeasure"), "PYM", None),
        (1234, None, TypeError),
        ("PYMeasure-1", None, ValueError),
        ("pymeasure", None, ValueError),
        ("pymEASure", None, ValueError),
        ("PYM1easure", None, ValueError),
    ),
)
def test_scpi_keyword_init(input_value, shortform, exception):
    ctx = pytest.raises(exception) if exception else nullcontext()
    with ctx:
        keyword = SCPIKeyword(input_value)
        assert keyword.shortform == shortform


PYMEASURE_KEYWORD = SCPIKeyword("PYMeasure")


def test_scpi_keyword_repr():
    assert repr(PYMEASURE_KEYWORD) == "SCPIKeyword('PYMeasure')"


@pytest.mark.parametrize(
    "input_value, valid",
    (
        ("Pym", True),
        ("Pymeasure", True),
        ("Pymeas", False),
    ),
)
def test_scpi_keyword_eq(input_value, valid):
    assert (PYMEASURE_KEYWORD == input_value) is valid
