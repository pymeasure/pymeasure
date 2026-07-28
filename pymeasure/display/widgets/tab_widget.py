#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from typing import Generic, TypeVar

import pyqtgraph as pg

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

Curve = TypeVar("Curve")
DEFAULT_COLOR = pg.intColor(0)


class TabWidget(Generic[Curve]):
    """ Utility class to define default implementation for some basic methods.

        When defining a widget to be used in subclasses of
        :class:`ManagedWindowBase<pymeasure.display.windows.managed_window.ManagedWindowBase>`,
        users should inherit from this class and provide an
        implementation of these methods
    """

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def new_curve(self, results, color=DEFAULT_COLOR, **kwargs) -> Curve:
        """ Create a new curve """
        ...  # noqa: PIE790

    def load(self, curve: Curve) -> None:
        """ Add curve to widget """

    def remove(self, curve: Curve) -> None:
        """ Remove curve from widget """

    def set_color(self, curve: Curve, color) -> None:
        """ Set color for widget """

    def preview_widget(self, parent=None):
        """ Return a Qt widget suitable for preview during loading

        See also :class:`ResultsDialog<pymeasure.display.widgets.results_dialog.ResultsDialog>`
        If the object returned is not None, then it should have also an
        attribute `name`.
        """

        return

    def clear_widget(self) -> None:
        """ Clear widget content

        Behaviour is widget specific and it is currently used in preview mode
        """

        return
