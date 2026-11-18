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

# Tests to run on a real controller. They are skipped unless pytest gets an address:
#
#   pytest tests/instruments/eurotherm/test_eurothermepc3000_with_device.py \
#       --device-address ASRL3::INSTR
#
# Set EUROTHERM_ADDRESS (Modbus address, default 1) and EUROTHERM_BAUD_RATE if needed.
# Run them on an idle controller: they read parameters, change a few settings (PID,
# rate limits, units) and restore them, and never start a program or heat.
#
# Verified on 2026-11-05 with an EPC3000 over Modbus TCP. test_ramp_units was changed to a
# read check afterwards, as that register is read-only on this model.

import pytest
from eurotherm_device_utils import (
    assert_changes_and_restores,
    assert_plausible_output,
    assert_plausible_temperature,
    connection_kwargs,
)

from pymeasure.instruments.eurotherm import EurothermEPC3000


@pytest.fixture(scope="module")
def controller(connected_device_address):
    controller = EurothermEPC3000(connected_device_address, **connection_kwargs())
    try:
        assert_plausible_temperature(controller.process_value)
    except Exception as exc:  # noqa: BLE001
        pytest.exit(f"Cannot communicate with the controller: {exc!r}", returncode=1)
    yield controller
    controller.adapter.close()


def test_process_value(controller):
    assert_plausible_temperature(controller.process_value)


def test_working_setpoint(controller):
    assert_plausible_temperature(controller.working_setpoint)


def test_output_level(controller):
    assert_plausible_output(controller.output_level)


def test_target_setpoint_rewrite(controller):
    """Write back the current target setpoint, which does not change anything."""
    setpoint = controller.target_setpoint
    assert_plausible_temperature(setpoint)
    controller.target_setpoint = setpoint
    assert controller.target_setpoint == pytest.approx(setpoint)


@pytest.mark.parametrize("name", ["proportional_band", "integral_time", "derivative_time"])
def test_pid(controller, name):
    old = getattr(controller, name)
    assert_changes_and_restores(controller, name, old + 1)


def test_active_setpoint(controller):
    assert controller.active_setpoint in (1, 2)


@pytest.mark.parametrize("name", ["setpoint1", "setpoint2"])
def test_setpoint_read(controller, name):
    """Only read: these setpoints are stored in non-volatile memory."""
    assert_plausible_temperature(getattr(controller, name))


def test_setpoint_rate_limit(controller):
    old = controller.setpoint_rate_limit
    assert_changes_and_restores(controller, "setpoint_rate_limit", old + 1)


def test_setpoint_rate_limit_down(controller):
    old = controller.setpoint_rate_limit_down
    assert_changes_and_restores(controller, "setpoint_rate_limit_down", old + 1)


def test_remote_setpoint(controller):
    """Only read: the remote setpoint replaces the local one once enabled."""
    assert_plausible_temperature(controller.remote_setpoint)


def test_ramp_done(controller):
    assert controller.ramp_done in [False, True]


def test_ramp_units(controller):
    assert controller.ramp_units in ["secs", "mins", "hours"]


def test_setpoint_limits(controller):
    assert controller.setpoint_low_limit < controller.setpoint_high_limit


def test_operating_mode(controller):
    assert controller.operating_mode in ["auto", "manual"]


def test_integral_hold(controller):
    assert controller.integral_hold in [False, True]


def test_standby_enabled(controller):
    assert controller.standby_enabled in [False, True]


def test_execution_status(controller):
    assert controller.execution_status in ["working", "standby", "startup"]


def test_temperature_units(controller):
    assert controller.temperature_units in ["C", "F", "K"]


def test_input_status(controller):
    assert controller.input_status in [
        "good",
        "not configured",
        "out of range",
        "under range",
        "hardware invalid",
        "scaling",
        "out",
        "bad",
    ]


def test_leak_current(controller):
    assert isinstance(controller.leak_current, float)
