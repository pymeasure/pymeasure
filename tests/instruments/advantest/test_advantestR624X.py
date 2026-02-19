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

from pymeasure.instruments.advantest import AdvantestR6245, AdvantestR6246
from pymeasure.instruments.advantest.advantestR624X import (
    SearchMode, OccurrenceAfterStop, HighSpeedTriggerMode,
    JumpCondition, ProgramClearMode, ComparisonMode,
    ComparisonValueType, SequenceInterruptionType, SequenceWaitMode,
    VoltageRange, CurrentRange, SweepMode, SampleHold, SampleMode,
    OutputType, MeasurementType, DOR, COR, SRER, SESR,
    seq_voltage_source, seq_current_source,
    seq_voltage_pulsed_source, seq_current_pulsed_source,
    seq_measure_voltage, seq_measure_current,
    seq_timing_parameters, seq_sample_hold_mode, seq_comparison_limits,
    seq_enable_source, seq_standby, seq_relay_mode, seq_fast_mode,
    seq_voltage_fixed_level_sweep, seq_current_fixed_level_sweep,
    seq_voltage_fixed_pulsed_sweep, seq_current_fixed_pulsed_sweep,
    seq_voltage_sweep, seq_current_sweep,
    seq_voltage_pulsed_sweep, seq_current_pulsed_sweep,
    seq_sample_mode, seq_lo_common_relay,
    seq_digital_output, seq_digital_output_enable,
    seq_conditional_jump, seq_clear_program,
    seq_wait, seq_join,
)


def test_init():
    with expected_protocol(
            AdvantestR6246,
            [],
            ):
        pass  # Verify the expected communication.


def test_set_current():
    with expected_protocol(
        AdvantestR6246,
        [("di 1,0,2.1100e-04,2.1300e-04", None),
         ("spot 1,2.3120e-03", None),
         (None, "ABCD 7.311e-4")]
    ) as inst:
        inst.ch_A.current_source(0, 0.000211, 2.13e-4)
        inst.ch_A.change_source_current = 23.12e-4
        assert inst.read_measurement() == 0.0007311


def test_event_status_setter():
    with expected_protocol(
        AdvantestR6246,
        [('*ese 255', None),
         ('*ese?', "200")]
    ) as inst:
        inst.event_status_enable = 258  # too large, gets truncated
        assert inst.event_status_enable == 200


# LDS? query tests

def test_operation_mode():
    with expected_protocol(
        AdvantestR6246,
        [("lds?", "JM 1,1,1;GDLY 0,1.0000e-03")]
    ) as inst:
        result = inst.operation_mode()
        assert result == "JM 1,1,1;GDLY 0,1.0000e-03"


def test_system_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_50?", "FMT 0,1,1,2;LTL 0,1,3;LF 0,2;S0")]
    ) as inst:
        result = inst.system_settings()
        assert result == "FMT 0,1,1,2;LTL 0,1,3;LF 0,2;S0"


def test_output_waveform_settings_ch_a():
    with expected_protocol(
        AdvantestR6246,
        [("lds_01?", "DV 1,20,5.0000e+00,1.0000e-01")]
    ) as inst:
        result = inst.ch_A.output_waveform_settings()
        assert result == "DV 1,20,5.0000e+00,1.0000e-01"


def test_output_waveform_settings_ch_b():
    with expected_protocol(
        AdvantestR6246,
        [("lds_02?", "DI 2,3,1.0000e-03,1.0000e+01")]
    ) as inst:
        result = inst.ch_B.output_waveform_settings()
        assert result == "DI 2,3,1.0000e-03,1.0000e+01"


def test_measurement_range_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_11?", "RV 1,1,1,0;MST 1,13;WT 1,0,0,0,0")]
    ) as inst:
        result = inst.ch_A.measurement_range_settings()
        assert result == "RV 1,1,1,0;MST 1,13;WT 1,0,0,0,0"


def test_response_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_21?", "FL 1,2;OPM 1,3;OSL 1,1,1")]
    ) as inst:
        result = inst.ch_A.response_settings()
        assert result == "FL 1,2;OPM 1,3;OSL 1,1,1"


def test_data_output_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_31?", "NUG 1,1;CMD 1,1,1,0,0;OFM 1,1,1;WM 1,1")]
    ) as inst:
        result = inst.ch_A.data_output_settings()
        assert result == "NUG 1,1;CMD 1,1,1,0,0;OFM 1,1,1;WM 1,1"


def test_io_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_41?", "IAN 1,1;TOT 1,0;TJM 1,1;SCT 1,1,1")]
    ) as inst:
        result = inst.ch_A.io_settings()
        assert result == "IAN 1,1;TOT 1,0;TJM 1,1;SCT 1,1,1"


# Search measurement tests

def test_search_measurement_setup():
    with expected_protocol(
        AdvantestR6246,
        [("mar 0,1,2;FXV 1,20,6,17,2,0;nent", None)]
    ) as inst:
        inst.search_measurement_setup(
            SearchMode.BINARY_SENSE,
            OccurrenceAfterStop.LEAVE_AS_IS,
            'FXV 1,20,6,17,2,0'
        )


def test_search_measurement_setup_search_channel():
    with expected_protocol(
        AdvantestR6246,
        [("mar 0,2,2;WV 2,1,1,20,-3,0,17,6.2E-2,-3;nent", None)]
    ) as inst:
        inst.search_measurement_setup(
            SearchMode.BINARY_SEARCH_NEGATIVE,
            OccurrenceAfterStop.LEAVE_AS_IS,
            'WV 2,1,1,20,-3,0,17,6.2E-2,-3'
        )


def test_search_measurement_setup_invalid_command():
    with expected_protocol(
        AdvantestR6246,
        []
    ) as inst:
        with pytest.raises(ValueError):
            inst.search_measurement_setup(1, 1, 'DV 1,20,5,0.1')


def test_search_comparison_setup():
    with expected_protocol(
        AdvantestR6246,
        [("mar 0,1,2;cmd 1,3,1,5.8000e+00,-1.4000e+00;nent", None)]
    ) as inst:
        inst.search_comparison_setup(
            SearchMode.BINARY_SENSE,
            OccurrenceAfterStop.LEAVE_AS_IS,
            1, 3, 1, 5.8, -1.4
        )


def test_search_comparison_setup_invalid_limits():
    with expected_protocol(
        AdvantestR6246,
        []
    ) as inst:
        with pytest.raises(ValueError):
            inst.search_comparison_setup(1, 1, 1, 2, 1, -1.0, 5.0)


# High-speed sequence tests

def test_store_highspeed_sequence():
    with expected_protocol(
        AdvantestR6246,
        [("pgst 1;DV 1,20,2,5;CN 1;end", None)]
    ) as inst:
        inst.store_highspeed_sequence(1, 'DV 1,20,2,5;CN 1')


def test_conditional_jump():
    with expected_protocol(
        AdvantestR6246,
        [("ext 3,1,10", None)]
    ) as inst:
        inst.conditional_jump(3, JumpCondition.HI_PROCEED, 10)


def test_enable_highspeed_sequence():
    with expected_protocol(
        AdvantestR6246,
        [("pgon 0,1", None)]
    ) as inst:
        inst.enable_highspeed_sequence(HighSpeedTriggerMode.CONTINUOUS)


def test_disable_highspeed_sequence():
    with expected_protocol(
        AdvantestR6246,
        [("pgof", None)]
    ) as inst:
        inst.disable_highspeed_sequence()


def test_clear_highspeed_sequence_specified():
    with expected_protocol(
        AdvantestR6246,
        [("pcel 5,1", None)]
    ) as inst:
        inst.clear_highspeed_sequence(5, ProgramClearMode.SPECIFIED_ONLY)


def test_clear_highspeed_sequence_and_subsequent():
    with expected_protocol(
        AdvantestR6246,
        [("pcel 6,2", None)]
    ) as inst:
        inst.clear_highspeed_sequence(6, ProgramClearMode.SPECIFIED_AND_SUBSEQUENT)


def test_store_highspeed_sequence_invalid_command():
    with expected_protocol(
        AdvantestR6246,
        []
    ) as inst:
        with pytest.raises(ValueError):
            inst.store_highspeed_sequence(1, 'RU 1')


def test_interrupt_sequence():
    with expected_protocol(
        AdvantestR6246,
        [("sqsp 2", None)]
    ) as inst:
        inst.interrupt_sequence(SequenceInterruptionType.PAUSE)


def test_search_comparison_setup_enums():
    with expected_protocol(
        AdvantestR6246,
        [("mar 0,1,2;cmd 1,2,1,3.0000e+00,-1.0000e+00;nent", None)]
    ) as inst:
        inst.search_comparison_setup(
            SearchMode.BINARY_SENSE,
            OccurrenceAfterStop.LEAVE_AS_IS,
            1,
            ComparisonMode.ON_WITH_POLARITY,
            ComparisonValueType.VOLTAGE,
            3.0, -1.0
        )


def test_sequence_wait():
    with expected_protocol(
        AdvantestR6246,
        [("wait 1,5.0", None)]
    ) as inst:
        inst.sequence_wait(SequenceWaitMode.WAIT_TIME, 5.0)


# Sequence command builder tests


def test_seq_voltage_source():
    assert seq_voltage_source(1, VoltageRange.FIXED_BEST, 5.0, 0.1) == \
        'dv 1,20,5.0000e+00,1.0000e-01'


def test_seq_current_source():
    assert seq_current_source(2, CurrentRange.FIXED_BEST, 1e-3, 10.0) == \
        'di 2,20,1.0000e-03,1.0000e+01'


def test_seq_voltage_pulsed_source():
    assert seq_voltage_pulsed_source(
        1, VoltageRange.FIXED_BEST, 5.0, 0.0, 0.1) == \
        'pv 1,20,5.0000e+00,0.0000e+00,1.0000e-01'


def test_seq_current_pulsed_source():
    assert seq_current_pulsed_source(
        1, CurrentRange.FIXED_BEST, 1e-3, 0.0, 10.0) == \
        'pi 1,20,1.0000e-03,0.0000e+00,1.0000e+01'


def test_seq_measure_voltage():
    assert seq_measure_voltage(1) == 'rv 1,1,1,0'


def test_seq_measure_voltage_disabled():
    assert seq_measure_voltage(
        2, enable=False, internal_measurement=False,
        voltage_range=VoltageRange.FIXED_60V) == 'rv 2,2,2,5'


def test_seq_measure_current():
    assert seq_measure_current(1) == 'ri 1,1,1,0'


def test_seq_timing_parameters():
    assert seq_timing_parameters(1, 0, 1e-3, 5e-3, 10e-3) == \
        'wt 1,0.0000e+00,1.0000e-03,5.0000e-03,1.0000e-02'


def test_seq_sample_hold_mode():
    assert seq_sample_hold_mode(1, SampleHold.MODE_1mS) == 'mst 1,9'


def test_seq_comparison_limits():
    assert seq_comparison_limits(1, True, True, 5.0, -1.0) == \
        'cmd 1,2,1,5.0000e+00,-1.0000e+00'


def test_seq_enable_source():
    assert seq_enable_source(1) == 'cn 1'
    assert seq_enable_source(2) == 'cn 2'


def test_seq_standby():
    assert seq_standby(1) == 'cl 1'


def test_seq_relay_mode():
    assert seq_relay_mode(1, 3) == 'opm 1,3'


def test_seq_fast_mode():
    assert seq_fast_mode(1, True) == 'fl 1,1'
    assert seq_fast_mode(1, False) == 'fl 1,2'


def test_seq_voltage_fixed_level_sweep():
    assert seq_voltage_fixed_level_sweep(
        1, VoltageRange.FIXED_BEST, 5.0, 10, 0.1) == \
        'fxv 1,20,5.0000e+00,10,1.0000e-01,0.0000e+00'


def test_seq_current_fixed_level_sweep():
    assert seq_current_fixed_level_sweep(
        1, CurrentRange.FIXED_BEST, 1e-3, 10, 10.0) == \
        'fxi 1,20,1.0000e-03,10,1.0000e+01,0.0000e+00'


def test_seq_voltage_fixed_pulsed_sweep():
    assert seq_voltage_fixed_pulsed_sweep(
        1, VoltageRange.FIXED_BEST, 5.0, 0.0, 10, 0.1) == \
        'pxv 1,20,5.0000e+00,0.0000e+00,10,1.0000e-01,0.0000e+00'


def test_seq_current_fixed_pulsed_sweep():
    assert seq_current_fixed_pulsed_sweep(
        1, CurrentRange.FIXED_BEST, 1e-3, 0.0, 10, 10.0) == \
        'pxi 1,20,1.0000e-03,0.0000e+00,10,1.0000e+01,0.0000e+00'


def test_seq_voltage_sweep():
    assert seq_voltage_sweep(
        1, SweepMode.LINEAR_ONE_WAY_SWEEP, 1, VoltageRange.FIXED_BEST,
        0.0, 5.0, 100, 0.1) == \
        'wv 1,1,1,20,0.0000e+00,5.0000e+00,100,1.0000e-01,0.0000e+00'


def test_seq_current_sweep():
    assert seq_current_sweep(
        1, SweepMode.LINEAR_ONE_WAY_SWEEP, 1, CurrentRange.FIXED_BEST,
        0.0, 1e-3, 100, 10.0) == \
        'wi 1,1,1,20,0.0000e+00,1.0000e-03,100,1.0000e+01,0.0000e+00'


def test_seq_voltage_pulsed_sweep():
    assert seq_voltage_pulsed_sweep(
        1, SweepMode.LINEAR_ONE_WAY_SWEEP, 1, VoltageRange.FIXED_BEST,
        0.0, 0.0, 5.0, 100, 0.1) == \
        'pwv 1,1,1,20,0.0000e+00,0.0000e+00,5.0000e+00,100,' \
        '1.0000e-01,0.0000e+00'


def test_seq_current_pulsed_sweep():
    assert seq_current_pulsed_sweep(
        1, SweepMode.LINEAR_ONE_WAY_SWEEP, 1, CurrentRange.FIXED_BEST,
        0.0, 0.0, 1e-3, 100, 10.0) == \
        'pwi 1,1,1,20,0.0000e+00,0.0000e+00,1.0000e-03,100,' \
        '1.0000e+01,0.0000e+00'


def test_seq_sample_mode():
    assert seq_sample_mode(SampleMode.ASYNC) == 'jm 1,1,1'


def test_seq_lo_common_relay():
    assert seq_lo_common_relay(True) == 'ltl 0,2,3'
    assert seq_lo_common_relay(True, True) == 'ltl 0,2,2'


def test_seq_digital_output():
    assert seq_digital_output(255) == 'dios 0,255'
    assert seq_digital_output([100, 200]) == 'dios 0,100,200'


def test_seq_digital_output_enable():
    assert seq_digital_output_enable(65535) == 'dioe 0,65535'


def test_seq_conditional_jump():
    assert seq_conditional_jump(
        3, JumpCondition.HI_PROCEED, 10) == 'ext 3,1,10'


def test_seq_clear_program():
    assert seq_clear_program(
        5, ProgramClearMode.SPECIFIED_ONLY) == 'pcel 5,1'


def test_seq_wait():
    assert seq_wait(SequenceWaitMode.WAIT_TIME, 5.0) == 'wait 1,5.0'


def test_seq_join():
    result = seq_join(
        seq_voltage_source(1, 20, 5, 0.1), seq_enable_source(1))
    assert result == 'dv 1,20,5.0000e+00,1.0000e-01;cn 1'


def test_seq_voltage_source_invalid_channel():
    with pytest.raises(ValueError):
        seq_voltage_source(3, VoltageRange.AUTO, 1.0, 0.1)


def test_store_highspeed_sequence_with_builders():
    with expected_protocol(
        AdvantestR6246,
        [("pgst 1;dv 1,20,5.0000e+00,1.0000e-01;cn 1;end", None)]
    ) as inst:
        cmd = seq_join(
            seq_voltage_source(1, VoltageRange.FIXED_BEST, 5.0, 0.1),
            seq_enable_source(1))
        inst.store_highspeed_sequence(1, cmd)


# AdvantestR624X instrument-level method tests


def test_enable_source():
    with expected_protocol(
        AdvantestR6246,
        [("cn 0", None)]
    ) as inst:
        inst.enable_source()


def test_standby():
    with expected_protocol(
        AdvantestR6246,
        [("cl 0", None)]
    ) as inst:
        inst.standby()


def test_clear_status_register():
    with expected_protocol(
        AdvantestR6246,
        [("*cls", None)]
    ) as inst:
        inst.clear_status_register()


def test_trigger():
    with expected_protocol(
        AdvantestR6246,
        [("xe 0", None)]
    ) as inst:
        inst.trigger()


def test_stop():
    with expected_protocol(
        AdvantestR6246,
        [("sp 0", None)]
    ) as inst:
        inst.stop()


def test_digital_output_int():
    with expected_protocol(
        AdvantestR6246,
        [("dios 0,255", None)]
    ) as inst:
        inst.digital_output(255)


def test_digital_output_list():
    with expected_protocol(
        AdvantestR6246,
        [("dios 0,100,200", None)]
    ) as inst:
        inst.digital_output([100, 200])


def test_trigger_output_signal():
    with expected_protocol(
        AdvantestR6246,
        [("osig 0,2,3,1", None)]
    ) as inst:
        inst.trigger_output_signal(2, 3, 1)


def test_output_format():
    with expected_protocol(
        AdvantestR6246,
        [("fmt 0,1,2,3", None)]
    ) as inst:
        inst.output_format(1, 2, 3)


def test_lo_common_relay():
    with expected_protocol(
        AdvantestR6246,
        [("ltl 0,2,3", None)]
    ) as inst:
        inst.lo_common_relay(True)


def test_lo_common_relay_with_lo():
    with expected_protocol(
        AdvantestR6246,
        [("ltl 0,1,2", None)]
    ) as inst:
        inst.lo_common_relay(False, lo_relay=True)


def test_start_sequence_program():
    with expected_protocol(
        AdvantestR6246,
        [("ru 0,1,10,5", None)]
    ) as inst:
        inst.start_sequence_program(1, 10, 5)


def test_store_sequence_command():
    with expected_protocol(
        AdvantestR6246,
        [("st 5;dv 1,20,5,0.1;end", None)]
    ) as inst:
        inst.store_sequence_command(5, 'dv 1,20,5,0.1')


def test_store_sequence_command_trailing_semicolon():
    with expected_protocol(
        AdvantestR6246,
        [("st 3;cn 1;cl 2;end", None)]
    ) as inst:
        inst.store_sequence_command(3, 'cn 1;cl 2;')


def test_query_sequence_program():
    with expected_protocol(
        AdvantestR6246,
        [("lst? 5", "DV 1,20,5,0.1;CN 1;")]
    ) as inst:
        result = inst.query_sequence_program(5)
        assert result == "DV 1,20,5,0.1;CN 1;"


def test_parse_measurement_with_header():
    with expected_protocol(
        AdvantestR6246,
        []
    ) as inst:
        val, header = inst.parse_measurement("ABCD 1.234e-3")
        assert val == 1.234e-3
        assert header == "ABCD"


def test_parse_measurement_without_header():
    with expected_protocol(
        AdvantestR6246,
        []
    ) as inst:
        val, header = inst.parse_measurement("5.678e+1")
        assert val == 5.678e+1
        assert header is None


def test_check_errors_no_error():
    with expected_protocol(
        AdvantestR6246,
        [("err?", "00000")]
    ) as inst:
        inst.check_errors()


def test_check_errors_undefined_command():
    with expected_protocol(
        AdvantestR6246,
        [("err?", "00200")]
    ) as inst:
        with pytest.raises(OSError, match="Error 00200"):
            inst.check_errors()


# AdvantestR624X settings/controls/measurements tests


def test_srq_enabled():
    with expected_protocol(
        AdvantestR6246,
        [("s0", None)]
    ) as inst:
        inst.srq_enabled = True


def test_srq_disabled():
    with expected_protocol(
        AdvantestR6246,
        [("s1", None)]
    ) as inst:
        inst.srq_enabled = False


def test_sweep_delay_time():
    with expected_protocol(
        AdvantestR6246,
        [("gdly 0,1.0000e-03", None)]
    ) as inst:
        inst.sweep_delay_time = 1e-3


def test_trigger_link_enabled():
    with expected_protocol(
        AdvantestR6246,
        [("tlnk 0,2", None)]
    ) as inst:
        inst.trigger_link_enabled = True


def test_display_enabled():
    with expected_protocol(
        AdvantestR6246,
        [("disp 0,1", None)]
    ) as inst:
        inst.display_enabled = True


def test_display_disabled():
    with expected_protocol(
        AdvantestR6246,
        [("disp 0,2", None)]
    ) as inst:
        inst.display_enabled = False


def test_line_frequency_50():
    with expected_protocol(
        AdvantestR6246,
        [("lf 0,1", None)]
    ) as inst:
        inst.line_frequency = 50


def test_line_frequency_60():
    with expected_protocol(
        AdvantestR6246,
        [("lf 0,2", None)]
    ) as inst:
        inst.line_frequency = 60


def test_store_config():
    with expected_protocol(
        AdvantestR6246,
        [("sav 2", None)]
    ) as inst:
        inst.store_config = 2


def test_load_config():
    with expected_protocol(
        AdvantestR6246,
        [("rcl 3", None)]
    ) as inst:
        inst.load_config = 3


def test_service_request_enable_register():
    with expected_protocol(
        AdvantestR6246,
        [("*sre 100", None),
         ("*sre?", "100")]
    ) as inst:
        inst.service_request_enable_register = 100
        result = inst.service_request_enable_register
        assert isinstance(result, SRER)


def test_power_on_clear():
    with expected_protocol(
        AdvantestR6246,
        [("*psc 1", None),
         ("*psc?", "1")]
    ) as inst:
        inst.power_on_clear = True
        assert inst.power_on_clear is True


def test_device_operation_enable_register():
    with expected_protocol(
        AdvantestR6246,
        [("doe 1024", None),
         ("doe?", "1024")]
    ) as inst:
        inst.device_operation_enable_register = 1024
        assert inst.device_operation_enable_register == 1024


def test_digital_output_enable():
    with expected_protocol(
        AdvantestR6246,
        [("dioe 0,255", None),
         ("dioe?", "255")]
    ) as inst:
        inst.digital_output_enable = 255
        assert inst.digital_output_enable == 255


def test_sequence_program_number():
    with expected_protocol(
        AdvantestR6246,
        [("lnub?", "#3003,1, 2,19")]
    ) as inst:
        assert inst.sequence_program_number == 3


def test_sequence_program_number_single():
    with expected_protocol(
        AdvantestR6246,
        [("lnub?", "#3001,1")]
    ) as inst:
        assert inst.sequence_program_number == 1


def test_status_byte_register():
    with expected_protocol(
        AdvantestR6246,
        [("*stb?", "64")]
    ) as inst:
        assert inst.status_byte_register == 64


def test_event_status_register():
    with expected_protocol(
        AdvantestR6246,
        [("*esr?", "128")]
    ) as inst:
        result = inst.event_status_register
        assert isinstance(result, SESR)
        assert result == SESR.PON


def test_device_operation_register():
    with expected_protocol(
        AdvantestR6246,
        [("doc?", "2048")]
    ) as inst:
        result = inst.device_operation_register
        assert isinstance(result, DOR)
        assert result == DOR.END_OF_SEQUENCE_PROGRAM


def test_error_register():
    with expected_protocol(
        AdvantestR6246,
        [("err?", "00000")]
    ) as inst:
        assert inst.error_register == 0


def test_self_test():
    with expected_protocol(
        AdvantestR6246,
        [("*tst?", "0")]
    ) as inst:
        assert inst.self_test == 0


# SMUChannel source/measurement method tests


def test_ch_voltage_source():
    with expected_protocol(
        AdvantestR6246,
        [("dv 1,20,5.0000e+00,1.0000e-01", None)]
    ) as inst:
        inst.ch_A.voltage_source(VoltageRange.FIXED_BEST, 5.0, 0.1)


def test_ch_voltage_source_ch_b():
    with expected_protocol(
        AdvantestR6246,
        [("dv 2,0,1.0000e+01,5.0000e-02", None)]
    ) as inst:
        inst.ch_B.voltage_source(VoltageRange.AUTO, 10.0, 0.05)


def test_ch_voltage_pulsed_source():
    with expected_protocol(
        AdvantestR6246,
        [("pv 1,20,5.0000e+00,0.0000e+00,1.0000e-01", None)]
    ) as inst:
        inst.ch_A.voltage_pulsed_source(
            VoltageRange.FIXED_BEST, 5.0, 0.0, 0.1)


def test_ch_current_source():
    with expected_protocol(
        AdvantestR6246,
        [("di 1,20,1.0000e-03,1.0000e+01", None)]
    ) as inst:
        inst.ch_A.current_source(CurrentRange.FIXED_BEST, 1e-3, 10.0)


def test_ch_current_pulsed_source():
    with expected_protocol(
        AdvantestR6246,
        [("pi 2,9,5.0000e-03,0.0000e+00,1.0000e+01", None)]
    ) as inst:
        inst.ch_B.current_pulsed_source(
            CurrentRange.FIXED_6mA, 5e-3, 0.0, 10.0)


def test_ch_measure_voltage():
    with expected_protocol(
        AdvantestR6246,
        [("rv 1,1,1,0", None)]
    ) as inst:
        inst.ch_A.measure_voltage()


def test_ch_measure_voltage_disabled():
    with expected_protocol(
        AdvantestR6246,
        [("rv 2,2,2,5", None)]
    ) as inst:
        inst.ch_B.measure_voltage(
            enable=False, internal_measurement=False,
            voltage_range=VoltageRange.FIXED_60V)


def test_ch_measure_current():
    with expected_protocol(
        AdvantestR6246,
        [("ri 1,1,1,0", None)]
    ) as inst:
        inst.ch_A.measure_current()


def test_ch_measure_current_with_range():
    with expected_protocol(
        AdvantestR6246,
        [("ri 2,1,1,11", None)]
    ) as inst:
        inst.ch_B.measure_current(
            current_range=CurrentRange.FIXED_600mA)


def test_ch_enable_source():
    with expected_protocol(
        AdvantestR6246,
        [("cn 1", None)]
    ) as inst:
        inst.ch_A.enable_source()


def test_ch_enable_source_ch_b():
    with expected_protocol(
        AdvantestR6246,
        [("cn 2", None)]
    ) as inst:
        inst.ch_B.enable_source()


def test_ch_standby():
    with expected_protocol(
        AdvantestR6246,
        [("cl 1", None)]
    ) as inst:
        inst.ch_A.standby()


def test_ch_trigger():
    with expected_protocol(
        AdvantestR6246,
        [("xe 1", None)]
    ) as inst:
        inst.ch_A.trigger()


def test_ch_stop():
    with expected_protocol(
        AdvantestR6246,
        [("sp 2", None)]
    ) as inst:
        inst.ch_B.stop()


def test_ch_clear_measurement_buffer():
    with expected_protocol(
        AdvantestR6246,
        [("mbc 1", None)]
    ) as inst:
        inst.ch_A.clear_measurement_buffer()


# SMUChannel sweep method tests


def test_ch_voltage_fixed_level_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("fxv 1,20,5.0000e+00,10,1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.voltage_fixed_level_sweep(
            VoltageRange.FIXED_BEST, 5.0, 10, 0.1)


def test_ch_voltage_fixed_pulsed_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("pxv 1,20,5.0000e+00,0.0000e+00,10,1.0000e-01,0.0000e+00",
          None)]
    ) as inst:
        inst.ch_A.voltage_fixed_pulsed_sweep(
            VoltageRange.FIXED_BEST, 5.0, 0.0, 10, 0.1)


def test_ch_voltage_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("wv 1,1,1,20,0.0000e+00,5.0000e+00,100,"
          "1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.voltage_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1,
            VoltageRange.FIXED_BEST, 0.0, 5.0, 100, 0.1)


def test_ch_voltage_pulsed_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("pwv 1,1,1,20,0.0000e+00,0.0000e+00,5.0000e+00,100,"
          "1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.voltage_pulsed_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1,
            VoltageRange.FIXED_BEST, 0.0, 0.0, 5.0, 100, 0.1)


def test_ch_voltage_random_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("mdwv 1,1,1,1,100,1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.voltage_random_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1, 1, 100, 0.1)


def test_ch_voltage_random_pulsed_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("mpwv 1,1,1,1,100,1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.voltage_random_pulsed_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1, 1, 100, 0.1)


def test_ch_voltage_random_memory():
    with expected_protocol(
        AdvantestR6246,
        [("rms 1;dv1,20,5.0000e+00,1.0000e-01;rend", None)]
    ) as inst:
        inst.ch_A.voltage_random_memory(
            1, VoltageRange.FIXED_BEST, 5.0, 0.1)


def test_ch_current_fixed_level_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("fxi 1,20,1.0000e-03,10,1.0000e+01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.current_fixed_level_sweep(
            CurrentRange.FIXED_BEST, 1e-3, 10, 10.0)


def test_ch_current_fixed_pulsed_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("pxi 2,20,1.0000e-03,0.0000e+00,10,1.0000e+01,0.0000e+00",
          None)]
    ) as inst:
        inst.ch_B.current_fixed_pulsed_sweep(
            CurrentRange.FIXED_BEST, 1e-3, 0.0, 10, 10.0)


def test_ch_current_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("wi 1,1,1,20,0.0000e+00,1.0000e-03,100,"
          "1.0000e+01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.current_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1,
            CurrentRange.FIXED_BEST, 0.0, 1e-3, 100, 10.0)


def test_ch_current_pulsed_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("pwi 1,1,1,20,0.0000e+00,0.0000e+00,1.0000e-03,100,"
          "1.0000e+01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.current_pulsed_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1,
            CurrentRange.FIXED_BEST, 0.0, 0.0, 1e-3, 100, 10.0)


def test_ch_current_random_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("mdwi 1,1,1,1,100,1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_A.current_random_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1, 1, 100, 0.1)


def test_ch_current_random_pulsed_sweep():
    with expected_protocol(
        AdvantestR6246,
        [("mpwi 2,1,1,1,100,1.0000e-01,0.0000e+00", None)]
    ) as inst:
        inst.ch_B.current_random_pulsed_sweep(
            SweepMode.LINEAR_ONE_WAY_SWEEP, 1, 1, 100, 0.1)


def test_ch_current_random_memory():
    with expected_protocol(
        AdvantestR6246,
        [("rms 5;di1,20,1.0000e-03,1.0000e+01;rend", None)]
    ) as inst:
        inst.ch_A.current_random_memory(
            5, CurrentRange.FIXED_BEST, 1e-3, 10.0)


def test_ch_read_random_memory():
    with expected_protocol(
        AdvantestR6246,
        [("rms_11? 1", "DV 1,20,5.0000e+00,1.0000e-01")]
    ) as inst:
        result = inst.ch_A.read_random_memory(1)
        assert result == "DV 1,20,5.0000e+00,1.0000e-01"


# SMUChannel settings/controls tests


def test_ch_fast_mode_enabled():
    with expected_protocol(
        AdvantestR6246,
        [("fl 1,1", None)]
    ) as inst:
        inst.ch_A.fast_mode_enabled = True


def test_ch_fast_mode_disabled():
    with expected_protocol(
        AdvantestR6246,
        [("fl 2,2", None)]
    ) as inst:
        inst.ch_B.fast_mode_enabled = False


def test_ch_sample_hold_mode():
    with expected_protocol(
        AdvantestR6246,
        [("mst 1,13", None)]
    ) as inst:
        inst.ch_A.sample_hold_mode = SampleHold.MODE_1PLC


def test_ch_null_operation_enabled():
    with expected_protocol(
        AdvantestR6246,
        [("nug 1,2", None)]
    ) as inst:
        inst.ch_A.null_operation_enabled = True


def test_ch_null_operation_disabled():
    with expected_protocol(
        AdvantestR6246,
        [("nug 2,1", None)]
    ) as inst:
        inst.ch_B.null_operation_enabled = False


def test_ch_auto_zero_enabled():
    with expected_protocol(
        AdvantestR6246,
        [("cm 1,1", None)]
    ) as inst:
        inst.ch_A.auto_zero_enabled = True


def test_ch_auto_zero_disabled():
    with expected_protocol(
        AdvantestR6246,
        [("cm 2,2", None)]
    ) as inst:
        inst.ch_B.auto_zero_enabled = False


def test_ch_relay_mode():
    with expected_protocol(
        AdvantestR6246,
        [("opm 1,3", None)]
    ) as inst:
        inst.ch_A.relay_mode = 3


def test_ch_analog_input():
    with expected_protocol(
        AdvantestR6246,
        [("ian 1,2", None)]
    ) as inst:
        inst.ch_A.analog_input = 2


def test_ch_trigger_output_timing():
    with expected_protocol(
        AdvantestR6246,
        [("tot 1,4", None)]
    ) as inst:
        inst.ch_A.trigger_output_timing = 4


def test_ch_trigger_input():
    with expected_protocol(
        AdvantestR6246,
        [("tjm 1,2", None)]
    ) as inst:
        inst.ch_A.trigger_input = 2


def test_ch_change_source_voltage():
    with expected_protocol(
        AdvantestR6246,
        [("spot 1,3.0000e+00", None)]
    ) as inst:
        inst.ch_A.change_source_voltage = 3.0


def test_ch_measurement_count():
    with expected_protocol(
        AdvantestR6246,
        [("nub_01?", "42")]
    ) as inst:
        assert inst.ch_A.measurement_count == 42


def test_ch_operation_register():
    with expected_protocol(
        AdvantestR6246,
        [("coc_01?", "1024")]
    ) as inst:
        result = inst.ch_A.operation_register
        assert isinstance(result, COR)
        assert result == COR.OVERLOAD_DETECTION


def test_ch_output_enable_register():
    with expected_protocol(
        AdvantestR6246,
        [("coe_01?", "512"),
         ("coe_01 512", None)]
    ) as inst:
        assert inst.ch_A.output_enable_register == 512
        inst.ch_A.output_enable_register = 512


# SMUChannel misc method tests (timing, modes, wire, calibration)


def test_ch_sample_mode():
    with expected_protocol(
        AdvantestR6246,
        [("jm 1,1,1", None)]
    ) as inst:
        inst.ch_A.sample_mode(SampleMode.ASYNC)


def test_ch_sample_mode_no_auto():
    with expected_protocol(
        AdvantestR6246,
        [("jm 5,2,2", None)]
    ) as inst:
        inst.ch_B.sample_mode(
            SampleMode.SWEEP_SYNC, auto_sampling=False)


def test_ch_timing_parameters():
    with expected_protocol(
        AdvantestR6246,
        [("wt 1,0.0000e+00,1.0000e-03,5.0000e-03,1.0000e-02", None)]
    ) as inst:
        inst.ch_A.timing_parameters(0, 1e-3, 5e-3, 10e-3)


def test_ch_output_type():
    with expected_protocol(
        AdvantestR6246,
        [("ofm 1,1,1", None)]
    ) as inst:
        inst.ch_A.output_type(
            OutputType.REAL_TIME_OUTPUT,
            MeasurementType.MEASURE_DATA)


def test_ch_output_type_buffering():
    with expected_protocol(
        AdvantestR6246,
        [("ofm 2,2,2", None)]
    ) as inst:
        inst.ch_B.output_type(
            OutputType.BUFFERING_OUTPUT_ALL,
            MeasurementType.MEASURE_DATA_AND_OCCURENCE)


def test_ch_scanner_control():
    with expected_protocol(
        AdvantestR6246,
        [("sct 1,2,1", None)]
    ) as inst:
        inst.ch_A.scanner_control(2, 1)


def test_ch_wire_mode_four_wire():
    with expected_protocol(
        AdvantestR6246,
        [("osl 1,1,1", None)]
    ) as inst:
        inst.ch_A.wire_mode(True, lo_guard=True)


def test_ch_wire_mode_two_wire():
    with expected_protocol(
        AdvantestR6246,
        [("osl 2,2,2", None)]
    ) as inst:
        inst.ch_B.wire_mode(False, lo_guard=False)


def test_ch_comparison_limits():
    with expected_protocol(
        AdvantestR6246,
        [("cmd 1,2,1,5.0000e+00,-1.0000e+00", None)]
    ) as inst:
        inst.ch_A.comparison_limits(True, True, 5.0, -1.0)


def test_ch_comparison_limits_off():
    with expected_protocol(
        AdvantestR6246,
        [("cmd 2,1,2,1.0000e+01,-1.0000e+01", None)]
    ) as inst:
        inst.ch_B.comparison_limits(False, False, 10.0, -10.0)


def test_ch_select_for_output():
    with expected_protocol(
        AdvantestR6246,
        [("fch_01?", None)]
    ) as inst:
        inst.ch_A.select_for_output()


def test_ch_select_for_output_ch_b():
    with expected_protocol(
        AdvantestR6246,
        [("fch_02?", None)]
    ) as inst:
        inst.ch_B.select_for_output()


def test_ch_read_measurement_from_addr():
    with expected_protocol(
        AdvantestR6246,
        [("rmm_11? 5", "ABCD 2.345e-2")]
    ) as inst:
        val, header = inst.ch_A.read_measurement_from_addr(5)
        assert val == 2.345e-2
        assert header == "ABCD"


def test_ch_init_calibration():
    with expected_protocol(
        AdvantestR6246,
        [("cini 1", None)]
    ) as inst:
        inst.ch_A.init_calibration()


def test_ch_store_calibration_factor():
    with expected_protocol(
        AdvantestR6246,
        [("csrt 2", None)]
    ) as inst:
        inst.ch_B.store_calibration_factor()


def test_ch_calibration_measured_value():
    with expected_protocol(
        AdvantestR6246,
        [("std 1,1.0000e+00", None)]
    ) as inst:
        inst.ch_A.calibration_measured_value = 1.0


def test_ch_calibration_generation_factor():
    with expected_protocol(
        AdvantestR6246,
        [("ccs 1,5.0000e-04", None)]
    ) as inst:
        inst.ch_A.calibration_generation_factor = 5e-4


def test_ch_calibration_measurement_factor():
    with expected_protocol(
        AdvantestR6246,
        [("ccm 1,1.0000e-03", None)]
    ) as inst:
        inst.ch_A.calibration_measurement_factor = 1e-3


# AdvantestR6245 tests


def test_r6245_init():
    with expected_protocol(
        AdvantestR6245,
        []
    ):
        pass


def test_r6245_voltage_source():
    with expected_protocol(
        AdvantestR6245,
        [("dv 1,20,1.0000e+02,1.0000e-01", None)]
    ) as inst:
        inst.ch_A.voltage_source(VoltageRange.FIXED_BEST, 100.0, 0.1)
