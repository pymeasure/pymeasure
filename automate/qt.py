#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic functions/classes for Qt applications
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import logging
from PyQt4.QtGui import QPlainTextEdit

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
        
    
class QLogHandler(logging.Handler):
    
    def __init__(self, log_display):
        super(QLogHandler, self).__init__()
        if not isinstance(log_display, QPlainTextEdit):
            raise Exception("QLogHandler is only implemented for QPlainTextEdit objects")
        self.log_display = log_display
    
    def emit(self, record):
        self.log_display.appendPlainText(self.format(record))

