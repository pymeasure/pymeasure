#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
    strict_range, strict_discrete_set, strict_map,
    truncated_range, truncated_discrete_set, truncated_map
)

def test_strict_range():
    assert strict_range(5, range(10)) == 5
    assert strict_range(5.1, range(10)) == 5.1
    with pytest.raises(ValueError) as e_info:
        strict_range(20, range(10))


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

def test_strict_map():
    values = {5: 1, 10: 2, 20: 3}
    assert strict_map(5, values) == 1
    assert strict_map(10, values) == 2
    assert strict_map(20, values) == 3
    with pytest.raises(ValueError) as e_info:
        strict_map(5.1, values)

    assert strict_map(5, range(10)) == 5
    with pytest.raises(ValueError) as e_info:
        strict_map(5.1, range(10))
    with pytest.raises(ValueError) as e_info:
        strict_map(20, range(10))

    values = [1, 2, 5]
    assert strict_map(5, values) == 2
    with pytest.raises(ValueError) as e_info:
        strict_map(3, values)

def test_truncated_map():
    values = {5: 1, 10: 2, 20: 3}
    assert truncated_map(5, values) == 1
    assert truncated_map(10, values) == 2
    assert truncated_map(20, values) == 3
    assert truncated_map(30, values) == 3
    assert truncated_map(0, values) == 1

    assert truncated_map(5, range(10)) == 5
    assert truncated_map(5.1, range(10)) == 6
    assert truncated_map(-10, range(10)) == 0
    assert truncated_map(20, range(10)) == 9