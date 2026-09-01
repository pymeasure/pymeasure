#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from threading import Event, Thread
from time import monotonic

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class InterruptableEvent(Event):
    """
    This subclass solves the problem indicated in bug
    https://bugs.python.org/issue35935 that prevents the
    wait of an Event to be interrupted by a KeyboardInterrupt.
    """

    def wait(self, timeout: float | None = None) -> bool:
        if timeout is None:
            while not super().wait(0.1):
                pass
            return True
        else:
            deadline = monotonic() + timeout
            while True:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    return self.is_set()
                if super().wait(min(remaining, 0.1)):
                    return True


class StoppableThread(Thread):
    """ Base class for Threads which require the ability
    to be stopped by a thread-safe method call
    """

    def __init__(self):
        super().__init__()
        self._should_stop = InterruptableEvent()
        self._should_stop.clear()

    def join(self, timeout: float | None = 0) -> None:
        """ Joins the current thread and forces it to stop after
        the timeout if necessary

        :param timeout: Timeout duration in seconds
        """
        self._should_stop.wait(timeout)
        if not self.should_stop():
            self.stop()
        return super().join(0)

    def stop(self) -> None:
        self._should_stop.set()

    def should_stop(self) -> bool:
        return self._should_stop.is_set()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(should_stop={self.should_stop()})>"
