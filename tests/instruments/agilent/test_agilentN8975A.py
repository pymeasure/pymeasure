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
from pymeasure.instruments.agilent.agilentN8975A import AgilentN8975A


class TestAgilentN8975A:
    def test_abort(self):
        with expected_protocol(
            AgilentN8975A,
            [("ABOR", None),
             ]
        ) as inst:
            inst.abort()

    def test_calibrate(self):
        with expected_protocol(
            AgilentN8975A,
            [("CORR:COLL STAN", None),
             ]
        ) as inst:
            inst.calibrate()

    def test_initiate(self):
        with expected_protocol(
            AgilentN8975A,
            [("INIT:IMM", None),
             ]
        ) as inst:
            inst.initiate()

    def test_single(self):
        with expected_protocol(
            AgilentN8975A,
            [("INIT:CONT 0", None),
             ("ABOR", None),
             ("INIT:IMM", None),
             ("*OPC?", "1"),
             ]
        ) as inst:
            inst.single()

    @pytest.mark.parametrize("average", [1, 999])
    def test_average(self, average):
        with expected_protocol(
            AgilentN8975A,
            [(f"AVER:COUN {average}", None),
             ("AVER:COUN?", f"{average:e}"),  # NFA responds in scientific format
             ]
        ) as inst:
            inst.average = average
            assert average == inst.average

    @pytest.mark.parametrize("average_enabled, mapping", [
                              (True, 1),
                              (False, 0),
                              ])
    def test_average_enabled(self, average_enabled, mapping):
        with expected_protocol(
            AgilentN8975A,
            [(f"AVER {mapping}", None),
             ("AVER?", f"{mapping}"),
             ]
        ) as inst:
            inst.average_enabled = average_enabled
            assert average_enabled == inst.average_enabled

    @pytest.mark.parametrize("bandwidth", [100e3, 200e3, 400e3, 1e6, 2e6, 4e6])
    def test_bandwidth(self, bandwidth):
        with expected_protocol(
            AgilentN8975A,
            [(f"BAND {bandwidth:f}", None),
             ("BAND?", f"{bandwidth}"),
             ]
        ) as inst:
            inst.bandwidth = bandwidth
            assert bandwidth == inst.bandwidth

    @pytest.mark.parametrize("continuous_mode_enabled, mapping", [
                              (True, 1),
                              (False, 0),
                              ])
    def test_continuous_mode_enabled(self, continuous_mode_enabled, mapping):
        with expected_protocol(
            AgilentN8975A,
            [(f"INIT:CONT {mapping}", None),
             ("INIT:CONT?", f"{mapping}"),
             ]
        ) as inst:
            inst.continuous_mode_enabled = continuous_mode_enabled
            assert continuous_mode_enabled == inst.continuous_mode_enabled

    def test_gain_scalar(self):
        with expected_protocol(
            AgilentN8975A,
            [("FREQ:MODE?", "FIX"),
             ("FETCH:SCALAR:DATA:CORR:GAIN? DB", "0.12e1" + "\x00"),
             ]
        ) as inst:
            assert [1.2] == inst.gain

    def test_gain_array(self):
        gain = [1, 1.11, 3.4e1, -3E-2]
        gain_str = "1,1.11,3.4e1,-3E-2"
        with expected_protocol(
            AgilentN8975A,
            [("FREQ:MODE?", "SWE"),
             ("FETCH:ARRAY:DATA:CORR:GAIN? DB", gain_str + "\x00"),
             ]
        ) as inst:
            assert gain == inst.gain

    def test_noise_figure_scalar(self):
        with expected_protocol(
            AgilentN8975A,
            [("FREQ:MODE?", "FIX"),
             ("FETCH:SCALAR:DATA:CORR:NFIG? DB", "+0.146E+0" + "\x00"),
             ]
        ) as inst:
            assert [0.146] == inst.noise_figure

    def test_noise_figure_array(self):
        noise_figure = [2, 6.711, 3.4e1, -3E-2]
        noise_figure_str = "2,6.711,3.4e1,-3E-2"
        with expected_protocol(
            AgilentN8975A,
            [("FREQ:MODE?", "SWE"),
             ("FETCH:ARRAY:DATA:CORR:NFIG? DB", noise_figure_str + "\x00"),
             ]
        ) as inst:
            assert noise_figure == inst.noise_figure


class TestAgilentN8975AFrequency:
    @pytest.mark.parametrize("start_frequency", [10e6, 26.4999e9])
    def test_start_frequency(self, start_frequency):
        with expected_protocol(
            AgilentN8975A,
            [(f"FREQ:STAR {start_frequency:f}", None),
             ("FREQ:STAR?", f"{start_frequency}"),
             ]
        ) as inst:
            inst.frequency.start_frequency = start_frequency
            assert start_frequency == inst.frequency.start_frequency

    @pytest.mark.parametrize("stop_frequency", [10.1e6, 26.5e9])
    def test_stop_frequency(self, stop_frequency):
        with expected_protocol(
            AgilentN8975A,
            [(f"FREQ:STOP {stop_frequency:f}", None),
             ("FREQ:STOP?", f"{stop_frequency}"),
             ]
        ) as inst:
            inst.frequency.stop_frequency = stop_frequency
            assert stop_frequency == inst.frequency.stop_frequency

    @pytest.mark.parametrize("mode, mapping", [
                             ("sweep", "SWE"),
                             ("fixed", "FIX"),
                             ("list", "LIST"),
                             ])
    def test_mode(self, mode, mapping):
        with expected_protocol(
            AgilentN8975A,
            [(f"FREQ:MODE {mapping}", None),
             ("FREQ:MODE?", f"{mapping}"),
             ]
        ) as inst:
            inst.frequency.mode = mode
            assert mode == inst.frequency.mode

    @pytest.mark.parametrize("fixed_value", [10e6, 26.5e9])
    def test_fixed_value(self, fixed_value):
        with expected_protocol(
            AgilentN8975A,
            [(f"FREQ:FIX {fixed_value:f}", None),
             ("FREQ:FIX?", f"{fixed_value}"),
             ]
        ) as inst:
            inst.frequency.fixed_value = fixed_value
            assert fixed_value == inst.frequency.fixed_value

    def test_list_data(self):
        list_data = [10e6, 13e7, 20.33e9]
        list_data_str = "10000000.0,130000000.0,20330000000.0"
        with expected_protocol(
            AgilentN8975A,
            [(f"FREQ:LIST:DATA {list_data_str}", None),
             ("FREQ:LIST:DATA?", list_data_str + "\x00"),
             ]
        ) as inst:
            inst.frequency.list_data = list_data
            assert list_data == inst.frequency.list_data

    def test_number_of_entries(self):
        with expected_protocol(
            AgilentN8975A,
            [("FREQ:LIST:COUN?", "3"),
             ]
        ) as inst:
            assert 3 == inst.frequency.number_of_entries

    def test_number_of_points(self):
        with expected_protocol(
            AgilentN8975A,
            [("SWE:POIN 51", None),
             ("SWE:POIN?", "51"),
             ]
        ) as inst:
            inst.frequency.number_of_points = 51
            assert 51 == inst.frequency.number_of_points
