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

import pytest
from pymeasure.instruments.rigol import DHOBase


@pytest.fixture(scope="module")
def scope(connected_device_address):
    """Connect to a real DHO-series scope; skip if --device-address is not given."""
    instr = DHOBase(connected_device_address)
    return instr


# ======================================================================= #
#  Live hardware tests                                                    #
# ======================================================================= #


def test_idn_contains_dho(scope):
    assert "DHO" in scope.id


@pytest.mark.parametrize("ch_n", [1, 2, 3, 4])
def test_channel_display_roundtrip(scope, ch_n):
    ch = getattr(scope, f"ch_{ch_n}")
    original = ch.display_enabled
    ch.display_enabled = not original
    assert ch.display_enabled is not original
    ch.display_enabled = original


@pytest.mark.parametrize("coupling", ["AC", "DC", "GND"])
def test_channel_coupling_roundtrip(scope, coupling):
    original = scope.ch_1.coupling
    scope.ch_1.coupling = coupling
    assert scope.ch_1.coupling == coupling
    scope.ch_1.coupling = original


def test_channel_scale_roundtrip(scope):
    original = scope.ch_1.scale
    scope.ch_1.scale = 1.0
    assert scope.ch_1.scale == pytest.approx(1.0, rel=1e-3)
    scope.ch_1.scale = original


def test_channel_offset_roundtrip(scope):
    original = scope.ch_1.offset
    scope.ch_1.offset = 0.0
    assert scope.ch_1.offset == pytest.approx(0.0, abs=1e-3)
    scope.ch_1.offset = original


def test_timebase_scale_roundtrip(scope):
    original = scope.timebase_scale
    scope.timebase_scale = 1e-3
    assert scope.timebase_scale == pytest.approx(1e-3, rel=1e-3)
    scope.timebase_scale = original


def test_trigger_source_roundtrip(scope):
    original = scope.trigger_source
    scope.trigger_source = "CHAN1"
    assert scope.trigger_source == "CHAN1"
    scope.trigger_source = original


def test_trigger_level_roundtrip(scope):
    original = scope.trigger_level
    scope.trigger_level = 0.0
    assert scope.trigger_level == pytest.approx(0.0, abs=0.01)
    scope.trigger_level = original


def test_trigger_status_is_valid(scope):
    assert scope.trigger_status in ("TD", "WAIT", "RUN", "AUTO", "STOP")


def test_run_stop_single(scope):
    scope.run()
    scope.stop()
    scope.single()
    scope.run()


def test_sample_rate_positive(scope):
    assert scope.sample_rate > 0


def test_measure_vpp_returns_float(scope):
    result = scope.measure("VPP", 1)
    assert isinstance(result, float)


def test_get_waveform_shape(scope):
    scope.stop()
    t, v = scope.get_waveform(channel=1, mode="NORM", fmt="BYTE")
    assert len(t) > 0
    assert len(t) == len(v)
    scope.run()


def test_get_waveform_time_monotonic(scope):
    scope.stop()
    t, _ = scope.get_waveform(channel=1)
    assert all(t[i] < t[i + 1] for i in range(len(t) - 1))
    scope.run()
