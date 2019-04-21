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

import pyqtgraph as pg
import numpy as np

from .Qt import QtCore

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResultsCurve(pg.PlotDataItem):
    """ Creates a curve loaded dynamically from a file through the Results
    object and supports error bars. The data can be forced to fully reload
    on each update, useful for cases when the data is changing across the full
    file instead of just appending.
    """

    def __init__(self, results, x, y, xerr=None, yerr=None,
                 force_reload=False, **kwargs):
        super().__init__(**kwargs)
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
        super().__init__(**kwargs)
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
        super().__init__()

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
            mouse_point = self.plot.vb.mapSceneToView(self.position)
            self.coordinates.emit(mouse_point.x(), mouse_point.y())
            self.vertical.setPos(mouse_point.x())
            self.horizontal.setPos(mouse_point.y())

    def mouseMoved(self, event=None):
        """ Updates the mouse position upon mouse movement """
        if event is not None:
            self.position = event[0]
            self.update()
        else:
            raise Exception("Mouse location not known")
