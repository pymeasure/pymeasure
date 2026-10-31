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

# Run these tests with a connected controller, e.g.:
#   pytest tests/instruments/newport/test_smc100_with_device.py \
#       --device-address ASRL/dev/ttyUSB0::INSTR
# The stage is reset, homed and moved by a small amount: make sure it can move freely.

import pytest

from pymeasure.instruments.newport.smc100 import (
    SMC100CC,
    SMC100PP,
    SMC100CommandError,
    SMC100ControllerState,
)

DISPLACEMENT = 0.5


@pytest.fixture(scope="module")
def smc100(connected_device_address):
    probe = SMC100PP(connected_device_address)
    model = probe.firmware_version.split()[0]
    probe.adapter.close()
    cls = {"SMC_PP": SMC100PP, "SMC_CC": SMC100CC}[model]
    instr = cls(connected_device_address)
    instr.reset()
    instr.home()
    instr.wait_until_ready(timeout=instr.home_timeout * 1.1)
    yield instr
    instr.stop()
    instr.adapter.close()


def test_firmware_version(smc100):
    assert smc100.firmware_version.startswith(("SMC_PP", "SMC_CC"))


def test_ready_after_homing(smc100):
    assert smc100.state.controller_state == SMC100ControllerState.READY
    assert smc100.check_errors() == []


def test_velocity(smc100):
    velocity = smc100.velocity
    smc100.velocity = velocity / 2
    assert smc100.velocity == pytest.approx(velocity / 2)
    smc100.velocity = velocity
    assert smc100.velocity == pytest.approx(velocity)


def test_move_relative(smc100):
    start = smc100.position
    timeout = smc100.get_motion_time(DISPLACEMENT) * 2 + 1
    smc100.move_relative(DISPLACEMENT)
    smc100.wait_until_ready(timeout=timeout)
    assert smc100.position == pytest.approx(start + DISPLACEMENT, abs=1e-3)


def test_move_absolute(smc100):
    target = smc100.position - DISPLACEMENT
    timeout = smc100.get_motion_time(DISPLACEMENT) * 2 + 1
    smc100.position = target
    smc100.wait_until_ready(timeout=timeout)
    assert smc100.setpoint == pytest.approx(target, abs=1e-3)
    assert smc100.position == pytest.approx(target, abs=1e-3)


def test_command_not_allowed_raises(smc100):
    with pytest.raises(SMC100CommandError):
        smc100.home()  # not allowed in READY state
