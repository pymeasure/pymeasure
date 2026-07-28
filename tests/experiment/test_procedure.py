#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

import pickle

import pytest
from data.procedure_for_testing import RandomProcedure

from pymeasure.experiment.parameters import Parameter
from pymeasure.experiment.procedure import Procedure, ProcedureWrapper, UnknownProcedure
from pymeasure.units import ureg


def test_parameters():
    class TestProcedure(Procedure):
        x = Parameter('X', default=5)

    p = TestProcedure()
    assert p.x == 5
    p.x = 10
    assert p.x == 10
    assert p.parameters_are_set()
    objs = p.parameter_objects()
    assert 'x' in objs
    assert objs['x'].value == p.x


# TODO: Add tests for measureables


def test_procedure_wrapper():
    assert RandomProcedure.iterations.value == 100
    procedure = RandomProcedure()
    procedure.iterations = 101
    wrapper = ProcedureWrapper(procedure)

    new_wrapper = pickle.loads(pickle.dumps(wrapper))
    assert hasattr(new_wrapper, 'procedure')
    assert new_wrapper.procedure.iterations == 101
    assert RandomProcedure.iterations.value == 100


# This test checks that user can define properties using the parameters inside the procedure
# The test ensure that property is evaluated only when the Parameter has been processed during
# class initialization.


def test_procedure_properties():
    class TestProcedure(Procedure):
        @property
        def a(self):
            assert isinstance(self.x, int)
            return self.x

        @property
        def z(self):
            assert isinstance(self.x, int)
            return self.x

        x = Parameter('X', default=5)

    p = TestProcedure()
    assert p.x == 5


# Make sure that a procedure can be initialized even though some properties are raising
# errors at initialization time


def test_procedure_init_with_invalid_property():
    class TestProcedure(Procedure):
        @property
        def prop(self):
            return self.x

    p = TestProcedure()
    with pytest.raises(AttributeError):
        _ = p.prop  # AttributeError
    p.x = 5
    assert p.prop == 5


@pytest.mark.parametrize("header, units", (
        ("x (m)", ureg.m),
        ("x (m/s)", ureg.m / ureg.s),
        ("x (V/(m*s))", ureg.V / ureg.m / ureg.s),
        ("x (1)", ureg.dimensionless)
))
def test_procedure_parse_columns(header, units):
    assert Procedure.parse_columns([header])[header] == ureg.Quantity(1, units)


@pytest.mark.parametrize("valid_header_no_unit", (
        ["x"], ["x ( x + y )"], ["x ( notes )"], ["x [V]"]
))
def test_procedure_no_parsed_units(valid_header_no_unit):
    assert Procedure.parse_columns(valid_header_no_unit) == {}


@pytest.mark.parametrize("invalid_header_unit", (
        ["x (sqrt)"], ["x (x)"], ["x (y)"],
))
def test_procedure_invalid_parsed_unit(invalid_header_unit):
    with pytest.raises(ValueError):
        Procedure.parse_columns(invalid_header_unit)


# Phase 2: non-idempotent convert must not be double-invoked.


class _CountingParameter(Parameter):
    """Parameter subclass recording every `convert` invocation."""

    def __init__(self, name, default=None, **kwargs):
        self.convert_calls: list = []
        super().__init__(name, default=default, **kwargs)

    def convert(self, value):
        self.convert_calls.append(value)
        return value


def test_parameter_values_does_not_double_convert():
    """`parameter_values()` must not invoke `convert` a second time on already-converted values."""

    class TestProcedure(Procedure):
        x = _CountingParameter('X', default=None)

    p = TestProcedure()
    p.x = 5
    # one convert call from the descriptor __set__
    assert p._parameters['x'].convert_calls == [5]
    values = p.parameter_values()
    assert values['x'] == 5
    # no additional convert calls
    assert p._parameters['x'].convert_calls == [5]


def test_parameter_objects_does_not_double_convert():
    """`parameter_objects()` must not invoke `convert` a second time on already-converted values."""

    class TestProcedure(Procedure):
        x = _CountingParameter('X', default=None)

    p = TestProcedure()
    p.x = 7
    assert p._parameters['x'].convert_calls == [7]
    objs = p.parameter_objects()
    assert objs['x'].value == 7
    assert p._parameters['x'].convert_calls == [7]


def test_refresh_parameters_no_raise_on_unset_parameter():
    """`refresh_parameters()` must not raise when a Parameter has no value (None)."""

    class TestProcedure(Procedure):
        x = Parameter('X', default=None)

    p = TestProcedure()
    assert p.x is None
    p.refresh_parameters()  # must not raise


def test_param_values_not_populated():
    """`_param_values` is no longer created by `_update_parameters`."""

    class TestProcedure(Procedure):
        x = Parameter('X', default=5)

    p = TestProcedure()
    assert getattr(p, '_param_values', None) is None


def test_procedure_wrapper_pickle_with_unset_parameter():
    """Pickling a procedure with an unset (None) parameter round-trips without raising."""
    procedure = RandomProcedure()
    procedure.iterations = 101
    procedure.seed = None
    wrapper = ProcedureWrapper(procedure)

    new_wrapper = pickle.loads(pickle.dumps(wrapper))
    assert new_wrapper.procedure.iterations == 101
    assert new_wrapper.procedure.seed is None
    assert RandomProcedure.iterations.value == 100


def test_unknown_procedure_parameter_objects_returns_empty():
    """`UnknownProcedure.parameter_objects()` returns `{}` (nothing restorable)."""
    p = UnknownProcedure({'iterations': '100', 'delay': '0.001'})
    assert p.parameter_objects() == {}
    assert p.metadata_objects() == {}
