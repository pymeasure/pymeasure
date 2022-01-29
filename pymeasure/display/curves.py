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
import sys

import numpy as np
import pyqtgraph as pg
from .Qt import QtCore

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    from matplotlib.cm import viridis
except ImportError:
    log.warning("Matplotlib not found. Images will be greyscale")


def _greyscale_colormap(x):
    """Simple greyscale colormap. Assumes x is already normalized."""
    return np.array([x, x, x, 1])


class ResultsCurve(pg.PlotDataItem):
    """ Creates a curve loaded dynamically from a file through the Results object. The data can
    be forced to fully reload on each update, useful for cases when the data is changing across
    the full file instead of just appending.
    """

    def __init__(self, results, x, y, force_reload=False, **kwargs):
        super().__init__(**kwargs)
        self.results = results
        self.pen = kwargs.get('pen', None)
        self.x, self.y = x, y
        self.force_reload = force_reload

    def update_data(self):
        """Updates the data by polling the results"""
        if self.force_reload:
            self.results.reload()
        data = self.results.data  # get the current snapshot

        # Set x-y data
        self.setData(data[self.x], data[self.y])


# TODO: Add method for changing x and y

class ResultsImage(pg.ImageItem):
    """ Creates an image loaded dynamically from a file through the Results
    object."""

    def __init__(self, results, x, y, z, force_reload=False):
        self.results = results
        self.x = x
        self.y = y
        self.z = z
        self.xstart = getattr(self.results.procedure, self.x + '_start')
        self.xend = getattr(self.results.procedure, self.x + '_end')
        self.xstep = getattr(self.results.procedure, self.x + '_step')
        self.xsize = int(np.ceil((self.xend - self.xstart) / self.xstep)) + 1
        self.ystart = getattr(self.results.procedure, self.y + '_start')
        self.yend = getattr(self.results.procedure, self.y + '_end')
        self.ystep = getattr(self.results.procedure, self.y + '_step')
        self.ysize = int(np.ceil((self.yend - self.ystart) / self.ystep)) + 1
        self.img_data = np.zeros((self.ysize, self.xsize, 4))
        self.force_reload = force_reload
        if 'matplotlib.cm' in sys.modules:
            self.colormap = viridis
        else:
            self.colormap = _greyscale_colormap

        super().__init__(image=self.img_data)

        # Scale and translate image so that the pixels are in the coorect
        # position in "data coordinates"
        self.scale(self.xstep, self.ystep)
        self.translate(int(self.xstart / self.xstep) - 0.5,
                       int(self.ystart / self.ystep) - 0.5)  # 0.5 so pixels centered

    def update_data(self):
        if self.force_reload:
            self.results.reload()

        data = self.results.data
        zmin = data[self.z].min()
        zmax = data[self.z].max()

        # populate the image array with the new data
        for idx, row in data.iterrows():
            xdat = row[self.x]
            ydat = row[self.y]
            xidx, yidx = self.find_img_index(xdat, ydat)
            self.img_data[yidx, xidx, :] = self.colormap((row[self.z] - zmin) / (zmax - zmin))

        # set image data, need to transpose since pyqtgraph assumes column-major order
        self.setImage(image=np.transpose(self.img_data, axes=(1, 0, 2)))

    def find_img_index(self, x, y):
        """ Finds the integer image indices corresponding to the
        closest x and y points of the data given some x and y data.
        """

        indices = [self.xsize - 1, self.ysize - 1]  # default to the final pixel
        if self.xstart <= x <= self.xend:  # only change if within reasonable range
            indices[0] = self.round_up((x - self.xstart) / self.xstep)
        if self.ystart <= y <= self.yend:
            indices[1] = self.round_up((y - self.ystart) / self.ystep)

        return indices

    def round_up(self, x):
        """Convenience function since numpy rounds to even"""
        if x % 1 >= 0.5:
            return int(x) + 1
        else:
            return int(x)

    # TODO: colormap selection


class BufferCurve(pg.PlotDataItem):
    """ Creates a curve based on a predefined buffer size and allows data to be added dynamically.
    """

    data_updated = QtCore.QSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._buffer = None

    def prepare(self, size, dtype=np.float32):
        """ Prepares the buffer based on its size, data type """
        self._buffer = np.empty((size, 2), dtype=dtype)
        self._ptr = 0

    def append(self, x, y):
        """ Appends data to the curve with optional errors """
        if self._buffer is None:
            raise Exception("BufferCurve buffer must be prepared")
        if len(self._buffer) <= self._ptr:
            raise Exception("BufferCurve overflow")

        # Set x-y data
        self._buffer[self._ptr, :2] = [x, y]
        self.setData(self._buffer[:self._ptr, :2])

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
