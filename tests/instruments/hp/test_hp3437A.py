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

import numpy as np
import pytest

from pymeasure.adapters import FakeAdapter
from pymeasure.instruments.hp import HP3437A


class RecordingFakeAdapter(FakeAdapter):
    """Fake adapter that serves one reply and records every timeout assignment."""

    def __init__(self, timeout, reply=""):
        super().__init__()
        self._timeout = timeout
        self._buffer = reply
        self.timeout_writes = []

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self.timeout_writes.append(value)
        self._timeout = value


@pytest.fixture
def make_instrument(monkeypatch):
    """Return a HP3437A factory with a stubbed status (ASCII mode, known readings)."""

    def factory(timeout, number_readings=1000, delay=0.01):
        adapter = RecordingFakeAdapter(timeout=timeout, reply="1.0,2.0\r\n")
        instrument = HP3437A(adapter)
        monkeypatch.setattr(HP3437A, "talk_ascii", property(lambda self: True))
        monkeypatch.setattr(HP3437A, "number_readings", property(lambda self: number_readings))
        monkeypatch.setattr(HP3437A, "delay", property(lambda self: delay))
        return instrument

    return factory


def test_read_data_restores_timeout(make_instrument):
    """A long sweep raises the timeout for the read and restores it afterwards."""
    instrument = make_instrument(timeout=100)

    data = instrument.read_data()

    np.testing.assert_array_equal(data, [1.0, 2.0])
    assert instrument.adapter.timeout_writes == [pytest.approx(30000), 100]
    assert instrument.adapter.timeout == 100


def test_read_data_keeps_larger_timeout(make_instrument):
    """A timeout already large enough is left untouched apart from the restore."""
    instrument = make_instrument(timeout=1e6)

    instrument.read_data()

    assert instrument.adapter.timeout == 1e6
    assert instrument.adapter.timeout_writes == [1e6]


def test_read_data_keeps_none_timeout(make_instrument):
    """A ``None`` timeout (no timeout) is restored unchanged."""
    instrument = make_instrument(timeout=None)

    instrument.read_data()

    assert instrument.adapter.timeout is None
    assert instrument.adapter.timeout_writes == [None]


def test_read_data_keeps_infinite_timeout(make_instrument):
    """An infinite timeout is not replaced by a finite sweep timeout."""
    instrument = make_instrument(timeout=float("inf"))

    instrument.read_data()

    assert instrument.adapter.timeout == float("inf")
    assert instrument.adapter.timeout_writes == [float("inf")]
