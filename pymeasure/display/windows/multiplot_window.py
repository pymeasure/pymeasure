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

import os

import pyqtgraph as pg

from .managed_window import ManagedWindowBase
from ..widgets.multiplot_widget import MultiPlotWidget, MultiPlotResultsDialog
from ..widgets.log_widget import LogWidget
from ..browser import BrowserItem
from ..Qt import QtWidgets
from ..manager import Experiment
from ...experiment import Results

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MultiPlotWindow(ManagedWindowBase):
    """
    A window for plotting multiple graphs that share the X axis with custom Y axis

    .. seealso::
        Tutorial :ref:`tutorial-plotterwindow`
        A tutorial and example code for using the Plotter and PlotterWindow.

    Parameters for :code:`__init__` constructor.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the initial data-column for the x-axis of the plot
    :param y_axis: the initial data-column for the y-axis of the plot, either a single y-axis label
        or a list of y-axis labels for each plot
    :param linewidth: linewidth for the displayed curves, default is 1
    :param num_plots: number of plots to display, default is 1
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.managed_window.ManagedWindowBase`

    """

    def __init__(self, procedure_class, x_axis=None, y_axis=None, linewidth=1, num_plots=1,
                 **kwargs):
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.num_plots = num_plots
        self.log_widget = LogWidget("Experiment Log")
        self.plot_widget = MultiPlotWidget("Results Graph", procedure_class.DATA_COLUMNS, x_axis,
                                           y_axis,
                                           num_plots=num_plots, linewidth=linewidth)
        self.plot_widget.setMinimumSize(100, 200)

        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.plot_widget, self.log_widget)

        super().__init__(procedure_class, **kwargs)

        # Setup measured_quantities once we know x_axis and y_axis
        measure_quantities = [self.x_axis, self.y_axis]
        if type(self.y_axis) == list:
            # Expand y_axis if it is a list
            measure_quantities = [self.x_axis, *self.y_axis]
        self.browser_widget.browser.measured_quantities = measure_quantities

        logging.getLogger().addHandler(self.log_widget.handler)  # needs to be in Qt context?
        log.setLevel(self.log_level)
        log.info("MultiPlotWindow connected to logging")

    def open_experiment(self):
        dialog = MultiPlotResultsDialog(self.procedure_class.DATA_COLUMNS, self.x_axis, self.y_axis,
                                        num_plots=self.num_plots)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            for filename in map(str, filenames):
                if filename in self.manager.experiments:
                    QtWidgets.QMessageBox.warning(
                        self, "Load Error",
                        "The file %s cannot be opened twice." % os.path.basename(filename)
                    )
                elif filename == '':
                    return
                else:
                    results = Results.load(filename)
                    experiment = self.new_experiment(results)
                    for curves in experiment.curve_list:
                        if curves:
                            for curve in curves:
                                curve.update_data()
                    experiment.browser_item.progressbar.setValue(100)
                    self.manager.load(experiment)
                    log.info('Opened data file %s' % filename)

    def new_experiment(self, results, curve=None):
        if curve is None:
            curve_list = []
            for wdg in self.widget_list:
                curve_list.append(self.new_curve(wdg, results))
        else:
            curve_list = curve[:]

        curve_color = pg.intColor(0)
        for wdg, curve in zip(self.widget_list, curve_list):
            if isinstance(wdg, MultiPlotWidget):
                curve_color = curve[0].opts['pen'].color()
                break

        browser_item = BrowserItem(results, curve_color)
        return Experiment(results, curve_list, browser_item)
