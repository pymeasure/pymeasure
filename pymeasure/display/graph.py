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

from .qt_variant import QtCore, QtGui

import pyqtgraph as pg
import numpy as np


class ResultsCurve(pg.PlotDataItem):
    """ Creates a curve loaded dynamically from a file through the Results
    object and supports error bars. The data can be forced to fully reload
    on each update, useful for cases when the data is changing across the full
    file instead of just appending.
    """

    def __init__(self, results, x, y, xerr=None, yerr=None,
                 force_reload=False, **kwargs):
        pg.PlotDataItem.__init__(self, **kwargs)
        self.results = results
        self.pen = kwargs.get('pen', None)
        self.x, self.y = x, y
        self.force_reload = force_reload
        if xerr or yerr:
            self._errorBars = pg.ErrorBarItem(pen=kwargs.get('pen', None))
            self.xerr, self.yerr = xerr, yerr

    def update(self):
        """Updates the data by polling the results"""

        if self.force_reload:
            self.results.reload()
        data = self.results.data  # get the current snapshot

        # Set x-y data
        self.setData(data[self.x], data[self.y])

        # Set error bars if enabled at construction
        if hasattr(self, '_errorBars'):
            self._errorBars.setOpts(
                        x=data[self.x],
                        y=data[self.y],
                        top=data[self.yerr],
                        bottom=data[self.yerr],
                        left=data[self.xerr],
                        right=data[self.yerr],
                        beam=max(data[self.xerr], data[self.yerr])
                    )

# TODO: Add method for changing x and y


class BufferCurve(pg.PlotDataItem):
    """ Creates a curve based on a predefined buffer size and allows
    data to be added dynamically, in additon to supporting error bars
    """

    data_updated = QtCore.QSignal()

    def __init__(self, errors=False, **kwargs):
        pg.PlotDataItem.__init__(self, **kwargs)
        if errors:
            self._errorBars = pg.ErrorBarItem(pen=kwargs.get('pen', None))
        self._buffer = None

    def prepare(self, size, dtype=np.float32):
        """ Prepares the buffer based on its size, data type """
        if hasattr(self, '_errorBars'):
            self._buffer = np.empty((size, 4), dtype=dtype)
        else:
            self._buffer = np.empty((size, 2), dtype=dtype)
        self._ptr = 0

    def append(self, x, y, xError=None, yError=None):
        """ Appends data to the curve with optional errors """
        if self._buffer is None:
            raise Exception("BufferCurve buffer must be prepared")
        if len(self._buffer) <= self._ptr:
            raise Exception("BufferCurve overflow")

        # Set x-y data
        self._buffer[self._ptr, :2] = [x, y]
        self.setData(self._buffer[:self._ptr, :2])

        # Set error bars if enabled at construction
        if hasattr(self, '_errorBars'):
            self._buffer[self._ptr, 2:] = [xError, yError]
            self._errorBars.setOpts(
                        x=self._buffer[:self._ptr, 0],
                        y=self._buffer[:self._ptr, 1],
                        top=self._buffer[:self._ptr, 3],
                        bottom=self._buffer[:self._ptr, 3],
                        left=self._buffer[:self._ptr, 2],
                        right=self._buffer[:self._ptr, 2],
                        beam=np.max(self._buffer[:self._ptr, 2:])
                    )

        self._ptr += 1
        self.data_updated.emit()


class Crosshairs(QtCore.QObject):
    """ Attaches crosshairs to the a plot and provides a signal with the
    x and y graph coordinates
    """

    coordinates = QtCore.QSignal(float, float)

    def __init__(self, plot, pen=None):
        """ Initiates the crosshars onto a plot given the pen style.

        Example pen:
        pen=pg.mkPen(color='#AAAAAA', style=QtCore.Qt.DashLine)
        """
        QtCore.QObject.__init__(self)
        self.vertical = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.horizontal = pg.InfiniteLine(angle=0, movable=False, pen=pen)
        plot.addItem(self.vertical, ignoreBounds=True)
        plot.addItem(self.horizontal, ignoreBounds=True)

        self.position = None
        self.proxy = pg.SignalProxy(plot.scene().sigMouseMoved, rateLimit=60,
                                    slot=self.mouseMoved)
        self.plot = plot

    def hide(self):
        self.vertical.hide()
        self.horizontal.hide()

    def show(self):
        self.vertical.show()
        self.horizontal.show()

    def update(self):
        """ Updates the mouse position based on the data in the plot. For
        dynamic plots, this is called each time the data changes to ensure
        the x and y values correspond to those on the display.
        """
        if self.position is not None:
            mousePoint = self.plot.vb.mapSceneToView(self.position)
            self.coordinates.emit(mousePoint.x(), mousePoint.y())
            self.vertical.setPos(mousePoint.x())
            self.horizontal.setPos(mousePoint.y())

    def mouseMoved(self, event=None):
        """ Updates the mouse position upon mouse movement """
        if event is not None:
            self.position = event[0]
            self.update()
        else:
            raise Exception("Mouse location not known")


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