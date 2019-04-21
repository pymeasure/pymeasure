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

from pymeasure.experiment.parameters import Parameter
from pymeasure.experiment.parameters import IntegerParameter
from pymeasure.experiment.parameters import BooleanParameter
from pymeasure.experiment.parameters import FloatParameter


def test_parameter_default():
    p = Parameter('Test', default=5)
    assert p.value == 5


def test_integer_units():
    p = IntegerParameter('Test', units='V')
    assert p.units == 'V'


def test_integer_value():
    p = IntegerParameter('Test')
    with pytest.raises(ValueError):
        v = p.value  # not set
    with pytest.raises(ValueError):
        p.value = 'a'  # not an integer
    p.value = 0.5  # a float
    assert p.value == 0
    p.value = False  # a boolean
    assert p.value == 0
    p.value = 10
    assert p.value == 10


def test_integer_bounds():
    p = IntegerParameter('Test', minimum=0, maximum=10)
    p.value = 10
    assert p.value == 10
    with pytest.raises(ValueError):
        p.value = 100  # above maximum
    with pytest.raises(ValueError):
        p.value = -100  # below minimum


def test_boolean_value():
    p = BooleanParameter('Test')
    with pytest.raises(ValueError):
        v = p.value  # not set
    p.value = 'a'  # a string
    assert p.value == True
    p.value = 10  # a number
    assert p.value == True
    p.value = 0  # zero
    assert p.value == False
    p.value = True
    assert p.value == True


def test_float_value():
    p = FloatParameter('Test')
    with pytest.raises(ValueError):
        v = p.value  # not set
    with pytest.raises(ValueError):
        p.value = 'a'  # not a float
    p.value = False  # boolean
    assert p.value == 0.0
    p.value = 100
    assert p.value == 100.0


def test_float_bounds():
    p = FloatParameter('Test', minimum=0.1, maximum=0.5)
    p.value = 0.3
    assert p.value == 0.3
    with pytest.raises(ValueError):
        p.value = 10  # above maximum
    with pytest.raises(ValueError):
        p.value = -10  # below minimum

# TODO: Add tests for VectorParameter, ListParamter, and Measurable
