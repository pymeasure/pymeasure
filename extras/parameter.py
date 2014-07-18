from PyQt4 import QtGui

class Parameter(QtGui.QDoubleSpinBox):
    def __init__(self, parent=None):
        super(Parameter, self).__init__(parent)
        self.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.validator = QtGui.QDoubleValidator(-1.0e9, 1.0e9, 10, self)
        self.validator.setNotation(QtGui.QDoubleValidator.ScientificNotation)
        self.setMaximum( 10000000000)
        self.setMinimum(-10000000000)

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

if __name__ == '__main__':
    import sys
    app    = QtGui.QApplication(sys.argv)
    sdf = Parameter()
    sdf.setUnit("Blah")
    sdf.show()
    sys.exit(app.exec_())