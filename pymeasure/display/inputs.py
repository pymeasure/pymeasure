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

import logging
import re
from typing import Any, Generic, TypeVar, cast

from pymeasure.experiment.parameters import (
    BooleanParameter,
    FloatParameter,
    IntegerParameter,
    ListParameter,
    Parameter,
    VectorParameter,
)

from .Qt import QtGui, QtWidgets

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


P = TypeVar("P", bound=Parameter)


class Input(Generic[P]):
    """
    Mix-in class that connects a :mod:`Parameter <.parameters>` object to a GUI
    input box.

    :param parameter: The parameter to connect to this input box.
    :attr parameter: Read-only property to access the associated parameter.
    """

    def __init__(self, parameter: P, **kwargs):
        super().__init__(**kwargs)
        self._parameter = None
        self.set_parameter(parameter)

    def set_parameter(self, parameter: P) -> None:
        """
        Connects a new parameter to the input box, and initializes the box
        value.

        :param parameter: parameter to connect.
        """
        self._parameter = parameter

        if parameter.is_set():
            self.setValue(parameter.value)

        if hasattr(parameter, 'units') and parameter.units:
            self.setSuffix(f" {parameter.units}")

        self.setToolTip(parameter._cli_help_fields())

    def update_parameter(self) -> None:
        """
        Update the parameter value with the Input GUI element's current value.
        """
        self._parameter.value = self.value()  # type: ignore

    @property
    def parameter(self) -> P:
        """
        The connected parameter object. Read-only property; see
        :meth:`set_parameter`.

        Note that reading this property will have the side-effect of updating
        its value from the GUI input box.
        """
        self.update_parameter()
        return cast(P, self._parameter)


class StringInput(Input[Parameter[str] | VectorParameter], QtWidgets.QLineEdit):
    """
    String input box connected to a :class:`Parameter`. Parameter subclasses
    that are string-based may also use this input, but non-string parameters
    should use more specialised input classes.
    """

    def __init__(
        self, parameter: Parameter[str], parent: QtWidgets.QWidget | None = None, **kwargs
    ):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def __vector_init__(
        self, parameter: VectorParameter, parent: QtWidgets.QWidget | None = None, **kwargs
    ):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def setValue(self, value: str) -> None:
        # QtWidgets.QLineEdit has a setText() method instead of setValue()
        return super().setText(value)

    def setSuffix(self, value) -> None:
        pass

    def value(self) -> str:
        # QtWidgets.QLineEdit has a text() method instead of value()
        return super().text()


class IntegerInput(Input[IntegerParameter], QtWidgets.QSpinBox):
    """
    Spin input box for integer values, connected to a :class:`IntegerParameter`.
    """

    def __init__(
        self, parameter: IntegerParameter, parent: QtWidgets.QWidget | None = None, **kwargs
    ):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
        if parameter.step:
            self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            self.setSingleStep(parameter.step)
            self.setEnabled(True)
        else:
            self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter: IntegerParameter) -> None:
        # Override from :class:`Input`
        self.setMinimum(parameter.minimum)
        self.setMaximum(parameter.maximum)
        super().set_parameter(parameter)  # default gets set here, after min/max

    def stepEnabled(self):
        if self.parameter.step:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepUpEnabled | \
                QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        else:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepNone


class BooleanInput(Input[BooleanParameter], QtWidgets.QCheckBox):
    """
    Checkbox for boolean values, connected to a :class:`BooleanParameter`.
    """

    def __init__(
        self, parameter: BooleanParameter, parent: QtWidgets.QWidget | None = None, **kwargs
    ):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def set_parameter(self, parameter: BooleanParameter) -> None:
        # Override from :class:`Input`
        self.setText(parameter.name)
        super().set_parameter(parameter)

    def setValue(self, value: bool) -> None:
        return super().setChecked(value)

    def setSuffix(self, value) -> None:
        pass

    def value(self) -> bool:
        return super().isChecked()


class ListInput(Input[ListParameter], QtWidgets.QComboBox):
    """
    Dropdown for list values, connected to a :class:`ListParameter`.
    """

    def __init__(self, parameter: ListParameter, parent: QtWidgets.QWidget | None = None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
        self._stringChoices = None
        self.setEditable(False)

    def set_parameter(self, parameter: ListParameter) -> None:
        # Override from :class:`Input`
        try:
            if hasattr(parameter, 'units') and parameter.units:
                suffix = f" {parameter.units}"
            else:
                suffix = ""

            self._stringChoices = (
                tuple((str(choice) + suffix) for choice in parameter.choices)
                if parameter.choices is not None
                else ()
            )
        except TypeError:  # choices is None
            self._stringChoices = ()
        self.clear()
        self.addItems(self._stringChoices)

        super().set_parameter(parameter)

    def setValue(self, value: Any) -> None:
        try:
            index = self._parameter.choices.index(value)
            self.setCurrentIndex(index)
        except (TypeError, ValueError) as e:  # no choices or choice invalid
            raise ValueError("Invalid choice for parameter. "
                             f"Must be one of {self._parameter.choices!s}") from e

    def setSuffix(self, value) -> None:
        pass

    def value(self) -> Any:
        return self._parameter.choices[self.currentIndex()]


class ScientificInput(Input[FloatParameter], QtWidgets.QDoubleSpinBox):
    """
    Spinner input box for floating-point values, connected to a
    :class:`FloatParameter`. This box will display and accept values in
    scientific notation when appropriate.

    .. seealso::
        Class :class:`~.FloatInput`
            For a non-scientific floating-point input box.
    """

    def __init__(
        self, parameter: FloatParameter, parent: QtWidgets.QWidget | None = None, **kwargs
    ):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
        if parameter.step:
            self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.UpDownArrows)
            self.setSingleStep(parameter.step)
            self.setEnabled(True)
        else:
            self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter: FloatParameter) -> None:
        # Override from :class:`Input`
        self._parameter = parameter  # required before super().set_parameter
        # for self.validate which is called when setting self.decimals()
        self.validator = QtGui.QDoubleValidator(
            parameter.minimum,
            parameter.maximum,
            parameter.decimals,
            self)
        self.setDecimals(parameter.decimals)
        self.setMinimum(parameter.minimum)
        self.setMaximum(parameter.maximum)
        self.validator.setNotation(QtGui.QDoubleValidator.Notation.ScientificNotation)
        super().set_parameter(parameter)  # default gets set here, after min/max

    def validate(self, input: str | None, pos: int) -> tuple[QtGui.QValidator.State, str, int]:
        if input is not None and self._parameter.units:
            input = input[:-(len(self._parameter.units) + 1)]
            result = self.validator.validate(input, pos)
            return result[0], result[1] + f" {self._parameter.units}", result[2]
        else:
            return self.validator.validate(input, pos)

    def fixCase(self, text: str) -> None:
        self.lineEdit().setText(text.lower())

    def toDouble(self, string: str) -> float:
        value, success = self.validator.locale().toDouble(string)
        if not success:
            raise ValueError('String could not be converted to a double')
        else:
            return value

    def toString(self, value: float, format: str = 'g', precision: int = 6) -> str:
        return self.validator.locale().toString(value, format, precision)

    def valueFromText(self, text: str | None) -> float:
        text = str(text)
        if self._parameter.units:
            text = text[:-(len(self._parameter.units) + 1)]
        try:
            val = self.toDouble(text)
        except ValueError:
            val = self._parameter.default
        if val is None:
            val = 0.0
        return val

    def textFromValue(self, v: float) -> str:
        string = self.toString(v).replace("e+", "e")
        string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
        return string

    def stepBy(self, steps):
        value = self.value()
        if self._parameter.step_type == "log":
            sign = 1 if value >= 0 else -1
            self.setValue(value * cast(float, self._parameter.step) ** (sign * steps))
        else:
            super().stepBy(steps)

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

    def __init__(
        self, parameter: VectorParameter, parent: QtWidgets.QWidget | None = None, **kwargs
    ):
        super().__vector_init__(parameter=parameter, parent=parent, **kwargs)

    def setValue(self, value: list[float]) -> None:  # override the method from StringInput
        _value = "[" + ", ".join(map(str, value)) + "]"
        # QtWidgets.QLineEdit has a setText() method instead of setValue()
        return super().setText(_value)
