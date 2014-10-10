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
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QProgressBar, QPixmap, QIcon, QColor
from PyQt4.QtCore import QObject, pyqtSignal, Qt
from os.path import basename
from automate.experiment import Procedure, QProcedureThread, Experiment
from automate.listeners import QResultsWriter
from automate.qtgraph import ResultsCurve

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


class Manager(QObject):

    experiments = []
    _is_continuous = True
    _start_on_add = True
    _running_thread = None
    queued = pyqtSignal(object)
    running = pyqtSignal(object)
    finished = pyqtSignal(object)
    failed = pyqtSignal(object)
    aborted = pyqtSignal(object)
    abort_returned = pyqtSignal(object)

    def __init__(self, plot, browser, parent=None):
        super(Manager, self).__init__(parent=parent)
        self.plot = plot
        self.browser = browser
    
    def isRunning(self):
        """ Returns True if a procedure is currently running
        """
        return self._running_thread != None
        
    def runningExperiment(self):
        """ Returns the results object of the running procedure
        """
        for experiment in self.experiments:
            if experiment.procedure.status == Procedure.RUNNING:
                return experiment
        return None
        
    def queuedExperiments(self):
        """ Returns the procedures which are queued
        """
        queued = []
        for experiment in self.experiments:
            if experiment.procedure.status == Procedure.QUEUED:
                queued.append(experiment)
        return queued
        
    def hasQueuedExperiments(self):
        return len(self.queuedExperiments()) > 0
    
    def filePaths(self):
        """ Returns a list of file paths for the Experiments in the Manager
        """
        return [experiment.results.data_filename for experiment in self.experiments]
                
    def queue(self, experiment):
        self.load(experiment)
        self.queued.emit(experiment)
        if self._start_on_add and not self.isRunning():
            self.next()
            
    def load(self, experiment):
        self.plot.addItem(experiment.curve)
        self.browser.add(experiment)
        
        self.experiments.append(experiment)
            
    def next(self):
        """ Initiates the start of the next experiment in the queue as long
        as no other experiments is currently running and there is a procedure
        in the queue
        """
        if self.isRunning():
            raise Exception("Another procedure is already running")
        else:
            queued = self.queuedExperiments()
            if len(queued) == 0:
                return
                #raise Exception("No experiments are queued to be run")
            else:
                experiment = queued[0]
                index = self.experiments.index(experiment)
                
                self._running_thread = QProcedureThread(parent=self)
                self._running_thread.load(experiment.procedure)
                self._running_thread.finished.connect(self._callback)
                
                self._data_writer = QResultsWriter(experiment.results)
                self._running_thread.data.connect(self._data_writer.write)
                
                self._running_thread.progress.connect(experiment.browser_item.progressbar.setValue)
                self._running_thread.status_changed.connect(experiment.browser_item.setStatus)
                
                self._data_writer.start()
                self._running_thread.start()
                self.running.emit(experiment)
    
    def resume(self):
        self._start_on_add = True
        self._continous = True
        self.next()
        
    def remove(self, experiment):
        """ Removes the Experiment from the Manager, unless it is currently running
        """
        if not experiment in self.experiments:
            raise Exception("Attempting to remove an Experiemnt that is not in the Manager")
        else:
            if self.isRunning() and experiment == self.runningExperiment():
                raise Exception("Attempting to remove the currently running experiment")
            else:
                self.browser.takeTopLevelItem(self.browser.indexOfTopLevelItem(experiment.browser_item))
                self.plot.removeItem(experiment.curve)
                self.experiments.pop(self.experiments.index(experiment))
               
    def clear(self):
        for experiment in self.experiments[:]:
            self.remove(experiment)
    
    def abort(self):
        """ Aborts the currently running experiment, but raises an exception if
        there is no running experiment
        """    
        if not self.isRunning():
            raise Exception("Attempting to abort when no experiment is running")
        else:
            self._start_on_add = False
            self._continous = False
        
            self._running_thread.abort()
            self._data_writer.join()
            
            self.aborted.emit(self.experimentFromProcedure(self._running_thread.procedure))
        
    def _callback(self):
        """ Handles the different cases upon which the running procedure thread
        can call back
        """
        for experiment in self.experiments:
            if experiment.procedure == self._running_thread.procedure:
                break
        self._running_thread = None
        self._data_writer = None
        if experiment.procedure.status == Procedure.FAILED:
            self.failed.emit(experiment)
        elif experiment.procedure.status == Procedure.ABORTED:
            self.abort_returned.emit(experiment)
        elif experiment.procedure.status == Procedure.FINISHED:
            self.finished.emit(experiment)
            if self._is_continuous: # Continue running procedures
                self.next()
            
    def experimentFromBrowserItem(self, browser_item):
        for experiment in self.experiments:
            if experiment.browser_item == browser_item:
                return experiment
        raise Exception("This BrowserItem did not match any Experiments in the Manager")
        
    def experimentFromProcedure(self, procedure):
        for experiment in self.experiments:
            if experiment.procedure == procedure:
                return experiment
        raise Exception("This Procedure did not match any Experiments in the Manager")
        
    
class BrowserItem(QTreeWidgetItem):
    
    def __init__(self, results, curve, parent=None):
        super(BrowserItem, self).__init__(parent)
        
        pixelmap = QPixmap(24, 24)
        pixelmap.fill(curve.opts['pen'].color())
        self.setIcon(0, QIcon(pixelmap))
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(0, 2)
        self.setText(1, basename(results.data_filename))
        
        self.setStatus(results.procedure.status)
        
        self.progressbar = QProgressBar()
        self.progressbar.setRange(0,100)
        self.progressbar.setValue(0)    
    
    def setStatus(self, status):
        status_label = {
            Procedure.QUEUED: 'Queued', Procedure.RUNNING: 'Running',
            Procedure.FAILED: 'Failed', Procedure.ABORTED: 'Aborted', 
            Procedure.FINISHED: 'Finished'}
        self.setText(3, status_label[status])
        
        if status == Procedure.FAILED or status == Procedure.ABORTED:
            # Set progress bar color to red
            return # Commented this out
            self.progressbar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #AAAAAA;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: red;
            }
            """)
            


class ExperimentBrowser(QTreeWidget):
        
    def __init__(self, procedure_class, parameters, parent=None):
        super(ExperimentBrowser, self).__init__(parent)
        self.procedure_parameters = parameters
        self.procedure_class = procedure_class
        
        header_labels = ["Graph", "Filename", "Progress", "Status"]
        parameter_objects = procedure_class().parameterObjects() # Get the default parameters
        for parameter in parameters:
            if parameter in parameter_objects:
                header_labels.append(parameter_objects[parameter].name)
            else:
                raise Exception("Invalid parameter input for a ExperimentBrowser column")
        
        self.setColumnCount(len(header_labels))
        self.setHeaderLabels(header_labels)
        
        for i, width in enumerate([80, 140]):
            self.header().resizeSection(i, width)
        
    def add(self, experiment):
        if not isinstance(experiment.procedure, self.procedure_class):
            raise Exception("This ResultsBrowser only supports '%s' objects")
        
        item = experiment.browser_item
        for i, column in enumerate(self.procedure_parameters):
            item.setText(i+4, str(getattr(experiment.procedure, column)))
        
        self.addTopLevelItem(item)
        self.setItemWidget(item, 2, item.progressbar)
        return item   


    
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
        
        
class QueueManager(QObject):
    
    queue = []
    _is_continuous = True
    _start_on_add = True
    _running_thread = None
    added = pyqtSignal(object)
    running = pyqtSignal(object)
    finished = pyqtSignal(object)
    failed = pyqtSignal(object)
    aborted = pyqtSignal(object)
    abort_returned = pyqtSignal(object)

    def __init__(self, procedure_class, parent=None):
        QObject.__init__(self, parent=parent)
        self.procedure_class = procedure_class
        
    def isRunning(self):
        """ Returns True if a procedure is currently running
        """
        return self._running_thread != None
        
    def runningResults(self):
        """ Returns the results object of the running procedure
        """
        for results in self.queue:
            if results.procedure.status == Procedure.RUNNING:
                return results
        
    def queuedResults(self):
        """ Returns the procedures which are queued
        """
        queued = []
        for results in self.queue:
            if results.procedure.status == Procedure.QUEUED:
                queued.append(results)
        return queued
        
    def add(self, results):
        """ Adds the results object to the queue to be filled once the procedure
        is ready to be run
        """
        if results.procedure.status != Procedure.QUEUED:
            raise Exception("Adding a procedure to the manager queue that has"
                            " a non-queued status")
        if not isinstance(results.procedure, self.procedure_class):
            raise Exception("Procedure object is of class '%s' instead of '%s'" % (
                        results.procedure.__class__, self.procedure_class))
        self.queue.append(results)
        if self._start_on_add:
            self.next()
        
    def next(self):
        """ Initiates the start of the next procedure in the queue as long
        as no other procedure is currently running and there is a procedure
        in the queue
        """
        if self.isRunning():
            raise Exception("Another procedure is already running")
        else:
            queued = self.queuedResults()
            if len(queued) == 0:
                raise Exception("No procedures are queued to be run")
            else:
                results = queued[0]
                self._running_thread = ProcedureThread(parent=self)
                self._running_thread.load(results.procedure)
                self._running_thread.finished.connect(self._callback)
                self._running_thread.start()
                self.running.emit(results)
    
    def abort(self):
        """ Aborts the currently running procedure, but raises an exception if
        there is no running procedure
        """    
        if not self.isRunning():
            raise Exception("Attempting to abort when no procedure is running")
        else:
            self._running_thread.abort()
            
            self.aborted.emit(results)
        
    def _callback(self):
        """ Handles the different cases upon which the running procedure thread
        can call back
        """
        results = self.runningResults()
        results.procedure.status = self._running_thread.procedure.status
        # TODO: Verify that the procedure in the thread and the results are concurrent
        if self._running_thread.procedure.status == Procedure.FAILED:
            self.failed.emit(results)
        elif self._running_thread.procedure.status == Procedure.ABORTED:
            self.abort_returned.emit(results)
        elif self._running_thread.procedure.status == Procedure.FINISHED:
            self.finished.emit(results)
            
        self._running_thread = None
        if self._is_continuous: # Continue running procedures
            self.next()
            
    def remove(self, results):
        """ Removes the procedure from the queue, unless it is currently running
        """
        if not results in self.queue:
            raise Exception("Attempting to remove a procedure that is not in the queue")
        else:
            if self.isRunning() and results.procedure == self._running_thread.procedure:
                raise Exception("Attempting to remove the currently running procedure")
            else:
                self.queue.pop(self.queue.index(results))
                
    def swap(self, r1, r2):
        """ Swaps the ordering of two procedures which are queued
        """
        queued = self.queuedItems()
        if not r1 in queued or not r2 in queued:
            raise Exception("Both procedures must be queued for them to be eligible to swap")
        else:
            if self.isRunning():
                if r1.procedure == self._running_thread.procedure or r2.procedure == self._running_thread.procedure:
                    # This should not occur since the status would not be queued
                    raise Exception("Attempting to re-order a procedure that is running")
            # TODO: Ensure locking of the queue so that nothing happens when the swap occurs
            i1 = self.queue.index(r1)
            i2 = self.queue.index(r2)
            self.queue.pop(i1)
            self.queue.insert(i1, r2)
            self.queue.pop(i2)
            self.queue.insert(i2, r1)
            
