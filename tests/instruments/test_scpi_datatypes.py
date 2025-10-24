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

from pymeasure.instruments import SCPIKeyword, SCPIKeywordEnum


# === SCPIKeyword ===


@pytest.mark.parametrize(
    "input_value, shortform, expected_exception",
    (
        ("ALPHa", "ALPH", None),
        ("ALPH", "ALPH", None),
        ("ALPHa1", "ALPH1", None),
        (SCPIKeyword("ALPHa"), "ALPH", None),
        (1234, None, TypeError),
        ("ALPHa-1", None, ValueError),
        ("alpha", None, ValueError),
        ("alPHa", None, ValueError),
        ("A1PHa", None, ValueError),
    ),
)
def test_scpi_keyword_init(input_value, shortform, expected_exception):
    ctx = pytest.raises(expected_exception) if expected_exception else nullcontext()
    with ctx:
        keyword = SCPIKeyword(input_value)
        assert keyword.shortform == shortform


ALPHA_KEYWORD = SCPIKeyword("ALPHa")


def test_scpi_keyword_repr():
    assert repr(ALPHA_KEYWORD) == "SCPIKeyword('ALPHa')"


@pytest.mark.parametrize(
    "input_value, valid",
    (
        ("Alph", True),
        ("Alpha", True),
        ("ALP", False),
    ),
)
def test_scpi_keyword_eq(input_value, valid):
    assert (ALPHA_KEYWORD == input_value) is valid


# === SCPIKeywordEnum ===


class AlphaKeywordEnum(SCPIKeywordEnum):
    ALPHA = "ALPHa"


@pytest.mark.parametrize(
    "input_value, valid",
    (
        ("Alph", True),
        ("Alpha", True),
        ("ALP", False),
    ),
)
def test_scpi_keyword_enum_eq(input_value, valid):
    assert (AlphaKeywordEnum.ALPHA == input_value) is valid


@pytest.mark.parametrize(
    "input_value, expected_member, expected_exception",
    [
        ("ALPHa", AlphaKeywordEnum.ALPHA, None),
        ("alph", AlphaKeywordEnum.ALPHA, None),
        ("Alpha", AlphaKeywordEnum.ALPHA, None),
        ("Bravo", None, ValueError),
        ("", None, ValueError),
        (None, None, ValueError),
    ],
)
def test_scpi_keyword_enum_lookup(input_value, expected_member, expected_exception):
    ctx = pytest.raises(expected_exception) if expected_exception else nullcontext()
    with ctx:
        assert AlphaKeywordEnum(input_value) is expected_member
