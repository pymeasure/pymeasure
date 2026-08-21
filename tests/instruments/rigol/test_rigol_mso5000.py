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

import math

import pytest

from pymeasure.instruments.rigol import MSO5000
from pymeasure.test import expected_protocol


@pytest.mark.parametrize(
    "name, command, response, expected",
    [
        (
            "id",
            "*IDN?",
            "RIGOL TECHNOLOGIES,MSO5074,SERIAL,00.01",
            "RIGOL TECHNOLOGIES,MSO5074,SERIAL,00.01",
        ),
        ("complete", "*OPC?", "1", "1"),
        ("status", "*STB?", "4", "4"),
    ],
)
def test_inherited_ieee4882_measurements(name, command, response, expected):
    with expected_protocol(MSO5000, [(command, response)]) as instrument:
        assert getattr(instrument, name) == expected


@pytest.mark.parametrize("name, command", [("clear", "*CLS"), ("reset", "*RST")])
def test_inherited_ieee4882_actions(name, command):
    with expected_protocol(MSO5000, [(command, None)]) as instrument:
        getattr(instrument, name)()


@pytest.mark.parametrize(
    "name, command",
    [
        ("event_status_enable_bits", "ESE"),
        ("service_request_enable_bits", "SRE"),
    ],
)
def test_ieee4882_enable_registers(name, command):
    with expected_protocol(
        MSO5000,
        [(f"*{command} 21", None), (f"*{command}?", "21")],
    ) as instrument:
        setattr(instrument, name, 21)
        assert getattr(instrument, name) == 21


@pytest.mark.parametrize("name", ["event_status_enable_bits", "service_request_enable_bits"])
@pytest.mark.parametrize("value", [-1, 256])
def test_ieee4882_enable_registers_reject_out_of_range_values(name, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        setattr(instrument, name, value)


def test_query_event_status_register():
    with expected_protocol(MSO5000, [("*ESR?", "32")]) as instrument:
        assert instrument.query_event_status_register() == 32


def test_download_screenshot():
    payload = b"BM\n" + bytes(range(7))
    with expected_protocol(MSO5000, [(":DISP:DATA?", b"#210" + payload + b"\n")]) as instrument:
        assert instrument.download_screenshot() == payload


@pytest.mark.parametrize(
    "method, argument, command",
    [
        ("save_state", 12, "*SAV 12"),
        ("save_reference_waveform", 4, ":REF:SAVE 4"),
        ("save_csv", "D:\\capture.csv", ":SAVE:CSV D:\\capture.csv"),
        ("save_image", "D:\\capture.png", ":SAVE:IMAG D:\\capture.png"),
        ("save_setup", "D:\\capture.stp", ":SAVE:SET D:\\capture.stp"),
        ("save_waveform", "D:\\capture.wfm", ":SAVE:WAV D:\\capture.wfm"),
        ("load_setup", "D:\\capture.stp", ":LOAD:SET D:\\capture.stp"),
    ],
)
def test_persistence_actions(method, argument, command):
    with expected_protocol(MSO5000, [(command, None)]) as instrument:
        getattr(instrument, method)(argument)


def test_recall_state():
    with expected_protocol(MSO5000, [("*RCL", None)]) as instrument:
        instrument.recall_state()


@pytest.mark.parametrize(
    "method, value",
    [
        ("save_state", -1),
        ("save_state", 50),
        ("save_reference_waveform", 0),
        ("save_reference_waveform", 11),
    ],
)
def test_persistence_actions_reject_out_of_range_values(method, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        getattr(instrument, method)(value)


@pytest.mark.parametrize(
    "name, command, value, raw",
    [
        ("csv_length", ":SAVE:CSV:LENG", "MAX", "MAX"),
        ("image_type", ":SAVE:IMAG:TYPE", "JPEG", "JPEG"),
        ("image_color", ":SAVE:IMAG:COL", "GRAY", "GRAY"),
    ],
)
def test_persistence_discrete_controls(name, command, value, raw):
    with expected_protocol(
        MSO5000,
        [(f"{command} {value}", None), (f"{command}?", raw)],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == value


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_image_inverted(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":SAVE:IMAG:INV {raw}", None), (":SAVE:IMAG:INV?", raw)],
    ) as instrument:
        instrument.image_inverted = value
        assert instrument.image_inverted is value


def test_csv_channel_enabled():
    with expected_protocol(
        MSO5000,
        [(":SAVE:CSV:CHAN CHAN2,1", None), (":SAVE:CSV:CHAN? CHAN2", "1")],
    ) as instrument:
        instrument.set_csv_channel_enabled("CHAN2", True)
        assert instrument.get_csv_channel_enabled("CHAN2") is True


def test_save_complete():
    with expected_protocol(MSO5000, [(":SAVE:STAT?", "1")]) as instrument:
        assert instrument.save_complete is True


def test_download_setup():
    payload = b"setup\n=data"
    with expected_protocol(MSO5000, [(":SYST:SET?", b"#211" + payload + b"\n")]) as instrument:
        assert instrument.download_setup() == payload


def test_upload_setup():
    payload = b"setup=data"
    with expected_protocol(MSO5000, [(b":SYST:SET #210" + payload, None)]) as instrument:
        instrument.upload_setup(payload)


def test_upload_setup_rejects_non_bytes():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(TypeError):
        instrument.upload_setup("setup=data")  # pyright: ignore[reportArgumentType]


def test_self_test():
    with expected_protocol(MSO5000, [("*TST?", "0")]) as instrument:
        assert instrument.self_test() == 0


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("auxiliary_output", ":SYST:AOUT", "PFA"),
        ("system_language", ":SYST:LANG", "GERM"),
        ("power_on_configuration", ":SYST:PON", "LAT"),
    ],
)
def test_system_discrete_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f"{command} {value}", None), (f"{command}?", value)],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, command",
    [("autoscale_enabled", "AUT"), ("beeper_enabled", "BEEP"), ("front_panel_locked", "LOCK")],
)
@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_system_boolean_controls(name, command, value, raw):
    with expected_protocol(
        MSO5000,
        [(f":SYST:{command} {raw}", None), (f":SYST:{command}?", raw)],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) is value


@pytest.mark.parametrize(
    "name, command, value, response",
    [
        ("system_date", "DATE", (2026, 8, 19), "2026,8,19"),
        ("system_time", "TIME", (21, 45, 7), "21,45,7"),
    ],
)
def test_system_date_and_time(name, command, value, response):
    with expected_protocol(
        MSO5000,
        [(f":SYST:{command} {response}", None), (f":SYST:{command}?", response)],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, value",
    [
        ("system_date", (2016, 1, 1)),
        ("system_date", (2026, 2, 30)),
        ("system_time", (24, 0, 0)),
        ("system_time", (12, 60, 0)),
    ],
)
def test_system_date_and_time_reject_invalid_values(name, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        setattr(instrument, name, value)


@pytest.mark.parametrize(
    "name, command, value",
    [("gpib_address", "GPIB", 12), ("screen_saver_time", "SSAV:TIME", 45)],
)
def test_system_numeric_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":SYST:{command} {value}", None), (f":SYST:{command}?", str(value))],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == value


def test_screen_saver_time_accepts_off_response():
    with expected_protocol(MSO5000, [(":SYST:SSAV:TIME?", "OFF")]) as instrument:
        assert instrument.screen_saver_time == "OFF"


@pytest.mark.parametrize(
    "name, command, response, expected",
    [
        ("horizontal_grid_count", ":SYST:GAM?", "10", 10),
        ("analog_channel_count", ":SYST:RAM?", "4", 4),
        ("hardware_modules", ":SYST:MOD?", "1,1,0,0,0", [1, 1, 0, 0, 0]),
    ],
)
def test_system_measurements(name, command, response, expected):
    with expected_protocol(MSO5000, [(command, response)]) as instrument:
        assert getattr(instrument, name) == expected


def test_option_status():
    with expected_protocol(MSO5000, [(":SYST:OPT:STAT? AWG", "1")]) as instrument:
        assert instrument.option_status("AWG") is True


def test_option_status_rejects_invalid_option():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.option_status("UNKNOWN")


def test_system_key_actions():
    with expected_protocol(
        MSO5000,
        [
            (":SYST:KEY:PRES CH1", None),
            (":SYST:KEY:INCR VSCALE1", None),
            (":SYST:KEY:DECR HPOSITION,3", None),
        ],
    ) as instrument:
        instrument.press_key("CH1")
        instrument.increase_key("VSCALE1")
        instrument.decrease_key("HPOSITION", 3)


def test_inherited_next_error():
    with expected_protocol(MSO5000, [("SYST:ERR?", '0,"No error"')]) as instrument:
        assert instrument.next_error == [0.0, '"No error"']


def test_channel_bandwidth_limit():
    with expected_protocol(
        MSO5000,
        [(":CHAN1:BWL 20M", None), (":CHAN1:BWL?", "20M")],
    ) as instrument:
        instrument.ch_1.bandwidth_limit = "20M"
        assert instrument.ch_1.bandwidth_limit == "20M"


def test_channel_bandwidth_limit_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.ch_1.bandwidth_limit = "50M"


def test_channel_coupling():
    with expected_protocol(
        MSO5000,
        [(":CHAN1:COUP AC", None), (":CHAN1:COUP?", "AC")],
    ) as instrument:
        instrument.ch_1.coupling = "AC"
        assert instrument.ch_1.coupling == "AC"


def test_channel_coupling_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.ch_1.coupling = "LFREJECT"


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_channel_display_enabled(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":CHAN2:DISP {raw}", None), (":CHAN2:DISP?", raw)],
    ) as instrument:
        instrument.ch_2.display_enabled = value
        assert instrument.ch_2.display_enabled is value


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_channel_invert(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":CHAN1:INV {raw}", None), (":CHAN1:INV?", raw)],
    ) as instrument:
        instrument.ch_1.invert = value
        assert instrument.ch_1.invert is value


def test_channel_offset():
    with expected_protocol(
        MSO5000,
        [(":CHAN1:OFFS 0.01", None), (":CHAN1:OFFS?", "1E-2")],
    ) as instrument:
        instrument.ch_1.offset = 0.01
        assert instrument.ch_1.offset == pytest.approx(0.01)


def test_channel_scale():
    with expected_protocol(
        MSO5000,
        [(":CHAN1:SCAL 0.1", None), (":CHAN1:SCAL?", "1E-1")],
    ) as instrument:
        instrument.ch_1.scale = 0.1
        assert instrument.ch_1.scale == pytest.approx(0.1)


def test_channel_probe():
    with expected_protocol(
        MSO5000,
        [(":CHAN1:PROB 10", None), (":CHAN1:PROB?", "10")],
    ) as instrument:
        instrument.ch_1.probe = 10
        assert instrument.ch_1.probe == pytest.approx(10)


def test_channel_probe_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.ch_1.probe = 7


def test_channel_units():
    with expected_protocol(
        MSO5000,
        [(":CHAN1:UNIT AMP", None), (":CHAN1:UNIT?", "AMP")],
    ) as instrument:
        instrument.ch_1.units = "AMP"
        assert instrument.ch_1.units == "AMP"


def test_channel_units_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.ch_1.units = "DBM"


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_channel_vernier_enabled(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":CHAN1:VERN {raw}", None), (":CHAN1:VERN?", raw)],
    ) as instrument:
        instrument.ch_1.vernier_enabled = value
        assert instrument.ch_1.vernier_enabled is value


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_delayed_sweep_enabled(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":TIM:DEL:ENAB {raw}", None), (":TIM:DEL:ENAB?", raw)],
    ) as instrument:
        instrument.delayed_sweep_enabled = value
        assert instrument.delayed_sweep_enabled is value


def test_delayed_timebase_offset():
    with expected_protocol(
        MSO5000,
        [(":TIM:DEL:OFFS 0.001", None), (":TIM:DEL:OFFS?", "1E-3")],
    ) as instrument:
        instrument.delayed_timebase_offset = 1e-3
        assert instrument.delayed_timebase_offset == pytest.approx(1e-3)


def test_delayed_timebase_scale():
    with expected_protocol(
        MSO5000,
        [(":TIM:DEL:SCAL 1e-06", None), (":TIM:DEL:SCAL?", "1E-6")],
    ) as instrument:
        instrument.delayed_timebase_scale = 1e-6
        assert instrument.delayed_timebase_scale == pytest.approx(1e-6)


def test_timebase_offset():
    with expected_protocol(
        MSO5000,
        [(":TIM:MAIN:OFFS 0.002", None), (":TIM:MAIN:OFFS?", "2E-3")],
    ) as instrument:
        instrument.timebase_offset = 2e-3
        assert instrument.timebase_offset == pytest.approx(2e-3)


def test_timebase_scale():
    with expected_protocol(
        MSO5000,
        [(":TIM:MAIN:SCAL 0.001", None), (":TIM:MAIN:SCAL?", "1E-3")],
    ) as instrument:
        instrument.timebase_scale = 1e-3
        assert instrument.timebase_scale == pytest.approx(1e-3)


@pytest.mark.parametrize("value", ["MAIN", "XY", "ROLL"])
def test_timebase_mode(value):
    with expected_protocol(
        MSO5000,
        [(f":TIM:MODE {value}", None), (":TIM:MODE?", value)],
    ) as instrument:
        instrument.timebase_mode = value
        assert instrument.timebase_mode == value


def test_timebase_mode_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.timebase_mode = "INVALID"


@pytest.mark.parametrize("value", ["CENT", "LB", "RB", "TRIG", "USER"])
def test_horizontal_reference_mode(value):
    with expected_protocol(
        MSO5000,
        [(f":TIM:HREF:MODE {value}", None), (":TIM:HREF:MODE?", value)],
    ) as instrument:
        instrument.horizontal_reference_mode = value
        assert instrument.horizontal_reference_mode == value


def test_horizontal_reference_mode_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.horizontal_reference_mode = "LEFT"


@pytest.mark.parametrize("value", [-500, 0, 500])
def test_horizontal_reference_position(value):
    with expected_protocol(
        MSO5000,
        [(f":TIM:HREF:POS {value}", None), (":TIM:HREF:POS?", str(value))],
    ) as instrument:
        instrument.horizontal_reference_position = value
        assert instrument.horizontal_reference_position == value


def test_horizontal_reference_position_rejects_out_of_range_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.horizontal_reference_position = 501


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_timebase_vernier_enabled(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":TIM:VERN {raw}", None), (":TIM:VERN?", raw)],
    ) as instrument:
        instrument.timebase_vernier_enabled = value
        assert instrument.timebase_vernier_enabled is value


def test_waveform_source():
    with expected_protocol(
        MSO5000,
        [(":WAV:SOUR CHAN2", None), (":WAV:SOUR?", "CHAN2")],
    ) as instrument:
        instrument.waveform_source = "CHAN2"
        assert instrument.waveform_source == "CHAN2"


def test_waveform_source_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.waveform_source = "FFT"


@pytest.mark.parametrize("value", ["NORM", "MAX", "RAW"])
def test_waveform_mode(value):
    with expected_protocol(
        MSO5000,
        [(f":WAV:MODE {value}", None), (":WAV:MODE?", value)],
    ) as instrument:
        instrument.waveform_mode = value
        assert instrument.waveform_mode == value


def test_waveform_mode_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.waveform_mode = "SCREEN"


@pytest.mark.parametrize("value", ["WORD", "BYTE", "ASC"])
def test_waveform_format(value):
    with expected_protocol(
        MSO5000,
        [(f":WAV:FORM {value}", None), (":WAV:FORM?", value)],
    ) as instrument:
        instrument.waveform_format = value
        assert instrument.waveform_format == value


def test_waveform_format_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.waveform_format = "FLOAT"


def test_waveform_points():
    with expected_protocol(
        MSO5000,
        [(":WAV:POIN 1000", None), (":WAV:POIN?", "1000")],
    ) as instrument:
        instrument.waveform_points = 1000
        assert instrument.waveform_points == 1000


@pytest.mark.parametrize(
    "name, command, raw, expected",
    [
        ("waveform_x_increment", ":WAV:XINC?", "1E-8", 1e-8),
        ("waveform_x_origin", ":WAV:XOR?", "-5E-6", -5e-6),
        ("waveform_x_reference", ":WAV:XREF?", "0", 0),
        ("waveform_y_increment", ":WAV:YINC?", "4E-3", 4e-3),
        ("waveform_y_origin", ":WAV:YOR?", "0", 0),
        ("waveform_y_reference", ":WAV:YREF?", "128", 128),
    ],
)
def test_waveform_scaling_measurements(name, command, raw, expected):
    with expected_protocol(MSO5000, [(command, raw)]) as instrument:
        assert getattr(instrument, name) == pytest.approx(expected)


@pytest.mark.parametrize("name, command", [("waveform_start", "STAR"), ("waveform_stop", "STOP")])
def test_waveform_boundaries(name, command):
    with expected_protocol(
        MSO5000,
        [(f":WAV:{command} 500", None), (f":WAV:{command}?", "500")],
    ) as instrument:
        setattr(instrument, name, 500)
        assert getattr(instrument, name) == 500


def test_get_waveform_preamble():
    response = "0,0,1000,1,1E-8,-5E-6,0,4E-3,0,128"
    with expected_protocol(MSO5000, [(":WAV:PRE?", response)]) as instrument:
        preamble = instrument.get_waveform_preamble()
        assert preamble["format"] == 0
        assert preamble["points"] == 1000
        assert preamble["x_increment"] == pytest.approx(1e-8)
        assert preamble["y_reference"] == 128


def test_waveform_data_byte():
    payload = bytes([128, 10, 126, 132])
    block = b"#14" + payload + b"\n"
    with expected_protocol(
        MSO5000,
        [(":WAV:FORM?", "BYTE"), (":WAV:DATA?", block)],
    ) as instrument:
        data = instrument.waveform_data()
        assert data.tolist() == [128, 10, 126, 132]


def test_waveform_data_word():
    payload = bytes([128, 0, 10, 0])
    block = b"#14" + payload + b"\n"
    with expected_protocol(
        MSO5000,
        [(":WAV:FORM?", "WORD"), (":WAV:DATA?", block)],
    ) as instrument:
        data = instrument.waveform_data()
        assert data.tolist() == [128, 10]


@pytest.mark.parametrize(
    "block, message",
    [
        (b"!1", "does not start with an IEEE block header"),
        (b"#1x", "contains an invalid IEEE block header"),
        (b"#14abc", "declares 4 data bytes, received 3"),
    ],
)
def test_waveform_data_byte_rejects_malformed_ieee_block(block, message):
    with (
        expected_protocol(
            MSO5000,
            [(":WAV:FORM?", "BYTE"), (":WAV:DATA?", block)],
        ) as instrument,
        pytest.raises(ValueError, match=message),
    ):
        instrument.waveform_data()


@pytest.mark.filterwarnings("ignore:Breaking on termination character")
def test_waveform_data_byte_rejects_data_beyond_declared_length():
    block = b"#14" + bytes([128, 130, 126, 132]) + b"x\n"
    with (
        expected_protocol(
            MSO5000,
            [(":WAV:FORM?", "BYTE"), (":WAV:DATA?", block)],
        ) as instrument,
        pytest.raises(ValueError, match="beyond its declared IEEE block length"),
    ):
        instrument.waveform_data()


def test_waveform_data_word_rejects_odd_payload_length():
    block = b"#13" + bytes([128, 0, 130]) + b"\n"
    with (
        expected_protocol(
            MSO5000,
            [(":WAV:FORM?", "WORD"), (":WAV:DATA?", block)],
        ) as instrument,
        pytest.raises(ValueError, match="odd number of bytes"),
    ):
        instrument.waveform_data()


def test_waveform_data_word_rejects_nonzero_upper_bytes():
    block = b"#14" + bytes([128, 1, 130, 0]) + b"\n"
    with (
        expected_protocol(
            MSO5000,
            [(":WAV:FORM?", "WORD"), (":WAV:DATA?", block)],
        ) as instrument,
        pytest.raises(ValueError, match="non-zero upper bytes"),
    ):
        instrument.waveform_data()


def test_waveform_data_ascii():
    with expected_protocol(
        MSO5000,
        [(":WAV:FORM?", "ASC"), (":WAV:DATA?", "0.1,0.2,-0.3")],
    ) as instrument:
        data = instrument.waveform_data()
        assert data == pytest.approx([0.1, 0.2, -0.3])


def test_waveform_data_ascii_with_ieee_block_header():
    payload = "0.1,0.2,-0.3,"
    response = f"#2{len(payload):02d}{payload}"
    with expected_protocol(
        MSO5000,
        [(":WAV:FORM?", "ASC"), (":WAV:DATA?", response)],
    ) as instrument:
        data = instrument.waveform_data()
        assert data == pytest.approx([0.1, 0.2, -0.3])


def test_waveform_data_ascii_rejects_malformed_ieee_block():
    with (
        expected_protocol(
            MSO5000,
            [(":WAV:FORM?", "ASC"), (":WAV:DATA?", "#2100.1,0.2")],
        ) as instrument,
        pytest.raises(ValueError, match="declares 10 data bytes, received 7"),
    ):
        instrument.waveform_data()


@pytest.mark.parametrize("value", ["EDGE", "PULS", "SLOP", "VID", "PATT", "DUR"])
def test_trigger_mode(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:MODE {value}", None), (":TRIG:MODE?", value)],
    ) as instrument:
        instrument.trigger_mode = value
        assert instrument.trigger_mode == value


def test_trigger_mode_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.trigger_mode = "INVALID"


@pytest.mark.parametrize("value", ["AC", "DC", "LFR", "HFR"])
def test_trigger_coupling(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:COUP {value}", None), (":TRIG:COUP?", value)],
    ) as instrument:
        instrument.trigger_coupling = value
        assert instrument.trigger_coupling == value


def test_trigger_status():
    with expected_protocol(MSO5000, [(":TRIG:STAT?", "TD")]) as instrument:
        assert instrument.trigger_status == "TD"


@pytest.mark.parametrize("value", ["AUTO", "NORM", "SING"])
def test_trigger_sweep(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:SWE {value}", None), (":TRIG:SWE?", value)],
    ) as instrument:
        instrument.trigger_sweep = value
        assert instrument.trigger_sweep == value


def test_trigger_holdoff():
    with expected_protocol(
        MSO5000,
        [(":TRIG:HOLD 2e-07", None), (":TRIG:HOLD?", "2E-7")],
    ) as instrument:
        instrument.trigger_holdoff = 2e-7
        assert instrument.trigger_holdoff == pytest.approx(2e-7)


@pytest.mark.parametrize("value", [7e-9, 10.1])
def test_trigger_holdoff_rejects_out_of_range_value(value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.trigger_holdoff = value


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_trigger_noise_rejection_enabled(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:NREJ {raw}", None), (":TRIG:NREJ?", raw)],
    ) as instrument:
        instrument.trigger_noise_rejection_enabled = value
        assert instrument.trigger_noise_rejection_enabled is value


@pytest.mark.parametrize("value", ["CHAN1", "CHAN4", "D0", "D15", "ACL"])
def test_edge_trigger_source(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:EDGE:SOUR {value}", None), (":TRIG:EDGE:SOUR?", value)],
    ) as instrument:
        instrument.edge_trigger_source = value
        assert instrument.edge_trigger_source == value


def test_edge_trigger_source_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.edge_trigger_source = "MATH1"


@pytest.mark.parametrize("value", ["POS", "NEG", "RFAL"])
def test_edge_trigger_slope(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:EDGE:SLOP {value}", None), (":TRIG:EDGE:SLOP?", value)],
    ) as instrument:
        instrument.edge_trigger_slope = value
        assert instrument.edge_trigger_slope == value


def test_edge_trigger_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:EDGE:LEV 0.16", None), (":TRIG:EDGE:LEV?", "1.6E-1")],
    ) as instrument:
        instrument.edge_trigger_level = 0.16
        assert instrument.edge_trigger_level == pytest.approx(0.16)


@pytest.mark.parametrize("value", ["CHAN1", "CHAN4", "D0", "D15"])
def test_pulse_trigger_source(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:PULS:SOUR {value}", None), (":TRIG:PULS:SOUR?", value)],
    ) as instrument:
        instrument.pulse_trigger_source = value
        assert instrument.pulse_trigger_source == value


def test_pulse_trigger_source_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.pulse_trigger_source = "ACL"


@pytest.mark.parametrize("value", ["GRE", "LESS", "GLES"])
def test_pulse_trigger_condition(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:PULS:WHEN {value}", None), (":TRIG:PULS:WHEN?", value)],
    ) as instrument:
        instrument.pulse_trigger_condition = value
        assert instrument.pulse_trigger_condition == value


def test_pulse_trigger_condition_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.pulse_trigger_condition = "EQUAL"


def test_pulse_trigger_upper_width():
    with expected_protocol(
        MSO5000,
        [(":TRIG:PULS:UWID 3e-06", None), (":TRIG:PULS:UWID?", "3E-6")],
    ) as instrument:
        instrument.pulse_trigger_upper_width = 3e-6
        assert instrument.pulse_trigger_upper_width == pytest.approx(3e-6)


def test_pulse_trigger_lower_width():
    with expected_protocol(
        MSO5000,
        [(":TRIG:PULS:LWID 1e-06", None), (":TRIG:PULS:LWID?", "1E-6")],
    ) as instrument:
        instrument.pulse_trigger_lower_width = 1e-6
        assert instrument.pulse_trigger_lower_width == pytest.approx(1e-6)


def test_pulse_trigger_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:PULS:LEV 0.16", None), (":TRIG:PULS:LEV?", "1.6E-1")],
    ) as instrument:
        instrument.pulse_trigger_level = 0.16
        assert instrument.pulse_trigger_level == pytest.approx(0.16)


@pytest.mark.parametrize("value", ["CHAN1", "CHAN2", "CHAN3", "CHAN4"])
def test_slope_trigger_source(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:SLOP:SOUR {value}", None), (":TRIG:SLOP:SOUR?", value)],
    ) as instrument:
        instrument.slope_trigger_source = value
        assert instrument.slope_trigger_source == value


def test_slope_trigger_source_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.slope_trigger_source = "D0"


@pytest.mark.parametrize("value", ["GRE", "LESS", "GLES"])
def test_slope_trigger_condition(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:SLOP:WHEN {value}", None), (":TRIG:SLOP:WHEN?", value)],
    ) as instrument:
        instrument.slope_trigger_condition = value
        assert instrument.slope_trigger_condition == value


def test_slope_trigger_upper_time():
    with expected_protocol(
        MSO5000,
        [(":TRIG:SLOP:TUPP 3e-06", None), (":TRIG:SLOP:TUPP?", "3E-6")],
    ) as instrument:
        instrument.slope_trigger_upper_time = 3e-6
        assert instrument.slope_trigger_upper_time == pytest.approx(3e-6)


def test_slope_trigger_lower_time():
    with expected_protocol(
        MSO5000,
        [(":TRIG:SLOP:TLOW 2e-08", None), (":TRIG:SLOP:TLOW?", "2E-8")],
    ) as instrument:
        instrument.slope_trigger_lower_time = 2e-8
        assert instrument.slope_trigger_lower_time == pytest.approx(2e-8)


@pytest.mark.parametrize("value", ["TA", "TB", "TAB"])
def test_slope_trigger_window(value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:SLOP:WIND {value}", None), (":TRIG:SLOP:WIND?", value)],
    ) as instrument:
        instrument.slope_trigger_window = value
        assert instrument.slope_trigger_window == value


def test_slope_trigger_upper_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:SLOP:ALEV 0.16", None), (":TRIG:SLOP:ALEV?", "1.6E-1")],
    ) as instrument:
        instrument.slope_trigger_upper_level = 0.16
        assert instrument.slope_trigger_upper_level == pytest.approx(0.16)


def test_slope_trigger_lower_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:SLOP:BLEV -0.16", None), (":TRIG:SLOP:BLEV?", "-1.6E-1")],
    ) as instrument:
        instrument.slope_trigger_lower_level = -0.16
        assert instrument.slope_trigger_lower_level == pytest.approx(-0.16)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("video_trigger_source", "SOUR", ["CHAN1", "CHAN4"]),
        ("video_trigger_polarity", "POL", ["POS", "NEG"]),
        ("video_trigger_mode", "MODE", ["ODDF", "EVEN", "LINE", "ALIN"]),
        (
            "video_trigger_standard",
            "STAN",
            ["PALS", "NTSC", "480P", "720P60", "1080I50"],
        ),
    ],
)
def test_video_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:VID:{command} {value}", None), (f":TRIG:VID:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


def test_video_trigger_line():
    with expected_protocol(
        MSO5000,
        [(":TRIG:VID:LINE 100", None), (":TRIG:VID:LINE?", "100")],
    ) as instrument:
        instrument.video_trigger_line = 100
        assert instrument.video_trigger_line == 100


def test_video_trigger_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:VID:LEV 0.16", None), (":TRIG:VID:LEV?", "1.6E-1")],
    ) as instrument:
        instrument.video_trigger_level = 0.16
        assert instrument.video_trigger_level == pytest.approx(0.16)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("timeout_trigger_source", "SOUR", ["CHAN1", "CHAN4", "D0", "D15"]),
        ("timeout_trigger_slope", "SLOP", ["POS", "NEG", "RFAL"]),
    ],
)
def test_timeout_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:TIM:{command} {value}", None), (f":TRIG:TIM:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


def test_timeout_trigger_time():
    with expected_protocol(
        MSO5000,
        [(":TRIG:TIM:TIME 0.002", None), (":TRIG:TIM:TIME?", "2E-3")],
    ) as instrument:
        instrument.timeout_trigger_time = 2e-3
        assert instrument.timeout_trigger_time == pytest.approx(2e-3)


@pytest.mark.parametrize("value", [15e-9, 10.1])
def test_timeout_trigger_time_rejects_out_of_range_value(value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.timeout_trigger_time = value


def test_timeout_trigger_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:TIM:LEV 0.16", None), (":TRIG:TIM:LEV?", "1.6E-1")],
    ) as instrument:
        instrument.timeout_trigger_level = 0.16
        assert instrument.timeout_trigger_level == pytest.approx(0.16)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("window_trigger_source", "SOUR", ["CHAN1", "CHAN4"]),
        ("window_trigger_slope", "SLOP", ["POS", "NEG", "RFAL"]),
        ("window_trigger_position", "POS", ["EXIT", "ENT", "TIME"]),
    ],
)
def test_window_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:WIND:{command} {value}", None), (f":TRIG:WIND:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


def test_window_trigger_time():
    with expected_protocol(
        MSO5000,
        [(":TRIG:WIND:TIME 0.002", None), (":TRIG:WIND:TIME?", "2E-3")],
    ) as instrument:
        instrument.window_trigger_time = 2e-3
        assert instrument.window_trigger_time == pytest.approx(2e-3)


@pytest.mark.parametrize("value", [7e-9, 10.1])
def test_window_trigger_time_rejects_out_of_range_value(value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.window_trigger_time = value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("window_trigger_upper_level", "ALEV", 0.16),
        ("window_trigger_lower_level", "BLEV", -0.16),
    ],
)
def test_window_trigger_levels(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:WIND:{command} {value:g}", None), (f":TRIG:WIND:{command}?", str(value))],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == pytest.approx(value)


def test_autoscale():
    with expected_protocol(MSO5000, [(":AUT", None)]) as instrument:
        instrument.autoscale()


def test_clear_waveforms():
    with expected_protocol(MSO5000, [(":CLE", None)]) as instrument:
        instrument.clear_waveforms()


def test_run():
    with expected_protocol(MSO5000, [(":RUN", None)]) as instrument:
        instrument.run()


def test_stop():
    with expected_protocol(MSO5000, [(":STOP", None)]) as instrument:
        instrument.stop()


def test_single():
    with expected_protocol(MSO5000, [(":SING", None)]) as instrument:
        instrument.single()


def test_force_trigger():
    with expected_protocol(MSO5000, [(":TFOR", None)]) as instrument:
        instrument.force_trigger()


def test_acquisition_averages():
    with expected_protocol(
        MSO5000,
        [
            (":ACQ:AVER 128", None),
            (":ACQ:AVER?", "128"),
        ],
    ) as instrument:
        instrument.acquisition_averages = 128
        assert instrument.acquisition_averages == 128


def test_acquisition_averages_rejects_non_power_of_two():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.acquisition_averages = 3


@pytest.mark.parametrize("value", ["AUTO", 200_000_000])
def test_acquisition_memory_depth_accepts_documented_values(value):
    with expected_protocol(MSO5000, [(f":ACQ:MDEP {value}", None)]) as instrument:
        instrument.acquisition_memory_depth = value


def test_acquisition_memory_depth():
    with expected_protocol(
        MSO5000,
        [
            (":ACQ:MDEP 1000000", None),
            (":ACQ:MDEP?", "1.0000E+06"),
        ],
    ) as instrument:
        instrument.acquisition_memory_depth = 1_000_000
        assert instrument.acquisition_memory_depth == 1_000_000


def test_acquisition_memory_depth_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.acquisition_memory_depth = 2_000


@pytest.mark.parametrize("value", ["NORM", "AVER", "PEAK", "HRES"])
def test_acquisition_type(value):
    with expected_protocol(
        MSO5000,
        [
            (f":ACQ:TYPE {value}", None),
            (":ACQ:TYPE?", value),
        ],
    ) as instrument:
        instrument.acquisition_type = value
        assert instrument.acquisition_type == value


def test_acquisition_type_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.acquisition_type = "INVALID"


def test_sample_rate():
    with expected_protocol(MSO5000, [(":ACQ:SRAT?", "2.500000E+9")]) as instrument:
        assert instrument.sample_rate == pytest.approx(2.5e9)


def test_logic_analyzer_sample_rate():
    with expected_protocol(MSO5000, [(":ACQ:LA:SRAT?", "1.250000E+9")]) as instrument:
        assert instrument.logic_analyzer_sample_rate == pytest.approx(1.25e9)


def test_logic_analyzer_memory_depth():
    with expected_protocol(MSO5000, [(":ACQ:LA:MDEP?", "1.250000E+4")]) as instrument:
        assert instrument.logic_analyzer_memory_depth == pytest.approx(1.25e4)


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_anti_aliasing_enabled(value, raw):
    with expected_protocol(
        MSO5000,
        [
            (f":ACQ:AAL {raw}", None),
            (":ACQ:AAL?", raw),
        ],
    ) as instrument:
        instrument.anti_aliasing_enabled = value
        assert instrument.anti_aliasing_enabled is value


def test_pattern_trigger_pattern():
    pattern = ["H", "R", "L", *(["X"] * 17)]
    raw = ",".join(pattern)
    with expected_protocol(
        MSO5000, [(f":TRIG:PATT:PATT {raw}", None), (":TRIG:PATT:PATT?", raw)]
    ) as instrument:
        instrument.pattern_trigger_pattern = pattern
        assert instrument.pattern_trigger_pattern == pattern


@pytest.mark.parametrize(
    "pattern",
    [["X"] * 19, ["R", "F", *(["X"] * 18)], ["Q", *(["X"] * 19)]],
)
def test_pattern_trigger_pattern_rejects_invalid_value(pattern):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.pattern_trigger_pattern = pattern


def test_pattern_trigger_source_and_level():
    with expected_protocol(
        MSO5000,
        [
            (":TRIG:PATT:SOUR D15", None),
            (":TRIG:PATT:SOUR?", "D15"),
            (":TRIG:PATT:LEV CHAN2,0.16", None),
            (":TRIG:PATT:LEV? CHAN2", "1.6E-1"),
        ],
    ) as instrument:
        instrument.pattern_trigger_source = "D15"
        assert instrument.pattern_trigger_source == "D15"
        instrument.set_pattern_trigger_level("CHAN2", 0.16)
        assert instrument.get_pattern_trigger_level("CHAN2") == pytest.approx(0.16)


def test_duration_trigger_pattern():
    pattern = ["L", "X", "H", "L", *(["X"] * 16)]
    raw = ",".join(pattern)
    with expected_protocol(
        MSO5000, [(f":TRIG:DUR:TYPE {raw}", None), (":TRIG:DUR:TYPE?", raw)]
    ) as instrument:
        instrument.duration_trigger_pattern = pattern
        assert instrument.duration_trigger_pattern == pattern


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("duration_trigger_source", "SOUR", ["CHAN1", "D15"]),
        ("duration_trigger_condition", "WHEN", ["GRE", "LESS", "GLES", "UNGL"]),
    ],
)
def test_duration_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:DUR:{command} {value}", None), (f":TRIG:DUR:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, command",
    [
        ("duration_trigger_upper_time", "TUPP"),
        ("duration_trigger_lower_time", "TLOW"),
    ],
)
def test_duration_trigger_times(name, command):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:DUR:{command} 3e-06", None), (f":TRIG:DUR:{command}?", "3E-6")],
    ) as instrument:
        setattr(instrument, name, 3e-6)
        assert getattr(instrument, name) == pytest.approx(3e-6)


def test_duration_trigger_level():
    with expected_protocol(
        MSO5000,
        [(":TRIG:DUR:LEV D0,-1.2", None), (":TRIG:DUR:LEV? D0", "-1.2")],
    ) as instrument:
        instrument.set_duration_trigger_level("D0", -1.2)
        assert instrument.get_duration_trigger_level("D0") == pytest.approx(-1.2)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("runt_trigger_source", "SOUR", ["CHAN1", "CHAN4"]),
        ("runt_trigger_polarity", "POL", ["POS", "NEG"]),
        ("runt_trigger_condition", "WHEN", ["NONE", "GRE", "LESS", "GLES"]),
    ],
)
def test_runt_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:RUNT:{command} {value}", None), (f":TRIG:RUNT:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("runt_trigger_upper_width", "WUPP", 2e-6),
        ("runt_trigger_lower_width", "WLOW", 1e-6),
        ("runt_trigger_upper_level", "ALEV", 0.16),
        ("runt_trigger_lower_level", "BLEV", -0.16),
    ],
)
def test_runt_trigger_numeric_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:RUNT:{command} {value:g}", None), (f":TRIG:RUNT:{command}?", str(value))],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == pytest.approx(value)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("delay_trigger_source_a", "SA", ["CHAN1", "D15"]),
        ("delay_trigger_slope_a", "SLOPA", ["POS", "NEG"]),
        ("delay_trigger_source_b", "SB", ["CHAN2", "D0"]),
        ("delay_trigger_slope_b", "SLOPB", ["POS", "NEG"]),
        ("delay_trigger_condition", "TYPE", ["GRE", "LESS", "GLES", "GOUT"]),
    ],
)
def test_delay_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:DEL:{command} {value}", None), (f":TRIG:DEL:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("delay_trigger_upper_time", "TUPP", 2e-6),
        ("delay_trigger_lower_time", "TLOW", 1e-6),
        ("delay_trigger_source_a_level", "ALEV", 0.16),
        ("delay_trigger_source_b_level", "BLEV", -0.16),
    ],
)
def test_delay_trigger_numeric_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:DEL:{command} {value:g}", None), (f":TRIG:DEL:{command}?", str(value))],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == pytest.approx(value)


@pytest.mark.parametrize(
    "name, value",
    [
        ("delay_trigger_upper_time", 8e-9),
        ("delay_trigger_upper_time", 10.1),
        ("delay_trigger_lower_time", 7e-9),
        ("delay_trigger_lower_time", 10),
    ],
)
def test_delay_trigger_times_reject_out_of_range_values(name, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        setattr(instrument, name, value)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("setup_hold_data_source", "DSRC", ["CHAN2", "D15"]),
        ("setup_hold_clock_source", "CSRC", ["CHAN1", "D0"]),
        ("setup_hold_clock_slope", "SLOP", ["POS", "NEG"]),
        ("setup_hold_data_pattern", "PATT", ["H", "L"]),
        ("setup_hold_type", "TYPE", ["SET", "HOLD", "SETH"]),
    ],
)
def test_setup_hold_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:SHOL:{command} {value}", None), (f":TRIG:SHOL:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("setup_hold_setup_time", "STIM", 2e-6),
        ("setup_hold_hold_time", "HTIM", 3e-6),
        ("setup_hold_data_level", "DLEV", 0.16),
        ("setup_hold_clock_level", "CLEV", -0.16),
    ],
)
def test_setup_hold_numeric_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:SHOL:{command} {value:g}", None), (f":TRIG:SHOL:{command}?", str(value))],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == pytest.approx(value)


@pytest.mark.parametrize("name", ["setup_hold_setup_time", "setup_hold_hold_time"])
@pytest.mark.parametrize("value", [7e-9, 1.1])
def test_setup_hold_times_reject_out_of_range_values(name, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        setattr(instrument, name, value)


@pytest.mark.parametrize(
    "name, command, values",
    [
        ("nth_edge_trigger_source", "SOUR", ["CHAN1", "D15"]),
        ("nth_edge_trigger_slope", "SLOP", ["POS", "NEG"]),
    ],
)
def test_nth_edge_trigger_discrete_controls(name, command, values):
    for value in values:
        with expected_protocol(
            MSO5000,
            [(f":TRIG:NEDG:{command} {value}", None), (f":TRIG:NEDG:{command}?", value)],
        ) as instrument:
            setattr(instrument, name, value)
            assert getattr(instrument, name) == value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("nth_edge_trigger_idle_time", "IDLE", 2e-6),
        ("nth_edge_trigger_edge_count", "EDGE", 20),
        ("nth_edge_trigger_level", "LEV", 0.16),
    ],
)
def test_nth_edge_trigger_numeric_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":TRIG:NEDG:{command} {value:g}", None), (f":TRIG:NEDG:{command}?", str(value))],
    ) as instrument:
        setattr(instrument, name, value)
        assert getattr(instrument, name) == pytest.approx(value)


@pytest.mark.parametrize(
    "name, value",
    [
        ("nth_edge_trigger_idle_time", 15e-9),
        ("nth_edge_trigger_idle_time", 10.1),
        ("nth_edge_trigger_edge_count", 0),
        ("nth_edge_trigger_edge_count", 65536),
    ],
)
def test_nth_edge_trigger_numeric_controls_reject_out_of_range_values(name, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        setattr(instrument, name, value)


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("source", "SOUR", "MATH2"),
        ("mode", "MODE", "PREC"),
        ("am_source", "AMS", "CHAN3"),
        ("setup_primary_source_a", "SET:PSA", "D15"),
        ("setup_primary_source_b", "SET:PSB", "CHAN2"),
        ("setup_digital_source_a", "SET:DSA", "MATH1"),
        ("setup_digital_source_b", "SET:DSB", "D0"),
        ("area", "AREA", "CURS"),
    ],
)
def test_measurement_discrete_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":MEAS:{command} {value}", None), (f":MEAS:{command}?", value)],
    ) as instrument:
        setattr(instrument.measurements, name, value)
        assert getattr(instrument.measurements, name) == value


@pytest.mark.parametrize("value, raw", [(True, "1"), (False, "0")])
def test_measurement_statistic_display(value, raw):
    with expected_protocol(
        MSO5000,
        [(f":MEAS:STAT:DISP {raw}", None), (":MEAS:STAT:DISP?", raw)],
    ) as instrument:
        instrument.measurements.statistic_display = value
        assert instrument.measurements.statistic_display is value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("setup_max", "SET:MAX", 90),
        ("setup_mid", "SET:MID", 50),
        ("setup_min", "SET:MIN", -20),
        ("cregion_cursor_a_x", "CREG:CAX", 250),
        ("cregion_cursor_b_x", "CREG:CBX", 750),
        ("category", "CAT", 2),
    ],
)
def test_measurement_numeric_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":MEAS:{command} {value}", None), (f":MEAS:{command}?", str(value))],
    ) as instrument:
        setattr(instrument.measurements, name, value)
        assert getattr(instrument.measurements, name) == value


@pytest.mark.parametrize(
    "name, value",
    [
        ("source", "REF1"),
        ("mode", "FAST"),
        ("am_source", "MATH1"),
        ("setup_max", 101),
        ("setup_min", -101),
        ("cregion_cursor_a_x", -1),
        ("cregion_cursor_b_x", 1001),
        ("category", 3),
    ],
)
def test_measurement_controls_reject_invalid_values(name, value):
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        setattr(instrument.measurements, name, value)


def test_measurement_threshold_source_and_actions():
    with expected_protocol(
        MSO5000,
        [
            (":MEAS:THR:SOUR MATH4", None),
            (":MEAS:THR:DEF", None),
            (":MEAS:CLE ITEM7", None),
            (":MEAS:STAT:RES", None),
        ],
    ) as instrument:
        instrument.measurements.threshold_source = "MATH4"
        instrument.measurements.reset_thresholds()
        instrument.measurements.clear("ITEM7")
        instrument.measurements.reset_statistics()


def test_measurement_item_set_and_query():
    with expected_protocol(
        MSO5000,
        [
            (":MEAS:ITEM RRDEL,CHAN1,D0", None),
            (":MEAS:ITEM? RRDEL,CHAN1,D0", "1.25E-6"),
        ],
    ) as instrument:
        instrument.measurements.enable_item("RRDEL", "CHAN1", "D0")
        assert instrument.measurements.item("RRDEL", "CHAN1", "D0") == pytest.approx(1.25e-6)


def test_measurement_statistic_item_set_and_query():
    with expected_protocol(
        MSO5000,
        [
            (":MEAS:STAT:ITEM VPP,CHAN2", None),
            (":MEAS:STAT:ITEM? AVER,VPP,CHAN2", "2.5E+0"),
        ],
    ) as instrument:
        instrument.measurements.enable_statistic_item("VPP", "CHAN2")
        assert instrument.measurements.statistic_item("AVER", "VPP", "CHAN2") == pytest.approx(2.5)


def test_measurement_item_defaults_to_selected_source():
    with expected_protocol(MSO5000, [(":MEAS:ITEM? FREQ", "1.0E+6")]) as instrument:
        assert instrument.measurements.item("FREQ") == pytest.approx(1e6)


def test_measurement_unavailable_returns_nan():
    with expected_protocol(MSO5000, [(":MEAS:ITEM? VMAX,CHAN1", "****")]) as instrument:
        assert math.isnan(instrument.measurements.item("VMAX", "CHAN1"))


def test_measurement_methods_reject_invalid_arguments():
    with expected_protocol(MSO5000, []) as instrument:
        with pytest.raises(ValueError):
            instrument.measurements.clear("ITEM11")
        with pytest.raises(ValueError):
            instrument.measurements.item("UNKNOWN")
        with pytest.raises(ValueError):
            instrument.measurements.item("VPP", "REF1")
        with pytest.raises(ValueError):
            instrument.measurements.item("VPP", None, "CHAN2")
        with pytest.raises(ValueError):
            instrument.measurements.statistic_item("MEAN", "VPP")


def test_measure_compatibility_method():
    with expected_protocol(MSO5000, [(":MEAS:ITEM? VPP,CHAN3", "3.3")]) as instrument:
        assert instrument.measure("VPP", 3) == pytest.approx(3.3)


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("measure_indicator", "MEAS:IND", True, "1", "1"),
        ("mode", "MODE", "TRAC", "TRAC", "TRAC"),
        ("manual_type", "MAN:TYPE", "TIME", "TIME", "TIME"),
        ("manual_source", "MAN:SOUR", "MATH3", "MATH3", "MATH3"),
        ("manual_time_unit", "MAN:TUN", "DEGR", "DEGR", "DEGR"),
        ("manual_vertical_unit", "MAN:VUN", "PERC", "PERC", "PERC"),
        ("track_source1", "TRAC:SOUR1", "CHAN2", "CHAN2", "CHAN2"),
        ("track_source2", "TRAC:SOUR2", "MATH4", "MATH4", "MATH4"),
    ],
)
def test_cursor_discrete_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":CURS:{command} {wire}", None), (f":CURS:{command}?", reply)],
    ) as instrument:
        setattr(instrument.cursor, name, value)
        assert getattr(instrument.cursor, name) == value


@pytest.mark.parametrize(
    "name, command, value",
    [
        ("manual_cursor_a_x", "MAN:CAX", 250),
        ("manual_cursor_b_x", "MAN:CBX", 750),
        ("manual_cursor_a_y", "MAN:CAY", 120),
        ("manual_cursor_b_y", "MAN:CBY", 360),
        ("track_cursor_a_x", "TRAC:CAX", 300),
        ("track_cursor_b_x", "TRAC:CBX", 700),
        ("xy_ax", "XY:AX", 100),
        ("xy_bx", "XY:BX", 300),
        ("xy_ay", "XY:AY", 120),
        ("xy_by", "XY:BY", 360),
    ],
)
def test_cursor_position_controls(name, command, value):
    with expected_protocol(
        MSO5000,
        [(f":CURS:{command} {value}", None), (f":CURS:{command}?", str(value))],
    ) as instrument:
        setattr(instrument.cursor, name, value)
        assert getattr(instrument.cursor, name) == value


@pytest.mark.parametrize(
    "name, command, reply, expected",
    [
        ("manual_cursor_a_x_value", "MAN:AXV", "1.25E-6", 1.25e-6),
        ("manual_cursor_a_y_value", "MAN:AYV", "2.5E+0", 2.5),
        ("manual_cursor_b_x_value", "MAN:BXV", "2.25E-6", 2.25e-6),
        ("manual_cursor_b_y_value", "MAN:BYV", "3.5E+0", 3.5),
        ("manual_x_delta", "MAN:XDEL", "1E-6", 1e-6),
        ("manual_inverse_x_delta", "MAN:IXD", "1E+6", 1e6),
        ("manual_y_delta", "MAN:YDEL", "1E+0", 1.0),
        ("track_cursor_a_y", "TRAC:CAY", "120", 120),
        ("track_cursor_b_y", "TRAC:CBY", "360", 360),
        ("track_cursor_a_x_value", "TRAC:AXV", "1E-6", 1e-6),
        ("track_cursor_a_y_value", "TRAC:AYV", "1E+0", 1.0),
        ("track_cursor_b_x_value", "TRAC:BXV", "2E-6", 2e-6),
        ("track_cursor_b_y_value", "TRAC:BYV", "2E+0", 2.0),
        ("track_x_delta", "TRAC:XDEL", "1E-6", 1e-6),
        ("track_y_delta", "TRAC:YDEL", "1E+0", 1.0),
        ("track_inverse_x_delta", "TRAC:IXD", "1E+6", 1e6),
        ("xy_cursor_a_x_value", "XY:AXV", "1E+0", 1.0),
        ("xy_cursor_a_y_value", "XY:AYV", "2E+0", 2.0),
        ("xy_cursor_b_x_value", "XY:BXV", "3E+0", 3.0),
        ("xy_cursor_b_y_value", "XY:BYV", "4E+0", 4.0),
    ],
)
def test_cursor_measurements(name, command, reply, expected):
    with expected_protocol(MSO5000, [(f":CURS:{command}?", reply)]) as instrument:
        assert getattr(instrument.cursor, name) == pytest.approx(expected)


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("type", "TYPE", "DOTS", "DOTS", "DOTS"),
        ("grading_time", "GRAD:TIME", "0.2", "0.2", "0.2"),
        ("waveform_brightness", "WBR", 75, "75", "75"),
        ("grid", "GRID", "HALF", "HALF", "HALF"),
        ("grid_brightness", "GBR", 45, "45", "45"),
        ("rulers", "RUL", True, "1", "1"),
        ("color", "COL", False, "0", "0"),
    ],
)
def test_display_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":DISP:{command} {wire}", None), (f":DISP:{command}?", reply)],
    ) as instrument:
        setattr(instrument.display, name, value)
        assert getattr(instrument.display, name) == value


def test_display_clear():
    with expected_protocol(MSO5000, [(":DISP:CLE", None)]) as instrument:
        instrument.display.clear()


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("display", "DISP", True, "1", "1"),
        ("type", "TYPE", "VERT", "VERT", "VERT"),
        ("source", "SOUR", "CHAN3", "CHAN3", "CHAN3"),
        ("size", "SIZE", 3, "3", "3"),
        ("static", "STAT", True, "1", "1"),
        ("bottom_limit", "BLIM", -1.25, "-1.25", "-1.25E+0"),
        ("left_limit", "LLIM", -2e-6, "-2e-06", "-2E-6"),
        ("right_limit", "RLIM", 2e-6, "2e-06", "2E-6"),
        ("top_limit", "TLIM", 1.25, "1.25", "1.25E+0"),
    ],
)
def test_histogram_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":HIST:{command} {wire}", None), (f":HIST:{command}?", reply)],
    ) as instrument:
        setattr(instrument.histogram, name, value)
        assert getattr(instrument.histogram, name) == pytest.approx(value)


def test_histogram_reset():
    with expected_protocol(MSO5000, [(":HIST:RES", None)]) as instrument:
        instrument.histogram.reset()


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("enabled", "ENAB", True, "1", "1"),
        ("source", "SOUR", "CHAN2", "CHAN2", "CHAN2"),
        ("operate", "OPER", "STOP", "STOP", "STOP"),
        ("measurement_display", "MDIS", False, "0", "0"),
        ("x", "X", 0.2, "0.2", "2E-1"),
        ("y", "Y", 0.4, "0.4", "4E-1"),
    ],
)
def test_mask_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":MASK:{command} {wire}", None), (f":MASK:{command}?", reply)],
    ) as instrument:
        setattr(instrument.mask, name, value)
        result = getattr(instrument.mask, name)
        if isinstance(value, float):
            assert result == pytest.approx(value)
        else:
            assert result == value


@pytest.mark.parametrize(
    "name, command, reply",
    [("passed", "PASS", "12"), ("failed", "FAIL", "3"), ("total", "TOT", "15")],
)
def test_mask_counters(name, command, reply):
    with expected_protocol(MSO5000, [(f":MASK:{command}?", reply)]) as instrument:
        assert getattr(instrument.mask, name) == int(reply)


def test_mask_actions():
    with expected_protocol(MSO5000, [(":MASK:CRE", None), (":MASK:RES", None)]) as instrument:
        instrument.mask.create()
        instrument.mask.reset()


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("enabled", "ENAB", True, "1", "1"),
        ("start", "STAR", False, "0", "0"),
        ("play", "PLAY", True, "1", "1"),
        ("current", "CURR", 7, "7", "7"),
        ("frames", "FRAM", 100, "100", "100"),
    ],
)
def test_recording_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":REC:{command} {wire}", None), (f":REC:{command}?", reply)],
    ) as instrument:
        setattr(instrument.recording, name, value)
        assert getattr(instrument.recording, name) == value


def test_reference_global_controls():
    with expected_protocol(
        MSO5000,
        [
            (":REF:DISP 1", None),
            (":REF:DISP?", "1"),
            (":REF:LAB:ENAB 0", None),
            (":REF:LAB:ENAB?", "0"),
        ],
    ) as instrument:
        instrument.references.display = True
        assert instrument.references.display is True
        instrument.references.label_enabled = False
        assert instrument.references.label_enabled is False


def test_reference_slot_controls():
    with expected_protocol(
        MSO5000,
        [
            (":REF:SOUR 3,MATH2", None),
            (":REF:SOUR? 3", "MATH2"),
            (":REF:VSC 3,2.5", None),
            (":REF:VSC? 3", "2.5E+0"),
            (":REF:VOFF 3,-0.25", None),
            (":REF:VOFF? 3", "-2.5E-1"),
            (":REF:COL 3,ORAN", None),
            (":REF:COL? 3", "ORAN"),
            (":REF:LAB:CONT 3,baseline", None),
            (":REF:LAB:CONT? 3", "baseline"),
            (":REF:RES 3", None),
            (":REF:CURR 3", None),
        ],
    ) as instrument:
        instrument.references.set_source(3, "MATH2")
        assert instrument.references.source(3) == "MATH2"
        instrument.references.set_vertical_scale(3, 2.5)
        assert instrument.references.vertical_scale(3) == pytest.approx(2.5)
        instrument.references.set_vertical_offset(3, -0.25)
        assert instrument.references.vertical_offset(3) == pytest.approx(-0.25)
        instrument.references.set_color(3, "ORAN")
        assert instrument.references.color(3) == "ORAN"
        instrument.references.set_label_content(3, "baseline")
        assert instrument.references.label_content(3) == "baseline"
        instrument.references.reset(3)
        instrument.references.select_current(3)


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("display", "DISP", True, "1", "1"),
        ("operator", "OPER", "FFT", "FFT", "FFT"),
        ("source1", "SOUR1", "REF2", "REF2", "REF2"),
        ("source2", "SOUR2", "CHAN4", "CHAN4", "CHAN4"),
        ("left_source_1", "LSOU1", "D7", "D7", "D7"),
        ("left_source_2", "LSOU2", "CHAN2", "CHAN2", "CHAN2"),
        ("invert", "INV", False, "0", "0"),
        ("fft_source", "FFT:SOUR", "CHAN3", "CHAN3", "CHAN3"),
        ("fft_window", "FFT:WIND", "FLAT", "FLAT", "FLAT"),
        ("fft_unit", "FFT:UNIT", "DB", "DB", "DB"),
        ("fft_search_enabled", "FFT:SEAR:ENAB", True, "1", "1"),
        ("fft_search_order", "FFT:SEAR:ORD", "FREQ", "FREQ", "FREQ"),
        ("filter_type", "FILT:TYPE", "BPAS", "BPAS", "BPAS"),
    ],
)
def test_math_discrete_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":MATH2:{command} {wire}", None), (f":MATH2:{command}?", reply)],
    ) as instrument:
        setattr(instrument.math_2, name, value)
        assert getattr(instrument.math_2, name) == value


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("scale", "SCAL", 2.5, "2.5", "2.5E+0"),
        ("offset", "OFFS", -0.25, "-0.25", "-2.5E-1"),
        ("fft_scale", "FFT:SCAL", 5.0, "5", "5E+0"),
        ("fft_offset", "FFT:OFFS", -10.0, "-10", "-1E+1"),
        ("fft_horizontal_scale", "FFT:HSC", 1e6, "1e+06", "1E+6"),
        ("fft_horizontal_center", "FFT:HCEN", 5e5, "500000", "5E+5"),
        ("fft_frequency_start", "FFT:FREQ:STAR", 1e3, "1000", "1E+3"),
        ("fft_frequency_end", "FFT:FREQ:END", 1e6, "1e+06", "1E+6"),
        ("fft_search_num", "FFT:SEAR:NUM", 7, "7", "7"),
        ("fft_search_threshold", "FFT:SEAR:THR", -20.0, "-20", "-2E+1"),
        ("fft_search_excursion", "FFT:SEAR:EXC", 3.0, "3", "3E+0"),
        ("filter_w1", "FILT:W1", 1e3, "1000", "1E+3"),
        ("filter_w2", "FILT:W2", 2e3, "2000", "2E+3"),
        ("sensitivity", "SENS", 0.3, "0.3", "3E-1"),
        ("distance", "DIST", 25, "25", "25"),
        ("threshold1", "THR1", 0.1, "0.1", "1E-1"),
        ("threshold2", "THR2", 0.2, "0.2", "2E-1"),
        ("threshold3", "THR3", 0.3, "0.3", "3E-1"),
        ("threshold4", "THR4", 0.4, "0.4", "4E-1"),
    ],
)
def test_math_numeric_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":MATH2:{command} {wire}", None), (f":MATH2:{command}?", reply)],
    ) as instrument:
        setattr(instrument.math_2, name, value)
        assert getattr(instrument.math_2, name) == pytest.approx(value)


def test_math_reset_and_channel_ids():
    with expected_protocol(
        MSO5000,
        [
            (":MATH1:RES", None),
            (":MATH2:RES", None),
            (":MATH3:RES", None),
            (":MATH4:RES", None),
        ],
    ) as instrument:
        instrument.math_1.reset()
        instrument.math_2.reset()
        instrument.math_3.reset()
        instrument.math_4.reset()


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("state", "STAT", True, "1", "1"),
        ("mode", "MODE", "RUNT", "RUNT", "RUNT"),
        ("event", "EVEN", 2, "2", "2"),
        ("edge_slope", "EDGE:SLOP", "EITH", "EITH", "EITH"),
        ("edge_source", "EDGE:SOUR", "CHAN2", "CHAN2", "CHAN2"),
        ("pulse_polarity", "PULS:POL", "NEG", "NEG", "NEG"),
        ("pulse_qualifier", "PULS:QUAL", "GLES", "GLES", "GLES"),
        ("pulse_source", "PULS:SOUR", "CHAN3", "CHAN3", "CHAN3"),
        ("runt_polarity", "RUNT:POL", "POS", "POS", "POS"),
        ("runt_qualifier", "RUNT:QUAL", "LESS", "LESS", "LESS"),
        ("runt_source", "RUNT:SOUR", "CHAN4", "CHAN4", "CHAN4"),
        ("slope_polarity", "SLOP:POL", "NEG", "NEG", "NEG"),
        ("slope_qualifier", "SLOP:QUAL", "GRE", "GRE", "GRE"),
        ("slope_source", "SLOP:SOUR", "CHAN1", "CHAN1", "CHAN1"),
    ],
)
def test_search_discrete_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":SEAR:{command} {wire}", None), (f":SEAR:{command}?", reply)],
    ) as instrument:
        setattr(instrument.search, name, value)
        assert getattr(instrument.search, name) == value


@pytest.mark.parametrize(
    "name, command, value, wire, reply",
    [
        ("edge_threshold", "EDGE:THR", 0.1, "0.1", "1E-1"),
        ("pulse_upper_width", "PULS:UWID", 2e-6, "2e-06", "2E-6"),
        ("pulse_lower_width", "PULS:LWID", 1e-6, "1e-06", "1E-6"),
        ("pulse_threshold", "PULS:THR", 0.2, "0.2", "2E-1"),
        ("runt_width_upper", "RUNT:WUPP", 3e-6, "3e-06", "3E-6"),
        ("runt_width_lower", "RUNT:WLOW", 2e-6, "2e-06", "2E-6"),
        ("runt_threshold1", "RUNT:THR1", 0.1, "0.1", "1E-1"),
        ("runt_threshold2", "RUNT:THR2", 0.2, "0.2", "2E-1"),
        ("slope_time_upper", "SLOP:TUPP", 4e-6, "4e-06", "4E-6"),
        ("slope_time_lower", "SLOP:TLOW", 3e-6, "3e-06", "3E-6"),
        ("slope_threshold1", "SLOP:THR1", 0.1, "0.1", "1E-1"),
        ("slope_threshold2", "SLOP:THR2", 0.2, "0.2", "2E-1"),
    ],
)
def test_search_numeric_controls(name, command, value, wire, reply):
    with expected_protocol(
        MSO5000,
        [(f":SEAR:{command} {wire}", None), (f":SEAR:{command}?", reply)],
    ) as instrument:
        setattr(instrument.search, name, value)
        assert getattr(instrument.search, name) == pytest.approx(value)


def test_search_results():
    with expected_protocol(
        MSO5000,
        [(":SEAR:COUN?", "12"), (":SEAR:VAL? 7", "1.25E-6")],
    ) as instrument:
        assert instrument.search.count == 12
        assert instrument.search.value(7) == pytest.approx(1.25e-6)


def test_advanced_scope_controls_reject_invalid_values():
    with expected_protocol(MSO5000, []) as instrument:
        invalid = [
            (instrument.cursor, "mode", "AUTO"),
            (instrument.cursor, "manual_cursor_a_x", 1000),
            (instrument.display, "waveform_brightness", 0),
            (instrument.histogram, "size", 5),
            (instrument.mask, "x", 0),
            (instrument.recording, "frames", 0),
            (instrument.math_1, "fft_search_num", 16),
            (instrument.math_1, "sensitivity", 0.01),
            (instrument.search, "event", -1),
            (instrument.search, "pulse_upper_width", 11),
        ]
        for child, name, value in invalid:
            with pytest.raises(ValueError):
                setattr(child, name, value)
        with pytest.raises(ValueError):
            instrument.references.source(11)
        with pytest.raises(ValueError):
            instrument.search.value(1001)


@pytest.mark.parametrize(
    "name, command, value, reply",
    [
        ("state", "STAT", True, "1"),
        ("active_channel", "ACT", "D7", "D7"),
        ("size", "SIZE", "MED", "MED"),
    ],
)
def test_logic_analyzer_controls(name, command, value, reply):
    wire = int(value) if isinstance(value, bool) else value
    with expected_protocol(
        MSO5000,
        [(f":LA:{command} {wire}", None), (f":LA:{command}?", reply)],
    ) as instrument:
        setattr(instrument.logic_analyzer, name, value)
        assert getattr(instrument.logic_analyzer, name) == value


def test_logic_analyzer_setting_measurement_and_actions():
    with expected_protocol(
        MSO5000,
        [
            (":LA:AUTOS 1", None),
            (":LA:TCAL?", "2.5E-9"),
            (":LA:DISP GRO2,1", None),
            (":LA:DISP? GRO2", "1"),
            (":LA:DEL GRO3", None),
            (":LA:GRO:APP GRO1,D0,D7,D15", None),
        ],
    ) as instrument:
        instrument.logic_analyzer.auto_sort = True
        assert instrument.logic_analyzer.time_calibration == pytest.approx(2.5e-9)
        instrument.logic_analyzer.set_display("GRO2", True)
        assert instrument.logic_analyzer.display("GRO2") is True
        instrument.logic_analyzer.delete_group("GRO3")
        instrument.logic_analyzer.append_group("GRO1", "D0", "D7", "D15")


def test_digital_channel_controls_and_channel_ids():
    with expected_protocol(
        MSO5000,
        [
            (":LA:DIG:DISP D7,1", None),
            (":LA:DIG:DISP? D7", "1"),
            (":LA:DIG:POS D7,12", None),
            (":LA:DIG:POS? D7", "12"),
            (":LA:DIG:LAB D7,clock", None),
            (":LA:DIG:LAB? D7", "clock"),
        ],
    ) as instrument:
        instrument.d_7.display = True
        assert instrument.d_7.display is True
        instrument.d_7.position = 12
        assert instrument.d_7.position == 12
        instrument.d_7.label = "clock"
        assert instrument.d_7.label == "clock"
        assert instrument.digital_channels[7] is instrument.d_7


def test_logic_pod_controls_and_channel_ids():
    with expected_protocol(
        MSO5000,
        [
            (":LA:POD2:DISP 1", None),
            (":LA:POD2:DISP?", "1"),
            (":LA:POD2:THR 1.4", None),
            (":LA:POD2:THR?", "1.4E+0"),
        ],
    ) as instrument:
        instrument.pod_2.display = True
        assert instrument.pod_2.display is True
        instrument.pod_2.threshold = 1.4
        assert instrument.pod_2.threshold == pytest.approx(1.4)


@pytest.mark.parametrize(
    "catalog_id, name, command, value, reply",
    [
        ("BUSN.MODE", "mode", "MODE", "PAR", "PAR"),
        ("BUSN.DISPLAY", "display", "DISP", True, "1"),
        ("BUSN.FORMAT", "format", "FORM", "HEX", "HEX"),
        ("BUSN.EVENT", "event", "EVEN", True, "1"),
        ("BUSN.EVENT.FORMAT", "event_format", "EVEN:FORM", "ASC", "ASC"),
        ("BUSN.EVENT.VIEW", "event_view", "EVEN:VIEW", "DET", "DET"),
        ("BUSN.LABEL", "label", "LAB", False, "0"),
        ("BUSN.POSITION", "position", "POS", 25, "25"),
        ("BUSN.PARALLEL.BUS", "parallel_bus", "PAR:BUS", "D7D0", "D7D0"),
        ("BUSN.PARALLEL.CLK", "parallel_clk", "PAR:CLK", "CHAN2", "CHAN2"),
        ("BUSN.PARALLEL.SLOPE", "parallel_slope", "PAR:SLOP", "BOTH", "BOTH"),
        ("BUSN.PARALLEL.WIDTH", "parallel_width", "PAR:WIDT", 8, "8"),
        ("BUSN.PARALLEL.BITX", "parallel_bitx", "PAR:BITX", 3, "3"),
        ("BUSN.PARALLEL.SOURCE", "parallel_source", "PAR:SOUR", "D7", "D7"),
        ("BUSN.PARALLEL.POLARITY", "parallel_polarity", "PAR:POL", "NEG", "NEG"),
        ("BUSN.PARALLEL.NREJECT", "parallel_noise_reject", "PAR:NREJ", True, "1"),
        ("BUSN.PARALLEL.NRTIME", "parallel_noise_reject_time", "PAR:NRT", 1e-06, "1E-6"),
        ("BUSN.RS232.TX", "rs232_tx", "RS232:TX", "CHAN2", "CHAN2"),
        ("BUSN.RS232.RX", "rs232_rx", "RS232:RX", "OFF", "OFF"),
        ("BUSN.RS232.POLARITY", "rs232_polarity", "RS232:POL", "NEG", "NEG"),
        ("BUSN.RS232.ENDIAN", "rs232_endian", "RS232:END", "LSB", "LSB"),
        ("BUSN.RS232.BAUD", "rs232_baud", "RS232:BAUD", 9600, "9600"),
        ("BUSN.RS232.DBITS", "rs232_data_bits", "RS232:DBIT", 8, "8"),
        ("BUSN.RS232.SBITS", "rs232_stop_bits", "RS232:SBIT", 1.5, "1.5"),
        ("BUSN.RS232.PARITY", "rs232_parity", "RS232:PAR", "EVEN", "EVEN"),
        ("BUSN.RS232.PACKET", "rs232_packet", "RS232:PACK", True, "1"),
        ("BUSN.RS232.PEND", "rs232_pend", "RS232:PEND", "CR", "CR"),
        ("BUSN.IIC.SCLK.SOURCE", "iic_clock_source", "IIC:SCLK:SOUR", "CHAN1", "CHAN1"),
        ("BUSN.IIC.SDA.SOURCE", "iic_data_source", "IIC:SDA:SOUR", "CHAN2", "CHAN2"),
        ("BUSN.IIC.ADDRESS", "iic_address", "IIC:ADDR", "RW", "RW"),
        ("BUSN.SPI.SCLK.SOURCE", "spi_clock_source", "SPI:SCLK:SOUR", "CHAN1", "CHAN1"),
        ("BUSN.SPI.SCLK.SLOPE", "spi_clock_slope", "SPI:SCLK:SLOP", "NEG", "NEG"),
        ("BUSN.SPI.MISO.SOURCE", "spi_miso_source", "SPI:MISO:SOUR", "CHAN2", "CHAN2"),
        ("BUSN.SPI.MISO.POLARITY", "spi_miso_polarity", "SPI:MISO:POL", "LOW", "LOW"),
        ("BUSN.SPI.MOSI.SOURCE", "spi_mosi_source", "SPI:MOSI:SOUR", "OFF", "OFF"),
        ("BUSN.SPI.MOSI.POLARITY", "spi_mosi_polarity", "SPI:MOSI:POL", "HIGH", "HIGH"),
        ("BUSN.SPI.DBITS", "spi_data_bits", "SPI:DBIT", 16, "16"),
        ("BUSN.SPI.ENDIAN", "spi_endian", "SPI:END", "MSB", "MSB"),
        ("BUSN.SPI.MODE", "spi_mode", "SPI:MODE", "TIM", "TIM"),
        ("BUSN.SPI.TIMEOUT.TIME", "spi_timeout_time", "SPI:TIM:TIME", 1e-06, "1E-6"),
        ("BUSN.SPI.SS.SOURCE", "spi_ss_source", "SPI:SS:SOUR", "CHAN3", "CHAN3"),
        ("BUSN.SPI.SS.POLARITY", "spi_ss_polarity", "SPI:SS:POL", "LOW", "LOW"),
        ("BUSN.CAN.SOURCE", "can_source", "CAN:SOUR", "CHAN1", "CHAN1"),
        ("BUSN.CAN.STYPE", "can_source_type", "CAN:STYP", "DIFF", "DIFF"),
        ("BUSN.CAN.BAUD", "can_baud", "CAN:BAUD", 1000000, "1000000"),
        ("BUSN.CAN.SPOINT", "can_sample_point", "CAN:SPO", 50, "50"),
        ("BUSN.FLEXRAY.BAUD", "flexray_baud", "FLEX:BAUD", 10000000, "10000000"),
        ("BUSN.FLEXRAY.SOURCE", "flexray_source", "FLEX:SOUR", "CHAN1", "CHAN1"),
        ("BUSN.FLEXRAY.SPOINT", "flexray_sample_point", "FLEX:SPO", 50, "50"),
        ("BUSN.FLEXRAY.STYPE", "flexray_source_type", "FLEX:STYP", "BP", "BP"),
        ("BUSN.LIN.BAUD", "lin_baud", "LIN:BAUD", 19200, "19200"),
        ("BUSN.LIN.POLARITY", "lin_polarity", "LIN:POL", False, "0"),
        ("BUSN.LIN.SOURCE", "lin_source", "LIN:SOUR", "CHAN2", "CHAN2"),
        ("BUSN.LIN.STANDARD", "lin_standard", "LIN:STAN", "MIX", "MIX"),
        ("BUSN.IIS.SOURCE.CLOCK", "iis_source_clock", "IIS:SOUR:CLOC", "CHAN1", "CHAN1"),
        ("BUSN.IIS.SOURCE.DATA", "iis_source_data", "IIS:SOUR:DATA", "CHAN3", "CHAN3"),
        ("BUSN.IIS.SOURCE.WSELECT", "iis_source_word_select", "IIS:SOUR:WSEL", "CHAN2", "CHAN2"),
        ("BUSN.IIS.ALIGNMENT", "iis_alignment", "IIS:ALIG", "IIS", "IIS"),
        ("BUSN.IIS.CLOCK.SLOPE", "iis_clock_slope", "IIS:CLOC:SLOP", "POS", "POS"),
        ("BUSN.IIS.RWIDTH", "iis_right_width", "IIS:RWID", 24, "24"),
        ("BUSN.M1553.SOURCE", "m1553_source", "M1553:SOUR", "CHAN4", "CHAN4"),
    ],
    ids=lambda value: value if isinstance(value, str) and "." in value else None,
)
def test_bus_controls(catalog_id, name, command, value, reply):
    del catalog_id
    wire = int(value) if isinstance(value, bool) else value
    separator = " "
    with expected_protocol(
        MSO5000,
        [
            (f":BUS2:{command}{separator}{wire}", None),
            (f":BUS2:{command}?", reply),
        ],
    ) as instrument:
        setattr(instrument.bus_2, name, value)
        result = getattr(instrument.bus_2, name)
        if isinstance(value, float):
            assert result == pytest.approx(value)
        else:
            assert result == value


def test_bus_threshold():
    with expected_protocol(
        MSO5000,
        [(":BUS3:THR 0.5,CAN", None), (":BUS3:THR? CAN", "5E-1")],
    ) as instrument:
        instrument.bus_3.set_threshold("CAN", 0.5)
        assert instrument.bus_3.threshold("CAN") == pytest.approx(0.5)


def test_bus_read_events():
    payload = "RS232,Time,Data,,0s,55"
    response = f"#9{len(payload):09d}{payload}"
    with expected_protocol(MSO5000, [(":BUS1:DATA?", response)]) as instrument:
        assert instrument.bus_1.read_events() == payload


def test_bus_export_events():
    with expected_protocol(MSO5000, [(r":BUS4:EEXP D:\events.csv", None)]) as instrument:
        instrument.bus_4.export_events(r"D:\events.csv")


@pytest.mark.parametrize(
    "catalog_id, name, command, value, reply",
    [
        ("TRIGGER.RS232.SOURCE", "rs232_source", "RS232:SOUR", "CHAN2", "CHAN2"),
        ("TRIGGER.RS232.WHEN", "rs232_when", "RS232:WHEN", "DATA", "DATA"),
        ("TRIGGER.RS232.PARITY", "rs232_parity", "RS232:PAR", "EVEN", "EVEN"),
        ("TRIGGER.RS232.STOP", "rs232_stop", "RS232:STOP", 1.5, "1.5"),
        ("TRIGGER.RS232.DATA", "rs232_data", "RS232:DATA", 85, "85"),
        ("TRIGGER.RS232.WIDTH", "rs232_width", "RS232:WIDT", 8, "8"),
        ("TRIGGER.RS232.BAUD", "rs232_baud", "RS232:BAUD", 9600, "9600"),
        ("TRIGGER.RS232.LEVEL", "rs232_level", "RS232:LEV", 0.5, "5E-1"),
        ("TRIGGER.IIC.SCL", "iic_clock_source", "IIC:SCL", "CHAN1", "CHAN1"),
        ("TRIGGER.IIC.SDA", "iic_data_source", "IIC:SDA", "CHAN2", "CHAN2"),
        ("TRIGGER.IIC.WHEN", "iic_when", "IIC:WHEN", "ADDR", "ADDR"),
        ("TRIGGER.IIC.AWIDTH", "iic_address_width", "IIC:AWID", 7, "7"),
        ("TRIGGER.IIC.ADDRESS", "iic_address", "IIC:ADDR", 85, "85"),
        ("TRIGGER.IIC.DIRECTION", "iic_direction", "IIC:DIR", "READ", "READ"),
        ("TRIGGER.IIC.DATA", "iic_data", "IIC:DATA", 4660, "4660"),
        ("TRIGGER.IIC.CLEVEL", "iic_clock_level", "IIC:CLEV", 0.5, "5E-1"),
        ("TRIGGER.IIC.DLEVEL", "iic_data_level", "IIC:DLEV", 0.6, "6E-1"),
        ("TRIGGER.IIC.DBYTES", "iic_data_bytes", "IIC:DBYT", 2, "2"),
        ("TRIGGER.CAN.BAUD", "can_baud", "CAN:BAUD", 500000, "500000"),
        ("TRIGGER.CAN.SOURCE", "can_source", "CAN:SOUR", "CHAN2", "CHAN2"),
        ("TRIGGER.CAN.STYPE", "can_source_type", "CAN:STYP", "RXTX", "RXTX"),
        ("TRIGGER.CAN.WHEN", "can_when", "CAN:WHEN", "IDR", "IDR"),
        ("TRIGGER.CAN.SPOINT", "can_sample_point", "CAN:SPO", 60, "60"),
        ("TRIGGER.CAN.LEVEL", "can_level", "CAN:LEV", 0.7, "7E-1"),
        ("TRIGGER.SPI.SCL", "spi_clock_source", "SPI:SCL", "CHAN1", "CHAN1"),
        ("TRIGGER.SPI.SDA", "spi_data_source", "SPI:SDA", "CHAN2", "CHAN2"),
        ("TRIGGER.SPI.WHEN", "spi_when", "SPI:WHEN", "CS", "CS"),
        ("TRIGGER.SPI.WIDTH", "spi_width", "SPI:WIDT", 16, "16"),
        ("TRIGGER.SPI.DATA", "spi_data", "SPI:DATA", 4660, "4660"),
        ("TRIGGER.SPI.TIMEOUT", "spi_timeout", "SPI:TIM", 1e-06, "1E-6"),
        ("TRIGGER.SPI.SLOPE", "spi_slope", "SPI:SLOP", "NEG", "NEG"),
        ("TRIGGER.SPI.CLEVEL", "spi_clock_level", "SPI:CLEV", 0.5, "5E-1"),
        ("TRIGGER.SPI.DLEVEL", "spi_data_level", "SPI:DLEV", 0.6, "6E-1"),
        ("TRIGGER.SPI.SLEVEL", "spi_select_level", "SPI:SLEV", 0.7, "7E-1"),
        ("TRIGGER.SPI.MODE", "spi_mode", "SPI:MODE", "LOW", "LOW"),
        ("TRIGGER.SPI.CS", "spi_cs", "SPI:CS", "CHAN3", "CHAN3"),
        ("TRIGGER.FLEXRAY.BAUD", "flexray_baud", "FLEX:BAUD", 5000000, "5000000"),
        ("TRIGGER.FLEXRAY.LEVEL", "flexray_level", "FLEX:LEV", 0.5, "5E-1"),
        ("TRIGGER.FLEXRAY.SOURCE", "flexray_source", "FLEX:SOUR", "CHAN1", "CHAN1"),
        ("TRIGGER.FLEXRAY.WHEN", "flexray_when", "FLEX:WHEN", "FRAM", "FRAM"),
        ("TRIGGER.IIS.ALIGNMENT", "iis_alignment", "IIS:ALIG", "LJ", "LJ"),
        ("TRIGGER.IIS.CLOCK.SLOPE", "iis_clock_slope", "IIS:CLOC:SLOP", "NEG", "NEG"),
        ("TRIGGER.IIS.SOURCE.CLOCK", "iis_source_clock", "IIS:SOUR:CLOC", "CHAN1", "CHAN1"),
        ("TRIGGER.IIS.SOURCE.DATA", "iis_source_data", "IIS:SOUR:DATA", "CHAN3", "CHAN3"),
        ("TRIGGER.IIS.SOURCE.WSELECT", "iis_source_word_select", "IIS:SOUR:WSEL", "CHAN2", "CHAN2"),
        ("TRIGGER.IIS.WHEN", "iis_when", "IIS:WHEN", "INR", "INR"),
        ("TRIGGER.IIS.AUDIO", "iis_audio", "IIS:AUD", "LEFT", "LEFT"),
        ("TRIGGER.IIS.DATA", "iis_data", "IIS:DATA", 4660, "4660"),
        ("TRIGGER.LIN.SOURCE", "lin_source", "LIN:SOUR", "CHAN2", "CHAN2"),
        ("TRIGGER.LIN.ID", "lin_id", "LIN:ID", 10, "10"),
        ("TRIGGER.LIN.BAUD", "lin_baud", "LIN:BAUD", 19200, "19200"),
        ("TRIGGER.LIN.STANDARD", "lin_standard", "LIN:STAN", "BOTH", "BOTH"),
        ("TRIGGER.LIN.SAMPLEPOINT", "lin_sample_point", "LIN:SAMP", 50, "50"),
        ("TRIGGER.LIN.WHEN", "lin_when", "LIN:WHEN", "IDD", "IDD"),
        ("TRIGGER.LIN.LEVEL", "lin_level", "LIN:LEV", 0.5, "5E-1"),
        ("TRIGGER.M1553.SOURCE", "m1553_source", "M1553:SOUR", "CHAN4", "CHAN4"),
        ("TRIGGER.M1553.WHEN", "m1553_when", "M1553:WHEN", "DATA", "DATA"),
        ("TRIGGER.M1553.POLARITY", "m1553_polarity", "M1553:POL", "POS", "POS"),
        ("TRIGGER.M1553.ALEVEL", "m1553_alevel", "M1553:ALEV", 1.0, "1E+0"),
        ("TRIGGER.M1553.BLEVEL", "m1553_blevel", "M1553:BLEV", -1.0, "-1E+0"),
    ],
    ids=lambda value: value if isinstance(value, str) and value.startswith("TRIGGER.") else None,
)
def test_protocol_trigger_controls(catalog_id, name, command, value, reply):
    del catalog_id
    wire = f"{value:g}" if isinstance(value, float) else value
    with expected_protocol(
        MSO5000,
        [(f":TRIG:{command} {wire}", None), (f":TRIG:{command}?", reply)],
    ) as instrument:
        setattr(instrument.protocol_trigger, name, value)
        result = getattr(instrument.protocol_trigger, name)
        if isinstance(value, float):
            assert result == pytest.approx(value)
        else:
            assert result == value


def test_mixed_signal_controls_reject_invalid_values():
    with expected_protocol(MSO5000, []) as instrument:
        invalid = [
            (instrument.d_0, "position", 32),
            (instrument.pod_1, "threshold", 15.1),
            (instrument.bus_1, "can_baud", 9_999),
            (instrument.bus_1, "spi_data_bits", 33),
            (instrument.protocol_trigger, "iic_data_bytes", 0),
            (instrument.protocol_trigger, "lin_id", 64),
        ]
        for child, name, value in invalid:
            with pytest.raises(ValueError):
                setattr(child, name, value)
        with pytest.raises(ValueError):
            instrument.logic_analyzer.set_display("POD3", True)
        with pytest.raises(ValueError):
            instrument.logic_analyzer.append_group("GRO1")
        with pytest.raises(ValueError):
            instrument.bus_1.threshold("UNKNOWN")


def test_quick_operation():
    with expected_protocol(
        MSO5000,
        [(":QUIC:OPER SWAV", None), (":QUIC:OPER?", "SWAV")],
    ) as instrument:
        instrument.quick.operation = "SWAV"
        assert instrument.quick.operation == "SWAV"


def test_quick_operation_rejects_invalid_value():
    with expected_protocol(MSO5000, []) as instrument, pytest.raises(ValueError):
        instrument.quick.operation = "PRINT"


@pytest.mark.parametrize(
    "name, command, value, reply",
    [
        ("enabled", "ENAB", True, "1"),
        ("display_type", "DISP", "DISP_CHART", "DISP_CHART"),
        ("source", "SOUR", "SOURCE1", "SOURCE1"),
        ("sweep_type", "SWEE", "LOG_SWEEP", "LOG_SWEEP"),
        ("reference_input", "REFI", "CHAN1", "CHAN1"),
        ("reference_output", "REFO", "CHAN2", "CHAN2"),
        ("impedance", "IMP", "OMEG", "OMEG"),
        ("start", "STAR", 10.0, "1E+1"),
        ("stop", "STOP", 1e6, "1E+6"),
        ("point", "POIN", 100, "100"),
        ("voltage_profile", "VOLT:PROF", False, "0"),
    ],
)
def test_bode_plot_controls(name, command, value, reply):
    wire = (
        int(value)
        if isinstance(value, bool)
        else f"{value:g}"
        if isinstance(value, float)
        else value
    )
    with expected_protocol(
        MSO5000, [(f":BODE:{command} {wire}", None), (f":BODE:{command}?", reply)]
    ) as instrument:
        setattr(instrument.bode_plot, name, value)
        result = getattr(instrument.bode_plot, name)
        assert result == pytest.approx(value) if isinstance(value, float) else result == value


def test_bode_plot_voltage_and_results():
    with expected_protocol(
        MSO5000,
        [
            (":BODE:VOLT 0.2,F1KHZ", None),
            (":BODE:VOLT? F1KHZ", "2E-1"),
            (":BODE:GMAR?", "12.5"),
            (":BODE:GMAR:FREQ?", "1000"),
            (":BODE:PMAR?", "45"),
            (":BODE:PMAR:FREQ?", "2000"),
        ],
    ) as instrument:
        instrument.bode_plot.set_voltage("F1KHZ", 0.2)
        assert instrument.bode_plot.voltage("F1KHZ") == pytest.approx(0.2)
        assert instrument.bode_plot.gain_margin == pytest.approx(12.5)
        assert instrument.bode_plot.gain_margin_frequency == pytest.approx(1000)
        assert instrument.bode_plot.phase_margin == pytest.approx(45)
        assert instrument.bode_plot.phase_margin_frequency == pytest.approx(2000)


@pytest.mark.parametrize(
    "name, command, value, reply",
    [
        ("enabled", "ENAB", True, "1"),
        ("source", "SOUR", "CHAN2", "CHAN2"),
        ("mode", "MODE", "FREQ", "FREQ"),
        ("digits", "NDIG", 6, "6"),
        ("totalize_enabled", "TOT:ENAB", False, "0"),
    ],
)
def test_counter_controls(name, command, value, reply):
    wire = int(value) if isinstance(value, bool) else value
    with expected_protocol(
        MSO5000, [(f":COUN:{command} {wire}", None), (f":COUN:{command}?", reply)]
    ) as instrument:
        setattr(instrument.counter, name, value)
        assert getattr(instrument.counter, name) == value


def test_counter_result_and_action():
    with expected_protocol(
        MSO5000, [(":COUN:CURR?", "1.25E+6"), (":COUN:TOT:CLE", None)]
    ) as instrument:
        assert instrument.counter.current == pytest.approx(1.25e6)
        instrument.counter.clear_totalizer()


@pytest.mark.parametrize(
    "name, command, value, reply",
    [
        ("enabled", "ENAB", True, "1"),
        ("source", "SOUR", "CHAN2", "CHAN2"),
        ("mode", "MODE", "DCRM", "DCRM"),
    ],
)
def test_dvm_controls(name, command, value, reply):
    wire = int(value) if isinstance(value, bool) else value
    with expected_protocol(
        MSO5000, [(f":DVM:{command} {wire}", None), (f":DVM:{command}?", reply)]
    ) as instrument:
        setattr(instrument.dvm, name, value)
        assert getattr(instrument.dvm, name) == value


def test_dvm_current():
    with expected_protocol(MSO5000, [(":DVM:CURR?", "0.125000")]) as instrument:
        assert instrument.dvm.current == pytest.approx(0.125)


@pytest.mark.parametrize(
    "name, command, value, reply",
    [
        ("type", "TYPE", "QUAL", "QUAL"),
        ("current_source", "CURR", "CHAN1", "CHAN1"),
        ("voltage_source", "VOLT", "CHAN2", "CHAN2"),
        ("quality_frequency_reference", "QUAL:FREQ", "VOLT", "VOLT"),
        ("reference_level_method", "REFL:METH", "PERC", "PERC"),
        ("reference_level_percent_high", "REFL:PERC:HIGH", 90, "90"),
        ("reference_level_percent_low", "REFL:PERC:LOW", 10, "10"),
        ("reference_level_percent_mid", "REFL:PERC:MID", 50, "50"),
    ],
)
def test_power_analysis_controls(name, command, value, reply):
    with expected_protocol(
        MSO5000, [(f":POW:{command} {value}", None), (f":POW:{command}?", reply)]
    ) as instrument:
        setattr(instrument.power_analysis, name, value)
        assert getattr(instrument.power_analysis, name) == value


@pytest.mark.parametrize(
    "name, command, value, reply",
    [
        ("frequency_fixed", "FREQ", 1000.0, "1E+3"),
        ("phase_adjust", "PHAS", 90.0, "9E+1"),
        ("function_shape", "FUNC", "SIN", "SIN"),
        ("function_ramp_symmetry", "FUNC:RAMP:SYMM", 50.0, "5E+1"),
        ("voltage_level_immediate_amplitude", "VOLT", 0.5, "5E-1"),
        ("voltage_level_immediate_offset", "VOLT:OFFS", 0.0, "0"),
        ("pulse_duty_cycle", "PULS:DCYC", 20.0, "20"),
        ("type", "TYPE", "NONE", "NONE"),
        ("mod_type", "MOD:TYPE", "AM", "AM"),
        ("mod_am_depth", "MOD:AM", 100, "100"),
        ("mod_am_internal_frequency", "MOD:AM:INT:FREQ", 1000, "1000"),
        ("mod_fm_internal_frequency", "MOD:FM:INT:FREQ", 1000, "1000"),
        ("mod_am_internal_function", "MOD:AM:INT:FUNC", "SIN", "SIN"),
        ("mod_fm_internal_function", "MOD:FM:INT:FUNC", "SQU", "SQU"),
        ("mod_fm_deviation", "MOD:FM:DEV", 1000.0, "1E+3"),
        ("sweep_type", "SWE:TYPE", "LOG", "LOG"),
        ("sweep_time", "SWE:STIM", 1.0, "1"),
        ("sweep_back_time", "SWE:BTIM", 0.0, "0"),
        ("burst_type", "BURS:TYPE", "NCYC", "NCYC"),
        ("burst_cycles", "BURS:CYCL", 10, "10"),
        ("burst_delay", "BURS:DEL", 0.0, "0"),
        ("output_enabled", "OUTP2", True, "1"),
        ("output_impedance", "OUTP2:IMP", "OMEG", "OMEG"),
    ],
)
def test_awg_controls(name, command, value, reply):
    wire = (
        int(value)
        if isinstance(value, bool)
        else f"{value:g}"
        if isinstance(value, float)
        else value
    )
    with expected_protocol(
        MSO5000, [(f":SOUR2:{command} {wire}", None), (f":SOUR2:{command}?", reply)]
    ) as instrument:
        setattr(instrument.awg_2, name, value)
        result = getattr(instrument.awg_2, name)
        assert result == pytest.approx(value) if isinstance(value, float) else result == value


def test_awg_actions_and_apply_query():
    with expected_protocol(
        MSO5000,
        [
            (":SOUR1:PHAS:INIT", None),
            (":SOUR1:APPL?", "SIN,1000,0.5,0,90"),
            (":SOUR1:APPL:NOIS 0.5,0", None),
            (":SOUR1:APPL:PULS 1000,0.5,0,90", None),
            (":SOUR1:APPL:RAMP", None),
            (":SOUR1:APPL:SIN 1000", None),
            (":SOUR1:APPL:SQU 1000,0.5", None),
            (":SOUR1:APPL:USER 1000,0.5,0", None),
        ],
    ) as instrument:
        instrument.awg_1.reset_phase()
        assert instrument.awg_1.get_applied_waveform() == ("SIN", "1000", "0.5", "0", "90")
        instrument.awg_1.apply_noise(0.5, 0)
        instrument.awg_1.apply_pulse(1000, 0.5, 0, 90)
        instrument.awg_1.apply_ramp()
        instrument.awg_1.apply_sine(1000)
        instrument.awg_1.apply_square(1000, 0.5)
        instrument.awg_1.apply_user(1000, 0.5, 0)


def test_awg_upload_waveform():
    data = b"\x00\x00\xff\x3f"
    with expected_protocol(
        MSO5000, [(b":TRAC2:DATA:DAC16 volatile,END,#14" + data, None)]
    ) as instrument:
        instrument.awg_2.upload_waveform(data)


def test_integrated_functions_reject_invalid_values():
    with expected_protocol(MSO5000, []) as instrument:
        for child, name, value in [
            (instrument.bode_plot, "point", 9),
            (instrument.counter, "digits", 7),
            (instrument.power_analysis, "reference_level_percent_high", 101),
            (instrument.awg_1, "phase_adjust", 361),
            (instrument.awg_1, "burst_cycles", 0),
        ]:
            with pytest.raises(ValueError):
                setattr(child, name, value)
        with pytest.raises(ValueError):
            instrument.awg_1.apply_sine(None, 0.5)
        with pytest.raises(ValueError):
            instrument.awg_1.upload_waveform(b"\x00\x00")
        with pytest.raises(TypeError):
            instrument.awg_1.upload_waveform([0, 1])  # pyright: ignore[reportArgumentType]
