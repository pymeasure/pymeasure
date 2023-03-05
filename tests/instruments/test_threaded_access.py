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

from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument


class ThreadedAccessTester(Instrument):
    """Pause-able instrument class for testing threaded access.

    It automatically pauses at wait_for() invocations (e.g. during ask).
    Call its resume() method to continue, and pause() to enable pausing again.
    """
    def __init__(self, adapter, name="Threadtest instr", event_timeout=1):
        super().__init__(adapter, name)
        self._event = threading.Event()
        self._event_timeout = event_timeout
        self._wait_timed_out = False

    def wait_for(self, query_delay=0):
        """During ask, wait using a threading.Event has been set."""
        self._wait_timed_out = not self._event.wait(timeout=self._event_timeout)

    def pause(self):
        self._event.clear()

    def resume(self):
        self._event.set()

    ctrl = Instrument.control("G?", "S %g", "Control a thing.")


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
    with expected_protocol(
        ThreadedAccessTester,
        [("G?", "42")],
    ) as inst:
        # inst.ctrl == 42
        print('starting')
        q1 = queue.Queue()
        t1 = threading.Thread(target=lambda q: q.put(inst.ctrl), args=[q1])
        t1.start()
        inst.resume()
        t1.join(timeout=2)
        assert q1.get() == 42
        assert not inst._wait_timed_out
