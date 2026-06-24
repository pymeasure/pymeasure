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

# Tested using SCPI over telnet (via ethernet). call signature:
# $ pytest test_agilentE4980A_with_device.py --device-address "TCPIP0::172.23.19.101::INSTR"
#
# tested with a Keysight E4980A LCR Meter


import pytest
from pymeasure.instruments.agilent.agilentE4980 import AgilentE4980


@pytest.fixture(scope="module")
def agilentE4980(connected_device_address):
    instr = AgilentE4980(connected_device_address)
    return instr


@pytest.mark.parametrize("freq", [40, 1E6])
def test_frequency(agilentE4980, freq):
    """Test Agilent E4980 frequency getter/setter."""
    agilentE4980.frequency = freq
    assert freq == agilentE4980.frequency
