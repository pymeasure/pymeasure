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
import pyqtgraph as pg
from functools import partial

from ..curves import ResultsCurve
from ..Qt import QtCore, QtGui
from .plot_widget import PlotWidget
from .plot_frame import PlotFrame
from .results_dialog import ResultsDialog
from ...experiment.results import Results

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MultiPlotWidget(PlotWidget):
    """ Extends the PlotFrame to allow different columns
    of the data to be dynamically choosen across multple plots
    """

    def __init__(self, name, columns, x_axis=None, y_axis=None, num_plots=1, *args, **kwargs):

        super().__init__(name, columns, x_axis, y_axis, setup=False, *args)
        self.num_plots = num_plots
        self._setup_ui()
        self._layout()
        if x_axis is not None:
            self.columns_x.setCurrentIndex(self.columns_x.findText(x_axis))
            for i in range(self.num_plots):
                self.plot_frame[i].change_x_axis(x_axis)
        if y_axis is not None:
            y_axis_label = y_axis
            for idx, i in enumerate(range(self.num_plots)):
                if type(y_axis) == list:
                    y_axis_label = y_axis[idx]
                self.columns_y[i].setCurrentIndex(self.columns_y[i].findText(y_axis_label))
                self.plot_frame[i].change_y_axis(y_axis_label)

    def _setup_ui(self):
        self.columns_x_label = QtGui.QLabel(self)
        self.columns_x_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_x_label.setText('X Axis:')
        self.columns_y_label = []
        for i in range(self.num_plots):
            self.columns_y_label.append(QtGui.QLabel(self))
            self.columns_y_label[i].setMaximumSize(QtCore.QSize(45, 16777215))
            if i:
                self.columns_y_label[i].setText('Y Axis ' + str(i + 1) + ':')
            else:
                self.columns_y_label[i].setText('Y Axis :')

        self.columns_x = QtGui.QComboBox(self)
        self.columns_y = []
        for i in range(self.num_plots):
            self.columns_y.append(QtGui.QComboBox(self))
        for column in self.columns:
            self.columns_x.addItem(column)
            for i in range(self.num_plots):
                self.columns_y[i].addItem(column)
        self.columns_x.activated.connect(self.update_x_column)
        for i in range(self.num_plots):
            self.columns_y[i].activated.connect(partial(self.update_y_column, plot_idx=i))

        self.plot_frame = []
        for i in range(self.num_plots):
            self.plot_frame.append(PlotFrame(
                self.columns[0],
                self.columns[1],
                self.refresh_time,
                self.check_status,
                # show_label=(i == (self.num_plots - 1))
            ))

        self.updated = [self.plot_frame[i].updated for i in range(self.num_plots)]
        self.plot = [self.plot_frame[i].plot for i in range(self.num_plots)]
        self.columns_x.setCurrentIndex(0)
        for i in range(self.num_plots):
            self.columns_y[i].setCurrentIndex(1)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.columns_x_label)
        hbox.addWidget(self.columns_x)
        for i in range(self.num_plots):
            hbox.addWidget(self.columns_y_label[i])
            hbox.addWidget(self.columns_y[i])

        vbox.addLayout(hbox)
        vbox.setSpacing(10)
        for i in range(self.num_plots):
            vbox.addWidget(self.plot_frame[i])
        self.setLayout(vbox)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(color=color, width=2)
        if 'antialias' not in kwargs:
            kwargs['antialias'] = False
        curves = []
        for i in range(self.num_plots):
            curve = ResultsCurve(results,
                                 x=self.plot_frame[i].x_axis,
                                 y=self.plot_frame[i].y_axis,
                                 **kwargs
                                 )
            curve.setSymbol(None)
            curve.setSymbolBrush(None)
            curves.append(curve)
        return curves

    def update_x_column(self, index):
        axis = self.columns_x.itemText(index)
        for i in range(self.num_plots):
            self.plot_frame[i].change_x_axis(axis)

    def update_y_column(self, index, plot_idx):
        axis = self.columns_y[plot_idx].itemText(index)
        self.plot_frame[plot_idx].change_y_axis(axis)

    def load(self, curve):
        for i in range(self.num_plots):
            curve[i].x = self.columns_x.currentText()
            curve[i].y = self.columns_y[i].currentText()
            curve[i].update_data()
            self.plot_frame[i].plot.addItem(curve[i])

    def remove(self, curve):
        for i in range(self.num_plots):
            self.plot_frame[i].plot.removeItem(curve[i])

    def clear(self):
        for i in range(self.num_plots):
            self.plot_frame[i].plot.clear()

    def set_color(self, curve, color):
        for i in range(self.num_plots):
            curve[i].setPen(pg.mkPen(color=color, width=2))


class MultiPlotResultsDialog(ResultsDialog):

    def __init__(self, columns, x_axis, y_axis, num_plots=1, *args, **kwargs):
        self.num_plots = num_plots
        super().__init__(columns, setup=False, *args)
        self.plot_widget = MultiPlotWidget("Results", self.columns,
                                           self.x_axis, self.y_axis, num_plots=num_plots,
                                           parent=self)
        self.plot = self.plot_widget.plot
        self._setup_ui()

    def update_plot(self, filename):
        self.plot_widget.clear()
        if not os.path.isdir(filename) and filename != '':
            try:
                results = Results.load(str(filename))
            except ValueError:
                return
            except Exception as e:
                raise e
            for i in range(self.num_plots):
                # The pyqtgraph pen width was changed to 1 (originally: 1.75) to
                # circumvent plotting slowdown. Once the issue
                # (https://github.com/pyqtgraph/pyqtgraph/issues/533) is resolved
                # it can be reverted
                curve = ResultsCurve(results,
                                     x=self.plot_widget.plot_frame[i].x_axis,
                                     y=self.plot_widget.plot_frame[i].y_axis,
                                     pen=pg.mkPen(color=(255, 0, 0), width=1),
                                     antialias=True
                                     )
                curve.update_data()

                self.plot_widget.plot_frame[i].plot.addItem(curve)

            self.preview_param.clear()
            for key, param in results.procedure.parameter_objects().items():
                new_item = QtGui.QTreeWidgetItem([param.name, str(param)])
                self.preview_param.addTopLevelItem(new_item)
            self.preview_param.sortItems(0, QtCore.Qt.AscendingOrder)
