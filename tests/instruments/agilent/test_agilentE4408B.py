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

from pymeasure.test import expected_protocol
from pymeasure.instruments.agilent.agilentE4408B import AgilentE4408B


def test_start_frequency_get():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:STAR?;", 1e6)],
    ) as inst:
        assert inst.start_frequency == 1e6


def test_start_frequency_set():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:STAR 1.000000e+06 Hz;", None)],
    ) as inst:
        inst.start_frequency = 1e6


def test_stop_frequency_get():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:STOP?;", 3e9)],
    ) as inst:
        assert inst.stop_frequency == 3e9


def test_stop_frequency_set():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:STOP 3.000000e+09 Hz;", None)],
    ) as inst:
        inst.stop_frequency = 3e9


def test_center_frequency_get():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:CENT?;", 1.5e9)],
    ) as inst:
        assert inst.center_frequency == 1.5e9


def test_center_frequency_set():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:CENT 1.500000e+09 Hz;", None)],
    ) as inst:
        inst.center_frequency = 1.5e9


def test_frequency_step_get():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:CENT:STEP:INCR?;", 1e3)],
    ) as inst:
        assert inst.frequency_step == 1e3


def test_frequency_step_set():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:FREQ:CENT:STEP:INCR 1000 Hz;", None)],
    ) as inst:
        inst.frequency_step = 1e3


def test_frequency_points_get():
    with expected_protocol(
        AgilentE4408B,
        [(":SENSe:SWEEp:POINts?;", 101)],
    ) as inst:
        assert inst.frequency_points == 101


def test_frequency_points_set():
    with expected_protocol(
        AgilentE4408B,
        [(":SENSe:SWEEp:POINts 101;", None)],
    ) as inst:
        inst.frequency_points = 101


def test_frequency_points_truncated():
    with expected_protocol(
        AgilentE4408B,
        [(":SENSe:SWEEp:POINts 101;", None)],
    ) as inst:
        inst.frequency_points = 50


def test_sweep_time_get():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:SWE:TIME?;", 1.0)],
    ) as inst:
        assert inst.sweep_time == 1.0


def test_sweep_time_set():
    with expected_protocol(
        AgilentE4408B,
        [(":SENS:SWE:TIME 1.00e+00;", None)],
    ) as inst:
        inst.sweep_time = 1.0


def test_id():
    with expected_protocol(
        AgilentE4408B,
        [("*IDN?", "Agilent Technologies,E4408B,US12345678,A.02.00")],
    ) as inst:
        assert inst.id == "Agilent Technologies,E4408B,US12345678,A.02.00"
