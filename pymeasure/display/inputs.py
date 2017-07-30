#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

from .Qt import QtCore, QtGui

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Input(QtCore.QObject):
    """ Takes a Parameter object in the constructor and has a
    parameter method
    """

    def __init__(self, parameter):
        super().__init__()
        self._parameter = None
        self.set_parameter(parameter)

    def set_parameter(self, parameter):
        """Connects a parameter to the input box, and initializes the box value.

        :param parameter: parameter to connect.
        :return:
        """
        self._parameter = parameter

        if parameter.default:
            self.setValue(parameter.default)

        if hasattr(parameter, 'units') and parameter.units:
            self.setSuffix(" %s" % parameter.units)

    def update_parameter(self):
        """ Mutates the self._parameter variable to update
        its value
        """
        self._parameter.value = self.value()

    @property
    def parameter(self):
        self.update_parameter()
        return self._parameter


class StringInput(QtGui.QLineEdit, Input):
    def __init__(self, parameter, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        Input.__init__(self, parameter)

    def setValue(self, value):
        # QtGui.QLineEdit has a setText() method instead of setValue()
        return super().setText(value)

    def setSuffix(self, value):
        pass

    def value(self):
        # QtGui.QLineEdit has a text() method instead of value()
        return super().text()


class FloatInput(QtGui.QDoubleSpinBox, Input):
    def __init__(self, parameter, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent)
        Input.__init__(self, parameter)
        self.setMinimum(self._parameter.minimum)
        self.setMaximum(self._parameter.maximum)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)


class IntegerInput(QtGui.QSpinBox, Input):
    def __init__(self, parameter, parent=None):
        QtGui.QSpinBox.__init__(self, parent)
        Input.__init__(self, parameter)
        self.setMinimum(self._parameter.minimum)
        self.setMaximum(self._parameter.maximum)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)


class BooleanInput(object):
    # TODO: Implement this class
    pass


class ListInput(object):
    # TODO: Implement this class
    pass


class ScientificInput(QtGui.QDoubleSpinBox, Input):
    def __init__(self, parameter, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent)
        self.setMinimum(parameter.minimum)
        self.setMaximum(parameter.maximum)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.validator = QtGui.QDoubleValidator(
            parameter.minimum,
            parameter.maximum,
            10, self)
        self.validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
        Input.__init__(self, parameter)

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
        if self._parameter.units:
            return float(str(text)[:-(len(self._parameter.units) + 1)])
        else:
            return float(str(text))

    def textFromValue(self, value):
        string = "{:g}".format(value).replace("e+", "e")
        string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
        return string

    def stepEnabled(self):
        return QtGui.QAbstractSpinBox.StepNone
