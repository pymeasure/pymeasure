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
from pymeasure.instruments.keithley.keithley2000 import Keithley2000


def test_voltage_read():
    with expected_protocol(
        Keithley2000,
        [(":READ?", "3.1415")],
    ) as inst:
        assert inst.voltage == pytest.approx(3.1415)


def test_voltage_range():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:RANG?", "955"),
         (":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG 234", None)
         ],
    ) as inst:
        assert inst.voltage_range == 955
        inst.voltage_range = 234


def test_voltage_range_trunc():
    with expected_protocol(
        Keithley2000,
        [(":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG 1010", None),
         (":SENS:VOLT:RANG?", "1010"),
         ],
    ) as inst:
        inst.voltage_range = 3333  # too large, gets truncated
        assert inst.voltage_range == 1010


def test_mode():
    "Confirm that mode string mapping works correctly"
    with expected_protocol(
        Keithley2000,
        [(":CONF?", "VOLT:AC"),
         (":CONF:FRES", None),
         ],
    ) as inst:
        assert inst.mode == 'voltage ac'
        inst.mode = 'resistance 4W'


def test_measure_voltage():
    with expected_protocol(
        Keithley2000,
        [(":CONF:VOLT:AC", None),
         (":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG 300", None),
         ],
    ) as inst:
        inst.measure_voltage(max_voltage=300, ac=True)
