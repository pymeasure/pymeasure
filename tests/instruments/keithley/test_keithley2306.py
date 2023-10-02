#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.instruments.keithley.keithley2306 import Keithley2306


def test_init():
    with expected_protocol(
            Keithley2306,
            [],
            ):
        pass  # Verify the expected communication.


def test_nplc():
    with expected_protocol(
            Keithley2306,
            [(b":SENS2:NPLC?", b"1.234")],
            ) as instr:
        assert instr.ch2.nplc == 1.234


def test_nplc_setter():
    with expected_protocol(
            Keithley2306,
            [(b":SENS2:NPLC 1.234", None)],
            ) as instr:
        instr.ch2.nplc = 1.234


def test_relay():
    with expected_protocol(
            Keithley2306,
            [(b":OUTP:REL2?", b"ONE")],
            ) as instr:
        assert instr.relay2.closed is True


def test_relay_setter():
    with expected_protocol(
            Keithley2306,
            [(b":OUTP:REL2 ONE", None)],
            ) as instr:
        instr.relay2.closed = True


def test_step():
    with expected_protocol(
            Keithley2306,
            [(b":SENS:PCUR:STEP:TLEV3?", 4)],
            ) as instr:
        step = instr.ch1.pulse_current_step(3)
        assert step.trigger_level == 4
