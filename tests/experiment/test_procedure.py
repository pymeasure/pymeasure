#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import pickle

from pymeasure.experiment.procedure import Procedure, ProcedureWrapper
from pymeasure.experiment.parameters import Parameter

from data.procedure_for_testing import RandomProcedure


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
            assert(isinstance(self.x, int))
            return self.x

        @property
        def z(self):
            assert(isinstance(self.x, int))
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
