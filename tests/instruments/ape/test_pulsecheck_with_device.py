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

"""Tests requiring a pulseCheck connected over RS232, e.g.::

    pytest tests/instruments/ape/test_pulsecheck_with_device.py \
        --device-address ASRL/dev/ttyUSB0::INSTR

The settings the tests change are read at the start and written back afterwards. The turning
angle is moved by a few steps only and returned to where it started. No pulse train is
required; the autocorrelation is checked for its shape, not its content.
"""

import time

import numpy as np
import pytest

from pymeasure.instruments.ape import PulseCheck
from pymeasure.instruments.ape.pulsecheck import TRIGGER_MODES

#: Settings the tests below write, and which are restored when they are done.
#: `filter` comes last, since leaving `trigger_mode` forces it to 'low' (see
#: `test_trigger_mode_resets_filter`).
RESTORED_SETTINGS = ("sensitivity", "gain", "scan_range", "averages", "math_enabled",
                     "measurement_running", "trigger_mode", "filter")


@pytest.fixture(scope="module")
def instrument(connected_device_address):
    inst = PulseCheck(connected_device_address)
    time.sleep(0.3)
    settings = {name: getattr(inst, name) for name in RESTORED_SETTINGS}
    yield inst
    for name, value in settings.items():
        assert set_and_read(inst, name, value) == value, f"could not restore {name}"


def set_and_read(instrument, name, value, timeout=10):
    """Write a property and read it back, repeating until the setting arrives.

    The instrument discards a setting if the next command follows too closely, and
    occasionally even then, so the value is written repeatedly rather than only polled.

    :param instrument: the instrument to write to.
    :param name: name of the property.
    :param value: value to write.
    :param timeout: how long to keep trying, in s.
    :returns: the value read back.
    """
    deadline = time.monotonic() + timeout
    while True:
        setattr(instrument, name, value)
        time.sleep(0.3)
        read = getattr(instrument, name)
        if read == value or time.monotonic() > deadline:
            return read


def test_resolution(instrument):
    assert instrument.resolution in (4, 8, 16, 32, 64, 128, 256)


def test_alpha(instrument):
    assert isinstance(instrument.alpha, int)


def test_tau_register(instrument):
    assert isinstance(instrument.tau_register, int)


def test_settings(instrument):
    assert set(instrument.settings) == {"sensitivity", "gain", "scan_range", "filter",
                                        "averages", "resolution", "alpha", "math_enabled",
                                        "trigger_mode"}


@pytest.mark.parametrize("value", [1, 3, 10, 30, 100, 300])
def test_sensitivity(instrument, value):
    assert set_and_read(instrument, "sensitivity", value) == value


@pytest.mark.parametrize("value", [0, 100, 500, 999])
def test_gain(instrument, value):
    assert set_and_read(instrument, "gain", value) == value


@pytest.mark.parametrize("value", ["low", "medium", "high"])
def test_filter(instrument, value):
    assert set_and_read(instrument, "filter", value) == value


@pytest.mark.parametrize("value", [1, 2, 4, 8, 16])
def test_averages(instrument, value):
    assert set_and_read(instrument, "averages", value) == value


@pytest.mark.parametrize("value", [1.5e-12, 5e-12, 15e-12, 50e-12, 150e-12])
def test_scan_range(instrument, value):
    assert set_and_read(instrument, "scan_range", value) == value


@pytest.mark.parametrize("value", [False, True])
def test_math_enabled(instrument, value):
    assert set_and_read(instrument, "math_enabled", value) == value


@pytest.mark.parametrize("value", [False, True])
def test_measurement_running(instrument, value):
    assert set_and_read(instrument, "measurement_running", value) == value


@pytest.mark.parametrize("value", list(TRIGGER_MODES))
def test_trigger_mode(instrument, value):
    assert set_and_read(instrument, "trigger_mode", value) == value


def test_trigger_mode_resets_filter(instrument):
    """The 'trigger' mode forces the filter to 'low', and it stays there on the way back."""
    assert set_and_read(instrument, "trigger_mode", "freerun") == "freerun"
    assert set_and_read(instrument, "filter", "high") == "high"

    assert set_and_read(instrument, "trigger_mode", "trigger") == "trigger"
    assert instrument.filter == "low"
    assert set_and_read(instrument, "trigger_mode", "freerun") == "freerun"
    assert instrument.filter == "low"


@pytest.mark.parametrize("mode", ["fringe", "slow"])
def test_other_trigger_modes_keep_filter(instrument, mode):
    assert set_and_read(instrument, "trigger_mode", "freerun") == "freerun"
    assert set_and_read(instrument, "filter", "high") == "high"

    assert set_and_read(instrument, "trigger_mode", mode) == mode
    assert instrument.filter == "high"


def test_raw_acf(instrument):
    acf = instrument.raw_acf()
    assert len(acf) == instrument.resolution
    # the raw 16 bit samples are shifted down by 6 bits
    assert all(0 <= value < 2 ** 10 for value in acf)


def test_raw_acf_repeated(instrument):
    """Consecutive traces must stay in sync, since the reply carries no framing."""
    resolution = instrument.resolution
    for _ in range(5):
        assert len(instrument.raw_acf()) == resolution


def test_raw_acf_after_other_commands(instrument):
    """Reading settings in between must not shift the trace's bytes."""
    _ = instrument.settings
    assert len(instrument.raw_acf()) == instrument.resolution


@pytest.mark.parametrize("scan_range", [5e-12, 50e-12, 150e-12])
def test_acf(instrument, scan_range):
    assert set_and_read(instrument, "scan_range", scan_range) == scan_range
    delay, acf = instrument.acf
    assert len(delay) == len(acf) == instrument.resolution
    assert np.isclose(delay[-1] - delay[0], scan_range, rtol=1e-6, atol=0)
    assert np.isclose(delay[0], -delay[-1], rtol=1e-6, atol=0)


def test_tune(instrument):
    start = instrument.alpha
    try:
        instrument.tune(20)
        time.sleep(2)
        assert instrument.alpha == start + 20
    finally:
        instrument.set_alpha(start)
    assert instrument.alpha == start


def test_set_alpha(instrument):
    start = instrument.alpha
    try:
        instrument.set_alpha(start + 15)
        assert instrument.alpha == start + 15
    finally:
        instrument.set_alpha(start)
    assert instrument.alpha == start
