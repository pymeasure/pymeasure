from PyQt4.QtCore import QThread, pyqtSignal, QObject
from threading import Event
import pyqtgraph as pg
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

class BufferCurve(pg.PlotDataItem):
    """ Creates a curve based on a predefined buffer size and allows
    data to be added dynamically, in additon to supporting error bars
    """
    
    dataUpdated = pyqtSignal()
    
    def __init__(self, errors=False, **kwargs):
        pg.PlotDataItem.__init__(self, **kwargs)
        if errors:
            self._errorBars = pg.ErrorBarItem(pen=kwargs.get('pen', None))
        self._buffer = None
        
    def prepare(self, size, dtype=np.float32):
        """ Prepares the buffer based on its size, data type """
        if hasattr(self, '_errorBars'):
            self._buffer = np.empty((size,4), dtype=dtype)
        else:
            self._buffer = np.empty((size,2), dtype=dtype)
        self._ptr = 0
        
    def append(self, x, y, xError=None, yError=None):
        """ Appends data to the curve with optional errors """
        if self._buffer is None:
            raise Exception("BufferCurve buffer must be prepared")
        if len(self._buffer) <= self._ptr:
            raise Exception("BufferCurve overflow")
            
        # Set x-y data
        self._buffer[self._ptr,:2] = [x, y]
        self.setData(self._buffer[:self._ptr,:2])
        
        # Set error bars if enabled at construction
        if hasattr(self, '_errorBars'):
            self._buffer[self._ptr,2:] = [xError, yError]
            self._errorBars.setOpts(
                        x=self._buffer[:self._ptr,0],
                        y=self._buffer[:self._ptr,1],
                        top=self._buffer[:self._ptr,3], 
                        bottom=self._buffer[:self._ptr,3],
                        left=self._buffer[:self._ptr,2],
                        right=self._buffer[:self._ptr,2],
                        beam=np.max(self._buffer[:self._ptr,2:])
                    )
                    
        self._ptr += 1
        self.dataUpdated.emit()
        
class Crosshairs(QObject):
    """ Attaches crosshairs to the a plot and provides a signal with the
    x and y graph coordinates
    """
    
    coordinates = pyqtSignal(float, float)
    
    def __init__(self, plot, pen=None):
        """ Initiates the crosshars onto a plot given the pen style.
        
        Example pen:
        pen=pg.mkPen(color='#AAAAAA', style=QtCore.Qt.DashLine)
        """      
        QObject.__init__(self)
        self.vertical = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.horizontal = pg.InfiniteLine(angle=0, movable=False, pen=pen)
        plot.addItem(self.vertical, ignoreBounds=True)
        plot.addItem(self.horizontal, ignoreBounds=True)
        
        self.position = None
        self.proxy = pg.SignalProxy(plot.scene().sigMouseMoved, rateLimit=60, 
                                    slot=self.mouseMoved)
        self.plot = plot
    
    def hide(self):
        self.vertical.hide()
        self.horizontal.hide()
        
    def show(self):
        self.vertical.show()
        self.horizontal.show()
        
    def update(self):
        """ Updates the mouse position based on the data in the plot. For 
        dynamic plots, this is called each time the data changes to ensure
        the x and y values correspond to those on the display.
        """
        if self.position is not None:
            mousePoint = self.plot.vb.mapSceneToView(self.position)
            self.coordinates.emit(mousePoint.x(), mousePoint.y())
            self.vertical.setPos(mousePoint.x())
            self.horizontal.setPos(mousePoint.y())
            
    def mouseMoved(self, event=None):
        """ Updates the mouse position upon mouse movement """
        if event is not None:
            self.position = event[0]
            self.update()
        else:
            raise Exception("Mouse location not known")
        
