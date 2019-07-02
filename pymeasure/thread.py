#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from threading import Thread, Event

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StoppableThread(Thread):
    """ Base class for Threads which require the ability
    to be stopped by a thread-safe method call
    """

    def __init__(self):
        super().__init__()
        self._should_stop = Event()
        self._should_stop.clear()

    def join(self, timeout=0):
        """ Joins the current thread and forces it to stop after
        the timeout if necessary

        :param timeout: Timeout duration in seconds
        """
        self._should_stop.wait(timeout)
        if not self.should_stop():
            self.stop()
        return super().join(0)

    def stop(self):
        self._should_stop.set()

    def should_stop(self):
        return self._should_stop.is_set()

    def __repr__(self):
        return "<%s(should_stop=%s)>" % (
            self.__class__.__name__, self.should_stop())
