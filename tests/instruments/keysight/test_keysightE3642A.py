import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.keysight.keysightE3642A import KeysightE3642A


def test_init():
    with expected_protocol(
            KeysightE3642A,
            [],
    ):
        pass  # Verify the expected communication.


def test_current_setter():
    with expected_protocol(
            KeysightE3642A,
            [(b'CURR 2.670000', None)],
    ) as inst:
        inst.current = 2.67


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'CURR?', None),
      (b'++read eoi', b'+2.67000000E+00\n')],
     2.67),
    ([(b'CURR?', None),
      (b'++read eoi', b'+5.00000000E+00\n')],
     5.0),
))
def test_current_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3642A,
            comm_pairs,
    ) as inst:
        assert inst.current == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'OUTPUT:STATE 1', None)],
     True),
    ([(b'OUTPUT:STATE 0', None)],
     False),
))
def test_output_state_enabled_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3642A,
            comm_pairs,
    ) as inst:
        inst.output_state_enabled = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'OUTPUT:STATE?', None),
      (b'++read eoi', b'1\n')],
     True),
    ([(b'OUTPUT:STATE?', None),
      (b'++read eoi', b'0\n')],
     False),
))
def test_output_state_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3642A,
            comm_pairs,
    ) as inst:
        assert inst.output_state_enabled == value


def test_voltage_setter():
    with expected_protocol(
            KeysightE3642A,
            [(b'VOLT 5.310000', None)],
    ) as inst:
        inst.voltage = 5.31


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT?', None),
      (b'++read eoi', b'+5.31000000E+00\n')],
     5.31),
    ([(b'VOLT?', None),
      (b'++read eoi', b'+8.00000000E+00\n')],
     8.0),
))
def test_voltage_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3642A,
            comm_pairs,
    ) as inst:
        assert inst.voltage == value


def test_apply():
    with expected_protocol(
            KeysightE3642A,
            [(b'VOLT 8.000000', None),
             (b'CURR 5.000000', None)],
    ) as inst:
        assert inst.apply(**{'voltage': 8.0, 'current': 5.0}) is None
