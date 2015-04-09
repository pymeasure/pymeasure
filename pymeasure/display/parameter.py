#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands
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

from qt_variant import QtGui


class Parameter(QtGui.QDoubleSpinBox):

    def __init__(self, parent=None):
        super(Parameter, self).__init__(parent)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.validator = QtGui.QDoubleValidator(-1.0e9, 1.0e9, 10, self)
        self.validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
        self.setMaximum(1e12)
        self.setMinimum(-1e12)

        # This is the physical unit associated with this value
        self.unit = ""

    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def fixCase(self, text):
        self.lineEdit().setText(text.toLower())

    def valueFromText(self, text):
        return float(str(text))

    def textFromValue(self, value):
        # return "%.*g" % (self.decimals(), value)
        return "%.4g" % (value)

    def stepEnabled(self):
        return QtGui.QAbstractSpinBox.StepNone

    def __str__(self):
        return "%.4g %s" % (self.value(), self.unit)

    def setUnit(self, string):
        self.unit = string
        self.setProperty("unit", string)

    def getUnit(self):
        self.unit = self.property("unit").toString()
        return self.unit
