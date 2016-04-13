#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
from logging.handlers import QueueHandler

try:
    import zmq
    from msgpack_numpy import loads, dumps
except ImportError:
    log.warning("ZMQ and MsgPack are required for TCP communication")

from time import sleep

from threading import Thread
from pymeasure.thread import StoppableThread
from pymeasure.process import StoppableProcess
from .results import Results

class Listener(StoppableThread):
    """Base class for Threads that need to listen for messages
    on a ZMQ TCP port and can be stopped by a thread-safe
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
        super(Listener, self).__init__()

    def receive(self, flags=0):
        topic, raw_data = self.subscriber.recv_multipart(flags=flags)
        return topic.decode(), loads(raw_data, encoding='utf-8')

    def message_waiting(self):
        return self.poller.poll(self.timeout)

    def __repr__(self):
        return "<%s(port=%s,topic=%s,should_stop=%s)>" % (
            self.__class__.__name__, self.port, self.topic, self.should_stop())


class Recorder(Thread):
    """ Recorder loads the initial Results for a filepath and
    appends data by listening for it over a queue. The queue
    ensures that no data is lost between the Recorder and Worker.
    """

    def __init__(self, results, queue):
        """ Constructs a Recorder to record the Procedure data
        into the filepath, by waiting for data on the subscription
        port
        """
        self.results = results
        self.queue = queue
        super(Recorder, self).__init__()

    def run(self):
        with open(self.results.data_filename, 'ab', buffering=0) as handle:
            log.info("Recording to file: %s" % self.results.data_filename)
            while True:
                data = self.queue.get()
                if data is None:
                    break
                handle.write(self.results.format(data).encode())
            log.info("Recorder caught stop command")

class Daemon(StoppableThread):
    """ Daemon receives commands by listening for it over a queue and
    puts the response in another queue. The queues ensure that no data
    is lost between the Daemon and Server.
    """

    def __init__(self):
        """ Constructs a Daemon to receive commands from a Server process
        """
        super(Daemon, self).__init__()

    def run(self):
        while True:
            data = self.commands.command_queue.get()
            if data is None:
                self.stop()
            response = self.commands.eval(data)
            self.commands.response_queue.put(response.encode())
        log.info("Daemon %s caught stop command" %self.name)

class Server(StoppableProcess):
    """ Server manages and runs Daemon threads, publishes received data on a ZMQ socket
    and keeps a data buffer to prevent lost packages.
    """
    def __init__(self, port, log_queue=None, log_level=logging.INFO):
        self.daemons = []
        self.port = port
        if log_queue is None:
            log_queue = Queue()
        self.log_queue = log_queue
        self.log_level = log_level

        super(Server, self).__init__()

    def run(self):
        global log
        log = logging.getLogger()
        log.setLevel(self.log_level)
        # log.handlers = [] # Remove all other handlers
        log.addHandler(QueueHandler(self.log_queue))
        log.info("Server process %s started" %self.name)

        if self.port is not None:
            self.context = zmq.Context()
            log.debug("Worker ZMQ Context: %r" % self.context)
            self.publisher = self.context.socket(zmq.PUB)
            self.publisher.bind('tcp://*:%d' % self.port)
            log.info("Worker connected to tcp://*:%d" % self.port)
            sleep(0.01)

        while not self.should_stop():
            data = self.queue.get()
            if data is None:
                self.stop()
            self.emit(*data)
            if data[0] == 'create_instrument':
                self.create_daemon(*data[1])
        log.info("Server %s caught stop command" %self.name)

    def emit(self, topic, data):
        """ Emits data of some topic over TCP """
        if isinstance(topic, str):
            topic = topic.encode()
        log.debug("Emitting message: %s %s" % (topic, data))
        try:
            self.publisher.send_multipart([topic, dumps(data)])
        except (NameError, AttributeError):
            pass # No dumps defined