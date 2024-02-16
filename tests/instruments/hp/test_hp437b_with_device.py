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

import pytest
from time import sleep
from pymeasure.instruments.hp import HP437B
from pymeasure.instruments.hp.hp437b import MeasurementUnit, OperatingMode, TriggerMode, \
    GroupTriggerMode
import numpy as np


class TestHP437B:
    """
    Unit tests for HP437B class.

    This test suite, needs the following setup to work properly:
        - A HP437B device should be connected to a gpib capable adapter;
        - The device's address must be set in the RESOURCE constant.
        - Some power sensor connected to the power reference reading around 0 dBm (+/- 1 dBm)
    """

    BOOLEANS = [True, False]

    FILTER_VALUES = reversed([1, 2, 4, 8, 16, 32, 64, 128, 256, 512])

    GROUP_TRIGGER_MODES = [e for e in GroupTriggerMode]

    @pytest.fixture
    def makeHp437b(self, connected_device_address):
        return HP437B(connected_device_address)

    @pytest.fixture
    def make_resetted_instr(self, makeHp437b):
        makeHp437b.reset()
        makeHp437b.clear_status_registers()
        return makeHp437b

    def test_range(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.range = 5
        assert instr.range == 5
        assert instr.automatic_range_enabled is False

    def test_operating_mode(self, make_resetted_instr):
        instr = make_resetted_instr
        assert instr.operating_mode == OperatingMode.NORMAL

    def test_trigger_mode(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.trigger_mode = TriggerMode.HOLD
        assert instr.trigger_mode == TriggerMode.HOLD

        instr.trigger_mode = TriggerMode.FREE_RUNNING
        assert instr.trigger_mode == TriggerMode.FREE_RUNNING

    @pytest.mark.parametrize('boolean', BOOLEANS)
    def test_automatic_range_enabled(self, make_resetted_instr, boolean):
        instr = make_resetted_instr
        instr.automatic_range_enabled = boolean
        assert instr.automatic_range_enabled == boolean

    @pytest.mark.parametrize('gtmode', GROUP_TRIGGER_MODES)
    def test_group_trigger_mode(self, make_resetted_instr, gtmode):
        instr = make_resetted_instr
        instr.group_trigger_mode = gtmode
        assert instr.group_trigger_mode == gtmode

    @pytest.mark.parametrize('boolean', BOOLEANS)
    def test_duty_cycle_enabled(self, make_resetted_instr, boolean):
        instr = make_resetted_instr
        instr.duty_cycle_enabled = boolean
        assert instr.duty_cycle_enabled == boolean

    @pytest.mark.parametrize('boolean', BOOLEANS)
    def test_filter_automatic_enabled(self, make_resetted_instr, boolean):
        instr = make_resetted_instr
        instr.filter_automatic_enabled = boolean
        sleep(2)
        assert instr.filter_automatic_enabled == boolean

    @pytest.mark.parametrize('filter', FILTER_VALUES)
    def test_filter(self, make_resetted_instr, filter):
        instr = make_resetted_instr
        instr.filter = filter
        assert instr.filter == filter

    @pytest.mark.parametrize('boolean', BOOLEANS)
    def test_limits_enabled(self, make_resetted_instr, boolean):
        instr = make_resetted_instr
        instr.limits_enabled = boolean
        assert instr.limits_enabled == boolean

    def test_limit_high_hit(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.power_reference_enabled = True
        sleep(2)
        assert (-1 <= instr.power <= 1)
        instr.limit_low = -10
        instr.limit_high = -1
        instr.limits_enabled = True
        sleep(1)
        assert instr.limit_high_hit is True
        instr.limits_enabled = False

    def test_limit_low_hit(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.power_reference_enabled = True
        sleep(2)
        assert (-1 <= instr.power <= 1)
        instr.limit_high = 10
        instr.limit_low = 1
        instr.limits_enabled = True
        sleep(1)
        assert instr.limit_low_hit is True
        instr.limits_enabled = False

    def test_limit_high(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.limit_high = 299.999
        assert instr.limit_high == 299.999

    @pytest.mark.parametrize('boolean', BOOLEANS)
    def test_offset_enabled(self, make_resetted_instr, boolean):
        instr = make_resetted_instr
        instr.offset_enabled = boolean
        assert instr.offset_enabled == boolean

    def test_offset(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.offset_enabled = True
        instr.offset = 20.22
        assert instr.offset == 20.22

    @pytest.mark.parametrize('boolean', BOOLEANS)
    def test_relative_mode_enabled(self, make_resetted_instr, boolean):
        instr = make_resetted_instr
        instr.relative_mode_enabled = boolean
        assert instr.relative_mode_enabled == boolean

    def test_measurement_units_and_linear_display_enabled(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.relative_mode_enabled = True
        instr.linear_display_enabled = True
        assert instr.measurement_unit == MeasurementUnit.PERCENT

        instr.linear_display_enabled = False
        assert instr.measurement_unit == MeasurementUnit.DB

        instr.relative_mode_enabled = False
        instr.linear_display_enabled = True
        assert instr.measurement_unit == MeasurementUnit.WATTS
        assert instr.linear_display_enabled is True

        instr.linear_display_enabled = False
        assert instr.measurement_unit == MeasurementUnit.DBM
        assert instr.linear_display_enabled is False

    @pytest.mark.parametrize('resolution', [1, 0.1, 0.01])
    def test_resolution_linear(self, make_resetted_instr, resolution):
        instr = make_resetted_instr

        instr.linear_display_enabled = True
        instr.resolution = resolution
        assert instr.resolution == resolution

    @pytest.mark.parametrize('resolution', [0.1, 0.01, 0.001])
    def test_resolution_logarithmic(self, make_resetted_instr, resolution):
        instr = make_resetted_instr

        instr.linear_display_enabled = False
        instr.resolution = resolution
        assert instr.resolution == resolution

    def test_frequency(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.frequency = 50e6
        assert instr.frequency == 50e6

    def test_duty_cycle(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.duty_cycle = 0.500
        assert instr.duty_cycle == 0.500

    def test_calibration_factor(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.calibration_factor = 50.00
        assert instr.calibration_factor == 50.00

    def test_sensor_data_read_cal_factor_table(self, make_resetted_instr):
        instr = make_resetted_instr
        frequencies = np.arange(1e9, 81e9, 1e9)
        cal_factors = [100.0 for _ in range(0, 80)]
        instr.sensor_data_write_cal_factor_table(9, frequencies, cal_factors)
        freq_data, cal_fac_data = instr.sensor_data_read_cal_factor_table(9)

        assert freq_data.sort() == frequencies.sort()
        assert cal_fac_data.sort() == cal_fac_data.sort()
