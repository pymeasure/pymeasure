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

from pymeasure.instruments.rohdeschwarz.smp04 import SMP04
from pymeasure.test import expected_protocol


def test_frequency_setter():
    with expected_protocol(SMP04, [("FREQ 40000000000.000", None)]) as inst:
        inst.frequency = 40e9


def test_frequency_getter():
    with expected_protocol(SMP04, [("FREQ?", "4.0E10")]) as inst:
        assert inst.frequency == 40e9


def test_frequency_truncates_to_standard_minimum():
    # Standard model: the 2 GHz lower limit clamps sub-2 GHz requests.
    with expected_protocol(SMP04, [("FREQ 2000000000.000", None)]) as inst:
        inst.frequency = 1e9


def test_frequency_extension_option_allows_low_frequency():
    # SMP-B11 lowers the limit to 10 MHz.
    with expected_protocol(
        SMP04, [("FREQ 1000000000.000", None)],
        frequency_extension_option=True,
    ) as inst:
        inst.frequency = 1e9


def test_power_setter():
    with expected_protocol(SMP04, [("POW -10.00", None)]) as inst:
        inst.power = -10


def test_power_truncates_to_standard_minimum():
    # Standard model: truncated_range clamps to the -20 dBm lower limit.
    with expected_protocol(SMP04, [("POW -20.00", None)]) as inst:
        inst.power = -200


def test_step_attenuator_option_allows_low_power():
    # SMP-B15/B17 lowers the limit to -130 dBm.
    with expected_protocol(
        SMP04, [("POW -130.00", None)],
        step_attenuator_option=True,
    ) as inst:
        inst.power = -200


def test_output_enabled_setter():
    with expected_protocol(SMP04, [("OUTP 1", None)]) as inst:
        inst.output_enabled = True


def test_frequency_mode_setter():
    with expected_protocol(SMP04, [("FREQ:MODE SWEEP", None)]) as inst:
        inst.frequency_mode = "SWEEP"


def test_power_mode_getter():
    with expected_protocol(SMP04, [("POW:MODE?", "FIXED")]) as inst:
        assert inst.power_mode == "FIXED"


def test_reference_source_setter():
    with expected_protocol(SMP04, [("ROSC:SOUR EXT", None)]) as inst:
        inst.reference_source = "EXT"


def test_reference_frequency_setter():
    with expected_protocol(SMP04, [("ROSC:EXT:FREQ 1e+07", None)]) as inst:
        inst.reference_frequency = 10e6


def test_reference_frequency_rejects_off_step_value():
    with expected_protocol(SMP04, []) as inst, pytest.raises(ValueError):
        inst.reference_frequency = 10.5e6


def test_alc_enabled_setter():
    with expected_protocol(SMP04, [("POW:ALC 1", None)]) as inst:
        inst.alc_enabled = True


def test_attenuator_mode_setter():
    with expected_protocol(SMP04, [("OUTP:AMOD FIX", None)]) as inst:
        inst.attenuator_mode = "FIX"


def test_am_enabled_setter():
    with expected_protocol(SMP04, [("AM:STAT 1", None)]) as inst:
        inst.am_enabled = True


def test_fm_enabled_getter():
    with expected_protocol(SMP04, [("FM:STAT?", "1")]) as inst:
        assert inst.fm_enabled is True


def test_pulse_modulation_enabled_setter():
    with expected_protocol(SMP04, [("PULM:STAT 1", None)]) as inst:
        inst.pulse_modulation_enabled = True


def test_questionable_condition_getter():
    with expected_protocol(SMP04, [("STAT:QUES:COND?", "32")]) as inst:
        assert inst.questionable_condition == 32


def test_frequency_ok_when_bit_clear():
    with expected_protocol(SMP04, [("STAT:QUES:COND?", "0")]) as inst:
        assert inst.frequency_ok is True


def test_frequency_ok_when_bit_set():
    with expected_protocol(SMP04, [("STAT:QUES:COND?", "32")]) as inst:
        assert inst.frequency_ok is False
