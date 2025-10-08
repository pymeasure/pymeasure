import pytest
import numpy as np

from pymeasure.instruments.exfo.ctp10 import CTP10
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        CTP10,
        [],
    ):
        pass  # Verify the expected communication.


def test_start_wavelength_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAV:STOP 1550.0NM", None)],
    ) as inst:
        inst.start_wavelength_nm = 1550.0


def test_start_wavelength_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAV:STAR?", b"1.55000000E-006,NM\r\n")],
    ) as inst:
        assert inst.start_wavelength_nm == 1550.0


def test_stop_wavelength_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAV:STOP 1580.0NM", None)],
    ) as inst:
        inst.stop_wavelength_nm = 1580.0


def test_stop_wavelength_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAV:STOP?", b"1.58000000E-006,NM\r\n")],
    ) as inst:
        assert inst.stop_wavelength_nm == 1580.0


def test_resolution_pm_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAV:SAMP 10PM", None)],
    ) as inst:
        inst.resolution_pm = 10


def test_resolution_pm_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAV:SAMP?", b"1.00000000E-011,PM\r\n")],
    ) as inst:
        assert inst.resolution_pm == 10


def test_sweep_speed_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:SPE 50", None)],
    ) as inst:
        inst.sweep_speed_nmps = 50


def test_sweep_speed_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:SPE?", b"5.0\r\n")],
    ) as inst:
        assert inst.sweep_speed_nmps == 50


def test_laser_power_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:POW 5.0DBM", None)],
    ) as inst:
        inst.laser_power_dbm = 5.0


def test_laser_power_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:POW?", b"5.00000000E+000,DBM\r\n")],
    ) as inst:
        assert inst.laser_power_dbm == 5.0


def test_condition_register():
    with expected_protocol(
        CTP10,
        [(b":STAT:OPER:COND?", b"0\r\n")],
    ) as inst:
        assert inst.condition_register == 0


def test_initiate_sweep():
    with expected_protocol(
        CTP10,
        [
            (b":INIT:STAB ON", None),
            (b":INIT:SMOD SING", None),
            (b":INIT", None),
        ],
    ) as inst:
        inst.initiate_sweep()


def test_query_error():
    with expected_protocol(
        CTP10,
        [(b":SYST:ERR?", b"0,No error\r\n")],
    ) as inst:
        assert inst.query_error() == 0


def test_clear_errors():
    with expected_protocol(
        CTP10,
        [
            (b"*CLS", None),
            (b":SYST:ERR?", b"0,No error\r\n"),
        ],
    ) as inst:
        assert inst.clear_errors() == 0


def test_get_trace_length():
    with expected_protocol(
        CTP10,
        [(b":TRAC:SENS4:CHAN1:TYPE1:DATA:LENG?", b"6001\r\n")],
    ) as inst:
        assert inst.get_trace_length(channel=1) == 6001


def test_get_trace_resolution_pm():
    with expected_protocol(
        CTP10,
        [(b":TRAC:SENS4:CHAN1:TYPE1:DATA:SAMP?", b"1.00000000E-011\r\n")],
    ) as inst:
        assert inst.get_trace_resolution_pm(channel=1) == 10.0


def test_get_trace_start_wavelength_nm():
    with expected_protocol(
        CTP10,
        [(b":TRAC:SENS4:CHAN1:TYPE1:DATA:STAR?", b"1.55000000E-006\r\n")],
    ) as inst:
        assert inst.get_trace_start_wavelength_nm(channel=1) == 1550.0


def test_create_reference():
    with expected_protocol(
        CTP10,
        [
            (b":REF:SENS4:CHAN1:INIT", None),
            (b":STAT:OPER:COND?", b"0\r\n"),
            (b":SYST:ERR?", b"0,No error\r\n"),
        ],
    ) as inst:
        assert inst.create_reference(channel=1) == 0


def test_get_power():
    with expected_protocol(
        CTP10,
        [(b":CTP:SENS4:CHAN1:POW?", b"-5.25,DBM\r\n")],
    ) as inst:
        assert inst.get_power(channel=1) == "-5.25,DBM"


def test_id():
    with expected_protocol(
        CTP10,
        [(b"*IDN?", b"EXFO,CTP10,12345,1.0.0\r\n")],
    ) as inst:
        assert inst.id == "EXFO,CTP10,12345,1.0.0"


def test_clear():
    with expected_protocol(CTP10, [(b"*CLS", None)]) as inst:
        inst.clear()


def test_reset():
    with expected_protocol(
        CTP10,
        [(b"*RST", None)],
    ) as inst:
        inst.reset()
