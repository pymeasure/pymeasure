#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

pytest.skip('Only works with connected hardware', allow_module_level=True)

# change the resource name to the address of your instrument
RESOURCE = "ASRL5::INSTR"


@pytest.fixture(scope="session")
def hmp4040():
    """
    Return a HMP4040 instrument.
    """
    hmp4040 = HMP4040(RESOURCE)
    hmp4040.reset()
    return hmp4040


def test_beep(hmp4040):
    """Test emission of a beep from the instrument."""
    hmp4040.beep()
    hmp4040.reset()


def test_voltage_limits(hmp4040):
    """Test minimum and maximum voltages."""
    hmp4040.voltage_to_min()
    assert hmp4040.voltage == hmp4040.min_voltage
    hmp4040.voltage_to_max()
    assert hmp4040.voltage == hmp4040.max_voltage
    hmp4040.reset()


def test_voltage_stepping(hmp4040):
    """Test stepping voltages up and down."""
    hmp4040.voltage = 0.0
    hmp4040.step_voltage_up()
    assert hmp4040.voltage == hmp4040.voltage_step
    hmp4040.step_voltage_down()
    assert hmp4040.voltage == 0.0
    hmp4040.reset()


def test_channel_state(hmp4040):
    """Test activation and deactivation of channels."""
    hmp4040.selected_channel = 1
    assert hmp4040.selected_channel == 1

    hmp4040.set_channel_state(2, True)
    # check that the selected channel is reset to 2.
    assert hmp4040.selected_channel == 1
    hmp4040.reset()


def test_sequence(hmp4040):
    """Test sequence execution."""
    # NOTE: There are actually no assertions in this test. But it is possible
    # to check the sequence execution by looking at display of the instrument.
    hmp4040.selected_channel == 1
    hmp4040.voltage = 0.0
    hmp4040.sequence = [1.0, 1.0, 1.0, 2.0, 2.0, 1.0]
    hmp4040.repetitions = 0
    hmp4040.transfer_sequence(1)
    hmp4040.output_enabled = True
    hmp4040.selected_channel_active = True
    hmp4040.start_sequence(1)
    sleep(4)
    hmp4040.stop_sequence(1)
    hmp4040.output_enabled = False
    hmp4040.clear_sequence(1)
    hmp4040.reset()
