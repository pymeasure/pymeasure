#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
import tempfile
import shutil

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
    FileInputWidget,
    EstimatorWidget,
)
from ...experiment import Results, Procedure, unique_filename

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

    This class is not intended to be used directly, but it should be subclassed to provide some
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
        :code:`Load sequence` button
    :param inputs_in_scrollarea: boolean that display or hide a scrollbar to the input area
    :param enable_file_input: a boolean controlling whether a
        :class:`~pymeasure.display.widgets.fileinput_widget.FileInputWidget` to specify where the
        experiment's result will be saved is displayed (True, default) or not (False). This widget
        contains a field to enter the (base of the) filename (with or without extension; if absent,
        the extension will be appended). This field also allows for placeholders to use
        parameter-values and metadata-value in the filename. The widget also has a field to select
        the directory where the file is to be stored, and a toggle to control whether the data
        should be saved to the selected file, or not (i.e., to a temporary file instead).
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
                 inputs_in_scrollarea=False,
                 enable_file_input=True,
                 hide_groups=True,
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
        self.inputs_in_scrollarea = inputs_in_scrollarea
        self.enable_file_input = enable_file_input
        self.log = logging.getLogger(log_channel)
        self.log_level = log_level
        log.setLevel(log_level)
        self.log.setLevel(log_level)
        self.widget_list = widget_list

        # Check if the get_estimates function is reimplemented
        self.use_estimator = not self.procedure_class.get_estimates == Procedure.get_estimates

        # Validate DATA_COLUMNS fit pymeasure column header format
        Procedure.parse_columns(self.procedure_class.DATA_COLUMNS)

        self._setup_ui()
        self._layout()

    def _setup_ui(self):

        self.queue_button = QtWidgets.QPushButton('Queue', self)
        self.queue_button.clicked.connect(self._queue)

        self.abort_button = QtWidgets.QPushButton('Abort', self)
        self.abort_button.setEnabled(False)
        self.abort_button.clicked.connect(self.abort)

        self.browser_widget = BrowserWidget(
            self.procedure_class,
            self.displays,
            [],  # This value will be patched by subclasses, if needed
            parent=self
        )
        self.browser_widget.show_button.clicked.connect(self.show_experiments)
        self.browser_widget.hide_button.clicked.connect(self.hide_experiments)
        self.browser_widget.clear_button.clicked.connect(self.clear_experiments)
        self.browser_widget.open_button.clicked.connect(self.open_experiment)
        self.browser = self.browser_widget.browser

        self.browser.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.browser_item_menu)
        self.browser.itemChanged.connect(self.browser_item_changed)

        self.inputs = InputsWidget(
            self.procedure_class,
            self.inputs,
            parent=self,
            hide_groups=self.hide_groups,
            inputs_in_scrollarea=self.inputs_in_scrollarea,
        )
        if self.enable_file_input:
            self.file_input = FileInputWidget(parent=self)

        self.manager = Manager(self.widget_list,
                               self.browser,
                               log_level=self.log_level,
                               parent=self)
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

        if self.use_estimator:
            self.estimator = EstimatorWidget(
                parent=self
            )

    def _layout(self):
        self.main = QtWidgets.QWidget(self)

        inputs_dock = QtWidgets.QWidget(self)
        inputs_vbox = QtWidgets.QVBoxLayout(self.main)

        queue_abort_hbox = QtWidgets.QHBoxLayout()
        queue_abort_hbox.setSpacing(10)
        queue_abort_hbox.setContentsMargins(-1, 6, -1, 6)
        queue_abort_hbox.addWidget(self.queue_button)
        queue_abort_hbox.addWidget(self.abort_button)
        queue_abort_hbox.addStretch()

        inputs_vbox.addWidget(self.inputs)
        inputs_vbox.addSpacing(15)
        if self.enable_file_input:
            inputs_vbox.addWidget(self.file_input)
            inputs_vbox.addSpacing(15)

        inputs_vbox.addLayout(queue_abort_hbox)

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
        splitter.addWidget(self.browser_widget)

        vbox = QtWidgets.QVBoxLayout(self.main)
        vbox.setSpacing(0)
        vbox.addWidget(splitter)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(1000, 800)

    def quit(self, evt=None):
        if self.manager.is_running():
            self.abort()

        self.close()

    def browser_item_changed(self, item, column):
        if column == 0:
            state = item.checkState(0)
            experiment = self.manager.experiments.with_browser_item(item)
            if state == QtCore.Qt.CheckState.Unchecked:
                for curve in experiment.curve_list:
                    if curve:
                        curve.wdg.remove(curve)
            else:
                for curve in experiment.curve_list:
                    if curve:
                        curve.wdg.load(curve)

    def browser_item_menu(self, position):
        item = self.browser.itemAt(position)

        if item is not None:
            experiment = self.manager.experiments.with_browser_item(item)

            menu = QtWidgets.QMenu(self)

            # Open
            action_open = QtGui.QAction(menu)
            action_open.setText("Open Data Externally")
            action_open.triggered.connect(
                lambda: self.open_file_externally(experiment.results.data_filename))
            menu.addAction(action_open)

            # Reveal in file explorer
            action_reveal = QtGui.QAction(menu)
            action_reveal.setText("Reveal in File Explorer")
            action_reveal.triggered.connect(
                lambda: self.reveal_in_file_explorer(experiment.results.data_filename))
            menu.addAction(action_reveal)

            # Save a copy of the datafile
            action_save = QtGui.QAction(menu)
            action_save.setText("Save Data File Copy")
            action_save.triggered.connect(
                lambda: self.save_experiment_copy(experiment.results.data_filename))
            menu.addAction(action_save)

            # Change Color
            action_change_color = QtGui.QAction(menu)
            action_change_color.setText("Change Color")
            action_change_color.triggered.connect(
                lambda: self.change_color(experiment))
            menu.addAction(action_change_color)

            # Remove
            action_remove = QtGui.QAction(menu)
            action_remove.setText("Remove Graph")
            if self.manager.is_running():
                if self.manager.running_experiment() == experiment:  # Experiment running
                    action_remove.setEnabled(False)
            action_remove.triggered.connect(lambda: self.remove_experiment(experiment))
            menu.addAction(action_remove)

            # Delete
            action_delete = QtGui.QAction(menu)
            action_delete.setText("Delete Data File")
            if self.manager.is_running():
                if self.manager.running_experiment() == experiment:  # Experiment running
                    action_delete.setEnabled(False)
            action_delete.triggered.connect(lambda: self.delete_experiment_data(experiment))
            menu.addAction(action_delete)

            # Use parameters
            action_use = QtGui.QAction(menu)
            action_use.setText("Use These Parameters")
            action_use.triggered.connect(
                lambda: self.set_parameters(experiment.procedure.parameter_objects()))
            menu.addAction(action_use)
            menu.exec(self.browser.viewport().mapToGlobal(position))

    def remove_experiment(self, experiment):
        reply = QtWidgets.QMessageBox.question(self, 'Remove Graph',
                                               "Are you sure you want to remove the graph?",
                                               QtWidgets.QMessageBox.StandardButton.Yes |
                                               QtWidgets.QMessageBox.StandardButton.No,
                                               QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.manager.remove(experiment)

    def delete_experiment_data(self, experiment):
        reply = QtWidgets.QMessageBox.question(self, 'Delete Data',
                                               "Are you sure you want to delete this data file?",
                                               QtWidgets.QMessageBox.StandardButton.Yes |
                                               QtWidgets.QMessageBox.StandardButton.No,
                                               QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.manager.remove(experiment)
            os.unlink(experiment.data_filename)

    def show_experiments(self):
        root = self.browser.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, QtCore.Qt.CheckState.Checked)

    def hide_experiments(self):
        root = self.browser.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

    def clear_experiments(self):
        self.manager.clear()

    def open_experiment(self):
        dialog = ResultsDialog(self.procedure_class,
                               widget_list=self.widget_list)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            for filename in map(str, filenames):
                if filename in self.manager.experiments:
                    QtWidgets.QMessageBox.warning(
                        self, "Load Error",
                        "The file %s cannot be opened twice." % os.path.basename(filename)
                    )
                elif filename == '':
                    return
                else:
                    results = Results.load(filename)
                    experiment = self.new_experiment(results)
                    for curve in experiment.curve_list:
                        if curve:
                            curve.update_data()
                    experiment.browser_item.progressbar.setValue(100)
                    self.manager.load(experiment)
                    log.info('Opened data file %s' % filename)

    def save_experiment_copy(self, source_filename):
        """Save a copy of the datafile to a selected folder and file.
        Primarily useful for experiments that are stored in a temporary file.
        """
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setDefaultSuffix('.csv')

        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            shutil.copy2(source_filename, filename)

            log.info(f"Copied data from '{source_filename}' to '{filename}'.")

    def change_color(self, experiment):
        color = QtWidgets.QColorDialog.getColor(
            parent=self)
        if color.isValid():
            pixelmap = QtGui.QPixmap(24, 24)
            pixelmap.fill(color)
            experiment.browser_item.setIcon(0, QtGui.QIcon(pixelmap))
            for curve in experiment.curve_list:
                if curve:
                    curve.wdg.set_color(curve, color=color)

    def open_file_externally(self, filename):
        """ Method to open the datafile using an external editor or viewer. Uses the default
        application to open a datafile of this filetype, but can be overridden by the child
        class in order to open the file in another application of choice.
        """
        system = platform.system()
        if (system == 'Windows'):
            # The empty argument after the start is needed to be able to cope
            # correctly with filenames with spaces
            _ = subprocess.Popen(['start', '', filename], shell=True)
        elif (system == 'Linux'):
            _ = subprocess.Popen(['xdg-open', filename])
        elif (system == 'Darwin'):
            _ = subprocess.Popen(['open', filename])
        else:
            raise Exception("{cls} method open_file_externally does not support {system} OS".format(
                cls=type(self).__name__, system=system))

    def reveal_in_file_explorer(self, filename: str) -> None:
        """Method to open the file explorer at the location of the given filename.

        Args:
            filename (str): Path to the file to be revealed in the file explorer.
        """

        path = os.path.normpath(filename)
        system = platform.system()
        if system == "Windows":
            _ = subprocess.Popen(["explorer", "/select,", path], shell=True)
        elif system == "Linux":
            _ = subprocess.Popen(["xdg-open", os.path.dirname(path)])
        elif system == "Darwin":
            _ = subprocess.Popen(["open", "-R", path])
        else:
            raise Exception(
                "{cls} method reveal_in_file_explorer does not support {system} OS".format(
                    cls=type(self).__name__, system=system
                )
            )

    def make_procedure(self):
        if not isinstance(self.inputs, InputsWidget):
            raise Exception("ManagedWindow can not make a Procedure"
                            " without a InputsWidget type")
        return self.inputs.get_procedure()

    def new_curve(self, wdg, results, color=None, **kwargs):
        if color is None:
            color = pg.intColor(self.browser.topLevelItemCount() % 8)
        return wdg.new_curve(results, color=color, **kwargs)

    def new_experiment(self, results, curve=None):
        if curve is None:
            curve_list = []
            for wdg in self.widget_list:
                new_curve = self.new_curve(wdg, results)
                if isinstance(new_curve, (tuple, list)):
                    curve_list.extend(new_curve)
                else:
                    curve_list.append(new_curve)
        else:
            curve_list = curve[:]

        curve_color = pg.intColor(0)
        for curve in curve_list:
            if hasattr(curve, 'color'):
                curve_color = curve.color
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
        """ Queue a measurement based on the parameters in the input-widget.

        Semi-abstract method, which must be overridden by the child class if the filename- and
        directory-inputs are disabled. When filename- and directory inputs are enabled, overwriting
        is not required, but can be done for custom naming, input processing, or other features.

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

        # Check if the filename and the directory inputs are available
        if not self.enable_file_input:
            raise NotImplementedError("Queue method must be overwritten if the filename- and "
                                      "directory-inputs are disabled.")

        if procedure is None:
            procedure = self.make_procedure()

        if self.store_measurement:
            try:
                filename = unique_filename(
                    self.directory,
                    prefix=self.file_input.filename_base,
                    datetimeformat="",
                    procedure=procedure,
                    ext=self.file_input.filename_extension,
                )
            except KeyError as E:
                if not E.args[0].startswith("The following placeholder-keys are not valid:"):
                    raise E from None
                log.error(f"Invalid filename provided: {E.args[0]}")
                return
        else:
            filename = tempfile.mktemp(prefix='TempFile_', suffix='.csv')

        results = Results(procedure, filename)

        experiment = self.new_experiment(results)
        self.manager.queue(experiment)

    def abort(self):
        self.abort_button.setEnabled(False)
        self.abort_button.setText("Resume")
        self.abort_button.clicked.disconnect()
        self.abort_button.clicked.connect(self.resume)
        try:
            self.manager.abort()
        except:  # noqa
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
        self.browser_widget.show_button.setEnabled(True)
        self.browser_widget.hide_button.setEnabled(True)
        self.browser_widget.clear_button.setEnabled(True)

    def running(self, experiment):
        self.browser_widget.clear_button.setEnabled(False)

    def abort_returned(self, experiment):
        if self.manager.experiments.has_next():
            self.abort_button.setText("Resume")
            self.abort_button.setEnabled(True)
        else:
            self.browser_widget.clear_button.setEnabled(True)

    def finished(self, experiment):
        if not self.manager.experiments.has_next():
            self.abort_button.setEnabled(False)
            self.browser_widget.clear_button.setEnabled(True)

    @property
    def directory(self):
        if not self.enable_file_input:
            raise AttributeError("File-input widget not enabled (i.e., enable_file_input == False)")
        return self.file_input.directory

    @directory.setter
    def directory(self, value):
        if not self.enable_file_input:
            raise AttributeError("File-input widget not enabled (i.e., enable_file_input == False)")
        self.file_input.directory = value

    @property
    def filename(self):
        if not self.enable_file_input:
            raise AttributeError("File-input widget not enabled (i.e., enable_file_input == False)")
        return self.file_input.filename

    @filename.setter
    def filename(self, value):
        if not self.enable_file_input:
            raise AttributeError("File-input widget not enabled (i.e., enable_file_input == False)")
        self.file_input.filename = value

    @property
    def store_measurement(self):
        if not self.enable_file_input:
            raise AttributeError("File-input widget not enabled (i.e., enable_file_input == False)")
        return self.file_input.store_measurement

    @store_measurement.setter
    def store_measurement(self, value):
        if not self.enable_file_input:
            raise AttributeError("File-input widget not enabled (i.e., enable_file_input == False)")
        self.file_input.store_measurement = value


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
    :param log_fmt: formatting string for the log-widget
    :param log_datefmt: formatting string for the date in the log-widget
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.managed_window.ManagedWindowBase`

    """

    def __init__(self, procedure_class, x_axis=None, y_axis=None, linewidth=1,
                 log_fmt=None, log_datefmt=None, **kwargs):
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.log_widget = LogWidget("Experiment Log", fmt=log_fmt, datefmt=log_datefmt)
        self.plot_widget = PlotWidget("Results Graph", procedure_class.DATA_COLUMNS, self.x_axis,
                                      self.y_axis, linewidth=linewidth)
        self.plot_widget.setMinimumSize(100, 200)

        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.plot_widget, self.log_widget)

        super().__init__(procedure_class, **kwargs)

        # Setup measured_quantities once we know x_axis and y_axis
        self.browser_widget.browser.measured_quantities.update([self.x_axis, self.y_axis])

        logging.getLogger().addHandler(self.log_widget.handler)  # needs to be in Qt context?
        log.setLevel(self.log_level)
        log.info("ManagedWindow connected to logging")
