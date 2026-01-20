#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from time import sleep

import pytest

from pymeasure.instruments.rohdeschwarz.hmp import HMP4040


@pytest.fixture(scope="module")
def hmp4040(connected_device_address):
    """Return a HMP4040 instrument."""
    hmp4040 = HMP4040(connected_device_address)
    return hmp4040


@pytest.fixture
def resetted_hmp4040(hmp4040):
    """Return a HMP4040 instrument with resetted state."""
    hmp4040.reset()
    return hmp4040


def test_beep(resetted_hmp4040):
    """Test emission of a beep from the instrument."""
    resetted_hmp4040.beep()


def test_voltage_limits(resetted_hmp4040):
    """Test minimum and maximum voltages."""
    resetted_hmp4040.voltage_to_min()
    assert resetted_hmp4040.voltage == resetted_hmp4040.min_voltage
    resetted_hmp4040.voltage_to_max()
    assert resetted_hmp4040.voltage == resetted_hmp4040.max_voltage


def test_voltage_stepping(resetted_hmp4040):
    """Test stepping voltages up and down."""
    resetted_hmp4040.voltage = 0.0
    resetted_hmp4040.step_voltage_up()
    assert resetted_hmp4040.voltage == resetted_hmp4040.voltage_step
    resetted_hmp4040.step_voltage_down()
    assert resetted_hmp4040.voltage == 0.0


def test_channel_state(resetted_hmp4040):
    """Test activation and deactivation of channels."""
    resetted_hmp4040.selected_channel = 1
    assert resetted_hmp4040.selected_channel == 1

    resetted_hmp4040.set_channel_state(2, True)
    # check that the selected channel is reset to 2.
    assert resetted_hmp4040.selected_channel == 1


def test_sequence(resetted_hmp4040):
    """Test sequence execution."""
    # NOTE: There are actually no assertions in this test. But it is possible to check the sequence
    # execution by looking at display of the instrument.
    resetted_hmp4040.selected_channel == 1
    resetted_hmp4040.voltage = 0.0
    resetted_hmp4040.sequence = [1.0, 1.0, 1.0, 2.0, 2.0, 1.0]
    resetted_hmp4040.repetitions = 0
    resetted_hmp4040.transfer_sequence(1)
    resetted_hmp4040.output_enabled = True
    resetted_hmp4040.selected_channel_active = True
    resetted_hmp4040.start_sequence(1)
    sleep(4)
    resetted_hmp4040.stop_sequence(1)
    resetted_hmp4040.output_enabled = False
    resetted_hmp4040.clear_sequence(1)
