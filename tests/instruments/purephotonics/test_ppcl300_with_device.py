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

"""Tests with a connected PPCL300.

Run with ``pytest tests/instruments/purephotonics/test_ppcl300_with_device.py
--device-address ASRL/dev/ttyUSB0::INSTR``.
Tests which enable the optical output run only if the environment variable
``PPCL300_EMISSION=1`` is set.
"""

import os

import pytest

from pymeasure.instruments.purephotonics import PPCL300, ITLAError, ITLAExecutionError

emission = pytest.mark.skipif(
    os.environ.get("PPCL300_EMISSION") != "1",
    reason="Set PPCL300_EMISSION=1 to allow enabling the optical output.",
)


@pytest.fixture(scope="module")
def laser(connected_device_address):
    laser = PPCL300(connected_device_address)
    laser.wait_until_ready()
    yield laser
    laser.emission_enabled = False
    laser.adapter.close()


@pytest.fixture
def disabled_laser(laser):
    laser.emission_enabled = False
    laser.wait_until_ready()
    return laser


def test_id(laser):
    assert laser.manufacturer == "PurePh"
    assert laser.model.startswith("PPCL")
    assert laser.id.startswith("PurePh,PPCL")


def test_limits(laser):
    assert laser.power_min < laser.power_max
    assert 180e12 < laser.frequency_min < laser.frequency_max < 200e12
    assert laser.fine_tune_range > 0


def test_monitors(laser):
    assert len(laser.temperatures) == 2
    assert -10 < laser.case_temperature < 80
    assert len(laser.currents) == 2


def test_power_setpoint(disabled_laser):
    old = disabled_laser.power_setpoint
    try:
        disabled_laser.power_setpoint = disabled_laser.power_min
        assert disabled_laser.power_setpoint == disabled_laser.power_min
    finally:
        disabled_laser.power_setpoint = old


def test_power_setpoint_out_of_range(disabled_laser):
    old = disabled_laser.power_setpoint
    try:
        with pytest.raises(ValueError):
            disabled_laser.power_setpoint = disabled_laser.power_max + 5
        assert disabled_laser.power_setpoint == old
    finally:
        disabled_laser.power_setpoint = old


def test_read_only_register(disabled_laser):
    with pytest.raises(ITLAExecutionError) as exc:
        disabled_laser.write_register(0x42, 0)
    assert exc.value.error == ITLAError.RNW


def test_resynchronization(laser):
    channel = laser.channel
    laser.write_bytes(b"\x00\x00")  # break the framing
    assert laser.channel == channel


@emission
def test_emission_and_fine_tuning(disabled_laser):
    laser = disabled_laser
    laser.emission_enabled = True
    laser.wait_until_ready(120)
    assert laser.emission_enabled is True
    assert laser.power > laser.power_min - 1
    frequency = laser.frequency
    try:
        laser.fine_tune_frequency = -1e9
        laser.wait_until_ready(120)
        assert laser.fine_tune_frequency == -1e9
        assert laser.frequency == pytest.approx(frequency - 1e9)
    finally:
        laser.fine_tune_frequency = 0
        laser.wait_until_ready(120)
        laser.emission_enabled = False
        laser.wait_until_ready()
