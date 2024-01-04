#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import time
import pytest

from pymeasure.instruments.aimtti.aimttiPL import PL303QMDP


@pytest.fixture(scope="module")
def psu(connected_device_address):
    instr = PL303QMDP(connected_device_address)
    instr.reset()
    return instr


def test_voltage(psu):
    psu.ch_2.voltage_setpoint = 1.2
    psu.ch_2.current_limit = 1.0
    psu.ch_2.current_range = "HIGH"
    psu.ch_2.output_enabled = True

    time.sleep(1)

    print(psu.ch_2.voltage)

    time.sleep(5)

    psu.ch_2.output_enabled = False


def test_voltage_all(psu):
    psu.ch_2.voltage_setpoint = 1.2
    psu.ch_2.current_limit = 1.0

    psu.ch_1.voltage_setpoint = 24.0
    psu.ch_1.current_limit = 1.2

    psu.all_outputs_enabled = True

    time.sleep(5)

    psu.all_outputs_enabled = False
    psu.local()
