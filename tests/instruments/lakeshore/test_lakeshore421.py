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

from pymeasure.instruments.lakeshore import LakeShore421


def test_init():
    with expected_protocol(
            LakeShore421,
            [],
            ):
        pass  # Verify the expected communication.


def test_unit():
    with expected_protocol(
            LakeShore421,
            [(b"UNIT?", b"G")],
            ) as instr:
        assert instr.unit == "G"


def test_unit_setter():
    with expected_protocol(
            LakeShore421,
            [(b"UNIT G", None)],
            ) as instr:
        instr.unit = "G"


def test_max_hold_reset():
    with expected_protocol(
            LakeShore421,
            [(b"MAXC", None)],
            ) as instr:
        instr.max_hold_reset()
