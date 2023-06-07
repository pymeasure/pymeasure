import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.ametek import Ametek7270


def test_init():
    with expected_protocol(
            Ametek7270,
            [],
    ):
        pass  # Verify the expected communication.


def test_sensitivity_getter():
    with expected_protocol(
            Ametek7270,
            [(b'SEN', b'27\n')],
    ) as inst:
        assert inst.sensitivity == 1.0


def test_slope_getter():
    with expected_protocol(
            Ametek7270,
            [(b'SLOPE', b'1\n')],
    ) as inst:
        assert inst.slope == 12


def test_time_constant_getter():
    with expected_protocol(
            Ametek7270,
            [(b'TC', b'30\n')],
    ) as inst:
        assert inst.time_constant == 100000.0


def test_x_getter():
    with expected_protocol(
            Ametek7270,
            [(b'X.', b'0.0E+00\n')],
    ) as inst:
        assert inst.x == 0.0


def test_y_getter():
    with expected_protocol(
            Ametek7270,
            [(b'Y.', b'0.0E+00\n')],
    ) as inst:
        assert inst.y == 0.0


def test_xy_getter():
    with expected_protocol(
            Ametek7270,
            [(b'XY.', b'0.0E+00,0.0E+00\n')],
    ) as inst:
        assert inst.xy == [0.0, 0.0]


def test_mag_getter():
    with expected_protocol(
            Ametek7270,
            [(b'MAG.', b'0.0E+00\n')],
    ) as inst:
        assert inst.mag == 0.0


def test_theta_getter():
    with expected_protocol(
            Ametek7270,
            [(b'PHA.', b'-1.8E+02\n')],
    ) as inst:
        assert inst.theta == -180.0


@pytest.mark.parametrize("method, command", [('x1', 'X1.'),
                                             ('y1', 'Y1.'),
                                             ('x2', 'X2.'),
                                             ('y2', 'Y2.')])
def test_failing_properties(method, command):
    """in standard single reference mode, these tests should raise a ValueError"""
    with pytest.raises(ValueError):
        with expected_protocol(
                Ametek7270,
                [(f'{command}'.encode(), b'\n')]
        ) as inst:
            getattr(inst, method) == 0.0


def test_harmonic_getter():
    with expected_protocol(
            Ametek7270,
            [(b'REFN', b'7\n')],
    ) as inst:
        assert inst.harmonic == 7


def test_phase_getter():
    with expected_protocol(
            Ametek7270,
            [(b'REFP.', b'2.5E+02\n')],
    ) as inst:
        assert inst.phase == 250.0


def test_voltage_getter():
    with expected_protocol(
            Ametek7270,
            [(b'OA.', b'0.0E+00\n')],
    ) as inst:
        assert inst.voltage == 0.0


def test_frequency_getter():
    with expected_protocol(
            Ametek7270,
            [(b'OF.', b'1.2E+04\n')],
    ) as inst:
        assert inst.frequency == 12000.0


def test_dac1_getter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 1', b'7.0E+00\n')],
    ) as inst:
        assert inst.dac1 == 7.0


def test_dac2_getter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 2', b'-7.0E+00\n')],
    ) as inst:
        assert inst.dac2 == -7.0


def test_dac3_getter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 3', b'2.6E+00\n')],
    ) as inst:
        assert inst.dac3 == 2.6


def test_dac4_getter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 4', b'5.5E+00\n')],
    ) as inst:
        assert inst.dac4 == 5.5


def test_adc1_getter():
    with expected_protocol(
            Ametek7270,
            [(b'ADC. 1', b'0.0E+00\n')],
    ) as inst:
        assert inst.adc1 == 0.0


def test_adc2_getter():
    with expected_protocol(
            Ametek7270,
            [(b'ADC. 2', b'0.0E+00\n')],
    ) as inst:
        assert inst.adc2 == 0.0


def test_adc3_getter():
    with expected_protocol(
            Ametek7270,
            [(b'ADC. 3', b'-1.6E-01\n')],
    ) as inst:
        assert inst.adc3 == -0.16


def test_adc4_getter():
    with expected_protocol(
            Ametek7270,
            [(b'ADC. 4', b'-1.64E-01\n')],
    ) as inst:
        assert inst.adc4 == -0.164


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SEN 0', b'')],
     0.0),
    ([(b'SEN 1', b'')],
     2e-09),
    ([(b'SEN 2', b'')],
     5e-09),
    ([(b'SEN 3', b'')],
     1e-08),
    ([(b'SEN 4', b'')],
     2e-08),
    ([(b'SEN 5', b'')],
     5e-08),
    ([(b'SEN 6', b'')],
     1e-07),
    ([(b'SEN 7', b'')],
     2e-07),
    ([(b'SEN 8', b'')],
     5e-07),
    ([(b'SEN 9', b'')],
     1e-06),
    ([(b'SEN 10', b'')],
     2e-06),
    ([(b'SEN 11', b'')],
     5e-06),
    ([(b'SEN 12', b'')],
     1e-05),
    ([(b'SEN 13', b'')],
     2e-05),
    ([(b'SEN 14', b'')],
     5e-05),
    ([(b'SEN 15', b'')],
     0.0001),
    ([(b'SEN 16', b'')],
     0.0002),
    ([(b'SEN 17', b'')],
     0.0005),
    ([(b'SEN 18', b'')],
     0.001),
    ([(b'SEN 19', b'')],
     0.002),
    ([(b'SEN 20', b'')],
     0.005),
    ([(b'SEN 21', b'')],
     0.01),
    ([(b'SEN 22', b'')],
     0.02),
    ([(b'SEN 23', b'')],
     0.05),
    ([(b'SEN 24', b'')],
     0.1),
    ([(b'SEN 25', b'')],
     0.2),
    ([(b'SEN 26', b'')],
     0.5),
    ([(b'SEN 27', b'')],
     1.0),
))
def test_sensitivity_setter(comm_pairs, value):
    with expected_protocol(
            Ametek7270,
            comm_pairs,
    ) as inst:
        inst.sensitivity = value


def test_slope_setter():
    with expected_protocol(
            Ametek7270,
            [(b'SLOPE 1', b'')],
    ) as inst:
        inst.slope = 12


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'TC 0', b'')],
     1e-05),
    ([(b'TC 1', b'')],
     2e-05),
    ([(b'TC 2', b'')],
     5e-05),
    ([(b'TC 3', b'')],
     0.0001),
    ([(b'TC 4', b'')],
     0.0002),
    ([(b'TC 5', b'')],
     0.0005),
    ([(b'TC 6', b'')],
     0.001),
    ([(b'TC 7', b'')],
     0.002),
    ([(b'TC 8', b'')],
     0.005),
    ([(b'TC 9', b'')],
     0.01),
    ([(b'TC 10', b'')],
     0.02),
    ([(b'TC 11', b'')],
     0.05),
    ([(b'TC 12', b'')],
     0.1),
    ([(b'TC 13', b'')],
     0.2),
    ([(b'TC 14', b'')],
     0.5),
    ([(b'TC 15', b'')],
     1.0),
    ([(b'TC 16', b'')],
     2.0),
    ([(b'TC 17', b'')],
     5.0),
    ([(b'TC 18', b'')],
     10.0),
    ([(b'TC 19', b'')],
     20.0),
    ([(b'TC 20', b'')],
     50.0),
    ([(b'TC 21', b'')],
     100.0),
    ([(b'TC 22', b'')],
     200.0),
    ([(b'TC 23', b'')],
     500.0),
    ([(b'TC 24', b'')],
     1000.0),
    ([(b'TC 25', b'')],
     2000.0),
    ([(b'TC 26', b'')],
     5000.0),
    ([(b'TC 27', b'')],
     10000.0),
    ([(b'TC 28', b'')],
     20000.0),
    ([(b'TC 29', b'')],
     50000.0),
    ([(b'TC 30', b'')],
     100000.0),
))
def test_time_constant_setter(comm_pairs, value):
    with expected_protocol(
            Ametek7270,
            comm_pairs,
    ) as inst:
        inst.time_constant = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'REFN 7', b'')],
     7),
    ([(b'REFN 7', b'')],
     7),
    ([(b'REFN 7', b'')],
     7),
    ([(b'REFN 7', b'')],
     7),
    ([(b'REFN 7', b'')],
     7),
    ([(b'REFN 7', b'')],
     7),
))
def test_harmonic_setter(comm_pairs, value):
    with expected_protocol(
            Ametek7270,
            comm_pairs,
    ) as inst:
        inst.harmonic = value


def test_phase_setter():
    with expected_protocol(
            Ametek7270,
            [(b'REFP. 250', b'')],
    ) as inst:
        inst.phase = 250


def test_voltage_setter():
    with expected_protocol(
            Ametek7270,
            [(b'OA. 2.7', b'')],
    ) as inst:
        inst.voltage = 2.7


def test_frequency_setter():
    with expected_protocol(
            Ametek7270,
            [(b'OF. 12000', b'')],
    ) as inst:
        inst.frequency = 12000


def test_dac1_setter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 1 7', b'')],
    ) as inst:
        inst.dac1 = 7


def test_dac2_setter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 2 -7', b'')],
    ) as inst:
        inst.dac2 = -7


def test_dac3_setter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 3 2.6', b'')],
    ) as inst:
        inst.dac3 = 2.6


def test_dac4_setter():
    with expected_protocol(
            Ametek7270,
            [(b'DAC. 4 5.5', b'')],
    ) as inst:
        inst.dac4 = 5.5


@pytest.mark.parametrize("comm_pairs, value", (
    ([],
     True),
    ([],
     False),
))
def test_autogain_setter(comm_pairs, value):
    with expected_protocol(
            Ametek7270,
            comm_pairs,
    ) as inst:
        inst.autogain = value


def test_set_voltage_mode():
    with expected_protocol(
            Ametek7270,
            [(b'IMODE 0', b'')],
    ) as inst:
        assert inst.set_voltage_mode() is None


def test_set_differential_mode():
    with expected_protocol(
            Ametek7270,
            [(b'VMODE 3', b''),
             (b'LF 3 0', b'')],
    ) as inst:
        assert inst.set_differential_mode() is None


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'IMODE 1', b'')],
     (), {'low_noise': False}, None),
    ([(b'IMODE 2', b'')],
     (), {'low_noise': True}, None),
))
def test_set_current_mode(comm_pairs, args, kwargs, value):
    with expected_protocol(
            Ametek7270,
            comm_pairs,
    ) as inst:
        assert inst.set_current_mode(*args, **kwargs) == value


def test_set_channel_A_mode():
    with expected_protocol(
            Ametek7270,
            [(b'VMODE 1', b'')],
    ) as inst:
        assert inst.set_channel_A_mode() is None


def test_id():
    with expected_protocol(
            Ametek7270,
            [(b'ID', b'7270\n'),
             (b'VER', b'2.11\n')],
    ) as inst:
        assert inst.id == '7270/2.11'


def test_shutdown():
    with expected_protocol(
            Ametek7270,
            [(b'OA. 0', b'')],
    ) as inst:
        assert inst.shutdown() is None
