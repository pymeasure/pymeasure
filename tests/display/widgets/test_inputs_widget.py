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

from pymeasure.display.Qt import QtCore
from pymeasure.experiment import Procedure, BooleanParameter, Parameter, FloatParameter, \
    IntegerParameter, ListParameter
from pymeasure.display.widgets import InputsWidget


@pytest.mark.parametrize(
    "hide_groups,exp_visible,exp_enabled", [
        (True, False, True),
        (False, True, False),
    ]
)
def test_input_toggling(qtbot, hide_groups, exp_visible, exp_enabled):
    """Test whether the basic toggling works.

    This test is run for both hiding (hide_groups=True) and disabling (hide_groups=False) the
    inputs.
    """

    class TestProcedure(Procedure):
        toggle_par = BooleanParameter('toggle', default=True)
        x = Parameter('X', default='value', group_by='toggle_par')

    wdg = InputsWidget(TestProcedure, inputs=('toggle_par', 'x'), hide_groups=hide_groups)
    qtbot.addWidget(wdg)

    assert wdg.toggle_par.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is True
    assert wdg.x.isEnabled() is True

    qtbot.mouseClick(wdg.toggle_par, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par.height()/2)))

    assert wdg.toggle_par.isChecked() is False
    assert wdg.x.isVisibleTo(wdg) is exp_visible
    assert wdg.x.isEnabled() is exp_enabled

    qtbot.mouseClick(wdg.toggle_par, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par.height()/2)))

    assert wdg.toggle_par.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is True
    assert wdg.x.isEnabled() is True


def test_input_toggling_start_hidden(qtbot):
    """Test whether the basic toggling works.

    This test is run for both hiding (hide_groups=True) and disabling (hide_groups=False) the
    inputs.
    """

    class TestProcedure(Procedure):
        toggle_par = BooleanParameter('toggle', default=False)
        x = Parameter('X', default='value', group_by='toggle_par')

    wdg = InputsWidget(TestProcedure, inputs=('toggle_par', 'x'))
    qtbot.addWidget(wdg)

    assert wdg.toggle_par.isChecked() is False
    assert wdg.x.isVisibleTo(wdg) is False

    qtbot.mouseClick(wdg.toggle_par, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par.height()/2)))

    assert wdg.toggle_par.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is True


def test_input_toggling_multiple_conditions(qtbot):
    """Test if multiple conditions are handled correctly together."""

    class TestProcedure(Procedure):
        toggle_par1 = BooleanParameter('toggle', default=True)
        toggle_par2 = BooleanParameter('toggle', default=False)
        x = Parameter('X', default='value', group_by=['toggle_par1', 'toggle_par2'],
                      group_condition=[True, False])

    wdg = InputsWidget(TestProcedure, inputs=('toggle_par1', 'toggle_par2', 'x'))
    qtbot.addWidget(wdg)

    assert wdg.toggle_par1.isChecked() is True
    assert wdg.toggle_par2.isChecked() is False
    assert wdg.x.isVisibleTo(wdg) is True

    qtbot.mouseClick(wdg.toggle_par1, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par1.height()/2)))

    assert wdg.toggle_par1.isChecked() is False
    assert wdg.toggle_par2.isChecked() is False
    assert wdg.x.isVisibleTo(wdg) is False

    qtbot.mouseClick(wdg.toggle_par2, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par2.height()/2)))

    assert wdg.toggle_par1.isChecked() is False
    assert wdg.toggle_par2.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is False

    qtbot.mouseClick(wdg.toggle_par1, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par1.height()/2)))

    assert wdg.toggle_par1.isChecked() is True
    assert wdg.toggle_par2.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is False

    qtbot.mouseClick(wdg.toggle_par2, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par2.height()/2)))

    assert wdg.toggle_par1.isChecked() is True
    assert wdg.toggle_par2.isChecked() is False
    assert wdg.x.isVisibleTo(wdg) is True


@pytest.mark.parametrize(
    "condition", [
        True,
        False,
    ]
)
def test_input_toggling_boolean(qtbot, condition):
    """Test if a boolean conditions are handled correctly."""

    class TestProcedure(Procedure):
        toggle_par = BooleanParameter('toggle', default=True)
        x = Parameter('X', default='value', group_by='toggle_par', group_condition=condition)

    wdg = InputsWidget(TestProcedure, inputs=('toggle_par', 'x'))
    qtbot.addWidget(wdg)

    assert wdg.toggle_par.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is condition

    qtbot.mouseClick(wdg.toggle_par, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par.height()/2)))

    assert wdg.toggle_par.isChecked() is False
    assert wdg.x.isVisibleTo(wdg) is not condition

    qtbot.mouseClick(wdg.toggle_par, QtCore.Qt.LeftButton,
                     pos=QtCore.QPoint(2, int(wdg.toggle_par.height()/2)))

    assert wdg.toggle_par.isChecked() is True
    assert wdg.x.isVisibleTo(wdg) is condition


@pytest.mark.parametrize(
    "partype,default,condition,kwargs", [
        (Parameter, "default_value", "condition_value", {}),
        (FloatParameter, 0.7, 5.89, {}),
        (IntegerParameter, 3, 5, {}),
        (BooleanParameter, False, True, {}),
        (ListParameter, "default", "condition", {"choices": ["default", "condition"]}),
    ]
)
def test_input_toggling_various_inputs(qtbot, partype, default, condition, kwargs):
    """Test if various input-types are handled correctly for toggling."""

    class TestProcedure(Procedure):
        toggle_par = partype('toggle', default=default, **kwargs)
        x = Parameter('X', default='value', group_by='toggle_par', group_condition=condition)

    wdg = InputsWidget(TestProcedure, inputs=('toggle_par', 'x'))
    qtbot.addWidget(wdg)

    assert wdg.x.isVisibleTo(wdg) is False

    wdg.toggle_par.setValue(condition)

    assert wdg.x.isVisibleTo(wdg) is True

    wdg.toggle_par.setValue(default)

    assert wdg.x.isVisibleTo(wdg) is False


def test_input_toggling_lambda_condition(qtbot):
    """Test if a lambda-function is handled for toggling."""

    class TestProcedure(Procedure):
        toggle_par = IntegerParameter('toggle', default=100)
        x = Parameter('X', default='value', group_by='toggle_par',
                      group_condition=lambda v: 50 < v < 90)

    wdg = InputsWidget(TestProcedure, inputs=('toggle_par', 'x'))
    qtbot.addWidget(wdg)

    assert wdg.x.isVisibleTo(wdg) is False

    wdg.toggle_par.setValue(80)

    assert wdg.x.isVisibleTo(wdg) is True

    wdg.toggle_par.setValue(40)

    assert wdg.x.isVisibleTo(wdg) is False
