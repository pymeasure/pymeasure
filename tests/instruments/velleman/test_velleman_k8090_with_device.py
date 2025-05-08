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


"""
Test the instrument class for the Velleman F8090.

This tests the instrument class with the real device connected.
"""

import pytest
from time import sleep

from pymeasure.adapters import SerialAdapter
from pymeasure.instruments.velleman import VellemanK8090, VellemanK8090Switches as Switches


@pytest.fixture()
def instrument(connected_device_address):
    """Get instrument object.

    Run like ``--device-address="ASRL1::INSTR"`` to use the visa adapter, and
    like ``--device-address="COM1"`` to use the serial adapter.
    """
    if "ASRL" in connected_device_address:
        return VellemanK8090(connected_device_address, timeout=500)
    else:
        adapter = SerialAdapter(
            connected_device_address, baudrate=19200, timeout=0.5, read_termination=chr(0x0F)
        )
        return VellemanK8090(adapter)


def test_version(instrument):
    ver = instrument.version

    assert ver is not None and isinstance(ver, tuple)


def test_status(instrument):
    last_on, curr_on, time_on = instrument.status

    assert isinstance(curr_on, Switches)


def test_switch_on_off(instrument):
    """Test switch on-off together.

    This tests the physical switches and the status feedback.
    You must also hear the real relays clicking, and verify the
    LEDs 1 and 3 alone light up.
    """
    instrument.switch_off = Switches.ALL
    sleep(0.5)

    instrument.switch_on = Switches.CH1 | Switches.CH3
    sleep(0.5)

    _, curr_on_1, _ = instrument.status

    instrument.switch_off = Switches.ALL
    sleep(0.5)

    _, curr_on_2, _ = instrument.status

    assert curr_on_1 == Switches.CH1 | Switches.CH3
    assert curr_on_2 == Switches.NONE

    # Test another pointless off switch, to test a lack of confirmation
    instrument.switch_off = Switches.ALL
    sleep(0.5)
