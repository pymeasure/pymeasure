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

from contextlib import contextmanager

import numpy as np

from pymeasure.adapters import ProtocolAdapter
from pymeasure.instruments.hp import HP3437A
from pymeasure.test import expected_protocol


@contextmanager
def hp_with_timeout(monkeypatch, timeout, number_readings=1000, delay=0.01):
    """Yield a HP3437A on a ProtocolAdapter plus the timeouts seen during reads.

    ``talk_ascii``, ``number_readings``, and ``delay`` are stubbed at class level so that no
    status reads are needed and the sweep time is deterministic.
    """
    monkeypatch.setattr(HP3437A, "talk_ascii", property(lambda self: True))
    monkeypatch.setattr(HP3437A, "number_readings", property(lambda self: number_readings))
    monkeypatch.setattr(HP3437A, "delay", property(lambda self: delay))
    recorded = []
    with expected_protocol(
        HP3437A,
        [(None, "1.0,2.0\r\n")],
        connection_attributes={"timeout": timeout},
    ) as instrument:
        assert isinstance(instrument.adapter, ProtocolAdapter)
        original_read_bytes = instrument.adapter._read_bytes

        def recording_read_bytes(*args, **kwargs):
            recorded.append(instrument.adapter.timeout)
            return original_read_bytes(*args, **kwargs)

        instrument.adapter._read_bytes = recording_read_bytes
        yield instrument, recorded


def test_read_data_raises_timeout_for_read_and_restores(monkeypatch):
    """A long sweep raises the timeout during the read and restores it afterwards."""
    with hp_with_timeout(monkeypatch, timeout=100) as (instrument, recorded):
        data = instrument.read_data()

    np.testing.assert_array_equal(data, [1.0, 2.0])
    assert recorded == [30000]
    assert isinstance(recorded[0], int)
    assert instrument.adapter.timeout == 100


def test_read_data_keeps_larger_timeout(monkeypatch):
    """A timeout already large enough is in force during the read and restored afterwards."""
    with hp_with_timeout(monkeypatch, timeout=1_000_000) as (instrument, recorded):
        instrument.read_data()

    assert recorded == [1_000_000]
    assert isinstance(recorded[0], int)
    assert instrument.adapter.timeout == 1_000_000


def test_read_data_keeps_none_timeout(monkeypatch):
    """A ``None`` timeout (no timeout) is in force during the read and restored afterwards."""
    with hp_with_timeout(monkeypatch, timeout=None) as (instrument, recorded):
        instrument.read_data()

    assert recorded == [None]
    assert instrument.adapter.timeout is None


def test_read_data_caps_timeout_at_one_million(monkeypatch):
    """A very long sweep caps the temporary timeout at one million milliseconds."""
    with hp_with_timeout(monkeypatch, timeout=100, number_readings=9999, delay=0.9999999) as (
        instrument,
        recorded,
    ):
        instrument.read_data()

    assert recorded == [1_000_000]
    assert isinstance(recorded[0], int)
    assert instrument.adapter.timeout == 100
