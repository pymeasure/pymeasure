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

from pymeasure.adapters import ProtocolAdapter
from pymeasure.instruments.newport.smc100 import (
    SMC100,
    SMC100CC,
    SMC100PP,
    SMC100CommandError,
    SMC100ControllerState,
    SMC100PositionerError,
    SMC100StateCode,
)
from pymeasure.test import expected_protocol

OK = ("1TE", "1TE@")


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr("pymeasure.instruments.newport.smc100.time.sleep", lambda s: None)


def test_init():
    with expected_protocol(SMC100PP, []):
        pass


@pytest.mark.parametrize("address", (0, 32, 2.5))
def test_invalid_address(address):
    with pytest.raises(ValueError):
        SMC100PP(adapter=None, address=address)


@pytest.mark.parametrize("address", (3, 3.0))
def test_address_prefix(address):
    with expected_protocol(SMC100PP, [("3TP", "3TP12.5")], address=address) as inst:
        assert inst.position == 12.5


def test_unexpected_reply():
    with expected_protocol(SMC100PP, [("1TP", "1TH12.5")]) as inst, pytest.raises(ConnectionError):
        _ = inst.position


def test_firmware_version():
    with expected_protocol(SMC100PP, [("1VE", "1VE SMC_PP 3.0.0")]) as inst:
        assert inst.firmware_version == "SMC_PP 3.0.0"


def test_stage_identifier():
    with expected_protocol(SMC100CC, [("1ID?", "1IDURS100CC")]) as inst:
        assert inst.stage_identifier == "URS100CC"


def test_status():
    with expected_protocol(SMC100PP, [("1TS", "1TS000233")]) as inst:
        error, state = inst.status
        assert error == SMC100PositionerError.POSITIVE_END_OF_RUN
        assert state == SMC100StateCode.READY_FROM_MOVING


def test_state():
    with expected_protocol(SMC100PP, [("1TS", "1TS00000A")]) as inst:
        state = inst.state
        assert state == SMC100StateCode.NOT_REFERENCED_FROM_RESET
        assert state.controller_state == SMC100ControllerState.NOT_REFERENCED


def test_positioner_error():
    with expected_protocol(SMC100PP, [("1TS", "1TS00203D")]) as inst:
        assert inst.positioner_error == SMC100PositionerError.FOLLOWING_ERROR


@pytest.mark.parametrize("code", SMC100StateCode)
def test_every_state_code_has_controller_state(code):
    assert isinstance(code.controller_state, SMC100ControllerState)


def test_position_getter():
    with expected_protocol(SMC100PP, [("1TP", "1TP-1.234")]) as inst:
        assert inst.position == -1.234


@pytest.mark.parametrize("value, command", ((45, "1PA45"), (123.45678, "1PA123.45678")))
def test_position_setter(value, command):
    with expected_protocol(SMC100PP, [(command, None), OK]) as inst:
        inst.position = value


def test_position_setter_error():
    with (
        expected_protocol(SMC100PP, [("1PA500", None), ("1TE", "1TEG")]) as inst,
        pytest.raises(SMC100CommandError, match="Displacement out of limits"),
    ):
        inst.position = 500


def test_setpoint():
    with expected_protocol(SMC100PP, [("1TH", "1TH45")]) as inst:
        assert inst.setpoint == 45


@pytest.mark.parametrize("value, command", ((-2.5, "1PR-2.5"), (-123.45678, "1PR-123.45678")))
def test_move_relative(value, command):
    with expected_protocol(SMC100PP, [(command, None), OK]) as inst:
        inst.move_relative(value)


def test_get_motion_time():
    with expected_protocol(SMC100PP, [("1PT0.5", "1PT0.203")]) as inst:
        assert inst.get_motion_time(-0.5) == 0.203


def test_stop():
    with expected_protocol(SMC100PP, [("1ST", None)]) as inst:
        inst.stop()


def test_home():
    with expected_protocol(SMC100PP, [("1OR", None), OK]) as inst:
        inst.home()


def test_home_not_allowed():
    with expected_protocol(SMC100PP, [("1OR", None), ("1TE", "1TEK")]) as inst:
        with pytest.raises(SMC100CommandError) as exc_info:
            inst.home()
        assert exc_info.value.code == "K"


def test_check_errors_unknown_code():
    with expected_protocol(SMC100PP, [("1TE", "1TEZ")]) as inst:
        assert inst.check_errors() == [("Z", "Unknown error")]


def test_wait_until_ready(no_sleep):
    with expected_protocol(
        SMC100PP, [("1TS", "1TS00001E"), ("1TS", "1TS000028"), ("1TS", "1TS000032")]
    ) as inst:
        inst.wait_until_ready()


def test_wait_until_ready_stuck(no_sleep):
    with (
        expected_protocol(SMC100PP, [("1TS", "1TS000028"), ("1TS", "1TS00203D")]) as inst,
        pytest.raises(RuntimeError, match="DISABLE_FROM_MOVING"),
    ):
        inst.wait_until_ready()


def test_wait_until_ready_timeout(no_sleep, monkeypatch):
    # Windows' coarse monotonic clock may not advance between calls, hence a fake one.
    monkeypatch.setattr(
        "pymeasure.instruments.newport.smc100.time.monotonic", iter([0.0, 1.0]).__next__
    )
    with expected_protocol(SMC100PP, [("1TS", "1TS000028")]) as inst, pytest.raises(TimeoutError):
        inst.wait_until_ready(timeout=0)


def test_enable():
    with expected_protocol(SMC100PP, [("1MM1", None), OK]) as inst:
        inst.enable()


def test_disable():
    with expected_protocol(SMC100PP, [("1MM0", None), OK]) as inst:
        inst.disable()


def test_reset_without_wait():
    with expected_protocol(SMC100PP, [("1RS", None)]) as inst:
        inst.reset(wait=False)


def test_reset(no_sleep):
    with expected_protocol(SMC100PP, [("1RS", None)]) as inst:
        inst.reset()
        assert isinstance(inst.adapter, ProtocolAdapter)
        assert inst.adapter.connection.flush.called


def test_enter_configuration():
    with expected_protocol(SMC100PP, [("1PW1", None), OK]) as inst:
        inst.enter_configuration()


def test_exit_configuration(no_sleep):
    with expected_protocol(
        SMC100PP, [("1PW0", None), ("1TS", "1TS000014"), ("1TS", "1TS00000C")]
    ) as inst:
        inst.exit_configuration()


@pytest.mark.parametrize(
    "prop, command, value, reply",
    (
        ("velocity", "VA", 8, "8"),
        ("acceleration", "AC", 80, "80"),
        ("jerk_time", "JR", 0.04, "0.04"),
        ("software_limit_negative", "SL", -170, "-170"),
        ("software_limit_positive", "SR", 170, "170"),
        ("backlash", "BA", 0.1, "0.1"),
        ("peak_current_limit", "QIL", 1, "1"),
        ("home_search_type", "HT", 2, "2"),
        ("home_velocity", "OH", 8, "8"),
        ("home_timeout", "OT", 93.5, "93.5"),
    ),
)
@pytest.mark.parametrize("cls", (SMC100, SMC100PP, SMC100CC))
def test_common_controls(cls, prop, command, value, reply):
    with expected_protocol(
        cls, [(f"1{command}{reply}", None), OK, (f"1{command}?", f"1{command}{reply}")]
    ) as inst:
        setattr(inst, prop, value)
        assert getattr(inst, prop) == value


@pytest.mark.parametrize(
    "prop, value",
    (
        ("velocity", 0),
        ("jerk_time", 0),
        ("software_limit_negative", 1),
        ("software_limit_positive", -1),
        ("home_search_type", 5),
        ("home_timeout", 0),
    ),
)
def test_common_controls_invalid(prop, value):
    with expected_protocol(SMC100PP, []) as inst, pytest.raises(ValueError):
        setattr(inst, prop, value)


@pytest.mark.parametrize(
    "prop, command, value, reply",
    (
        ("base_velocity", "VB", 2, "2"),
        ("micro_step_factor", "FRM", 100, "100"),
    ),
)
def test_pp_controls(prop, command, value, reply):
    with expected_protocol(
        SMC100PP, [(f"1{command}{reply}", None), OK, (f"1{command}?", f"1{command}{reply}")]
    ) as inst:
        setattr(inst, prop, value)
        assert getattr(inst, prop) == value


@pytest.mark.parametrize(
    "prop, command, value, reply",
    (
        ("proportional_gain", "KP", 426.27, "426.27"),
        ("integral_gain", "KI", 24462.9, "24462.9"),
        ("derivative_gain", "KD", 1.66992, "1.66992"),
        ("friction_compensation", "FF", 0, "0"),
        ("closed_loop_enabled", "SC", True, "1"),
        ("closed_loop_enabled", "SC", False, "0"),
    ),
)
def test_cc_controls(prop, command, value, reply):
    with expected_protocol(
        SMC100CC, [(f"1{command}{reply}", None), OK, (f"1{command}?", f"1{command}{reply}")]
    ) as inst:
        setattr(inst, prop, value)
        assert getattr(inst, prop) == value
