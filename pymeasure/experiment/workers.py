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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import zmq
from msgpack import dumps
from traceback import format_exc

from .process import StoppableProcess
from .results import Results
from .procedure import Procedure


class ProcedureWorker(StoppableProcess):
    """ ProcedureWorker runs the procedure and emits information about
    the procedure and its status over a ZMQ channel
    """

    def __init__(self, filepath, channel):
        """ Constructs a ProcedureWorker to perform the Procedure 
        defined in the file at the filepath
        """
        self.results = Results.load(filepath)
        self.procedure = self.results.procedure
        self.procedure.status = Procedure.QUEUED

        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(channel)

        # route Procedure output
        self.procedure.should_stop = self.should_stop
        self.procedure.emit = self.emit
        super(ProcedureWorker, self).__init__()

    def emit(self, topic, data):
        self.publisher.send_multipart([topic.encode(), dumps(data).encode()])

    def update_status(self, status):
        self.status = status
        self.emit('status', status)

    def handle_exception(self, expection):
        log.error("ProcedureWorker caught error in %r" % self.procedure)
        log.exception(exception)
        traceback_str = format_exc()
        self.emit('error', traceback_str)

    def run(self):
        log.info("Running %r with %r" % (self.procedure, self))
        self.update_status(Procedure.RUNNING)
        self.emit('progress', 0.)
        self.procedure.enter()
        try:
            self.procedure.execute()
        except Exception as e:
            self.handle_exception(e)
            self.update_status(Procedure.FAILED)
        finally:
            self.procedure.exit()
            if self.procedure.status == Procedure.RUNNING:
                self.update_status(Procedure.FINISHED)
                self.emit('progress', 100.)
            self.stop()
