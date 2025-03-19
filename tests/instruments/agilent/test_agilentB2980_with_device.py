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
# test is for B2987A/B model


import pytest
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2987
from time import sleep
# from pyvisa.errors import VisaIOError

@pytest.fixture(scope="module")
def agilentB2987(connected_device_address):
    instr = AgilentB2987(connected_device_address)
    return instr
    
def test_id(agilentB2987):
    vendor, model, serial_number, firmware_version = agilentB2987.id.split(",")
    # assert vendor == "Keysight Technologies"
    assert model[:5] == "B2987" # omit letter at the end of model
    
def test_battery(agilentB2987):
    battery_level = agilentB2987.battery_level
    assert 0 <= battery_level <= 100

    battery_cycles = agilentB2987.battery_cycles
    assert battery_cycles >= 0

    battery_selftest = agilentB2987.battery_selftest
    assert battery_selftest in [0, 1]

# def test_current_dc(agilentB2987):
    # current_dc = agilentB2987.current_dc
    # assert current_dc == 0

def test_output_states(agilentB2987):
    output_state = agilentB2987.output_state
    assert output_state in [0, 1]

    on_states = [1, '1', 'ON']
    off_states = [0, '0', 'OFF']
    
    for state in on_states:
        agilentB2987.output_state = state
        output_state = agilentB2987.output_state
        assert output_state == 1

    sleep(1)

    for state in off_states:
        agilentB2987.output_state = state
        output_state = agilentB2987.output_state
        assert output_state == 0

