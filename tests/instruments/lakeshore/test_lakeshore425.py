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

from pymeasure.test import expected_protocol

from pymeasure.instruments.lakeshore import LakeShore425

import pytest


def test_init():
    with expected_protocol(
            LakeShore425, []):
        pass  # Verify the expected communication.


def test_unit():
    # from manual
    with expected_protocol(
            LakeShore425, [(b"UNIT?", b"1")]) as instr:
        assert instr.unit == "G"


def test_unit_setter():
    # from manual
    with expected_protocol(
            LakeShore425, [(b"UNIT 2", None)]) as instr:
        instr.unit = "T"


def test_field():
    # from manual
    with expected_protocol(
            LakeShore425,
            [(b"RDGFIELD?", b"+123.456E-01")]
            ) as instr:
        assert instr.field == 123.456e-1


def test_zero_probe():
    # from manual
    with expected_protocol(
            LakeShore425, [(b"ZPROBE", None)]) as instr:
        instr.zero_probe()


def test_range():
    # from manual: map_values 1->35, 2->350, 3->3500, 4->35000
    with expected_protocol(
            LakeShore425,
            [(b"RANGE?", b"1"),
             (b"RANGE?", b"2"),
             (b"RANGE?", b"3"),
             (b"RANGE?", b"4")]) as instr:
        assert instr.range == 35
        assert instr.range == 350
        assert instr.range == 3500
        assert instr.range == 35000


def test_range_setter():
    # from manual
    with expected_protocol(
            LakeShore425, [(b"RANGE 3", None)]) as instr:
        instr.range = 3500


def test_range_setter_truncated_discrete_set():
    # in-between values are truncated to the nearest larger valid value
    # 100 -> 350 -> mapped to 2
    with expected_protocol(
            LakeShore425, [(b"RANGE 2", None)]) as instr:
        instr.range = 100


def test_range_setter_truncated_discrete_set_above_max():
    # value larger than max is truncated to max (35000 -> 4)
    with expected_protocol(
            LakeShore425, [(b"RANGE 4", None)]) as instr:
        instr.range = 100000


def test_auto_range():
    # from manual
    with expected_protocol(
            LakeShore425, [(b"AUTO", None)]) as instr:
        instr.auto_range()


def test_mode_getter():
    # from manual: RDGMODE? returns mode,filter,band
    with expected_protocol(
            LakeShore425, [(b"RDGMODE?", b"1,0,1")]) as instr:
        assert instr.mode == (1.0, 0.0, 1.0)


def test_mode_setter():
    # from manual: RDGMODE mode,filter,band
    with expected_protocol(
            LakeShore425, [(b"RDGMODE 2,1,1", None)]) as instr:
        instr.mode = (2, 1, 1)


def test_dc_mode_wideband():
    # wideband=True -> mode (1, 0, 1)
    with expected_protocol(
            LakeShore425, [(b"RDGMODE 1,0,1", None)]) as instr:
        instr.dc_mode(wideband=True)


def test_dc_mode_narrowband():
    # wideband=False -> mode (1, 0, 2)
    with expected_protocol(
            LakeShore425, [(b"RDGMODE 1,0,2", None)]) as instr:
        instr.dc_mode(wideband=False)


def test_ac_mode_wideband():
    # wideband=True -> mode (2, 1, 1)
    with expected_protocol(
            LakeShore425, [(b"RDGMODE 2,1,1", None)]) as instr:
        instr.ac_mode(wideband=True)


def test_ac_mode_narrowband():
    # wideband=False -> mode (2, 1, 2)
    with expected_protocol(
            LakeShore425, [(b"RDGMODE 2,1,2", None)]) as instr:
        instr.ac_mode(wideband=False)


def test_measure():
    # reads field N times, returns (mean, std)
    with expected_protocol(
            LakeShore425,
            [(b"RDGFIELD?", b"+100.000E-01"),
             (b"RDGFIELD?", b"+200.000E-01")]) as instr:
        mean, std = instr.measure(2, delay=0)
        assert mean == pytest.approx(15.0)
        assert std == pytest.approx(5.0)


def test_measure_aborts_early():
    # has_aborted callback returns True after the first read; field is read
    # only once even though points=100.
    call_count = {"n": 0}

    def abort_after_first():
        call_count["n"] += 1
        return call_count["n"] > 1

    with expected_protocol(
            LakeShore425,
            [(b"RDGFIELD?", b"+100.000E-01")]) as instr:
        mean, std = instr.measure(100, has_aborted=abort_after_first, delay=0)
        # only one read happened; remaining 99 points remain 0
        assert mean == pytest.approx(0.1)
        assert std > 0
