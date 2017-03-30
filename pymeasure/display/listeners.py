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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from .Qt import QtCore

try:
    import zmq
    from msgpack_numpy import loads
except ImportError:
    log.warning("ZMQ and MsgPack are required for TCP communication")

from time import sleep

from pymeasure.display.thread import StoppableQThread
from pymeasure.experiment.procedure import Procedure


class QListener(StoppableQThread):
    """Base class for QThreads that need to listen for messages
    on a ZMQ TCP port and can be stopped by a thread- and process-safe
    method call
    """

    def __init__(self, port, topic='', timeout=0.01):
        """ Constructs the Listener object with a subscriber port 
        over which to listen for messages

        :param port: TCP port to listen on
        :param topic: Topic to listen on
        :param timeout: Timeout in seconds to recheck stop flag
        """
        self.port = port
        self.topic = topic
        self.context = zmq.Context()
        log.debug("%s has ZMQ Context: %r" % (self.__class__.__name__, self.context))
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect('tcp://localhost:%d' % port)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())
        log.info("%s connected to '%s' topic on tcp://localhost:%d" % (
            self.__class__.__name__, topic, port))

        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)
        self.timeout = timeout
        super(QListener, self).__init__()

    def receive(self, flags=0):
        topic, raw_data = self.subscriber.recv_multipart(flags=flags)
        return topic.decode(), loads(raw_data, encoding='utf-8')

    def message_waiting(self):
        return self.poller.poll(self.timeout)

    def __repr__(self):
        return "<%s(port=%s,topic=%s,should_stop=%s)>" % (
            self.__class__.__name__, self.port, self.topic, self.should_stop())


class Monitor(QtCore.QThread):
    """ Monitor listens for status and progress messages
    from a Worker through a queue to ensure no messages
    are lost
    """

    status = QtCore.QSignal(int)
    progress = QtCore.QSignal(float)
    log = QtCore.QSignal(object)
    worker_running = QtCore.QSignal()
    worker_failed = QtCore.QSignal()
    worker_finished = QtCore.QSignal() # Distinguished from QThread.finished
    worker_abort_returned = QtCore.QSignal()

    def __init__(self, queue):
        self.queue = queue
        super(Monitor, self).__init__()

    def run(self):
        while True:
            data = self.queue.get()
            if data is None:
                break
            topic, data = data
            if topic == 'status':
                self.status.emit(data)
                if data == Procedure.RUNNING:
                    self.worker_running.emit()
                elif data == Procedure.FAILED:
                    self.worker_failed.emit()
                elif data == Procedure.FINISHED:
                    self.worker_finished.emit()
                elif data == Procedure.ABORTED:
                    self.worker_abort_returned.emit()
            elif topic == 'progress':
                self.progress.emit(data)
            elif topic == 'log':
                self.log.emit(data)

        log.info("Monitor caught stop command")





