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

import logging

import re
from typing import Any, Callable, Generic, Literal, TypeVar, Union

from pymeasure.experiment.parameters import BooleanParameter, FloatParameter, IntegerParameter, ListParameter, Parameter, PhysicalParameter
from pyqtgraph import SpinBox

from .Qt import QtGui, QtWidgets, QtCore

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class TrailingButton(QtWidgets.QPushButton):
    def __init__(self, glyph: str, slot: Callable, tooltip: str, *args, **kwargs) -> None:
        super().__init__(glyph, *args, **kwargs)
        self.setStyleSheet(
            """
            QPushButton {
            background: transparent;
            border: none;
            color: lightgray;
            }
            
            QPushButton:hover {
            color: black;
            }
            """
        )
        self.setFixedWidth(20)
        self.setToolTip(tooltip)
        self.clicked.connect(slot)
        
P = TypeVar("P", bound=Parameter)
Q = TypeVar("Q", bound=QtWidgets.QWidget)

class Input(QtWidgets.QWidget, Generic[P, Q]):
    """
    Generic class that defines and input QWidget and connects a :mod:`Parameter <.parameters>`
    object to a GUI input box.

    :param parameter: The parameter to connect to this input box.
    :attr parameter: Read-only property to access the associated parameter.
    """
    def __init__(self, widget: Q, parameter: P, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)

        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)
        self._layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self._layout.setSpacing(0)

        self.widget = widget
        self.widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        self._layout.addWidget(self.widget)

        self._trailing_layout = QtWidgets.QHBoxLayout()
        self._trailing_layout.setContentsMargins(0,0,0,0)
        self._trailing_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._trailing_widget = QtWidgets.QWidget()
        self._trailing_widget.setLayout(self._trailing_layout)
        self._trailing_layout.setSpacing(0)
        self._trailing_widget.setVisible(False)
        self._layout.addWidget(self._trailing_widget)
        
        self._parameter = None
        self.set_parameter(parameter)

        self.reset_button = TrailingButton("⟳", self.reset, "Reset to default")
        self.add_trailing_button(self.reset_button)
    
    def set_parameter(self, parameter: P) -> None:
        """
        Connects a new parameter to the input, and initializes the input
        value.

        :param parameter: parameter to connect.
        """
        self._parameter = parameter

        if parameter.is_set():
            self.set_value(parameter.value)
            
        if hasattr(parameter, 'units') and parameter.units:
            self.set_units(" %s" % parameter.units)

        self.setToolTip(parameter._cli_help_fields())
        
    def set_value(self, value) -> None:
        return None

    def set_units(self, units: str) -> None:
        return None

    def get_value(self) -> Any:
        return None

    def update_parameter(self) -> None:
        """
        Update the parameter value with the Input GUI element's current value.
        """
        self._parameter.value = self.get_value()

    def reset(self) -> None:
        if self._parameter.default is not None:
            self.set_value(self._parameter.default)

    def add_trailing_button(self, button: TrailingButton) -> None:
        self._trailing_layout.addWidget(button)
    
    def event(self, e: QtCore.QEvent):
        if e.type() == QtCore.QEvent.Type.HoverEnter:
            self._trailing_widget.setVisible(True)
        elif e.type() == QtCore.QEvent.Type.HoverLeave:
            self._trailing_widget.setVisible(False)
        return super().event(e)
        
    @property
    def parameter(self) -> Union[Parameter, None]:
        """
        The connected parameter object. Read-only property; see
        :meth:`set_parameter`.

        Note that reading this property will have the side-effect of updating
        its value from the GUI input box.
        """
        self.update_parameter()
        return self._parameter

class StringInput(Input[Parameter, QtWidgets.QLineEdit]):
    """
    String input box connected to a :class:`Parameter`. Parameter subclasses
    that are string-based may also use this input, but non-string parameters
    should use more specialised input classes.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(widget=QtWidgets.QLineEdit(), parameter=parameter, parent=parent, **kwargs)
        
    def set_value(self, value: str) -> None:
        return self.widget.setText(value)

    def set_units(self, units: str) -> None:
        return None

    def get_value(self) -> Any:
        return self.widget.text()


class IntegerInput(Input[IntegerParameter, QtWidgets.QSpinBox]):
    """
    Spin input box for integer values, connected to a :class:`IntegerParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(widget = QtWidgets.QSpinBox(), parameter=parameter, parent=parent, **kwargs)
        if parameter.step:
            self.widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            self.widget.setSingleStep(parameter.step)
            self.widget.setEnabled(True)
        else:
            self.widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self.widget.setMinimum(parameter.minimum)
        self.widget.setMaximum(parameter.maximum)
        super().set_parameter(parameter)  # default gets set here, after min/max

    def stepEnabled(self):
        if self.parameter.step:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled | \
                QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        else:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepNone

    def set_value(self, value):
        self.widget.setValue(value)

    def set_units(self, units: str) -> None:
        self.widget.setSuffix(units)

    def get_value(self) -> int:
        return self.widget.value()

class BooleanInput(Input[BooleanParameter, QtWidgets.QCheckBox]):
    """
    Checkbox for boolean values, connected to a :class:`BooleanParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(widget=QtWidgets.QCheckBox(), parameter=parameter, parent=parent, **kwargs)
    
    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self.widget.setText(parameter.name)
        super().set_parameter(parameter)

    def set_value(self, value) -> None:
        self.widget.setChecked(value)

    def set_units(self, units: str) -> None:
        pass

    def get_value(self) -> Any:
        return self.widget.isChecked()


class ListInput(Input[ListParameter, QtWidgets.QComboBox]):
    """
    Dropdown for list values, connected to a :class:`ListParameter`.
    """

    def __init__(self, parameter: ListParameter, parent=None, **kwargs):
        super().__init__(widget=QtWidgets.QComboBox(), parameter=parameter, parent=parent, **kwargs)
        self._stringChoices = None
        self.widget.setEditable(False)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        try:
            if hasattr(parameter, 'units') and parameter.units:
                suffix = " %s" % parameter.units
            else:
                suffix = ""

            self._stringChoices = tuple((str(choice) + suffix) for choice in parameter.choices)
        except TypeError:  # choices is None
            self._stringChoices = tuple()
        self.widget.clear()
        self.widget.addItems(self._stringChoices)
        super().set_parameter(parameter)

    def set_value(self, value):
        try:
            index = self._parameter.choices.index(value)
            self.widget.setCurrentIndex(index)
        except (TypeError, ValueError) as e:  # no choices or choice invalid
            raise ValueError("Invalid choice for parameter. "
                             "Must be one of %s" % str(self._parameter.choices)) from e

    def set_units(self, units: str) -> None:
        pass

    def get_value(self):
        return self._parameter.choices[self.widget.currentIndex()]
    
class ScientificInput(Input[FloatParameter, QtWidgets.QDoubleSpinBox]):
    """
    Spinner input box for floating-point values, connected to a
    :class:`FloatParameter`. This box will display and accept values in
    scientific notation when appropriate.

    .. seealso::
        Class :class:`~.FloatInput`
            For a non-scientific floating-point input box.
    """

    def __init__(self, parameter: FloatParameter, parent=None, **kwargs):
        super().__init__(widget=QtWidgets.QDoubleSpinBox(), parameter=parameter, parent=parent, **kwargs)
        if parameter.step:
            self.widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            self.widget.setSingleStep(parameter.step)
            self.widget.setEnabled(True)
        else:
            self.widget.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self._parameter = parameter  # required before super().set_parameter
        # for self.validate which is called when setting self.decimals()
        self.validator = QtGui.QDoubleValidator(
            parameter.minimum,
            parameter.maximum,
            parameter.decimals,
            self)
        self.widget.setDecimals(parameter.decimals)
        self.widget.setMinimum(parameter.minimum)
        self.widget.setMaximum(parameter.maximum)
        self.validator.setNotation(QtGui.QDoubleValidator.Notation.ScientificNotation)
        super().set_parameter(parameter)  # default gets set here, after min/max

    def set_value(self, value):
        self.widget.setValue(value)

    def set_units(self, units: str) -> None:
        self.widget.setSuffix(units)

    def get_value(self) -> Any:
        return self.widget.value()
    
    def validate(self, text, pos):
        if self._parameter.units:
            text = text[:-(len(self._parameter.units) + 1)]
            result = self.validator.validate(text, pos)
            return result[0], result[1] + " %s" % self._parameter.units, result[2]
        else:
            return self.validator.validate(text, pos)

    def fixCase(self, text):
        self.widget.lineEdit().setText(text.toLower())

    def toDouble(self, string):
        value, success = self.validator.locale().toDouble(string)
        if not success:
            raise ValueError('String could not be converted to a double')
        else:
            return value

    def toString(self, value, format='g', precision=6):
        return self.validator.locale().toString(value, format, precision)

    def valueFromText(self, text):
        text = str(text)
        if self._parameter.units:
            text = text[:-(len(self._parameter.units) + 1)]
        try:
            val = self.toDouble(text)
        except ValueError:
            val = self._parameter.default
        return val

    def textFromValue(self, value):
        string = self.toString(value).replace("e+", "e")
        string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
        return string

    def stepEnabled(self):
        if self.parameter.step:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled | \
                QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        else:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepNone


class VectorInput(StringInput):
    """
    String input box connected to a :class:`VectorParameter`. This box will
    display and accept lists.
    """
    #TODO: Turn this into an editable list with item delegates
    def set_value(self, value):  # override the method from StringInput
        value = "[" + ", ".join(map(str, value)) + "]"
        # QtWidgets.QLineEdit has a setText() method instead of setValue()
        self.widget.setText(value)

class UncertaintyWidget(QtWidgets.QWidget):
    _uncertainty_type: Literal["absolute", "relative", "percentage"]
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.h_layout.setContentsMargins(0,0,0,0)
        
        self._uncertainty_type = "absolute"
        self._units = ""

        self.quant_spin_box = SpinBox()
        self.quant_spin_box.setFixedHeight(23)
        self.h_layout.addWidget(self.quant_spin_box)

        self.pm_label = QtWidgets.QLabel("±")
        self.h_layout.addWidget(self.pm_label)

        self.uncert_spin_box = SpinBox()
        self.uncert_spin_box.setFixedHeight(23)
        self.h_layout.addWidget(self.uncert_spin_box)

    @property
    def uncertainty_type(self) -> Literal["absolute", "relative", "percentage"]:
        return self._uncertainty_type

    @uncertainty_type.setter
    def uncertainty_type(self, value: Literal["absolute", "relative", "percentage"]):
        if value == "absolute":
            self.uncert_spin_box.setSuffix(self._units)
        elif value == "percentage":
            self.uncert_spin_box.setSuffix("%")
        elif value == "relative":
            self.uncert_spin_box.setSuffix("")
        else:
            raise ValueError("Uncertainty type must be absolute, relative, or percentage!")
        
        self._uncertainty_type = value
    
    def set_value(self, value: list):
        self.quant_spin_box.setValue(value[0])
        self.uncert_spin_box.setValue(value[1])
        
    def get_value(self) -> list:
        return [self.quant_spin_box.value(), self.uncert_spin_box.value()]

    def set_units(self, units: str):
        self._units = units
        self.quant_spin_box.setSuffix(units)
        
class UncertQuantInput(Input[PhysicalParameter, UncertaintyWidget]):
    _default_uncert: Literal["absolute", "relative", "percentage"]
    
    def __init__(self, parameter: PhysicalParameter, *args, **kwargs):
        super().__init__(UncertaintyWidget(), parameter, *args, **kwargs)
        self.pm_button = TrailingButton("±", self._change_uncert_type, "Change uncertainty type")
        self.add_trailing_button(self.pm_button)
        self.widget.setMinimumHeight(22)
        
    def set_value(self, value: list):
        self.widget.set_value(value)

    def set_parameter(self, parameter: PhysicalParameter) -> None:
        parameter.uncertainty_type = self.widget.uncertainty_type
        self._default_uncert = parameter.uncertainty_type
        super().set_parameter(parameter)

    def reset(self) -> None:
        self.widget.uncertainty_type = self._default_uncert
        super().reset()

    def set_units(self, units: str) -> None:
        self.widget.set_units(units)

    def get_value(self) -> Any:
        return self.widget.get_value()

    def _change_uncert_type(self) -> None:
        if self.widget.uncertainty_type == "absolute":
            self.widget.uncertainty_type = "percentage"
            curr_val = self.widget.get_value()
            self.widget.set_value([curr_val[0], curr_val[1]/curr_val[0]*100])
        else:
            self.widget.uncertainty_type = "absolute"
            curr_val = self.widget.get_value()
            self.widget.set_value([curr_val[0], curr_val[0]*curr_val[1]/100])

