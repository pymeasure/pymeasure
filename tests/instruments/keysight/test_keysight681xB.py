#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.instruments.keysight import Keysight6812B
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
            Keysight6812B,
            [],
    ):
        pass  # Verify the expected communication.


def test_clipped_sine_setpoint_pct_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'FUNC:CSIN 50.000000', None)],
    ) as inst:
        inst.clipped_sine_setpoint_pct = 50


def test_clipped_sine_setpoint_pct_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'FUNC:CSIN?', b'1.00000E+2\n')],
    ) as inst:
        assert inst.clipped_sine_setpoint_pct == 100.0


def test_crest_factor_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:CURR:CRESTFACTOR?', b'3.67883E+0\n')],
    ) as inst:
        assert inst.crest_factor == 3.67883


def test_current_ac_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:CURR:AC?', b'7.42623E-3\n')],
    ) as inst:
        assert inst.current_ac == 0.00742623


def test_current_acdc_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:CURR:ACDC?', b'7.36194E-3\n')],
    ) as inst:
        assert inst.current_acdc == 0.00736194


def test_current_amplitude_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:CURR:AMPL:MAX?', b'2.63954E-2\n')],
    ) as inst:
        assert inst.current_amplitude == 0.0263954


def test_current_dc_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:CURR:DC?', b'-3.13139E-4\n')],
    ) as inst:
        assert inst.current_dc == -0.000313139


def test_current_setpoint_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'CURRENT 2.000000', None)],
    ) as inst:
        inst.current_setpoint = 2


def test_current_setpoint_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'CURRENT?', b'6.56500E+0\n')],
    ) as inst:
        assert inst.current_setpoint == 6.565


def test_frequency_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:FREQUENCY?', b'6.00000E+1\n')],
    ) as inst:
        assert inst.frequency == 60.0


def test_frequency_setpoint_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'FREQ 60.000000', None)],
    ) as inst:
        inst.frequency_setpoint = 60


def test_frequency_setpoint_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'FREQ?', b'6.00000E+1\n')],
    ) as inst:
        assert inst.frequency_setpoint == 60.0


def test_id_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'*IDN?', b'HEWLETT-PACKARD,6812B,0,A.00.07\n')],
    ) as inst:
        assert inst.id == 'HEWLETT-PACKARD,6812B,0,A.00.07'


def test_output_enabled_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'OUTPUT:STATE 0', None)],
    ) as inst:
        inst.output_enabled = False


def test_output_enabled_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'OUTPUT:STATE?', b'0\n')],
    ) as inst:
        assert inst.output_enabled is False


def test_power_apparent_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:POW:AC:APPARENT?', b'7.13993E-4\n')],
    ) as inst:
        assert inst.power_apparent == 0.000713993


def test_power_dc_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:POW:DC?', b'3.49334E-6\n')],
    ) as inst:
        assert inst.power_dc == 3.49334e-06


def test_power_factor_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:POW:AC:PFACTOR?', b'1.99682E-1\n')],
    ) as inst:
        assert inst.power_factor == 0.199682


def test_power_reactive_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:POW:AC:REACTIVE?', b'6.63752E-4\n')],
    ) as inst:
        assert inst.power_reactive == 0.000663752


def test_power_real_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:POW:AC:REAL?', b'1.47986E-4\n')],
    ) as inst:
        assert inst.power_real == 0.000147986


def test_power_total_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:POW:AC:TOTAL?', b'1.26880E-4\n')],
    ) as inst:
        assert inst.power_total == 0.00012688


def test_pulse_count_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:COUNT 10.000000', None)],
    ) as inst:
        inst.pulse_count = 10


def test_pulse_count_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:COUNT?', b'1.00000E+0\n')],
    ) as inst:
        assert inst.pulse_count == 1.0


def test_pulse_duty_cycle_pct_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:DCYCLE 50.000000', None)],
    ) as inst:
        inst.pulse_duty_cycle_pct = 50


def test_pulse_duty_cycle_pct_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:DCYCLE?', b'5.00000E+1\n')],
    ) as inst:
        assert inst.pulse_duty_cycle_pct == 50.0


def test_pulse_period_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:PER 1.500000', None)],
    ) as inst:
        inst.pulse_period = 1.5


def test_pulse_period_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:PER?', b'3.33333E-2\n')],
    ) as inst:
        assert inst.pulse_period == 0.0333333


def test_pulse_width_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:WIDTH 0.500000', None)],
    ) as inst:
        inst.pulse_width = 0.5


def test_pulse_width_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'PULSE:WIDTH?', b'1.66667E-2\n')],
    ) as inst:
        assert inst.pulse_width == 0.0166667


def test_trigger_source_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRIG:SEQ1:SOUR BUS', None)],
    ) as inst:
        inst.trigger_source = 'BUS'


def test_trigger_source_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRIG:SOUR?', b'BUS\n')],
    ) as inst:
        assert inst.trigger_source == 'BUS'


def test_trigger_sync_phase_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRIG:SYNC:PHASE 0.000000', None)],
    ) as inst:
        inst.trigger_sync_phase = 0


def test_trigger_sync_phase_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRIG:SYNC:PHASE?', b'0.0E+0\n')],
    ) as inst:
        assert inst.trigger_sync_phase == 0.0


def test_trigger_sync_source_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRIG:SYNC:SOUR IMM', None)],
    ) as inst:
        inst.trigger_sync_source = 'IMM'


def test_trigger_sync_source_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRIG:SYNC:SOUR?', b'IMM\n')],
    ) as inst:
        assert inst.trigger_sync_source == 'IMM'


def test_user_wfm_catalog_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'TRACE:CATALOG?', b'"SINUSOID","SQUARE","CSINUSOID","FERRO","QSW"\n')],
    ) as inst:
        assert inst.user_wfm_catalog == ['SINUSOID', 'SQUARE', 'CSINUSOID', 'FERRO', 'QSW']


def test_voltage_ac_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:VOLT:AC?', b'9.03367E-2\n')],
    ) as inst:
        assert inst.voltage_ac == 0.0903367


def test_voltage_acdc_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:VOLT:ACDC?', b'9.09677E-2\n')],
    ) as inst:
        assert inst.voltage_acdc == 0.0909677


def test_voltage_dc_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'MEAS:VOLT:DC?', b'-1.85131E-2\n')],
    ) as inst:
        assert inst.voltage_dc == -0.0185131


def test_voltage_sense_source_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLTAGE:SENSE:SOURCE EXT', None)],
    ) as inst:
        inst.voltage_sense_source = 'EXT'


def test_voltage_sense_source_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLTAGE:SENSE:SOURCE?', b'INT\n')],
    ) as inst:
        assert inst.voltage_sense_source == 'INT'


def test_voltage_setpoint_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLT 60.000000', None)],
    ) as inst:
        inst.voltage_setpoint = 60


def test_voltage_setpoint_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLT?', b'0.0E+0\n')],
    ) as inst:
        assert inst.voltage_setpoint == 0.0


def test_voltage_trigger_level_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLT:TRIG 50.000000', None)],
    ) as inst:
        inst.voltage_trigger_level = 50


def test_voltage_trigger_level_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLT:TRIG?', b'0.0E+0\n')],
    ) as inst:
        assert inst.voltage_trigger_level == 0.0


def test_voltage_trigger_mode_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLT:MODE FIX', None)],
    ) as inst:
        inst.voltage_trigger_mode = 'FIX'


def test_voltage_trigger_mode_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'VOLT:MODE?', b'FIX\n')],
    ) as inst:
        assert inst.voltage_trigger_mode == 'FIX'


def test_waveform_setter():
    with expected_protocol(
            Keysight6812B,
            [(b'FUNC QSW', None)],
    ) as inst:
        inst.waveform = 'QSW'


def test_waveform_getter():
    with expected_protocol(
            Keysight6812B,
            [(b'FUNC?', b'SIN\n')],
    ) as inst:
        assert inst.waveform == 'SIN'


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'*RST', None)],
     (), {}, None),
))
def test_reset(comm_pairs, args, kwargs, value):
    with expected_protocol(
            Keysight6812B,
            comm_pairs,
    ) as inst:
        assert inst.reset(*args, **kwargs) == value
