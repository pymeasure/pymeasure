#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
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
