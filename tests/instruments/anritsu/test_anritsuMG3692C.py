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

from pymeasure.instruments.anritsu import AnritsuMG3692C


def test_init():
    with expected_protocol(
            AnritsuMG3692C,
            [],
            ):
        pass  # Verify the expected communication.


def test_power():
    with expected_protocol(
            AnritsuMG3692C,
            [(b":POWER?;", "123.45")],
            ) as instr:
        assert instr.power == 123.45


def test_power_setter():
    with expected_protocol(
            AnritsuMG3692C,
            [(b":POWER 123.45 dBm;", None)],
            ) as instr:
        instr.power = 123.45


def test_frequency():
    with expected_protocol(
            AnritsuMG3692C,
            [(b":FREQUENCY?;", "123.45")],
            ) as instr:
        assert instr.frequency == 123.45


def test_frequency_setter():
    with expected_protocol(
            AnritsuMG3692C,
            [(b":FREQUENCY 1.234500e+02 Hz;", None)],
            ) as instr:
        instr.frequency = 123.45


def test_output():
    with expected_protocol(
            AnritsuMG3692C,
            [(b":OUTPUT?", "1")],
            ) as instr:
        assert instr.output is True


def test_output_setter():
    with expected_protocol(
            AnritsuMG3692C,
            [(b":OUTPUT ON;", None)],
            ) as instr:
        instr.output = True
