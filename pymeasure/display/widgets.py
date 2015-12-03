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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from .Qt import QtCore, QtGui

import pyqtgraph as pg
import numpy as np
from .curves import ResultsCurve, Crosshairs


class PlotFrame(QtGui.QFrame):
    """ Combines a PyQtGraph Plot with Crosshairs. Refreshes
    the plot based on the refresh_time, and allows the axes
    to be changed on the fly, which updates the plotted data
    """

    LABEL_STYLE = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}
    updated = QtCore.QSignal()

    def __init__(self, x_axis=None, y_axis=None, refresh_time=0.2, parent=None):
        super(PlotFrame, self).__init__(parent=parent)
        self.refresh_time = refresh_time
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
        self.coordinates.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)

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
        self.timer.start(self.refresh_time*1e3)

    def update_coordinates(self, x, y):
        label = "(%0.3f, %0.3f)"
        self.coordinates.setText(label % (x, y))

    def update_curves(self):
        for item in self.plot.items:
            if isinstance(item, ResultsCurve):
                item.update()

    def parse_units(self, axis):
        """ Returns the units of an axis by searching the string
        """ 
        # TODO Implement this method
        return None

    def change_x_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, ResultsCurve):
                item.x = axis
        self.plot.setLabel('bottom', axis, units=self.parse_units(axis), **self.LABEL_STYLE)

    def change_y_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, ResultsCurve):
                item.y = axis
        self.plot.setLabel('left', axis, units=self.parse_units(axis), **self.LABEL_STYLE)


class PlotWidget(QtGui.QWidget):
    """ Extends the PlotFrame to allow different columns
    of the data to be dynamically choosen
    """

    x_axis_changed = QtCore.QSignal(str)
    y_axis_changed = QtCore.QSignal(str)

    def __init__(self, columns, x_axis=None, y_axis=None, refresh_time=0.2, parent=None):
        super(PlotWidget, self).__init__(parent=parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self._setup_ui()
        self.plot_frame.change_x_axis(x_axis)
        self.plot_frame.change_y_axis(y_axis)

    def _setup_ui(self):

        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)

        columns_x_label = QtGui.QLabel(self)
        columns_x_label.setMaximumSize(QtCore.QSize(45, 16777215))
        columns_x_label.setText('X Axis:')
        columns_y_label = QtGui.QLabel(self)
        columns_y_label.setMaximumSize(QtCore.QSize(45, 16777215))
        columns_y_label.setText('Y Axis:')
        
        self.columns_x = QtGui.QComboBox(self)
        self.columns_y = QtGui.QComboBox(self)
        for column in self.columns:
            self.columns_x.addItem(column)
            self.columns_y.addItem(column)
        self.columns_x.activated.connect(self.update_x_column)
        self.columns_y.activated.connect(self.update_y_column)

        hbox.addWidget(columns_x_label)
        hbox.addWidget(self.columns_x)
        hbox.addWidget(columns_y_label)
        hbox.addWidget(self.columns_y)
        vbox.addLayout(hbox)
        
        self.plot_frame = PlotFrame(self.columns[0], self.columns[1])
        self.updated = self.plot_frame.updated
        self.plot = self.plot_frame.plot
        self.columns_x.setCurrentIndex(0)
        self.columns_y.setCurrentIndex(1)

        vbox.addWidget(self.plot_frame)
        self.setLayout(vbox)

    def update_x_column(self, index):
        axis = self.columns_x.itemText(index)
        self.plot_frame.change_x_axis(axis)
        self.x_axis_changed.emit(axis)

    def update_y_column(self, index):
        axis = self.columns_y.itemText(index)
        self.plot_frame.change_y_axis(axis) 
        self.y_axis_changed.emit(axis)