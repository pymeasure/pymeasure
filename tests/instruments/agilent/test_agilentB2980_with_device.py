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

# Tested using SCPI over USB. call signature:
# $ pytest test_agilentB2980_with_device.py --device-address USB0::0x2A8D::0x9B01::MY61390198::INSTR
#
# Test are organized in classes
# The applied tests depend on the connected instrument model
# The instrument model is detected during the test start


import pytest
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2987 # B2987 supports all features

# from pyvisa.errors import VisaIOError

AMMETERS = ["B2981", "B2983", "B2985", "B2987"]
ELECTROMETERS = ["B2985", "B2987"]
HAS_BATTERY = ["B2983", "B2987"]

# TODO: get model from instrument id 
model = "B2987"

@pytest.fixture(scope="module")
def agilentB298x(connected_device_address):
    instr = AgilentB2987(connected_device_address)
    return instr


@pytest.mark.skipif((model not in AMMETERS),  reason = "Model must be " + " or ".join(AMMETERS))
class TestAgilentB298xAmmeter:
    """
    Test of the ammeter functions.
    """
    def test_id(self, agilentB298x):
        vendor, model, serial_number, firmware_version = agilentB298x.id.split(",")
        model = model[:5] # omit the letter at the end
        # assert vendor == "Keysight Technologies"
        assert  model in AMMETERS

    def test_input_states(self, agilentB298x):
        input_enabled = agilentB298x.input_enabled
        assert input_enabled in [True, False]

    def test_zero_correction(self, agilentB298x):
        zero_correction = agilentB298x.zero_correction
        assert zero_correction in [True, False]

@pytest.mark.skipif((model not in ELECTROMETERS), reason = "Model must be " + " or ".join(ELECTROMETERS))
class TestAgilentB298xElectrometer:
    """
    Test of the electrometer functions for B2985 and B2987.
    """
    def test_ouput_states(self, agilentB298x):
        output_enabled = agilentB298x.output_enabled
        assert output_enabled in [True, False]


@pytest.mark.skipif((model not in HAS_BATTERY), reason = "Model must be " + " or ".join(HAS_BATTERY))
class TestAgilentB298xBattery:
    """
    Test of the battery functions for B2983 and B2987.
    """
    def test_battery_level(self, agilentB298x):
        battery_level = agilentB298x.battery_level
        assert 0 <= battery_level <= 100

    def test_battery_cycles(self, agilentB298x):
        battery_cycles = agilentB298x.battery_cycles
        assert battery_cycles >= 0

    def test_battery_selftest(self, agilentB298x):
        battery_selftest = agilentB298x.battery_selftest
        assert battery_selftest in [0, 1]


