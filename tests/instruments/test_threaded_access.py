"""Test thread-safe access to instrument connections.

If you want to confirm that the tests still properly test thread issues, replace CommonBase._rlock
temporarily with a contextlib.nullcontext() -- all tests in this module must fail!

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

import pytest

from pymeasure.instruments import Instrument
from pymeasure.instruments.fakes import FakeInstrument
from pymeasure.test import expected_protocol

# TODO: also guard CommonBase.binary_values and binary methods in general
# TODO: Need more thread-safety in manipulating ThreadedAccessTester?
# TODO: Maybe smoother to fake comms with pyvisa-sim?


class ThreadedAccessTester(FakeInstrument):
    """Pause-able instrument class for testing threaded access."""

    def __init__(self, adapter, name="Threadtest instr", event_timeout=1):
        super().__init__(adapter, name)
        self._event_timeout = event_timeout
        self._wait_timed_out = threading.Event()

    def wait_for(self, query_delay: threading.Event):
        """Wait until the passed event has been set.

        Uses the fact that we can pass a delay to ask(), that is passed to
        wait_for, to have per-thread events when invoking ask()
        """
        if isinstance(query_delay, int):
            super().wait_for(query_delay)
            return
        timed_out = not query_delay.wait(timeout=self._event_timeout)
        # Latching way to store timed-out event(s)
        if timed_out:
            self._wait_timed_out.set()


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

    assert not inst._wait_timed_out.is_set()
    assert q1.get() == "M1"
    assert q2.get() == "M2"


def test_thieving_read():
    """Avoid that another thread can interrupt an occurring ask() and steal its reply with a read().

    mermaid diagram:
    sequenceDiagram
        Note over Thread1: ask(CMD1)
        activate Thread1
        Thread1->>connection: write CMD1
        Note over Thread2: manual sequencing
        opt not strictly needed
            Thread2->>connection: write CMD2
        end
        connection-->>Thread2: read REPLY1
        connection-->>Thread1: read REPLY2
        deactivate Thread1

    Note: This also covers the "stolen checked-get errorstate" scenario
    """
    inst = ThreadedAccessTester("")

    q1 = queue.Queue()
    t1Event = threading.Event()
    t1 = threading.Thread(target=lambda q, e: q.put(inst.ask("M1", e)), args=(q1, t1Event))
    t1.start()

    def t2_func(q):
        inst.write("M2")
        q.put(inst.read())

    q2 = queue.Queue()
    t2 = threading.Thread(target=t2_func, args=(q2,))
    t2.start()

    # Thread 2 can steal the read buffer meant for thread 1
    time.sleep(0.1)
    t1Event.set()  # Now wake up thread 1 to fetch its reply
    t2.join(timeout=2)
    t1.join(timeout=2)

    assert not inst._wait_timed_out.is_set()
    assert q1.get() == "M1"
    assert q2.get() == "M2"


@pytest.fixture
def sequencingtester():
    # we need to define the event before the class because we need to pass this to control()
    post_ask_event = threading.Event()
    pre_check_errors_event = threading.Event()

    class ThreadedSequencingTester(ThreadedAccessTester):
        _errcheck_result = []
        _errcheck_lock = threading.Lock()
        _set_errstate_when_entering_check_errors = False
        errcheck_has_happened_once = threading.Event()
        prop1 = FakeInstrument.control(
            "", "%s", """""",
            check_get_errors=True,
            values_kwargs={'post_ask_event': post_ask_event},
        )
        prop2 = FakeInstrument.control(
            "", "%s", """""",
            check_get_errors=True,
        )

        def ask(self, command, query_delay=0, post_ask_event=None):
            """Ask variant that can wait after the ask has completed.
            """
            ret = super().ask(command, query_delay=query_delay)
            if post_ask_event:
                # If we stop because of an event, we first need to put an
                # errorstate marker in the buffer to indicate that this command
                # put the instrument into an error state
                self.write('errstate_from_interrupted_ask')
                timed_out = not post_ask_event.wait(timeout=self._event_timeout)
                # Latching way to store timed-out event(s)
                if timed_out:
                    self._wait_timed_out.set()
            return ret

        def check_errors(self):
            # Mimic main feature of vanilla check_errors: the values call
            # This consumes the errorstate marker we set above; don't send a command
            # as that would remain in the buffer.
            if self._set_errstate_when_entering_check_errors and not self.errcheck_has_happened_once.is_set():
                self.adapter._buffer += 'errstate\n'
                self.errcheck_has_happened_once.set()

            timed_out = not pre_check_errors_event.wait(timeout=self._event_timeout)
            if timed_out:
                self._wait_timed_out.set()
            with self._errcheck_lock:
                self._errcheck_result.append(*self.values(''))

    inst = ThreadedSequencingTester("")
    return inst, post_ask_event, pre_check_errors_event


def test_property_get_errcheck_is_not_intercepted(sequencingtester):
    """Avoid that another thread can interrupt sequencing when getting in our properties.
    We want to make sure that a property command and its check_errors() call stay together.

    mermaid diagram:
    sequenceDiagram
        Note over Thread1: get prop1
        activate Thread1
        Note over Thread1: calls values()->ask()
        activate Thread1
        Thread1->>connection: write GET_P1
        connection-->>Thread1: read REPLY_P1
        Note over connection: this creates error state
        Note over Thread2: get prop2
        activate Thread2
        Note over Thread2: calls values()->ask()
        activate Thread2
        Thread2->>connection: write GET_P2
        connection-->>Thread2: read REPLY_P2
        deactivate Thread2
        Note over Thread2: check errors for P2
        Thread2->>connection: write ERRCHECK
        connection-->>Thread2: read ERRSTATE_P1
        Note over Thread2: Gets P1's error!
        deactivate Thread2
        Note over Thread1: check errors
        Thread1->>connection: write ERRCHECK
        connection-->>Thread1: read ???
        deactivate Thread1

    """

    inst, post_ask_event, pre_check_errors_event = sequencingtester
    pre_check_errors_event.set()  # we don't need this for this test
    inst.write('M1')  # reply for the first property read

    def t1_func(q):
        q.put(inst.prop1)

    q1 = queue.Queue()
    t1 = threading.Thread(target=t1_func, args=(q1,))
    t1.start()

    def t2_func(q):
        inst.write("M2")
        q.put(inst.prop2)

    q2 = queue.Queue()
    # Thread 2 runs without stopping at an event
    t2 = threading.Thread(target=t2_func, args=(q2,))
    t2.start()

    time.sleep(0.1)
    post_ask_event.set()  # Now wake up thread 1 to proceed and run check_errors
    t2.join(timeout=2)
    t1.join(timeout=2)

    assert not inst._wait_timed_out.is_set()
    assert q1.get() == "M1"
    assert q2.get() == "M2"
    # The errchecks must be: first element from the prop1 access, the second empty from prop2
    assert inst._errcheck_result == ['errstate_from_interrupted_ask', '']


@pytest.fixture
def sequencingtester2():
    # we need to define the event before the class because we need to pass this to control()
    post_ask_event = threading.Event()
    pre_check_errors_event = threading.Event()

    class ThreadedSequencingTester(Instrument):
        _wait_timed_out = threading.Event()
        _event_timeout = 1

        def ask(self, command, query_delay=0, post_ask_event=None):
            """Ask variant that can wait after the ask has completed.
            """
            ret = super().ask(command, query_delay=query_delay)
            if post_ask_event:
                timed_out = not post_ask_event.wait(timeout=self._event_timeout)
                # Latching way to store timed-out event(s)
                if timed_out:
                    self._wait_timed_out.set()
            return ret

        def check_errors(self):
            timed_out = not pre_check_errors_event.wait(timeout=self._event_timeout)
            if timed_out:
                self._wait_timed_out.set()
            super().check_errors()

        checked_prop1 = Instrument.control(
            "CP1?", "CP1 %s", """""",
            check_set_errors=True,
            # values_kwargs={'post_ask_event': post_ask_event},
        )
        prop2 = Instrument.control(
            "P2?", "P2 %s", """""",
        )

    return ThreadedSequencingTester, post_ask_event, pre_check_errors_event


def test_property_set_errcheck_is_not_intercepted(sequencingtester2):
    """Avoid that another thread can interrupt sequencing when setting in our properties.

    Equivalent to test_property_get_errcheck_is_not_intercepted(), just for setting.
    """

    inst, post_ask_event, pre_check_errors_event = sequencingtester2
    post_ask_event.set()  # we don't need this for this test

    with expected_protocol(
        inst,
        [
            ('CP1 42', None),
            ('SYST:ERR?', '1,5'),
            ('SYST:ERR?', '0'),
            ('P2?', 'M2'),
        ],
        name='Test12',
    ) as inst:

        def t1_func():
            inst.checked_prop1 = '42'

        t1 = threading.Thread(target=t1_func)
        t1.start()

        def t2_func(q):
            q.put(inst.prop2)

        q2 = queue.Queue()
        # Thread 2 runs without stopping at an event
        t2 = threading.Thread(target=t2_func, args=(q2,))
        t2.start()

        time.sleep(0.1)
        pre_check_errors_event.set()  # Now wake up thread 1 to proceed with check_errors
        t2.join(timeout=2)
        t1.join(timeout=2)

        assert not inst._wait_timed_out.is_set(), "Timed out waiting for an event"
        # If expected_protocol raises an AssertionError because the comm pairs mismatch,
        # q2 will remain empty, so this cannot block otherwise the test hangs.
        assert q2.get(block=False) == "M2"
