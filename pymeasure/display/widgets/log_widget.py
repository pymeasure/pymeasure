#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from ..Qt import QtWidgets
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

        return formatted


class LogWidget(TabWidget, QtWidgets.QWidget):
    """ Widget to display logging information in GUI

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.managed_window.ManagedWindowBase>`
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.view = QtWidgets.QPlainTextEdit()
        self.view.setReadOnly(True)
        self.handler = LogHandler()
        self.handler.setFormatter(HTMLFormatter(
            fmt='%(asctime)s : %(message)s (%(levelname)s)',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        ))
        self.handler.connect(self.view.appendHtml)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.view)
        self.setLayout(vbox)
