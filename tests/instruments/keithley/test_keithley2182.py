#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.keithley.keithley2182 import Keithley2182


def test_voltage_read():
    with expected_protocol(
        Keithley2182,
        [(":READ?", "3.1415")],
    ) as inst:
        assert inst.voltage == pytest.approx(3.1415)


def test_voltage_range():
    with expected_protocol(
        Keithley2182,
        [(":SENS:VOLT:CHAN1:RANG?", "92"),
         (":SENS:VOLT:CHAN1:RANG 2", None)
         ],
    ) as inst:
        assert inst.ch_1.voltage_range == 92
        inst.ch_1.voltage_range = 2


def test_voltage_range_trunc():
    with expected_protocol(
        Keithley2182,
        [(":SENS:VOLT:CHAN2:RANG 15", None),
         (":SENS:VOLT:CHAN2:RANG?", "12"),
         ],
    ) as inst:
        inst.ch_2.voltage_range = 15  # too large, gets truncated
        assert inst.ch_2.voltage_range == 12


def test_active_channel():
    with expected_protocol(
        Keithley2182,
        [(":SENS:CHAN?", "1"),
         (":SENS:CHAN 2", None),
         ],
    ) as inst:
        assert inst.active_channel == 1
        inst.active_channel = 2


def test_thermocouple():
    with expected_protocol(
        Keithley2182,
        [(":SENS:TEMP:TC?", "S"),
         (":SENS:TEMP:TC K", None),
         ],
    ) as inst:
        assert inst.thermocouple == 'S'
        inst.thermocouple = 'K'


def test_setup_voltage():
    with expected_protocol(
        Keithley2182,
        [(":SENS:CHAN 1;"
          ":SENS:FUNC 'VOLT';"
          ":SENS:VOLT:NPLC 5;", None),
         (":SENS:VOLT:RANG:AUTO 1", None),
         ("SYST:ERR?", '0,"No error"'),
         ],
    ) as inst:
        inst.ch_1.setup_voltage()


def test_setup_temperature():
    with expected_protocol(
        Keithley2182,
        [(":SENS:CHAN 2;"
          ":SENS:FUNC 'TEMP';"
          ":SENS:TEMP:NPLC 5", None),
         ("SYST:ERR?", '0,"No error"'),
         ],
    ) as inst:
        inst.ch_2.setup_temperature()
