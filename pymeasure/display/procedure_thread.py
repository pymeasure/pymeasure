#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands
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

from pymeasure.experiment import Procedure
from .qt_variant import QtCore

from threading import Event


class QProcedureThread(QtCore.QThread):
    """Encapsulates the Procedure to be run within a QThread,
    compatible with PyQt4.
    """

    data = QtCore.QSignal(dict)
    progress = QtCore.QSignal(float)
    status_changed = QtCore.QSignal(int)
    finished = QtCore.QSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.procedure = None
        self.abort_event = Event()
        self.abort_event.clear()

    def load(self, procedure):
        if not isinstance(procedure, Procedure):
            raise ValueError("Loading object must be inhereted from the"
                             " Procedure class")
        self.procedure = procedure
        self.procedure.status = Procedure.QUEUED
        self.procedure.has_aborted = self.has_aborted
        self.procedure.emit_data = self.data.emit
        self.procedure.emit_progress = self.progress.emit

    def run(self):
        if self.procedure is None:
            raise Exception("Attempting to run Procedure object "
                            "before loading")
        self.procedure.status = Procedure.RUNNING
        self.status_changed.emit(self.procedure.status)
        self.procedure.enter()
        try:
            self.procedure.execute()
        except:
            self.procedure.status = Procedure.FAILED
            self.status_changed.emit(self.procedure.status)

            import sys
            import traceback

            traceback.print_exc(file=sys.stdout)
        finally:
            self.procedure.exit()
            if self.procedure.status == Procedure.RUNNING:
                self.procedure.status = Procedure.FINISHED
                self.status_changed.emit(self.procedure.status)
                self.progress.emit(100.)
            self.finished.emit()
            self.abort_event.set()  # ensure the thread joins

    def has_aborted(self):
        return self.abort_event.isSet()

    def abort(self):
        self.abort_event.set()
        self.procedure.status = Procedure.ABORTED
        self.status_changed.emit(self.procedure.status)

    def join(self, timeout=0):
        self.abort_event.wait(timeout)
        if not self.abort_event.isSet():
            self.abort_event.set()
        super(QProcedureThread, self).wait()
