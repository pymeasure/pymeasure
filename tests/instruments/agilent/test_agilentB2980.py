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
from pymeasure.test import expected_protocol
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2981
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2983
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2985
from pymeasure.instruments.agilent.agilentB2980 import AgilentB2987


class AgilentB298xAmmeterTests:
    """
    Test of the ammeter functions
    """
    @pytest.mark.parametrize("state", [0, 1])
    def test_input_enabled(self, state):
        """Verify the communication of the input_enabled getter/setter."""
        with expected_protocol(
            AgilentB2981,
            [
                (":INP?", state),
                (f":INP {state}", None),
            ],
        ) as inst:
            assert state == inst.input_enabled
            inst.input_enabled = state

    @pytest.mark.parametrize("state", [0, 1])
    def test_zero_correction(self, state):
        """Verify the communication of the zero correct function getter/setter."""
        with expected_protocol(
            AgilentB2981,
            [
                (":INP:ZCOR?", state),
                (f":INP:ZCOR {state}", None),
            ],
        ) as inst:
            assert state == inst.zero_correction
            inst.zero_correction = state


class AgilentB298xElectrometerTests:
    """
    Test of the electrometer functions
    """
    @pytest.mark.parametrize("state", [0, 1])
    def test_output_enabled(self, state):
        """Verify the communication of the output_enabled getter/setter."""
        with expected_protocol(
            AgilentB2985,
            [
                (":OUTP?", state),
                (f":OUTP {state}", None),
            ],
        ) as inst:
            assert state == inst.output_enabled
            inst.output_enabled = state

class AgilentB298xBatteryTests:
    """
    Test of the battery
    """
    def test_battery_level(self):
        """Verify the communication of the battery level getter."""
        LEVEL = 38
        with expected_protocol(
            AgilentB2987,
            [
                (":SYST:BATT?", str(LEVEL)),
            ],
        ) as inst:
            assert inst.battery_level == pytest.approx(LEVEL)

    def test_battery_cycles(self):
        """Verify the communication of the battery cycles getter."""
        CYCLES = 93
        with expected_protocol(
            AgilentB2987,
            [
                (":SYST:BATT:CYCL?", str(CYCLES)),
            ],
        ) as inst:
            assert inst.battery_cycles == pytest.approx(CYCLES)

    def test_battery_selftest(self):
        """Verify the communication of the battery selftest getter."""
        RESULT = 0
        with expected_protocol(
            AgilentB2987,
            [
                (":SYST:BATT:TEST?", str(RESULT)),
            ],
        ) as inst:
            assert inst.battery_selftest == RESULT

##########################
# Instrument definitions #
##########################

class TestAgilentB2981(AgilentB298xAmmeterTests):
    """Test the B2981x functions"""
    pass
            
class TestAgilentB2983(AgilentB298xAmmeterTests, AgilentB298xBatteryTests):
    """Test the B2983x functions"""
    pass

class TestAgilentB2985(AgilentB298xAmmeterTests, AgilentB298xElectrometerTests):
    """Test the B2985x functions"""
    pass

class TestAgilentB2987(AgilentB298xAmmeterTests, AgilentB298xElectrometerTests, AgilentB298xBatteryTests):
    """Test the B2987x functions"""
    pass

