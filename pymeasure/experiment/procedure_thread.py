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

from .procedure import Procedure

from threading import Event, Thread
try:
    from Queue import Queue
except:
    from queue import Queue


class ProcedureThread(Thread):
    """Encapsulates the Procedure to be run within a thread."""

    def __init__(self):
        Thread.__init__(self)
        self.procedure = None
        self.abort_event = Event()
        self.abort_event.clear()
        self.data_queues = []
        self.progress_queue = Queue()
        self.finished = Event()

    def load(self, procedure):
        if not isinstance(procedure, Procedure):
            raise ValueError("Loading object must be inhereted from the"
                             " Procedure class")
        self.procedure = procedure
        self.procedure.status = Procedure.QUEUED
        self.procedure.has_aborted = self.has_aborted
        self.procedure.emit_data = self.emit_data
        self.procedure.emit_progress = self.emit_progress

    def run(self):
        if self.procedure is None:
            raise Exception("Attempting to run Procedure object "
                            "before loading")
        self.procedure.status = Procedure.RUNNING
        self.procedure.enter()
        try:
            self.procedure.execute()
        except:
            self.procedure.status = Procedure.FAILED

            import sys
            import traceback

            traceback.print_exc(file=sys.stdout)
        finally:
            self.procedure.exit()
            if self.procedure.status == Procedure.RUNNING:
                self.procedure.status = Procedure.FINISHED
                self.emit_progress(100.)
            self.finished.set()
            self.abort_event.set()  # ensure the thread joins

    def emit_progress(self, percent):
        self.progress_queue.put(percent)

    def emit_finished(self):
        self.finished.set()

    def add_data_queue(self, queue):
        self.data_queues.append(queue)

    def emit_data(self, data):
        for queue in self.data_queues:
            queue.put(data)

    def is_running(self):
        return self.isAlive()

    def has_aborted(self):
        return self.abort_event.isSet()

    def abort(self):
        self.abort_event.set()
        self.procedure.status = Procedure.ABORTED

    def join(self, timeout=0):
        self.abort_event.wait(timeout)
        if not self.abort_event.isSet():
            self.abort_event.set()
        super(ProcedureThread, self).join()
