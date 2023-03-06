"""Test thread-safe access to instrument connections.

See https://github.com/pymeasure/pymeasure/issues/506
"""
#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import queue
import threading
import time

from pymeasure.instruments.fakes import FakeInstrument


class ThreadedAccessTester(FakeInstrument):
    """Pause-able instrument class for testing threaded access."""
    def __init__(self, adapter, name="Threadtest instr", event_timeout=1):
        super().__init__(adapter, name)
        self._event_timeout = event_timeout
        self._wait_timed_out = False

    def wait_for(self, query_delay: threading.Event):
        """Wait until the passed event has been set.

        Uses the fact that we can pass a delay to ask(), that is passed to
        wait_for, to have per-thread events when invoking ask()
        """
        timed_out = not query_delay.wait(timeout=self._event_timeout)
        # Latching way to store timed-out event(s)
        # TODO: Needs locks or atomic access to be guaranteed to be correct
        self._wait_timed_out = self._wait_timed_out or timed_out


def test_thieving_ask():
    """Avoid that another thread can interrupt an occurring ask() and steal its reply.

    mermaid diagram:
    sequenceDiagram
        Note over Thread1: ask(CMD1)
        activate Thread1
        Thread1->>connection: write CMD1
        Note over Thread2: ask(CMD2)
        activate Thread2
        Thread2->>connection: write CMD2
        connection-->>Thread2: read REPLY1
        Note left of Thread2: wrong reply!
        deactivate Thread2
        connection-->>Thread1: read REPLY2
        Note right of Thread1: wrong reply!
        deactivate Thread1
    """
    inst = ThreadedAccessTester("")

    q1 = queue.Queue()
    t1Event = threading.Event()
    t1 = threading.Thread(target=lambda q, e: q.put(inst.ask("M1", e)), args=(q1, t1Event))
    t1.start()

    q2 = queue.Queue()
    t2Event = threading.Event()
    t2 = threading.Thread(target=lambda q, e: q.put(inst.ask("M2", e)), args=(q2, t2Event))
    t2.start()

    t2Event.set()  # Wake thread 2 so it could steal the read buffer meant for thread 1
    time.sleep(0.1)
    t1Event.set()  # Now wake up thread 1 to fetch its reply
    t2.join(timeout=2)
    t1.join(timeout=2)

    assert not inst._wait_timed_out
    assert q1.get() == "M1"
    assert q2.get() == "M2"
