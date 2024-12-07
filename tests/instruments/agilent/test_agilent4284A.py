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
from pymeasure.instruments.agilent import Agilent4284A


@pytest.mark.parametrize("frequency", [20, 100, 1e4, 1e6])
def test_frequency(frequency):
    with expected_protocol(
        Agilent4284A,
        [("FREQ?", frequency),
         (f"FREQ {frequency:g}", None),],
    ) as inst:
        assert frequency == inst.frequency
        inst.frequency = frequency


def test_frequency_limit():
    with pytest.raises(ValueError):
        with expected_protocol(
            Agilent4284A,
            [("FREQ 1", None)],
        ) as inst:
            inst.frequency = 1


@pytest.mark.parametrize("power_mode", ["0", "1"])
def test_high_power_mode(power_mode):
    with expected_protocol(
        Agilent4284A,
        [("OUTP:HPOW?", power_mode),],
    ) as inst:
        assert bool(power_mode) == inst.high_power_enabled


@pytest.mark.parametrize("impedance_mode", [
    "CPD", "CPQ", "CPG", "CPRP", "CSD", "CSQ", "CSRS", "LPQ", "LPD", "LPG", "LPRP",
    "LSD", "LSQ", "LSRS", "RX", "ZTD", "ZTR", "GB", "YTD", "YTR"])
def test_impedance_mode(impedance_mode):
    with expected_protocol(
        Agilent4284A,
        [("FUNC:IMP?", impedance_mode),
         (f"FUNC:IMP {impedance_mode}", None),],
    ) as inst:
        assert impedance_mode == inst.impedance_mode
        inst.impedance_mode = impedance_mode


def test_enable_high_power():
    with expected_protocol(
        Agilent4284A,
        [("*OPT?", "1,0,0,0,0"),
         ("OUTP:HPOW 1", None),
         ("VOLT:LEV 5", None),],
    ) as inst:
        inst.high_power_enabled = True
        inst.ac_voltage = 5


def test_disable_high_power():
    with pytest.raises(ValueError):
        with expected_protocol(
            Agilent4284A,
            [("OUTP:HPOW 0", None),
             ("VOLT:LEV 5", None)],
        ) as inst:
            inst.high_power_enabled = False
            inst.ac_voltage = 5


@pytest.fixture
def param_list():
    freq_input = [1e7, 5e6, 1e6, 5e5, 1e5, 5e4, 1e4, 5e3, 1e3, 500, 100, 50, 20, 10]
    freq_str = "1000000,500000,100000,50000,10000,5000,1000,500,100,50,20"
    freq_output = [1e6, 5e5, 1e5, 5e4, 1e4, 5e3, 1e3, 500, 100, 50, 20]
    measured_str = "0.5,-0.785,+0,+0,"
    return freq_input, freq_str, freq_output, measured_str


def sweep_measurement(param_list):
    with expected_protocol(
        Agilent4284A,
        [("*CLS", None),
         ("TRIG:SOUR BUS;:DISP:PAGE LIST;:FORM ASC;:LIST:MODE SEQ;:INIT:CONT ON", None),
         (f"LIST:FREQ {param_list[1][:-3]};:TRIG:IMM", None),
         ("STAT:OPER?", "+8"),
         ("FETCH?", f"{param_list[3]*10}"),
         ("LIST:FREQ?", f"{param_list[1][:-3]}"),
         ("LIST:FREQ 20;:TRIG:IMM", None),
         ("STAT:OPER?", "+8"),
         ("FETCH?", f"{param_list[3]}"),
         ("LIST:FREQ?", "20"),
         ("SYST:ERR?", '0,"No error"')],
    ) as inst:
        results = inst.sweep_measurement('frequency', param_list[0])
        assert results[0] == [0.5,] * 11
        assert results[1] == [-0.785,] * 11
        assert results[2] == param_list[2]
