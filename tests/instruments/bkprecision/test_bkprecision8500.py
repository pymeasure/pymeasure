#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
import serial
from pymeasure.instruments.bkprecision.bkprecision8500 import BKPrecision8500

pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestBKPrecision8500:
    """
    Unit tests for BKPrecision8500 class.

    This test suite, needs the following setup to work properly:
        - A BKPrecision8500 device should be connected to the computer;
        - Additionally a PSU should be connected to the load, set to 5 V, 1 A
        - The device's address must be set in the RESOURCE constant.
    """

    ###############################################################
    # BKPrecision8500 device goes here:
    RESOURCE = "ASRL/dev/cu.usbserial-FTBPC8BS::INSTR"
    ###############################################################

    #########################
    # PARAMETRIZATION CASES #
    #########################
    BOOLEANS = [False, True]
    MODES = ["CC", "CV", "CW", "CR"]
    VOLTAGES = [0.512, 1, 2.5, 7.123, 12, 65.7, 120]
    CURRENTS = [0, 0.0001, 0.0022, 0.12, 0.5, 7.8, 12.3, 30]
    POWERS = [0, 0.001, 0.5, 1.234, 10.7, 50, 30, 128.3, 300]
    RESISTANCES = [1.01,10.233,1000,4000]

    LOAD = BKPrecision8500(RESOURCE)

    ############
    # FIXTURES #
    ############
    @pytest.fixture
    def make_resetted_load(self):
        self.LOAD.remote_enabled = True
        self.LOAD.input_enabled = False
        self.LOAD.maximum_allowed_voltage = 120
        self.LOAD.maximum_allowed_current = 30
        self.LOAD.maximum_allowed_power = 300
        self.LOAD.mode = 'CC'
        self.LOAD.cc_mode_current = 0.0
        self.LOAD.remote_sensing_enabled = False
        return self.LOAD

    #########
    # TESTS #
    #########

    def test_load_initialization_bad(self):
        bad_resource = "ASRL/dev/cu.usbserial-FTBOGUS1::INSTR"
        with pytest.raises((serial.serialutil.SerialException)):
            LOAD = BKPrecision8500(bad_resource)

    @pytest.mark.parametrize("case", MODES)
    def test_modes(self, make_resetted_load, case):
        load = make_resetted_load
        load.mode = case
        assert load.mode == case

    def test_mode_bogus(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.mode = 'BOGUS'

    @pytest.mark.parametrize("case", VOLTAGES)
    def test_maximum_allowed_voltages(self, make_resetted_load, case):
        load = make_resetted_load
        load.maximum_allowed_voltage = case
        assert load.maximum_allowed_voltage == case

    def test_maximum_allowed_voltage_zero(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.maximum_allowed_voltage = 0

    def test_maximum_allowed_voltage_negative(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.maximum_allowed_voltage = -1

    def test_maximum_allowed_voltage_200(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.maximum_allowed_voltage = 200

    @pytest.mark.parametrize("case", VOLTAGES)
    def test_cv_mode_voltage(self, make_resetted_load, case):
        load = make_resetted_load
        load.cv_mode_voltage = case
        assert load.cv_mode_voltage == case

    def test_cv_mode_voltage_over_allowed(self, make_resetted_load):
        load = make_resetted_load
        load.maximum_allowed_voltage = 10
        with pytest.raises((Exception)):
            load.cv_mode_voltage = 20

    def test_cv_mode_voltage_negative(self, make_resetted_load):
        load = make_resetted_load
        load.maximum_allowed_voltage = 10
        with pytest.raises((Exception)):
            load.cv_mode_voltage = -1

    @pytest.mark.parametrize("case", CURRENTS)
    def test_maximum_allowed_currents(self, make_resetted_load, case):
        load = make_resetted_load
        load.maximum_allowed_current = case
        assert load.maximum_allowed_current == case

    def test_maximum_allowed_current_negative(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.maximum_allowed_current = -1

    @pytest.mark.parametrize("case", CURRENTS)
    def test_cc_mode_current(self, make_resetted_load, case):
        load = make_resetted_load
        load.cc_mode_current = case
        assert load.cc_mode_current == case

    def test_cc_mode_current_over_allowed(self, make_resetted_load):
        load = make_resetted_load
        load.maximum_allowed_current = 10
        with pytest.raises((Exception)):
            load.cc_mode_current = 20

    def test_cc_mode_current_negative(self, make_resetted_load):
        load = make_resetted_load
        load.maximum_allowed_current = 10
        with pytest.raises((Exception)):
            load.cc_mode_current = -1

    @pytest.mark.parametrize("case", POWERS)
    def test_maximum_allowed_powers(self, make_resetted_load, case):
        load = make_resetted_load
        load.maximum_allowed_power = case
        assert load.maximum_allowed_power == case

    def test_maximum_allowed_power_negative(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.maximum_allowed_power = -1

    def test_maximum_allowed_power_500(self, make_resetted_load):
        load = make_resetted_load
        with pytest.raises((Exception)):
            load.maximum_allowed_power = 500

    @pytest.mark.parametrize("case", POWERS)
    def test_cw_mode_power(self, make_resetted_load, case):
        load = make_resetted_load
        load.cw_mode_power = case
        assert load.cw_mode_power == case

    def test_cw_mode_power_over_allowed(self, make_resetted_load):
        load = make_resetted_load
        load.maximum_allowed_power = 10
        with pytest.raises((Exception)):
            load.cw_mode_power = 20

    def test_cw_mode_power_negative(self, make_resetted_load):
        load = make_resetted_load
        load.maximum_allowed_power = 10
        with pytest.raises((Exception)):
            load.cw_mode_power = -1

    @pytest.mark.parametrize("case", RESISTANCES)
    def test_cr_mode_resistance(self, make_resetted_load, case):
        load = make_resetted_load
        load.cr_mode_resistance = case
        assert load.cr_mode_resistance == case

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_remote_sensing_enabled(self, make_resetted_load, case):
        load = make_resetted_load
        load.remote_sensing_enabled = case
        assert load.remote_sensing_enabled == case

    def test_input_voltage_input_off(self, make_resetted_load):
        load = make_resetted_load
        v = load.input_voltage
        assert 4.5 < v and v < 5.5

    def test_input_current_input_off(self, make_resetted_load):
        load = make_resetted_load
        i = load.input_current
        assert i == 0

    def test_input_voltage_mode_cc(self, make_resetted_load):
        load = make_resetted_load
        load.mode = 'CC'
        load.input_enabled = True
        time.sleep(0.1)
        v = load.input_voltage
        assert 4.5 < v and v < 5.5
        load.cc_mode_current = 0.5
        time.sleep(0.1)
        i = load.input_current
        assert 0.45 < i and i < 0.55
        load.input_enabled = False

    def test_input_current_mode_cv(self, make_resetted_load):
        load = make_resetted_load
        load.mode = 'CV'
        load.cv_mode_voltage = 1
        load.input_enabled = True
        time.sleep(0.2)
        v = load.input_voltage
        assert 0.9 < v and v < 1.1
        i = load.input_current
        assert 0.9 < i and i < 1.1
        load.input_enabled = False

    def test_input_power_mode_cc(self, make_resetted_load):
        load = make_resetted_load
        load.mode = 'CC'
        load.cc_mode_current = 0.1
        load.input_enabled = True
        time.sleep(0.2)
        w = load.input_power
        assert 0.45 < w and w < 0.55
        load.input_enabled = False

    def test_input_power_mode_cw(self, make_resetted_load):
        load = make_resetted_load
        load.mode = 'CW'
        load.cw_mode_power = 0.2
        load.input_enabled = True
        time.sleep(0.2)
        w = load.input_power
        assert 0.1 < w and w < 0.3
        load.input_enabled = False
