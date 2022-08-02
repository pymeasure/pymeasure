#!/usr/bin/env python
"""
Unit tests for the HCP TC038
"""

import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.hcp import TC038


def test_setpoint():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRDD0120,01\x03", b"\x020101OK00C8\x03")]
    ) as inst:
        assert inst.setpoint == 20


def test_setpoint_setter():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")]
    ) as inst:
        inst.setpoint = 20


def test_temperature():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")]
    ) as inst:
        assert 20 == inst.temperature


def test_monitored():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010WRM\x03", b"\x020101OK00C8\x03")]
    ) as inst:
        assert 20 == inst.monitored_value


def test_set_monitored():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")]
    ):
        pass  # Instantiation calls set_monitored_quantity()


def test_set_monitored_wrong_input():
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")]
    ) as inst:
        with pytest.raises(KeyError):
            inst.set_monitored_quantity("temper")


def test_information():
    # Communication from manual.
    with expected_protocol(
        TC038,
        [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03"),
         (b"\x0201010INF6\x03",
          b"\x020101OKUT150333 V01.R001111222233334444\x03")]
    ) as inst:
        value = inst.information
        assert value == "UT150333 V01.R001111222233334444"
