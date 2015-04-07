"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from threading import Event
from Queue import Queue
from qt_variant import QtCore


class QListener(QtCore.QThread):
    """Base class for PyQt4/PySide threaded classes that listen for data
    from the measurement. Each QListener provides methods to act
    as slots for singals.
    """

    def __init__(self, parent=None):
        self.abortEvent = Event()
        super(QListener, self).__init__(parent)

    def join(self, timeout=0):
        self.abortEvent.wait(timeout)
        if not self.abortEvent.isSet():
            self.abortEvent.set()
        super(QListener, self).wait()


class QResultsWriter(QListener):
    """ Class for writing results to a file in the Qt context, where the
    write method is called as a slot to fill up the data
    """

    def __init__(self, results, parent=None):
        self.results = results
        self.queue = Queue()
        super(QResultsWriter, self).__init__(parent)

    def write(self, data):
        """ Slot for writing data asynchronously without closing the file
        """
        self.queue.put(data)

    def run(self):
        with open(self.results.data_filename, 'a', 0) as handle:
            while not self.abortEvent.isSet():
                if not self.queue.empty():
                    data = self.queue.get()
                    handle.write(self.results.format(data))
