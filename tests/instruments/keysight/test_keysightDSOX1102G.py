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

import logging

import pytest

from pymeasure.instruments.keysight.keysightDSOX1102G import KeysightDSOX1102G
from pymeasure.test import expected_protocol


# Channel number used in single-channel tests
CH = 1


# ---------------------------
# Channel properties
# ---------------------------

@pytest.mark.parametrize("ch_number", [1, 2])
@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_ch_bwlimit(ch_number, state, as_int):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:BWLimit?", as_int),
            (f":channel{ch_number}:BWLimit {as_int}", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).bwlimit is state
        inst.ch(ch_number).bwlimit = state


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("ch_number", [1, 2])
@pytest.mark.parametrize("case, mapped", [("ac", "AC"), ("dc", "DC")])
def test_ch_coupling(ch_number, case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:COUPling?", mapped),
            (f":channel{ch_number}:COUPling {mapped}", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).coupling == case
        inst.ch(ch_number).coupling = case


@pytest.mark.parametrize("ch_number", [1, 2])
@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_ch_display(ch_number, state, as_int):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:DISPlay?", as_int),
            (f":channel{ch_number}:DISPlay {as_int}", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).display is state
        inst.ch(ch_number).display = state


@pytest.mark.parametrize("ch_number", [1, 2])
@pytest.mark.parametrize("state, as_int", [(True, 1), (False, 0)])
def test_ch_invert(ch_number, state, as_int):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:INVert?", as_int),
            (f":channel{ch_number}:INVert {as_int}", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).invert is state
        inst.ch(ch_number).invert = state


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("ch_number", [1, 2])
def test_ch_label_get(ch_number):
    # Device returns quoted, uppercased label
    with expected_protocol(
        KeysightDSOX1102G,
        [(f":channel{ch_number}:LABel?", '"MYLABEL"')],
    ) as inst:
        assert inst.ch(ch_number).label == '"MYLABEL"'


@pytest.mark.parametrize("ch_number", [1, 2])
def test_ch_label_set(ch_number):
    with expected_protocol(
        KeysightDSOX1102G,
        [(f':channel{ch_number}:LABel "label"', None)],
    ) as inst:
        inst.ch(ch_number).label = "label"


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
def test_ch_label_truncation_and_uppercase():
    # Device truncates long labels to 10 chars and uppercases them; the getter
    # returns the quoted string as the device returns it.
    with expected_protocol(
        KeysightDSOX1102G,
        [(f":channel{CH}:LABel?", '"QUITE LONG"')],
    ) as inst:
        assert inst.ch(CH).label == '"QUITE LONG"'


@pytest.mark.parametrize("ch_number", [1, 2])
def test_ch_offset(ch_number):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:OFFSet?", "1.000000"),
            (f":channel{ch_number}:OFFSet 1.000000", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).offset == 1.0
        inst.ch(ch_number).offset = 1


@pytest.mark.parametrize("ch_number", [1, 2])
def test_ch_probe_attenuation(ch_number):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:PROBe?", "10.000000"),
            (f":channel{ch_number}:PROBe 10.000000", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).probe_attenuation == 10.0
        inst.ch(ch_number).probe_attenuation = 10


def test_ch_probe_attenuation_out_of_range():
    with expected_protocol(KeysightDSOX1102G, []) as inst:
        with pytest.raises(ValueError):
            inst.ch(CH).probe_attenuation = 0.01


@pytest.mark.parametrize("ch_number", [1, 2])
def test_ch_range(ch_number):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:RANGe?", "10.000000"),
            (f":channel{ch_number}:RANGe 10.000000", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).range == 10.0
        inst.ch(ch_number).range = 10


@pytest.mark.parametrize("ch_number", [1, 2])
def test_ch_scale(ch_number):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{ch_number}:SCALe?", "0.100000"),
            (f":channel{ch_number}:SCALe 0.100000", None),
        ],
    ) as inst:
        assert inst.ch(ch_number).scale == 0.1
        inst.ch(ch_number).scale = 0.1


# ---------------------------
# Channel.current_configuration
# ---------------------------

def test_ch_current_configuration():
    raw = (':CHAN1:RANG +40.0E+00;OFFS +0.00000E+00;COUP DC;IMP ONEM;DISP 1;BWL 0;'
           'INV 0;LAB "1";UNIT VOLT;PROB +10E+00;PROB:SKEW +0.00E+00;STYP SING')
    expected = {
        "CHAN": 1,
        "OFFS": 0.0,
        "RANG": 40.0,
        "COUP": "DC",
        "IMP": "ONEM",
        "DISP": True,
        "BWL": False,
        "INV": False,
        "LAB": '"1"',
        "UNIT": "VOLT",
        "PROB": 10.0,
        "PROB:SKEW": 0.0,
        "STYP": "SING",
    }
    with expected_protocol(
        KeysightDSOX1102G,
        [(":channel1?", raw)],
    ) as inst:
        assert inst.ch(1).current_configuration == expected


# ---------------------------
# Channel.setup
# ---------------------------

def test_ch_setup_warns_when_both_range_and_scale_given(caplog):
    caplog.set_level(logging.WARNING)
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{CH}:RANGe 1.000000", None),
            (f":channel{CH}:SCALe 1.000000", None),
        ],
    ) as inst:
        inst.ch(CH).setup(vertical_range=1, scale=1)
    assert 'Both "vertical_range" and "scale" are specified.' in caplog.text


def test_ch_setup_only_specified_parameters_sent():
    # Only probe_attenuation is specified; no other channel commands should be sent.
    with expected_protocol(
        KeysightDSOX1102G,
        [(f":channel{CH}:PROBe 10.000000", None)],
    ) as inst:
        inst.ch(CH).setup(probe_attenuation=10)


def test_ch_setup_full():
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (f":channel{CH}:PROBe 10.000000", None),
            (f":channel{CH}:BWLimit 0", None),
            (f":channel{CH}:COUPling DC", None),
            (f":channel{CH}:DISPlay 1", None),
            (f":channel{CH}:INVert 0", None),
            (f':channel{CH}:LABel "LABEL"', None),
            (f":channel{CH}:OFFSet 0.000000", None),
            (f":channel{CH}:RANGe 8.000000", None),
            (f":channel{CH}:SCALe 0.100000", None),
        ],
    ) as inst:
        inst.ch(CH).setup(
            bwlimit=False,
            coupling="dc",
            display=True,
            invert=False,
            label="LABEL",
            offset=0,
            probe_attenuation=10,
            vertical_range=8,
            scale=0.1,
        )


# ---------------------------
# Timebase properties
# ---------------------------

@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("case, mapped", [
    ("main", "MAIN"), ("window", "WIND"), ("xy", "XY"), ("roll", "ROLL"),
])
def test_timebase_mode(case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":TIMebase:MODE?", mapped),
            (f":TIMebase:MODE {mapped}", None),
        ],
    ) as inst:
        assert inst.timebase_mode == case
        inst.timebase_mode = case


def test_timebase_offset():
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":TIMebase:POSition?", "1.000000"),
            (":TIMebase:REFerence CENTer;:TIMebase:POSition 1.000000", None),
        ],
    ) as inst:
        assert inst.timebase_offset == 1.0
        inst.timebase_offset = 1


def test_timebase_range():
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":TIMebase:RANGe?", "1.000000"),
            (":TIMebase:RANGe 1.000000", None),
        ],
    ) as inst:
        assert inst.timebase_range == 1.0
        inst.timebase_range = 1


def test_timebase_scale():
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":TIMebase:SCALe?", "0.100000"),
            (":TIMebase:SCALe 0.100000", None),
        ],
    ) as inst:
        assert inst.timebase_scale == 0.1
        inst.timebase_scale = 0.1


def test_timebase_property():
    raw = ":TIM:MODE MAIN;REF CENT;MAIN:RANG +1.00E-03;POS +0.0E+00"
    expected = {"REF": "CENT", "MAIN:RANG": 1.0e-3, "POS": 0.0, "MODE": "MAIN"}
    with expected_protocol(
        KeysightDSOX1102G,
        [(":timebase?", raw)],
    ) as inst:
        assert inst.timebase == expected


def test_timebase_setup():
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":TIMebase:MODE MAIN", None),
            (":TIMebase:REFerence CENTer;:TIMebase:POSition 1.000000", None),
            (":TIMebase:RANGe 1.000000", None),
            (":TIMebase:SCALe 0.100000", None),
        ],
    ) as inst:
        inst.timebase_setup(mode="main", offset=1, horizontal_range=1, scale=0.1)


def test_timebase_setup_partial():
    with expected_protocol(
        KeysightDSOX1102G,
        [(":TIMebase:MODE ROLL", None)],
    ) as inst:
        inst.timebase_setup(mode="roll")


# ---------------------------
# Acquisition properties
# ---------------------------

@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("case, mapped", [
    ("normal", "NORM"), ("average", "AVER"),
    ("hresolution", "HRES"), ("peak", "PEAK"),
])
def test_acquisition_type(case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":ACQuire:TYPE?", mapped),
            (f":ACQuire:TYPE {mapped}", None),
        ],
    ) as inst:
        assert inst.acquisition_type == case
        inst.acquisition_type = case


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("case, mapped", [
    ("realtime", "RTIM"), ("segmented", "SEGM"),
])
def test_acquisition_mode(case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":ACQuire:MODE?", mapped),
            (f":ACQuire:MODE {mapped}", None),
        ],
    ) as inst:
        assert inst.acquisition_mode == case
        inst.acquisition_mode = case


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("case, mapped", [
    ("normal", "NORM"), ("maximum", "MAX"), ("raw", "RAW"),
])
def test_waveform_points_mode(case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:points:mode?", mapped),
            (f":waveform:points:mode {mapped}", None),
        ],
    ) as inst:
        assert inst.waveform_points_mode == case
        inst.waveform_points_mode = case


@pytest.mark.parametrize("points", [100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000, 62500])
def test_waveform_points(points):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:points?", str(points)),
            (f":waveform:points {points}", None),
        ],
    ) as inst:
        assert inst.waveform_points == points
        inst.waveform_points = points


def test_waveform_points_out_of_range():
    with expected_protocol(KeysightDSOX1102G, []) as inst:
        with pytest.raises(ValueError):
            inst.waveform_points = 7


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("case, mapped", [
    ("channel1", "CHAN1"), ("channel2", "CHAN2"), ("function", "FUNC"),
    ("fft", "FFT"), ("wmemory1", "WMEM1"), ("wmemory2", "WMEM2"), ("ext", "EXT"),
])
def test_waveform_source(case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:source?", mapped),
            (f":waveform:source {mapped}", None),
        ],
    ) as inst:
        assert inst.waveform_source == case
        inst.waveform_source = case


@pytest.mark.filterwarnings("ignore:Cannot cast.*:FutureWarning")
@pytest.mark.parametrize("case, mapped", [
    ("ascii", "ASC"), ("word", "WORD"), ("byte", "BYTE"),
])
def test_waveform_format(case, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:format?", mapped),
            (f":waveform:format {mapped}", None),
        ],
    ) as inst:
        assert inst.waveform_format == case
        inst.waveform_format = case


# ---------------------------
# waveform_preamble
# ---------------------------

def test_waveform_preamble():
    # format=4 -> ASCII, type=0 -> NORMAL
    raw_preamble = "4,0,62500,1,1.6E-08,-5.0E-04,0,7.851759E-04,0,32768"
    expected = {
        "format": "ASCII",
        "type": "NORMAL",
        "points": 62500,
        "count": 1,
        "xincrement": 1.6e-08,
        "xorigin": -5.0e-04,
        "xreference": 0,
        "yincrement": 7.851759e-04,
        "yorigin": 0.0,
        "yreference": 32768,
    }
    with expected_protocol(
        KeysightDSOX1102G,
        [(":waveform:preamble?", raw_preamble)],
    ) as inst:
        preamble = inst.waveform_preamble
        assert preamble == expected
        # type checks
        assert isinstance(preamble["format"], str)
        assert isinstance(preamble["type"], str)
        assert isinstance(preamble["points"], int)
        assert isinstance(preamble["count"], int)
        assert isinstance(preamble["xreference"], int)
        assert isinstance(preamble["yreference"], int)
        assert isinstance(preamble["xincrement"], float)
        assert isinstance(preamble["xorigin"], float)
        assert isinstance(preamble["yincrement"], float)
        assert isinstance(preamble["yorigin"], float)


@pytest.mark.parametrize("format_int, format_str", [(0, "BYTE"), (1, "WORD"), (4, "ASCII")])
def test_waveform_preamble_format_mapping(format_int, format_str):
    raw_preamble = f"{format_int},0,100,1,1.0E-08,0,0,1.0E-03,0,0"
    with expected_protocol(
        KeysightDSOX1102G,
        [(":waveform:preamble?", raw_preamble)],
    ) as inst:
        assert inst.waveform_preamble["format"] == format_str


@pytest.mark.parametrize("type_int, type_str", [
    (0, "NORMAL"), (1, "PEAK DETECT"), (2, "AVERAGE"), (3, "HRES"),
])
def test_waveform_preamble_type_mapping(type_int, type_str):
    raw_preamble = f"4,{type_int},100,1,1.0E-08,0,0,1.0E-03,0,0"
    with expected_protocol(
        KeysightDSOX1102G,
        [(":waveform:preamble?", raw_preamble)],
    ) as inst:
        assert inst.waveform_preamble["type"] == type_str


# ---------------------------
# waveform_data
# ---------------------------

def test_waveform_data_forces_ascii_and_strips_header():
    # waveform_data setter first sets format to ascii, then queries data.
    # Device returns an IEEE 488.2 arbitrary block: '#9' header, 9-digit
    # length, then data values. The first data value is concatenated to the
    # header (no separator); the code strips the first 10 characters.
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:format ASC", None),
            (":waveform:data?", "#90000001001.0,2.0,3.0"),
        ],
    ) as inst:
        data = inst.waveform_data
        assert data == [1.0, 2.0, 3.0]


def test_waveform_data_single_element():
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:format ASC", None),
            (":waveform:data?", "#9000000030.5"),
        ],
    ) as inst:
        assert inst.waveform_data == [0.5]


# ---------------------------
# System methods
# ---------------------------

def test_autoscale():
    with expected_protocol(
        KeysightDSOX1102G,
        [(":autoscale", None)],
    ) as inst:
        inst.autoscale()


def test_run():
    with expected_protocol(
        KeysightDSOX1102G,
        [(":run", None)],
    ) as inst:
        inst.run()


def test_stop():
    with expected_protocol(
        KeysightDSOX1102G,
        [(":stop", None)],
    ) as inst:
        inst.stop()


def test_single():
    with expected_protocol(
        KeysightDSOX1102G,
        [(":single", None)],
    ) as inst:
        inst.single()


@pytest.mark.parametrize("source, mapped", [
    ("channel1", "CHAN1"), ("channel2", "CHAN2"), ("function", "FUNC"),
    ("math", "MATH"), ("fft", "FFT"), ("abus", "ABUS"), ("ext", "EXT"),
])
def test_digitize(source, mapped):
    with expected_protocol(
        KeysightDSOX1102G,
        [(f":DIGitize {mapped}", None)],
    ) as inst:
        inst.digitize(source)


def test_clear_status():
    with expected_protocol(
        KeysightDSOX1102G,
        [("*CLS", None)],
    ) as inst:
        inst.clear_status()


def test_factory_reset():
    with expected_protocol(
        KeysightDSOX1102G,
        [("*RST", None)],
    ) as inst:
        inst.factory_reset()


def test_default_setup():
    with expected_protocol(
        KeysightDSOX1102G,
        [(":SYSTem:PRESet", None)],
    ) as inst:
        inst.default_setup()


def test_system_setup_get():
    setup_string = ":SYS:SETUP some-data-block"
    with expected_protocol(
        KeysightDSOX1102G,
        [(":system:setup?", setup_string)],
    ) as inst:
        assert inst.system_setup == setup_string


def test_system_setup_set():
    setup_string = ":SYS:SETUP some-data-block"
    with expected_protocol(
        KeysightDSOX1102G,
        [(f":system:setup {setup_string}", None)],
    ) as inst:
        inst.system_setup = setup_string


def test_ch_valid_returns_channel():
    with expected_protocol(KeysightDSOX1102G, []) as inst:
        assert inst.ch(1) is inst.ch1
        assert inst.ch(2) is inst.ch2


def test_ch_invalid_raises_value_error():
    with expected_protocol(KeysightDSOX1102G, []) as inst:
        with pytest.raises(ValueError):
            inst.ch(3)


# ---------------------------
# download_data
# ---------------------------

def test_download_data():
    preamble_raw = "4,0,100,1,1.6E-08,-5.0E-04,0,7.851759E-04,0,32768"
    with expected_protocol(
        KeysightDSOX1102G,
        [
            (":waveform:source CHAN1", None),
            (":waveform:points:mode NORM", None),
            (":waveform:points 100", None),
            (":waveform:preamble?", preamble_raw),
            (":waveform:format ASC", None),
            (":waveform:data?", "#90000001001.0,2.0,3.0"),
        ],
    ) as inst:
        data, preamble = inst.download_data(source="channel1", points=100)
        assert data.tolist() == [1.0, 2.0, 3.0]
        assert preamble["format"] == "ASCII"
        assert preamble["points"] == 100


def test_download_data_missing_argument():
    with expected_protocol(KeysightDSOX1102G, []) as inst:
        with pytest.raises(TypeError):
            inst.download_data()
