#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import platform
import subprocess

import pyqtgraph as pg

from ..browser import BrowserItem
from ..manager import Manager, Experiment
from ..Qt import QtCore, QtWidgets, QtGui
from ..widgets import (
    PlotWidget,
    BrowserWidget,
    InputsWidget,
    LogWidget,
    ResultsDialog,
    SequencerWidget,
    DirectoryLineEdit,
    EstimatorWidget,
    AnalysisBrowserWidget,
)
from ...experiment import Results, Procedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ManagedWindowBase(QtWidgets.QMainWindow):
    """
    Base class for GUI experiment management .

    The ManagedWindowBase provides an interface for inputting experiment
    parameters, running several experiments
    (:class:`~pymeasure.experiment.procedure.Procedure`), plotting
    result curves, and listing the experiments conducted during a session.

    The ManagedWindowBase uses a Manager to control Workers in a Queue,
    and provides a simple interface.
    The :meth:`~pymeasure.display.windows.managed_window.ManagedWindowBase.queue` method must be
    overridden by the child class.

    The ManagedWindowBase allow user to define a set of widget that display information about the
    experiment. The information displayed may include: plots, tabular view, logging information,...

    This class is not intended to be used directy, but it should be subclassed to provide some
    appropriate widget list. Example of classes usable as element of widget list are:

    - :class:`~pymeasure.display.widgets.log_widget.LogWidget`
    - :class:`~pymeasure.display.widgets.plot_widget.PlotWidget`
    - :class:`~pymeasure.display.widgets.image_widget.ImageWidget`

    Of course, users can define its own widget making sure that inherits from
    :class:`~pymeasure.display.widgets.tab_widget.TabWidget`.

    Examples of ready to use classes inherited from ManagedWindowBase are:

    - :class:`~pymeasure.display.windows.managed_window.ManagedWindow`
    - :class:`~pymeasure.display.windows.managed_image_window.ManagedImageWindow`

    .. seealso::

        Tutorial :ref:`tutorial-managedwindow`
            A tutorial and example on the basic configuration and usage of ManagedWindow.

    Parameters for :code:`__init__` constructor.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param widget_list: list of widget to be displayed in the GUI
    :param inputs: list of :class:`~pymeasure.experiment.parameters.Parameter` instance variable
        names, which the display will generate graphical fields for
    :param displays: list of :class:`~pymeasure.experiment.parameters.Parameter` instance variable
        names displayed in the browser window
    :param log_channel: :code:`logging.Logger` instance to use for logging output
    :param log_level: logging level
    :param parent: Parent widget or :code:`None`
    :param sequencer: a boolean stating whether or not the sequencer has to be included into the
        window
    :param sequencer_inputs: either :code:`None` or a list of the parameter names to be scanned
        over. If no list of parameters is given, the parameters displayed in the manager queue
        are used.
    :param sequence_file: simple text file to quickly load a pre-defined sequence with the
        code:`Load sequence` button
    :param inputs_in_scrollarea: boolean that display or hide a scrollbar to the input area
    :param directory_input: specify, if present, where the experiment's result will be saved.
    :param hide_groups: a boolean controlling whether parameter groups are hidden (True, default)
        or disabled/grayed-out (False) when the group conditions are not met.
    :param marker_choice: optional string specifying what marker to use for points on the plot.
        Default is None (i.e. just  a line). See here for choices:
        https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/scatterplotitem.html#pyqtgraph.ScatterPlotItem.setSymbol
    :param port: port to establish zmq server on (default is 5888). If None, no server is established.
        Note, establishing the server adds 2-3 seconds per experiment. Set to None if not using for speed.
    """


    def __init__(self,
                 procedure_class,
                 widget_list=(),
                 inputs=(),
                 displays=(),
                 log_channel='',
                 log_level=logging.INFO,
                 parent=None,
                 sequencer=False,
                 sequencer_inputs=None,
                 sequence_file=None,
                 analyzer=False,
                 inputs_in_scrollarea=False,
                 directory_input=False,
                 hide_groups=True,
                 marker_choice=None,
                 port=5888,
                 ):

        super().__init__(parent)
        app = QtCore.QCoreApplication.instance()
        app.aboutToQuit.connect(self.quit)
        self.procedure_class = procedure_class
        self.inputs = inputs
        self.hide_groups = hide_groups
        self.displays = displays
        self.use_sequencer = sequencer
        self.sequencer_inputs = sequencer_inputs
        self.sequence_file = sequence_file
        self.use_analyzer = analyzer
        self.inputs_in_scrollarea = inputs_in_scrollarea
        self.directory_input = directory_input
        self.log = logging.getLogger(log_channel)
        self.log_level = log_level
        log.setLevel(log_level)
        self.log.setLevel(log_level)
        self.widget_list = widget_list
        self.marker_choice = marker_choice
        self.port = port

        # Check if the get_estimates function is reimplemented
        self.use_estimator = not self.procedure_class.get_estimates == Procedure.get_estimates

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        if self.directory_input:
            self.directory_label = QtWidgets.QLabel(self)
            self.directory_label.setText('Directory')
            self.directory_line = DirectoryLineEdit(parent=self)

        self.queue_button = QtWidgets.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self._queue)

        self.abort_button = QtWidgets.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)

        self.browser_widget = BrowserWidget(
            self.procedure_class,
            self.displays,
            [],  # This value will be patched by subclasses, if needed
            parent=self
        )

        self.abort_button.clicked.connect(self.browser_widget.abort)
        self.manager = self.browser_widget.manager

        self.inputs = InputsWidget(
            self.procedure_class,
            self.inputs,
            parent=self,
            hide_groups=self.hide_groups,
        )

        if self.use_analyzer:
            self.analysis_browser_widget = AnalysisBrowserWidget(
                self.procedure_class,
                self.displays,
                [],  # This value will be patched by subclasses, if needed
                parent=self
            )

        if self.use_sequencer:
            self.sequencer = SequencerWidget(
                self.sequencer_inputs,
                self.sequence_file,
                parent=self
            )

        if self.use_estimator:
            self.estimator = EstimatorWidget(
                parent=self
            )

    def _layout(self):
        self.main = QtWidgets.QWidget(self)

        inputs_dock = QtWidgets.QWidget(self)
        inputs_vbox = QtWidgets.QVBoxLayout(self.main)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        hbox.addStretch()

        if self.directory_input:
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(self.directory_label)
            vbox.addWidget(self.directory_line)
            vbox.addLayout(hbox)

        if self.inputs_in_scrollarea:
            inputs_scroll = QtWidgets.QScrollArea()
            inputs_scroll.setWidgetResizable(True)
            inputs_scroll.setFrameStyle(QtWidgets.QScrollArea.Shape.NoFrame)

            self.inputs.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                      QtWidgets.QSizePolicy.Policy.Fixed)
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

        dock = QtWidgets.QDockWidget('Input Parameters')
        dock.setWidget(inputs_dock)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        if self.use_sequencer:
            sequencer_dock = QtWidgets.QDockWidget('Sequencer')
            sequencer_dock.setWidget(self.sequencer)
            sequencer_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
            self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, sequencer_dock)

        if self.use_estimator:
            estimator_dock = QtWidgets.QDockWidget('Estimator')
            estimator_dock.setWidget(self.estimator)
            estimator_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
            self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, estimator_dock)

        self.tabs = QtWidgets.QTabWidget(self.main)
        for wdg in self.widget_list:
            self.tabs.addTab(wdg, wdg.name)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        splitter.addWidget(self.tabs)

        if self.use_analyzer:
            browser_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
            browser_splitter.addWidget(self.browser_widget)
            browser_splitter.addWidget(self.analysis_browser_widget)
            splitter.addWidget(browser_splitter)
        else:
            splitter.addWidget(self.browser_widget)

        vbox = QtWidgets.QVBoxLayout(self.main)
        vbox.setSpacing(0)
        vbox.addWidget(splitter)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(1000, 800)

    def quit(self, evt=None):
        if self.browser_widget.manager.is_running():
            self.browser_widget.abort()
        if self.use_analyzer:
            if self.analysis_browser_widget.analysis_manager.is_running():
                self.analysis_browser_widget.abort_analysis()

        self.close()

    def make_procedure(self):
        if not isinstance(self.inputs, InputsWidget):
            raise Exception("ManagedWindow can not make a Procedure"
                            " without a InputsWidget type")
        return self.inputs.get_procedure()

    def new_curve(self, wdg, results, color=None, marker=None, **kwargs):
        if color is None:
            color = pg.intColor(self.browser_widget.browser.topLevelItemCount() % 8)
        return wdg.new_curve(results, color=color, marker=marker, **kwargs)

    def new_experiment(self, results, curve=None):
        if curve is None:
            curve_list = []
            for wdg in self.widget_list:
                curve_list.append(self.new_curve(wdg, results, marker=self.marker_choice))
        else:
            curve_list = curve[:]

        curve_color = pg.intColor(0)
        for wdg, curve in zip(self.widget_list, curve_list):
            if isinstance(wdg, PlotWidget):
                curve_color = curve.opts['pen'].color()
                break

        browser_item = BrowserItem(results, curve_color)
        return Experiment(results, curve_list, browser_item)

    def set_parameters(self, parameters):
        """ This method should be overwritten by the child class. The
        parameters argument is a dictionary of Parameter objects.
        The Parameters should overwrite the GUI values so that a user
        can click "Queue" to capture the same parameters.
        """
        if not isinstance(self.inputs, InputsWidget):
            raise Exception("ManagedWindow can not set parameters"
                            " without a InputsWidget")
        self.inputs.set_parameters(parameters)

    def _queue(self, checked):
        """ This method is a wrapper for the `self.queue` method to be connected
        to the `queue` button. It catches the positional argument that is passed
        when it is called by the button and calls the `self.queue` method without
        any arguments.
        """
        self.queue()

    def queue(self, procedure=None):
        """

        Abstract method, which must be overridden by the child class.

        Implementations must call ``self.manager.queue(experiment)`` and pass
        an ``experiment``
        (:class:`~pymeasure.experiment.experiment.Experiment`) object which
        contains the
        :class:`~pymeasure.experiment.results.Results` and
        :class:`~pymeasure.experiment.procedure.Procedure` to be run.

        The optional `procedure` argument is not required for a basic implementation,
        but is required when the
        :class:`~pymeasure.display.widgets.sequencer_widget.SequencerWidget` is used.

        For example:

        .. code-block:: python

            def queue(self):
                filename = unique_filename('results', prefix="data") # from pymeasure.experiment

                procedure = self.make_procedure() # Procedure class was passed at construction
                results = Results(procedure, filename)
                experiment = self.new_experiment(results)

                self.manager.queue(experiment)

        """
        raise NotImplementedError(
            "Abstract method ManagedWindow.queue not implemented")


    @property
    def directory(self):
        if not self.directory_input:
            raise ValueError("No directory input in the ManagedWindow")
        return self.directory_line.text()

    @directory.setter
    def directory(self, value):
        if not self.directory_input:
            raise ValueError("No directory input in the ManagedWindow")

        self.directory_line.setText(str(value))


class ManagedWindow(ManagedWindowBase):
    """
    Display experiment output with an
    :class:`~pymeasure.display.widgets.plot_widget.PlotWidget` class.

    .. seealso::

        Tutorial :ref:`tutorial-managedwindow`
            A tutorial and example on the basic configuration and usage of ManagedWindow.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the initial data-column for the x-axis of the plot
    :param y_axis: the initial data-column for the y-axis of the plot
    :param linewidth: linewidth for the displayed curves, default is 1
    :param \\**kwargs: optional keyword arguments that will be passed to
    :class:`~pymeasure.display.windows.managed_window.ManagedWindowBase`

    """

    def __init__(self, procedure_class, x_axis=None, y_axis=None, linewidth=1, **kwargs):
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.log_widget = LogWidget("Experiment Log")
        self.plot_widget = PlotWidget("Results Graph", procedure_class.DATA_COLUMNS, self.x_axis,
                                      self.y_axis, linewidth=linewidth)
        self.plot_widget.setMinimumSize(100, 200)

        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.plot_widget, self.log_widget)
        super().__init__(procedure_class, **kwargs)

        # Setup measured_quantities once we know x_axis and y_axis
        self.browser_widget.browser.measured_quantities = [self.x_axis, self.y_axis]

        logging.getLogger().addHandler(self.log_widget.handler)  # needs to be in Qt context?
        log.setLevel(self.log_level)
        log.info("ManagedWindow connected to logging")

