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

import pytest
import time

from pymeasure.instruments.aimtti import LD400P


@pytest.fixture(scope="module")
def instrument(connected_device_address):
    instr = LD400P(connected_device_address)
    instr.reset()
    return instr


def test_load(instrument):
    """
    Connect the load to a power supply that delivers at least 1V and can supply 200mA
    Then run tests.
    """
    assert 0.9 <= instrument.voltage

    instrument.mode = "C"
    instrument.level_a = 0.2
    instrument.level_b = 0.1
    instrument.level_select = "A"

    time.sleep(0.1)

    assert instrument.mode == "C"
    assert instrument.level_select == "A"

    instrument.input = "On"
    time.sleep(2)
    assert pytest.approx(instrument.current, 0.01) == 0.2

    instrument.level_select = "B"
    time.sleep(2)
    assert pytest.approx(instrument.current, 0.01) == 0.1
