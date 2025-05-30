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
from pymeasure.instruments.aimtti.ld400p import LD400P


def test_mode():
    with expected_protocol(
        LD400P,
        [
            ("MODE P", None),
            ("MODE?", "MODE P"),
        ],
    ) as inst:
        inst.mode = "P"
        assert inst.mode == "P"


def test_mode_write_invalid():
    with expected_protocol(LD400P, []) as inst:
        with pytest.raises(ValueError):
            inst.mode = "X"


def test_level_select():
    with expected_protocol(
        LD400P,
        [
            ("LVLSEL V", None),
            ("LVLSEL?", "LVLSEL V"),
        ],
    ) as inst:
        inst.level_select = "V"
        assert inst.level_select == "V"


def test_level_a():
    with expected_protocol(
        LD400P,
        [
            ("A 10.5", None),
            ("A?", "A 10.5W"),
        ],
    ) as inst:
        inst.level_a = 10.5
        assert inst.level_a == 10.5


def test_level_b():
    with expected_protocol(
        LD400P,
        [
            ("B 10.5", None),
            ("B?", "B 10.5W"),
        ],
    ) as inst:
        inst.level_b = 10.5
        assert inst.level_b == 10.5


def test_input_enabled():
    with expected_protocol(
        LD400P,
        [
            ("INP 1", None),
            ("INP?", "INP 1"),
        ],
    ) as inst:
        inst.input_enabled = True
        enabled = inst.input_enabled
        assert enabled and isinstance(enabled, bool)


def test_voltage():
    with expected_protocol(
        LD400P,
        [
            ("V?", "3.14V"),
        ],
    ) as inst:
        assert inst.voltage == 3.14


def test_current():
    with expected_protocol(
        LD400P,
        [
            ("I?", "3.14A"),
        ],
    ) as inst:
        assert inst.current == 3.14


def test_options():
    with expected_protocol(
        LD400P,
        [],
    ) as inst:
        with pytest.raises(AttributeError):
            _ = inst.options
