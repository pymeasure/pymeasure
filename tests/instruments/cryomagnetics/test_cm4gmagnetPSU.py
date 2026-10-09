import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.cryomagnetics import Cryomagnetics4G100


def test_init():
    with expected_protocol(
            Cryomagnetics4G100,
            [],
    ):
        pass  # Verify the expected communication.


def test_fast_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RATE? 5', b'0.0290')],
    ) as inst:
        assert inst.fast_rate == 0.029


def test_identity_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'*IDN?', b'ICE Oxford,4G,8423,1.67,324')],
    ) as inst:
        assert inst.identity == ['ICE Oxford', '4G', 8423.0, 1.67, 324.0]


def test_magnet_current_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'UNITS A;IMAG?', b'0.0000A')],
    ) as inst:
        assert inst.magnet_current == 0.0


def test_magnet_name_setter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME BIG YELLOW', None)],
    ) as inst:
        inst.magnet_name = 'BIG YELLOW'


def test_magnet_name_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME?', b'BIG YELLOW')],
    ) as inst:
        assert inst.magnet_name == 'BIG YELLOW'


def test_magnet_voltage_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'VMAG?', b'-0.001V')],
    ) as inst:
        assert inst.magnet_voltage == -0.001


def test_output_current_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'UNITS A;IOUT?', b'0.0000A')],
    ) as inst:
        assert inst.output_current == 0.0


def test_output_voltage_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'VOUT?', b'0.000V')],
    ) as inst:
        assert inst.output_voltage == 0.0


def test_persistent_switch_heater_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'PSHTR?', b'0')],
    ) as inst:
        assert inst.persistent_switch_heater == 'OFF'


def test_range_1_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RATE? 0', b'0.0010')],
    ) as inst:
        assert inst.range_1_rate == 0.001


def test_range_2_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RATE? 1', b'0.0010')],
    ) as inst:
        assert inst.range_2_rate == 0.001


def test_range_3_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RATE? 2', b'0.0010')],
    ) as inst:
        assert inst.range_3_rate == 0.001


def test_range_4_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RATE? 3', b'0.0010')],
    ) as inst:
        assert inst.range_4_rate == 0.001


def test_range_5_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RATE? 4', b'0.0010')],
    ) as inst:
        assert inst.range_5_rate == 0.001


def test_range_boundary_0_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RANGE? 0', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_0 == 1.0


def test_range_boundary_1_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RANGE? 1', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_1 == 1.0


def test_range_boundary_2_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RANGE? 2', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_2 == 1.0


def test_range_boundary_3_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RANGE? 3', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_3 == 1.0


def test_range_boundary_4_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'RANGE? 4', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_4 == 1.0


def test_sweep_lower_limit_setter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'UNITS A;LLIM -0.15', None)],
    ) as inst:
        inst.sweep_lower_limit = -0.15


def test_sweep_lower_limit_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'UNITS A;LLIM?', b'-0.1500A')],
    ) as inst:
        assert inst.sweep_lower_limit == -0.15


def test_sweep_mode_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'SWEEP?', b'Standby')],
    ) as inst:
        assert inst.sweep_mode == 'STANDBY'


def test_sweep_upper_limit_setter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'UNITS A;ULIM 0.15', None)],
    ) as inst:
        inst.sweep_upper_limit = 0.15


def test_sweep_upper_limit_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'UNITS A;ULIM?', b'0.1500A')],
    ) as inst:
        assert inst.sweep_upper_limit == 0.15


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'UNITS G', None)],
     'G'),
    ([(b'UNITS A', None)],
     'A'),
))
def test_units_setter(comm_pairs, value):
    with expected_protocol(
            Cryomagnetics4G100,
            comm_pairs,
    ) as inst:
        inst.units = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'UNITS?', b'kG')],
     'kG'),
    ([(b'UNITS?', b'A')],
     'A'),
))
def test_units_getter(comm_pairs, value):
    with expected_protocol(
            Cryomagnetics4G100,
            comm_pairs,
    ) as inst:
        assert inst.units == value


def test_usb_error_report_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'ERROR?', b'0')],
    ) as inst:
        assert inst.usb_error_report is False


def test_voltage_limit_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'VLIM?', b'5.000V')],
    ) as inst:
        assert inst.voltage_limit == 5.0
