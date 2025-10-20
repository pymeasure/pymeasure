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

from pymeasure.test import expected_protocol
from pymeasure.instruments.ilxlightwave.ldp3811 import LDP3811, LDP3811Mode


def test_output_enabled_getter():
    with expected_protocol(LDP3811, [(b"OUTPUT?", 1)]) as inst:
        assert inst.output_enabled is True


def test_output_enabled_setter():
    with expected_protocol(LDP3811, [(b"OUTPUT 0", None)]) as inst:
        inst.output_enabled = False


def test_mode_getter():
    with expected_protocol(LDP3811, [(b"MODE?", "CW")]) as inst:
        assert inst.mode == LDP3811Mode.CONT_WAVE


def test_mode_setter():
    with expected_protocol(LDP3811, [(b"MODE PRI", None)]) as inst:
        inst.mode = LDP3811Mode.CONST_PULSE_REP


def test_current():
    with expected_protocol(LDP3811, [(b"LDI?", 155)]) as inst:
        assert inst.current == 155


def test_current_setpoint_getter():
    with expected_protocol(LDP3811, [(b"SET:LDI?", 155)]) as inst:
        assert inst.current_setpoint == 155


def test_current_setpoint_setter():
    with expected_protocol(
        LDP3811, [("RANGE?", 200), ("LIMIT:I200?", 200), (b"LDI 155", None)]
    ) as inst:
        inst.current_setpoint = 155


def test_current_range_500_enabled_getter():
    with expected_protocol(LDP3811, [("RANGE?", 500)]) as inst:
        assert inst.current_range_500_enabled is True


def test_current_range_500_enabled_setter():
    with expected_protocol(LDP3811, [("RANGE 200", None)]) as inst:
        inst.current_range_500_enabled = False


def test_current_limit_500_getter():
    with expected_protocol(LDP3811, [("LIMIT:I500?", 150)]) as inst:
        assert inst.current_limit_500 == 150


def test_current_limit_500_setter():
    with expected_protocol(LDP3811, [("LIMIT:I500 150", None)]) as inst:
        inst.current_limit_500 = 150


def test_current_limit_200_getter():
    with expected_protocol(LDP3811, [("LIMIT:I200?", 150)]) as inst:
        assert inst.current_limit_200 == 150


def test_current_limit_200_setter():
    with expected_protocol(LDP3811, [("LIMIT:I200 150", None)]) as inst:
        inst.current_limit_200 = 150


def test_duty_cycle():
    with expected_protocol(LDP3811, [("CDC?", 45)]) as inst:
        assert inst.duty_cycle == 45


def test_duty_cycle_setpoint_getter():
    with expected_protocol(LDP3811, [("SET:CDC?", 45)]) as inst:
        assert inst.duty_cycle_setpoint == 45


def test_duty_cycle_setpoint_setter():
    with expected_protocol(LDP3811, [("PW?", 1), ("CDC 45", None)]) as inst:
        inst.duty_cycle_setpoint = 45


def test_pulse_repetition_interval():
    with expected_protocol(LDP3811, [("PRI?", 45)]) as inst:
        assert inst.pulse_repetition_interval == 45


def test_pulse_repetition_interval_setpoint_getter():
    with expected_protocol(LDP3811, [("SET:PRI?", 45)]) as inst:
        assert inst.pulse_repetition_interval_setpoint == 45


def test_pulse_repetition_interval_setpoint_setter():
    with expected_protocol(LDP3811, [("PW?", 1), ("PRI 45", None)]) as inst:
        inst.pulse_repetition_interval_setpoint = 45


def test_pulse_width():
    with expected_protocol(LDP3811, [("PW?", 45)]) as inst:
        assert inst.pulse_width == 45


def test_pulse_width_setpoint_getter():
    with expected_protocol(LDP3811, [("SET:PW?", 45)]) as inst:
        assert inst.pulse_width_setpoint == 45


def test_pulse_width_setpoint_setter():
    with expected_protocol(LDP3811, [("PRI?", 100), ("PW 45", None)]) as inst:
        inst.pulse_width_setpoint = 45
