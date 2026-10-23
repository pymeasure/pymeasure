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

from pyqtgraph.console import ConsoleWidget as PGConsoleWidget

from pymeasure.display.Qt import QtWidgets
from pymeasure.display.widgets.console_widget import ConsoleWidget
from pymeasure.display.widgets.tab_widget import TabWidget


def test_console_widget_inheritance(qtbot):
    """Test that ConsoleWidget inherits from TabWidget and PGConsoleWidget."""
    assert issubclass(ConsoleWidget, TabWidget)
    assert issubclass(ConsoleWidget, PGConsoleWidget)


def test_console_widget_name_stored(qtbot):
    """Test that the name passed at construction is stored as an attribute."""
    widget = ConsoleWidget(name="my_console")
    qtbot.addWidget(widget)
    assert widget.name == "my_console"


def test_console_widget_tab_registration(qtbot):
    """Test that the widget can be registered as a tab in a QTabWidget."""
    tabs = QtWidgets.QTabWidget()
    qtbot.addWidget(tabs)

    widget = ConsoleWidget(name="console")
    tabs.addTab(widget, widget.name)

    assert tabs.indexOf(widget) == 0
    assert tabs.tabText(0) == "console"
