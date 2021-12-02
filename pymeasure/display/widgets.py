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
import re
import pyqtgraph as pg
from functools import partial
import numpy
from collections import ChainMap
from itertools import product
from inspect import signature
from datetime import datetime, timedelta

from .browser import Browser
from .curves import ResultsCurve, Crosshairs, ResultsImage
from .inputs import BooleanInput, IntegerInput, ListInput, ScientificInput, StringInput
from .thread import StoppableQThread
from .log import LogHandler
from .Qt import QtCore, QtGui
from ..experiment import parameters, Procedure
from ..experiment.results import Results

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PlotFrame(QtGui.QFrame):
    """ Combines a PyQtGraph Plot with Crosshairs. Refreshes
    the plot based on the refresh_time, and allows the axes
    to be changed on the fly, which updates the plotted data
    """

    LABEL_STYLE = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}
    updated = QtCore.QSignal()
    ResultsClass = ResultsCurve
    x_axis_changed = QtCore.QSignal(str)
    y_axis_changed = QtCore.QSignal(str)

    def __init__(self, x_axis=None, y_axis=None, refresh_time=0.2, check_status=True, parent=None):
        super().__init__(parent)
        self.refresh_time = refresh_time
        self.check_status = check_status
        self._setup_ui()
        self.change_x_axis(x_axis)
        self.change_y_axis(y_axis)

    def _setup_ui(self):
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: #fff")
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Sunken)
        self.setMidLineWidth(1)

        vbox = QtGui.QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget(self, background='#ffffff')
        self.coordinates = QtGui.QLabel(self)
        self.coordinates.setMinimumSize(QtCore.QSize(0, 20))
        self.coordinates.setStyleSheet("background: #fff")
        self.coordinates.setText("")
        self.coordinates.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        vbox.addWidget(self.plot_widget)
        vbox.addWidget(self.coordinates)
        self.setLayout(vbox)

        self.plot = self.plot_widget.getPlotItem()

        self.crosshairs = Crosshairs(self.plot,
                                     pen=pg.mkPen(color='#AAAAAA', style=QtCore.Qt.DashLine))
        self.crosshairs.coordinates.connect(self.update_coordinates)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_curves)
        self.timer.timeout.connect(self.crosshairs.update)
        self.timer.timeout.connect(self.updated)
        self.timer.start(int(self.refresh_time * 1e3))

    def update_coordinates(self, x, y):
        self.coordinates.setText("(%g, %g)" % (x, y))

    def update_curves(self):
        for item in self.plot.items:
            if isinstance(item, self.ResultsClass):
                if self.check_status:
                    if item.results.procedure.status == Procedure.RUNNING:
                        item.update_data()
                else:
                    item.update_data()

    def parse_axis(self, axis):
        """ Returns the units of an axis by searching the string
        """
        units_pattern = r"\((?P<units>\w+)\)"
        try:
            match = re.search(units_pattern, axis)
        except TypeError:
            match = None

        if match:
            if 'units' in match.groupdict():
                label = re.sub(units_pattern, '', axis)
                return label, match.groupdict()['units']
        else:
            return axis, None

    def change_x_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, self.ResultsClass):
                item.x = axis
                item.update_data()
        label, units = self.parse_axis(axis)
        self.plot.setLabel('bottom', label, units=units, **self.LABEL_STYLE)
        self.x_axis = axis
        self.x_axis_changed.emit(axis)

    def change_y_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, self.ResultsClass):
                item.y = axis
                item.update_data()
        label, units = self.parse_axis(axis)
        self.plot.setLabel('left', label, units=units, **self.LABEL_STYLE)
        self.y_axis = axis
        self.y_axis_changed.emit(axis)

class ImageFrame(PlotFrame):
    """ Extends PlotFrame to plot also axis Z using colors
    """
    ResultsClass = ResultsImage
    z_axis_changed = QtCore.QSignal(str)

    def __init__(self, x_axis, y_axis, z_axis=None, refresh_time=0.2, check_status=True, parent=None):
        super().__init__(x_axis, y_axis, refresh_time, check_status, parent)
        self.change_z_axis(z_axis)

    def change_z_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, self.ResultsClass):
                item.z = axis
                item.update_data()
        label, units = self.parse_axis(axis)
        if units is not None:
            self.plot.setTitle(label + ' (%s)'%units)
        else:
            self.plot.setTitle(label)
        self.z_axis = axis
        self.z_axis_changed.emit(axis)

class TabWidget(object):
    """ Utility class to define default implementation for some basic methods.

        When defining a widget to be used in subclasses of ManagedWindowBase, users should inherit
        from this class and provide the specialized implementation of these method's
    """

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def new_curve(self, *args, **kwargs):
        """ Create a new curve """
        return None

    def load(self, curve):
        """ Add curve to widget """
        pass

    def remove(self, curve):
        """ Remove curve from widget """
        pass

    def set_color(self, curve, color):
        """ Set color for widget """
        pass

class PlotWidget(TabWidget, QtGui.QWidget):
    """ Extends the PlotFrame to allow different columns
    of the data to be dynamically choosen
    """

    def __init__(self, name, columns, x_axis=None, y_axis=None, refresh_time=0.2,
                 check_status=True, linewidth=1, parent=None):
        super().__init__(name, parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.check_status = check_status
        self.linewidth = linewidth
        self._setup_ui()
        self._layout()
        if x_axis is not None:
            self.columns_x.setCurrentIndex(self.columns_x.findText(x_axis))
            self.plot_frame.change_x_axis(x_axis)
        if y_axis is not None:
            self.columns_y.setCurrentIndex(self.columns_y.findText(y_axis))
            self.plot_frame.change_y_axis(y_axis)

    def _setup_ui(self):
        self.columns_x_label = QtGui.QLabel(self)
        self.columns_x_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_x_label.setText('X Axis:')
        self.columns_y_label = QtGui.QLabel(self)
        self.columns_y_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_y_label.setText('Y Axis:')

        self.columns_x = QtGui.QComboBox(self)
        self.columns_y = QtGui.QComboBox(self)
        for column in self.columns:
            self.columns_x.addItem(column)
            self.columns_y.addItem(column)
        self.columns_x.activated.connect(self.update_x_column)
        self.columns_y.activated.connect(self.update_y_column)

        self.plot_frame = PlotFrame(
            self.columns[0],
            self.columns[1],
            self.refresh_time,
            self.check_status
        )
        self.updated = self.plot_frame.updated
        self.plot = self.plot_frame.plot
        self.columns_x.setCurrentIndex(0)
        self.columns_y.setCurrentIndex(1)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.columns_x_label)
        hbox.addWidget(self.columns_x)
        hbox.addWidget(self.columns_y_label)
        hbox.addWidget(self.columns_y)

        vbox.addLayout(hbox)
        vbox.addWidget(self.plot_frame)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(color=color, width=self.linewidth)
        if 'antialias' not in kwargs:
            kwargs['antialias'] = False
        curve = ResultsCurve(results,
                             x=self.plot_frame.x_axis,
                             y=self.plot_frame.y_axis,
                             **kwargs
                             )
        curve.setSymbol(None)
        curve.setSymbolBrush(None)
        return curve

    def update_x_column(self, index):
        axis = self.columns_x.itemText(index)
        self.plot_frame.change_x_axis(axis)

    def update_y_column(self, index):
        axis = self.columns_y.itemText(index)
        self.plot_frame.change_y_axis(axis)

    def load(self, curve):
        curve.x = self.columns_x.currentText()
        curve.y = self.columns_y.currentText()
        curve.update_data()
        self.plot.addItem(curve)

    def remove(self, curve):
        self.plot.removeItem(curve)

    def set_color(self, curve, color):
        """ Change the color of the pen of the curve """
        curve.pen.setColor(color)
        curve.updateItems(styleUpdate=True)

class ImageWidget(TabWidget, QtGui.QWidget):
    """ Extends the ImageFrame to allow different columns
    of the data to be dynamically choosen
    """

    def __init__(self, name, columns, x_axis, y_axis, z_axis=None, refresh_time=0.2, check_status=True,
                 parent=None):
        super().__init__(name, parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.check_status = check_status
        self.x_axis = x_axis
        self.y_axis = y_axis
        self._setup_ui()
        self._layout()
        if z_axis is not None:
            self.columns_z.setCurrentIndex(self.columns_z.findText(z_axis))
            self.image_frame.change_z_axis(z_axis)

    def _setup_ui(self):
        self.columns_z_label = QtGui.QLabel(self)
        self.columns_z_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_z_label.setText('Z Axis:')

        self.columns_z = QtGui.QComboBox(self)
        for column in self.columns:
            self.columns_z.addItem(column)
        self.columns_z.activated.connect(self.update_z_column)

        self.image_frame = ImageFrame(
            self.x_axis,
            self.y_axis,
            self.columns[0],
            self.refresh_time,
            self.check_status
        )
        self.updated = self.image_frame.updated
        self.plot = self.image_frame.plot
        self.columns_z.setCurrentIndex(2)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.columns_z_label)
        hbox.addWidget(self.columns_z)


        vbox.addLayout(hbox)
        vbox.addWidget(self.image_frame)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        """ Creates a new image """
        image = ResultsImage(results,
                             x=self.image_frame.x_axis,
                             y=self.image_frame.y_axis,
                             z=self.image_frame.z_axis
                             )
        return image

    def update_z_column(self, index):
        axis = self.columns_z.itemText(index)
        self.image_frame.change_z_axis(axis)

    def load(self, curve):
        curve.z = self.columns_z.currentText()
        curve.update_data()
        self.plot.addItem(curve)

    def remove(self, curve):
        self.plot.removeItem(curve)

class BrowserWidget(QtGui.QWidget):
    def __init__(self, *args, parent=None):
        super().__init__(parent)
        self.browser_args = args
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.browser = Browser(*self.browser_args, parent=self)
        self.clear_button = QtGui.QPushButton('Clear all', self)
        self.clear_button.setEnabled(False)
        self.hide_button = QtGui.QPushButton('Hide all', self)
        self.hide_button.setEnabled(False)
        self.show_button = QtGui.QPushButton('Show all', self)
        self.show_button.setEnabled(False)
        self.open_button = QtGui.QPushButton('Open', self)
        self.open_button.setEnabled(True)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.show_button)
        hbox.addWidget(self.hide_button)
        hbox.addWidget(self.clear_button)
        hbox.addStretch()
        hbox.addWidget(self.open_button)

        vbox.addLayout(hbox)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)

class InputsWidget(QtGui.QWidget):
    # tuple of Input classes that do not need an external label
    NO_LABEL_INPUTS = (BooleanInput,)

    def __init__(self, procedure_class, inputs=(), parent=None, hide_groups=True):
        super().__init__(parent)
        self._procedure_class = procedure_class
        self._procedure = procedure_class()
        self._inputs = inputs
        self._setup_ui()
        self._layout()
        self._hide_groups = hide_groups
        self._setup_visibility_groups()

    def _setup_ui(self):
        parameter_objects = self._procedure.parameter_objects()
        for name in self._inputs:
            parameter = parameter_objects[name]
            if parameter.ui_class is not None:
                element = parameter.ui_class(parameter)

            elif isinstance(parameter, parameters.FloatParameter):
                element = ScientificInput(parameter)

            elif isinstance(parameter, parameters.IntegerParameter):
                element = IntegerInput(parameter)

            elif isinstance(parameter, parameters.BooleanParameter):
                element = BooleanInput(parameter)

            elif isinstance(parameter, parameters.ListParameter):
                element = ListInput(parameter)

            elif isinstance(parameter, parameters.Parameter):
                element = StringInput(parameter)

            setattr(self, name, element)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(6)

        self.labels = {}
        parameters = self._procedure.parameter_objects()
        for name in self._inputs:
            if not isinstance(getattr(self, name), self.NO_LABEL_INPUTS):
                label = QtGui.QLabel(self)
                label.setText("%s:" % parameters[name].name)
                vbox.addWidget(label)
                self.labels[name] = label

            vbox.addWidget(getattr(self, name))

        self.setLayout(vbox)

    def _setup_visibility_groups(self):
        groups = {}
        parameters = self._procedure.parameter_objects()
        for name in self._inputs:
            parameter = parameters[name]

            group_state = {g: True for g in parameter.group_by}

            for group_name, condition in parameter.group_by.items():
                if group_name not in self._inputs or group_name == name:
                    continue

                if isinstance(getattr(self, group_name), BooleanInput):
                    # Adjust the boolean condition to a condition suitable for a checkbox
                    condition = QtCore.Qt.CheckState.Checked if condition else QtCore.Qt.CheckState.Unchecked

                if group_name not in groups:
                    groups[group_name] = []

                groups[group_name].append((name, condition, group_state))

        for group_name, group in groups.items():
            toggle = partial(self.toggle_group, group_name=group_name, group=group)
            group_el = getattr(self, group_name)
            if isinstance(group_el, BooleanInput):
                group_el.stateChanged.connect(toggle)
                toggle(group_el.checkState())
            elif isinstance(group_el, StringInput):
                group_el.textChanged.connect(toggle)
                toggle(group_el.text())
            elif isinstance(group_el, (IntegerInput, ScientificInput)):
                group_el.valueChanged.connect(toggle)
                toggle(group_el.value())
            elif isinstance(group_el, ListInput):
                group_el.currentTextChanged.connect(toggle)
                toggle(group_el.currentText())
            else:
                raise NotImplementedError(
                    "Grouping based on %s (%s) is not implemented." % (group_name, group_el))

    def toggle_group(self, state, group_name, group):
        for (name, condition, group_state) in group:
            if callable(condition):
                group_state[group_name] = condition(state)
            else:
                group_state[group_name] = (state == condition)

            visible = all(group_state.values())

            if self._hide_groups:
                getattr(self, name).setHidden(not visible)
            else:
                getattr(self, name).setDisabled(not visible)

            if name in self.labels:
                if self._hide_groups:
                    self.labels[name].setHidden(not visible)
                else:
                    self.labels[name].setDisabled(not visible)

    def set_parameters(self, parameter_objects):
        for name in self._inputs:
            element = getattr(self, name)
            element.set_parameter(parameter_objects[name])

    def get_procedure(self):
        """ Returns the current procedure """
        self._procedure = self._procedure_class()
        parameter_values = {}
        for name in self._inputs:
            element = getattr(self, name)
            parameter_values[name] = element.parameter.value
        self._procedure.set_parameters(parameter_values)
        return self._procedure

class LogWidget(TabWidget, QtGui.QWidget):
    """ Widget to display logging information in GUI

    It is recommended to include this widget in all subclasses of ManagedWindowBase
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
        self.handler = LogHandler()
        self.handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s : %(message)s (%(levelname)s)',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        ))
        self.handler.connect(self.view.appendPlainText)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.view)
        self.setLayout(vbox)

class ResultsDialog(QtGui.QFileDialog):
    def __init__(self, columns, x_axis=None, y_axis=None, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.x_axis, self.y_axis = x_axis, y_axis
        self.setOption(QtGui.QFileDialog.DontUseNativeDialog, True)
        self._setup_ui()

    def _setup_ui(self):
        preview_tab = QtGui.QTabWidget()
        vbox = QtGui.QVBoxLayout()
        param_vbox = QtGui.QVBoxLayout()
        vbox_widget = QtGui.QWidget()
        param_vbox_widget = QtGui.QWidget()

        self.plot_widget = PlotWidget("Results", self.columns, self.x_axis, self.y_axis, parent=self)
        self.plot = self.plot_widget.plot
        self.preview_param = QtGui.QTreeWidget()
        param_header = QtGui.QTreeWidgetItem(["Name", "Value"])
        self.preview_param.setHeaderItem(param_header)
        self.preview_param.setColumnWidth(0, 150)
        self.preview_param.setAlternatingRowColors(True)

        vbox.addWidget(self.plot_widget)
        param_vbox.addWidget(self.preview_param)
        vbox_widget.setLayout(vbox)
        param_vbox_widget.setLayout(param_vbox)
        preview_tab.addTab(vbox_widget, "Plot Preview")
        preview_tab.addTab(param_vbox_widget, "Run Parameters")
        self.layout().addWidget(preview_tab, 0, 5, 4, 1)
        self.layout().setColumnStretch(5, 1)
        self.setMinimumSize(900, 500)
        self.resize(900, 500)

        self.setFileMode(QtGui.QFileDialog.ExistingFiles)
        self.currentChanged.connect(self.update_plot)

    def update_plot(self, filename):
        self.plot.clear()
        if not os.path.isdir(filename) and filename != '':
            try:
                results = Results.load(str(filename))
            except ValueError:
                return
            except Exception as e:
                raise e

            curve = ResultsCurve(results,
                                 x=self.plot_widget.plot_frame.x_axis,
                                 y=self.plot_widget.plot_frame.y_axis,
                                 # The pyqtgraph pen width was changed to 1 (originally: 1.75) to circumvent plotting slowdown.
                                 # Once the issue (https://github.com/pyqtgraph/pyqtgraph/issues/533) is resolved it can be reverted
                                 pen=pg.mkPen(color=(255, 0, 0), width=1),
                                 antialias=True
                                 )
            curve.update_data()

            self.plot.addItem(curve)

            self.preview_param.clear()
            for key, param in results.procedure.parameter_objects().items():
                new_item = QtGui.QTreeWidgetItem([param.name, str(param)])
                self.preview_param.addTopLevelItem(new_item)
            self.preview_param.sortItems(0, QtCore.Qt.AscendingOrder)


""" This defines a list of functions that can be used to generate a sequence. """
SAFE_FUNCTIONS = {
    'range': range,
    'sorted': sorted,
    'list': list,
    'arange': numpy.arange,
    'linspace': numpy.linspace,
    'arccos': numpy.arccos,
    'arcsin': numpy.arcsin,
    'arctan': numpy.arctan,
    'arctan2': numpy.arctan2,
    'ceil': numpy.ceil,
    'cos': numpy.cos,
    'cosh': numpy.cosh,
    'degrees': numpy.degrees,
    'e': numpy.e,
    'exp': numpy.exp,
    'fabs': numpy.fabs,
    'floor': numpy.floor,
    'fmod': numpy.fmod,
    'frexp': numpy.frexp,
    'hypot': numpy.hypot,
    'ldexp': numpy.ldexp,
    'log': numpy.log,
    'log10': numpy.log10,
    'modf': numpy.modf,
    'pi': numpy.pi,
    'power': numpy.power,
    'radians': numpy.radians,
    'sin': numpy.sin,
    'sinh': numpy.sinh,
    'sqrt': numpy.sqrt,
    'tan': numpy.tan,
    'tanh': numpy.tanh,
}


class SequenceEvaluationException(Exception):
    """Raised when the evaluation of a sequence string goes wrong."""
    pass


class SequencerWidget(QtGui.QWidget):
    """
    Widget that allows to generate a sequence of measurements with varying
    parameters. Moreover, one can write a simple text file to easily load a
    sequence.

    Currently requires a queue function of the ManagedWindow to have a
    "procedure" argument.
    """

    MAXDEPTH = 10

    def __init__(self, inputs=None, sequence_file=None, parent=None):
        super().__init__(parent)
        self._parent = parent

        self._check_queue_signature()

        # if no explicit inputs are given, use the displayed parameters
        if inputs is not None:
            self._inputs = inputs
        else:
            self._inputs = self._parent.displays

        self._get_properties()
        self._setup_ui()
        self._layout()

        # Load the sequence file if supplied.
        if sequence_file is not None:
            self.load_sequence(fileName=sequence_file)

    def _check_queue_signature(self):
        """
        Check if the call signature of the implementation of the`ManagedWindow.queue`
        method accepts the `procedure` keyword argument, which is required for using
        the sequencer.
        """

        call_signature = signature(self._parent.queue)

        if 'procedure' not in call_signature.parameters:
            raise AttributeError(
                "The queue method of of the ManagedWindow does not accept the 'procedure'"
                "keyword argument. Accepting this keyword argument is required when using"
                "the 'SequencerWidget'."
            )

    def _get_properties(self):
        """
        Obtain the names of the input parameters.
        """

        parameter_objects = self._parent.procedure_class().parameter_objects()

        self.names = {key: parameter.name
                      for key, parameter
                      in parameter_objects.items()
                      if key in self._inputs}

        self.names_inv = {name: key for key, name in self.names.items()}

    def _setup_ui(self):
        self.tree = QtGui.QTreeWidget(self)
        self.tree.setHeaderLabels(["Level", "Parameter", "Sequence"])
        width = self.tree.viewport().size().width()
        self.tree.setColumnWidth(0, int(0.7 * width))
        self.tree.setColumnWidth(1, int(0.9 * width))
        self.tree.setColumnWidth(2, int(0.9 * width))

        self.add_root_item_btn = QtGui.QPushButton("Add root item")
        self.add_root_item_btn.clicked.connect(
            partial(self._add_tree_item, level=0)
        )

        self.add_tree_item_btn = QtGui.QPushButton("Add item")
        self.add_tree_item_btn.clicked.connect(self._add_tree_item)

        self.remove_tree_item_btn = QtGui.QPushButton("Remove item")
        self.remove_tree_item_btn.clicked.connect(self._remove_selected_tree_item)

        self.load_seq_button = QtGui.QPushButton("Load sequence")
        self.load_seq_button.clicked.connect(self.load_sequence)
        self.load_seq_button.setToolTip("Load a sequence from a file.")

        self.queue_button = QtGui.QPushButton("Queue sequence")
        self.queue_button.clicked.connect(self.queue_sequence)

    def _layout(self):
        btn_box = QtGui.QHBoxLayout()
        btn_box.addWidget(self.add_root_item_btn)
        btn_box.addWidget(self.add_tree_item_btn)
        btn_box.addWidget(self.remove_tree_item_btn)

        btn_box_2 = QtGui.QHBoxLayout()
        btn_box_2.addWidget(self.load_seq_button)
        btn_box_2.addWidget(self.queue_button)

        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(6)
        vbox.addWidget(self.tree)
        vbox.addLayout(btn_box)
        vbox.addLayout(btn_box_2)
        self.setLayout(vbox)

    def _add_tree_item(self, *, level=None, parameter=None, sequence=None):
        """
        Add an item to the sequence tree. An item will be added as a child
        to the selected (existing) item, except when level is given.

        :param level: An integer value determining the level at which an
            item is added. If level is 0, a root item will be added.

        :param parameter: If given, the parameter field is pre-filled
        :param sequence: If given, the sequence field is pre-filled
        """

        selected = self.tree.selectedItems()

        if len(selected) >= 1 and level != 0:
            parent = selected[0]
        else:
            parent = self.tree.invisibleRootItem()

        if level is not None and level > 0:
            p_depth = self._depth_of_child(parent)

            while p_depth > level - 1:
                parent = parent.parent()
                p_depth = self._depth_of_child(parent)

        comboBox = QtGui.QComboBox()
        lineEdit = QtGui.QLineEdit()

        comboBox.addItems(list(sorted(self.names_inv.keys())))

        item = QtGui.QTreeWidgetItem(parent, [""])
        depth = self._depth_of_child(item)
        item.setText(0, "{:d}".format(depth))

        self.tree.setItemWidget(item, 1, comboBox)
        self.tree.setItemWidget(item, 2, lineEdit)

        self.tree.expandAll()

        for selected_item in selected:
            selected_item.setSelected(False)

        if parameter is not None:
            idx = self.tree.itemWidget(item, 1).findText(parameter)
            self.tree.itemWidget(item, 1).setCurrentIndex(idx)
            if idx == -1:
                log.error(
                    "Parameter '{}' not found while loading sequence".format(
                        parameter) + ", probably mistyped."
                )

        if sequence is not None:
            self.tree.itemWidget(item, 2).setText(sequence)

        item.setSelected(True)

    def _remove_selected_tree_item(self):
        """
        Remove the selected item (and any child items) from the sequence tree.
        """

        selected = self.tree.selectedItems()
        if len(selected) == 0:
            return

        item = selected[0]
        parent = item.parent()

        if parent is None:
            parent = self.tree.invisibleRootItem()

        parent.removeChild(item)

        for selected_item in self.tree.selectedItems():
            selected_item.setSelected(False)

        parent.setSelected(True)

    def queue_sequence(self):
        """
        Obtain a list of parameters from the sequence tree, enter these into
        procedures, and queue these procedures.
        """

        self.queue_button.setEnabled(False)

        try:
            sequence = self.get_sequence_from_tree()
        except SequenceEvaluationException:
            log.error("Evaluation of one of the sequence strings went wrong, no sequence queued.")
        else:
            log.info(
                "Queuing %d measurements based on the entered sequences." % len(sequence)
            )

            for entry in sequence:
                QtGui.QApplication.processEvents()
                parameters = dict(ChainMap(*entry[::-1]))

                procedure = self._parent.make_procedure()
                procedure.set_parameters(parameters)
                self._parent.queue(procedure=procedure)

        finally:
            self.queue_button.setEnabled(True)

    def load_sequence(self, *, fileName=None):
        """
        Load a sequence from a .txt file.

        :param fileName: Filename (string) of the to-be-loaded file.
        """

        if fileName is None:
            fileName, _ = QtGui.QFileDialog.getOpenFileName(self, 'OpenFile')

        if len(fileName) == 0:
            return

        content = []

        with open(fileName, "r") as file:
            content = file.readlines()

        pattern = re.compile("([-]+) \"(.*?)\", \"(.*?)\"")
        for line in content:
            line = line.strip()
            match = pattern.search(line)

            if not match:
                continue

            level = len(match.group(1)) - 1

            if level < 0:
                continue

            parameter = match.group(2)
            sequence = match.group(3)

            self._add_tree_item(
                level=level, 
                parameter=parameter, 
                sequence=sequence,
            )

    def get_sequence_from_tree(self):
        """
        Generate a list of parameters from the sequence tree.
        """

        iterator = QtGui.QTreeWidgetItemIterator(self.tree)
        sequences = []
        current_sequence = [[] for i in range(self.MAXDEPTH)]
        temp_sequence = [[] for i in range(self.MAXDEPTH)]

        while iterator.value():
            item = iterator.value()
            depth = self._depth_of_child(item)

            name = self.tree.itemWidget(item, 1).currentText()
            parameter = self.names_inv[name]
            values = self.eval_string(
                self.tree.itemWidget(item, 2).text(),
                name, depth,
            )

            try:
                sequence_entry = [{parameter: value} for value in values]
            except TypeError:
                log.error(
                    "TypeError, likely no sequence for one of the parameters"
                )
            else:
                current_sequence[depth].extend(sequence_entry)

            iterator += 1
            next_depth = self._depth_of_child(iterator.value())

            for depth_idx in range(depth, next_depth, -1):
                temp_sequence[depth_idx].extend(current_sequence[depth_idx])

                if depth_idx != 0:
                    sequence_products = list(product(
                        current_sequence[depth_idx - 1],
                        temp_sequence[depth_idx]
                    ))

                    for i in range(len(sequence_products)):
                        try:
                            element = sequence_products[i][1]
                        except IndexError:
                            log.error(
                                "IndexError, likely empty nested parameter"
                            )
                        else:
                            if isinstance(element, tuple):
                                sequence_products[i] = (
                                    sequence_products[i][0], *element)

                    temp_sequence[depth_idx - 1].extend(sequence_products)
                    temp_sequence[depth_idx] = []

                current_sequence[depth_idx] = []
                current_sequence[depth_idx - 1] = []

            if depth == next_depth:
                temp_sequence[depth].extend(current_sequence[depth])
                current_sequence[depth] = []

        sequences = temp_sequence[0]

        for idx in range(len(sequences)):
            if not isinstance(sequences[idx], tuple):
                sequences[idx] = (sequences[idx],)

        return sequences

    @staticmethod
    def _depth_of_child(item):
        """
        Determine the level / depth of a child item in the sequence tree.
        """

        depth = -1
        while item:
            item = item.parent()
            depth += 1
        return depth

    @staticmethod
    def eval_string(string, name=None, depth=None):
        """
        Evaluate the given string. The string is evaluated using a list of
        pre-defined functions that are deemed safe to use, to prevent the
        execution of malicious code. For this purpose, also any built-in
        functions or global variables are not available.

        :param string: String to be interpreted.
        :param name: Name of the to-be-interpreted string, only used for
            error messages.
        :param depth: Depth of the to-be-interpreted string, only used
            for error messages.
        """

        evaluated_string = None
        if len(string) > 0:
            try:
                evaluated_string = eval(
                    string, {"__builtins__": None}, SAFE_FUNCTIONS
                )
            except TypeError:
                log.error("TypeError, likely a typo in one of the " +
                          "functions for parameter '{}', depth {}".format(
                              name, depth
                          ))
                raise SequenceEvaluationException()
            except SyntaxError:
                log.error("SyntaxError, likely unbalanced brackets " +
                          "for parameter '{}', depth {}".format(name, depth))
                raise SequenceEvaluationException()
            except ValueError:
                log.error("ValueError, likely wrong function argument " +
                          "for parameter '{}', depth {}".format(name, depth))
                raise SequenceEvaluationException()
        else:
            log.error("No sequence entered for " +
                      "for parameter '{}', depth {}".format(name, depth))
            raise SequenceEvaluationException()

        evaluated_string = numpy.array(evaluated_string)
        return evaluated_string

class DirectoryLineEdit(QtGui.QLineEdit):
    """
    Widget that allows to choose a directory path.
    A completer is implemented for quick completion.
    A browse button is available.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        completer = QtGui.QCompleter(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)

        model = QtGui.QDirModel(completer)
        model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Drives | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        completer.setModel(model)

        self.setCompleter(completer)

        browse_action = QtGui.QAction(self)
        browse_action.setIcon(self.style().standardIcon(getattr(QtGui.QStyle, 'SP_DialogOpenButton')))
        browse_action.triggered.connect(self.browse_triggered)

        self.addAction(browse_action, QtGui.QLineEdit.TrailingPosition)

    def browse_triggered(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, 'Directory', '/')
        if path != '':
            self.setText(path)


class EstimatorThread(StoppableQThread):
    new_estimates = QtCore.QSignal(list)

    def __init__(self, get_estimates_callable):
        StoppableQThread.__init__(self)

        self._get_estimates = get_estimates_callable

        self.delay = 2

    def __del__(self):
        self.wait()

    def run(self):
        self._should_stop.clear()

        while not self._should_stop.wait(self.delay):
            estimates = self._get_estimates()
            self.new_estimates.emit(estimates)


class EstimatorWidget(QtGui.QWidget):
    """
    Widget that allows to display up-front estimates of the measurement
    procedure.

    This widget relies on a `get_estimates` method of the `Procedure` class.
    `get_estimates` is expected to return a list of tuples, where each tuple
    contains two strings: a label and the estimate.

    If the `SequencerWidget` is also used, it is possible to ask for the
    current sequencer or its length by asking for two keyword arguments in the
    Implementation of the `get_estimates` function: `sequence` and
    `sequence_length`, respectively.

    """
    provide_sequence = False
    provide_sequence_length = False
    number_of_estimates = 0
    sequencer = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent

        self.check_get_estimates_signature()

        self.update_thread = EstimatorThread(self.get_estimates)
        self.update_thread.new_estimates.connect(self.display_estimates)

        self._setup_ui()
        self._layout()

        self.update_estimates()

        self.update_box.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)

    def check_get_estimates_signature(self):
        """ Method that checks the signature of the get_estimates function.
        It checks which input arguments are allowed and, if the output is
        correct for the EstimatorWidget, stores the number of estimates.
        """

        # Check function arguments
        proc = self._parent.make_procedure()
        call_signature = signature(proc.get_estimates)

        if "sequence" in call_signature.parameters:
            self.provide_sequence = True

        if "sequence_length" in call_signature.parameters:
            self.provide_sequence_length = True

        estimates = self.get_estimates()

        # Check if the output of the function is acceptable
        raise_error = True
        if isinstance(estimates, (list, tuple)):
            if all([isinstance(est, (tuple, list)) for est in estimates]):
                if all([len(est) == 2 for est in estimates]):
                    raise_error = False

        if raise_error:
            raise TypeError(
                "If implemented, the get_estimates function is expected to"
                "return an int or float representing the estimated duration,"
                "or a list of tuples of strings, where each tuple  represents"
                "an estimate containing two string: the first is a label for"
                "the estimate, the second is the estimate itself."
            )

        # Store the number of estimates
        self.number_of_estimates = len(estimates)

    def _setup_ui(self):
        self.line_edits = list()
        for idx in range(self.number_of_estimates):
            qlb = QtGui.QLabel(self)

            qle = QtGui.QLineEdit(self)
            qle.setEnabled(False)
            qle.setAlignment(QtCore.Qt.AlignRight)

            self.line_edits.append((qlb, qle))

        # Add a checkbox for continuous updating
        self.update_box = QtGui.QCheckBox(self)
        self.update_box.setTristate(True)
        self.update_box.stateChanged.connect(self._set_continuous_updating)

        # Add a button for instant updating
        self.update_button = QtGui.QPushButton("Update", self)
        self.update_button.clicked.connect(self.update_estimates)

    def _layout(self):
        f_layout = QtGui.QFormLayout(self)
        for row in self.line_edits:
            f_layout.addRow(*row)

        update_hbox = QtGui.QHBoxLayout()
        update_hbox.addWidget(self.update_box)
        update_hbox.addWidget(self.update_button)
        f_layout.addRow("Update continuously", update_hbox)

    def get_estimates(self):
        """ Method that makes a procedure with the currently entered
        parameters and returns the estimates for these parameters.
        """
        # Make a procedure
        procedure = self._parent.make_procedure()

        kwargs = dict()

        sequence = None
        sequence_length = None
        if hasattr(self._parent, "sequencer"):
            try:
                sequence = self._parent.sequencer.get_sequence_from_tree()
            except SequenceEvaluationException:
                sequence_length = 0
            else:
                sequence_length = len(sequence)

        if self.provide_sequence:
            kwargs["sequence"] = sequence

        if self.provide_sequence_length:
            kwargs["sequence_length"] = sequence_length

        estimates = procedure.get_estimates(**kwargs)

        if isinstance(estimates, (int, float)):
            estimates = self._estimates_from_duration(estimates, sequence_length)

        return estimates

    def update_estimates(self):
        """ Method that gets and displays the estimates.
        Implemented for connecting to the 'update'-button.
        """
        estimates = self.get_estimates()
        self.display_estimates(estimates)

    def display_estimates(self, estimates):
        """ Method that updates the shown estimates for the given set of
        estimates.

        :param estimates: The set of estimates to be shown in the form of a
            list of tuples of (2) strings
        """
        if len(estimates) != self.number_of_estimates:
            raise ValueError(
                "Number of estimates changed after initialisation "
                "(from %d to %d)." % (self.number_of_estimates, len(estimates))
            )

        for idx, estimate in enumerate(estimates):
            self.line_edits[idx][0].setText(estimate[0])
            self.line_edits[idx][1].setText(estimate[1])

    def _estimates_from_duration(self, duration, sequence_length):
        estimates = list()

        estimates.append(("Duration", "%d s" % int(duration)))

        if hasattr(self._parent, "sequencer"):
            estimates.append(("Sequence length", str(sequence_length)))
            estimates.append(("Sequence duration", "%d s" % int(sequence_length * duration)))

        estimates.append(('Measurement finished at', str(datetime.now() + timedelta(
            seconds=duration))[:-7]))

        if hasattr(self._parent, "sequencer"):
            estimates.append(('Sequence finished at', str(datetime.now() + timedelta(
                seconds=duration * sequence_length))[:-7]))

        return estimates

    def _set_continuous_updating(self):
        state = self.update_box.checkState()

        self.update_thread.stop()
        self.update_thread.join()

        if state == QtCore.Qt.CheckState.Unchecked:
            pass
        elif state == QtCore.Qt.CheckState.PartiallyChecked:
            self.update_thread.delay = 2
            self.update_thread.start()
        elif state == QtCore.Qt.CheckState.Checked:
            self.update_thread.delay = 0.1
            self.update_thread.start()
