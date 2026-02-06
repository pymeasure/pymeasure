import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.voltcraft import LCR500


def test_init():
    with expected_protocol(
        LCR500,
        [],
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:EQUI ser", None)], True),
        ([(b"FUNC:EQUI pal", None)], False),
    ),
)
def test_equivalent_circuit_serial_enabled_setter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        inst.equivalent_circuit_serial_enabled = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:EQUI?", b"ser")], True),
        ([(b"FUNC:EQUI?", b"pal")], False),
    ),
)
def test_equivalent_circuit_serial_enabled_getter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        assert inst.equivalent_circuit_serial_enabled == value


def test_fetch_getter():
    with expected_protocol(
        LCR500,
        [(b"FETC?", b"+1.56061e-12,-8.62924e+01,100000")],
    ) as inst:
        assert inst.fetch == [1.56061e-12, -86.2924, 100000.0]


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FREQ 100", None)], 100),
        ([(b"FREQ 120", None)], 120),
        ([(b"FREQ 400", None)], 400),
        ([(b"FREQ 1000", None)], 1000),
        ([(b"FREQ 4000", None)], 4000),
        ([(b"FREQ 10000", None)], 10000),
        ([(b"FREQ 40000", None)], 40000),
        ([(b"FREQ 50000", None)], 50000),
        ([(b"FREQ 75000", None)], 75000),
        ([(b"FREQ 100000", None)], 100000),
    ),
)
def test_frequency_setter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        inst.frequency = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FREQ?", b"100")], 100.0),
        ([(b"FREQ?", b"120")], 120.0),
        ([(b"FREQ?", b"400")], 400.0),
        ([(b"FREQ?", b"1000")], 1000.0),
        ([(b"FREQ?", b"4000")], 4000.0),
        ([(b"FREQ?", b"10000")], 10000.0),
        ([(b"FREQ?", b"40000")], 40000.0),
        ([(b"FREQ?", b"50000")], 50000.0),
        ([(b"FREQ?", b"75000")], 75000.0),
        ([(b"FREQ?", b"100000")], 100000.0),
    ),
)
def test_frequency_getter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        assert inst.frequency == value


def test_id_getter():
    with expected_protocol(
        LCR500,
        [(b"*IDN?", b"VOLTCRAFT,LCR-500,CN2502021007224,20250222AM")],
    ) as inst:
        assert inst.id == "VOLTCRAFT,LCR-500,CN2502021007224,20250222AM"


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:LEV 300", None)], 300),
        ([(b"FUNC:LEV 600", None)], 600),
    ),
)
def test_level_setter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        inst.level = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:LEV?", b"300")], 300.0),
        ([(b"FUNC:LEV?", b"600")], 600.0),
    ),
)
def test_level_getter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        assert inst.level == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:IMPA r", None)], "r"),
        ([(b"FUNC:IMPA l", None)], "l"),
        ([(b"FUNC:IMPA c", None)], "c"),
        ([(b"FUNC:IMPA z", None)], "z"),
        ([(b"FUNC:IMPA auto", None)], "auto"),
    ),
)
def test_main_parameter_setter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        inst.main_parameter = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:IMPA?", b"r")], "r"),
        ([(b"FUNC:IMPA?", b"l")], "l"),
        ([(b"FUNC:IMPA?", b"c")], "c"),
        ([(b"FUNC:IMPA?", b"z")], "z"),
        ([(b"FUNC:IMPA?", b"c-auto")], "auto"),
    ),
)
def test_main_parameter_getter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        assert inst.main_parameter == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:RANG auto", None)], "auto"),
        ([(b"FUNC:RANG 10", None)], 10),
        ([(b"FUNC:RANG 100", None)], 100),
        ([(b"FUNC:RANG 1000", None)], 1000),
        ([(b"FUNC:RANG 10000", None)], 10000),
        ([(b"FUNC:RANG 100000", None)], 100000),
    ),
)
def test_measurement_range_setter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        inst.measurement_range = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:RANG?", b"auto")], "auto"),
        ([(b"FUNC:RANG?", b"10")], 10.0),
        ([(b"FUNC:RANG?", b"100")], 100.0),
        ([(b"FUNC:RANG?", b"1000")], 1000.0),
        ([(b"FUNC:RANG?", b"10000")], 10000.0),
        ([(b"FUNC:RANG?", b"100000")], 100000.0),
    ),
)
def test_measurement_range_getter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        assert inst.measurement_range == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:IMPB x", None)], "x"),
        ([(b"FUNC:IMPB q", None)], "q"),
        ([(b"FUNC:IMPB d", None)], "d"),
        ([(b"FUNC:IMPB esr", None)], "esr"),
        ([(b"FUNC:IMPB theta", None)], "theta"),
    ),
)
def test_secondary_parameter_setter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        inst.secondary_parameter = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"FUNC:IMPB?", b"x")], "x"),
        ([(b"FUNC:IMPB?", b"q")], "q"),
        ([(b"FUNC:IMPB?", b"d")], "d"),
        ([(b"FUNC:IMPB?", b"esr")], "esr"),
        ([(b"FUNC:IMPB?", b"theta")], "theta"),
    ),
)
def test_secondary_parameter_getter(comm_pairs, value):
    with expected_protocol(
        LCR500,
        comm_pairs,
    ) as inst:
        assert inst.secondary_parameter == value
