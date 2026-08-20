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
