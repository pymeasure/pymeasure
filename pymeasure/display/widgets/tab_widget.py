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

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TabWidget:
    """ Utility class to define default implementation for some basic methods.

        When defining a widget to be used in subclasses of
        :class:`ManagedWindowBase<pymeasure.display.windows.managed_window.ManagedWindowBase>`,
        users should inherit from this class and provide an
        implementation of these methods
    """

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

    def new_curve(self, *args, **kwargs):
        """ Create a new curve """
        return None

    def load(self, curve):
        """ Add curve to widget """
        pass

    def remove(self, curve):
        """ Remove curve from widget """
        pass

    def set_color(self, curve, color):
        """ Set color for widget """
        pass

    def preview_widget(self, parent=None):
        """ Return a Qt widget suitable for preview during loading

        See also :class:`ResultsDialog<pymeasure.display.widgets.results_dialog.ResultsDialog>`
        If the object returned is not None, then it should have also an
        attribute `name`.
        """

        return None

    def clear_widget(self):
        """ Clear widget content

        Behaviour is widget specific and it is currently used in preview mode
        """

        return None
