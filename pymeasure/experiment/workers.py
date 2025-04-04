#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
from __future__ import annotations

import logging
import time
import traceback
from queue import Queue
from typing import Any, Sequence

import numpy as np

from .listeners import Recorder
from .procedure import Procedure
from .results import Results
from ..thread import StoppableThread

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import zmq
    import cloudpickle
except ImportError:
    zmq = None
    cloudpickle = None
    log.warning("ZMQ and cloudpickle are required for TCP communication")


class Worker(StoppableThread):
    """ Worker runs the procedure and emits information about
    the procedure and its status over a ZMQ TCP port. In a child
    thread, a Recorder is run to write the results to
    """

    def __init__(self, results, log_queue=None, log_level=logging.INFO, port=None):
        """ Constructs a Worker to perform the Procedure
        defined in the file at the filepath
        """
        super().__init__()

        self.port = port
        if not isinstance(results, Results):
            raise ValueError("Invalid Results object during Worker construction")
        self.results = results
        self.results.procedure.check_parameters()
        self.results.procedure.status = Procedure.QUEUED

        self.recorder = None
        self.recorder_queue = Queue()

        self.monitor_queue = Queue()
        if log_queue is None:
            log_queue = Queue()
        self.log_queue = log_queue
        self.log_level = log_level

        global log
        log = logging.getLogger(__name__)
        log.setLevel(self.log_level)
        # log.handlers = []  # Remove all other handlers
        # log.addHandler(TopicQueueHandler(self.monitor_queue))
        # log.addHandler(QueueHandler(self.log_queue))

        self.context = None
        self.publisher = None
        if self.port is not None and zmq is not None:
            try:
                self.context = zmq.Context()
                log.debug("Worker ZMQ Context: %r" % self.context)
                self.publisher = self.context.socket(zmq.PUB)
                self.publisher.bind('tcp://*:%d' % self.port)
                log.info("Worker connected to tcp://*:%d" % self.port)
                # wait so that the socket will be ready before starting to emit messages
                time.sleep(0.3)
            except Exception:
                log.exception("Couldn't establish ZMQ publisher!")
                self.context = None
                self.publisher = None

    def join(self, timeout: int = 0):
        try:
            super().join(timeout)
        except (KeyboardInterrupt, SystemExit):
            log.warning("User stopped Worker join prematurely")
            self.stop()
            super().join(0)

    def emit(self, topic: str, record: Any):
        """ Emits data of some topic over TCP """
        log.debug("Emitting message: %s %s", topic, record)

        try:
            self.publisher.send_serialized(
                record,
                serialize=lambda rec: (topic.encode(), cloudpickle.dumps(rec)),
            )
        except (NameError, AttributeError):
            pass  # No dumps defined
        if topic == 'results':
            self.handle_record(record)
        elif topic == 'batch results':
            self.handle_batch_record(record)
        elif topic == 'status' or topic == 'progress':
            self.monitor_queue.put((topic, record))

    def handle_record(self, record: dict[str, Any]):
        self.recorder.handle(record)

    def handle_batch_record(self, record: Any):
        if self._is_dictionary_of_sequences(record):
            lengths = list(len(value) for value in record.values())
            if not all(length == lengths[0] for length in lengths):
                log.error(
                    'Data loss detected: not all sequences in the batch have the same length.'
                )
                self.stop()
                return

            for index in range(lengths[0]):
                # Handle the records one by one.
                single_record = {key: value[index] for key, value in record.items()}
                self.handle_record(single_record)
        else:
            log.error(f'Unsupported type ({type(record)}) for batch results.')
            self.stop()

    def _is_dictionary_of_sequences(self, record: Any) -> bool:
        """
        Checks if the record is a dictionary of sequences, there are a couple data types that we do
        not want to treat as sequences, such as strings and bytes. This function will return False
        if any of the values in the dictionary are strings or bytes or not a sequence.
        """
        sequence_types = (Sequence, np.ndarray)
        type_exceptions = (str, bytes)
        if not isinstance(record, dict):
            return False
        return all(
            isinstance(value, sequence_types) and not isinstance(value, type_exceptions) for value
            in record.values()
        )

    def handle_abort(self):
        log.exception("User stopped Worker execution prematurely")
        self.update_status(Procedure.ABORTED)

    def handle_error(self):
        log.exception("Worker caught an error on %r", self.procedure)
        traceback_str = traceback.format_exc()
        self.emit('error', traceback_str)
        self.update_status(Procedure.FAILED)

    def is_last(self):
        raise NotImplementedError('should be monkey patched by a manager')

    def update_status(self, status: int):
        self.procedure.status = status
        self.emit('status', status)

    def shutdown(self):
        self.procedure.shutdown()

        if self.should_stop() and self.procedure.status == Procedure.RUNNING:
            self.update_status(Procedure.ABORTED)
        elif self.procedure.status == Procedure.RUNNING:
            self.update_status(Procedure.FINISHED)
            self.emit('progress', 100.)

        self.recorder.stop()
        self.monitor_queue.put(None)
        if self.context is not None:
            # Cleanly close down ZMQ context and associated socket
            # For some reason, we need to close the socket before the
            # context, otherwise context termination hangs.
            self.publisher.close()
            self.context.term()

    def run(self):
        log.info("Worker thread started")

        self.procedure = self.results.procedure

        self.recorder = Recorder(self.results, self.recorder_queue)
        self.recorder.start()

        # locals()[self.procedures_file] = __import__(self.procedures_file)

        # route Procedure methods & log
        self.procedure.should_stop = self.should_stop
        self.procedure.emit = self.emit
        self.procedure.is_last = self.is_last

        log.info("Worker started running an instance of %r", self.procedure.__class__.__name__)
        self.update_status(Procedure.RUNNING)
        self.emit('progress', 0.)

        try:
            self.procedure.startup()
            self.procedure.evaluate_metadata()
            self.results.store_metadata()
            self.procedure.execute()
        except (KeyboardInterrupt, SystemExit):
            self.handle_abort()
        except Exception:
            self.handle_error()
        finally:
            self.shutdown()
            self.stop()

    def __repr__(self):
        return "<{}(port={},procedure={},should_stop={})>".format(
            self.__class__.__name__, self.port,
            self.procedure.__class__.__name__,
            self.should_stop()
        )
