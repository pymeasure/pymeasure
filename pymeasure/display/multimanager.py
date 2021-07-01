#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
from .manager import ExperimentQueue, Manager

class MultiExperiment(QtCore.QObject):
    """ The Experiment class helps group the :class:`.Procedure`,
    :class:`.Results`, and their display functionality. Its function
    is only a convenient container.

    :param results: :class:`.Results` object
    :param curve: :class:`.ResultsCurve` object
    :param browser_item: :class:`.BrowserItem` object
    """

    def __init__(self, results, curves, browser_item, parent=None):
        super().__init__(parent)
        self.results = results
        self.data_filename = self.results.data_filename
        self.procedure = self.results.procedure
        self.curves = curves
        self.browser_item = browser_item

class MultiExperimentQueue(ExperimentQueue):
    """ Represents a Queue of Experiments and allows queries to
    be easily preformed
    """

    def __init__(self):
        super().__init__()
        self.queue = []

    def __contains__(self, value):
        if isinstance(value, MultiExperiment):
            return value in self.queue
        if isinstance(value, str):
            for experiment in self.queue:
                if basename(experiment.data_filename) == basename(value):
                    return True
            return False
        return False


class MultiManager(Manager):
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

    def __init__(self, plots, **kwargs):

        super().__init__(plot=None, **kwargs)

        self.experiments = MultiExperimentQueue()
        self.plots = plots

    def load(self, experiment):
        """ Load a previously executed Experiment
        """
        for idx, i in enumerate(self.plots):
            i.addItem(experiment.curves[idx])

        self.browser.add(experiment)
        self.experiments.append(experiment)

    def remove(self, experiment):
        """ Removes an Experiment
        """
        self.experiments.remove(experiment)
        self.browser.takeTopLevelItem(
            self.browser.indexOfTopLevelItem(experiment.browser_item))
        for idx, i in enumerate(self.plots):
            i.removeItem(experiment.curves[idx])


    def _finish(self):
        log.debug("Manager's running experiment has finished")
        experiment = self._running_experiment
        self._clean_up()
        experiment.browser_item.setProgress(100.)
        for curve in experiment.curves:
            curve.update()
        self.finished.emit(experiment)
        if self._is_continuous:  # Continue running procedures
            self.next()