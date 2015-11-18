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
from pymeasure.display.procedure_process import QProcedureProcess
from pymeasure.display.listeners import QResultsWriter
from .qt_variant import QtCore


class Manager(QtCore.QObject):
    """Controls the execution of :class:`.Experiment` classes by implementing
    a queue system in which Experiments are added, removed, executed, or
    aborted. When instantiated, the Manager is linked to a :class:`.Browser`
    and a PyQtGraph `PlotItem` within the user interface, which are updated
    in accordance with the execution status of the Experiments.
    """
    experiments = []
    _is_continuous = True
    _start_on_add = True
    _running_process = None
    queued = QtCore.QSignal(object)
    running = QtCore.QSignal(object)
    finished = QtCore.QSignal(object)
    failed = QtCore.QSignal(object)
    aborted = QtCore.QSignal(object)
    abort_returned = QtCore.QSignal(object)

    def __init__(self, plot, browser, parent=None):
        super(Manager, self).__init__(parent=parent)
        self.plot = plot
        self.browser = browser

    def is_running(self):
        """ Returns True if a procedure is currently running
        """
        return self._running_process is not None

    def running_experiment(self):
        """ Returns the results object of the running procedure
        """
        for experiment in self.experiments:
            if experiment.procedure.status == Procedure.RUNNING:
                return experiment
        return None

    def queued_experiments(self):
        """ Returns the Experiments that are queued
        """
        queued = []
        for experiment in self.experiments:
            if experiment.procedure.status == Procedure.QUEUED:
                queued.append(experiment)
        return queued

    def has_queued_experiments(self):
        """ Returns True if there is at least one Experiment in the queue.
        """
        return len(self.queued_experiments()) > 0

    def file_paths(self):
        """ Returns a list of file paths for the Experiments in the Manager
        """
        return [experiment.results.data_filename for
                experiment in self.experiments]

    def queue(self, experiment):
        """ Adds an experiment to the queue.
        """
        self.load(experiment)
        self.queued.emit(experiment)
        if self._start_on_add and not self.is_running():
            self.next()

    def load(self, experiment):
        """ Load a previously executed experiment into the Browser.
        """
        self.plot.addItem(experiment.curve)
        self.browser.add(experiment)

        self.experiments.append(experiment)

    def next(self):
        """ Initiates the start of the next experiment in the queue as long
        as no other experiments are currently running and there is a procedure
        in the queue.
        """
        if self.is_running():
            raise Exception("Another procedure is already running")
        else:
            queued = self.queued_experiments()
            if len(queued) == 0:
                return
                # raise Exception("No experiments are queued to be run")
            else:
                experiment = queued[0]
                # index = self.experiments.index(experiment)

                self._running_process = QProcedureProcess()
                self._running_process.load(experiment.procedure)
                self._running_process.finished.connect(self._callback)

                self._data_writer = QResultsWriter(experiment.results)
                self._running_process.data.connect(self._data_writer.write)

                self._running_process.progress.connect(
                    experiment.browser_item.progressbar.setValue)
                self._running_process.status_changed.connect(
                    experiment.browser_item.setStatus)

                self._data_writer.start()
                self._running_process.start()
                self.running.emit(experiment)

    def resume(self):
        """ Resume processing of the queue.
        """
        self._start_on_add = True
        self._continous = True
        self.next()

    def remove(self, experiment):
        """ Removes the Experiment from the Manager, unless it is currently running.
        """
        if experiment not in self.experiments:
            raise Exception("Attempting to remove an Experiemnt that is "
                            "not in the Manager")
        else:
            if self.is_running() and experiment == self.running_experiment():
                raise Exception("Attempting to remove the currently"
                                " running experiment")
            else:
                self.browser.takeTopLevelItem(
                    self.browser.indexOfTopLevelItem(experiment.browser_item))
                self.plot.removeItem(experiment.curve)
                self.experiments.pop(self.experiments.index(experiment))

    def clear(self):
        """ Remove all Experiments from the Manager.
        """
        for experiment in self.experiments[:]:
            self.remove(experiment)

    def abort(self):
        """ Aborts the currently running Experiment, but raises an exception if
        there is no running experiment
        """
        if not self.is_running():
            raise Exception("Attempting to abort when no experiment is"
                            " running")
        else:
            self._start_on_add = False
            self._continous = False

            self._running_process.abort()
            self._data_writer.join()

            self.aborted.emit(
                self.experiment_from_procedure(self._running_process.procedure))

    def _callback(self):
        """ Handles the different cases upon which the running procedure thread
        can call back
        """
        for experiment in self.experiments:
            if experiment.procedure == self._running_process.procedure:
                break
        self._running_process = None
        self._data_writer = None
        if experiment.procedure.status == Procedure.FAILED:
            self.failed.emit(experiment)
        elif experiment.procedure.status == Procedure.ABORTED:
            self.abort_returned.emit(experiment)
        elif experiment.procedure.status == Procedure.FINISHED:
            self.finished.emit(experiment)
            if self._is_continuous:  # Continue running procedures
                self.next()

    def experiment_from_browser_item(self, browser_item):
        for experiment in self.experiments:
            if experiment.browser_item == browser_item:
                return experiment
        raise Exception("This BrowserItem did not match any Experiments "
                        "in the Manager")

    def experiment_from_procedure(self, procedure):
        for experiment in self.experiments:
            if experiment.procedure == procedure:
                return experiment
        raise Exception("This Procedure did not match any Experiments"
                        " in the Manager")
