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

import io

import pytest

from pymeasure.instruments.rigol.rigol_ds1000z import (
    RigolDS1000Z,
    DisplayImageFormat,
    _normalize_memory_depth_value,
    _parse_memory_depth,
    _parse_tmc_block,
    _parse_waveform_preamble,
)
from pymeasure.test import expected_protocol


def _stream_reader(payload):
    stream = io.BytesIO(payload)

    def reader(count, break_on_termchar=False):
        return stream.read(count)

    return reader


def _display_queries(active_channels):
    """Helper that yields command/response pairs for channel display state queries."""
    pairs = []
    for index in range(1, 5):
        state = b"1\n" if index in active_channels else b"0\n"
        pairs.append((f":CHAN{index}:DISP?".encode("ascii"), state))
    return pairs


def test_parse_waveform_preamble_success():
    reply = "1,2,750,16,0.001,0.0,0.0,0.02,-4.0,128.0"
    parsed = _parse_waveform_preamble(reply)
    assert parsed["format_code"] == 1
    assert parsed["points"] == 750
    assert parsed["x_increment"] == pytest.approx(0.001)
    assert parsed["y_increment"] == pytest.approx(0.02)


def test_parse_waveform_preamble_invalid_field_count():
    with pytest.raises(RuntimeError):
        _parse_waveform_preamble("1,2,3")


def test_parse_tmc_block_extracts_payload_and_skips_terminator():
    reader = _stream_reader(b"#40005hello\n")
    payload = _parse_tmc_block(reader)
    assert payload == b"hello"


def test_parse_tmc_block_rejects_invalid_header():
    reader = _stream_reader(b"!!0005hello")
    with pytest.raises(RuntimeError):
        _parse_tmc_block(reader)


@pytest.mark.parametrize(
    "value,expected",
    [
        (" auto ", ("AUTO", None)),
        ("6000", ("6000", 6000)),
        (6000, ("6000", 6000)),
    ],
)
def test_normalize_memory_depth_value_success(value, expected):
    assert _normalize_memory_depth_value(value) == expected


def test_normalize_memory_depth_value_invalid_string():
    with pytest.raises(ValueError):
        _normalize_memory_depth_value("not-a-number")


def test_normalize_memory_depth_value_rejects_unknown_numeric():
    with pytest.raises(ValueError):
        _normalize_memory_depth_value(12345)


def test_parse_memory_depth_invalid_reply():
    with pytest.raises(RuntimeError):
        _parse_memory_depth("banana")



def test_display_grab_image_includes_optional_arguments():
    with expected_protocol(
        RigolDS1000Z,
        [(b":DISP:DATA? [ON,OFF,PNG]", b"#40004data")]
    ) as inst:
        result = inst.display.grab_image(color=True, invert=False, image_format=DisplayImageFormat.PNG)
        assert result == b"data"



def test_display_grab_image_rejects_unsupported_format():
    with expected_protocol(RigolDS1000Z, []) as inst:
        with pytest.raises(ValueError):
            inst.display.grab_image(image_format="svg")



def test_display_type_set_and_get():
    with expected_protocol(
        RigolDS1000Z,
        [(b":DISP:TYPE VECT", None), (b":DISP:TYPE?", b"VECT")]
    ) as inst:
        inst.display.type = "VECT"
        assert inst.display.type == "VECT"



def test_display_type_setter_rejects_invalid_mode():
    with expected_protocol(RigolDS1000Z, []) as inst:
        with pytest.raises(ValueError):
            inst.display.type = "lines"



def test_display_persistence_set_and_get_inf():
    with expected_protocol(
        RigolDS1000Z,
        [(b":DISP:GRAD:TIME INF", None), (b":DISP:GRAD:TIME?", b"inf")]
    ) as inst:
        inst.display.persistence = "INF"
        assert inst.display.persistence == float('inf')



def test_display_persistence_rejects_invalid_value():
    with expected_protocol(RigolDS1000Z, []) as inst:
        with pytest.raises(ValueError):
            inst.display.persistence = "fast"



def test_waveform_brightness_setter_rejects_out_of_range():
    with expected_protocol(RigolDS1000Z, []) as inst:
        with pytest.raises(ValueError):
            inst.display.waveform_brightness = 200


def test_memory_depth_single_channel_allows_maximum_depth():
    commands = _display_queries({1})
    commands.append((b":ACQ:MDEP 24000000", None))
    with expected_protocol(RigolDS1000Z, commands) as inst:
        inst.memory_depth = 24_000_000


def test_memory_depth_rejects_value_not_allowed_for_active_channels():
    commands = _display_queries({1})
    with expected_protocol(RigolDS1000Z, commands) as inst:
        with pytest.raises(ValueError):
            inst.memory_depth = 6000


def test_memory_depth_two_channels_accepts_mid_range_depth():
    commands = _display_queries({1, 2})
    commands.append((b":ACQ:MDEP 6000000", None))
    with expected_protocol(RigolDS1000Z, commands) as inst:
        inst.memory_depth = 6_000_000


def test_memory_depth_respects_digital_channel_hint():
    commands = _display_queries({1}) + _display_queries({1})
    commands.append((b":ACQ:MDEP 24000000", None))
    with expected_protocol(RigolDS1000Z, commands) as inst:
        inst.set_digital_channel_hint(16)
        with pytest.raises(ValueError):
            inst.memory_depth = 24_000_000
        inst.set_digital_channel_hint(0)
        inst.memory_depth = 24_000_000


def test_memory_depth_setter_accepts_auto_without_queries():
    with expected_protocol(RigolDS1000Z, [(b":ACQ:MDEP AUTO", None)]) as inst:
        inst.memory_depth = "AUTO"


def test_memory_depth_getter_parses_auto():
    with expected_protocol(RigolDS1000Z, [(b":ACQ:MDEP?", b"AUTO\n")]) as inst:
        assert inst.memory_depth == "AUTO"


def test_memory_depth_getter_parses_numeric_value():
    with expected_protocol(RigolDS1000Z, [(b":ACQ:MDEP?", b"6000000\n")]) as inst:
        assert inst.memory_depth == 6_000_000


def test_set_digital_channel_hint_rejects_invalid_value():
    with expected_protocol(RigolDS1000Z, []) as inst:
        with pytest.raises(ValueError):
            inst.set_digital_channel_hint(4)
