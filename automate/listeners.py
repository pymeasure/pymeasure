#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic classes for experiment listeners
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from threading import Event, Thread
from Queue import Queue

class Listener(Thread):
    """Base class for threaded classes that listen for data
    from the measurement. Each Listener has its own queue
    that should be filled with measurement data.    
    """
        
    def __init__(self,):
        self.abortEvent = Event()
        self.queue = Queue()
        super(Listener, self).__init__()
        
    def join(self, timeout=0):
        self.abortEvent.wait(timeout)
        if not self.abortEvent.isSet():
            self.abortEvent.set()
        super(Listener, self).join()
        
class CSVWriter(Listener):
    """Writes the incoming data to a CSV file using a comma to 
    delimit the rows and a line break to delimit the columns.    
    """
    
    def __init__(self, filename, labels=None):
        self.filename = filename
        self.labels = labels
        super(DataWriter, self).__init__()
        
    def run(self):
        import csv
        with open(self.filename, 'wb', 0) as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            firstLine = True
            while not self.abortEvent.isSet():
                if not self.queue.empty():
                    data = self.queue.get()
                    if self.labels is None:
                        if firstLine:
                            writer.writerow(data.keys())
                            firstLine = False
                        writer.writerow(data.values())
                    else:
                        if firstLine:
                            writer.writerow(self.labels)
                            firstLine = False
                        writer.writerow([data[x] for x in self.labels])

class LogWriter(Listener):
    """ Writes the contents of a Queue to the specified filename
    """

    def __init__(self, filename):
        self.filename = filename
        super(LogWriter, self).__init__()
        
    def run(self):
        with open(self.filename, 'wb', 0) as handle:
            while not self.abortEvent.isSet():
                if not self.queue.empty():
                    handle.writeline(self.queue.get())
                    
class ETADisplay(Listener):
    """ Uses the ETA package to print a status message that shows
    the amount of time left for the process. The number of counts
    signifies the number of times the progress queue is expected to
    be updated (once per loop).    
    """
    
    def __init__(self, count):
        from eta import ETA
        self.eta = eta = ETA(count)
        super(ETADisplay, self).__init__()
        
    def run(self):
        while not self.abortEvent.isSet():
            if not self.queue.empty():
                self.queue.get()
                self.eta.print_status()
        self.eta.done()
