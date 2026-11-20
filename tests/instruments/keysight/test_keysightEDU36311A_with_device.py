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
#
# UNPLUG EVERYTHING FROM THE EDU36311A OUTPUTS BEFORE STARTING THIS TEST
#
# Test using USB port:
# $ pytest -k EDU36311A --device-address "USB0::0x2A8D::0x8F01::<serial>::INSTR"

import pytest

from pymeasure.instruments.keysight.keysightEDU36311A import KeysightEDU36311A, OperatingMode

CHANNELS = [1, 2, 3]
MAX_VOLTAGE = {1: 6.18, 2: 30.9, 3: 30.9}
MIN_CURRENT = {1: 0.002, 2: 0.001, 3: 0.001}
MAX_CURRENT = {1: 5.15, 2: 1.03, 3: 1.03}
SAVE_LOCATION = 9  # overwritten unless it holds a saved state


@pytest.fixture(scope="module")
def edu36311a(connected_device_address):
    instr = KeysightEDU36311A(connected_device_address)
    instr.clear()
    yield instr
    instr.reset()
    instr.adapter.close()


@pytest.fixture
def psu(edu36311a):
    edu36311a.reset()
    assert edu36311a.complete == "1"
    yield edu36311a
    assert edu36311a.check_errors() == []


def test_id(psu):
    assert "EDU36311A" in psu.id


@pytest.mark.parametrize("ch", CHANNELS)
def test_voltage_setpoint(psu, ch):
    assert psu.channels[ch].voltage_setpoint == 0
    psu.channels[ch].voltage_setpoint = MAX_VOLTAGE[ch]
    assert psu.channels[ch].voltage_setpoint == pytest.approx(MAX_VOLTAGE[ch])


@pytest.mark.parametrize("ch", CHANNELS)
def test_current_limit(psu, ch):
    psu.channels[ch].current_limit = MIN_CURRENT[ch]
    assert psu.channels[ch].current_limit == pytest.approx(MIN_CURRENT[ch])
    psu.channels[ch].current_limit = MAX_CURRENT[ch]
    assert psu.channels[ch].current_limit == pytest.approx(MAX_CURRENT[ch])


@pytest.mark.parametrize("ch", CHANNELS)
def test_measurements_output_off(psu, ch):
    assert psu.channels[ch].output_enabled is False
    assert psu.channels[ch].voltage == pytest.approx(0, abs=0.05)
    assert psu.channels[ch].current == pytest.approx(0, abs=0.01)
    assert psu.channels[ch].operating_mode == OperatingMode.OFF


def test_output_enabled(psu):
    psu.ch_2.voltage_setpoint = 0
    psu.ch_2.current_limit = MIN_CURRENT[2]
    psu.ch_2.output_enabled = True
    try:
        assert psu.ch_2.output_enabled is True
    finally:
        psu.ch_2.output_enabled = False
    assert psu.ch_2.output_enabled is False


@pytest.mark.parametrize("ch", CHANNELS)
def test_output_delays(psu, ch):
    psu.channels[ch].output_on_delay = 0.5
    psu.channels[ch].output_off_delay = 0.25
    assert psu.channels[ch].output_on_delay == pytest.approx(0.5)
    assert psu.channels[ch].output_off_delay == pytest.approx(0.25)


@pytest.mark.parametrize("ch, low, high", [(1, 0.5, 6.6), (2, 1.5, 33), (3, 1.5, 33)])
def test_over_voltage_protection(psu, ch, low, high):
    assert psu.channels[ch].over_voltage_protection_level == pytest.approx(high)
    psu.channels[ch].over_voltage_protection_level = low
    assert psu.channels[ch].over_voltage_protection_level == pytest.approx(low)
    assert psu.channels[ch].over_voltage_protection_tripped is False
    psu.channels[ch].clear_over_voltage_protection()


@pytest.mark.parametrize("ch", CHANNELS)
def test_over_current_protection(psu, ch):
    assert psu.channels[ch].over_current_protection_enabled is False
    psu.channels[ch].over_current_protection_enabled = True
    assert psu.channels[ch].over_current_protection_enabled is True
    assert psu.channels[ch].over_current_protection_delay == pytest.approx(0.05)
    psu.channels[ch].over_current_protection_delay = 0.2
    assert psu.channels[ch].over_current_protection_delay == pytest.approx(0.2)
    assert psu.channels[ch].over_current_protection_delay_start == "SCH"
    psu.channels[ch].over_current_protection_delay_start = "CCTR"
    assert psu.channels[ch].over_current_protection_delay_start == "CCTR"
    assert psu.channels[ch].over_current_protection_tripped is False
    psu.channels[ch].clear_over_current_protection()
    psu.channels[ch].clear_protection()


@pytest.mark.parametrize("ch", CHANNELS)
def test_trigger_settings(psu, ch):
    psu.channels[ch].triggered_voltage = 2
    psu.channels[ch].triggered_current = 0.5
    assert psu.channels[ch].triggered_voltage == pytest.approx(2)
    assert psu.channels[ch].triggered_current == pytest.approx(0.5)
    assert psu.channels[ch].voltage_mode == "FIX"
    assert psu.channels[ch].current_mode == "FIX"
    psu.channels[ch].voltage_mode = "STEP"
    psu.channels[ch].current_mode = "STEP"
    assert psu.channels[ch].voltage_mode == "STEP"
    assert psu.channels[ch].current_mode == "STEP"
    assert psu.channels[ch].trigger_source == "BUS"
    psu.channels[ch].trigger_source = "IMM"
    assert psu.channels[ch].trigger_source == "IMM"
    psu.channels[ch].trigger_delay = 0.1
    assert psu.channels[ch].trigger_delay == pytest.approx(0.1)
    assert psu.channels[ch].trigger_continuous_enabled is False


def test_bus_trigger(psu):
    psu.ch_1.triggered_voltage = 1.5
    psu.ch_1.voltage_mode = "STEP"
    psu.ch_1.trigger_source = "BUS"
    psu.ch_1.initiate()
    psu.trigger()
    assert psu.complete == "1"
    assert psu.ch_1.voltage_setpoint == pytest.approx(1.5)


def test_abort(psu):
    psu.ch_1.triggered_voltage = 1.5
    psu.ch_1.voltage_mode = "STEP"
    psu.ch_1.trigger_source = "BUS"
    psu.ch_1.trigger_delay = 10
    psu.ch_1.initiate()
    psu.trigger()
    psu.ch_1.abort()
    assert psu.ch_1.voltage_setpoint == 0


def test_tracking_enabled(psu):
    psu.ch_2.voltage_setpoint = 12
    assert psu.tracking_enabled is False
    psu.tracking_enabled = True
    assert psu.tracking_enabled is True
    assert psu.ch_3.voltage_setpoint == pytest.approx(12)
    psu.tracking_enabled = False


def test_display(psu):
    assert psu.display_enabled is True
    assert psu.display_view == "METER3"
    psu.display_view = "METER1"
    assert psu.complete == "1"
    assert psu.display_view == "METER1"
    psu.display_enabled = False
    assert psu.display_enabled is False


def test_beeper_enabled(psu):
    original = psu.beeper_enabled
    try:
        psu.beeper_enabled = not original
        assert psu.beeper_enabled is (not original)
    finally:
        psu.beeper_enabled = original


def _read_state_block(psu):
    return psu.binary_values("SYST:SET?", dtype="u1").tobytes()


def test_save_recall_state(psu):
    if psu.ask("OUTP:PON:STAT?").strip() == f"RCL{SAVE_LOCATION}":
        pytest.skip(f"Location {SAVE_LOCATION} is the power-on state.")
    reset_state = _read_state_block(psu)
    psu.recall_state(SAVE_LOCATION)
    assert psu.complete == "1"
    slot_in_use = _read_state_block(psu) != reset_state
    psu.reset()
    if slot_in_use:
        pytest.skip(f"Location {SAVE_LOCATION} holds a saved state, which would be overwritten.")

    try:
        psu.ch_1.voltage_setpoint = 0
        psu.ch_1.output_enabled = True
        psu.ch_2.voltage_setpoint = 12.5
        psu.ch_2.current_limit = 0.25
        psu.ch_3.over_voltage_protection_level = 20
        psu.ch_3.output_on_delay = 1.5
        psu.tracking_enabled = False
        psu.save_state(SAVE_LOCATION)
        assert psu.complete == "1"

        psu.reset()
        assert psu.ch_1.output_enabled is False
        assert psu.ch_2.voltage_setpoint == 0

        psu.recall_state(SAVE_LOCATION)
        assert psu.complete == "1"
        assert psu.ch_1.output_enabled is True
        assert psu.ch_1.voltage_setpoint == 0
        assert psu.ch_2.voltage_setpoint == pytest.approx(12.5)
        assert psu.ch_2.current_limit == pytest.approx(0.25)
        assert psu.ch_3.over_voltage_protection_level == pytest.approx(20)
        assert psu.ch_3.output_on_delay == pytest.approx(1.5)
    finally:
        psu.reset()
        psu.save_state(SAVE_LOCATION)
