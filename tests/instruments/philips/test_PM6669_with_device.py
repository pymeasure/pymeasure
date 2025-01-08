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


@pytest.mark.parametrize("case, expected", FUNCTION_STRINGS)
def test_function_modes(philips_pm6669, case, expected):
    philips_pm6669.measuring_function = case
    assert philips_pm6669.measuring_function == expected


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
    philips_pm6669.freerun_enabled = case
    assert philips_pm6669.freerun_enabled == case
