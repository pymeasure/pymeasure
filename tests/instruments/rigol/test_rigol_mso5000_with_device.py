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
transfer settings, ``test_awg_loopback_control`` drives a 1 kHz, 1 Vpp sine from
G1 into CH2, and ``test_network_description_write_readback`` temporarily changes
the inactive network description. These tests restore their previous values before
returning. The suite does not apply network configuration or issue reset, autoscale,
self-test, front-panel emulation, setup upload/recall, or instrument-file write commands.
"""

import time

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


def test_measurement_readback(scope):
    sources = [
        *[f"D{number}" for number in range(16)],
        *[f"CHAN{number}" for number in range(1, 5)],
        *[f"MATH{number}" for number in range(1, 5)],
    ]
    assert scope.measurements.source in sources
    assert scope.measurements.mode in ["NORM", "PREC"]
    assert scope.measurements.am_source in [
        "CHAN1",
        "CHAN2",
        "CHAN3",
        "CHAN4",
        "OFF",
    ]
    assert -100 <= scope.measurements.setup_max <= 100
    assert -100 <= scope.measurements.setup_mid <= 100
    assert -100 <= scope.measurements.setup_min <= 100
    assert scope.measurements.setup_primary_source_a in sources
    assert scope.measurements.setup_primary_source_b in sources
    assert scope.measurements.setup_digital_source_a in sources
    assert scope.measurements.setup_digital_source_b in sources
    assert isinstance(scope.measurements.statistics_display_enabled, bool)
    assert scope.measurements.area in ["MAIN", "ZOOM", "CURS"]
    assert 0 <= scope.measurements.cregion_cursor_a_x <= 1000
    assert 0 <= scope.measurements.cregion_cursor_b_x <= 1000
    assert 0 <= scope.measurements.category <= 2
    assert isinstance(scope.measurements.item("VPP", "CHAN1"), float)
    assert isinstance(scope.measurements.statistic_item("CURR", "VPP", "CHAN1"), float)


def test_reference_signal_measurement(scope):
    """Measure the 1 kHz, approximately 3 V reference output connected to CH1."""
    channel = scope.ch_1
    saved_channel = (
        channel.display_enabled,
        channel.coupling,
        channel.scale,
        channel.offset,
    )
    saved_scope = (
        scope.timebase_mode,
        scope.timebase_scale,
        scope.trigger_mode,
        scope.edge_trigger_source,
        scope.edge_trigger_slope,
        scope.edge_trigger_level,
        scope.trigger_sweep,
        scope.trigger_status != "STOP",
    )

    try:
        channel.display_enabled = True
        channel.coupling = "DC"
        channel.scale = 1
        channel.offset = 0
        scope.timebase_mode = "MAIN"
        scope.timebase_scale = 200e-6
        scope.trigger_mode = "EDGE"
        scope.edge_trigger_source = "CHAN1"
        scope.edge_trigger_slope = "POS"
        scope.edge_trigger_level = 1
        scope.trigger_sweep = "AUTO"
        scope.run()
        time.sleep(2)

        first_frequency = scope.measurements.item("FREQ", "CHAN1")
        first_amplitude = scope.measurements.item("VPP", "CHAN1")
        time.sleep(0.1)
        second_frequency = scope.measurements.item("FREQ", "CHAN1")
        second_amplitude = scope.measurements.item("VPP", "CHAN1")

        assert first_frequency == pytest.approx(1_000, rel=0.05)
        assert first_amplitude == pytest.approx(3, rel=0.2)
        assert second_frequency == pytest.approx(first_frequency, rel=0.01)
        assert second_amplitude == pytest.approx(first_amplitude, rel=0.1)
    finally:
        channel.display_enabled = saved_channel[0]
        channel.coupling = saved_channel[1]
        channel.scale = saved_channel[2]
        channel.offset = saved_channel[3]
        scope.timebase_scale = saved_scope[1]
        scope.timebase_mode = saved_scope[0]
        scope.edge_trigger_source = saved_scope[3]
        scope.edge_trigger_slope = saved_scope[4]
        scope.edge_trigger_level = saved_scope[5]
        scope.trigger_sweep = saved_scope[6]
        scope.trigger_mode = saved_scope[2]
        if saved_scope[7]:
            scope.run()
        else:
            scope.stop()


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


def test_cursor_readback(scope):
    cursor = scope.cursor
    assert isinstance(cursor.measurement_indicator_enabled, bool)
    assert cursor.mode in ["OFF", "MAN", "TRAC", "XY", "MEAS"]
    assert cursor.manual_type in ["TIME", "AMPL"]
    # Remaining cursor queries require a matching active mode on this firmware.


def test_display_readback(scope):
    assert scope.display.type in ["VECT", "DOTS"]
    assert scope.display.grading_time in ["MIN", "0.1", "0.2", "0.5", "1", "2", "5", "10", "INF"]
    assert 1 <= scope.display.waveform_brightness <= 100
    assert scope.display.grid in ["FULL", "HALF", "NONE", "IRE"]
    assert 1 <= scope.display.grid_brightness <= 100
    assert isinstance(scope.display.rulers_enabled, bool)
    assert isinstance(scope.display.color_grading_enabled, bool)


def test_histogram_readback(scope):
    assert isinstance(scope.histogram.enabled, bool)
    assert scope.histogram.type in ["HOR", "VERT", "MEAS"]
    assert scope.histogram.source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "OFF"]
    assert 1 <= scope.histogram.size <= 4
    assert isinstance(scope.histogram.statistics_enabled, bool)
    assert isinstance(scope.histogram.bottom_limit, float)
    assert isinstance(scope.histogram.left_limit, float)
    assert isinstance(scope.histogram.right_limit, float)
    assert isinstance(scope.histogram.top_limit, float)


def test_mask_readback(scope):
    assert isinstance(scope.mask.enabled, bool)
    assert scope.mask.source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert scope.mask.operate in ["RUN", "STOP"]
    assert isinstance(scope.mask.statistics_display_enabled, bool)
    assert 0.01 <= scope.mask.x <= 2
    assert 0.04 <= scope.mask.y <= 2
    assert scope.mask.passed >= 0
    assert scope.mask.failed >= 0
    assert scope.mask.total >= 0


def test_recording_readback(scope):
    assert isinstance(scope.recording.enabled, bool)
    assert isinstance(scope.recording.recording_running, bool)
    assert isinstance(scope.recording.playback_running, bool)
    assert scope.recording.current >= 0
    assert scope.recording.frames >= 1


def test_reference_readback(scope):
    assert isinstance(scope.references.display_enabled, bool)
    assert isinstance(scope.references.label_enabled, bool)
    assert isinstance(scope.references.source(1), str)
    assert isinstance(scope.references.vertical_scale(1), float)
    assert isinstance(scope.references.vertical_offset(1), float)
    assert scope.references.color(1) in ["GRAY", "GRE", "BLUE", "RED", "ORAN"]
    assert isinstance(scope.references.label_content(1), str)


def test_math_readback(scope):
    math_channel = scope.math_1
    assert isinstance(math_channel.display_enabled, bool)
    assert isinstance(math_channel.operator, str)
    assert isinstance(math_channel.source1, str)
    assert isinstance(math_channel.source2, str)
    assert isinstance(math_channel.left_source_1, str)
    assert isinstance(math_channel.left_source_2, str)
    assert isinstance(math_channel.scale, float)
    assert isinstance(math_channel.offset, float)
    assert isinstance(math_channel.inverted, bool)
    assert math_channel.fft_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert isinstance(math_channel.fft_window, str)
    assert math_channel.fft_unit in ["VRMS", "DB"]
    assert isinstance(math_channel.fft_scale, float)
    assert isinstance(math_channel.fft_offset, float)
    assert isinstance(math_channel.fft_horizontal_scale, float)
    assert isinstance(math_channel.fft_horizontal_center, float)
    assert isinstance(math_channel.fft_frequency_start, float)
    assert isinstance(math_channel.fft_frequency_end, float)
    assert isinstance(math_channel.fft_search_enabled, bool)
    assert 1 <= math_channel.fft_search_num <= 15
    assert isinstance(math_channel.fft_search_threshold, float)
    assert isinstance(math_channel.fft_search_excursion, float)
    assert math_channel.fft_search_order in ["AMP", "FREQ"]
    # Filter, logic, and differentiation queries require their matching operator.


def test_search_readback(scope):
    assert scope.search.count >= 0
    assert isinstance(scope.search.enabled, bool)
    assert isinstance(scope.search.mode, str)
    assert scope.search.event >= 0
    assert isinstance(scope.search.edge_slope, str)
    assert isinstance(scope.search.edge_source, str)
    assert isinstance(scope.search.edge_threshold, float)
    assert isinstance(scope.search.pulse_polarity, str)
    assert isinstance(scope.search.pulse_qualifier, str)
    assert isinstance(scope.search.pulse_source, str)
    assert 800e-12 <= scope.search.pulse_upper_width <= 10
    assert 800e-12 <= scope.search.pulse_lower_width <= 10
    assert isinstance(scope.search.pulse_threshold, float)
    assert isinstance(scope.search.runt_polarity, str)
    assert isinstance(scope.search.runt_qualifier, str)
    assert isinstance(scope.search.runt_source, str)
    assert 800e-12 <= scope.search.runt_width_upper <= 10
    assert 800e-12 <= scope.search.runt_width_lower <= 10
    assert isinstance(scope.search.runt_threshold1, float)
    assert isinstance(scope.search.runt_threshold2, float)
    assert isinstance(scope.search.slope_polarity, str)
    assert isinstance(scope.search.slope_qualifier, str)
    assert isinstance(scope.search.slope_source, str)
    assert 800e-12 <= scope.search.slope_time_upper <= 10
    assert 800e-12 <= scope.search.slope_time_lower <= 10
    assert isinstance(scope.search.slope_threshold1, float)
    assert isinstance(scope.search.slope_threshold2, float)
    if scope.search.count:
        assert isinstance(scope.search.value(0), float)


def test_logic_analyzer_readback(scope):
    """Read logic-analyzer configuration with a connected active logic probe."""
    assert isinstance(scope.logic_analyzer.enabled, bool)
    assert scope.logic_analyzer.active_channel in [*[f"D{number}" for number in range(16)], "NONE"]
    assert scope.logic_analyzer.size in ["SMAL", "MED", "LARG"]
    assert isinstance(scope.logic_analyzer.time_calibration, float)
    assert isinstance(scope.logic_analyzer.is_displayed("D0"), bool)
    assert isinstance(scope.d_0.display_enabled, bool)
    assert 0 <= scope.d_0.position <= 31
    assert isinstance(scope.d_0.label, str)
    assert isinstance(scope.pod_1.display_enabled, bool)
    assert -15 <= scope.pod_1.threshold <= 15


@pytest.mark.parametrize(
    "name",
    [
        "mode",
        "display_enabled",
        "format",
        "event_table_enabled",
        "event_format",
        "event_view",
        "label_enabled",
        "position",
        "parallel_bus",
        "parallel_clk",
        "parallel_slope",
        "parallel_width",
        "parallel_bitx",
        "parallel_source",
        "parallel_polarity",
        "parallel_noise_rejection_enabled",
        "parallel_noise_reject_time",
        "rs232_tx",
        "rs232_rx",
        "rs232_polarity",
        "rs232_endian",
        "rs232_baud",
        "rs232_data_bits",
        "rs232_stop_bits",
        "rs232_parity",
        "rs232_packet_enabled",
        "rs232_pend",
        "iic_clock_source",
        "iic_data_source",
        "iic_address",
        "spi_clock_source",
        "spi_clock_slope",
        "spi_miso_source",
        "spi_miso_polarity",
        "spi_mosi_source",
        "spi_mosi_polarity",
        "spi_data_bits",
        "spi_endian",
        "spi_mode",
        "spi_timeout_time",
        "spi_ss_source",
        "spi_ss_polarity",
        "can_source",
        "can_source_type",
        "can_baud",
        "can_sample_point",
        "flexray_baud",
        "flexray_source",
        "flexray_sample_point",
        "flexray_source_type",
        "lin_baud",
        "lin_polarity",
        "lin_source",
        "lin_standard",
        "iis_source_clock",
        "iis_source_data",
        "iis_source_word_select",
        "iis_alignment",
        "iis_clock_slope",
        "iis_right_width",
        "m1553_source",
    ],
)
def test_bus_decoder_readback(scope, name):
    """Read one decoder setting with the matching decoder option installed."""
    assert getattr(scope.bus_1, name) is not None


@pytest.mark.parametrize(
    "name",
    [
        "rs232_source",
        "rs232_when",
        "rs232_parity",
        "rs232_stop",
        "rs232_data",
        "rs232_width",
        "rs232_baud",
        "rs232_level",
        "iic_clock_source",
        "iic_data_source",
        "iic_when",
        "iic_address_width",
        "iic_address",
        "iic_direction",
        "iic_data",
        "iic_clock_level",
        "iic_data_level",
        "iic_data_bytes",
        "can_baud",
        "can_source",
        "can_source_type",
        "can_when",
        "can_sample_point",
        "can_level",
        "spi_clock_source",
        "spi_data_source",
        "spi_when",
        "spi_width",
        "spi_data",
        "spi_timeout",
        "spi_slope",
        "spi_clock_level",
        "spi_data_level",
        "spi_select_level",
        "spi_mode",
        "spi_cs",
        "flexray_baud",
        "flexray_level",
        "flexray_source",
        "flexray_when",
        "iis_alignment",
        "iis_clock_slope",
        "iis_source_clock",
        "iis_source_data",
        "iis_source_word_select",
        "iis_when",
        "iis_audio",
        "iis_data",
        "lin_source",
        "lin_id",
        "lin_baud",
        "lin_standard",
        "lin_sample_point",
        "lin_when",
        "lin_level",
        "m1553_source",
        "m1553_when",
        "m1553_polarity",
        "m1553_alevel",
        "m1553_blevel",
    ],
)
def test_protocol_trigger_readback(scope, name):
    """Read one protocol-trigger setting with the matching trigger option installed."""
    assert getattr(scope.protocol_trigger, name) is not None


def test_quick_operation_readback(scope):
    assert scope.quick.operation in ["SIM", "SWAV", "SSET", "AME", "SRES"]


def test_bode_plot_readback(scope):
    assert isinstance(scope.bode_plot.enabled, bool)
    assert scope.bode_plot.point >= 10
    assert scope.bode_plot.source == "SOURCE1"


def test_counter_integrated_readback(scope):
    assert isinstance(scope.counter.current, float)
    assert isinstance(scope.counter.enabled, bool)
    assert scope.counter.digits in [3, 4, 5, 6]


def test_dvm_integrated_readback(scope):
    assert isinstance(scope.dvm.current, float)
    assert isinstance(scope.dvm.enabled, bool)
    assert scope.dvm.source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]


def test_power_analysis_readback(scope):
    assert scope.power_analysis.type in ["QUAL", "RIPP"]
    assert scope.power_analysis.current_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]
    assert scope.power_analysis.voltage_source in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]


def test_awg_readback(scope):
    assert scope.awg_1.frequency_fixed > 0
    assert scope.awg_1.function_shape in [
        "SIN",
        "SQU",
        "RAMP",
        "PULS",
        "NOIS",
        "DC",
        "SINC",
        "EXPR",
        "EXPF",
        "ECG",
        "GAUS",
        "LOR",
        "HAV",
        "ARB",
    ]
    assert isinstance(scope.awg_1.output_enabled, bool)
    assert len(scope.awg_1.get_applied_waveform()) == 5


def test_awg_loopback_control(scope):
    """Control G1 and verify its 1 kHz, 1 Vpp sine through the CH2 loopback."""
    awg = scope.awg_1
    channel = scope.ch_2
    saved_awg = (
        awg.output_enabled,
        awg.output_impedance,
        awg.function_shape,
        awg.frequency_fixed,
        awg.voltage_level_immediate_amplitude,
        awg.voltage_level_immediate_offset,
        awg.phase_adjust,
    )
    saved_channel = (
        channel.display_enabled,
        channel.coupling,
        channel.probe,
        channel.scale,
        channel.offset,
    )
    saved_scope = (
        scope.timebase_mode,
        scope.timebase_scale,
        scope.trigger_mode,
        scope.edge_trigger_source,
        scope.edge_trigger_slope,
        scope.edge_trigger_level,
        scope.trigger_sweep,
        scope.trigger_status != "STOP",
    )

    try:
        awg.output_enabled = False
        awg.output_impedance = "OMEG"
        awg.apply_sine(1_000, 1, 0, 0)
        assert awg.function_shape == "SIN"
        assert awg.frequency_fixed == pytest.approx(1_000)
        assert awg.voltage_level_immediate_amplitude == pytest.approx(1)
        assert awg.voltage_level_immediate_offset == pytest.approx(0)

        channel.display_enabled = True
        channel.coupling = "DC"
        channel.probe = 1
        channel.scale = 0.2
        channel.offset = 0
        scope.timebase_mode = "MAIN"
        scope.timebase_scale = 200e-6
        scope.trigger_mode = "EDGE"
        scope.edge_trigger_source = "CHAN2"
        scope.edge_trigger_slope = "POS"
        scope.edge_trigger_level = 0
        scope.trigger_sweep = "AUTO"
        scope.run()

        awg.output_enabled = True
        time.sleep(0.5)
        assert awg.output_enabled is True
        assert scope.measurements.item("FREQ", "CHAN2") == pytest.approx(1_000, rel=0.05)
        assert scope.measurements.item("VPP", "CHAN2") == pytest.approx(1, rel=0.3)
    finally:
        awg.output_enabled = False
        awg.output_impedance = saved_awg[1]
        awg.function_shape = saved_awg[2]
        awg.frequency_fixed = saved_awg[3]
        awg.voltage_level_immediate_amplitude = saved_awg[4]
        awg.voltage_level_immediate_offset = saved_awg[5]
        awg.phase_adjust = saved_awg[6]

        channel.display_enabled = saved_channel[0]
        channel.coupling = saved_channel[1]
        channel.probe = saved_channel[2]
        channel.scale = saved_channel[3]
        channel.offset = saved_channel[4]
        scope.timebase_scale = saved_scope[1]
        scope.timebase_mode = saved_scope[0]
        scope.edge_trigger_source = saved_scope[3]
        scope.edge_trigger_slope = saved_scope[4]
        scope.edge_trigger_level = saved_scope[5]
        scope.trigger_sweep = saved_scope[6]
        scope.trigger_mode = saved_scope[2]
        if saved_scope[7]:
            scope.run()
        else:
            scope.stop()
        awg.output_enabled = saved_awg[0]
        # Firmware 00.01.03.03.00 drops queries sent immediately after AWG restoration.
        time.sleep(1)


def test_network_description_write_readback(scope):
    saved = scope.network.description
    try:
        scope.network.description = "PYMEASURE_TEST"
        assert scope.network.description == "PYMEASURE_TEST"
    finally:
        scope.network.description = saved
    assert scope.network.description == saved


def test_network_readback(scope):
    assert isinstance(scope.network.dhcp_enabled, bool)
    assert isinstance(scope.network.auto_ip_enabled, bool)
    assert isinstance(scope.network.static_ip_enabled, bool)
    assert isinstance(scope.network.mdns_enabled, bool)
    assert isinstance(scope.network.gateway, str)
    assert isinstance(scope.network.dns, str)
    assert isinstance(scope.network.ip_address, str)
    assert isinstance(scope.network.subnet_mask, str)
    assert isinstance(scope.network.mac_address, str)
    assert scope.network.status in [
        "UNLINK",
        "CONNECTED",
        "INIT",
        "IPCONFLICT",
        "BUSY",
        "CONFIGURED",
        "DHCPFAILED",
        "INVALIDIP",
        "IPLOSE",
    ]
    assert isinstance(scope.network.visa_address, str)
    assert isinstance(scope.network.host_name, str)
    assert isinstance(scope.network.description, str)
