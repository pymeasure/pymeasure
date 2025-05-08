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

from ..widgets.dock_widget import DockWidget
from ..widgets.log_widget import LogWidget
from .managed_window import ManagedWindowBase

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ManagedDockWindow(ManagedWindowBase):
    """
    Display experiment output with multiple docking windows with
    :class:`~pymeasure.display.widgets.dock_widget.DockWidget` class.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the data column(s) for the x-axis of the plot. This may be a string or a list
        of strings from the data columns of the procedure. The list length determines the number of
        plots
    :param y_axis: the data column(s) for the y-axis of the plot. This may be a string or a list
        of strings from the data columns of the procedure. The list length determines the number of
        plots
    :param linewidth: linewidth for the displayed curves, default is 1
    :param log_fmt: formatting string for the log-widget
    :param log_datefmt: formatting string for the date in the log-widget
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.managed_window.ManagedWindowBase`
    """

    def __init__(self, procedure_class, x_axis=None, y_axis=None,
                 linewidth=1, log_fmt=None, log_datefmt=None, **kwargs):

        self.x_axis = x_axis
        self.y_axis = y_axis

        measure_quantities = []
        # Expand x_axis if it is a list
        if isinstance(self.x_axis, list):
            measure_quantities += [*self.x_axis]
            self.x_axis_labels = self.x_axis
            # Change x_axis to a string from list for ResultsDialog
            self.x_axis = self.x_axis[0]
        else:
            self.x_axis_labels = [self.x_axis, ]
            measure_quantities.append(self.x_axis)

        # Expand y_axis if it is a list
        if isinstance(self.y_axis, list):
            measure_quantities += [*self.y_axis]
            self.y_axis_labels = self.y_axis
            # Change y_axis to a string from list for ResultsDialog
            self.y_axis = self.y_axis[0]
        else:
            self.y_axis_labels = [self.y_axis, ]
            measure_quantities.append(self.y_axis)

        self.log_widget = LogWidget("Experiment Log", fmt=log_fmt, datefmt=log_datefmt)
        self.dock_widget = DockWidget("Dock Tab", procedure_class, self.x_axis_labels,
                                      self.y_axis_labels, linewidth=linewidth)

        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.dock_widget, self.log_widget)

        super().__init__(procedure_class, **kwargs)

        self.browser_widget.browser.measured_quantities.update(measure_quantities)

        logging.getLogger().addHandler(self.log_widget.handler)
        log.setLevel(self.log_level)
        log.info("DockWindow connected to logging")
