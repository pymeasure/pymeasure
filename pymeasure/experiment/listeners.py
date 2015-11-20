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

import zmq
from msgpack import dumps, loads
from multiprocessing import Process, Event

from .process import StoppableProcess
from .results import Results


class Listener(StoppableProcess):
    """Base class for Processes that need to listen for messages
    on a ZMQ channel and can be stopped by a thread- and process-safe
    method call
    """

    def __init__(self, channel, topic=''):
        """ Constructs the Listener object with a subscriber channel 
        over which to listen for messages

        :param channel: Channel to listen on
        """
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(channel)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())
        super(Listener, self).__init__()

    def receive(self):
        topic, raw_data = self.subscriber.recv()
        return topic.decode(), loads(raw_data).decode()

    def __repr__(self):
        return "<%s(channel=%s,topic=%s,should_stop=%s)>" % (
            self.__class__.__name__, channel, topic, self.should_stop())


class ResultsWriter(Listener):
    """ ResultsWriter loads the initial Results for a filepath and
    appends data by listening for it over a ZMQ channel
    """

    def __init__(self, filepath, channel, topic='results'):
        """ Constructs a ResultsWriter to record the Procedure data
        into the filepath, by waiting for data on the subscription
        channel
        """
        self.results = Results.load(filepath)
        super(ResultsWriter, self).__init__(channel, topic)

    def run(self):
        with open(self.results.data_filename, 'ab', buffering=0) as handle:
            while not self.should_stop():
                topic, data = self.receive()
                handle.write(self.results.format(data).encode())
