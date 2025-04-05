import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.keysight.keysightE3642A import KeysightE3642A


def test_init():
    with expected_protocol(
        KeysightE3642A,
        [],
    ):
        pass  # Verify the expected communication.


def test_current_limit_setter():
    with expected_protocol(
        KeysightE3642A,
        [(b"CURR 2.670000", None)],
    ) as inst:
        inst.current_limit = 2.67


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"CURR?", None), (None, b"+2.67000000E+00\n")], 2.67),
        ([(b"CURR?", None), (None, b"+5.00000000E+00\n")], 5.0),
    ),
)
def test_current_limit_getter(comm_pairs, value):
    with expected_protocol(
        KeysightE3642A,
        comm_pairs,
    ) as inst:
        assert inst.current_limit == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"OUTPUT:STATE 0", None)], False),
        ([(b"OUTPUT:STATE 1", None)], True),
    ),
)
def test_output_enabled_setter(comm_pairs, value):
    with expected_protocol(
        KeysightE3642A,
        comm_pairs,
    ) as inst:
        inst.output_enabled = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"OUTPUT:STATE?", None), (None, b"0\n")], False),
        ([(b"OUTPUT:STATE?", None), (None, b"1\n")], True),
    ),
)
def test_output_enabled_getter(comm_pairs, value):
    with expected_protocol(
        KeysightE3642A,
        comm_pairs,
    ) as inst:
        assert inst.output_enabled == value


def test_voltage_setpoint_setter():
    with expected_protocol(
        KeysightE3642A,
        [(b"VOLT 5.310000", None)],
    ) as inst:
        inst.voltage_setpoint = 5.31


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"VOLT?", None), (None, b"+5.31000000E+00\n")], 5.31),
        ([(b"VOLT?", None), (None, b"+8.00000000E+00\n")], 8.0),
    ),
)
def test_voltage_setpoint_getter(comm_pairs, value):
    with expected_protocol(
        KeysightE3642A,
        comm_pairs,
    ) as inst:
        assert inst.voltage_setpoint == value


def test_apply():
    with expected_protocol(
        KeysightE3642A,
        [(b"VOLT 8.000000", None), (b"CURR 5.000000", None)],
    ) as inst:
        assert inst.apply(**{"voltage_setpoint": 8.0, "current_limit": 5.0}) is None
