from PyQt4.QtCore import QThread, pyqtSignal
from threading import Event
import numpy as np
import datetime as dt

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

class MeasurementThread(QThread):
    """ Encapsulates a synchronous measurement procedure into a threaded
    object that provides convenient features for thread control
    """
    
    logger = pyqtSignal(dt.datetime, str)
    
    def __init__(self):
        QThread.__init__(self)
        self.alive = Event()
        self.alive.set()
    
    def isAlive(self):
        """ Returns True if the measurement thread is alive """
        return self.alive.isSet()
        
    def abort(self, delay=100):
        """ Aborts the execution of the thread and waits for a specific
        time in milliseconds for the procedure to catch the abort and finish
        """
        if delay < 0:
            raise ValueError("MeasurementThread abort delay time must be "
                             "positive")
        self.alive.clear()
        self.wait(int(delay))
        
    def procedure(self):
        """ Method to be overwritten with the measurement procedure """
        pass
        
    def onException(self):
        """ Method to be overwritten which handles an exception in the
        procedure method
        """
        pass
        
    def log(self, message):
        """ Emits a log message with the current date and time """
        self.logger.emit(dt.now(), message)
        
    def run(self):
        """ Runs the procedure and ensures that exceptions are handled and
        printed to standard output with full traceback
        """
        try:
            self.procedure()
        except:
            self.onException()
            import traceback
            traceback.print_exc()


