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

import numpy as np
import pytest

from pymeasure.experiment.parameters import Parameter
from pymeasure.experiment.parameters import IntegerParameter
from pymeasure.experiment.parameters import BooleanParameter
from pymeasure.experiment.parameters import FloatParameter
from pymeasure.experiment.parameters import ListParameter
from pymeasure.experiment.parameters import VectorParameter


def test_parameter_default():
    p = Parameter('Test', default=5)
    assert p.value == 5
    assert p.cli_args[0] == 5
    assert p.cli_args[1] == [('units are', 'units'), 'default']
    assert p._cli_help_fields() == 'Test:\n\nDefault is 5.'


def test_integer_units():
    p = IntegerParameter('Test', units='V')
    assert p.units == 'V'
    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default', 'minimum', 'maximum']


def test_integer_value():
    p = IntegerParameter('Test', units='tests')
    with pytest.raises(ValueError):
        _ = p.value  # not set
    with pytest.raises(ValueError):
        p.value = 'a'  # not an integer
    p.value = 0.5  # a float
    assert p.value == 0
    p.value = False  # a boolean
    assert p.value == 0
    p.value = 10
    assert p.value == 10
    p.value = '5'
    assert p.value == 5
    p.value = '11 tests'
    assert p.value == 11
    assert p.units == 'tests'
    with pytest.raises(ValueError):
        p.value = '31 incorrect units'  # not the correct units


def test_integer_bounds():
    p = IntegerParameter('Test', minimum=0, maximum=10)
    p.value = 10
    assert p.value == 10
    with pytest.raises(ValueError):
        p.value = 100  # above maximum
    with pytest.raises(ValueError):
        p.value = -100  # below minimum


def test_boolean_value_error():
    p = BooleanParameter('Test')
    with pytest.raises(ValueError):
        _ = p.value  # not set
    with pytest.raises(ValueError):
        p.value = 'a'  # a string
    with pytest.raises(ValueError):
        p.value = 10  # a number other than 0 or 1
    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default']


@pytest.mark.parametrize("value, mapping", (
                         ["True", True],
                         ["true", True],
                         [1, True],
                         [np.bool(True), True],
                         ["False", False],
                         ["false", False],
                         [0, False],
                         [np.bool(False), False],
                         ))
def test_boolean_value(value, mapping):
    p = BooleanParameter('Test')
    p.value = value
    assert p.value == mapping


def test_float_value():
    p = FloatParameter('Test', units='tests')
    with pytest.raises(ValueError):
        _ = p.value  # not set
    with pytest.raises(ValueError):
        p.value = 'a'  # not a float
    p.value = False  # boolean
    assert p.value == 0.0
    p.value = 100
    assert p.value == 100.0
    p.value = '1.06'
    assert p.value == 1.06
    p.value = '11.3 tests'
    assert p.value == 11.3
    assert p.units == 'tests'
    with pytest.raises(ValueError):
        p.value = '31.3 incorrect units'  # not the correct units
    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default',
                             ('decimals are', 'decimals')]


def test_float_bounds():
    p = FloatParameter('Test', minimum=0.1, maximum=0.5)
    p.value = 0.3
    assert p.value == 0.3
    with pytest.raises(ValueError):
        p.value = 10  # above maximum
    with pytest.raises(ValueError):
        p.value = -10  # below minimum


def test_list_string():
    # make sure string representation of choices is unique
    with pytest.raises(ValueError):
        _ = ListParameter('Test', choices=[1, '1'])


def test_list_value():
    p = ListParameter('Test', choices=[1, 2.2, 'three', 'and four'])
    p.value = 1
    assert p.value == 1
    p.value = 2.2
    assert p.value == 2.2
    p.value = '1'  # reading from file
    assert p.value == 1
    p.value = '2.2'  # reading from file
    assert p.value == 2.2
    p.value = 'three'
    assert p.value == 'three'
    p.value = 'and four'
    assert p.value == 'and four'
    with pytest.raises(ValueError):
        p.value = 5
    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default',
                             ('choices are', 'choices')]


def test_list_value_with_units():
    p = ListParameter(
        'Test', choices=[1, 2.2, 'three', 'and four'],
        units='tests')
    p.value = '1 tests'
    assert p.value == 1
    p.value = '2.2 tests'
    assert p.value == 2.2
    p.value = 'three tests'
    assert p.value == 'three'
    p.value = 'and four tests'
    assert p.value == 'and four'
    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default',
                             ('choices are', 'choices')]


def test_list_order():
    p = ListParameter('Test', choices=[1, 2.2, 'three', 'and four'])
    # check if order is preserved, choices are internally stored as dict
    assert p.choices == (1, 2.2, 'three', 'and four')
    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default',
                             ('choices are', 'choices')]


def test_vector_error():
    p = VectorParameter('test', length=3, units='tests')
    with pytest.raises(ValueError):
        p.value = '[0, 1, 2] wrong unit'
    with pytest.raises(ValueError):
        p.value = [1, 2]
    with pytest.raises(ValueError):
        p.value = ['a', 'b']
    with pytest.raises(ValueError):
        p.value = '0, 1, 2'

    assert p.cli_args[0] is None
    assert p.cli_args[1] == [('units are', 'units'), 'default', ('length is', '_length')]


@pytest.mark.parametrize("value, mapping", (
                         [[1, 2, 3], [1, 2, 3]],
                         ['[4, 5, 6]', [4, 5, 6]],
                         ['[7, 8, 9] tests', [7, 8, 9]],
                         [np.array([10, 11, 12]), [10, 11, 12]],
                         ))
def test_vector(value, mapping):
    p = VectorParameter('test', length=3, units='tests')
    p.value = value
    assert p.value == mapping

# TODO: Add tests for Measurable
