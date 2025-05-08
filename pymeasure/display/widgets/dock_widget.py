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

from os import path
import json

from pyqtgraph.dockarea import Dock, DockArea
from pyqtgraph.dockarea.Dock import DockLabel
import pyqtgraph as pg

from .plot_widget import PlotWidget, PlotFrame
from ..Qt import QtWidgets
from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DockWidget(TabWidget, QtWidgets.QWidget):
    """
    Widget that contains a DockArea with a number of Docks as determined by the length of
    the longest x_axis_labels or y_axis_labels list.

    :param name: Name for the TabWidget
    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis_labels: List of data column(s) for the x-axis of the plot. If the list is shorter
        than y_axis_labels the last item in the list to match y_axis_labels length.
    :param y_axis_labels: List of data column(s) for the y-axis of the plot. If the list is shorter
        than x_axis_labels the last item in the list to match x_axis_labels length.
    :param linewidth: line width for plots in
        :class:`~pymeasure.display.widgets.plot_widget.PlotWidget`
    :param layout_path: Directory path to save dock layout state. Default is './'
    :param layout_filename: Optional filename for dock layout file.
        Default: *current procedure class* + "_dock_layout.json"
    :param parent: Passed on to QtWidgets.QWidget. Default is None
    """

    def __init__(self, name, procedure_class, x_axis_labels=None, y_axis_labels=None, linewidth=1,
                 layout_path='./', layout_filename='', parent=None):
        super().__init__(name, parent)

        self.procedure_class = procedure_class
        if layout_filename:
            self.dock_layout_filename = path.join(layout_path, layout_filename)
        else:
            self.dock_layout_filename = path.join(layout_path,
                                                  procedure_class.__name__ + '_dock_layout.json')
        self.x_axis_labels = x_axis_labels
        self.y_axis_labels = y_axis_labels
        self.num_plots = max(len(self.x_axis_labels), len(self.y_axis_labels))
        self.linewidth = linewidth

        self.dock_area = DockArea()
        self.docks = []
        self.plot_frames = []

        self._setup_ui()
        self._layout()

    def save_dock_layout(self):
        """
        Save the current layout of the docks and the plot settings.
        When running the GUI you can access this function by right-clicking in the
        widget area to bring up the context menu and selecting "Save Dock Layout"
        """

        layout = {
            'docks': self.dock_area.saveState(),
            'plots': [i.plot_frame.plot_widget.saveState() for i in self.plot_frames]
        }
        with open(self.dock_layout_filename, 'w') as f:
            f.write(json.dumps(layout))
        log.info('Saved dock layout to file %s' % self.dock_layout_filename)

    def save_dock_action(self):
        save_dock_action = QtWidgets.QWidgetAction(self)
        save_dock_action.setText("Save Dock Layout")
        save_dock_action.triggered.connect(self.save_dock_layout)
        return save_dock_action

    def contextMenuEvent(self, event):
        position = event.pos()
        # Create menu outside pyqtgraph.PlotWidget position
        if isinstance(self.childAt(position), (PlotWidget, DockLabel, QtWidgets.QLabel, PlotFrame)):
            menu = QtWidgets.QMenu(self)
            menu.addAction(self.save_dock_action())
            menu.exec(self.mapToGlobal(position))

    def _setup_ui(self):
        for i in range(self.num_plots):
            # Set the default label for current dock from x_axis_labels and y_axis_labels
            # However, if list is shorter than num_plots, repeat last item in the list.
            x_label = self.x_axis_labels[min(i, len(self.x_axis_labels) - 1)]
            y_label = self.y_axis_labels[min(i, len(self.y_axis_labels) - 1)]

            dock = Dock("Dock " + str(i + 1), closable=False, size=(200, 50))
            self.dock_area.addDock(dock)
            self.plot_frames.append(
                PlotWidget("Results Graph", self.procedure_class.DATA_COLUMNS, x_label,
                           y_label, linewidth=self.linewidth))
            self.plot_frames[i].plot_frame.plot_widget.scene().contextMenu.append(
                self.save_dock_action())
            dock.addWidget(self.plot_frames[i])
            self.docks.append(dock)

    def _layout(self):

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.addWidget(self.dock_area)
        self.setLayout(vbox)

        # Load dock layout file if it exists in the directory of the current procedure
        if path.exists(self.dock_layout_filename):
            with open(self.dock_layout_filename, 'r') as f:
                dock_layout = f.read()
            layout = json.loads(dock_layout)
            docks = layout['docks']
            plots = layout['plots']
            # Make sure number of plots in the file matches num_plots
            if len(plots) == self.num_plots:
                self.dock_area.restoreState(docks)
                for idx, i in enumerate(self.plot_frames):
                    i.plot_frame.plot_widget.restoreState(plots[idx])
                log.info('Loaded dock layout from file %s' % self.dock_layout_filename)
            else:
                log.warning(
                    'Number of displayed docks does not match number of docks in layout file %s'
                    % self.dock_layout_filename)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(color=color, width=self.linewidth)
        if 'antialias' not in kwargs:
            kwargs['antialias'] = False
        curves = []
        for i in range(self.num_plots):
            curves.append(self.plot_frames[i].new_curve(results, color=color, **kwargs))
        return curves

    def clear(self):
        for i in range(self.num_plots):
            self.plot_frames[i].plot.clear()
