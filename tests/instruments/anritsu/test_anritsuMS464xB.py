#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments.anritsu import AnritsuMS464xB


def test_init():
    with expected_protocol(
        AnritsuMS464xB,
        [],
    ):
        pass  # Verify the expected communication.


def test_center_freq():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:FREQ:CENT 35000", None), (b":SENS1:FREQ:CENT?", 35000)],
    ) as instr:
        instr.ch_1.center_frequency = 35000
        assert instr.ch_1.center_frequency == 35000


def test_cw_freq():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:FREQ:CW 35000", None), (b":SENS1:FREQ:CW?", 35000)],
    ) as instr:
        instr.ch_1.cw_frequency = 35000
        assert instr.ch_1.cw_frequency == 35000


def test_span_frequency():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:FREQ:SPAN 35000", None), (b":SENS1:FREQ:SPAN?", 35000)],
    ) as instr:
        instr.ch_1.span_frequency = 35000
        assert instr.ch_1.span_frequency == 35000


def test_start_frequency():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:FREQ:STAR 35000", None), (b":SENS1:FREQ:STAR?", 35000)],
    ) as instr:
        instr.ch_1.start_frequency = 35000
        assert instr.ch_1.start_frequency == 35000


def test_stop_frequency():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:FREQ:STOP 35000", None), (b":SENS1:FREQ:STOP?", 35000)],
    ) as instr:
        instr.ch_1.stop_frequency = 35000
        assert instr.ch_1.stop_frequency == 35000


def test_sweep_type():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:SWE:TYP LOG", None), (b":SENS1:SWE:TYP?", "LOG")],
    ) as instr:
        instr.ch_1.sweep_type = "LOG"
        assert instr.ch_1.sweep_type == "LOG"


def test_sweep_mode():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:SA:MODE VNA", None), (b":SENS1:SA:MODE?", "VNA")],
    ) as instr:
        instr.ch_1.sweep_mode = "VNA"
        assert instr.ch_1.sweep_mode == "VNA"


def test_sweep_point():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:SWE:POI 6535", None), (b":SENS1:SWE:POI?", 6535)],
    ) as instr:
        instr.ch_1.sweep_points = 6535
        assert instr.ch_1.sweep_points == 6535


def test_num_averages():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:AVER:COUN 6535", None), (b":SENS1:AVER:COUN?", 6535)],
    ) as instr:
        instr.ch_1.num_averages = 6535
        assert instr.ch_1.num_averages == 6535


def test_bandwidth():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":SENS1:BWID 65535", None), (b":SENS1:BWID?", 65535)],
    ) as instr:
        instr.ch_1.bandwidth = 65535
        assert instr.ch_1.bandwidth == 65535


def test_binary_data_byte_format():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":FORM:BORD NORM", None), (b":FORM:BORD?", "NORM")],
    ) as instr:
        instr.binary_data_byte_format = AnritsuMS464xB.BinaryDataByteFormat.MSB_FIRST
        assert instr.binary_data_byte_format == str(AnritsuMS464xB.BinaryDataByteFormat.MSB_FIRST)


def test_binary_format():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":FORM:DATA REAL", None), (b":FORM:DATA?", "REAL")],
    ) as instr:
        instr.binary_data_format = AnritsuMS464xB.BinaryDataFormat.REAL
        assert instr.binary_data_format == str(AnritsuMS464xB.BinaryDataFormat.REAL)


def test_datafile_header():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":FORM:DATA:HEAD 1", None), (b":FORM:DATA:HEAD?", 1)],
    ) as instr:
        instr.datafile_header = True
        assert instr.datafile_header is True


def test_datafile_frequency():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":FORM:SNP:FREQ KHZ", None), (b":FORM:SNP:FREQ?", "KHZ")],
    ) as instr:
        instr.datafile_frequency = AnritsuMS464xB.DataFileFrequencyUnits.KHZ
        assert instr.datafile_frequency == str(AnritsuMS464xB.DataFileFrequencyUnits.KHZ)


def test_datafile_parameter():
    with expected_protocol(
        AnritsuMS464xB,
        [(b":FORM:SNP:PAR LOGPH", None), (b":FORM:SNP:PAR?", "LOGPH")],
    ) as instr:
        instr.datafile_parameter = AnritsuMS464xB.DataFileParameter.LOG_AND_PHASE
        assert instr.datafile_parameter == str(AnritsuMS464xB.DataFileParameter.LOG_AND_PHASE)
