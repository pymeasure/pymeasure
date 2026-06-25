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

from pymeasure.test import expected_protocol
from pymeasure.instruments.tdk.tdk_gen40_38 import TDK_Gen40_38


def test_init():
    with expected_protocol(
            TDK_Gen40_38,
            [(b"ADR 6", b"OK")],
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize("volt",
                         (b"10", b"20", b"40"))
def test_voltage_setpoint(volt):
    with expected_protocol(
            TDK_Gen40_38,
            [(b"ADR 6", b"OK"),
             (b"PV " + volt, b"OK"),
             (b"PV?", volt)]
    ) as instr:
        instr.voltage_setpoint = float(volt)
        assert instr.voltage_setpoint == float(volt)


def test_invalid_voltage():
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen40_38,
                [(b"ADR 6", b"OK"),
                 (b"PV 60", b"OK"), ]
        ) as instr:
            instr.voltage_setpoint = 60


def test_invalid_current_setpoint():
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen40_38,
                [(b"ADR 6", b"OK"),
                 (b"PC 50", b"OK"), ]
        ) as instr:
            instr.current_setpoint = 50


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Dynamic range differences: Gen40-38 over_voltage [2, 44], under_voltage [0, 38]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def test_over_voltage_within_range():
    with expected_protocol(
            TDK_Gen40_38,
            [(b"ADR 6", b"OK"),
             (b"OVP 20", b"OK"),
             (b"OVP?", b"20")]
    ) as instr:
        instr.over_voltage = 20
        assert instr.over_voltage == 20


def test_over_voltage_at_upper_bound():
    with expected_protocol(
            TDK_Gen40_38,
            [(b"ADR 6", b"OK"),
             (b"OVP 44", b"OK")]
    ) as instr:
        instr.over_voltage = 44


def test_over_voltage_above_upper_bound_invalid():
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen40_38,
                [(b"ADR 6", b"OK"),
                 (b"OVP 45", b"OK")]
        ) as instr:
            instr.over_voltage = 45


def test_over_voltage_below_lower_bound_invalid():
    # Gen40-38 over_voltage lower bound is 2.
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen40_38,
                [(b"ADR 6", b"OK"),
                 (b"OVP 1", b"OK")]
        ) as instr:
            instr.over_voltage = 1


def test_under_voltage_within_range():
    with expected_protocol(
            TDK_Gen40_38,
            [(b"ADR 6", b"OK"),
             (b"UVL 10", b"OK"),
             (b"UVL?", b"10")]
    ) as instr:
        instr.under_voltage = 10
        assert instr.under_voltage == 10


def test_under_voltage_at_upper_bound():
    with expected_protocol(
            TDK_Gen40_38,
            [(b"ADR 6", b"OK"),
             (b"UVL 38", b"OK")]
    ) as instr:
        instr.under_voltage = 38


def test_under_voltage_above_upper_bound_invalid():
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen40_38,
                [(b"ADR 6", b"OK"),
                 (b"UVL 39", b"OK")]
        ) as instr:
            instr.under_voltage = 39
