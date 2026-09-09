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

from pymeasure.instruments.rigol import MSO5000, DHOBase, RigolOscilloscope
from pymeasure.instruments.rigol.rigol_oscilloscope import _parse_ieee_block
from pymeasure.test import expected_protocol


def test_rigol_oscilloscope_drivers_share_protocol_base():
    assert issubclass(DHOBase, RigolOscilloscope)
    assert issubclass(MSO5000, RigolOscilloscope)
    assert DHOBase._read_ieee_block is RigolOscilloscope._read_ieee_block
    assert MSO5000._read_ieee_block is RigolOscilloscope._read_ieee_block


def test_parse_ieee_block_preserves_terminator_bytes_in_payload():
    payload = b"first\nsecond"
    block = f"#{len(str(len(payload)))}{len(payload)}".encode() + payload + b"\n"
    assert _parse_ieee_block(block, "Test response") == payload


@pytest.mark.parametrize(
    "block, message",
    [
        (b"!14data", "does not start with an IEEE block header"),
        (b"#0data", "invalid IEEE block header"),
        (b"#2x4data", "invalid IEEE block header"),
        (b"#14dat", "declares 4 data bytes, received 3"),
        (b"#14datax", "beyond its declared IEEE block length"),
    ],
)
def test_parse_ieee_block_rejects_malformed_blocks(block, message):
    with pytest.raises(ValueError, match=message):
        _parse_ieee_block(block, "Test response")


def test_query_waveform_preamble_rejects_wrong_value_count():
    with (
        expected_protocol(RigolOscilloscope, [(":WAV:PRE?", "0,1")]) as inst,
        pytest.raises(ValueError, match="Expected 10 waveform preamble values"),
    ):
        inst._query_waveform_preamble()


def test_read_ieee_block_rejects_zero_digit_count():
    with expected_protocol(RigolOscilloscope, [(":WAV:DATA?", b"#0")]) as inst:
        inst.write(":WAV:DATA?")
        with pytest.raises(ValueError, match="invalid IEEE block header"):
            inst._read_ieee_block("Test response")


def test_read_ieee_block_does_not_drain_after_data_beyond_declared_length(monkeypatch):
    responses = iter([b"#1", b"4", b"data", b"x"])
    calls = []

    def read_bytes(count, break_on_termchar=False):
        """Return the next prepared response and record the read arguments."""
        calls.append((count, break_on_termchar))
        return next(responses)

    with expected_protocol(RigolOscilloscope, []) as inst:
        monkeypatch.setattr(inst, "read_bytes", read_bytes)
        with pytest.raises(ValueError, match="beyond its declared IEEE block length"):
            inst._read_ieee_block("Test response")

    assert calls == [(2, False), (1, False), (4, False), (1, False)]
