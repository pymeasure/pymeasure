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
from typing import Any, Callable, Type

from pymeasure.experiment.parameters import Parameter

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

        
class Input(QtWidgets.QWidget):
    """
    Generic class that defines and input QWidget and connects a :mod:`Parameter <.parameters>`
    object to a GUI input box.

    :param parameter: The parameter to connect to this input box.
    :attr parameter: Read-only property to access the associated parameter.
    """
    _widget_type = None
    def __init__(self, parameter: Parameter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_Hover, True)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setAlignment(QtCore.Qt.Alignment.AlignLeft)
        self.layout.setSpacing(0)
        
        if self._widget_type is None:
            raise TypeError("Input must be instantiated as Tool[WidgetType]()")
        self.widget = self._widget_type()
        self.widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        self.layout.addWidget(self.widget)

        self._trailing_layout = QtWidgets.QHBoxLayout()
        self._trailing_layout.setContentsMargins(0,0,0,0)
        self._trailing_layout.setAlignment(QtCore.Qt.Alignment.AlignLeft)
        self._trailing_widget = QtWidgets.QWidget()
        self._trailing_widget.setLayout(self._trailing_layout)
        self._trailing_layout.setSpacing(0)
        self._trailing_widget.setVisible(False)
        self.layout.addWidget(self._trailing_widget)
        
        self._parameter = None
        self.set_parameter(parameter)

        self.reset_button = TrailingButton("⟳", self.reset, "Reset to default")
        self.add_trailing_button(self.reset_button)

    def __class_getitem__(cls, widget_type: Type[QtWidgets.QWidget]):
        class InputWithButtons(cls):
            _widget_type = widget_type
        InputWithButtons.__name__ = f"Input[{widget_type.__name__}]"
        return InputWithButtons
    
    def set_parameter(self, parameter: Parameter) -> None:
        """
        Connects a new parameter to the input box, and initializes the box
        value.

        :param parameter: parameter to connect.
        """
        self._parameter = parameter

        if parameter.is_set():
            self.set_value(parameter.value)
            
        if hasattr(parameter, 'units') and parameter.units:
            self.set_suffix(" %s" % parameter.units)

        self.setToolTip(parameter._cli_help_fields())

    def set_value(self, value: Any) -> None:
        return None

    def set_suffix(self, suffix: Any) -> None:
        return None

    #TODO: add a function value to be implemented in subclasses
    def update_parameter(self) -> None:
        """
        Update the parameter value with the Input GUI element's current value.
        """
        self._parameter.value = self.value()

    def reset(self) -> None:
        if self._parameter.default:
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
    def parameter(self) -> Parameter|None:
        """
        The connected parameter object. Read-only property; see
        :meth:`set_parameter`.

        Note that reading this property will have the side-effect of updating
        its value from the GUI input box.
        """
        self.update_parameter()
        return self._parameter

class StringInput(Input[QtWidgets.QLineEdit]):
    """
    String input box connected to a :class:`Parameter`. Parameter subclasses
    that are string-based may also use this input, but non-string parameters
    should use more specialised input classes.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def set_value(self, value: Any):
        # QtWidgets.QLineEdit has a setText() method instead of setValue()
        return self.widget.setText(value)

    def set_suffix(self, value: Any) -> None:
        return None

    def value(self):
        # QtWidgets.QLineEdit has a text() method instead of value()
        return self.widget.text()


class IntegerInput(Input[QtWidgets.QSpinBox]):
    """
    Spin input box for integer values, connected to a :class:`IntegerParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
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

    def set_suffix(self, suffix):
        self.widget.setSuffix(suffix)

class BooleanInput(Input[QtWidgets.QCheckBox]):
    """
    Checkbox for boolean values, connected to a :class:`BooleanParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self.widget.setText(parameter.name)
        super().set_parameter(parameter)

    def set_value(self, value):
        return self.widget.setChecked(value)

    def set_suffix(self, suffix):
        pass

    def value(self):
        return self.widget.isChecked()


class ListInput(Input[QtWidgets.QComboBox]):
    """
    Dropdown for list values, connected to a :class:`ListParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
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

    def set_suffix(self, suffix):
        pass

    def value(self):
        return self._parameter.choices[self.widget.currentIndex()]
    
class ScientificInput(Input[QtWidgets.QDoubleSpinBox]):
    """
    Spinner input box for floating-point values, connected to a
    :class:`FloatParameter`. This box will display and accept values in
    scientific notation when appropriate.

    .. seealso::
        Class :class:`~.FloatInput`
            For a non-scientific floating-point input box.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
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

    def set_suffix(self, suffix):
        self.widget.setSuffix(suffix)
        
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

    def set_value(self, value):  # override the method from StringInput
        value = "[" + ", ".join(map(str, value)) + "]"
        # QtWidgets.QLineEdit has a setText() method instead of setValue()
        self.widget.setText(value)
