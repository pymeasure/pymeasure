#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.philips.PM6669 import PM6669, Functions


FUNCTION_STRINGS = [
    ("FREQ A", Functions.FREQUENCY_A),
    ("PER A", Functions.PER_A),
    ("FREQ B", Functions.FREQUENCY_B),
    ("TOTM A", Functions.TOT_A),
    ("WIDTH A", Functions.WIDTH_A),
]


@pytest.fixture(scope="module")
def philips_pm6669(connected_device_address):
    instr = PM6669(connected_device_address)
    instr.reset_to_defaults()
    return instr


def test_init():
    with expected_protocol(
        PM6669,
        [(b"EOI ON", None), (b"FRUN OFF", None)],
    ):
        pass  # Verify the expected communication.


def test_function():
    with expected_protocol(
        PM6669,
        [
            (b"EOI ON", None),
            (b"FRUN OFF", None),
            (b"FREQ   A", None),
            (b"FNC?", "FREQ   A\n"),
            (b"FREQ   B", None),
            (b"FNC?", "FREQ   B\n"),
        ],
    ) as inst:
        inst.function = Functions.FREQUENCY_A
        assert inst.function == Functions.FREQUENCY_A
        inst.function = Functions.FREQUENCY_B
        assert inst.function == Functions.FREQUENCY_B


def test_measurement_time():
    with expected_protocol(
        PM6669,
        [
            (b"EOI ON", None),
            (b"FRUN OFF", None),
            (b"MTIME 1", None),
            (b"MEAC?", b"MTIME 1.00,FRUN OFF\nTOUT 25.5\n"),
            (b"MTIME 10", None),
            (b"MEAC?", b"MTIME 10.00,FRUN OFF\nTOUT 25.5\n"),
        ],
    ) as inst:
        inst.measurement_time = 1
        assert inst.measurement_time == 1
        inst.measurement_time = 10
        assert inst.measurement_time == 10


@pytest.mark.parametrize("case, expected", FUNCTION_STRINGS)
def test_function_modes(philips_pm6669, case, expected):
    philips_pm6669.function = case
    assert philips_pm6669.function == expected


@pytest.mark.parametrize("case", [0, 0.1, 10, 25.5])
def test_timeout_times(philips_pm6669, case):
    philips_pm6669.measurement_timeout = case
    assert philips_pm6669.measurement_timeout == case


@pytest.mark.parametrize("case", [0.2, 1, 10])
def test_measurement_times(philips_pm6669, case):
    philips_pm6669.measurement_time = case
    assert philips_pm6669.measurement_time == case


@pytest.mark.parametrize("case", [True, False])
def test_freerun(philips_pm6669, case):
    philips_pm6669.freerun = case
    assert philips_pm6669.freerun == case
