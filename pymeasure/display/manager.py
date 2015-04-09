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
from pymeasure.display.procedure_thread import QProcedureThread
from pymeasure.display.listeners import QResultsWriter
from qt_variant import QtCore


class Manager(QtCore.QObject):

    experiments = []
    _is_continuous = True
    _start_on_add = True
    _running_thread = None
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

    def isRunning(self):
        """ Returns True if a procedure is currently running
        """
        return self._running_thread is not None

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
        return [experiment.results.data_filename for
                experiment in self.experiments]

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
                # raise Exception("No experiments are queued to be run")
            else:
                experiment = queued[0]
                # index = self.experiments.index(experiment)

                self._running_thread = QProcedureThread(parent=self)
                self._running_thread.load(experiment.procedure)
                self._running_thread.finished.connect(self._callback)

                self._data_writer = QResultsWriter(experiment.results)
                self._running_thread.data.connect(self._data_writer.write)

                self._running_thread.progress.connect(
                    experiment.browser_item.progressbar.setValue)
                self._running_thread.status_changed.connect(
                    experiment.browser_item.setStatus)

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
        if experiment not in self.experiments:
            raise Exception("Attempting to remove an Experiemnt that is "
                            "not in the Manager")
        else:
            if self.isRunning() and experiment == self.runningExperiment():
                raise Exception("Attempting to remove the currently"
                                " running experiment")
            else:
                self.browser.takeTopLevelItem(
                    self.browser.indexOfTopLevelItem(experiment.browser_item))
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
            raise Exception("Attempting to abort when no experiment is"
                            " running")
        else:
            self._start_on_add = False
            self._continous = False

            self._running_thread.abort()
            self._data_writer.join()

            self.aborted.emit(
                self.experimentFromProcedure(self._running_thread.procedure))

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
            if self._is_continuous:  # Continue running procedures
                self.next()

    def experimentFromBrowserItem(self, browser_item):
        for experiment in self.experiments:
            if experiment.browser_item == browser_item:
                return experiment
        raise Exception("This BrowserItem did not match any Experiments "
                        "in the Manager")

    def experimentFromProcedure(self, procedure):
        for experiment in self.experiments:
            if experiment.procedure == procedure:
                return experiment
        raise Exception("This Procedure did not match any Experiments"
                        " in the Manager")
