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

from pymeasure.experiment.parameters import Metadata
from pymeasure.experiment.procedure import Procedure


def test_metadata_default():
    p = Metadata('Test', default=5)
    assert p.value == 5


def test_metadata_units():
    p = Metadata('Test', units='tests')
    assert p.units == 'tests'


def test_metadata_formatting():
    p1 = Metadata('Test', default=5.157, units='tests')
    assert str(p1) == "5.157 tests"

    p2 = Metadata('Test', default=5.157, units='tests', fmt="%.1f")
    assert str(p2) == "5.2 tests"


def test_metadata_notset():
    p = Metadata('Test')
    with pytest.raises(ValueError):
        p.value


def test_metadata_object_replacement():
    class TestProcedure(Procedure):
        md = Metadata('Test callable', default=19)

    pr = TestProcedure()
    assert pr.md == 19
    assert pr._metadata["md"].value == 19

    # Manually set another value
    pr.md = 20

    pr.evaluate_metadata()

    # Check if the metadata has been correctly replaced with the new value
    assert pr.md == 20
    assert pr._metadata["md"].value == 20


def test_metadata_fget_evaluation():
    def test_method():
        return "teststring"

    class TestAttribute():
        def callable(self):
            return 84

        @property
        def property(self):
            return 48

    class TestProcedure(Procedure):
        md_callable = Metadata('Test callable', fget=test_method)
        md_str_call = Metadata('Test string callable', fget="callable")
        md_str_prop = Metadata('Test string property', fget="property")
        md_nest_call = Metadata('Test nested callable', fget="atr.callable")
        md_nest_prop = Metadata('Test nested property', fget="atr.property")

        def callable(self):
            return 42

        @property
        def property(self):
            return 24

        atr = TestAttribute()

    pr = TestProcedure()

    # Check if all Metadata have no value yet
    assert not pr._metadata["md_callable"].is_set()
    assert not pr._metadata["md_str_call"].is_set()
    assert not pr._metadata["md_str_prop"].is_set()
    assert not pr._metadata["md_nest_call"].is_set()
    assert not pr._metadata["md_nest_prop"].is_set()

    pr.evaluate_metadata()

    # Check if all Metadata has been correctly evaluated
    assert pr._metadata["md_callable"].value == "teststring"
    assert pr._metadata["md_str_call"].value == 42
    assert pr._metadata["md_str_prop"].value == 24
    assert pr._metadata["md_nest_call"].value == 84
    assert pr._metadata["md_nest_prop"].value == 48
