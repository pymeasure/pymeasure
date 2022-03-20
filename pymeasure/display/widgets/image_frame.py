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

from ..curves import ResultsImage
from ..Qt import QtCore
from .plot_frame import PlotFrame

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ImageFrame(PlotFrame):
    """ Extends :class:`PlotFrame<pymeasure.display.widgets.plot_frame.PlotFrame>`
    to plot also axis Z using colors
    """
    ResultsClass = ResultsImage
    z_axis_changed = QtCore.QSignal(str)

    def __init__(self, x_axis, y_axis, z_axis=None,
                 refresh_time=0.2, check_status=True, parent=None):
        super().__init__(x_axis, y_axis, refresh_time, check_status, parent)
        self.change_z_axis(z_axis)

    def change_z_axis(self, axis):
        for item in self.plot.items:
            if isinstance(item, self.ResultsClass):
                item.z = axis
                item.update_data()
        label, units = self.parse_axis(axis)
        if units is not None:
            self.plot.setTitle(label + ' (%s)' % units)
        else:
            self.plot.setTitle(label)
        self.z_axis = axis
        self.z_axis_changed.emit(axis)
