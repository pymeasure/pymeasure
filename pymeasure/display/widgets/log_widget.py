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

from ..log import LogHandler
from ..Qt import QtGui
from .tab_widget import TabWidget

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LogWidget(TabWidget, QtGui.QWidget):
    """ Widget to display logging information in GUI

    It is recommended to include this widget in all subclasses of
    :class:`ManagedWindowBase<pymeasure.display.windows.ManagedWindowBase>`
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.view = QtGui.QPlainTextEdit()
        self.view.setReadOnly(True)
        self.handler = LogHandler()
        self.handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s : %(message)s (%(levelname)s)',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        ))
        self.handler.connect(self.view.appendPlainText)

    def _layout(self):
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)

        vbox.addWidget(self.view)
        self.setLayout(vbox)
