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

from pymeasure.instruments.advantest import AdvantestR6246
from pymeasure.instruments.advantest.advantestR624X import (
    SearchMode, OccurrenceAfterStop, HighSpeedTriggerMode,
    JumpCondition, ProgramClearMode,
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

def test_query_operation_mode():
    with expected_protocol(
        AdvantestR6246,
        [("lds?", "JM 1,1,1;GDLY 0,1.0000e-03")]
    ) as inst:
        result = inst.query_operation_mode()
        assert result == "JM 1,1,1;GDLY 0,1.0000e-03"


def test_query_system_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_50?", "FMT 0,1,1,2;LTL 0,1,3;LF 0,2;S0")]
    ) as inst:
        result = inst.query_system_settings()
        assert result == "FMT 0,1,1,2;LTL 0,1,3;LF 0,2;S0"


def test_query_output_waveform_ch_a():
    with expected_protocol(
        AdvantestR6246,
        [("lds_01?", "DV 1,20,5.0000e+00,1.0000e-01")]
    ) as inst:
        result = inst.ch_A.query_output_waveform()
        assert result == "DV 1,20,5.0000e+00,1.0000e-01"


def test_query_output_waveform_ch_b():
    with expected_protocol(
        AdvantestR6246,
        [("lds_02?", "DI 2,3,1.0000e-03,1.0000e+01")]
    ) as inst:
        result = inst.ch_B.query_output_waveform()
        assert result == "DI 2,3,1.0000e-03,1.0000e+01"


def test_query_measurement_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_11?", "RV 1,1,1,0;MST 1,13;WT 1,0,0,0,0")]
    ) as inst:
        result = inst.ch_A.query_measurement_settings()
        assert result == "RV 1,1,1,0;MST 1,13;WT 1,0,0,0,0"


def test_query_response_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_21?", "FL 1,2;OPM 1,3;OSL 1,1,1")]
    ) as inst:
        result = inst.ch_A.query_response_settings()
        assert result == "FL 1,2;OPM 1,3;OSL 1,1,1"


def test_query_data_output_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_31?", "NUG 1,1;CMD 1,1,1,0,0;OFM 1,1,1;WM 1,1")]
    ) as inst:
        result = inst.ch_A.query_data_output_settings()
        assert result == "NUG 1,1;CMD 1,1,1,0,0;OFM 1,1,1;WM 1,1"


def test_query_io_settings():
    with expected_protocol(
        AdvantestR6246,
        [("lds_41?", "IAN 1,1;TOT 1,0;TJM 1,1;SCT 1,1,1")]
    ) as inst:
        result = inst.ch_A.query_io_settings()
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
