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


from pymeasure.instruments.anaheimautomation import DPSeriesMotorController


def test_init():
    with expected_protocol(
            DPSeriesMotorController, []):
        pass  # Verify the expected communication.


def test_basespeed():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0VB", b"123")],
            ) as instr:
        assert instr.basespeed == 123


def test_basespeed_setter():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0B123", None)],
            ) as instr:
        instr.basespeed = 123


def test_step_position():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0VZ", b"13")],
            ) as instr:
        assert instr.step_position == 13


def test_step_position_setter():
    with expected_protocol(
            DPSeriesMotorController,
            [(b"@0P13", None), (b"@0G", None)],
            ) as instr:
        instr.step_position = 13
