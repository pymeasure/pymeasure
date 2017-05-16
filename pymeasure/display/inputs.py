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

from .Qt import QtCore, QtGui
import re


class Input(QtCore.QObject):
    """ Takes a Parameter object in the constructor and has a
    parameter method
    """ 
    
    def __init__(self, parameter):
        self.set_parameter(parameter)

    def set_parameter(self, parameter):
        self._parameter = parameter

    def update_parameter(self):
        """ Mutates the self._parameter variable to update
        its value
        """
        pass

    @property
    def parameter(self):
        self.update_parameter()
        return self._parameter


class StringInput(QtGui.QLineEdit, Input):
    
    def __init__(self, parameter, parent=None):
        QtGui.QLineEdit.__init__(self, parent=parent)
        Input.__init__(self, parameter)
        if self._parameter.default:
            self.setText(self._parameter.default)

    def set_parameter(self, parameter):
        super(StringInput, self).set_parameter(parameter)
        self.setText(parameter.value)

    def update_parameter(self):
        self._parameter.value = self.text()


class FloatInput(QtGui.QDoubleSpinBox, Input):
    
    def __init__(self, parameter, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent=parent)
        Input.__init__(self, parameter)
        self.setMinimum(self._parameter.minimum)
        self.setMaximum(self._parameter.maximum)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        if self._parameter.default:
            self.setValue(self._parameter.default)
        if self._parameter.units:
            self.setSuffix(" %s" % self._parameter.units)

    def set_parameter(self, parameter):
        super(FloatInput, self).set_parameter(parameter)
        self.setValue(parameter.value)

    def update_parameter(self):
        self._parameter.value = self.value()


class IntegerInput(QtGui.QSpinBox, Input):
    
    def __init__(self, parameter, parent=None):
        QtGui.QSpinBox.__init__(self, parent=parent)
        Input.__init__(self, parameter)
        self.setMinimum(self._parameter.minimum)
        self.setMaximum(self._parameter.maximum)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        if self._parameter.default:
            self.setValue(self._parameter.default)
        if self._parameter.units:
            self.setSuffix(" %s" % self._parameter.units)

    def set_parameter(self, parameter):
        super(IntegerInput, self).set_parameter(parameter)
        self.setValue(parameter.value)

    def update_parameter(self):
        self._parameter.value = self.value()


class BooleanInput():
    # TODO: Implement this class
    pass


class ListInput():
    # TODO: Implement this class
    pass


class ScientificInput(QtGui.QDoubleSpinBox, Input):

    def __init__(self, parameter, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent=parent)
        self.setMinimum(parameter.minimum)
        self.setMaximum(parameter.maximum)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.validator = QtGui.QDoubleValidator(
            parameter.minimum,
            parameter.maximum,
            10, self)
        self.validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
        Input.__init__(self, parameter)
        if self._parameter.default:
            self.setValue(self._parameter.default)
        if self._parameter.units:
            self.setSuffix(" %s" % self._parameter.units)

    def set_parameter(self, parameter):
        super(ScientificInput, self).set_parameter(parameter)
        self.setValue(parameter.value)

    def update_parameter(self):
        self._parameter.value = self.value()

    def validate(self, text, pos):
        if self._parameter.units:
            text = text[:-(len(self._parameter.units) + 1)]
            result = self.validator.validate(text, pos)
            return (result[0], result[1] + " %s" % self._parameter.units, result[2])
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
