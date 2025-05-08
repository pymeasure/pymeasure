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

import re
import pyqtgraph as pg

from ..curves import ResultsCurve, Crosshairs
from ..Qt import QtCore, QtWidgets
from ...experiment import Procedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PlotFrame(QtWidgets.QFrame):
    """ Combines a PyQtGraph Plot with Crosshairs. Refreshes
    the plot based on the refresh_time, and allows the axes
    to be changed on the fly, which updates the plotted data
    """

    LABEL_STYLE = {'font-size': '10pt', 'font-family': 'Arial', 'color': '#000000'}
    updated = QtCore.Signal()
    ResultsClass = ResultsCurve
    x_axis_changed = QtCore.Signal(str)
    y_axis_changed = QtCore.Signal(str)

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
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.setMidLineWidth(1)

        vbox = QtWidgets.QVBoxLayout(self)

        self.plot_widget = pg.PlotWidget(self, background='#ffffff')
        vbox.addWidget(self.plot_widget)
        self.setLayout(vbox)

        self.plot = self.plot_widget.getPlotItem()

        style = dict(self.LABEL_STYLE, justify='right')
        if "font-size" in style:  # LabelItem wants the size as 'size' rather than 'font-size'
            style["size"] = style.pop("font-size")
        self.coordinates = pg.LabelItem("", parent=self.plot, **style)
        self.coordinates.anchor(itemPos=(1, 1), parentPos=(1, 1), offset=(0, 3))

        self.crosshairs = Crosshairs(self.plot,
                                     pen=pg.mkPen(color='#AAAAAA',
                                                  style=QtCore.Qt.PenStyle.DashLine))
        self.crosshairs.coordinates.connect(self.update_coordinates)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_curves)
        self.timer.timeout.connect(self.crosshairs.update)
        self.timer.timeout.connect(self.updated)
        self.timer.start(int(self.refresh_time * 1e3))

    def update_coordinates(self, x, y):
        self.coordinates.setText(f"({x:g}, {y:g})")

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
