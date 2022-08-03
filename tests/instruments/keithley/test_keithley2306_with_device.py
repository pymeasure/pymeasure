#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
import math
from pymeasure.instruments.keithley.keithley2306 import Keithley2306

pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestKeithley2306:
    """
    Unit tests for Keithley2306 class.

    This test suite, needs the following setup to work properly:
        - A Keithley2306 device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
    """

    ##################################################
    # Keithley2306 device address goes here:
    RESOURCE = "USB0::10893::6039::CN57266430::INSTR"
    ##################################################

    #########################
    # PARAMETRIZATION CASES #
    #########################

    CHANNELS = [1, 2]
    RELAYS = [1, 2, 3, 4]
    BOOLEANS = [False, True]
    BRIGHTNESSES = [0, 0.12, 0.25, 0.3, 0.5, 0.6, 0.75, 0.8, 1]
    DISPLAY_TEXT_DATAS = ['', 'Hello', '0123456789012345678901234578901']
    BANDWIDTHS = ['high', 'low']
    IMPEDANCES = [0, 0.01, 0.1, 0.2, 0.25, 0.5, 0.77, 0.99, 1]
    SENSE_MODES = ['voltage', 'current', 'dvm']
    NPLCS = [0.01, 0.1, 1, 2, 4, 10]
    AVERAGE_COUNTS = [1, 2, 5, 10]
    CURRENT_RANGES = [0.005, 5]
    PULSE_CURRENT_AVERAGE_COUNTS = [1, 2, 5, 100, 500, 1000, 5000]
    PULSE_CURRENT_MODES = ['high', 'low', 'average']
    PULSE_CURRENT_TIMES = [33.33333e-06, 1.2E-3, 0.8333]
    PULSE_CURRENT_STEP_COUNTS = [0, 1, 5, 19]
    PULSE_CURRENT_STEP_TIMES = [33.33333e-06, 1.2E-3, 100e-3]
    PULSE_CURRENT_STEP_TIMEOUTS = [2e-3, 20.1e-3, 200e-3]
    PULSE_CURRENT_STEP_TIMEOUT_INITIALS = [10e-3, 210.3e-3, 60]
    PULSE_CURRENT_STEP_DELAYS = [0, 10e-3, 57.32e-3, 100e-3]
    PULSE_CURRENT_STEP_RANGES = [100e-3, 1, 5]
    PULSE_CURRENT_STEP_INDICES = [1, 2, 5, 20]
    PULSE_CURRENT_STEP_TRIGGER_LEVELS = [0, 50e-3, 100e-3, 500e-3, 1, 2.5, 5]
    PULSE_CURRENT_TRIGGER_DELAYS = [0, 0.05, 0.1, 1, 2, 5]
    PULSE_CURRENT_TRIGGER_LEVELS = [0, 50e-3, 100e-3, 500e-3, 1, 2.5, 5]
    PULSE_CURRENT_TRIGGER_LEVEL_RANGES = [100e-3, 1, 5]
    PULSE_CURRENT_TIMEOUTS = [0.005, 1, 32]
    LONG_INTEGRATION_TRIGGER_EDGES = ['rising', 'falling', 'neither']
    LONG_INTEGRATION_TIMES = [0.850, 1, 30, 60]
    LONG_INTEGRATION_TRIGGER_LEVELS = [0, 50e-3, 100e-3, 500e-3, 1, 2.5, 5]
    LONG_INTEGRATION_TIMEOUTS = [1, 30, 63]
    LONG_INTEGRATION_TRIGGER_LEVEL_RANGES = [100e-3, 1, 5]
    SOURCE_VOLTAGES = [0, 3.3, 15]
    SOURCE_VOLTAGE_PROTECTIONS = [0, 4, 8]
    SOURCE_CURRENTS = [0.006, 1, 5]
    SOURCE_CURRENT_LIMIT_TYPES = ['limit', 'trip']

    INSTR = Keithley2306(RESOURCE)

    ############
    # FIXTURES #
    ############

    def reset_display(self):
        self.INSTR.display_enabled = True
        self.INSTR.display_text_enabled = False
        self.INSTR.display_text_data = ''
        self.INSTR.display_brightness = 1.0

    def reset_relays(self):
        for i in range(1, 5):
            self.INSTR.relay(i).closed = False

    @pytest.fixture
    def instr(self):
        self.INSTR.reset()
        return self.INSTR

    #########
    # TESTS #
    #########

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_display_enabled(self, instr, case):
        try:
            assert instr.display_enabled
            instr.display_enabled = case
            assert instr.display_enabled == case
        finally:
            self.reset_display()

    @pytest.mark.parametrize("case", BRIGHTNESSES)
    def test_display_brightness(self, instr, case):
        try:
            assert instr.display_brightness == 1.0
            instr.display_brightness = case
            assert instr.display_brightness == math.ceil(4 * case) / 4
        finally:
            self.reset_display()

    @pytest.mark.parametrize("case", CHANNELS)
    def test_display_channel(self, instr, case):
        assert instr.display_channel == 1
        instr.display_channel = case
        assert instr.display_channel == case

    @pytest.mark.parametrize("display_text_data", DISPLAY_TEXT_DATAS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_display_text(self, instr, display_text_data, case):
        try:
            assert instr.display_text_data == ''
            assert not instr.display_text_enabled
            instr.display_text_data = display_text_data
            instr.display_text_enabled = case
            assert instr.display_text_data == display_text_data
            assert instr.display_text_enabled == case
        finally:
            self.reset_display()

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_output_enabled(self, instr, channel, case):
        assert not instr.ch(channel).enabled
        instr.ch(channel).enabled = case
        assert instr.ch(channel).enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BANDWIDTHS)
    def test_output_bandwidth(self, instr, channel, case):
        instr = instr
        assert instr.ch(channel).bandwidth == 'low' if channel == 1 else 'high'
        instr.ch(channel).bandwidth = case
        assert instr.ch(channel).bandwidth == case

    @pytest.mark.parametrize("case", IMPEDANCES)
    def test_output_impedance(self, instr, case):
        assert instr.ch1.impedance == 0.0
        instr.ch1.impedance = case
        assert instr.ch1.impedance == case

    @pytest.mark.parametrize("relay", RELAYS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_relay_closed(self, instr, relay, case):
        try:
            assert not instr.relay(relay).closed
            instr.relay(relay).closed = case
            assert instr.relay(relay).closed == case
        finally:
            self.reset_relays()

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_both_channels_enabled(self, instr, case):
        assert not instr.ch1.enabled
        assert not instr.ch2.enabled
        instr.both_channels_enabled = case
        assert instr.ch1.enabled == case
        assert instr.ch2.enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", SENSE_MODES)
    def test_sense_mode(self, instr, channel, case):
        assert instr.ch(channel).sense_mode == 'voltage'
        instr.ch(channel).sense_function = case
        assert instr.ch(channel).sense_function == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", NPLCS)
    def test_nplc(self, instr, channel, case):
        assert instr.ch(channel).nplc == 1
        instr.ch(channel).nplc = case
        time.sleep(0.5)
        assert instr.ch(channel).nplc == case
        instr.ch(channel).nplc == 1

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", AVERAGE_COUNTS)
    def test_average_count(self, instr, channel, case):
        assert instr.ch(channel).average_count == 1
        instr.ch(channel).average_count = case
        assert instr.ch(channel).average_count == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", CURRENT_RANGES)
    def test_current_range(self, instr, channel, case):
        assert instr.ch(channel).current_range == 5
        instr.ch(channel).current_range = case
        assert instr.ch(channel).current_range == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_current_range_auto(self, instr, channel, case):
        assert not instr.ch(channel).current_range_auto
        instr.ch(channel).current_range_auto = case
        assert instr.ch(channel).current_range_auto == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("pulse_current_measure_enabled", BOOLEANS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_AVERAGE_COUNTS)
    def test_pulse_current_average_count(self, instr, channel, pulse_current_measure_enabled, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_average_count == 1
        instr.ch(channel).pulse_current_measure_enabled = pulse_current_measure_enabled
        if not pulse_current_measure_enabled or case <= 100:
            instr.ch(channel).pulse_current_average_count = case
            assert instr.ch(channel).pulse_current_average_count == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_pulse_current_measure_enabled(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_measure_enabled
        instr.ch(channel).pulse_current_measure_enabled = case
        assert instr.ch(channel).pulse_current_measure_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_MODES)
    def test_pulse_current_mode(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_mode == 'high'
        instr.ch(channel).pulse_current_mode = case
        assert instr.ch(channel).pulse_current_mode == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TIMES)
    def test_pulse_current_time_high(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_time_high == 33.33333e-06
        instr.ch(channel).pulse_current_time_high = case
        assert instr.ch(channel).pulse_current_time_high == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TIMES)
    def test_pulse_current_time_low(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_time_low == 33.33333e-06
        instr.ch(channel).pulse_current_time_low = case
        assert instr.ch(channel).pulse_current_time_low == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TIMES)
    def test_pulse_current_time_average(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_time_average == 33.33333e-06
        instr.ch(channel).pulse_current_time_average = case
        assert instr.ch(channel).pulse_current_time_average == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TIMES)
    def test_pulse_current_time_digitize(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_time_digitize == 33.33333e-06
        instr.ch(channel).pulse_current_time_digitize = case
        assert instr.ch(channel).pulse_current_time_digitize == case

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_pulse_current_step_enabled(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert not instr.ch1.pulse_current_step_enabled
        instr.ch1.pulse_current_step_enabled = case
        assert instr.ch1.pulse_current_step_enabled == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_COUNTS)
    def test_pulse_current_step_up_count(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_up_count == 1
        instr.ch1.pulse_current_step_up_count = case
        assert instr.ch1.pulse_current_step_up_count == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_COUNTS)
    def test_pulse_current_step_down_count(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_down_count == 1
        instr.ch1.pulse_current_step_down_count = case
        assert instr.ch1.pulse_current_step_down_count == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_TIMES)
    def test_pulse_current_step_time(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_time == 200e-6
        instr.ch1.pulse_current_step_time = case
        assert instr.ch1.pulse_current_step_time == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_TIMEOUTS)
    def test_pulse_current_step_timeout(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_timeout == 2e-3
        instr.ch1.pulse_current_step_timeout = case
        assert instr.ch1.pulse_current_step_timeout == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_TIMEOUT_INITIALS)
    def test_pulse_current_step_timeout_initial(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_timeout_initial == 2
        instr.ch1.pulse_current_step_timeout_initial = case
        assert instr.ch1.pulse_current_step_timeout_initial == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_DELAYS)
    def test_pulse_current_step_delay(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_delay == 0
        instr.ch1.pulse_current_step_delay = case
        assert instr.ch1.pulse_current_step_delay == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_RANGES)
    def test_pulse_current_step_range(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step_range == 5
        instr.ch1.pulse_current_step_range = case
        assert instr.ch1.pulse_current_step_range == case

    @pytest.mark.parametrize("range", PULSE_CURRENT_STEP_RANGES)
    @pytest.mark.parametrize("step", PULSE_CURRENT_STEP_INDICES)
    @pytest.mark.parametrize("case", PULSE_CURRENT_STEP_TRIGGER_LEVELS)
    def test_pulse_current_step_trigger_level(self, instr, range, step, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_step(step).trigger_level == 0.0
        if case <= range:
            instr.ch1.pulse_current_step(step).trigger_level = case
            assert instr.ch1.pulse_current_step(step).trigger_level == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("pulse_current_measure_enabled", BOOLEANS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TRIGGER_DELAYS)
    def test_pulse_current_trigger_delay(self, instr, channel, pulse_current_measure_enabled, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_trigger_delay == 0
        instr.ch(channel).pulse_current_measure_enabled = pulse_current_measure_enabled
        if not pulse_current_measure_enabled or case <= 0.1:
            instr.ch(channel).pulse_current_trigger_delay = case
            assert instr.ch(channel).pulse_current_trigger_delay == case

    @pytest.mark.parametrize("case", PULSE_CURRENT_TRIGGER_LEVEL_RANGES)
    def test_pulse_current_trigger_level_range(self, instr, case):
        instr.ch1.pulse_current_fast_enabled = True
        assert instr.ch1.pulse_current_trigger_level_range == 5
        instr.ch1.pulse_current_trigger_level_range = case
        assert instr.ch1.pulse_current_trigger_level_range == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TRIGGER_LEVELS)
    def test_pulse_current_trigger_level(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_trigger_level == 0
        instr.ch(channel).pulse_current_trigger_level = case
        assert instr.ch(channel).pulse_current_trigger_level == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_pulse_current_fast_enabled(self, instr, channel, case):
        assert not instr.ch(channel).pulse_current_fast_enabled
        instr.ch(channel).pulse_current_fast_enabled = case
        assert instr.ch(channel).pulse_current_fast_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_pulse_current_search_enabled(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_search_enabled
        instr.ch(channel).pulse_current_search_enabled = case
        assert instr.ch(channel).pulse_current_search_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_pulse_current_detect_enabled(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert not instr.ch(channel).pulse_current_detect_enabled
        instr.ch(channel).pulse_current_detect_enabled = case
        assert instr.ch(channel).pulse_current_detect_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", PULSE_CURRENT_TIMEOUTS)
    def test_pulse_current_timeouts(self, instr, channel, case):
        instr.ch(channel).pulse_current_fast_enabled = True
        assert instr.ch(channel).pulse_current_timeout == 1
        instr.ch(channel).pulse_current_timeout = case
        assert instr.ch(channel).pulse_current_timeout == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", LONG_INTEGRATION_TRIGGER_EDGES)
    def test_long_integration_trigger_edge(self, instr, channel, case):
        instr.ch(channel).long_integration_fast_enabled = True
        assert instr.ch(channel).long_integration_trigger_edge == 'rising'
        instr.ch(channel).long_integration_trigger_edge = case
        assert instr.ch(channel).long_integration_trigger_edge == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", LONG_INTEGRATION_TIMES)
    def test_long_integration_time(self, instr, channel, case):
        instr.ch(channel).long_integration_fast_enabled = True
        assert instr.ch(channel).long_integration_time == 1.0
        instr.ch(channel).long_integration_time = case
        assert instr.ch(channel).long_integration_time == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", LONG_INTEGRATION_TRIGGER_LEVELS)
    def test_long_integration_trigger_level(self, instr, channel, case):
        instr.ch(channel).long_integration_fast_enabled = True
        instr.ch(channel).long_integration_timeout = 1
        assert instr.ch(channel).long_integration_trigger_level == 0
        instr.ch(channel).long_integration_trigger_level = case
        assert instr.ch(channel).long_integration_trigger_level == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", LONG_INTEGRATION_TIMEOUTS)
    def test_long_integration_timeout(self, instr, channel, case):
        instr.ch(channel).long_integration_fast_enabled = True
        assert instr.ch(channel).long_integration_timeout == 16
        instr.ch(channel).long_integration_timeout = case
        assert instr.ch(channel).long_integration_timeout == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_long_integration_fast_enabled(self, instr, channel, case):
        assert not instr.ch(channel).long_integration_fast_enabled
        instr.ch(channel).long_integration_fast_enabled = case
        assert instr.ch(channel).long_integration_fast_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_long_integration_search_enabled(self, instr, channel, case):
        instr.ch(channel).long_integration_fast_enabled = True
        assert instr.ch(channel).long_integration_search_enabled
        instr.ch(channel).long_integration_search_enabled = case
        assert instr.ch(channel).long_integration_search_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_long_integration_detect_enabled(self, instr, channel, case):
        instr.ch(channel).long_integration_fast_enabled = True
        assert not instr.ch(channel).long_integration_detect_enabled
        instr.ch(channel).long_integration_detect_enabled = case
        assert instr.ch(channel).long_integration_detect_enabled == case

    @pytest.mark.parametrize("case", LONG_INTEGRATION_TRIGGER_LEVEL_RANGES)
    def test_long_integration_trigger_level_range(self, instr, case):
        instr.ch1.long_integration_fast_enabled = True
        instr.ch1.long_integration_timeout = 1
        assert instr.ch1.long_integration_trigger_level_range == 5
        instr.ch1.long_integration_trigger_level_range = case
        assert instr.ch1.long_integration_trigger_level_range == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", SOURCE_VOLTAGES)
    def test_source_voltage(self, instr, channel, case):
        assert instr.ch(channel).source_voltage == 0
        instr.ch(channel).source_voltage = case
        assert instr.ch(channel).source_voltage == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", SOURCE_VOLTAGE_PROTECTIONS)
    def test_source_voltage_protection(self, instr, channel, case):
        assert instr.ch(channel).source_voltage_protection == 8
        instr.ch(channel).source_voltage_protection = case
        assert instr.ch(channel).source_voltage_protection == case

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_source_voltage_protection_enabled(self, instr, channel):
        assert not instr.ch(channel).source_voltage_protection_enabled
        assert isinstance(instr.ch(channel).source_voltage_protection_enabled, bool)

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_source_voltage_protection_clamp_enabled(self, instr, channel, case):
        assert not instr.ch(channel).source_voltage_protection_clamp_enabled
        instr.ch(channel).source_voltage_protection_clamp_enabled = case
        assert instr.ch(channel).source_voltage_protection_clamp_enabled == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", SOURCE_CURRENTS)
    def test_source_current_limit(self, instr, channel, case):
        assert instr.ch(channel).source_current_limit == 0.25
        instr.ch(channel).source_current_limit = case
        assert instr.ch(channel).source_current_limit == case

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("case", SOURCE_CURRENT_LIMIT_TYPES)
    def test_source_current_limit_type(self, instr, channel, case):
        assert instr.ch(channel).source_current_limit_type == 'limit'
        instr.ch(channel).source_current_limit_type = case
        assert instr.ch(channel).source_current_limit_type == case

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_source_current_limit_enabled(self, instr, channel):
        assert not instr.ch(channel).source_current_limit_enabled
        assert isinstance(instr.ch(channel).source_current_limit_enabled, bool)

    @pytest.mark.parametrize("sense_mode", SENSE_MODES)
    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_reading(self, instr, sense_mode, average_count, channel):
        instr.ch(channel).sense_mode = sense_mode
        instr.ch(channel).average_count = average_count
        time.sleep(0.1)
        assert type(instr.ch(channel).reading) == float

    @pytest.mark.parametrize("sense_mode", SENSE_MODES)
    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_readings(self, instr, sense_mode, average_count, channel):
        instr.ch(channel).sense_mode = sense_mode
        instr.ch(channel).average_count = average_count
        time.sleep(0.2)
        readings = instr.ch(channel).readings
        assert type(readings) == list
        assert len(readings) == average_count
        assert type(readings[0]) == float

    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_measured_voltage(self, instr, average_count, channel):
        instr.ch(channel).average_count = average_count
        time.sleep(0.1)
        assert type(instr.ch(channel).measured_voltage) == float
        assert instr.ch(channel).sense_mode == 'voltage'

    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_measured_voltages(self, instr, average_count, channel):
        instr.ch(channel).average_count = average_count
        time.sleep(0.2)
        measured_voltages = instr.ch(channel).measured_voltages
        assert type(measured_voltages) == list
        assert len(measured_voltages) == average_count
        assert type(measured_voltages[0]) == float
        assert instr.ch(channel).sense_mode == 'voltage'

    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_measured_current(self, instr, average_count, channel):
        instr.ch(channel).average_count = average_count
        time.sleep(0.1)
        assert type(instr.ch(channel).measured_current) == float
        assert instr.ch(channel).sense_mode == 'current'

    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_measured_currents(self, instr, average_count, channel):
        instr.ch(channel).average_count = average_count
        time.sleep(0.2)
        measured_currents = instr.ch(channel).measured_currents
        assert type(measured_currents) == list
        assert len(measured_currents) == average_count
        assert type(measured_currents[0]) == float
        assert instr.ch(channel).sense_mode == 'current'

    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_dvm_voltage(self, instr, average_count, channel):
        instr.ch(channel).average_count = average_count
        time.sleep(0.1)
        assert type(instr.ch(channel).dvm_voltage) == float
        assert instr.ch(channel).sense_mode == 'dvm'

    @pytest.mark.parametrize("average_count", AVERAGE_COUNTS)
    @pytest.mark.parametrize("channel", CHANNELS)
    def test_dvm_voltages(self, instr, average_count, channel):
        instr.ch(channel).average_count = average_count
        time.sleep(0.2)
        dvm_voltages = instr.ch(channel).dvm_voltages
        assert type(dvm_voltages) == list
        assert len(dvm_voltages) == average_count
        assert type(dvm_voltages[0]) == float
        assert instr.ch(channel).sense_mode == 'dvm'
