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

from pymeasure.instruments.unit import UNITUDP6933B
from pymeasure.test import expected_protocol


def test_id():
    with expected_protocol(
        UNITUDP6933B,
        [("*IDN?", "Uni-Trend,UDP6933B,0000000000000,1.00.0905")],
    ) as instr:
        assert instr.id == "Uni-Trend,UDP6933B,0000000000000,1.00.0905"


def test_reset():
    with expected_protocol(UNITUDP6933B, [("*RST", None)]) as instr:
        instr.reset()


def test_clear():
    with expected_protocol(UNITUDP6933B, [("*CLS", None)]) as instr:
        instr.clear()


def test_next_error():
    with expected_protocol(UNITUDP6933B, [("SYST:ERR?", '0,"No error"')]) as instr:
        error = instr.next_error

    assert error[0] == 0
    assert isinstance(error[1], str)
    assert "No error" in error[1]


def test_check_errors_logs_errors(caplog):
    with expected_protocol(
        UNITUDP6933B,
        [
            ("SYST:ERR?", '-100,"Command error"'),
            ("SYST:ERR?", '0,"No error"'),
        ],
    ) as instr:
        instr.check_errors()

    assert "Command error" in caplog.text


def test_voltage_getter():
    with expected_protocol(UNITUDP6933B, [("MEAS:VOLT?", "12.345")]) as instr:
        assert instr.voltage == 12.345


def test_current_getter():
    with expected_protocol(UNITUDP6933B, [("MEAS:CURR?", "0.123")]) as instr:
        assert instr.current == 0.123


def test_power_getter():
    with expected_protocol(UNITUDP6933B, [("MEASure:POWer?", "1.518")]) as instr:
        assert instr.power == 1.518


def test_voltage_setpoint_getter():
    with expected_protocol(UNITUDP6933B, [("VOLT?", "24.000")]) as instr:
        assert instr.voltage_setpoint == 24.0


@pytest.mark.parametrize(
    "voltage, command",
    ((0, "VOLT 0"), (12, "VOLT 12"), (150, "VOLT 150")),
)
def test_voltage_setpoint_setter(voltage, command):
    with expected_protocol(UNITUDP6933B, [(command, None)]) as instr:
        instr.voltage_setpoint = voltage


@pytest.mark.parametrize("voltage", (-0.1, 150.1))
def test_voltage_setpoint_validator(voltage):
    with expected_protocol(UNITUDP6933B, []) as instr, pytest.raises(ValueError):
        instr.voltage_setpoint = voltage


def test_current_limit_getter():
    with expected_protocol(UNITUDP6933B, [("CURR?", "1.500")]) as instr:
        assert instr.current_limit == 1.5


@pytest.mark.parametrize(
    "current_limit, command",
    ((0, "CURR 0"), (0.5, "CURR 0.5"), (5, "CURR 5")),
)
def test_current_limit_setter(current_limit, command):
    with expected_protocol(UNITUDP6933B, [(command, None)]) as instr:
        instr.current_limit = current_limit


@pytest.mark.parametrize("current_limit", (-0.1, 5.1))
def test_current_limit_validator(current_limit):
    with expected_protocol(UNITUDP6933B, []) as instr, pytest.raises(ValueError):
        instr.current_limit = current_limit


@pytest.mark.parametrize("state, command", ((True, "OUTP ON"), (False, "OUTP OFF")))
def test_output_enabled_setter(state, command):
    with expected_protocol(UNITUDP6933B, [(command, None)]) as instr:
        instr.output_enabled = state


@pytest.mark.parametrize("reply, state", (("ON", True), ("OFF", False)))
def test_output_enabled_getter(reply, state):
    with expected_protocol(UNITUDP6933B, [("OUTP?", reply)]) as instr:
        assert instr.output_enabled is state


@pytest.mark.parametrize("state", ("on", "off", 2, -1))
def test_output_enabled_validator(state):
    with expected_protocol(UNITUDP6933B, []) as instr, pytest.raises(ValueError):
        instr.output_enabled = state


@pytest.mark.parametrize(
    "voltage, current_limit, commands",
    (
        (0, 0, [("VOLT 0", None), ("CURR 0", None)]),
        (12, 0.5, [("VOLT 12", None), ("CURR 0.5", None)]),
        (150, 5, [("VOLT 150", None), ("CURR 5", None)]),
    ),
)
def test_apply(voltage, current_limit, commands):
    with expected_protocol(UNITUDP6933B, commands) as instr:
        instr.apply(voltage, current_limit)


@pytest.mark.parametrize("voltage", (-0.1, 150.1))
def test_apply_voltage_validator(voltage):
    with expected_protocol(UNITUDP6933B, []) as instr, pytest.raises(ValueError):
        instr.apply(voltage, 0.5)


@pytest.mark.parametrize("current_limit", (-0.1, 5.1))
def test_apply_current_limit_validator(current_limit):
    with expected_protocol(UNITUDP6933B, []) as instr, pytest.raises(ValueError):
        instr.apply(12, current_limit)
