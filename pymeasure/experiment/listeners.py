#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from logging import StreamHandler, FileHandler

from os import stat
import json
import pandas as pd
import numpy as np

from ..log import QueueListener
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


class Monitor(QueueListener):
    def __init__(self, results, queue):
        console = StreamHandler()
        console.setFormatter(results.formatter)

        super().__init__(queue, console)


class Listener(StoppableThread):
    """Base class for Threads that need to listen for messages on
    a ZMQ TCP port and can be stopped by a thread-safe method call
    """

    def __init__(self, port, topic='', timeout=0.01):
        """ Constructs the Listener object with a subscriber port
        over which to listen for messages

        :param port: TCP port to listen on
        :param topic: Topic to listen on
        :param timeout: Timeout in seconds to recheck stop flag
        """
        super().__init__()

        self.port = port
        self.topic = topic
        self.context = zmq.Context()
        log.debug(f"{self.__class__.__name__} has ZMQ Context: {self.context!r}")
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode())
        self.subscriber.connect('tcp://localhost:%d' % port)
        log.info("%s connected to '%s' topic on tcp://localhost:%d" % (
            self.__class__.__name__, topic, port))

        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)
        self.timeout = timeout

    def receive(self, flags=0):
        topic, record = self.subscriber.recv_serialized(
            deserialize=lambda msg: (msg[0].decode(), cloudpickle.loads(msg[1])),
            flags=flags
        )
        return topic, record

    def message_waiting(self):
        """Check if we have a message, wait at most until timeout."""
        return self.poller.poll(self.timeout * 1000)  # poll timeout is in ms

    def __repr__(self):
        return "<{}(port={},topic={},should_stop={})>".format(
            self.__class__.__name__, self.port, self.topic, self.should_stop())


class Recorder(QueueListener):
    """ Recorder loads the initial Results for a filepath and
    appends data by listening for it over a queue. The queue
    ensures that no data is lost between the Recorder and Worker.
    """

    def __init__(self, results, queue, **kwargs):
        """ Constructs a Recorder to record the Procedure data into
        the file path, by waiting for data on the subscription port
        """
        self.results = results
        handlers = []

        if self.results.output_format == 'JSON':
            self.handle = self._json_handle
        else:
            for filename in results.data_filenames:
                fh = FileHandler(filename=filename, **kwargs)
                fh.setFormatter(results.formatter)
                fh.setLevel(logging.NOTSET)
                handlers.append(fh)

        super().__init__(queue, *handlers)

    def stop(self):
        for handler in self.handlers:
            handler.close()

        super().stop()

    def _json_handle(self, record):
        """Method to override the normal logging FileHandler when the record is json.
        The json formatter returns a string for compatibility with filehandling, so the first
        step is to re-extract the dict. Then we check various conditions. The end result is a file with a
        single (possibly updated) dictionary of dictionaries"""

        record = json.loads(self.results.formatter.format(record))
        key = list(record.keys())[0]
        item = record[key]

        for file in self.results.data_filenames:
            if stat(file).st_size == 0:
                # this case is deprecated, new files have header in them
                with open(file, 'w') as f:
                    extant = {key: {}}
                    for column, value in item.items():
                        if not isinstance(value, (list,tuple)):
                            extant[key][column] = [value, ]
                        else:
                            extant[key] = item
                    json.dump(extant, f)

            else:
                with open(file, 'r') as f:
                    extant = json.load(f)

                keys = list(extant.keys())
                if len(keys) != 1:
                    raise ValueError(f'got more than one key for json, {len(keys)}')
                data = extant[keys[0]]
                for column, array in data.items():
                    if isinstance(data[column], (list,tuple)):
                        if isinstance(data[column], tuple):
                            data[column] = list(data[column])
                        if isinstance(item[column], (list,tuple,np.ndarray)):
                            data[column] = list(np.concatenate([array,item[column]]))
                        elif isinstance(item[column], (float, int)):
                            data[column].append(item[column])
                        else:
                            raise TypeError(f'got {item[column]} to append but it is type {type(item[column])}')
                    elif isinstance(data[column], (float,int)):
                        if isinstance(item[column], (float,int)):
                            data[column] = [data[column], item[column]]
                        elif isinstance(item[column], (list, tuple, np.ndarray)):
                            data[column] = [data[column], *item[column]]
                        else:
                            TypeError(f'got {item[column]} to add but it is type {type(item[column])}')
                    else:
                        raise TypeError(f'got unexpected type for the old data {data[column]}, {type(data[column])}')

                with open(file, 'w') as f:
                    json.dump(extant, f)





