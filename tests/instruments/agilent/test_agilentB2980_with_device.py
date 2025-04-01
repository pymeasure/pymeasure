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

# disconnect all cables from the unit before starting the test
#
# Tested using SCPI over USB. call signature:
# $ pytest test_agilentB2980_with_device.py --device-address USB0::0x2A8D::0x9B01::MY61390198::INSTR
#
# Test was performed with B2987B
#

import pytest
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2987  # B2987 supports all features
# from pyvisa.errors import VisaIOError

SUPPORTED_MODEL = 'B2987'


@pytest.fixture(scope="module")
def agilentB2980(connected_device_address):
    instr = AgilentB2987(connected_device_address)
    return instr


class TestResetandID:
    def test_reset(self, agilentB2980):
        agilentB2980.clear()
        agilentB2980.reset()
        assert len(agilentB2980.check_errors()) == 0

    def test_device_id(self, agilentB2980):
        vendor, device_id, serial_number, firmware_version = agilentB2980.id.split(',')
        assert SUPPORTED_MODEL in device_id


class TestagilentB2980:
    """Test of the ammeter functions."""

    def test_input_enabled(self, agilentB2980):
        input_enabled = agilentB2980.input_enabled
        assert type(input_enabled) is bool

    def test_zero_corrected(self, agilentB2980):
        zero_corrected = agilentB2980.zero_corrected
        assert type(zero_corrected) is bool

    def test_current(self, agilentB2980):
        current = agilentB2980.current
        assert type(current) is float

    @pytest.mark.parametrize("range", ['MIN', 'MAX', 'DEF', 'UP', 'DOWN', 2E-3, 1, 0])
    def test_current_range(self, agilentB2980, range):
        agilentB2980.current_range = range
        current_range = agilentB2980.current_range
        assert 2E-12 <= current_range <= 20E-3


class TestagilentB2980Trigger:
    """Test of the source functions for B2985 and B2987."""
    pass


class TestagilentB2980Source:
    """Test of the source functions for B2985 and B2987."""

    def test_enabled(self, agilentB2980):
        enabled = agilentB2980.source.enabled
        assert enabled in [True, False]


class TestagilentB2980Battery:
    """Test of the battery functions of B2983 and B2987."""

    def test_level(self, agilentB2980):
        level = agilentB2980.battery.level
        assert 0 <= level <= 100

    def test_cycles(self, agilentB2980):
        cycles = agilentB2980.battery.cycles
        assert cycles >= 0

    def test_selftest_passed(self, agilentB2980):
        selftest_passed = agilentB2980.battery.selftest_passed
        assert type(selftest_passed) is bool
