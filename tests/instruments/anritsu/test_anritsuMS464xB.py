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
from pymeasure.instruments.anritsu import AnritsuMS464xB, AnritsuMS4642B, AnritsuMS4644B,\
    AnritsuMS4645B, AnritsuMS4647B


def test_init():
    with expected_protocol(
        AnritsuMS464xB,
        [],
    ) as instr:
        assert len(instr.channels) == 16
        assert len(instr.ch_1.ports) == 4
        assert len(instr.ch_1.traces) == 16


def test_init_with_different_channel_numbers():
    # Test init with different number of active channels and installed ports
    with expected_protocol(
        AnritsuMS464xB,
        [],
        active_channels=12,
        installed_ports=2,
        traces_per_channel=10
    ) as instr:
        assert len(instr.channels) == 12
        assert len(instr.ch_1.ports) == 2
        assert len(instr.ch_1.traces) == 10


def test_init_unknown_active_channels():
    # Test init with unknown active channels and traces
    with expected_protocol(
        AnritsuMS464xB,
        [(":SYST:PORT:COUN?", "3"),
         (":DISP:COUN?", "2"),
         (":CALC1:PAR:COUN?", "8"),
         (":CALC2:PAR:COUN?", "12")],
        active_channels="auto",
        installed_ports="auto",
        traces_per_channel="auto",
    ) as instr:
        assert len(instr.channels) == 2
        assert len(instr.ch_1.ports) == 3
        assert len(instr.ch_1.traces) == 8
        assert len(instr.ch_2.traces) == 12


def test_update_channels():
    with expected_protocol(
        AnritsuMS464xB,
        [(":DISP:COUN?", "8"),
         (":DISP:COUN?", "12")],
    ) as instr:
        assert len(instr.channels) == 16
        instr.update_channels()
        assert len(instr.channels) == 8
        instr.update_channels()
        assert len(instr.channels) == 12


def test_channel_number_of_traces():
    # Test first level channel
    with expected_protocol(
        AnritsuMS464xB,
        [(":CALC6:PAR:COUN 16", None),
         (":CALC2:PAR:COUN?", "4")],
    ) as instr:
        instr.ch_6.number_of_traces = 16
        assert instr.ch_2.number_of_traces == 4


def test_channel_update_traces():
    # Test first level channel
    with expected_protocol(
        AnritsuMS464xB,
        [(":CALC1:PAR:COUN?", "4"),
         (":CALC1:PAR:COUN?", "12")],
    ) as instr:
        assert len(instr.ch_1.traces) == 16
        instr.ch_1.update_traces()
        assert len(instr.ch_1.traces) == 4
        instr.ch_1.update_traces()
        assert len(instr.ch_1.traces) == 12


def test_channel_port_power_level():
    # Test second level channel (port in channel)
    with expected_protocol(
        AnritsuMS464xB,
        [(":SOUR6:POW:PORT1 12", None),
         (":SOUR2:POW:PORT4?", "-1.5E1")],
    ) as instr:
        instr.ch_6.pt_1.power_level = 12.
        assert instr.ch_2.pt_4.power_level == -15.


def test_channel_trace_measurement_parameter():
    # Test second level channel (trace in channel)
    with expected_protocol(
        AnritsuMS464xB,
        [(":CALC6:PAR1:DEF S11", None),
         (":CALC2:PAR6:DEF?", "S21")],
    ) as instr:
        instr.ch_6.tr_1.measurement_parameter = "S11"
        assert instr.ch_2.tr_6.measurement_parameter == "S21"


def test_subclass_MS4642B_frequency_range():
    with expected_protocol(
        AnritsuMS4642B,
        [(":SENS1:FREQ:STOP 2e+10", None)],
    ) as instr:
        instr.ch_1.frequency_stop = 2e10
        with pytest.raises(ValueError):
            instr.ch_1.frequency_stop = 3e10


def test_subclass_MS4644B_frequency_range():
    with expected_protocol(
        AnritsuMS4644B,
        [(":SENS1:FREQ:STOP 4e+10", None)],
    ) as instr:
        instr.ch_1.frequency_stop = 4e10
        with pytest.raises(ValueError):
            instr.ch_1.frequency_stop = 5e10


def test_subclass_MS4645B_frequency_range():
    with expected_protocol(
        AnritsuMS4645B,
        [(":SENS1:FREQ:STOP 5e+10", None)],
    ) as instr:
        instr.ch_1.frequency_stop = 5e10
        with pytest.raises(ValueError):
            instr.ch_1.frequency_stop = 6e10


def test_subclass_MS4647B_frequency_range():
    with expected_protocol(
        AnritsuMS4647B,
        [(":SENS1:FREQ:STOP 7e+10", None)],
    ) as instr:
        instr.ch_1.frequency_stop = 7e10
        with pytest.raises(ValueError):
            instr.ch_1.frequency_stop = 8e10
