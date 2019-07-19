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

import os
import re
import pyqtgraph as pg

from .browser import Browser
from .curves import ResultsCurve, Crosshairs
from .inputs import BooleanInput, IntegerInput, ListInput, ScientificInput, StringInput
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
            if isinstance(item, ResultsCurve):
                if self.check_status:
                    if item.results.procedure.status == Procedure.RUNNING:
                        item.update()
                else:
                    item.update()

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
            if isinstance(item, ResultsCurve):
                item.x = axis
                item.update()
        label, units = self.parse_axis(axis)
        self.plot.setLabel('bottom', label, units=units, **self.LABEL_STYLE)
        self.x_axis = axis
        self.x_axis_changed.emit(axis)

    def change_y_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, ResultsCurve):
                item.y = axis
                item.update()
        label, units = self.parse_axis(axis)
        self.plot.setLabel('left', label, units=units, **self.LABEL_STYLE)
        self.y_axis = axis
        self.y_axis_changed.emit(axis)


class PlotWidget(QtGui.QWidget):
    """ Extends the PlotFrame to allow different columns
    of the data to be dynamically choosen
    """

    def __init__(self, columns, x_axis=None, y_axis=None, refresh_time=0.2, check_status=True,
                 parent=None):
        super().__init__(parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.check_status = check_status
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
            kwargs['pen'] = pg.mkPen(color=color, width=2)
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

    def __init__(self, procedure_class, inputs=(), parent=None):
        super().__init__(parent)
        self._procedure_class = procedure_class
        self._procedure = procedure_class()
        self._inputs = inputs
        self._setup_ui()
        self._layout()

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

        parameters = self._procedure.parameter_objects()
        for name in self._inputs:
            if not isinstance(getattr(self, name), self.NO_LABEL_INPUTS):
                label = QtGui.QLabel(self)
                label.setText("%s:" % parameters[name].name)
                vbox.addWidget(label)
            vbox.addWidget(getattr(self, name))

        self.setLayout(vbox)

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


class LogWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.handler.record.connect(self.view.appendPlainText)

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

        self.plot_widget = PlotWidget(self.columns, self.x_axis, self.y_axis, parent=self)
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
                                 pen=pg.mkPen(color=(255, 0, 0), width=1.75),
                                 antialias=True
                                 )
            curve.update()

            self.plot.addItem(curve)

            self.preview_param.clear()
            for key, param in results.procedure.parameter_objects().items():
                new_item = QtGui.QTreeWidgetItem([param.name, str(param)])
                self.preview_param.addTopLevelItem(new_item)
            self.preview_param.sortItems(0, QtCore.Qt.AscendingOrder)
