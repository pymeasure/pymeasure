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

from pymeasure.experiment import Results

from threading import Event, Thread
try:
    from Queue import Queue
except:
    from queue import Queue


class Listener(Thread):
    """This is the base class for threaded classes that listen for
    data from the measurement. They are intended to be used without
    the Qt display functionality and communicate with basic Python
    Queues.
    """

    def __init__(self,):
        self.abortEvent = Event()
        self.queue = Queue()
        super(Listener, self).__init__()

    def join(self, timeout=0):
        """ Joins the current thread with the Listener and forces an
        abort if the process does not halt after the timeout

        :param timeout: Timeout duration in seconds
        """
        self.abortEvent.wait(timeout)
        if not self.abortEvent.isSet():
            self.abortEvent.set()
        super(Listener, self).join()

    def has_aborted(self):
        """ Returns True if the Listener thread has been aborted
        """
        return self.abort_event.isSet()


class ResultsWriter(Listener):
    """Writes the incoming data through the Results object to
    a CSV file specified in by the results.data_filename.

    :param results: Results object to be written
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
                            new_data[key] = (value * float(current_trace-1) +
                                             data[key])/float(current_trace)
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
        super(AverageManager, self).__init__()

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
                        self.writers.append(ResultsWriter(
                            self.results[trace-1]))
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
            return self.average_results.data_filename.replace(
                    ".csv", "_#%d.csv" % trace)


class ETADisplay(Listener):
    """ Uses the ETA package to print a status message that shows
    the amount of time left for the process. The number of counts
    signifies the number of times the progress queue is expected to
    be updated (once per loop).
    """

    def __init__(self, count):
        from eta import ETA
        self.eta = ETA(count)
        super(ETADisplay, self).__init__()

    def run(self):
        while not self.abortEvent.isSet():
            if not self.queue.empty():
                self.queue.get()
                self.eta.print_status()
        self.eta.done()
