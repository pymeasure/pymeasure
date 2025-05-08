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

from ..widgets import (
    ImageWidget,
)
from .managed_window import ManagedWindow

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ManagedImageWindow(ManagedWindow):
    """
    Display experiment output with an :class:`~pymeasure.display.widgets.image_widget.ImageWidget`
    class.

    :param procedure_class: procedure class describing the experiment (see
        :class:`~pymeasure.experiment.procedure.Procedure`)
    :param x_axis: the data-column for the x-axis of the plot, cannot be changed afterwards for
        the image-plot
    :param y_axis: the data-column for the y-axis of the plot, cannot be changed afterwards for
        the image-plot
    :param z_axis: the initial data-column for the z-axis of the plot, can be changed afterwards
    :param \\**kwargs: optional keyword arguments that will be passed to
        :class:`~pymeasure.display.windows.managed_image_window.ManagedWindow`

    """

    def __init__(self, procedure_class, x_axis, y_axis, z_axis=None, **kwargs):
        self.z_axis = z_axis
        self.image_widget = ImageWidget(
            "Image", procedure_class.DATA_COLUMNS, x_axis, y_axis, z_axis)

        if "widget_list" not in kwargs:
            kwargs["widget_list"] = ()
        kwargs["widget_list"] = kwargs["widget_list"] + (self.image_widget,)

        super().__init__(procedure_class, x_axis=x_axis, y_axis=y_axis, **kwargs)
