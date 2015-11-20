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

from pymeasure.experiment import Procedure
from pymeasure.experiment.workers import ProcedureWorker
from pymeasure.experiment.listeners import ResultsWriter
from pymeasure.display.listeners import ProcedureMonitor
from .qt_variant import QtCore


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
        super(Experiment, self).__init__(self, parent=parent)
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

    def __init__(self, plot, browser, port=5558, parent=None):
        super(Manager, self).__init__(parent=parent)

        self.experiments = ExperimentQueue()
        self._worker = None
        self._writer = None
        self._running_experiment = None
        
        self.plot = plot
        self.browser = browser

        self.port = port
        self.monitor = ProcedureMonitor('tcp://localhost:%d' % port)
        # Route Monitor callbacks through signals and slots
        self.monitor.running.connect(self._running)
        self.monitor.finished.connect(self._finish)
        self.monitor.progress.connect(self._update_progress)
        self.monitor.status.connect(self._update_status)

    def __del__(self):
        """ Ensures that the processes and threads are properly
        shutdown before deleting the Manager
        """
        self.monitor.stop()
        self.monitor.join()
        if self._worker is not None:
            self._worker.stop()
            self._worker.join()

        if self._writer is not None:
            self._writer.stop()
            self._writer.join()

        super(Manager, self).__del__()

    def is_running(self):
        """ Returns True if a procedure is currently running
        """
        return self._worker is not None

    def _update_progress(self, progress):
        if self.is_running():
            self._running_experiment.browser_item.progressbar.setValue(progress)

    def _update_status(self, status):
        if self.is_running():
            self._running_experiment.procedure.status = status

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
                experiment = self.experiments.next()
                self._running_experiment = experiment

                self._writer = ResultsWriter(
                    experiment.data_filename,
                    'tcp://localhost:%s' % self.port
                )
                self.writer.start()
                sleep(0.01)

                self._worker = ProcedureWorker(
                    experiment.data_filename,
                    'tcp://*:%s' % self.port
                )
                self.worker.start()

    def _running(self):
        if self.is_running():
            self.running.emit(self.running_experiment)

    def _clean_up(self):
        self._worker.stop()
        self._writer.stop()
        self._worker.join()
        self._writer.join()
        
        del self._worker
        del self._writer

        self._worker = None
        self._writer = None
        self._running_experiment = None

    def _finish(self):
        experiment = self._running_experiment
        self.clean_up()
        if experiment.procedure.status == Procedure.FAILED:
            self.failed.emit(experiment)
        elif experiment.procedure.status == Procedure.ABORTED:
            self.abort_returned.emit(experiment)
        elif experiment.procedure.status == Procedure.FINISHED:
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
