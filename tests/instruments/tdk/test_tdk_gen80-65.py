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
from pymeasure.instruments.tdk.tdk_gen80_65 import TDK_Gen80_65


def test_init():
    with expected_protocol(
            TDK_Gen80_65,
            [(b"ADR 6", b"OK")],
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize("volt",
                         (b"10", b"20", b"40"))
def test_voltage_setpoint(volt):
    with expected_protocol(
            TDK_Gen80_65,
            [(b"ADR 6", b"OK"),
             (b"PV " + volt, b"OK"),
             (b"PV?", volt)]
    ) as instr:
        instr.voltage_setpoint = float(volt)
        assert instr.voltage_setpoint == float(volt)


def test_invalid_voltage_setpoint():
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen80_65,
                [(b"ADR 6", b"OK"),
                 (b"PV 160", b"OK"), ]
        ) as instr:
            instr.voltage_setpoint = 160


def test_invalid_current_setpoint():
    with pytest.raises(ValueError):
        with expected_protocol(
                TDK_Gen80_65,
                [(b"ADR 6", b"OK"),
                 (b"PC 150", b"OK"), ]
        ) as instr:
            instr.current_setpoint = 150
