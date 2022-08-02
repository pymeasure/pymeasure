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

from .browser import BrowserItem
from .curves import ResultsCurve
from .manager import Manager, Experiment
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
    EstimatorWidget,
    AnalysisBrowserWidget,
)
from ..experiment import Results, Procedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PlotterWindow(QtGui.QMainWindow):
    """
    A window for plotting experiment results. Should not be
    instantiated directly, but only via the
    :class:`~pymeasure.display.plotter.Plotter` class.

    .. seealso::

        Tutorial :ref:`tutorial-plotterwindow`
            A tutorial and example code for using the Plotter and PlotterWindow.

    .. attribute plot::

        The `pyqtgraph.PlotItem`_ object for this window. Can be
        accessed to further customise the plot view programmatically, e.g.,
        display log-log or semi-log axes by default, change axis range, etc.

    .. pyqtgraph.PlotItem: http://www.pyqtgraph.org/documentation/graphicsItems/plotitem.html

    """

    def __init__(self, plotter, refresh_time=0.1, linewidth=1, parent=None):
        super().__init__(parent)
        self.plotter = plotter
        self.refresh_time = refresh_time
        columns = plotter.results.procedure.DATA_COLUMNS

        self.setWindowTitle('Results Plotter')
        self.main = QtGui.QWidget(self)

        vbox = QtGui.QVBoxLayout(self.main)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(6)
        hbox.setContentsMargins(-1, 6, -1, -1)

        file_label = QtGui.QLabel(self.main)
        file_label.setText('Data Filename:')

        self.file = QtGui.QLineEdit(self.main)
        self.file.setText(plotter.results.data_filename)

        hbox.addWidget(file_label)
        hbox.addWidget(self.file)
        vbox.addLayout(hbox)

        self.plot_widget = PlotWidget("Plotter", columns, refresh_time=self.refresh_time,
                                      check_status=False, linewidth=linewidth)
        self.plot = self.plot_widget.plot

        vbox.addWidget(self.plot_widget)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

        self.curve = ResultsCurve(plotter.results, columns[0], columns[1],
                                  pen=pg.mkPen(color=pg.intColor(0), width=linewidth),
                                  antialias=False)
        self.plot.addItem(self.curve)

        self.plot_widget.updated.connect(self.check_stop)

    def quit(self, evt=None):
        log.info("Quitting the Plotter")
        self.close()
        self.plotter.stop()

    def check_stop(self):
        """ Checks if the Plotter should stop and exits the Qt main loop if so
        """
        if self.plotter.should_stop():
            QtCore.QCoreApplication.instance().quit()


class ManagedWindowBase(QtGui.QMainWindow):
    """
    Base class for GUI experiment management .

    The ManagedWindowBase provides an interface for inputting experiment
    parameters, running several experiments
    (:class:`~pymeasure.experiment.procedure.Procedure`), plotting
    result curves, and listing the experiments conducted during a session.

    The ManagedWindowBase uses a Manager to control Workers in a Queue,
    and provides a simple interface.
    The :meth:`~pymeasure.display.windows.ManagedWindowBase.queue` method must be
    overridden by the child class.

    The ManagedWindowBase allow user to define a set of widget that display information about the
    experiment. The information displayed may include: plots, tabular view, logging information,...

    This class is not intended to be used directy, but it should be subclassed to provide some
    appropriate widget list. Example of classes usable as element of widget list are:

    - :class:`~pymeasure.display.widgets.LogWidget`
    - :class:`~pymeasure.display.widgets.PlotWidget`
    - :class:`~pymeasure.display.widgets.ImageWidget`

    Of course, users can define its own widget making sure that inherits from
    :class:`~pymeasure.display.widgets.TabWidget`.

    Examples of ready to use classes inherited from ManagedWindowBase are:

    - :class:`~pymeasure.display.windows.ManagedWindow`
    - :class:`~pymeasure.display.windows.ManagedImageWindow`

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
        self.port = port

        # Check if the get_estimates function is reimplemented
        self.use_estimator = not self.procedure_class.get_estimates == Procedure.get_estimates

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        if self.directory_input:
            self.directory_label = QtGui.QLabel(self)
            self.directory_label.setText('Directory')
            self.directory_line = DirectoryLineEdit(parent=self)

        self.queue_button = QtGui.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self._queue)

        self.abort_button = QtGui.QPushButton('Abort', self)
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

        if self.use_estimator:
            estimator_dock = QtGui.QDockWidget('Estimator')
            estimator_dock.setWidget(self.estimator)
            estimator_dock.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, estimator_dock)

        self.tabs = QtGui.QTabWidget(self.main)
        for wdg in self.widget_list:
            self.tabs.addTab(wdg, wdg.name)

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.tabs)

        if self.use_analyzer:
            browser_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
            browser_splitter.addWidget(self.browser_widget)
            browser_splitter.addWidget(self.analysis_browser_widget)
            splitter.addWidget(browser_splitter)
        else:
            splitter.addWidget(self.browser_widget)

        vbox = QtGui.QVBoxLayout(self.main)
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

    def new_curve(self, wdg, results, color=None, **kwargs):
        if color is None:
            color = pg.intColor(self.browser_widget.browser.topLevelItemCount() % 8)
        return wdg.new_curve(results, color=color, **kwargs)

    def new_experiment(self, results, curve=None):
        if curve is None:
            curve_list = []
            for wdg in self.widget_list:
                curve_list.append(self.new_curve(wdg, results))
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
        but is required when the :class:`~pymeasure.display.widgets.SequencerWidget`
        is used.

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
    Display experiment output with an :class:`~pymeasure.display.widget.PlotWidget` class.

    .. seealso::

        Tutorial :ref:`tutorial-managedwindow`
            A tutorial and example on the basic configuration and usage of ManagedWindow.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the initial data-column for the x-axis of the plot
    :param y_axis: the initial data-column for the y-axis of the plot
    :param linewidth: linewidth for the displayed curves, default is 1
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.ManagedWindowBase`

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


class ManagedImageWindow(ManagedWindow):
    """
    Display experiment output with an :class:`~pymeasure.display.widget.ImageWidget` class.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the data-column for the x-axis of the plot, cannot be changed afterwards for
        the image-plot
    :param y_axis: the data-column for the y-axis of the plot, cannot be changed afterwards for
        the image-plot
    :param z_axis: the initial data-column for the z-axis of the plot, can be changed afterwards
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.ManagedWindow`

    """

    def __init__(self, procedure_class, x_axis, y_axis, z_axis=None, **kwargs):
        self.z_axis = z_axis
        self.image_widget = ImageWidget(
            "Image", procedure_class.DATA_COLUMNS, x_axis, y_axis, z_axis)

        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.image_widget,)

        super().__init__(procedure_class, x_axis=x_axis, y_axis=y_axis, **kwargs)
