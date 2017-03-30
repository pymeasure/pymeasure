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
from threading import Thread
from multiprocessing import Queue
from logging.handlers import QueueHandler
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

def console_log(logger, level=logging.INFO, queue=None):
    """Create a console log handler. Return a scribe thread object."""
    if queue is None:
        queue = Queue()
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(
        fmt='%(asctime)s: %(message)s (%(name)s, %(levelname)s)',
        datefmt='%I:%M:%S %p')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    scribe = Scribe(queue)
    return scribe

def file_log(logger, log_filename, level=logging.INFO, queue=None):
    """Create a file log handler. Return a scribe thread object."""
    if queue is None:
        queue = Queue()
    logger.setLevel(level)
    ch = logging.FileHandler(log_filename)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    scribe = Scribe(queue)
    return scribe


class Scribe(Thread):
    """ Scribe class which logs records as retrieved from a queue to support consistent
    multi-process logging.

    :param queue: The multiprocessing queue which the scriber will listen to.
    """
    def __init__(self, queue):
        self.queue = queue
        super(Scribe, self).__init__(name='logging-thread')

    def stop(self):
        self.queue.put(None)
        self.join()

    def run(self):
        log.info("Starting logger scribe")
        while True:
            try:
                record = self.queue.get()
            except (KeyboardInterrupt, SystemExit):
                break
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)

def setup_logging(logger=None, console=False, console_level='INFO', filename='', file_level='DEBUG', queue=None):
    """Setup logging for console and/or file logging. Returns a scribe thread object.
    Defaults to no logging."""    
    if queue is None:
        queue = Queue()
    if logger is None:
        logger = logging.getLogger()
    logger.handlers = []
    if console:
        console_log(logger, level=getattr(logging,console_level))
        logger.info('Set up console logging')
    if filename is not '':
        file_log(logger, filename, level=getattr(logging,file_level))
        logger.info('Set up file logging')
    scribe = Scribe(queue)
    return scribe

class TopicQueueHandler(QueueHandler):

    def __init__(self, queue, topic='log'):
        super(TopicQueueHandler, self).__init__(queue)
        self.topic = topic

    def enqueue(self, record):
        self.queue.put_nowait([self.topic, record])