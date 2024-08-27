import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol import DG800


def test_init():
    with expected_protocol(
            DG800,
            [],
    ):
        pass  # Verify the expected communication.


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


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':OUTP1 OFF', None)],
     False),
    ([(b':OUTP1 ON', None)],
     True),
))
def test_channel_1_output_status_setter(comm_pairs, value):
    with expected_protocol(
            DG800,
            comm_pairs,
    ) as inst:
        inst.channel_1.output_status = value


def test_channel_1_output_status_getter():
    with expected_protocol(
            DG800,
            [(b':OUTP1?', b'OFF\n')],
    ) as inst:
        assert inst.channel_1.output_status is False


def test_channel_1_sine_setter():
    with expected_protocol(
            DG800,
            [(b':SOUR1:APPL:SIN 500.000000,1.000000,0.000000,0.000000?', None)],
    ) as inst:
        inst.channel_1.sine = (500, 1, 0, 0)
