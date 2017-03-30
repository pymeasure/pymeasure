#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
from logging.handlers import QueueHandler
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import zmq
    from msgpack_numpy import dumps
except ImportError:
    log.warning("ZMQ and MsgPack are required for TCP communication")

from traceback import format_exc
from time import sleep

from multiprocessing import Queue
from pymeasure.process import StoppableProcess
from .listeners import Recorder
from .results import Results
from .procedure import Procedure
from ..log import TopicQueueHandler
from pymeasure.log import file_log


class Worker(StoppableProcess):
    """ Worker runs the procedure and emits information about
    the procedure and its status over a ZMQ TCP port. In a child
    thread, a Recorder is run to write the results to 
    """

    def __init__(self, results, log_queue=None, log_level=logging.INFO, port=None):
        """ Constructs a Worker to perform the Procedure 
        defined in the file at the filepath
        """
        super(Worker, self).__init__()
        self.port = port
        if not isinstance(results, Results):
            raise ValueError("Invalid Results object during Worker construction")
        self.results = results
        self.procedure = self.results.procedure
        self.procedures_file = self.procedure.__module__
        self.procedure.check_parameters()
        self.procedure.status = Procedure.QUEUED

        self.recorder_queue = Queue()
        self.monitor_queue = Queue()
        if log_queue is None:
            log_queue = Queue()
        self.log_queue = log_queue
        self.log_level = log_level

    def join(self, timeout=0):
        try:
            super(Worker, self).join(timeout)
        except (KeyboardInterrupt, SystemExit):
            log.warning("User stopped Worker join prematurely")
            self.stop()
            super(Worker, self).join(0)

    def emit(self, topic, data):
        """ Emits data of some topic over TCP """
        if isinstance(topic, str):
            topic = topic.encode()
        log.debug("Emitting message: %s %s" % (topic, data))
        try:
            self.publisher.send_multipart([topic, dumps(data)])
        except (NameError, AttributeError):
            pass # No dumps defined
        if topic == b'results':
            self.recorder_queue.put(data)
        elif topic == b'status' or topic == b'progress':
            self.monitor_queue.put((topic.decode(), data))

    def update_status(self, status):
        self.procedure.status = status
        self.emit('status', status)

    def handle_exception(self, exception):
        log.error("Worker caught error in %r" % self.procedure)
        log.exception(exception)
        traceback_str = format_exc()
        self.emit('error', traceback_str)

    def run(self):
        global log
        log = logging.getLogger()
        log.setLevel(self.log_level)
        log.handlers = [] # Remove all other handlers
        log.addHandler(TopicQueueHandler(self.monitor_queue))
        log.addHandler(QueueHandler(self.log_queue))
        log.info("Worker process started")

        self.recorder = Recorder(self.results, self.recorder_queue)
        self.recorder.start()

        locals()[self.procedures_file] = __import__(self.procedures_file)

        # route Procedure methods & log
        self.procedure.should_stop = self.should_stop
        self.procedure.emit = self.emit

        if self.port is not None:
            try:
                self.context = zmq.Context()
                log.debug("Worker ZMQ Context: %r" % self.context)
                self.publisher = self.context.socket(zmq.PUB)
                self.publisher.bind('tcp://*:%d' % self.port)
                log.info("Worker connected to tcp://*:%d" % self.port)
                sleep(0.01)
            except:
                pass

        log.info("Worker started running an instance of %r" % (self.procedure.__class__.__name__))
        self.update_status(Procedure.RUNNING)
        self.emit('progress', 0.)
        # Try to run the startup method
        try:
            self.procedure.startup()
        except Exception as e:
            log.warning("Error in startup method caused Worker to stop prematurely")
            self.handle_exception(e)
            self.update_status(Procedure.FAILED)
            self.recorder_queue.put(None)
            self.monitor_queue.put(None)
            self.stop()
            del self.recorder
            return
        # If all has gone well, run the execute method
        try:
            self.procedure.execute()
        except (KeyboardInterrupt, SystemExit):
            log.warning("User stopped Worker execution prematurely")
            self.update_status(Procedure.FAILED)
        except Exception as e:
            self.handle_exception(e)
            self.update_status(Procedure.FAILED)
        finally:
            self.procedure.shutdown()
            if self.should_stop() and self.procedure.status == Procedure.RUNNING:
                self.update_status(Procedure.ABORTED)
            if self.procedure.status == Procedure.RUNNING:
                self.update_status(Procedure.FINISHED)
                self.emit('progress', 100.)
            self.recorder_queue.put(None)
            self.monitor_queue.put(None)
            self.stop()
            del self.recorder

    def __repr__(self):
        return "<%s(port=%s,procedure=%s,should_stop=%s)>" % (
            self.__class__.__name__, self.port, 
            self.procedure.__class__.__name__, 
            self.should_stop()
        )