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

from pymeasure.instruments import SCPIKeyword, SCPIKeywordEnum
from pymeasure.instruments.validators import strict_discrete_set


# === SCPIKeyword ===


@pytest.mark.parametrize(
    "input_value, shortform",
    (
        ("ALPHa", "ALPH"),
        ("ALPH", "ALPH"),
        ("ALPHa1", "ALPH1"),
        (SCPIKeyword("ALPHa"), "ALPH"),
    ),
)
def test_scpi_keyword_init_valid(input_value, shortform):
    assert SCPIKeyword(input_value).shortform == shortform


@pytest.mark.parametrize("input_value", [1234])
def test_scpi_keyword_init_type_error(input_value):
    with pytest.raises(TypeError):
        SCPIKeyword(input_value)


@pytest.mark.parametrize("input_value", ("ALPHa-1", "alpha", "alPHa", "A1PHa"))
def test_scpi_keyword_init_value_error(input_value):
    with pytest.raises(ValueError):
        SCPIKeyword(input_value)


ALPHA_KEYWORD = SCPIKeyword("ALPHa")


def test_scpi_keyword_repr():
    assert repr(ALPHA_KEYWORD) == "SCPIKeyword('ALPHa')"


@pytest.mark.parametrize("input_value, valid", [("Alph", True), ("Alpha", True), ("ALP", False)])
def test_scpi_keyword_eq(input_value, valid):
    assert (ALPHA_KEYWORD == input_value) is valid


@pytest.mark.parametrize("input_value", ["Alph", "Alpha"])
def test_scpi_keyword_strict_discrete_set_valid(input_value):
    strict_discrete_set(input_value, [ALPHA_KEYWORD])


@pytest.mark.parametrize("input_value", ["ALP"])
def test_scpi_keyword_strict_discrete_set_value_error(input_value):
    with pytest.raises(ValueError):
        strict_discrete_set(input_value, [ALPHA_KEYWORD])


# === SCPIKeywordEnum ===


class PhoneticKeywordEnum(SCPIKeywordEnum):
    ALPHA = "ALPHa"
    BRAVO = SCPIKeyword("BRAVo")


@pytest.mark.parametrize("input_value, valid", [("Alph", True), ("Alpha", True), ("ALP", False)])
def test_scpi_keyword_enum_eq(input_value, valid):
    assert (PhoneticKeywordEnum.ALPHA == input_value) is valid


@pytest.mark.parametrize(
    "input_value, expected_member",
    [
        ("ALPHa", PhoneticKeywordEnum.ALPHA),
        ("alph", PhoneticKeywordEnum.ALPHA),
        ("Alpha", PhoneticKeywordEnum.ALPHA),
        ("Bravo", PhoneticKeywordEnum.BRAVO),
    ],
)
def test_scpi_keyword_enum_lookup_valid(input_value, expected_member):
    assert PhoneticKeywordEnum(input_value) is expected_member


@pytest.mark.parametrize("input_value", ["Charlie", "", None])
def test_scpi_keyword_enum_lookup_value_error(input_value):
    with pytest.raises(ValueError):
        PhoneticKeywordEnum(input_value)


def test_scpi_keyword_str():
    assert str(PhoneticKeywordEnum.ALPHA) == str(PhoneticKeywordEnum.ALPHA.value)
