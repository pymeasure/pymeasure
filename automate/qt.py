#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic functions/classes for Qt applications
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
from PyQt4.QtGui import QPlainTextEdit, QDoubleSpinBox, QAbstractSpinBox, QDoubleValidator
from PyQt4.QtGui import QTreeWidget

def runInIPython(app):
    """ Attempts to run the QApplication in the IPython main loop, which
    requires the command "%gui qt" to be run prior to the script execution.
    On failure the Qt main loop is initialized instead
    """
    try:
        from IPython.lib.guisupport import start_event_loop_qt4
        start_event_loop_qt4(app)
    except ImportError:
        app.exec_()
        
class QManagerView(QTreeWidget):
    def __init__(self, manager):
        super(QManagerView, self).__init__()
        
        self.manager = manager

        # Have the Manager use this class' methods as callbacks
        self.manager.running  = self.running
        self.manager.finished = self.finished
        self.manager.failed   = self.failed
        self.manager.aborted  = self.aborted
        self.manager.modified = self.modified

    def modified(self):
        """Update the local copy of the queue and render"""
        manager_items = self.manager._queue
    
class QLogHandler(logging.Handler):
    
    def __init__(self, log_display):
        super(QLogHandler, self).__init__()
        if not isinstance(log_display, QPlainTextEdit):
            raise Exception("QLogHandler is only implemented for QPlainTextEdit objects")
        self.log_display = log_display
    
    def emit(self, record):
        self.log_display.appendPlainText(self.format(record))

class Parameter(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(Parameter, self).__init__(parent)
        self.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.validator = QDoubleValidator(-1.0e9, 1.0e9, 10, self)
        self.validator.setNotation(QDoubleValidator.ScientificNotation)
        self.setMaximum( 1e12)
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
        return QAbstractSpinBox.StepNone

    def __str__(self):
        return "%.4g %s" % (self.value(), self.unit)

    def setUnit(self, string):
        self.unit = string
        self.setProperty("unit", string)

    def getUnit(self):
        self.unit = self.property("unit").toString()
        return self.unit