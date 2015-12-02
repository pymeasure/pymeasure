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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from os.path import basename
from time import sleep

from pymeasure.experiment import Procedure
from pymeasure.experiment.workers import Worker
from .listeners import Monitor
from .graph import PlotWidget
from .browser import Browser
from .qt_variant import QtCore, QtGui


class Experiment(QtCore.QObject):
    """ The Experiment class helps group the :class:`.Procedure`,
    :class:`.Results`, and their display functionality. Its function
    is only a convenient container.

    :param procedure: :class:`.Procedure` object
    :param results: :class:`.Results` object
    :param curve: :class:`.ResultsCurve` object
    :param browser_item: :class:`.BrowserItem` object
    """

    def __init__(self, results, curve, browser_item, parent=None):
        super(Experiment, self).__init__(parent)
        self.results = results
        self.data_filename = self.results.data_filename
        self.procedure = self.results.procedure
        self.curve = curve
        self.browser_item = browser_item


class ExperimentQueue(QtCore.QObject):
    """ Represents a Queue of Experiments and allows queries to
    be easily preformed
    """

    def __init__(self):
        self.queue = []

    def append(self, experiment):
        self.queue.append(experiment)

    def remove(self, experiment):
        if experiment not in self.queue:
            raise Exception("Attempting to remove an Experiment that is "
                            "not in the ExperimentQueue")
        else:
            if experiment.procedure.status == Procedure.RUNNING:
                raise Exception("Attempting to remove a running experiment")
            else:
                self.queue.pop(self.queue.index(experiment))

    def __contains__(self, value):
        if isinstance(value, Experiment):
            return value in self.queue
        if isinstance(value, str):
            for experiment in self.queue:
                if basename(experiment.data_filename) == basename(value):
                    return True
            return False
        return False

    def next(self):
        """ Returns the next experiment on the queue
        """
        for experiment in self.queue:
            if experiment.procedure.status == Procedure.QUEUED:
                return experiment
        raise Exception("There are no queued experiments")

    def has_next(self):
        """ Returns True if another item is on the queue
        """
        try:
            self.next()
        except:
            return False
        return True

    def with_browser_item(self, item):
        for experiment in self.queue:
            if experiment.browser_item is item:
                return experiment
        return None


class Manager(QtCore.QObject):
    """Controls the execution of :class:`.Experiment` classes by implementing
    a queue system in which Experiments are added, removed, executed, or
    aborted. When instantiated, the Manager is linked to a :class:`.Browser`
    and a PyQtGraph `PlotItem` within the user interface, which are updated
    in accordance with the execution status of the Experiments.
    """
    _is_continuous = True
    _start_on_add = True
    queued = QtCore.QSignal(object)
    running = QtCore.QSignal(object)
    finished = QtCore.QSignal(object)
    failed = QtCore.QSignal(object)
    aborted = QtCore.QSignal(object)
    abort_returned = QtCore.QSignal(object)

    def __init__(self, plot, browser, port=5888, parent=None):
        super(Manager, self).__init__(parent=parent)

        self.experiments = ExperimentQueue()
        self._worker = None
        self._running_experiment = None
        self._monitor = None
        
        self.plot = plot
        self.browser = browser

        self.port = port

    def is_running(self):
        """ Returns True if a procedure is currently running
        """
        return self._running_experiment is not None

    def running_experiment(self):
        if self.is_running():
            return self._running_experiment
        else:
            raise Exception("There is no Experiment running")

    def _update_progress(self, progress):
        if self.is_running():
            self._running_experiment.browser_item.setProgress(progress)

    def _update_status(self, status):
        if self.is_running():
            self._running_experiment.procedure.status = status
            self._running_experiment.browser_item.setStatus(status)

    def load(self, experiment):
        """ Load a previously executed Experiment
        """
        self.plot.addItem(experiment.curve)
        self.browser.add(experiment)
        self.experiments.append(experiment)

    def queue(self, experiment):
        """ Adds an experiment to the queue.
        """
        self.load(experiment)
        self.queued.emit(experiment)
        if self._start_on_add and not self.is_running():
            self.next()

    def remove(self, experiment):
        """ Removes an Experiment
        """
        self.experiments.remove(experiment)
        self.browser.takeTopLevelItem(
            self.browser.indexOfTopLevelItem(experiment.browser_item))
        self.plot.removeItem(experiment.curve)

    def clear(self):
        """ Remove all Experiments
        """
        for experiment in self.experiments[:]:
            self.remove(experiment)

    def next(self):
        """ Initiates the start of the next experiment in the queue as long
        as no other experiments are currently running and there is a procedure
        in the queue.
        """
        if self.is_running():
            raise Exception("Another procedure is already running")
        else:
            if self.experiments.has_next():
                log.debug("Manager is initiating the next experiment")
                experiment = self.experiments.next()
                self._running_experiment = experiment

                self._worker = Worker(experiment.results, self.port)

                self._monitor = Monitor(self._worker.monitor_queue)
                self._monitor.worker_running.connect(self._running)
                self._monitor.worker_failed.connect(self._failed)
                self._monitor.worker_abort_returned.connect(self._abort_returned)
                self._monitor.worker_finished.connect(self._finish)
                self._monitor.progress.connect(self._update_progress)
                self._monitor.status.connect(self._update_status)

                self._monitor.start()
                self._worker.start()

    def _running(self):
        if self.is_running():
            self.running.emit(self.running_experiment)

    def _clean_up(self):
        self._worker.join()
        del self._worker
        del self._monitor
        self._worker = None
        self._running_experiment = None
        log.debug("Manager has cleaned up after the Worker")

    def _failed(self):
        log.debug("Manager's running experiment has failed")
        experiment = self._running_experiment
        self._clean_up()
        self.failed.emit(experiment)

    def _abort_returned(self):
        log.debug("Manager's running experiment has returned after an abort")
        experiment = self._running_experiment
        self._clean_up()
        self.abort_returned.emit(experiment)

    def _finish(self):
        log.debug("Manager's running experiment has finished")
        experiment = self._running_experiment
        self._clean_up()
        experiment.browser_item.setProgress(100.)
        self.finished.emit(experiment)
        if self._is_continuous:  # Continue running procedures
            self.next()

    def resume(self):
        """ Resume processing of the queue.
        """
        self._start_on_add = True
        self._continous = True
        self.next()

    def abort(self):
        """ Aborts the currently running Experiment, but raises an exception if
        there is no running experiment
        """
        if not self.is_running():
            raise Exception("Attempting to abort when no experiment "
                            "is running")
        else:
            self._start_on_add = False
            self._continous = False

            self._worker.stop()

            self.aborted.emit(self._running_experiment)


class ManagedWindow(QtGui.QMainWindow):
    """ The ManagedWindow uses a Manager to control Workers in a Queue,
    and provides a simple interface. The queue method must be overwritten
    by a child class which is required to pass an Experiment containing the
    Results and Procedure to self.manager.queue.
    """

    def __init__(self, procedure_class, browser_columns=[], x_axis=None, y_axis=None, parent=None):
        super(ManagedWindow, self).__init__(parent=parent)
        app = QtCore.QCoreApplication.instance()
        app.aboutToQuit.connect(self.quit)
        self.procedure_class = procedure_class
        self.browser_columns = browser_columns
        self.x_axis, self.y_axis = x_axis, y_axis
        self._setup_ui()

    def _setup_ui(self):
        self.main = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        self.queue_button = QtGui.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self.queue)
        self.abort_button = QtGui.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        vbox.addLayout(hbox)

        self.plot_widget = PlotWidget(self.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis)
        self.plot_widget.x_axis_changed.connect(self.x_axis_changed)
        self.plot_widget.y_axis_changed.connect(self.y_axis_changed)
        self.plot = self.plot_widget.plot
        vbox.addWidget(self.plot_widget)

        self.browser = Browser(
            self.procedure_class,
            self.browser_columns, 
            [self.x_axis, self.y_axis],
            parent=self.main
        )
        
        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.browser.customContextMenuRequested.connect(self.on_curve_context)
        self.browser.itemChanged.connect(self.browser_item_changed)
        vbox.addWidget(self.browser)

        self.manager = Manager(self.plot, self.browser, parent=self)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

    def x_axis_changed(self, axis):
        self.x_axis = axis

    def y_axis_changed(self, axis):
        self.y_axis = axis

    def quit(self, evt=None):
        self.close()

    def browser_item_changed(self, item, column):
        if column == 0:
            state = item.checkState(0)
            experiment = self.manager.experiments.with_browser_item(item)
            if state == 0:
                self.plot.removeItem(experiment.curve)
            else:
                self.plot.addItem(experiment.curve)

    def queue(self):
        """ This method should be overwritten by the child class. The
        self.manager.queue method should be passed an Experiment object
        which contains the Results and Procedure to be run.
        """
        raise Exception("The queue method must call self.manager.queue(experiment)")

    def abort(self):
        self.abort_button.setEnabled(False)
        self.abort_button.setText("Resume")
        self.abort_button.clicked.disconnect()
        self.abort_button.clicked.connect(self.resume)
        try:
            self.manager.abort()
        except:
            log.error('Failed to abort experiment', exc_info=True)
            self.abort_button.setText("Abort")
            self.abort_button.clicked.disconnect()
            self.abort_button.clicked.connect(self.abort)

    def resume(self):
        self.abort_button.setText("Abort")
        self.abort_button.clicked.disconnect()
        self.abort_button.clicked.connect(self.abort)
        if self.manager.experiments.has_next():
            self.manager.resume()
        else:
            self.abort_button.setEnabled(False)

    def queued(self, experiment):
        self.abort_button.setEnabled(True)

    def running(self, experiment):
        pass

    def abort_returned(self, experiment):
        if self.manager.experiments.has_next():
            self.abort_button.setText("Resume")
            self.abort_button.setEnabled(True)

    def finished(self, experiment):
        if not self.manager.experiments.has_next():
            self.abort_button.setEnabled(False) 