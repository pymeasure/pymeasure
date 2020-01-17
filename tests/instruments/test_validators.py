#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
from pymeasure.instruments.validators import (
    strict_range, strict_discrete_range, strict_discrete_set,
    truncated_range, truncated_discrete_set,
    modular_range, modular_range_bidirectional,
    joined_validators
)


def test_strict_range():
    assert strict_range(5, range(10)) == 5
    assert strict_range(5.1, range(10)) == 5.1
    with pytest.raises(ValueError) as e_info:
        strict_range(20, range(10))


def test_strict_discrete_range():
    assert strict_discrete_range(0.1, [0, 0.2], 0.001) == 0.1
    assert strict_discrete_range(5, range(10), 0.1) == 5
    assert strict_discrete_range(5.1, range(10), 0.1) == 5.1
    assert strict_discrete_range(5.1, range(10), 0.001) == 5.1
    assert strict_discrete_range(-5.1, [-20, 20], 0.001) == -5.1
    with pytest.raises(ValueError) as e_info:
        strict_discrete_range(5.1, range(5), 0.001)
    with pytest.raises(ValueError) as e_info:
        strict_discrete_range(5.01, range(5), 0.1)
    with pytest.raises(ValueError) as e_info:
        strict_discrete_range(0.003, [0, 0.2], 0.002)


def test_strict_discrete_set():
    assert strict_discrete_set(5, range(10)) == 5
    with pytest.raises(ValueError) as e_info:
        strict_discrete_set(5.1, range(10))
    with pytest.raises(ValueError) as e_info:
        strict_discrete_set(20, range(10))


def test_truncated_range():
    assert truncated_range(5, range(10)) == 5
    assert truncated_range(5.1, range(10)) == 5.1
    assert truncated_range(-10, range(10)) == 0
    assert truncated_range(20, range(10)) == 9


def test_truncated_discrete_set():
    assert truncated_discrete_set(5, range(10)) == 5
    assert truncated_discrete_set(5.1, range(10)) == 6
    assert truncated_discrete_set(11, range(10)) == 9
    assert truncated_discrete_set(-10, range(10)) == 0


def test_modular_range():
    assert modular_range(5, range(10)) == 5
    assert abs(modular_range(5.1, range(10)) - 5.1) < 1e-6
    assert modular_range(11, range(10)) == 2
    assert abs(modular_range(11.3, range(10)) - 2.3) < 1e-6
    assert abs(modular_range(-7.1, range(10)) - 1.9) < 1e-6
    assert abs(modular_range(-13.2, range(10)) - 4.8) < 1e-6


def test_modular_range_bidirectional():
    assert modular_range_bidirectional(5, range(10)) == 5
    assert abs(modular_range_bidirectional(5.1, range(10)) - 5.1) < 1e-6
    assert modular_range_bidirectional(11, range(10)) == 2
    assert abs(modular_range_bidirectional(11.3, range(10)) - 2.3) < 1e-6
    assert modular_range_bidirectional(-7, range(10)) == -7
    assert abs(modular_range_bidirectional(-7.1, range(10)) - (-7.1)) < 1e-6
    assert abs(modular_range_bidirectional(-13.2, range(10)) - (-4.2)) < 1e-6


def test_joined_validators():
    tst_validator = joined_validators(strict_discrete_set, strict_range)
    assert tst_validator(5, [["ON", "OFF"], range(10)]) == 5
    assert tst_validator(5.1, [["ON", "OFF"], range(10)]) == 5.1
    assert tst_validator("ON", [["ON", "OFF"], range(10)]) == "ON"
    with pytest.raises(ValueError) as e_info:
        tst_validator("OUT", [["ON", "OFF"], range(10)])
    with pytest.raises(ValueError) as e_info:
        tst_validator(20, [["ON", "OFF"], range(10)])
