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

from ..browser import Browser
from ..Qt import QtWidgets

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BrowserWidget(QtWidgets.QWidget):
    """
    Widget wrapper for :class:`Browser<pymeasure.display.browser.Browser>` class
    """
    def __init__(self, *args, parent=None):
        super().__init__(parent)
        self.browser_args = args
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.browser = Browser(*self.browser_args, parent=self)
        self.clear_button = QtWidgets.QPushButton('Clear all', self)
        self.clear_button.setEnabled(False)
        self.hide_button = QtWidgets.QPushButton('Hide all', self)
        self.hide_button.setEnabled(False)
        self.show_button = QtWidgets.QPushButton('Show all', self)
        self.show_button.setEnabled(False)
        self.open_button = QtWidgets.QPushButton('Open', self)
        self.open_button.setEnabled(True)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.show_button)
        hbox.addWidget(self.hide_button)
        hbox.addWidget(self.clear_button)
        hbox.addStretch()
        hbox.addWidget(self.open_button)

        vbox.addLayout(hbox)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)
