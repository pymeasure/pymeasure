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
from pymeasure.instruments.agilent import Agilent4284A

IMPEDANCE_MODES = ("CPD", "CPQ", "CPG", "CPRP", "CSD", "CSQ", "CSRS",
                   "LPQ", "LPD", "LPG", "LPRP", "LSD", "LSQ", "LSRS",
                   "RX", "ZTD", "ZTR", "GB", "YTD", "YTR")


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


@pytest.mark.parametrize("impedance_mode", IMPEDANCE_MODES)
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


class TestCorrection:
    """Tests for the correction functions."""

    def test_measure_open(self):
        with expected_protocol(
            Agilent4284A,
            [(":CORR:OPEN", None)]
        ) as inst:
            inst.correction.measure_open()

    def test_measure_short(self):
        with expected_protocol(
            Agilent4284A,
            [(":CORR:SHOR", None)]
        ) as inst:
            inst.correction.measure_short()

    def test_measure_load(self):
        with expected_protocol(
            Agilent4284A,
            [(":CORR:LOAD", None)]
        ) as inst:
            inst.correction.measure_load()

    @pytest.mark.parametrize("state", [True, False])
    def test_open_enabled(self, state):
        mapping = {True: 1, False: 0}
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:OPEN:STAT {mapping[state]}", None),
             (":CORR:OPEN:STAT?", mapping[state])]
        ) as inst:
            inst.correction.open_enabled = state
            state == inst.correction.open_enabled

    @pytest.mark.parametrize("state", [True, False])
    def test_short_enabled(self, state):
        mapping = {True: 1, False: 0}
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SHOR:STAT {mapping[state]}", None),
             (":CORR:SHOR:STAT?", mapping[state])]
        ) as inst:
            inst.correction.short_enabled = state
            state == inst.correction.short_enabled

    @pytest.mark.parametrize("state", [True, False])
    def test_load_enabled(self, state):
        mapping = {True: 1, False: 0}
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:LOAD:STAT {mapping[state]}", None),
             (":CORR:LOAD:STAT?", mapping[state])]
        ) as inst:
            inst.correction.load_enabled = state
            state == inst.correction.load_enabled

    @pytest.mark.parametrize("impedance_mode", IMPEDANCE_MODES)
    def test_load_function(self, impedance_mode):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:LOAD:TYPE {impedance_mode}", None),
             (":CORR:LOAD:TYPE?", impedance_mode)]
        ) as inst:
            inst.correction.load_function = impedance_mode
            impedance_mode == inst.correction.load_function

    @pytest.mark.parametrize("cable_length", [0, 1, 2, 4])
    def test_cable_length(self, cable_length):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:LENG {cable_length}", None),
             (":CORR:LENG?", cable_length)]
        ) as inst:
            inst.correction.cable_length = cable_length
            cable_length == inst.correction.cable_length

    @pytest.mark.parametrize("cable_length", [-1, 1.1, 3, 2e1])
    def test_cable_length_validator(self, cable_length):
        with pytest.raises(ValueError):
            with expected_protocol(
                Agilent4284A,
                [(f":CORR:LENG {cable_length}", None)],
            ) as inst:
                inst.correction.cable_length = cable_length


@pytest.mark.parametrize("spot", [1, 2, 3])
class TestSpotCorrection:
    """Tests for the spot correction functions."""

    def test_measure_open(self, spot):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SPOT{spot}:OPEN", None)]
        ) as inst:
            inst.correction.spots[spot].measure_open()

    def test_measure_short(self, spot):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SPOT{spot}:SHOR", None)]
        ) as inst:
            inst.correction.spots[spot].measure_short()

    def test_measure_load(self, spot):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SPOT{spot}:LOAD", None)]
        ) as inst:
            inst.correction.spots[spot].measure_load()

    @pytest.mark.parametrize("state", [True, False])
    def test_spot_enabled(self, spot, state):
        mapping = {True: 1, False: 0}
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SPOT{spot}:STAT {mapping[state]}", None),
             (f":CORR:SPOT{spot}:STAT?", mapping[state])]
        ) as inst:
            inst.correction.spots[spot].enabled = state
            state == inst.correction.spots[spot].enabled

    @pytest.mark.parametrize("frequency", [20, 100, 1e4, 1e6])
    def test_spot_frequency(self, spot, frequency):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SPOT{spot}:FREQ?", frequency),
             (f":CORR:SPOT{spot}:FREQ {frequency:g}", None),],
        ) as inst:
            assert frequency == inst.correction.spots[spot].frequency
            inst.correction.spots[spot].frequency = frequency

    @pytest.mark.parametrize("impedance_mode", IMPEDANCE_MODES)
    def test_spot_load_function(self, spot, impedance_mode):
        with expected_protocol(
            Agilent4284A,
            [(f":CORR:SPOT{spot}:LOAD:STAN {impedance_mode}", None),
             (f":CORR:SPOT{spot}:LOAD:STAN?", impedance_mode)]
        ) as inst:
            inst.correction.spots[spot].load_function = impedance_mode
            impedance_mode == inst.correction.spots[spot].load_function
