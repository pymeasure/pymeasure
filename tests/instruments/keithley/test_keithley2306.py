from pymeasure.test import expected_protocol

from pymeasure.instruments.keithley.keithley2306 import Keithley2306


def test_init():
    with expected_protocol(
            Keithley2306,
            [],
            ) as instr:
        pass


def test_nplc():
    with expected_protocol(
            Keithley2306,
            [(b":SENS2:NPLC?", b"1.234")],
            ) as instr:
        assert instr.ch2.nplc == 1.234


def test_nplc_setter():
    with expected_protocol(
            Keithley2306,
            [(b":SENS2:NPLC 1.234", None)],
            ) as instr:
        instr.ch2.nplc = 1.234


def test_relay():
    with expected_protocol(
            Keithley2306,
            [(b":OUTP:REL2?", b"ONE")],
            ) as instr:
        assert instr.relay2.closed is True


def test_relay_setter():
    with expected_protocol(
            Keithley2306,
            [(b":OUTP:REL2 ONE", None)],
            ) as instr:
        instr.relay2.closed = True
