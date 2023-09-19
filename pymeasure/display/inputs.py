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

import logging

import re

from .Qt import QtGui, QtWidgets

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Input:
    """
    Mix-in class that connects a :mod:`Parameter <.parameters>` object to a GUI
    input box.

    :param parameter: The parameter to connect to this input box.
    :attr parameter: Read-only property to access the associated parameter.
    """

    def __init__(self, parameter, **kwargs):
        super().__init__(**kwargs)
        self._parameter = None
        self.set_parameter(parameter)

    def set_parameter(self, parameter):
        """
        Connects a new parameter to the input box, and initializes the box
        value.

        :param parameter: parameter to connect.
        """
        self._parameter = parameter

        if parameter.is_set():
            try:
                self.setValue(parameter.value)
            except TypeError as e:
                print(f'got type error for parameter: {parameter}. Trying to setValue: {parameter.value}')
                raise e

        if hasattr(parameter, 'units') and parameter.units:
            self.setSuffix(" %s" % parameter.units)

    def update_parameter(self):
        """
        Update the parameter value with the Input GUI element's current value.
        """
        self._parameter.value = self.value()

    @property
    def parameter(self):
        """
        The connected parameter object. Read-only property; see
        :meth:`set_parameter`.

        Note that reading this property will have the side-effect of updating
        its value from the GUI input box.
        """
        self.update_parameter()
        return self._parameter


class StringInput(Input, QtWidgets.QLineEdit):
    """
    String input box connected to a :class:`Parameter`. Parameter subclasses
    that are string-based may also use this input, but non-string parameters
    should use more specialised input classes.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def setValue(self, value):
        # QtWidgets.QLineEdit has a setText() method instead of setValue()
        return super().setText(value)

    def setSuffix(self, value):
        pass

    def value(self):
        # QtWidgets.QLineEdit has a text() method instead of value()
        return super().text()


class FloatInput(Input, QtWidgets.QDoubleSpinBox):
    """
    Spin input box for floating-point values, connected to a
    :class:`FloatParameter`.

    .. seealso::
        Class :class:`~.ScientificInput`
            For inputs in scientific notation.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self.setMinimum(parameter.minimum)
        self.setMaximum(parameter.maximum)
        super().set_parameter(parameter)  # default gets set here, after min/max


class IntegerInput(Input, QtWidgets.QSpinBox):
    """
    Spin input box for integer values, connected to a :class:`IntegerParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self.setMinimum(parameter.minimum)
        self.setMaximum(parameter.maximum)
        super().set_parameter(parameter)  # default gets set here, after min/max


class BooleanInput(Input, QtWidgets.QCheckBox):
    """
    Checkbox for boolean values, connected to a :class:`BooleanParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)

    def set_parameter(self, parameter):
        # Override from :class:`Input`
        self.setText(parameter.name)
        super().set_parameter(parameter)

    def setValue(self, value):
        return super().setChecked(value)

    def setSuffix(self, value):
        pass

    def value(self):
        return super().isChecked()


class ListInput(Input, QtWidgets.QComboBox):
    """
    Dropdown for list values, connected to a :class:`ListParameter`.
    """

    def __init__(self, parameter, parent=None, **kwargs):
        super().__init__(parameter=parameter, parent=parent, **kwargs)
        self._stringChoices = None
        self.setEditable(False)

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
        self.clear()
        self.addItems(self._stringChoices)

        super().set_parameter(parameter)

    def setValue(self, value):
        try:
            index = self._parameter.choices.index(value)
            self.setCurrentIndex(index)
        except (TypeError, ValueError) as e:  # no choices or choice invalid
            raise ValueError("Invalid choice for parameter. "
                             "Must be one of %s" % str(self._parameter.choices)) from e

    def setSuffix(self, value):
        pass

    def value(self):
        return self._parameter.choices[self.currentIndex()]


class ScientificInput(Input, QtWidgets.QDoubleSpinBox):
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
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

    def set_parameter(self, parameter):
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

    def validate(self, text, pos):
        if self._parameter.units:
            text = text[:-(len(self._parameter.units) + 1)]
            result = self.validator.validate(text, pos)
            return result[0], result[1] + " %s" % self._parameter.units, result[2]
        else:
            return self.validator.validate(text, pos)

    def fixCase(self, text):
        self.lineEdit().setText(text.toLower())

    def valueFromText(self, text):
        try:
            if self._parameter.units:
                return float(str(text)[:-(len(self._parameter.units) + 1)])
            else:
                return float(str(text))
        except ValueError:
            return self._parameter.default

    def textFromValue(self, value):
        string = f"{value:g}".replace("e+", "e")
        string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
        return string

    def stepEnabled(self):
        if hasattr(QtWidgets.QAbstractSpinBox, 'StepNone'):
            return QtWidgets.QAbstractSpinBox.StepNone
        else:
            return QtWidgets.QAbstractSpinBox.StepEnabledFlag.StepNone
