"""
Test the instrument class for the Velleman F8090.

This is not an integration test! This is software-only.
"""

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.velleman import VellemanK8090


def test_version():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 71 00 00 00 8B 0F"),
                bytearray.fromhex("04 71 FF 0A 01 81 0F"),
            )
        ],
    ) as inst:
        assert inst.version == (10, 1)


def test_status():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 18 00 00 00 E4 0F"),
                bytearray.fromhex("04 51 01 15 80 15 0F"),
            )
        ],
    ) as inst:
        last_on, curr_on, time_on = inst.status

        assert last_on == [True, False, False, False, False, False, False, False]
        assert curr_on == [True, False, True, False, True, False, False, False]
        assert time_on == [False, False, False, False, False, False, False, True]


def test_switch_on():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 11 05 00 00 E6 0F"),
                None,  # The real device does send a reply
            )
        ],
    ) as inst:
        inst.switch_on = [1, 3]
        # inst.switch_on([1, 3])


def test_switch_off():
    with expected_protocol(
        VellemanK8090,
        [
            (
                bytearray.fromhex("04 12 05 00 00 E5 0F"),
                None,
            )
        ],
    ) as inst:
        inst.switch_off = [1, 3]
