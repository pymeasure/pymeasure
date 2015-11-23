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

from .qt_variant import QtCore

import zmq
from msgpack import loads
from time import sleep
from multiprocessing import Event

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
        self.context = zmq.Context.instance()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect('tcp://localhost:%d' % port)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())
        log.info("%s connected to '%s' topic on tcp://localhost:%d" % (
            self.__class__.__name__, topic, port))

        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)
        self.timeout = timeout
        super(QListener, self).__init__()

    def receive(self):
        topic, raw_data = self.subscriber.recv()
        return topic.decode(), loads(raw_data).decode()

    def message_waiting(self):
        return self.poller.poll(self.timeout)

    def __repr__(self):
        return "<%s(port=%s,topic=%s,should_stop=%s)>" % (
            self.__class__.__name__, self.port, self.topic, self.should_stop())


class Monitor(QListener):
    """ Monitor listens for status and progress messages
    on a ZMQ TCP port and routes them to signals and slots
    """

    status = QtCore.QSignal(int)
    progress = QtCore.QSignal(float)
    running = QtCore.QSignal()
    failed = QtCore.QSignal()
    finished = QtCore.QSignal()

    def __init__(self, port, timeout=0.01):
        super(Monitor, self).__init__(port, topic='', timeout=timeout)

    def run(self):
        while not self.should_stop():
            if self.message_waiting():
                topic, data = self.receive()
                if topic == 'status':
                    self.status.emit(data)
                    if data == Procedure.FAILED:
                        self.failed.emit()
                    elif data == Procedure.FINISHED:
                        self.finished.emit()
                elif topic == 'progress':
                    self.progress.emit(data)
        log.info("Monitor caught stop command")





