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

from pymeasure.instruments.agilent.agilentE5062A import AgilentE5062A

import numpy as np

DISPLAY_LAYOUT_OPTIONS = [
        "D1",
        "D12",
        "D1_2",
        "D112",
        "D1_1_2",
        "D123",
        "D1_2_3",
        "D12_33",
        "D11_23",
        "D13_23",
        "D12_13",
        "D1234",
        "D1_2_3_4",
        "D12_34"
]


def initial_comm_pairs():
    """during initialization of the AgilentE5062A class, we need to set (&
    query) a few things from the VNA as part of setup. This function returns
    that initial communication.

    """
    comms = []
    for ch in 1 + np.arange(4):
        comms += [
            (f"CALC{ch}:PARameter:COUNt?", "1"),
            (f"SOURce{ch}:POWer:ATTenuation?", "0"),
        ]
    comms += [
        ("FORMat:DATA REAL", None),
        ("FORMat:BORDer SWAPped", None)
    ]
    return comms


def test_ch_visible_traces():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("CALC1:PARameter:COUNt 1", None),
                ("CALC1:PARameter:COUNt?", "1"),
                ("CALC1:PARameter:COUNt 2", None),
                ("CALC1:PARameter:COUNt?", "2"),
                ("CALC1:PARameter:COUNt 3", None),
                ("CALC1:PARameter:COUNt?", "3"),
                ("CALC1:PARameter:COUNt 4", None),
                ("CALC1:PARameter:COUNt?", "4")
            ]) as inst:
        # test ch visible_traces
        ot4 = np.arange(4) + 1
        ch = inst.channels[1]
        for opt in ot4:
            ch.visible_traces = opt
            assert ch.visible_traces == opt


def test_ch_traces():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("CALCulate1:PARameter1:DEFine S11", None),
                ("CALCulate1:PARameter1:DEFine?", "S11"),
                ("CALCulate1:PARameter1:DEFine S12", None),
                ("CALCulate1:PARameter1:DEFine?", "S12"),
                ("CALCulate1:PARameter1:DEFine S21", None),
                ("CALCulate1:PARameter1:DEFine?", "S21"),
                ("CALCulate1:PARameter1:DEFine S22", None),
                ("CALCulate1:PARameter1:DEFine?", "S22"),
                ("CALC1:PAR1:SEL", None)
            ]) as inst:
        tr = inst.channels[1].traces[1]
        for p in ['S11', 'S12', 'S21', 'S22']:
            tr.parameter = p
            assert tr.parameter == p
        tr.activate()


def test_ch_start_frequency():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:FREQuency:STARt 300000", None),
                ("SENSe1:FREQuency:STARt?", "300000"),
                ("SENSe1:FREQuency:STARt 3e+09", None),
                ("SENSe1:FREQuency:STARt?", "3000000000"),
            ]) as inst:
        ch = inst.channels[1]
        for f in [3e5, 3e9]:
            ch.start_frequency = f
            assert ch.start_frequency == f


def test_ch_stop_frequency():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:FREQuency:STOP 300000", None),
                ("SENSe1:FREQuency:STOP?", "300000"),
                ("SENSe1:FREQuency:STOP 3e+09", None),
                ("SENSe1:FREQuency:STOP?", "3000000000"),
            ]) as inst:
        ch = inst.channels[1]
        for f in [3e5, 3e9]:
            ch.stop_frequency = f
            assert ch.stop_frequency == f


def test_ch_scan_points():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:SWEep:POINts 2", None),
                ("SENSe1:SWEep:POINts?", "2"),
                ("SENSe1:SWEep:POINts 1601", None),
                ("SENSe1:SWEep:POINts?", "1601"),
            ]) as inst:
        ch = inst.channels[1]
        for p in [2, 1601]:
            ch.scan_points = p
            assert ch.scan_points == p


def test_ch_sweep_time():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:SWEep:TIME:AUTO 0", None),
                ("SENSe1:SWEep:TIME:AUTO?", "0"),
                ("SENSe1:SWEep:TIME 1", None),
                ("SENSe1:SWEep:TIME?", "1"),
                ("SENSe1:SWEep:TIME 2", None),
                ("SENSe1:SWEep:TIME?", "2"),
                ("SENSe1:SWEep:TIME:AUTO 1", None),
                ("SENSe1:SWEep:TIME:AUTO?", "1")
            ]) as inst:
        ch = inst.channels[1]
        ch.sweep_time_auto_enabled = False
        assert not ch.sweep_time_auto_enabled
        for t in [1, 2]:
            ch.sweep_time = t
            assert np.isclose(ch.sweep_time, t, rtol=.01)
        ch.sweep_time_auto_enabled = True
        assert ch.sweep_time_auto_enabled


def test_ch_sweep_type():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:SWEep:TYPE LIN", None),
                ("SENSe1:SWEep:TYPE?", "LIN"),
                ("SENSe1:SWEep:TYPE LOG", None),
                ("SENSe1:SWEep:TYPE?", "LOG"),
                ("SENSe1:SWEep:TYPE SEGM", None),
                ("SENSe1:SWEep:TYPE?", "SEGM"),
                ("SENSe1:SWEep:TYPE POW", None),
                ("SENSe1:SWEep:TYPE?", "POW"),
            ]) as inst:
        ch = inst.channels[1]
        for t in ['LIN', 'LOG', 'SEGM', 'POW']:
            ch.sweep_type = t
            assert ch.sweep_type == t  # returns just the capitalized part


def test_ch_averaging():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:AVERage 1", None),
                ("SENSe1:AVERage?", "1"),
                ("SENSe1:AVERage:CLEar", None),
                ("SENSe1:AVERage:COUNt 1", None),
                ("SENSe1:AVERage:COUNt?", "1"),
                ("SENSe1:AVERage:COUNt 999", None),
                ("SENSe1:AVERage:COUNt?", "999"),
                ("SENSe1:AVERage 0", None),
                ("SENSe1:AVERage?", "0")
            ]) as inst:
        ch = inst.channels[1]
        ch.averaging_enabled = True
        assert ch.averaging_enabled
        ch.restart_averaging()
        for n in [1, 999]:
            ch.averages = n
            assert ch.averages == n
        ch.averaging_enabled = False
        assert not ch.averaging_enabled


def test_ch_IF_bandwidth():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENSe1:BANDwidth 10", None),
                ("SENSe1:BANDwidth?", "10"),
                ("SENSe1:BANDwidth 30000", None),
                ("SENSe1:BANDwidth?", "30000")
            ]) as inst:
        ch = inst.channels[1]
        for bw in [10, 30e3]:
            ch.IF_bandwidth = bw
            assert ch.IF_bandwidth == bw


def test_ch_display_layout():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("DISPlay:SPLit D1", None),
                ("DISPlay:SPLit?", "D1"),
                ("DISPlay:SPLit D12_34", None),
                ("DISPlay:SPLit?", "D12_34")
            ]) as inst:
        for layout in ["D1", "D12_34"]:
            inst.display_layout = layout
            assert inst.display_layout == layout


def test_attenuation():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SOURce1:POWer:ATTenuation 0", None),
                ("SOURce1:POWer:ATTenuation?", "0"),
                ("SOURce1:POWer -5", None),
                ("SOURce1:POWer?", "-5"),
                ("SOURce1:POWer 10", None),
                ("SOURce1:POWer?", "10"),
                ("SOURce1:POWer:ATTenuation 40", None),
                ("SOURce1:POWer:ATTenuation?", "40"),
                ("SOURce1:POWer -45", None),
                ("SOURce1:POWer?", "-45"),
                ("SOURce1:POWer -30", None),
                ("SOURce1:POWer?", "-30"),
            ]) as inst:
        ch = inst.channels[1]
        for atten in [0, 40]:
            ch.attenuation = atten
            assert ch.attenuation == atten
            for p in [-5, 10]:
                power = -atten + p
                ch.power = power
                assert ch.power == power


def test_tr_display_layout():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("DISPlay:WINDow1:SPLit D1", None),
                ("DISPlay:WINDow1:SPLit?", "D1"),
                ("DISPlay:WINDow1:SPLit D12_34", None),
                ("DISPlay:WINDow1:SPLit?", "D12_34")
            ]) as inst:
        ch = inst.channels[1]
        for layout in ['D1', 'D12_34']:
            ch.display_layout = layout
            assert ch.display_layout == layout


def test_ch_activate_correct():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("DISPlay:SPLit D1_2", None),
                ("DISPlay:SPLit?", "D1_2"),  # for a check
                ("DISP:WIND2:ACT", None),
                ("DISPlay:SPLit D1", None),
            ]) as inst:
        inst.display_layout = 'D1_2'
        inst.channels[2].activate()
        inst.display_layout = 'D1'


def test_ch_activate_incorrect():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("DISPlay:SPLit D1", None),
                ("DISPlay:SPLit?", None)  # for a check
            ]) as inst:
        inst.display_layout = 'D1'
        with pytest.raises(ValueError):
            inst.channels[2].activate()


def test_tr_format():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("CALCulate1:FORMat MLOG", None),
                ("CALCulate1:FORMat?", "MLOG"),
                ("CALCulate1:FORMat PPH", None),
                ("CALCulate1:FORMat?", "PPH"),
            ]) as inst:
        ch = inst.channels[1]
        for opt in ["MLOG", "PPH"]:
            ch.trace_format = opt
            assert ch.trace_format == opt


def test_data():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("CALC1:DATA:FDAT?", None),
                (None, bytes('#6003216', encoding='ascii')),
                (None, bytes(3216)),
                (None, bytes('\n', encoding='ascii'))
            ]) as inst:
        real, imag = inst.channels[1].data
        assert np.size(real) == 201
        assert np.size(imag) == 201


def test_frequencies():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("SENS1:FREQ:DATA?", None),
                (None, bytes('#6001608', encoding='ascii')),
                (None, bytes(1608)),
                (None, bytes('\n', encoding='ascii'))
            ]) as inst:
        freqs = inst.channels[1].frequencies
        assert np.size(freqs) == 201


def test_reset():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("*RST", None)
            ]) as inst:
        inst.reset()


def test_abort():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                (":ABOR", None)
            ]) as inst:
        inst.abort()


def test_trigger_source():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("TRIGger:SOURce INT", None),
                ("TRIGger:SOURce?", "INT"),
                ("TRIGger:SOURce EXT", None),
                ("TRIGger:SOURce?", "EXT"),
                ("TRIGger:SOURce MAN", None),
                ("TRIGger:SOURce?", "MAN"),
                ("TRIGger:SOURce BUS", None),
                ("TRIGger:SOURce?", "BUS")
            ]) as inst:
        for src in ['INT', 'EXT', 'MAN', 'BUS']:
            inst.trigger_source = src
            assert inst.trigger_source == src


def test_trigger_continuous():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("INITiate1:CONTinuous 0", None),
                ("INITiate1:CONTinuous?", "0"),
                ("INITiate1:CONTinuous 1", None),
                ("INITiate1:CONTinuous?", "1")
            ]) as inst:
        ch = inst.channels[1]
        ch.trigger_continuous = False
        assert not ch.trigger_continuous
        ch.trigger_continuous = True
        assert ch.trigger_continuous


def test_trigger_initiate():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ('INITiate1', None)
            ]) as inst:
        ch = inst.channels[1]
        ch.trigger_initiate()


def test_trigger_bus():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("*TRG", None)
            ]) as inst:
        inst.trigger_bus()


def test_trigger():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("TRIGger", None)
            ]) as inst:
        inst.trigger()


def test_trigger_single():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("TRIGger:SINGle", None)
            ]) as inst:
        inst.trigger_single()


def test_wait_for_complete():
    with expected_protocol(
            AgilentE5062A,
            [
                *initial_comm_pairs(),
                ("TRIGger:SINGle", None),
                ("*OPC?", "1")
            ]) as inst:
        inst.trigger_single()
        inst.wait_for_complete()
