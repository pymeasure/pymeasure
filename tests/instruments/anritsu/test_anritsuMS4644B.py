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

from pymeasure.instruments.anritsu import AnritsuMS4644B


def test_init():
    with expected_protocol(
        AnritsuMS4644B,
        [],
    ):
        pass


def test_channel_number_of_traces():
    # Test first level channel
    with expected_protocol(
        AnritsuMS4644B,
        [(":CALC6:PAR:COUN 16", None),
         (":CALC2:PAR:COUN?", "4")],
    ) as instr:
        instr.ch_6.number_of_traces = 16
        assert instr.ch_2.number_of_traces == 4


def test_channel_port_power_level():
    # Test second level channel (port in channel)
    with expected_protocol(
        AnritsuMS4644B,
        [(":SOUR6:POW:PORT1 12", None),
         (":SOUR2:POW:PORT4?", "-1.5E1")],
    ) as instr:
        instr.ch_6.pt_1.power_level = 12.
        assert instr.ch_2.pt_4.power_level == -15.


def test_channel_trace_measurement_parameter():
    # Test second level channel (trace in channel)
    with expected_protocol(
        AnritsuMS4644B,
        [(":CALC6:PAR1:DEF S11", None),
         (":CALC2:PAR6:DEF?", "S21")],
    ) as instr:
        instr.ch_6.tr_1.measurement_parameter = "S11"
        assert instr.ch_2.tr_6.measurement_parameter == "S21"
