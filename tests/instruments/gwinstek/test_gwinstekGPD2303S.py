import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.gwinstek.gwinstekGPD2303S import GWInstekGPD230S


def test_init():
    with expected_protocol(
        GWInstekGPD230S,
        [],
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"IOUT1?", b"0.000A\r\n")], 0.0),
        ([(b"IOUT1?", b"0.000A\r\n")], 0.0),
        ([(b"IOUT1?", b"0.000A\r\n")], 0.0),
    ),
)
def test_channel_1_current_getter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        assert inst.channel_1.current == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"ISET1:1", None)], 1),
        ([(b"ISET1:1", None)], 1),
        ([(b"ISET1:1", None)], 1),
    ),
)
def test_channel_1_current_limit_setter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        inst.channel_1.current_limit = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"ISET1?", b"1.000A\r\n")], 1.0),
        ([(b"ISET1?", b"1.000A\r\n")], 1.0),
        ([(b"ISET1?", b"1.000A\r\n")], 1.0),
    ),
)
def test_channel_1_current_limit_getter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        assert inst.channel_1.current_limit == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"VOUT1?", b"5.001V\r\n")], 5.001),
        ([(b"VOUT1?", b"5.001V\r\n")], 5.001),
        ([(b"VOUT1?", b"5.001V\r\n")], 5.001),
    ),
)
def test_channel_1_voltage_getter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        assert inst.channel_1.voltage == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"VSET1:5", None)], 5),
        ([(b"VSET1:5", None)], 5),
        ([(b"VSET1:5", None)], 5),
    ),
)
def test_channel_1_voltage_limit_setter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        inst.channel_1.voltage_limit = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"VSET1?", b"5.000V\r\n")], 5.0),
        ([(b"VSET1?", b"5.000V\r\n")], 5.0),
        ([(b"VSET1?", b"5.000V\r\n")], 5.0),
        ([(b"VSET1?", b"5.000V\r\n")], 5.0),
    ),
)
def test_channel_1_voltage_limit_getter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        assert inst.channel_1.voltage_limit == value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b"OUT1", None)], 1),
        ([(b"OUT1", None)], 1),
        ([(b"OUT1", None)], 1),
    ),
)
def test_output_enabled_setter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        inst.output_enabled = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        (
            [(b"STATUS?", b"10101110\r\n")],
            {
                "raw": "0b10101110",
                "CH1": "CV",
                "CH2": "CC",
                "TRACKING": "Parallel",
                "BEEP": "On",
                "OUTPUT": "On",
                "BAUD": 9600,
            },
        ),
        (
            [(b"STATUS?", b"10101110\r\n")],
            {
                "raw": "0b10101110",
                "CH1": "CV",
                "CH2": "CC",
                "TRACKING": "Parallel",
                "BEEP": "On",
                "OUTPUT": "On",
                "BAUD": 9600,
            },
        ),
        (
            [(b"STATUS?", b"10101110\r\n")],
            {
                "raw": "0b10101110",
                "CH1": "CV",
                "CH2": "CC",
                "TRACKING": "Parallel",
                "BEEP": "On",
                "OUTPUT": "On",
                "BAUD": 9600,
            },
        ),
        (
            [(b"STATUS?", b"10101110\r\n")],
            {
                "raw": "0b10101110",
                "CH1": "CV",
                "CH2": "CC",
                "TRACKING": "Parallel",
                "BEEP": "On",
                "OUTPUT": "On",
                "BAUD": 9600,
            },
        ),
        (
            [(b"STATUS?", b"10101110\r\n")],
            {
                "raw": "0b10101110",
                "CH1": "CV",
                "CH2": "CC",
                "TRACKING": "Parallel",
                "BEEP": "On",
                "OUTPUT": "On",
                "BAUD": 9600,
            },
        ),
        (
            [(b"STATUS?", b"10101110\r\n")],
            {
                "raw": "0b10101110",
                "CH1": "CV",
                "CH2": "CC",
                "TRACKING": "Parallel",
                "BEEP": "On",
                "OUTPUT": "On",
                "BAUD": 9600,
            },
        ),
    ),
)
def test_status_getter(comm_pairs, value):
    with expected_protocol(
        GWInstekGPD230S,
        comm_pairs,
    ) as inst:
        assert inst.status == value
