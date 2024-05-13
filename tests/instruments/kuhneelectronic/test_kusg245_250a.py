#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.kuhneelectronic import Kusg245_250A
from pymeasure.instruments.kuhneelectronic.kusg245_250a import termination_character, encoding


termination_character = termination_character.encode(encoding=encoding)[0]


def test_voltage_5v():
    with expected_protocol(
        Kusg245_250A,
        [("5", bytes([0, 1, termination_character]))],
    ) as inst:
        assert inst.voltage_5v == 103.0 / 4700.0


def test_voltage_32v():
    with expected_protocol(
        Kusg245_250A,
        [("8", bytes([0, 1, termination_character]))],
    ) as inst:
        assert inst.voltage_32v == 1282.0 / 8200.0


def test_power_forward():
    with expected_protocol(
        Kusg245_250A,
        [("6", bytes([255, termination_character]))],
    ) as inst:
        assert inst.power_forward == 255


def test_power_reverse():
    with expected_protocol(
        Kusg245_250A,
        [("7", bytes([255, termination_character]))],
    ) as inst:
        assert inst.power_reverse == 255


def test_external_enabled():
    with expected_protocol(
        Kusg245_250A,
        [
            ("R", "A"),
            ("r?", bytes([1, termination_character])),
            ("r", "A"),
            ("r?", bytes([0, termination_character]))
        ],
    ) as inst:
        inst.external_enabled = True
        assert inst.external_enabled is True
        inst.external_enabled = False
        assert inst.external_enabled is False


def test_bias_enabled():
    with expected_protocol(
        Kusg245_250A,
        [
            ("X", "A"),
            ("x?", bytes([1, termination_character])),
            ("x", "A"),
            ("x?", bytes([0, termination_character]))
        ],
    ) as inst:
        inst.bias_enabled = True
        assert inst.bias_enabled is True
        inst.bias_enabled = False
        assert inst.bias_enabled is False


def test_rf_enabled():
    with expected_protocol(
        Kusg245_250A,
        [
            ("O", "A"),
            ("o?", bytes([1, termination_character])),
            ("o", "A"),
            ("o?", bytes([0, termination_character]))
        ],
    ) as inst:
        inst.rf_enabled = True
        assert inst.rf_enabled is True
        inst.rf_enabled = False
        assert inst.rf_enabled is False


def test_pulse_mode_enabled():
    with expected_protocol(
        Kusg245_250A,
        [
            ("P", "A"),
            ("p?", bytes([1, termination_character])),
            ("p", "A"),
            ("p?", bytes([0, termination_character]))
        ],
    ) as inst:
        inst.pulse_mode_enabled = True
        assert inst.pulse_mode_enabled is True
        inst.pulse_mode_enabled = False
        assert inst.pulse_mode_enabled is False


def test_freq_steps_fine_enabled():
    with expected_protocol(
        Kusg245_250A,
        [
            ("fm1", "A"),
            ("fm?", bytes([1, termination_character])),
            ("fm0", "A"),
            ("fm?", bytes([0, termination_character]))
        ],
    ) as inst:
        inst.freq_steps_fine_enabled = True
        assert inst.freq_steps_fine_enabled is True
        inst.freq_steps_fine_enabled = False
        assert inst.freq_steps_fine_enabled is False


def test_frequency_coarse():
    with expected_protocol(
        Kusg245_250A,
        [
            ("f2456", "A"),
            ("f?", "2456MHz"),
            ("f2400", "A"),
            ("f?", "2400MHz"),
            ("f2500", "A"),
            ("f?", "2500MHz"),
        ],
    ) as inst:
        inst.frequency_coarse = 2456
        assert inst.frequency_coarse == 2456
        inst.frequency_coarse = 2000  # must be truncated to 2400
        assert inst.frequency_coarse == 2400
        inst.frequency_coarse = 3000  # must be truncated to 2500
        assert inst.frequency_coarse == 2500


def test_frequency_fine():
    with expected_protocol(
        Kusg245_250A,
        [
            ("f2456780", "A"),
            ("f?", "2456780kHz"),
            ("f2400000", "A"),
            ("f?", "2400000kHz"),
            ("f2500000", "A"),
            ("f?", "2500000kHz"),
        ],
    ) as inst:
        inst.frequency_fine = 2456778  # must be rounded to 2456780
        assert inst.frequency_fine == 2456780
        inst.frequency_fine = 2000000  # must be truncated to 2400000
        assert inst.frequency_fine == 2400000
        inst.frequency_fine = 3000000  # must be truncated to 2500000
        assert inst.frequency_fine == 2500000


def test_power_setpoint():
    with expected_protocol(
        Kusg245_250A,
        [
            ("A123", "A"),
            ("A?", "123"),
            ("A000", "A"),
            ("A?", "000"),
            ("A250", "A"),
            ("A?", "250"),
        ],
    ) as inst:
        inst.power_setpoint = 123
        assert inst.power_setpoint == 123
        inst.power_setpoint = -1  # must be truncated to 0
        assert inst.power_setpoint == 0
        inst.power_setpoint = 300  # must be truncated to 250
        assert inst.power_setpoint == 250


def test_power_setpoint_limited():
    with expected_protocol(
        Kusg245_250A, [("A000", "A"), ("A?", "000"), ("A020", "A"), ("A?", "020")], power_limit=20
    ) as inst:
        inst.power_setpoint = -1  # must be truncated to 0
        assert inst.power_setpoint == 0
        inst.power_setpoint = 300  # must be truncated to power_limit
        assert inst.power_setpoint == 20


def test_pulse_width():
    with expected_protocol(
        Kusg245_250A,
        [
            ("C0125", "A"),
            ("C?", "0125"),
            ("C0010", "A"),
            ("C?", "0010"),
            ("C1000", "A"),
            ("C?", "1000"),
        ],
    ) as inst:
        inst.pulse_width = 123  # must be rounded to 125
        assert inst.pulse_width == 125
        inst.pulse_width = 0  # must be truncated to 10
        assert inst.pulse_width == 10
        inst.pulse_width = 10000  # must be truncated to 250
        assert inst.pulse_width == 1000


def test_off_time():
    with expected_protocol(
        Kusg245_250A,
        [
            ("c0125", "A"),
            ("c?", "0125"),
            ("c0010", "A"),
            ("c?", "0010"),
            ("c1000", "A"),
            ("c?", "1000"),
        ],
    ) as inst:
        inst.off_time = 123  # must be rounded to 125
        assert inst.off_time == 125
        inst.off_time = 0  # must be truncated to 10
        assert inst.off_time == 10
        inst.off_time = 10000  # must be truncated to 250
        assert inst.off_time == 1000


def test_phase_shift():
    with expected_protocol(
        Kusg245_250A,
        [
            ("H088", "A"),
            ("H?", bytes([88, termination_character])),
            ("H000", "A"),
            ("H?", bytes([0, termination_character])),
            ("H255", "A"),
            ("H?", bytes([255, termination_character])),
        ],
    ) as inst:
        inst.phase_shift = 124
        assert inst.phase_shift == pytest.approx(124, 0.01)
        inst.phase_shift = -1  # must be truncated to 0
        assert inst.phase_shift == 0
        inst.phase_shift = 358.6
        assert inst.phase_shift == pytest.approx(358.6, 0.01)


def test_reflection_limit():
    with expected_protocol(
        Kusg245_250A,
        [
            ("B0", "A"),
            ("B?", bytes([0, termination_character])),
            ("B4", "A"),
            ("B?", bytes([4, termination_character])),
            ("B5", "A"),
            ("B?", bytes([5, termination_character]))
        ],
    ) as inst:
        inst.reflection_limit = 0
        assert inst.reflection_limit == 0
        inst.reflection_limit = 182  # must be rounded to the next
        # higher discrete value (200)
        assert inst.reflection_limit == 200
        inst.reflection_limit = 300  # must be truncated to 230
        assert inst.reflection_limit == 230


def test_tune():
    with expected_protocol(
        Kusg245_250A,
        [("b010", "A")],
    ) as inst:
        inst.tune(10)


def test_tune_power_limited():
    with expected_protocol(Kusg245_250A, [("b020", "A")], power_limit=20) as inst:
        inst.tune(100)


def test_clear_VSWR_error():
    with expected_protocol(
        Kusg245_250A,
        [("z", "A")],
    ) as inst:
        inst.clear_VSWR_error()


def test_store_settings():
    with expected_protocol(
        Kusg245_250A,
        [("SE", "A")],
    ) as inst:
        inst.store_settings()


def test_turn_off():
    with expected_protocol(
        Kusg245_250A,
        [("o", "A"),
         ("x", "A")],
    ) as inst:
        inst.turn_off()


def test_turn_on():
    with expected_protocol(
        Kusg245_250A,
        [("X", "A"),
         ("O", "A")],
    ) as inst:
        inst.turn_on()
