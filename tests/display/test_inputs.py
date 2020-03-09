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
from unittest import mock

from pymeasure.display.Qt import QtGui, QtCore
from pymeasure.display.inputs import ScientificInput, BooleanInput, ListInput
from pymeasure.experiment.parameters import BooleanParameter, ListParameter, FloatParameter

@pytest.mark.parametrize("default_value", [True, False])
class TestBooleanInput:
    def test_init_from_param(self, qtbot, default_value):
        # set up BooleanInput
        bool_param = BooleanParameter('potato', default=default_value)
        bool_input = BooleanInput(bool_param)
        qtbot.addWidget(bool_input)

        # test
        assert bool_input.text() == bool_param.name
        assert bool_input.value() == default_value


    def test_setValue_should_update_value(self, qtbot, default_value):

        # set up BooleanInput
        bool_param = BooleanParameter('potato', default=default_value)
        bool_input = BooleanInput(bool_param)
        qtbot.addWidget(bool_input)

        bool_input.setValue(not default_value)
        assert bool_input.value() == (not default_value)


    def test_leftclick_should_update_parameter(self, qtbot, default_value):
        # set up BooleanInput
        bool_param = BooleanParameter('potato', default=default_value)

        with mock.patch('test_inputs.BooleanParameter.value',
                new_callable=mock.PropertyMock,
                return_value=default_value) as p:
            bool_input = BooleanInput(bool_param)
            qtbot.addWidget(bool_input)
            bool_input.show()

            # TODO: fix: fails to toggle on Windows
            #qtbot.mouseClick(bool_input, QtCore.Qt.LeftButton)
            bool_input.setValue(not default_value)

            assert bool_input.value() == (not default_value)
            bool_input.parameter # lazy update
            p.assert_called_once_with(not default_value)


class TestListInput:
    @pytest.mark.parametrize("choices,default_value", [
        (["abc", "def", "ghi"], "abc"), # strings
        ([123, 456, 789], 123), # numbers
        (["abc", "def", "ghi"], "def") # default not first value
    ])
    def test_init_from_param(self, qtbot, choices, default_value):
        list_param = ListParameter('potato',
                choices=choices,
                default=default_value,
                units='m')
        list_input = ListInput(list_param)
        qtbot.addWidget(list_input)

        assert list_input.isEditable() == False
        assert list_input.value() == default_value

    def test_setValue_should_update_value(self, qtbot):
        # Test write-read loop: verify value -> index -> value conversion
        choices = [123, 'abc', 0]
        list_param = ListParameter('potato', choices=choices, default=123)
        list_input = ListInput(list_param)
        qtbot.addWidget(list_input)

        for choice in choices:
            list_input.setValue(choice)
            assert list_input.currentText() == str(choice)
            assert list_input.value() == choice

    def test_setValue_should_update_parameter(self, qtbot):
        choices = [123, 'abc', 0]
        list_param = ListParameter('potato', choices=choices, default=123)
        list_input = ListInput(list_param)
        qtbot.addWidget(list_input)

        with mock.patch('test_inputs.ListParameter.value',
                new_callable=mock.PropertyMock,
                return_value=123) as p:
            for choice in choices:
                list_input.setValue(choice)
                list_input.parameter # lazy update
            p.assert_has_calls((mock.call(123), mock.call('abc'), mock.call(0)))


    def test_unit_should_append_to_strings(self, qtbot):
        list_param = ListParameter('potato', choices=[123, 456], default=123, units='m')
        list_input = ListInput(list_param)
        qtbot.addWidget(list_input)

        assert list_input.currentText() == '123 m'


    def test_set_invalid_value_should_raise(self, qtbot):
        list_param = ListParameter('potato', choices=[123, 456], default=123, units='m')
        list_input = ListInput(list_param)
        qtbot.addWidget(list_input)
        with pytest.raises(ValueError):
            list_input.setValue(789)

class TestScientificInput:
    @pytest.mark.parametrize("min_,max_,default_value", [
        [0, 20, 12],
        [0, 1000, 200], # regression #118: default above default max 99.99
        [-1000, 1000, -10] # regression #118: default below default min 0
    ])
    def test_init_from_param(self, qtbot, min_, max_, default_value):
        float_param = FloatParameter('potato',
                minimum=min_,
                maximum=max_,
                default=default_value,
                units='m')
        sci_input = ScientificInput(float_param)
        qtbot.addWidget(sci_input)

        assert sci_input.minimum() == min_
        assert sci_input.maximum() == max_
        assert sci_input.value() == default_value
        assert sci_input.suffix() == ' m'

    def test_setValue_within_range_should_set(self, qtbot):
        float_param = FloatParameter('potato',
            minimum=-10, maximum=10, default=0)
        sci_input = ScientificInput(float_param)
        qtbot.addWidget(sci_input)

        # test
        sci_input.setValue(5)
        assert sci_input.value() == 5

    def test_setValue_within_range_should_set_regression_118(self, qtbot):
        float_param = FloatParameter('potato',
            minimum=-1000, maximum=1000, default=0)
        sci_input = ScientificInput(float_param)
        qtbot.addWidget(sci_input)

        # test - validate min/max beyond QDoubleSpinBox defaults
        # QDoubleSpinBox defaults are 0 to 99.9 - so test value >= 100
        sci_input.setValue(999)
        assert sci_input.value() == 999

        sci_input.setValue(-999)
        assert sci_input.value() == -999

    def test_setValue_out_of_range_should_constrain(self, qtbot):
        float_param = FloatParameter('potato',
            minimum=-1000, maximum=1000, default=0)
        sci_input = ScientificInput(float_param)
        qtbot.addWidget(sci_input)

        # test
        sci_input.setValue(1024)
        assert sci_input.value() == 1000

        sci_input.setValue(-1024)
        assert sci_input.value() == -1000

    def test_setValue_should_update_param(self, qtbot):
        float_param = FloatParameter('potato',
            minimum=-1000, maximum=1000, default=10.0)
        sci_input = ScientificInput(float_param)
        qtbot.addWidget(sci_input)

        with mock.patch('test_inputs.FloatParameter.value',
                new_callable=mock.PropertyMock,
                return_value=10.0) as p:
            # test
            sci_input.setValue(5.0)
            sci_input.parameter # lazy update
            p.assert_called_once_with(5.0)
