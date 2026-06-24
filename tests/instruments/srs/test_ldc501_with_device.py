#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.errors import Error
from pymeasure.instruments.srs import LDC500Series


@pytest.fixture(scope="module")
def ldc501(connected_device_address):
    instr = LDC500Series(connected_device_address)
    instr.reset()
    instr.check_errors()
    instr.ld.current_range = "LOW"
    return instr


# --- ld current ---


def test_ld_current_limit_no_error(ldc501):
    ldc501.ld.current_limit = 100
    assert ldc501.ld.current_limit == 100


def test_ld_current_limit_out_range(ldc501):
    with pytest.raises(Error):
        ldc501.ld.current_limit = 300


def test_ld_current_setpoint_no_error(ldc501):
    ldc501.ld.current_limit = 100
    ldc501.ld.current_setpoint = 25
    assert ldc501.ld.current_setpoint == 25


def test_ld_current_setpoint_out_range(ldc501):
    ldc501.ld.current_limit = 100
    with pytest.raises(Error):
        ldc501.ld.current_setpoint = 101


# --- tec current ---


def test_tec_current_setpoint_no_error(ldc501):
    ldc501.tec.current_limit = 1
    ldc501.tec.current_setpoint = 0.5
    assert ldc501.tec.current_setpoint == 0.5


def test_tec_current_setpoint_out_range(ldc501):
    ldc501.tec.current_limit = 1
    with pytest.raises(Error):
        ldc501.tec.current_setpoint = 1.1


# --- tec temperature ---


def test_tec_temperature_limits_no_error(ldc501):
    ldc501.tec.temperature_limits = (25, 75)
    assert ldc501.tec.temperature_limits == (25, 75)


def test_tec_temperature_low_limit_out_range(ldc501):
    with pytest.raises(Error):
        ldc501.tec.temperature_low_limit = -300


def test_tec_temperature_high_limit_out_range(ldc501):
    with pytest.raises(Error):
        ldc501.tec.temperature_high_limit = 300


def test_tec_temperature_setpoint_no_error(ldc501):
    ldc501.tec.temperature_limits = (25, 75)
    ldc501.tec.temperature_setpoint = 55
    assert ldc501.tec.temperature_setpoint == 55


def test_tec_temperature_setpoint_out_range(ldc501):
    ldc501.tec.temperature_limits = (25, 75)
    with pytest.raises(Error):
        ldc501.tec.temperature_setpoint = 100
