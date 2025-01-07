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

# Tested using SCPI over telnet (via ethernet). call signature:
# $ pytest test_agilentE5062A_with_device.py --device-address 'TCPIP::192.168.2.233::INSTR'
#
# The RF stimulus is turned on with the default power level of 0 dBm. The test
# port connection can be anything that is safe for that power level.

import pytest
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


@pytest.fixture(scope="module")
def agilentE5062A(connected_device_address):
    instr = AgilentE5062A(connected_device_address)
    # ensure the device is in a defined state, e.g. by resetting it.
    return instr


def test_ch_visible_traces(agilentE5062A):
    agilentE5062A.clear()
    # test ch visible_traces
    ot4 = np.arange(4) + 1
    for ch in agilentE5062A.channels.values():
        for opt in ot4:
            ch.visible_traces = opt
            assert ch.visible_traces == opt
    assert not agilentE5062A.pop_err()[0]


def test_ch_traces(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        ch.visible_traces = 4
        for tr in ch.traces.values():
            for p in ['S11', 'S12', 'S21', 'S22']:
                tr.parameter = p
                assert tr.parameter == p
        tr.activate()
    assert not agilentE5062A.pop_err()[0]


def test_ch_start_frequency(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        for f in [3e5, 3e6, 3e7, 3e8, 3e9]:
            ch.start_frequency = f
            assert ch.start_frequency == f
        ch.start_frequency = 3e5
    assert not agilentE5062A.pop_err()[0]


def test_ch_stop_frequency(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        for f in [3e5, 3e6, 3e7, 3e8, 3e9]:
            ch.stop_frequency = f
            assert ch.stop_frequency == f
        ch.stop_frequency = 3e9
    assert not agilentE5062A.pop_err()[0]


def test_ch_scan_points(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        for p in [2, 201, 1601]:
            ch.scan_points = p
            assert ch.scan_points == p
    assert not agilentE5062A.pop_err()[0]


def test_ch_sweep_time(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        ch.sweep_time_auto_enabled = False
        assert not ch.sweep_time_auto_enabled
        for t in [1, 2]:
            ch.sweep_time = t
            assert np.isclose(ch.sweep_time, t, rtol=.01)
        ch.sweep_time_auto_enabled = True
        assert ch.sweep_time_auto_enabled
    assert not agilentE5062A.pop_err()[0]


def test_ch_sweep_type(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        for t in ['LIN', 'LOG', 'SEGM', 'POW']:
            ch.sweep_type = t
            assert ch.sweep_type == t  # returns just the capitalized part
    assert not agilentE5062A.pop_err()[0]


def test_ch_averaging(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        ch.averaging_enabled = True
        assert ch.averaging_enabled
        ch.restart_averaging()
        for n in [1, 10, 999]:
            ch.averages = n
            assert ch.averages == n
        ch.averaging_enabled = False
        assert not ch.averaging_enabled
    assert not agilentE5062A.pop_err()[0]


def test_ch_IF_bandwidth(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        for bw in [10, 10e3, 30e3]:
            ch.IF_bandwidth = bw
            assert ch.IF_bandwidth == bw
    assert not agilentE5062A.pop_err()[0]


def test_ch_display_layout(agilentE5062A):
    agilentE5062A.clear()
    for layout in DISPLAY_LAYOUT_OPTIONS:
        agilentE5062A.display_layout = layout
        assert agilentE5062A.display_layout == layout
    assert not agilentE5062A.pop_err()[0]


def test_attenuation(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        for atten in [0, 10, 20, 30, 40]:
            ch.attenuation = atten
            assert ch.attenuation == atten
            for p in [-5, 0, 10]:
                power = -atten + p
                ch.power = power
                assert ch.power == power
    assert not agilentE5062A.pop_err()[0]


def test_tr_display_layout(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.display_layout = 'D12_34'
    for ch in agilentE5062A.channels.values():
        for layout in DISPLAY_LAYOUT_OPTIONS:
            ch.display_layout = layout
            assert ch.display_layout == layout
    assert not agilentE5062A.pop_err()[0]


def test_ch_activate_correct(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.display_layout = 'D1_2'
    agilentE5062A.channels[2].activate()
    agilentE5062A.display_layout = 'D1'
    assert not agilentE5062A.pop_err()[0]


def test_ch_activate_incorrect(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.display_layout = 'D1'
    with pytest.raises(ValueError):
        agilentE5062A.channels[2].activate()
    assert not agilentE5062A.pop_err()[0]


def test_tr_format(agilentE5062A):
    agilentE5062A.clear()
    ch = agilentE5062A.channels[1]
    ch.activate()
    ch.visible_traces = 4
    for tr in ch.traces.values():
        tr.activate()
        for opt in ch.TRACE_FORMAT:
            ch.trace_format = opt
            assert ch.trace_format == opt
    assert not agilentE5062A.pop_err()[0]


def test_data(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.display_layout = 'D12_34'
    for ch in agilentE5062A.channels.values():
        ch.visible_traces = 1
        tr = ch.traces[1]
        tr.activate()
        tr.trace_format = 'SCOM'
        real, imag = ch.data
        assert np.size(real) == ch.scan_points
        assert np.size(imag) == ch.scan_points
    assert not agilentE5062A.pop_err()[0]


def test_frequencies(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.display_layout = 'D12_34'
    for ch in agilentE5062A.channels.values():
        ch.sweep_type = 'LIN'
        freqs = ch.frequencies
        assert np.size(freqs) == ch.scan_points
        assert np.any(np.isclose(ch.start_frequency, freqs))
        assert np.any(np.isclose(ch.stop_frequency, freqs))
    assert not agilentE5062A.pop_err()[0]


def test_reset(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.reset()
    assert not agilentE5062A.pop_err()[0]


def test_abort(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.abort()
    assert not agilentE5062A.pop_err()[0]


def test_trigger_source(agilentE5062A):
    agilentE5062A.clear()
    for src in ['INT', 'EXT', 'MAN', 'BUS']:
        agilentE5062A.trigger_source = src
        assert agilentE5062A.trigger_source == src
    assert not agilentE5062A.pop_err()[0]


def test_trigger_continuous(agilentE5062A):
    agilentE5062A.clear()
    for ch in agilentE5062A.channels.values():
        ch.trigger_continuous = False
        assert not ch.trigger_continuous
        ch.trigger_continuous = True
        assert ch.trigger_continuous
    assert not agilentE5062A.pop_err()[0]


def test_trigger_initiate(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.reset()
    for ch in agilentE5062A.channels.values():
        ch.trigger_continuous = False
        agilentE5062A.abort()  # the trigger needs to be in a hold state for initiate() to work.
        ch.trigger_initiate()
        ch.trigger_continuous = True
    assert not agilentE5062A.pop_err()[0]


def test_trigger_bus(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.reset()
    agilentE5062A.trigger_source = 'BUS'
    for ch in agilentE5062A.channels.values():
        ch.trigger_continuous = False
        agilentE5062A.abort()   # the trigger needs to be in a hold state for initiate() to work.
        ch.trigger_initiate()
        agilentE5062A.trigger_bus()
    agilentE5062A.trigger_source = 'INT'
    agilentE5062A.trigger_continuous = True
    assert not agilentE5062A.pop_err()[0]


def test_trigger(agilentE5062A):
    agilentE5062A.clear()
    agilentE5062A.reset()
    agilentE5062A.trigger_source = 'BUS'
    for ch in agilentE5062A.channels.values():
        ch.trigger_continuous = False
        agilentE5062A.abort()   # the trigger needs to be in a hold state for initiate() to work.
        ch.trigger_initiate()
        agilentE5062A.trigger()
    agilentE5062A.trigger_source = 'INT'
    agilentE5062A.trigger_continuous = True
    assert not agilentE5062A.pop_err()[0]


def test_trigger_single(agilentE5062A):
    """trigger_single() is different from trigger() in that the VNA does not
        return a response to *OPC? (the SCPI complete query) until the sweep is
        complete.

    """
    agilentE5062A.clear()
    agilentE5062A.reset()
    agilentE5062A.trigger_source = 'BUS'
    for ch in agilentE5062A.channels.values():
        ch.trigger_continuous = False
        agilentE5062A.abort()
        ch.trigger_initiate()
        agilentE5062A.trigger_single()
        agilentE5062A.wait_for_complete()
    agilentE5062A.trigger_source = 'INT'
    agilentE5062A.trigger_continuous = True
    assert not agilentE5062A.pop_err()[0]
