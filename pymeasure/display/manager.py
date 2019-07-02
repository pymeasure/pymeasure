#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from os.path import basename

from .Qt import QtCore
from .listeners import Monitor
from ..experiment import Procedure
from ..experiment.workers import Worker

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Experiment(QtCore.QObject):
    """ The Experiment class helps group the :class:`.Procedure`,
    :class:`.Results`, and their display functionality. Its function
    is only a convenient container.

    :param results: :class:`.Results` object
    :param curve: :class:`.ResultsCurve` object
    :param browser_item: :class:`.BrowserItem` object
    """

    def __init__(self, results, curve, browser_item, parent=None):
        super().__init__(parent)
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
        super().__init__()
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

    def __getitem__(self, key):
        return self.queue[key]

    def next(self):
        """ Returns the next experiment on the queue
        """
        for experiment in self.queue:
            if experiment.procedure.status == Procedure.QUEUED:
                return experiment
        raise StopIteration("There are no queued experiments")

    def has_next(self):
        """ Returns True if another item is on the queue
        """
        try:
            self.next()
        except StopIteration:
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
    log = QtCore.QSignal(object)

    def __init__(self, plot, browser, port=5888, log_level=logging.INFO, parent=None):
        super().__init__(parent)

        self.experiments = ExperimentQueue()
        self._worker = None
        self._running_experiment = None
        self._monitor = None
        self.log_level = log_level

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

    def _update_log(self, record):
        self.log.emit(record)

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

                self._worker = Worker(experiment.results, port=self.port, log_level=self.log_level)

                self._monitor = Monitor(self._worker.monitor_queue)
                self._monitor.worker_running.connect(self._running)
                self._monitor.worker_failed.connect(self._failed)
                self._monitor.worker_abort_returned.connect(self._abort_returned)
                self._monitor.worker_finished.connect(self._finish)
                self._monitor.progress.connect(self._update_progress)
                self._monitor.status.connect(self._update_status)
                self._monitor.log.connect(self._update_log)

                self._monitor.start()
                self._worker.start()

    def _running(self):
        if self.is_running():
            self.running.emit(self._running_experiment)

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
        experiment.curve.update()
        self.finished.emit(experiment)
        if self._is_continuous:  # Continue running procedures
            self.next()

    def resume(self):
        """ Resume processing of the queue.
        """
        self._start_on_add = True
        self._is_continuous = True
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
            self._is_continuous = False

            self._worker.stop()

            self.aborted.emit(self._running_experiment)
