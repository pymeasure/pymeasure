#!/usr/bin/env python
"""
Unit tests for the HCP TC038D
"""

# IMPORTS #####################################################################


import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.hcp import TC038D


def test_write_multiple():
    # Communication from manual.
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x0A\x00\x04\x08\x00\x00\x03\xE8\xFF\xFF\xFC\x18\x8D\xE9",
          b"\x01\x10\x01\x0A\x00\x04\xE0\x34")]
    ) as inst:
        inst.writeMultiple(0x010A, [1000, -1000])


def test_write_multiple_CRC_error():
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x06\x00\x02\x04\x00\x00\x01A\xbf\xb5",
          b"\x01\x10\x01\x06\x00\x02\x01\x02")],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.setpoint = 32.1


def test_write_multiple_wrong_values():
    with expected_protocol(
        TC038D, []
    ) as inst:
        with pytest.raises(ValueError):
            inst.writeMultiple(0x010A, 5.5)


def test_write_multiple_Value_error():
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x06\x00\x02\x04\x00\x00\x01A\xbf\xb5",
          b"\x01\x90\x02\x06\x00")],
    ) as inst:
        with pytest.raises(ValueError) as exc:
            inst.setpoint = 32.1
            assert str(exc) == "Wrong start address"


def test_read_CRC_error():
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
          b"\x01\x03\x04\x00\x00\x03\xE8\x01\x02")],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.temperature


def test_read_address_error():
    with expected_protocol(
            TC038D,
            [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
              b"\x01\x83\x02\01\02")],
    ) as inst:
        with pytest.raises(ValueError):
            inst.temperature


def test_read_elements_error():
    with expected_protocol(
            TC038D,
            [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
              b"\x01\x83\x03\01\02")],
    ) as inst:
        with pytest.raises(ValueError):
            inst.temperature


def test_read_any_error():
    with expected_protocol(
            TC038D,
            [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
              b"\x01\x43\x05\01\02")],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.temperature


def test_setpoint():
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x01\x06\x00\x02\x25\xf6",
          b"\x01\x03\x04\x00\x00\x00\x99:Y")],
    ) as inst:
        assert inst.setpoint == 15.3


def test_setpoint_setter():
    with expected_protocol(
        TC038D,
        [(b"\x01\x10\x01\x06\x00\x02\x04\x00\x00\x01A\xbf\xb5",
          b"\x01\x10\x01\x06\x00\x02\xa0\x35")],
    ) as inst:
        inst.setpoint = 32.1


def test_temperature():
    # Communication from manual.
    # Tests readRegister as well.
    with expected_protocol(
        TC038D,
        [(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
         b"\x01\x03\x04\x00\x00\x03\xE8\xFA\x8D")],
    ) as inst:
        assert inst.temperature == 100
