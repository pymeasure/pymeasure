import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol import DG800


def test_init():
    with expected_protocol(
            DG800,
            [],
    ):
        pass  # Verify the expected communication.


def test_channel_1_dc_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:DC 1,1,1.000000', None)],
    ) as inst:
        inst.channel_1.dc = 1


def test_channel_1_duty_cycle_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:PULS:DCYC 0.100000', None)],
    ) as inst:
        inst.channel_1.duty_cycle = 0.1


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':SOUR1:PULS:DCYC?', b'1.000000E-01\n')],
     0.1),
    ([(b':SOUR1:PULS:DCYC?', b'5.000000E-01\n')],
     0.5),
    ([(b':SOUR1:PULS:DCYC?', b'5.000000E-01\n')],
     0.5),
))
def test_channel_1_duty_cycle_getter(comm_pairs, value):
    with expected_protocol(
            DG800,
            comm_pairs,
    ) as inst:
        assert inst.channel_1.duty_cycle == value


def test_channel_1_high_impedance_setter():
    with expected_protocol(
            DG800,
            [(b':OUTP1:IMP INF', None)],
    ) as inst:
        inst.channel_1.high_impedance = True


def test_channel_1_load_setter():
    with expected_protocol(
            DG800,
            [(b':OUTP1:LOAD 50.000000', None)],
    ) as inst:
        inst.channel_1.load = 50


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':OUTP1:LOAD?', b'5.000000E+01\n')],
     50.0),
    ([(b':OUTP1:LOAD?', b'9.900000E+37\n')],
     9.9e+37),
))
def test_channel_1_load_getter(comm_pairs, value):
    with expected_protocol(
            DG800,
            comm_pairs,
    ) as inst:
        assert inst.channel_1.load == value


def test_channel_1_noise_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:NOIS 2.000000,0.000000', None)],
    ) as inst:
        inst.channel_1.noise = (2, 0)


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':OUTP1 OFF', None)],
     False),
    ([(b':OUTP1 ON', None)],
     True),
))
def test_channel_1_output_enabled_setter(comm_pairs, value):
    with expected_protocol(
            DG800,
            comm_pairs,
    ) as inst:
        inst.channel_1.output_enabled = value


def test_channel_1_output_enabled_getter():
    with expected_protocol(
            DG800,
            [(b':OUTP1?', b'OFF\n')],
    ) as inst:
        assert inst.channel_1.output_enabled is False


def test_channel_1_pulse_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:PULS 50.000000,1.000000,0.000000,0.000000', None)],
    ) as inst:
        inst.channel_1.pulse = (50, 1, 0, 0)


def test_channel_1_pulse_width_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:PULS:WIDT 0.000100', None)],
    ) as inst:
        inst.channel_1.pulse_width = 0.0001


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':SOUR1:PULS:WIDT?', b'2.000000E-05\n')],
     2e-05),
    ([(b':SOUR1:PULS:WIDT?', b'1.000000E-04\n')],
     0.0001),
))
def test_channel_1_pulse_width_getter(comm_pairs, value):
    with expected_protocol(
            DG800,
            comm_pairs,
    ) as inst:
        assert inst.channel_1.pulse_width == value


def test_channel_1_sine_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:SIN 500.000000,1.000000,0.000000,0.000000', None)],
    ) as inst:
        inst.channel_1.sine = (500, 1, 0, 0)


def test_channel_1_square_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:SQU 500.000000,1.000000,0.000000,0.000000', None)],
    ) as inst:
        inst.channel_1.square = (500, 1, 0, 0)


def test_channel_1_sync_enabled_setter():
    with expected_protocol(
            DG800,
            [(b':OUTP1:SYNC ON', None)],
    ) as inst:
        inst.channel_1.sync_enabled = True


def test_channel_1_triangle_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:RAMP 500.000000,1.000000,0.000000,0.000000', None)],
    ) as inst:
        inst.channel_1.triangle = (500, 1, 0, 0)


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':SOUR1:APPL?', b'"SIN,5.000000E+02,1.000000E+00,0.000000E+00,0.000000E+00"\n')],
     ['"SIN', 500.0, 1.0, 0.0, '0.000000E+00"']),
    ([(b':SOUR1:APPL?', b'"SQU,5.000000E+02,1.000000E+00,0.000000E+00,0.000000E+00"\n')],
     ['"SQU', 500.0, 1.0, 0.0, '0.000000E+00"']),
    ([(b':SOUR1:APPL?', b'"RAMP,5.000000E+02,1.000000E+00,0.000000E+00,0.000000E+00"\n')],
     ['"RAMP', 500.0, 1.0, 0.0, '0.000000E+00"']),
    ([(b':SOUR1:APPL?', b'"NOISE,DEF,2.000000E+00,0.000000E+00,DEF"\n')],
     ['"NOISE', 'DEF', 2.0, 0.0, 'DEF"']),
    ([(b':SOUR1:APPL?', b'"DC,DEF,DEF,1.000000E+00"\n')],
     ['"DC', 'DEF', 'DEF', '1.000000E+00"']),
    ([(b':SOUR1:APPL?', b'"PULSE,5.000000E+01,1.000000E+00,0.000000E+00,0.000000E+00"\n')],
     ['"PULSE', 50.0, 1.0, 0.0, '0.000000E+00"']),
))
def test_channel_1_waveform_getter(comm_pairs, value):
    with expected_protocol(
            DG800,
            comm_pairs,
    ) as inst:
        assert inst.channel_1.waveform == value
