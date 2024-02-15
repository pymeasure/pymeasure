import pytest

from pymeasure.instruments.pendulum import CNT91
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        CNT91,
        [],
    ):
        pass  # Verify the expected communication.


def test_batch_size_getter():
    with expected_protocol(
        CNT91,
        [(b"FORM:SMAX?", b"10000\n")],
    ) as inst:
        assert inst.batch_size == 10000


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"INIT:CONT 1.0", None)], True),
        ([(b"INIT:CONT 0.0", None)], False),
    ),
)
def test_continuous_setter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        inst.continuous = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"INIT:CONT?", b"1\n")], True),
        ([(b"INIT:CONT?", b"0\n")], False),
    ),
)
def test_continuous_getter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        assert inst.continuous == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"ARM:SLOP NEG", None)], "NEG"),
        ([(b"ARM:SLOP POS", None)], "POS"),
    ),
)
def test_external_arming_start_slope_setter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        inst.external_arming_start_slope = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"ARM:SLOP?", b"NEG\n")], "NEG"),
        ([(b"ARM:SLOP?", b"POS\n")], "POS"),
    ),
)
def test_external_arming_start_slope_getter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        assert inst.external_arming_start_slope == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"ARM:SOUR EXT1", None)], "A"),
        ([(b"ARM:SOUR IMM", None)], "IMM"),
    ),
)
def test_external_start_arming_source_setter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        inst.external_start_arming_source = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"ARM:SOUR?", b"EXT1\n")], "A"),
        ([(b"ARM:SOUR?", b"IMM\n")], "IMM"),
    ),
)
def test_external_start_arming_source_getter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        assert inst.external_start_arming_source == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FORM REAL", None)], "REAL"),
        ([(b"FORM ASC", None)], "ASCII"),
    ),
)
def test_format_setter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        inst.format = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FORM?", b"REAL\n")], "REAL"),
        ([(b"FORM?", b"ASC\n")], "ASCII"),
    ),
)
def test_format_getter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        assert inst.format == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b":ACQ:APER 1000", None)], 1000),
        ([(b":ACQ:APER 1", None)], 1),
        ([(b":ACQ:APER 2e-08", None)], 2e-08),
    ),
)
def test_gate_time_setter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        inst.gate_time = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b":ACQ:APER?", b"+1.0000000000000E+03\n")], 1000.0),
        ([(b":ACQ:APER?", b"+1.0000000000000E+00\n")], 1.0),
        ([(b":ACQ:APER?", b"+2.0000000000000E-08\n")], 2e-08),
    ),
)
def test_gate_time_getter(comm_pairs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        assert inst.gate_time == value


def test_buffer_frequency_time_series():
    with expected_protocol(
        CNT91,
        [
            (b"*CLS", None),
            (b"FORM ASC", None),
            (b":CONF:ARR:FREQ:BTB 10,(@1)", None),
            (b"INIT:CONT 0.0", None),
            (b":ACQ:APER 0.1", None),
            (b":INIT", None),
        ],
    ) as inst:
        assert inst.buffer_frequency_time_series(*("A", 10), **{"gate_time": 0.1}) is None


@pytest.mark.parametrize(
    "comm_pairs, args, kwargs, value",
    (
        (
            [
                (b"*OPC?", b"1\n"),
                (
                    b":FETC:ARR? 7",
                    b"+9.999992027E+06,+9.999991980E+06,+9.999992043E+06,+9.999992031E+06,+9.999992042E+06,+9.999992041E+06,+9.999992004E+06\n",  # noqa: E501
                ),
            ],
            (7,),
            {},
            [
                9999992.027,
                9999991.98,
                9999992.043,
                9999992.031,
                9999992.042,
                9999992.041,
                9999992.004,
            ],
        ),
        (
            [
                (b"*OPC?", b"1\n"),
                (b":FETC:ARR? MAX", b"+9.999992030E+06,+9.999992000E+06,+9.999992043E+06\n"),
            ],
            (),
            {},
            [9999992.03, 9999992.0, 9999992.043],
        ),
    ),
)
def test_read_buffer(comm_pairs, args, kwargs, value):
    with expected_protocol(
        CNT91,
        comm_pairs,
    ) as inst:
        assert inst.read_buffer(*args, **kwargs) == value
