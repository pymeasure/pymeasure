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

import numpy as np
import pyqtgraph as pg
from .Qt import QtCore, QtGui

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResultsCurve(pg.PlotDataItem):
    """Creates a curve loaded dynamically from a file through the Results object. The data can
    be forced to fully reload on each update, useful for cases when the data is changing across
    the full file instead of just appending.
    """

    def __init__(self, results, x, y, force_reload=False, wdg=None, **kwargs):
        super().__init__(**kwargs)
        self.results = results
        self.wdg = wdg
        self.pen = kwargs.get("pen", None)
        self.x, self.y = x, y
        self.force_reload = force_reload
        self.color = self.opts["pen"].color()

    def update_data(self):
        """Updates the data by polling the results"""
        if self.force_reload:
            self.results.reload()
        data = self.results.data  # get the current snapshot

        # Set x-y data
        self.setData(data[self.x], data[self.y])

    def set_color(self, color):
        self.pen.setColor(color)
        self.color = self.opts["pen"].color()
        self.updateItems(styleUpdate=True)


# TODO: Add method for changing x and y


class ResultsImage(pg.ImageItem):
    """Creates an image loaded dynamically from a file through the Results
    object."""

    def __init__(
        self, results, x, y, z, force_reload=False, wdg=None, colormap="viridis", **kwargs
    ):
        self.results = results
        self.wdg = wdg
        self.x = x
        self.y = y
        self.z = z
        self.xstart = getattr(self.results.procedure, self.x + "_start")
        self.xend = getattr(self.results.procedure, self.x + "_end")
        self.xstep = getattr(self.results.procedure, self.x + "_step")
        self.xsize = int(np.ceil((self.xend - self.xstart) / self.xstep))
        self.ystart = getattr(self.results.procedure, self.y + "_start")
        self.yend = getattr(self.results.procedure, self.y + "_end")
        self.ystep = getattr(self.results.procedure, self.y + "_step")
        self.ysize = int(np.ceil((self.yend - self.ystart) / self.ystep))
        self.img_data = np.zeros((self.ysize, self.xsize))
        self.force_reload = force_reload
        self.colormap = colormap

        super().__init__(image=self.img_data)

    def update_data(self):
        if self.force_reload:
            self.results.reload()

        # use numpy array operations to arrange the data more efficiently
        data = self.results.data
        z_data = data[self.z].to_numpy(dtype=np.float64)

        self.img_data.ravel()[: z_data.size] = z_data
        print(self.img_data.shape, z_data.shape, self.xsize * self.ysize)

        # set image data
        if len(z_data) != 0:
            self.setImage(
                image=self.img_data,
                rect=[
                    self.xstart - self.xstep / 2,
                    self.ystart - self.ystep / 2,
                    self.xend - self.xstart,
                    self.yend - self.ystart,
                ],
                autoLevels=True,
                colorMap=self.colormap,
            )

    def set_colormap(self, colormap):
        """Sets the colormap for the image."""
        self.colormap = colormap


class BufferCurve(pg.PlotDataItem):
    """Creates a curve based on a predefined buffer size and allows data to be added dynamically."""

    data_updated = QtCore.Signal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._buffer = None

    def prepare(self, size, dtype=np.float32):
        """Prepares the buffer based on its size, data type"""
        self._buffer = np.empty((size, 2), dtype=dtype)
        self._ptr = 0

    def append(self, x, y):
        """Appends data to the curve with optional errors"""
        if self._buffer is None:
            raise Exception("BufferCurve buffer must be prepared")
        if len(self._buffer) <= self._ptr:
            raise Exception("BufferCurve overflow")

        # Set x-y data
        self._buffer[self._ptr, :2] = [x, y]
        self.setData(self._buffer[: self._ptr, :2])

        self._ptr += 1
        self.data_updated.emit()


class Crosshairs(QtCore.QObject):
    """Attaches crosshairs to the a plot and provides a signal with the
    x and y graph coordinates
    """

    coordinates = QtCore.Signal(float, float)

    def __init__(self, plot, pen=None):
        """Initiates the crosshars onto a plot given the pen style.

        Example pen:
        pen=pg.mkPen(color='#AAAAAA', style=QtCore.Qt.PenStyle.DashLine)
        """
        super().__init__()

        self.vertical = pg.InfiniteLine(angle=90, movable=False, pen=pen)
        self.horizontal = pg.InfiniteLine(angle=0, movable=False, pen=pen)
        plot.addItem(self.vertical, ignoreBounds=True)
        plot.addItem(self.horizontal, ignoreBounds=True)

        self.position = None
        self.proxy = pg.SignalProxy(plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.plot = plot

    def hide(self):
        self.vertical.hide()
        self.horizontal.hide()

    def show(self):
        self.vertical.show()
        self.horizontal.show()

    def update(self):
        """Updates the mouse position based on the data in the plot. For
        dynamic plots, this is called each time the data changes to ensure
        the x and y values correspond to those on the display.
        """
        if self.position is not None:
            mouse_point = self.plot.vb.mapSceneToView(self.position)
            self.coordinates.emit(mouse_point.x(), mouse_point.y())
            self.vertical.setPos(mouse_point.x())
            self.horizontal.setPos(mouse_point.y())

    def mouseMoved(self, event=None):
        """Updates the mouse position upon mouse movement"""
        if event is not None:
            self.position = event[0]
            self.update()
        else:
            raise Exception("Mouse location not known")
