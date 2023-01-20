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

from pymeasure.test import expected_protocol
from pymeasure.instruments.kuhneelectronic import Kusg245_250A


def test_external_enabled():
    with expected_protocol(
        Kusg245_250A,
        [("R", None), ("r?", "1"), ("r", None), ("r?", "0")],
    ) as inst:
        inst.external_enabled = True
        assert inst.external_enabled is True
        inst.external_enabled = False
        assert inst.external_enabled is False


def test_bias_enabled():
    with expected_protocol(
        Kusg245_250A,
        [("X", None), ("x?", "1"), ("x", None), ("x?", "0")],
    ) as inst:
        inst.bias_enabled = True
        assert inst.bias_enabled is True
        inst.bias_enabled = False
        assert inst.bias_enabled is False


def test_rf_enabled():
    with expected_protocol(
        Kusg245_250A,
        [("O", None), ("o?", "1"), ("o", None), ("o?", "0")],
    ) as inst:
        inst.rf_enabled = True
        assert inst.rf_enabled is True
        inst.rf_enabled = False
        assert inst.rf_enabled is False


def test_pulse_mode_enabled():
    with expected_protocol(
        Kusg245_250A,
        [("P", None), ("p?", "1"), ("p", None), ("p?", "0")],
    ) as inst:
        inst.pulse_mode_enabled = True
        assert inst.pulse_mode_enabled is True
        inst.pulse_mode_enabled = False
        assert inst.pulse_mode_enabled is False


def test_freq_steps_fine_enabled():
    with expected_protocol(
        Kusg245_250A,
        [("fm1", None), ("fm?", "1"), ("fm0", None), ("fm?", "0")],
    ) as inst:
        inst.freq_steps_fine_enabled = True
        assert inst.freq_steps_fine_enabled is True
        inst.freq_steps_fine_enabled = False
        assert inst.freq_steps_fine_enabled is False


def test_frequency_coarse():
    with expected_protocol(
        Kusg245_250A,
        [
            ("f2456", None),
            ("f?", "2456"),
            ("f2400", None),
            ("f?", "2400"),
            ("f2500", None),
            ("f?", "2500"),
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
            ("f2456780", None),
            ("f?", "2456780"),
            ("f2400000", None),
            ("f?", "2400000"),
            ("f2500000", None),
            ("f?", "2500000"),
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
            ("A123", None),
            ("A?", "123"),
            ("A000", None),
            ("A?", "000"),
            ("A250", None),
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
        Kusg245_250A, [("A000", None), ("A?", "000"), ("A020", None), ("A?", "020")], power_limit=20
    ) as inst:
        inst.power_setpoint = -1  # must be truncated to 0
        assert inst.power_setpoint == 0
        inst.power_setpoint = 300  # must be truncated to power_limit
        assert inst.power_setpoint == 20


def test_pulse_width():
    with expected_protocol(
        Kusg245_250A,
        [
            ("C0125", None),
            ("C?", "0125"),
            ("C0010", None),
            ("C?", "0010"),
            ("C1000", None),
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
            ("c0125", None),
            ("c?", "0125"),
            ("c0010", None),
            ("c?", "0010"),
            ("c1000", None),
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
            ("H088", None),
            ("H?", "088"),
            ("H000", None),
            ("H?", "000"),
            ("H255", None),
            ("H?", "255"),
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
        [("B0", None), ("B?", "0"), ("B4", None), ("B?", "4"), ("B5", None), ("B?", "5")],
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
        [("b010", None)],
    ) as inst:
        inst.tune(10)


def test_tune_power_limited():
    with expected_protocol(Kusg245_250A, [("b020", None)], power_limit=20) as inst:
        inst.tune(100)


def test_clear_VSWR_error():
    with expected_protocol(
        Kusg245_250A,
        [("z", None)],
    ) as inst:
        inst.clear_VSWR_error()


def test_store_settings():
    with expected_protocol(
        Kusg245_250A,
        [("SE", None)],
    ) as inst:
        inst.store_settings()


def test_shutdown():
    with expected_protocol(
        Kusg245_250A,
        [("o", None),
         ("x", None)],
    ) as inst:
        inst.shutdown()


def test_turn_on():
    with expected_protocol(
        Kusg245_250A,
        [("X", None),
         ("O", None)],
    ) as inst:
        inst.turn_on()
