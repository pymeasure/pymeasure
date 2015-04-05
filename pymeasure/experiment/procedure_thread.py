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

from procedure import Procedure

from threading import Event, Thread
from Queue import Queue


class ProcedureThread(Thread):
    """Encapsulates the Procedure to be run within a thread."""
    
    def __init__(self):
        Thread.__init__(self)
        self.procedure = None
        self.abortEvent = Event()
        self.abortEvent.clear()
        self.dataQueues = []
        self.progressQueue = Queue()
        self.finished = Event()
        
    def load(self, procedure):
        if not isinstance(procedure, Procedure):
            raise ValueError("Loading object must be inhereted from the"
                             " Procedure class")
        self.procedure = procedure
        self.procedure.status = Procedure.QUEUED
        self.procedure.hasAborted = self.hasAborted
        self.procedure.emitData = self.emitData
        self.procedure.emitProgress = self.emitProgress
        
    def run(self):
        if self.procedure is None:
            raise Exception("Attempting to run Procedure object before loading")
        self.procedure.status = Procedure.RUNNING
        self.procedure.enter()
        try:
            self.procedure.execute()
        except:
            self.procedure.status = Procedure.FAILED
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
        finally:
            self.procedure.exit()
            if self.procedure.status == Procedure.RUNNING:
                self.procedure.status = Procedure.FINISHED
                self.emitProgress(100.)
            self.finished.set()
            self.abortEvent.set() # ensure the thread joins
                  
    def emitProgress(self, percent):
        self.progressQueue.put(percent)
    
    def emitFinished(self):
        self.finished.set()
    
    def addDataQueue(self, queue):
        self.dataQueues.append(queue)
            
    def emitData(self, data):
        for queue in self.dataQueues:
            queue.put(data)
    
    def isRunning(self):
        return self.isAlive()
    
    def hasAborted(self):
        return self.abortEvent.isSet()
        
    def abort(self):
        self.abortEvent.set()
        self.procedure.status = Procedure.ABORTED
        
    def join(self, timeout=0):
        self.abortEvent.wait(timeout)
        if not self.abortEvent.isSet():
            self.abortEvent.set()
        super(ProcedureThread, self).join()