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
import math
from pymeasure.instruments.keysight.keysightE3631A import KeysightE3631A

pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestKeysightE3631A:
    """
    Unit tests for KeysightE3631A class.

    This test suite, needs the following setup to work properly:
        - A KeysightE3631A device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
    """

    ##################################################
    # KeysightE3631A device address goes here:
    RESOURCE = "GPIB0::10::INSTR"
    ##################################################

    #########################
    # PARAMETRIZATION CASES #
    #########################

    CHANNELS = [1, 2, 3]
    BOOLEANS = [False, True]
    DISPLAY_TEXT_DATAS = ['', 'Hello', '0123456789012345678901234578901']
    CURRENT_RANGES = [0.005, 5]
    SOURCE_VOLTAGES = [0, 3.3, 15]
    SOURCE_VOLTAGE_PROTECTIONS = [0, 4, 8]
    SOURCE_CURRENTS = [0.006, 1, 5]

    INSTR = KeysightE3631A(RESOURCE)

    ############
    # FIXTURES #
    ############

    def reset_display(self):
        self.INSTR.display_enabled = True
        self.INSTR.display_text_enabled = False
        self.INSTR.display_text_data = ''

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

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_both_channels_enabled(self, instr, case):
        assert not instr.ch1.enabled
        assert not instr.ch2.enabled
        instr.both_channels_enabled = case
        assert instr.ch1.enabled == case
        assert instr.ch2.enabled == case

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
    def test_source_current_limit_enabled(self, instr, channel):
        assert not instr.ch(channel).source_current_limit_enabled
        assert isinstance(instr.ch(channel).source_current_limit_enabled, bool)
