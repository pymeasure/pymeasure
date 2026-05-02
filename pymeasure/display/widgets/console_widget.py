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

from pyqtgraph.console import ConsoleWidget as PGConsoleWidget

from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ConsoleWidget(TabWidget, PGConsoleWidget):
    """Display an interactive Python console in the GUI.

    It allows executing arbitrary Python commands at runtime and debugging the
    application.

    It can be included in subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.managed_window.ManagedWindowBase>`
    by adding it to the widget_list.

    :param name: Name of the widget. This is the text that will appear on the Tab in the GUI.
    :param parent: The Qt parent widget. Usually left as None or passed as the main window.
    :param namespace: A dictionary containing the local variables and modules you want to expose 
        to the console environment. For example, `{'window': self, 'device': your_device}`
        allows you to access the `window` object and your instrument directly in the console.
    :param text: The initial welcome message displayed when the console is first opened.
    """

    def __init__(self, name, parent=None, namespace=None, text="Interactive Python Console\n"):
        super().__init__(name=name, parent=parent, namespace=namespace, text=text)
