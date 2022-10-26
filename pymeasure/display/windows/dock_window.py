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

from .managed_window import ManagedWindowBase
from ..Qt import QtCore, QtWidgets
from ..widgets import (
    PlotWidget,
    LogWidget
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DockWindow(ManagedWindowBase):
    """
    Display experiment output with an :class:`~pymeasure.display.widgets.image_widget.ImageWidget`
    class.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the data column(s) for the x-axis of the plot. This may be string or a list
        of strings from the data columns of the procedure.
    :param y_axis: the data column(s) for the y-axis of the plot. This may be string or a list
        of strings from the data columns of the procedure.
    :param num_plots: the number of plots you want displayed in the DockWindow tab
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.managed_window.ManagedWindowBase`
    """

    def __init__(self, procedure_class, x_axis=None, y_axis=None, num_plots=1, *args, **kwargs):

        self.x_axis = x_axis
        self.y_axis = y_axis
        self.num_plots = num_plots

        self.log_widget = LogWidget("Experiment Log")
        self.widget_list = []

        super().__init__(
            procedure_class=procedure_class,
            setup=False,
            widget_list=self.widget_list,
            *args,
            **kwargs
        )

        self._setup_ui()
        self._layout()

        measure_quantities = []
        if type(self.x_axis) == list:
            # Expand x_axis if it is a list
            measure_quantities += [*self.x_axis]
        else:
            measure_quantities.append(self.x_axis)
        if type(self.y_axis) == list:
            # Expand y_axis if it is a list
            measure_quantities += [*self.y_axis]
        else:
            measure_quantities.append(self.y_axis)

        self.browser_widget.browser.measured_quantities = measure_quantities

        logging.getLogger().addHandler(self.log_widget.handler)  # needs to be in Qt context?
        log.setLevel(self.log_level)
        log.info("DockWindow connected to logging")

    def _layout(self):
        self.main = QtWidgets.QWidget(self)

        inputs_dock = QtWidgets.QWidget(self)
        inputs_vbox = QtWidgets.QVBoxLayout(self.main)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.queue_button)
        hbox.addWidget(self.abort_button)
        hbox.addStretch()

        if self.directory_input:
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(self.directory_label)
            vbox.addWidget(self.directory_line)
            vbox.addLayout(hbox)

        if self.inputs_in_scrollarea:
            inputs_scroll = QtWidgets.QScrollArea()
            inputs_scroll.setWidgetResizable(True)
            inputs_scroll.setFrameStyle(QtWidgets.QScrollArea.Shape.NoFrame)

            self.inputs.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                      QtWidgets.QSizePolicy.Policy.Fixed)
            inputs_scroll.setWidget(self.inputs)
            inputs_vbox.addWidget(inputs_scroll, 1)

        else:
            inputs_vbox.addWidget(self.inputs)

        if self.directory_input:
            inputs_vbox.addLayout(vbox)
        else:
            inputs_vbox.addLayout(hbox)

        inputs_vbox.addStretch(0)
        inputs_dock.setLayout(inputs_vbox)

        dock = QtWidgets.QDockWidget('Input Parameters')
        dock.setWidget(inputs_dock)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        if self.use_sequencer:
            sequencer_dock = QtWidgets.QDockWidget('Sequencer')
            sequencer_dock.setWidget(self.sequencer)
            sequencer_dock.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
            self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, sequencer_dock)

        if self.use_estimator:
            estimator_dock = QtWidgets.QDockWidget('Estimator')
            estimator_dock.setWidget(self.estimator)
            estimator_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetArea.NoDockWidgetFeatures)
            self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, estimator_dock)

        self.tabs = QtWidgets.QTabWidget(self.main)

        self.dock_area = DockArea()
        self.dock_area.name = 'Dock Tab'
        self.docks = []

        self.tabs.addTab(self.dock_area, self.dock_area.name)

        for idx, i in enumerate(range(self.num_plots)):
            x_axis_label = self.x_axis
            y_axis_label = self.y_axis
            # If x_axis or y_axis are a list, then we want to set the label to the passed list.
            # However, if list is smaller than num_plots, repeat last item in the list.
            if type(self.x_axis) == list:
                x_axis_label = self.x_axis[min(idx, len(self.x_axis) - 1)]
            if type(self.y_axis) == list:
                y_axis_label = self.y_axis[min(idx, len(self.y_axis) - 1)]
            self.widget_list.append(
                PlotWidget("Results Graph", self.procedure_class.DATA_COLUMNS, x_axis_label,
                           y_axis_label))
            dock = Dock("Dock " + str(i + 1), closable=False, size=(200, 50))
            self.dock_area.addDock(dock)
            dock.addWidget(self.widget_list[i])
            dock.nStyle = """
                          Dock > QWidget {
                              border: 1px solid #ff6600;
                              border-radius: 5px;
                          }"""
            dock.dragStyle = """
                          Dock > QWidget {
                              border: 14px solid #ff6600;
                              border-radius: 15px;
                          }"""
            dock.updateStyle()
            self.docks.append(dock)

        self.tabs.addTab(self.log_widget, self.log_widget.name)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.browser_widget)

        vbox = QtWidgets.QVBoxLayout(self.main)
        vbox.setSpacing(0)
        vbox.addWidget(splitter)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(1000, 800)
