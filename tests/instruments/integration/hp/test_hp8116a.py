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

import pytest
import math
import time
from pymeasure.instruments.hp import HP8116A, hp8116a

pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestHP8116A:
    """
    Unit tests for HP8116A class.

    This test suite, needs the following setup to work properly:
        - A HP8116A device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant.
        - You must set HAS_OPTION_001 according to the device's sweep/burst capability.
    """

    RESOURCE = 'GPIB0::12'
    HAS_OPTION_001 = True

    BOOLEANS = [False, True]
    OPERATING_MODES_WO_OPT001 = ['normal', 'triggered', 'gate', 'external_width']
    OPERATING_MODES_OPT001 = ['internal_sweep', 'external_sweep', 'internal_burst',
                              'external_burst']
    CONTROL_MODES = ['off', 'FM', 'AM', 'PWM', 'VCO']
    TRIGGER_SLOPES = ['off', 'positive', 'negative']
    SHAPES = ['dc', 'sine', 'triangle', 'square', 'pulse']

    UNITS = {
        'nano': 'NZ',
        'micro': 'UZ',
        'milli': 'MZ',
        'no_prefix': 'HZ',
        'kilo': 'KHZ',
        'mega': 'MHZ'
    }
    VALUES_WITH_UNITS = [[1e-9, '1 NZ'], [1e-6, '1 UZ'], [1e-3, '1 MZ'], [1, '1 HZ'],
                         [1e3, '1 KHZ'], [1e6, '1 MHZ'], [1.23456e-9, '1.23 NZ'], [1/3, '333 MZ'],
                         [1.23456e-6, '1.23 UZ'], [1e-6, '1 UZ']]

    VALUES_WITH_UNITS_TO_PARSE = [['FRQ 2.34 MZ', 2.34e-3], ['FRQ 23.4 MZ', 23.4e-3],
                                  ['FRQ 234  MZ', 234e-3],  ['FRQ 2.34 HZ', 2.34],
                                  ['FRQ 23.4 HZ', 23.4],    ['FRQ 234  HZ', 234.0],
                                  ['FRQ 2.34KHZ', 2.34e3],  ['FRQ 23.4KHZ', 23.4e3],
                                  ['FRQ 234 KHZ', 234e3],   ['FRQ 2.34MHZ', 2.34e6],
                                  ['FRQ 23.4MHZ', 23.4e6]]

    FREQUENCIES = [[1, 1], [1.23, 1.23], [1e3, 1e3], [1.23e3, 1.23e3], [1e6, 1e6], [1.23e6, 1.23e6],
                   [1.234, 1.23], [1.234e3, 1.23e3], [10.234e3, 10.2e3], [1.234e6, 1.23e6]]

    instr = HP8116A(RESOURCE)

    @pytest.fixture
    def make_resetted_instr(self):
        self.instr.reset()
        return self.instr

    def test_given_instrument_resetted_when_triggered_then_normal(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.write('M2')  # Triggered mode
        instr.reset()
        assert 'M1' in instr.ask('CST', 10)

    @pytest.mark.parametrize('case', OPERATING_MODES_WO_OPT001)
    def test_operating_modes_no_option001(self, make_resetted_instr, case):
        instr = make_resetted_instr
        if case == 'external_width':
            instr.write('W4')  # External width mode only valid in pulse mode
        instr.operating_mode = case
        assert instr.operating_mode == case

    @pytest.mark.parametrize('case', OPERATING_MODES_OPT001)
    def test_operating_modes_option001(self, make_resetted_instr, case):
        instr = make_resetted_instr

        instr.operating_mode = case
        if self.HAS_OPTION_001:
            assert instr.operating_mode == case
        else:
            assert instr.operating_mode == 'normal'

    @pytest.mark.parametrize('case', CONTROL_MODES)
    def test_control_modes(self, make_resetted_instr, case):
        instr = make_resetted_instr
        if case == 'PWM':
            instr.write('W4')  # PWM mode only valid in pulse mode
        instr.control_mode = case
        assert instr.control_mode == case

    @pytest.mark.parametrize('case', TRIGGER_SLOPES)
    def test_trigger_slopes(self, make_resetted_instr, case):
        instr = make_resetted_instr
        instr.trigger_slope = case
        assert instr.trigger_slope == case

    @pytest.mark.parametrize('case', SHAPES)
    def test_shapes(self, make_resetted_instr, case):
        instr = make_resetted_instr
        instr.shape = case
        assert instr.shape == case

    def test_given_long_operation_then_buffer_not_empty_bit_set(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.adapter.write('W4')  # Takes about 330 ms to process according to the service manual
        assert (instr.status & hp8116a.Status.buffer_not_empty)
        instr._wait_for_commands_processed()  # Now wait so that the instrument doesn't lock up

    def test_write(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.write('W4')
        assert not (instr.status & hp8116a.Status.buffer_not_empty)

    def test_given_read_called_then_exception(self, make_resetted_instr):
        instr = make_resetted_instr
        with pytest.raises(NotImplementedError):
            instr.read()

    def test_given_ask_called_then_return_value_valid(self, make_resetted_instr):
        instr = make_resetted_instr
        ret = instr.ask('IFRQ', 14)
        assert type(ret) is str
        assert '\n' not in ret
        assert '\r' not in ret
        assert 'FRQ' in ret

    @pytest.mark.parametrize('case, expected', VALUES_WITH_UNITS)
    def test_get_value_with_unit(self, case, expected):
        ret = HP8116A._get_value_with_unit(case, self.UNITS)
        assert ret == expected

    @pytest.mark.parametrize('case, expected', VALUES_WITH_UNITS_TO_PARSE)
    def test_parse_value_with_unit(self, case, expected):
        ret = HP8116A._parse_value_with_unit(case, self.UNITS)
        assert math.isclose(ret, expected)

    def test_generate_1_2_5_sequence(self):
        min = 200e-6
        max = 1
        expected = [200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3,
                    100e-3, 200e-3, 500e-3, 1]
        ret = HP8116A._generate_1_2_5_sequence(min, max)
        assert ret == expected

    @pytest.mark.parametrize('case', BOOLEANS)
    def test_haversine_enabled(self, case, make_resetted_instr):
        instr = make_resetted_instr
        instr.haversine_enabled = case
        assert instr.haversine_enabled == case

    @pytest.mark.parametrize('case', BOOLEANS)
    def test_autovernier_enabled(self, case, make_resetted_instr):
        instr = make_resetted_instr
        instr.autovernier_enabled = case
        assert instr.autovernier_enabled == case

    @pytest.mark.parametrize('case', BOOLEANS)
    def test_limit_enabled(self, case, make_resetted_instr):
        instr = make_resetted_instr
        instr.limit_enabled = case
        assert instr.limit_enabled == case

    @pytest.mark.parametrize('case', BOOLEANS)
    def test_complement_enabled(self, case, make_resetted_instr):
        instr = make_resetted_instr
        instr.complement_enabled = case
        assert instr.complement_enabled == case

    @pytest.mark.parametrize('case', BOOLEANS)
    def test_output_enabled(self, case, make_resetted_instr):
        instr = make_resetted_instr
        instr.output_enabled = case
        assert instr.output_enabled == case

    @pytest.mark.parametrize('case, expected', FREQUENCIES)
    def test_frequency(self, case, expected, make_resetted_instr):
        instr = make_resetted_instr
        instr.frequency = case
        assert math.isclose(instr.frequency, expected)

    def test_given_invalid_frequency_when_set_frequency_then_(self, make_resetted_instr):
        instr = make_resetted_instr
        with pytest.raises(ValueError):
            instr.frequency = 1e9  # Sadly 1 GHz is too high :(

    def test_check_has_option_001(self, make_resetted_instr):
        instr = make_resetted_instr
        assert instr._check_has_option_001() == self.HAS_OPTION_001

    def test_given_resetted_when_check_errors_then_no_error(self, make_resetted_instr):
        instr = make_resetted_instr
        errors = instr.check_errors()
        assert type(errors) is list
        assert len(errors) == 0

    def test_given_invalid_duty_cycle_when_check_errors_then_error(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.frequency = 50e6
        instr.duty_cycle = 90
        errors = instr.check_errors()
        assert len(errors) == 1
        assert errors[0] == 'DUTY C. ERROR'

    def test_given_two_error_conditions_when_check_errors_then_two_errors(self,
                                                                          make_resetted_instr):
        instr = make_resetted_instr

        # Triggering duty cycle error since 90 % is too high at 50 MHz
        instr.frequency = 50e6
        instr.duty_cycle = 90

        # Triggering handling error since autovernier is not possible in triggered mode
        instr.operating_mode = 'triggered'
        instr.autovernier_enabled = True

        errors = instr.check_errors()
        assert len(errors) == 2
        assert 'DUTY C. ERROR' in errors
        assert 'HANDLING ERROR' in errors

    def test_given_autovernier_disabled_when_start_autovernier_then_error(self,
                                                                          make_resetted_instr):
        instr = make_resetted_instr
        with pytest.raises(RuntimeError):
            instr.start_autovernier(HP8116A.frequency, HP8116A.Digit.LEAST_SIGNIFICANT,
                                    HP8116A.Direction.UP)

    def test_given_invalid_control_when_start_autovernier_then_error(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.autovernier_enabled = True
        with pytest.raises(ValueError):
            instr.start_autovernier(HP8116A.sweep_start, HP8116A.Digit.LEAST_SIGNIFICANT,
                                    HP8116A.Direction.UP)

    def test_autovernier(self, make_resetted_instr):
        instr = make_resetted_instr
        instr.autovernier_enabled = True
        instr.start_autovernier(HP8116A.amplitude, HP8116A.Digit.SECOND_SIGNIFICANT,
                                HP8116A.Direction.UP, 100e-3)
        time.sleep(0.5)
        instr.autovernier_enabled = False
        assert instr.amplitude > 120e-3
