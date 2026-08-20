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

"""Run readback checks against a real Rigol MSO5000 oscilloscope.

Invoke this module with ``--device-address``. Most tests only query the current
configuration. ``test_waveform_data_transfer`` temporarily changes waveform
transfer settings and restores them before returning. The suite does not issue
reset, autoscale, self-test, front-panel emulation, setup upload/recall, or
instrument-file write commands.
"""

import pytest

from pymeasure.instruments.rigol import MSO5000

SUPPORTED_MODELS = {"MSO5072", "MSO5074", "MSO5102", "MSO5104", "MSO5204", "MSO5354"}


@pytest.fixture(scope="module")
def scope(connected_device_address):
    """Connect to an MSO5000 and verify that the requested model is supported."""
    instrument = MSO5000(connected_device_address)
    identification = instrument.id
    manufacturer, model, *_ = identification.split(",")
    if manufacturer != "RIGOL TECHNOLOGIES" or model not in SUPPORTED_MODELS:
        instrument.shutdown()
        pytest.fail(f"Expected a supported Rigol MSO5000, received {identification!r}.")
    yield instrument
    instrument.shutdown()


def test_acquisition_readback(scope):
    assert scope.acquisition_averages in [2**n for n in range(1, 17)]
    assert scope.acquisition_memory_depth > 0
    assert scope.acquisition_type in ["NORM", "AVER", "PEAK", "HRES"]
    assert scope.sample_rate > 0
    assert scope.logic_analyzer_sample_rate > 0
    assert scope.logic_analyzer_memory_depth > 0
    assert isinstance(scope.anti_aliasing_enabled, bool)


def test_ieee4882_status_readback(scope):
    assert scope.complete == "1"
    assert 0 <= int(scope.status) <= 255
    assert 0 <= scope.event_status_enable_bits <= 255
    assert 0 <= scope.service_request_enable_bits <= 255
    assert 0 <= scope.query_event_status_register() <= 255


def test_persistence_readback(scope):
    screenshot = scope.download_screenshot()
    assert screenshot.startswith(b"BM")
    assert len(screenshot) > 54

    setup = scope.download_setup()
    assert len(setup) > 0

    assert scope.csv_length in ["DISP", "MAX"]
    assert scope.image_type in ["BMP24", "JPEG", "PNG", "TIFF"]
    assert isinstance(scope.image_inverted, bool)
    assert scope.image_color in ["COL", "GRAY"]
    assert isinstance(scope.save_complete, bool)
    for channel in ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "POD1", "POD2"]:
        assert isinstance(scope.get_csv_channel_enabled(channel), bool)


def test_system_readback(scope):
    assert scope.auxiliary_output in ["TOUT", "PFA"]
    assert isinstance(scope.autoscale_enabled, bool)
    assert isinstance(scope.beeper_enabled, bool)

    year, month, day = scope.system_date
    assert 2017 <= year <= 2099
    assert 1 <= month <= 12
    assert 1 <= day <= 31

    assert scope.horizontal_grid_count == 10
    assert 1 <= scope.gpib_address <= 30
    assert scope.system_language in [
        "SCH",
        "TCH",
        "KOR",
        "JAP",
        "ENGL",
        "GERM",
        "PORT",
        "POL",
        "FREN",
        "RUSS",
        "SPAN",
        "THAI",
        "IND",
    ]
    assert scope.power_on_configuration in ["LAT", "DEF"]
    assert scope.analog_channel_count in [2, 4]
    screen_saver_time = scope.screen_saver_time
    assert screen_saver_time == "OFF" or 1 <= screen_saver_time <= 999

    hours, minutes, seconds = scope.system_time
    assert 0 <= hours <= 23
    assert 0 <= minutes <= 59
    assert 0 <= seconds <= 59

    assert isinstance(scope.front_panel_locked, bool)
    modules = scope.hardware_modules
    assert len(modules) == 5
    assert all(value in [0, 1] for value in modules)

    for option in [
        "BW071",
        "BW072",
        "BW073",
        "BW12",
        "BW13",
        "BW23",
        "RL2",
        "4CH",
        "BND",
        "COMP",
        "EMBD",
        "AUTO",
        "FLEX",
        "AUDIO",
        "AERO",
        "AWG",
        "PWR",
    ]:
        assert isinstance(scope.option_status(option), bool)

    error = scope.next_error
    assert isinstance(error, list)
    assert len(error) == 2


def test_channel_readback(scope):
    for number in range(1, scope.analog_channel_count + 1):
        channel = getattr(scope, f"ch_{number}")
        assert channel.bandwidth_limit in ["20M", "100M", "200M", "OFF"]
        assert channel.coupling in ["AC", "DC", "GND"]
        assert isinstance(channel.display_enabled, bool)
        assert isinstance(channel.invert, bool)
        assert isinstance(channel.offset, float)
        assert channel.scale > 0
        assert channel.probe > 0
        assert channel.units in ["VOLT", "WATT", "AMP", "UNKN"]
        assert isinstance(channel.vernier_enabled, bool)


def test_timebase_readback(scope):
    assert isinstance(scope.delayed_sweep_enabled, bool)
    assert isinstance(scope.delayed_timebase_offset, float)
    assert scope.delayed_timebase_scale > 0
    assert isinstance(scope.timebase_offset, float)
    assert scope.timebase_scale > 0
    assert scope.timebase_mode in ["MAIN", "XY", "ROLL"]
    assert scope.horizontal_reference_mode in ["CENT", "LB", "RB", "TRIG", "USER"]
    assert -500 <= scope.horizontal_reference_position <= 500
    assert isinstance(scope.timebase_vernier_enabled, bool)


def test_waveform_metadata_readback(scope):
    assert scope.waveform_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
        *[f"MATH{number}" for number in range(1, 5)],
    ]
    assert scope.waveform_mode in ["NORM", "MAX", "RAW"]
    assert scope.waveform_format in ["WORD", "BYTE", "ASC"]
    assert scope.waveform_points > 0
    assert scope.waveform_x_increment > 0
    assert isinstance(scope.waveform_x_origin, float)
    assert scope.waveform_x_reference == 0
    assert scope.waveform_y_increment > 0
    assert isinstance(scope.waveform_y_origin, float)
    assert scope.waveform_y_reference == 128
    assert scope.waveform_start > 0
    assert scope.waveform_stop > 0
    assert len(scope.get_waveform_preamble()) == 10


def test_waveform_data_transfer(scope):
    saved = (
        scope.waveform_source,
        scope.waveform_mode,
        scope.waveform_format,
        scope.waveform_start,
        scope.waveform_stop,
    )
    try:
        scope.waveform_source = "CHAN1"
        scope.waveform_mode = "NORM"
        scope.waveform_start = 1
        scope.waveform_stop = 1000

        scope.waveform_format = "BYTE"
        byte_data = scope.waveform_data()
        assert len(byte_data) == 1000
        assert byte_data.dtype.name == "uint8"

        scope.waveform_format = "ASC"
        ascii_data = scope.waveform_data()
        assert len(ascii_data) == 1000
        assert ascii_data.dtype.name == "float64"

        scope.waveform_format = "WORD"
        try:
            word_data = scope.waveform_data()
        except ValueError as error:
            assert "beyond its declared IEEE block length" in str(error) or (
                "non-zero upper bytes" in str(error)
            )
        else:
            assert len(word_data) == 1000
            assert word_data.dtype.name == "uint16"
    finally:
        scope.adapter.flush_read_buffer()
        scope.waveform_source = saved[0]
        scope.waveform_mode = saved[1]
        scope.waveform_format = saved[2]
        scope.waveform_start = saved[3]
        scope.waveform_stop = saved[4]


def test_trigger_readback(scope):
    assert scope.trigger_mode in [
        "EDGE",
        "PULS",
        "SLOP",
        "VID",
        "PATT",
        "DUR",
        "TIM",
        "RUNT",
        "WIND",
        "DEL",
        "SET",
        "NEDG",
        "RS232",
        "IIC",
        "SPI",
        "CAN",
        "CANF",
        "FLEX",
        "LIN",
        "IIS",
        "M1553",
    ]
    assert scope.trigger_coupling in ["AC", "DC", "LFR", "HFR"]
    assert scope.trigger_status in ["TD", "WAIT", "RUN", "AUTO", "STOP"]
    assert scope.trigger_sweep in ["AUTO", "NORM", "SING"]
    assert 8e-9 <= scope.trigger_holdoff <= 10
    assert isinstance(scope.trigger_noise_rejection_enabled, bool)
    assert scope.edge_trigger_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
        "ACL",
    ]
    assert scope.edge_trigger_slope in ["POS", "NEG", "RFAL"]
    assert isinstance(scope.edge_trigger_level, float)


def test_pulse_trigger_readback(scope):
    assert scope.pulse_trigger_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    assert scope.pulse_trigger_condition in ["GRE", "LESS", "GLES"]
    assert 8e-10 <= scope.pulse_trigger_lower_width <= scope.pulse_trigger_upper_width
    assert scope.pulse_trigger_upper_width <= 10
    assert isinstance(scope.pulse_trigger_level, float)


def test_slope_trigger_readback(scope):
    assert scope.slope_trigger_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert scope.slope_trigger_condition in ["GRE", "LESS", "GLES"]
    assert 8e-10 <= scope.slope_trigger_lower_time <= scope.slope_trigger_upper_time
    assert scope.slope_trigger_upper_time <= 10
    assert scope.slope_trigger_window in ["TA", "TB", "TAB"]
    assert scope.slope_trigger_lower_level <= scope.slope_trigger_upper_level


def test_video_trigger_readback(scope):
    assert scope.video_trigger_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert scope.video_trigger_polarity in ["POS", "NEG"]
    assert scope.video_trigger_mode in ["ODDF", "EVEN", "LINE", "ALIN"]
    assert scope.video_trigger_line > 0
    assert scope.video_trigger_standard in [
        "PALS",
        "NTSC",
        "480P",
        "576P",
        "720P60",
        "720P50",
        "720P30",
        "720P25",
        "720P24",
        "1080P60",
        "1080P50",
        "1080P30",
        "1080P25",
        "1080P24",
        "1080I60",
        "1080I50",
    ]
    assert isinstance(scope.video_trigger_level, float)


def test_timeout_trigger_readback(scope):
    assert scope.timeout_trigger_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    assert scope.timeout_trigger_slope in ["POS", "NEG", "RFAL"]
    assert 16e-9 <= scope.timeout_trigger_time <= 10
    assert isinstance(scope.timeout_trigger_level, float)


def test_window_trigger_readback(scope):
    assert scope.window_trigger_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert scope.window_trigger_slope in ["POS", "NEG", "RFAL"]
    assert scope.window_trigger_position in ["EXIT", "ENT", "TIME"]
    assert 8e-9 <= scope.window_trigger_time <= 10
    assert scope.window_trigger_lower_level <= scope.window_trigger_upper_level


def test_pattern_trigger_readback(scope):
    pattern = scope.pattern_trigger_pattern
    assert len(pattern) == 20
    assert all(value in ["H", "L", "X", "R", "F"] for value in pattern)
    assert sum(value in ["R", "F"] for value in pattern) <= 1
    assert scope.pattern_trigger_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    assert isinstance(scope.get_pattern_trigger_level("CHAN1"), float)


def test_duration_trigger_readback(scope):
    assert scope.duration_trigger_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    pattern = scope.duration_trigger_pattern
    assert len(pattern) == 20
    assert all(value in ["H", "L", "X"] for value in pattern)
    assert scope.duration_trigger_condition in ["GRE", "LESS", "GLES", "UNGL"]
    assert 8e-10 <= scope.duration_trigger_upper_time <= 10
    assert 8e-10 <= scope.duration_trigger_lower_time <= 10
    assert isinstance(scope.get_duration_trigger_level("CHAN1"), float)


def test_runt_trigger_readback(scope):
    assert scope.runt_trigger_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert scope.runt_trigger_polarity in ["POS", "NEG"]
    assert scope.runt_trigger_condition in ["NONE", "GRE", "LESS", "GLES"]
    assert 8.01e-9 <= scope.runt_trigger_upper_width <= 10
    assert 8e-9 <= scope.runt_trigger_lower_width <= 9.9
    assert scope.runt_trigger_lower_level <= scope.runt_trigger_upper_level


def test_delay_trigger_readback(scope):
    sources = [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    assert scope.delay_trigger_source_a in sources
    assert scope.delay_trigger_slope_a in ["POS", "NEG"]
    assert scope.delay_trigger_source_b in sources
    assert scope.delay_trigger_slope_b in ["POS", "NEG"]
    assert scope.delay_trigger_condition in ["GRE", "LESS", "GLES", "GOUT"]
    assert 8.01e-9 <= scope.delay_trigger_upper_time <= 10
    assert 8e-9 <= scope.delay_trigger_lower_time <= 9.9
    assert isinstance(scope.delay_trigger_source_a_level, float)
    assert isinstance(scope.delay_trigger_source_b_level, float)


def test_setup_hold_trigger_readback(scope):
    sources = [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    assert scope.setup_hold_data_source in sources
    assert scope.setup_hold_clock_source in sources
    assert scope.setup_hold_clock_slope in ["POS", "NEG"]
    assert scope.setup_hold_data_pattern in ["H", "L"]
    assert scope.setup_hold_type in ["SET", "HOLD", "SETH"]
    assert 8e-9 <= scope.setup_hold_setup_time <= 1
    assert 8e-9 <= scope.setup_hold_hold_time <= 1
    assert isinstance(scope.setup_hold_data_level, float)
    assert isinstance(scope.setup_hold_clock_level, float)


def test_nth_edge_trigger_readback(scope):
    assert scope.nth_edge_trigger_source in [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
    ]
    assert scope.nth_edge_trigger_slope in ["POS", "NEG"]
    assert 16e-9 <= scope.nth_edge_trigger_idle_time <= 10
    assert 1 <= scope.nth_edge_trigger_edge_count <= 65535
    assert isinstance(scope.nth_edge_trigger_level, float)
