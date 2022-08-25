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

from logging import Handler

from .Qt import QtCore

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LogHandler(Handler):
    # Class Emitter is added to keep compatibility with PySide2
    # 1. Signal needs to be class attribute of a QObject subclass
    # 2. logging Handler emit method clashes with QObject emit method
    # 3. As a consequence, the LogHandler cannot inherit both from
    # Handler and QObject
    # 4. A new utility class Emitter subclass of QObject is
    # introduced to handle record Signal and workaround the problem
    class Emitter(QtCore.QObject):
        record = QtCore.QSignal(object)

    def __init__(self):
        super().__init__()
        self.emitter = self.Emitter()

    def connect(self, *args, **kwargs):
        return self.emitter.record.connect(*args, **kwargs)

    def emit(self, record):
        self.emitter.record.emit(self.format(record))
