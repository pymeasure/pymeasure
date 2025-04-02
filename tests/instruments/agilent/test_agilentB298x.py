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
from pymeasure.instruments.agilent.agilentB298x import AgilentB2987


class TestagilentB298x:
    """Tests of the ammeter functions"""

    @pytest.mark.parametrize("state", [0, 1])
    def test_input_enabled(self, state):
        """Verify the communication of the input_enabled getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":INP {state}", None),
             (":INP?", state)]
        ) as inst:
            inst.input_enabled = state
            assert state == inst.input_enabled

    @pytest.mark.parametrize("state", [0, 1])
    def test_zero_corrected(self, state):
        """Verify the communication of the zero correct function getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":INP:ZCOR {state}", None),
             (":INP:ZCOR?", state)]
        ) as inst:
            inst.zero_corrected = state
            assert state == inst.zero_corrected

    def test_measure(self):
        """Verify the communication of the measure getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS?", 1.24E-13),
             (":MEAS?", "1E-3,4895")]
        ) as inst:
            assert inst.measure == 1.24E-13
            assert inst.measure == [1E-3, 4895]

    def test_current(self):
        """Verify the communication of the current getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:CURR?", 2.24E-14)]
        ) as inst:
            assert inst.current == 2.24E-14

    @pytest.mark.parametrize("state", ['MIN', 20E-6])
    def test_current_range(self, state):
        """Verify the communication of the current_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":CURR:RANG {state}", None),
             (":CURR:RANG?", state)]
        ) as inst:
            inst.current_range = state
            assert state == inst.current_range

    @pytest.mark.parametrize("state", ['CURR', 'CHAR', 'VOLT', 'RES'])
    def test_function(self, state):
        """Verify the communication of the function getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":FUNC '{state}'", None),
             (":FUNC?", state)]
        ) as inst:
            inst.function = state
            assert state == inst.function

    def test_charge(self):
        """Verify the communication of the charge getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:CHAR?", 5E-9)]
        ) as inst:
            assert inst.charge == 5E-9

    @pytest.mark.parametrize("state", ['MIN', 2E-6])
    def test_charge_range(self, state):
        """Verify the communication of the charge_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":CHAR:RANG {state}", None),
             (":CHAR:RANG?", state)]
        ) as inst:
            inst.charge_range = state
            assert state == inst.charge_range

    def test_resistance(self):
        """Verify the communication of the resistance getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:RES?", 5E9)]
        ) as inst:
            assert inst.resistance == 5E9

    @pytest.mark.parametrize("state", ['MIN', 1E12])
    def test_resistance_range(self, state):
        """Verify the communication of the resistance_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":RES:RANG {state}", None),
             (":RES:RANG?", state)]
        ) as inst:
            inst.resistance_range = state
            assert state == inst.resistance_range

    def test_voltage(self):
        """Verify the communication of the voltage getter."""
        with expected_protocol(
            AgilentB2987,
            [(":MEAS:VOLT?", 11.34)]
        ) as inst:
            assert inst.voltage == 11.34

    @pytest.mark.parametrize("state", ['DEF', 20])
    def test_voltage_range(self, state):
        """Verify the communication of the voltage_range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":VOLT:RANG {state}", None),
             (":VOLT:RANG?", state)]
        ) as inst:
            inst.voltage_range = state
            assert state == inst.voltage_range


<<<<<<< Updated upstream
class TestagilentB298xSource:
=======
class TestAgilentB298xOutput:
>>>>>>> Stashed changes
    """Tests of the source functions"""

    @pytest.mark.parametrize("state", [0, 1])
    def test_enabled(self, state):
        """Verify the communication of the enabled getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP {state}", None),
             (":OUTP?", state)]
        ) as inst:
            inst.output.enabled = state
            assert state == inst.output.enabled

    @pytest.mark.parametrize("state", ['FLO', 'COMM'])
    def test_low_state(self, state):
        """Verify the communication of the low_state getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP:LOW {state}", None),
             (":OUTP:LOW?", state)]
        ) as inst:
            inst.output.low_state = state
            assert state == inst.output.low_state

    @pytest.mark.parametrize("state", ['ZERO', 'HIZ', 'NORM'])
    def test_off_state(self, state):
        """Verify the communication of the off_state getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":OUTP:OFF:MODE {state}", None),
             (":OUTP:OFF:MODE?", state)]
        ) as inst:
            inst.output.off_state = state
            assert state == inst.output.off_state

    def test_voltage(self):
        """Verify the communication of the voltage getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SOUR:VOLT?", 18)]
        ) as inst:
            assert inst.output.voltage == 18

    @pytest.mark.parametrize("state", ['MIN', 1000])
    def test_range(self, state):
        """Verify the communication of the range getter/setter."""
        with expected_protocol(
            AgilentB2987,
            [(f":SOUR:VOLT:RANG {state}", None),
             (":SOUR:VOLT:RANG?", state)]
        ) as inst:
            inst.output.range = state
            assert inst.output.range in ['MIN', 1000]


class TestagilentB298xTrigger:
    """Tests of the trigger functions"""

    SUB_SYSTEM = [':TRIG', ':ARM']

    # def test_init(self):
        # """Verify the communication of the trigger init method."""
        # with expected_protocol(
            # AgilentB2987,
            # [(":INIT")]
        # ) as inst:
            # assert inst.trigger.init() == 38

    @pytest.mark.parametrize("state", ['OFF', 'ONCE'])
    def test_once_bypassed(self, state):
        """Verify the communication of the trigger init method."""
        with expected_protocol(
            AgilentB2987,
            [(f":TRIG:BYP {state}", None),
             (":TRIG:BYP?", state)]
        ) as inst:
            assert type(inst.trigger.once_bypassed) is bool
        
        
        
    # def test_arm_count(self):

    # def test_arm_delay(self):

    # def test_arm_source(self):

    # def test_arm_timer(self):

    # def test_arm_output_signal(self):

    # def test_arm_output_enabled(self):


    # def test_test_is_idle(self):

    
    # def test_bypass(self):

    # def test_count(self):

    # def test_delay(self):

    # def test_source(self):

    # def test_timer(self):

    # def test_output_signal(self):

    # def test_output_enabled(self):


class TestagilentB298xBattery:
    """Tests of the battery functions"""

    def test_battery_level(self):
        """Verify the communication of the battery level getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT?", 38)]
        ) as inst:
            assert inst.battery.level == 38

    def test_battery_cycles(self):
        """Verify the communication of the battery cycles getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT:CYCL?", 42)]
        ) as inst:
            assert inst.battery.cycles == 42

    @pytest.mark.parametrize("state", [0, 1])
    def test_battery_selftest_passed(self, state):
        """Verify the communication of the battery selftest_passed getter."""
        with expected_protocol(
            AgilentB2987,
            [(":SYST:BATT:TEST?", state)]
        ) as inst:
            assert inst.battery.selftest_passed is not state
