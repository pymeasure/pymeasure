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

from ..log import LogHandler
from ..Qt import QtWidgets, QtCore, QtGui
from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HTMLFormatter(logging.Formatter):
    level_colors = {
        "DEBUG": "DarkGray",
        # "INFO": "Black",
        "WARNING": "DarkOrange",
        "ERROR": "Red",
        "CRITICAL": "DarkRed",
    }

    html_replacements = {
        "\r\n": "<br>  ",
        "\n": "<br>  ",
        "\r": "<br>  ",
        "  ": "&nbsp;" * 2,
        "\t": "&nbsp;" * 4,
    }

    def format(self, record):
        formatted = super().format(record)

        # Apply color if a level-color is defined
        if record.levelname in self.level_colors:
            formatted = f"<font color=\"{self.level_colors[record.levelname]}\">{formatted}</font>"

        # ensure newlines and indents are preserved
        for replacement in self.html_replacements.items():
            formatted = formatted.replace(*replacement)

        # Prepend the level as HTML comment
        formatted = f"<!--{record.levelname}-->{formatted}"

        return formatted


class LogWidget(TabWidget, QtWidgets.QWidget):
    """ Widget to display logging information in GUI

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.managed_window.ManagedWindowBase>`
    """

    fmt = '%(asctime)s : %(message)s (%(levelname)s)'
    datefmt = '%m/%d/%Y %I:%M:%S %p'

    tab_widget = None
    tab_index = None

    _blink_qtimer = QtCore.QTimer()
    _blink_color = None
    _blink_state = False

    def __init__(self, name, parent=None, fmt=None, datefmt=None):
        if fmt is not None:
            self.fmt = fmt
        if datefmt is not None:
            self.datefmt = datefmt

        super().__init__(name, parent)
        self._setup_ui()
        self._layout()

        # Setup blinking
        self._blink_qtimer.timeout.connect(self._blink)
        self.handler.connect(self._blinking_start)

    def _setup_ui(self):
        self.view = QtWidgets.QPlainTextEdit()
        self.view.setReadOnly(True)
        self.handler = LogHandler()
        self.handler.setFormatter(HTMLFormatter(
            fmt=self.fmt,
            datefmt=self.datefmt,
        ))
        self.handler.connect(self.view.appendHtml)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def _blink(self):
        self.tab_widget.tabBar().setTabTextColor(
            self.tab_index,
            QtGui.QColor("black" if self._blink_state else self._blink_color)
        )

        self._blink_state = not self._blink_state

    def _blinking_stop(self, index):
        if index == self.tab_index:
            self._blink_qtimer.stop()
            self._blink_state = True
            self._blink()

            self._blink_color = None
            self.tab_widget.setTabIcon(self.tab_index, QtGui.QIcon())

    def _blinking_start(self, message):
        # Delayed setup, since only now the widget is added to the TabWidget
        if self.tab_widget is None:
            self.tab_widget = self.parent().parent()
            self.tab_index = self.tab_widget.indexOf(self)
            self.tab_widget.tabBar().setIconSize(QtCore.QSize(12, 12))
            self.tab_widget.tabBar().currentChanged.connect(self._blinking_stop)

        if message.startswith("<!--ERROR-->") or message.startswith("<!--CRITICAL-->"):
            error = True
        elif message.startswith("<!--WARNING-->"):
            error = False
        else:  # no blinking
            return

        # Check if the current tab is actually the log-tab
        if self.tab_widget.currentIndex() == self.tab_index:
            self._blinking_stop(self.tab_widget.currentIndex())
            return

        # Define color and icon based on severity
        # If already red, this should not be updated
        if not self._blink_color == "red":
            self._blink_color = "red" if error else "darkorange"

            pixmapi = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical if \
                error else QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning

            icon = self.style().standardIcon(pixmapi)
            self.tab_widget.setTabIcon(self.tab_index, icon)

        # Start timer
        self._blink_qtimer.start(500)
