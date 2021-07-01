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

import os
import subprocess, platform

import pyqtgraph as pg
from ..experiment import Procedure
from os.path import basename

from .browser import BrowserItem
from .curves import ResultsCurve
from .multimanager import MultiManager, MultiExperiment
from .Qt import QtCore, QtGui
from .widgets import (
    PlotWidget,
    BrowserWidget,
    InputsWidget,
    LogWidget,
    ResultsDialog,
    SequencerWidget,
    ImageWidget,
    DirectoryLineEdit,
)
from ..experiment.results import Results
from .widgets import PlotFrame
from .windows import ManagedWindow

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class MultiPlotContainer(QtGui.QWidget):
    def __init__(self, widgets=None, parent=None):
        super().__init__(parent)
        self.widgets = widgets
        self._layout()

    def _layout(self):
        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)

        for widget in self.widgets:
            splitter.addWidget(widget)

        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(splitter)
        self.setLayout(vbox)


class MultiManagedWindow(ManagedWindow):
    """
    Abstract base class.

    The ManagedWindow provides an interface for inputting experiment
    parameters, running several experiments
    (:class:`~pymeasure.experiment.procedure.Procedure`), plotting
    result curves, and listing the experiments conducted during a session.

    The ManagedWindow uses a Manager to control Workers in a Queue,
    and provides a simple interface. The :meth:`~.queue` method must be
    overridden by the child class.

    .. seealso::

        Tutorial :ref:`tutorial-managedwindow`
            A tutorial and example on the basic configuration and usage of ManagedWindow.

    .. attribute:: plot

        The `pyqtgraph.PlotItem`_ object for this window. Can be
        accessed to further customise the plot view programmatically, e.g.,
        display log-log or semi-log axes by default, change axis range, etc.

    .. _pyqtgraph.PlotItem: http://www.pyqtgraph.org/documentation/graphicsItems/plotitem.html


    """

    def __init__(self, procedure_class, data_plots=None, setup=False, **kwargs):

        super().__init__(procedure_class, setup=False, **kwargs)


        self.data_plots = data_plots if data_plots is not None else [self.procedure_class.DATA_COLUMNS, ]
        self.plot_widgets = []
        self.plots = []
        self.procedure_class = procedure_class

        self.browser_item = None
        self._setup_ui()
        self._layout()



    def _setup_ui(self):
        self.log_widget = LogWidget()
        self.log.addHandler(self.log_widget.handler)  # needs to be in Qt context?
        log.info("ManagedWindow connected to logging")

        if self.directory_input:
            self.directory_label = QtGui.QLabel(self)
            self.directory_label.setText('Directory')
            self.directory_line = DirectoryLineEdit(parent=self)

        self.queue_button = QtGui.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self.queue)

        self.abort_button = QtGui.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort)


        for idx, i in enumerate(self.data_plots):
            self.plot_widgets.append(PlotWidget(i, i[0], i[1]))
            self.plots.append(self.plot_widgets[idx].plot)
        self.plot_container = MultiPlotContainer(parent=self, widgets=self.plot_widgets)

        self.browser_widget = BrowserWidget(
            self.procedure_class,
            self.displays,
            [self.x_axis, self.y_axis],
            parent=self
        )
        self.browser_widget.show_button.clicked.connect(self.show_experiments)
        self.browser_widget.hide_button.clicked.connect(self.hide_experiments)
        self.browser_widget.clear_button.clicked.connect(self.clear_experiments)
        self.browser_widget.open_button.clicked.connect(self.open_experiment)
        self.browser = self.browser_widget.browser

        self.browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.browser_item_menu)
        self.browser.itemChanged.connect(self.browser_item_changed)

        self.inputs = InputsWidget(
            self.procedure_class,
            self.inputs,
            parent=self
        )

        self.manager = MultiManager(self.plots, browser=self.browser, log_level=self.log_level, parent=self)
        self.manager.abort_returned.connect(self.abort_returned)
        self.manager.queued.connect(self.queued)
        self.manager.running.connect(self.running)
        self.manager.finished.connect(self.finished)
        self.manager.log.connect(self.log.handle)

        if self.use_sequencer:
            self.sequencer = SequencerWidget(
                self.sequencer_inputs,
                self.sequence_file,
                parent=self
            )

    def _layout(self):
        self.main = QtGui.QWidget(self)

        inputs_dock = QtGui.QWidget(self)
        inputs_vbox = QtGui.QVBoxLayout(self.main)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        hbox.addStretch()

        if self.directory_input:
            vbox = QtGui.QVBoxLayout()
            vbox.addWidget(self.directory_label)
            vbox.addWidget(self.directory_line)
            vbox.addLayout(hbox)

        if self.inputs_in_scrollarea:
            inputs_scroll = QtGui.QScrollArea()
            inputs_scroll.setWidgetResizable(True)
            inputs_scroll.setFrameStyle(QtGui.QScrollArea.NoFrame)

            self.inputs.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
            inputs_scroll.setWidget(self.inputs)
            inputs_vbox.addWidget(inputs_scroll, 1)

        else:
            inputs_vbox.addWidget(self.inputs)

        if self.directory_input:
            inputs_vbox.addLayout(vbox)
        else:
            inputs_vbox.addLayout(hbox)

        inputs_vbox.addStretch(0)
        inputs_dock.setLayout(inputs_vbox)

        dock = QtGui.QDockWidget('Input Parameters')
        dock.setWidget(inputs_dock)
        dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)

        if self.use_sequencer:
            sequencer_dock = QtGui.QDockWidget('Sequencer')
            sequencer_dock.setWidget(self.sequencer)
            sequencer_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, sequencer_dock)

        tabs = QtGui.QTabWidget(self.main)
        tabs.addTab(self.plot_container, "Results Graph")
        tabs.addTab(self.log_widget, "Experiment Log")

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(tabs)
        splitter.addWidget(self.browser_widget)
        #self.plot_widget.setMinimumSize(100, 200)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)
        vbox.addWidget(splitter)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(1000, 800)

    def open_experiment(self):
        dialog = ResultsDialog(self.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            for filename in map(str, filenames):
                if filename in self.manager.experiments:
                    QtGui.QMessageBox.warning(self, "Load Error",
                                              "The file %s cannot be opened twice." % os.path.basename(
                                                  filename))
                elif filename == '':
                    return
                else:
                    results = Results.load(filename)
                    experiment = self.new_experiment(results)
                    experiment.curve.update()
                    experiment.browser_item.progressbar.setValue(100.)
                    self.manager.load(experiment)
                    log.info('Opened data file %s' % filename)

    def change_color(self, experiment):
        color = QtGui.QColorDialog.getColor(
            initial=experiment.curves[0].opts['pen'].color(), parent=self)
        if color.isValid():
            pixelmap = QtGui.QPixmap(24, 24)
            pixelmap.fill(color)
            experiment.browser_item.setIcon(0, QtGui.QIcon(pixelmap))
            for idx, i in enumerate(experiment.curves):
                i.setPen(pg.mkPen(color=color, width=2))


    def new_curve(self, plot_widget, results, color=None, **kwargs):
        if color is None:
            color = pg.intColor(self.browser.topLevelItemCount() % 8)
        return plot_widget.new_curve(results, color=color, **kwargs)

    def new_experiment(self, results, curves=None):
        if curves is None:
            curves = []
            for idx, i in enumerate(self.plot_widgets):
                curves.append(self.new_curve(i, results))


        browser_item = BrowserItem(results, curves[0].opts['pen'].color())

        return MultiExperiment(results, curves, browser_item)
