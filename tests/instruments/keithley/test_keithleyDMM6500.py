#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.test import expected_protocol
from pymeasure.instruments.keithley.keithleyDMM6500 import KeithleyDMM6500


def test_init():
    with expected_protocol(
        KeithleyDMM6500,
        [
            ("*LANG SCPI", None),
        ],
    ):
        pass  # Verify the expected communication.


def test_terminals_used():
    with expected_protocol(
        KeithleyDMM6500,
        [
            ("*LANG SCPI", None),
            ("ROUT:TERM?", "FRON"),
        ],
    ) as inst:
        assert "FRONT" == inst.terminals_used


def test_voltage_nplc():
    with expected_protocol(
        KeithleyDMM6500,
        [
            ("*LANG SCPI", None),
            (":SENS:VOLT:NPLC 1.234", None),
            (":SENS:VOLT:NPLC?", "1.234"),
        ],
    ) as instr:
        instr.voltage_nplc = 1.234
        assert instr.voltage_nplc == 1.234


def test_nplc_setter():
    with expected_protocol(
        KeithleyDMM6500,
        [
            ("*LANG SCPI", None),
            (":SENS:FUNC?", "VOLT:DC"),
            ("VOLT:DC:NPLC 1.345", None),
            (":SENS:FUNC?", "VOLT:DC"),
            ("VOLT:DC:NPLC?", "1.345"),
        ],
    ) as instr:
        instr.nplc = 1.345
        assert 1.345 == instr.nplc
