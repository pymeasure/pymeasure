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

from pymeasure.test import expected_protocol

from pymeasure.instruments.lakeshore import LakeShore425


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
