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
from automate.experiment import Results

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


class ResultsWriter(Listener):
    """Writes the incoming data through the Results object to 
    """
    
    def __init__(self, results):
        self.results = results
        super(ResultsWriter, self).__init__()
        
    def run(self):
        with open(self.results.data_filename, 'a', 0) as handle:
            while not self.abortEvent.isSet():
                if not self.queue.empty():
                    data = self.queue.get()
                    handle.write(self.results.format(data))


class AverageWriter(ResultsWriter):
    
    def __init__(self, results):
        super(AverageWriter, self).__init__(results)
        self.loop_back = Event()
        self.first_pass = True

    def run(self):
        with open(self.results.data_filename, 'a', 0) as handle:
            start_pointer = handle.tell()
            current_trace = 1
            while not self.abortEvent.isSet():
                if self.loop_back.isSet():
                    self.first_pass = False
                    self.current_trace += 1
                    handle.seek(start_pointer)
                    self.loop_back.reset()
                if not self.queue.empty():
                    data = self.queue.get()
                    if not self.first_pass:
                        current_pointer = handle.tell()
                        old_data = self.results.parse(handle.readline())
                        handle.seek(current_pointer)
                        new_data = {}
                        for key, value in old_data.iteritems():
                            new_data[key] = (value * float(current_trace-1) + data[key])/float(current_trace)
                        handle.write(self.results.format(new_data))
                    else:
                        handle.write(self.results.format(data))


class AverageManager(Listener):
    """ Manages writing data to different files during the trace average so that
    all data is retained
    """

    LABEL = 'Trace'
    
    def __init__(self, average_results, traces=1):
        self.average_results = average_results
        self.traces = traces
        super(TraceAverageWriter, self).__init__()
        
    def run(self):
        average_writer = AverageWriter(self.average_results)
        average_writer.start()
        current_trace = 0
        self.results = []
        self.writers = []
        while not self.abortEvent.isSet():
            if not self.queue.empty():
                data = self.queue.get()
                if self.traces > 1:
                    trace = data.pop(AverageManager.LABEL)
                    if trace > current_trace:
                        if trace >= 2:
                            average_writer.loop_back.set()
                        self.results.append(Results(
                            self.average_results.procedure, 
                            self.trace_filename(trace)
                        ))
                        self.writers.append(ResultsWriter(self.results[trace-1]))
                        self.writers[trace-1].start()
                    self.writers[trace-1].queue.put(data)
                average_writer.queue.put(data)
                

        average_writer.abortEvent.set()
    
    @property
    def trace_filename(self, trace):
        """ Return the current trace filename """
        if self.traces < 2:
            return self.average_results.data_filename
        else:
            return self.average_results.data_filename.replace(".csv", "_#%d.csv" % trace)


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

try:

    from PyQt4.QtCore import QThread, pyqtSignal

    class QListener(QThread):
        """Base class for PyQt4 threaded classes that listen for data
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
            super(QListener, self).join()
        
        
    class QCSVWriter(QListener):
        """ Class for writing to CSV in the Qt context, where the write method
        is called as a slot to fill up the data
        """
        
        def __init__(self, filename, labels=None, parent=None):
            self.filename = filename
            self.labels = labels
            self.queue = Queue()
            super(QCSVWriter, self).__init__(parent)
            
        def write(self, data):
            """ Slot for writing data asynchronously without closing the file
            """
            self.queue.put(data)
            
        def run(self):
            import csv
            with open(self.filename, 'a', 0) as csvfile:
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
        
except:
    pass # PyQt4 is not installed
