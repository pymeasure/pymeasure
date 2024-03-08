import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.hp import HP33120A


def test_init():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None)],
    ):
        pass  # Verify the expected communication.


def test_amplitude_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'SOUR:VOLT 4', None)],
    ) as inst:
        inst.amplitude = 4


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'SOUR:VOLT?', b'+4.00000E+00')],
     4.0),
))
def test_amplitude_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.amplitude == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'SOUR:VOLT:UNIT?', b'VPP')],
     'Vpp'),
))
def test_amplitude_units_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.amplitude_units == value


def test_burst_count_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'BM:NCYC 500', None)],
    ) as inst:
        inst.burst_count = 500


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:NCYC?', b'+1.00000E+00')],
     1.0),
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:NCYC?', b'+5.00000E+02')],
     500.0),
))
def test_burst_count_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.burst_count == value


def test_burst_enabled_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'BM:STATE 1', None)],
    ) as inst:
        inst.burst_enabled = True


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:STATE?', b'1')],
     True),
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:STATE?', b'0')],
     False),
))
def test_burst_enabled_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.burst_enabled == value


def test_burst_phase_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'BM:PHAS 20', None)],
    ) as inst:
        inst.burst_phase = 20


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:PHAS?', b'+0.00000E+00')],
     0.0),
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:PHAS?', b'+2.00000E+01')],
     20.0),
))
def test_burst_phase_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.burst_phase == value


def test_burst_rate_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'BM:INT:RATE 250', None)],
    ) as inst:
        inst.burst_rate = 250


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:INT:RATE?', b'+1.00000E+02')],
     100.0),
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:INT:RATE?', b'+2.50000E+02')],
     250.0),
))
def test_burst_rate_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.burst_rate == value


def test_burst_source_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'BM:SOURCE INT', None)],
    ) as inst:
        inst.burst_source = 'INT'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'BM:SOURCE?', b'INT')],
     'INT'),
))
def test_burst_source_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.burst_source == value


def test_frequency_setter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'SOUR:FREQ 2000', None)],
    ) as inst:
        inst.frequency = 2000.0


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'SOUR:FREQ?', b'+2.00000000000E+03')],
     2000.0),
    ([(b'SOUR:VOLT:UNIT VPP', None),
      (b'SOUR:FREQ?', b'+2.00000000000E+03')],
     2000.0),
))
def test_frequency_getter(comm_pairs, value):
    with expected_protocol(
            HP33120A,
            comm_pairs,
    ) as inst:
        assert inst.frequency == value


def test_offset_getter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'SOUR:VOLT:OFFS?', b'+0.00000E+00')],
    ) as inst:
        assert inst.offset == 0.0


def test_shape_getter():
    with expected_protocol(
            HP33120A,
            [(b'SOUR:VOLT:UNIT VPP', None),
             (b'SOUR:FUNC:SHAP?', b'SIN')],
    ) as inst:
        assert inst.shape == 'sinusoid'
