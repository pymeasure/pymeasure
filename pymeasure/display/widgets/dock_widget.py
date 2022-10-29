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

from pyqtgraph.dockarea import Dock, DockArea
import pyqtgraph as pg

from .plot_widget import PlotWidget
from ..Qt import QtWidgets
from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DockWidget(TabWidget, QtWidgets.QWidget):
    """
    Widget that contains a DockArea with a number of Docks as determined by num_plots.

    :param name: Name for the TabWidget
    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the data column(s) for the x-axis of the plot. This may be string or a list
        of strings from the data columns of the procedure.
    :param y_axis: the data column(s) for the y-axis of the plot. This may be string or a list
        of strings from the data columns of the procedure.
    :param num_plots: the number of plots you want displayed in the DockWindow tab
    :param linewidth: line width for plots in
        :class:`~pymeasure.display.widgets.plot_widget.PlotWidget`
    :param parent: Passed on to QtWidgets.QWidget. Default is None
    """

    def __init__(self, name, procedure_class, x_axis=None, y_axis=None, num_plots=1, linewidth=1,
                 parent=None):
        self.procedure_class = procedure_class
        super().__init__(name, parent)
        self.num_plots = num_plots
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.linewidth = linewidth

        self.dock_area = DockArea()
        self.docks = []
        self.plot_frames = []

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        x_axis_label = self.x_axis
        y_axis_label = self.y_axis

        for idx, i in enumerate(range(self.num_plots)):
            # If x_axis or y_axis are a list, then we want to set the label to the passed list.
            # However, if list is smaller than num_plots, repeat last item in the list.
            if isinstance(self.x_axis, list):
                x_axis_label = self.x_axis[min(idx, len(self.x_axis) - 1)]
            if isinstance(self.y_axis, list):
                y_axis_label = self.y_axis[min(idx, len(self.y_axis) - 1)]

            dock = Dock("Dock " + str(i + 1), closable=False, size=(200, 50))
            self.dock_area.addDock(dock)
            self.plot_frames.append(
                PlotWidget("Results Graph", self.procedure_class.DATA_COLUMNS, x_axis_label,
                           y_axis_label, linewidth=self.linewidth))
            dock.addWidget(self.plot_frames[idx])
            self.docks.append(dock)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.addWidget(self.dock_area)
        self.setLayout(vbox)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(color=color, width=self.linewidth)
        if 'antialias' not in kwargs:
            kwargs['antialias'] = False
        curves = []
        for i in range(self.num_plots):
            curves.append(self.plot_frames[i].new_curve(results, color=pg.intColor(0), **kwargs))
        return curves

    def update_x_column(self, index):
        for i in range(self.num_plots):
            self.plot_frames[i].update_x_column(index)

    def update_y_column(self, index, plot_idx):
        axis = self.columns_y[plot_idx].itemText(index)
        self.plot_frames[plot_idx].change_y_axis(axis)

    def load(self, curves):
        for cdx, c in enumerate(curves):
            self.plot_frames[cdx].load(c)

    def remove(self, curve):
        for i in range(self.num_plots):
            self.plot_frames[i].plot.removeItem(curve[i])

    def clear(self):
        for i in range(self.num_plots):
            self.plot_frames[i].plot.clear()

    def set_color(self, curve, color):
        for i in range(self.num_plots):
            curve[i].setPen(pg.mkPen(color=color, width=self.linewidth))
