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

from pymeasure.instruments.rigol import RigolDS1000Z
from pymeasure.test import expected_protocol


def _display_queries(active_channels):
    """Helper that yields command/response pairs for channel display state queries."""
    pairs = []
    for index in range(1, 5):
        state = b"1\n" if index in active_channels else b"0\n"
        pairs.append((f":CHAN{index}:DISP?".encode("ascii"), state))
    return pairs


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
