#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments.keithley.keithley2200 import Keithley2200


def test_init():
    with expected_protocol(
        Keithley2200,
        [],
    ):
        pass  # Verify the expected communication.


def test_voltage():
    # instr.ch1.voltage should produce the following commands
    with expected_protocol(
        Keithley2200,
        [
            (b"INST:SEL CH1;VOLT 1.456", None),
            (b"INST:SEL CH1;VOLT?", 1.456),
            (b"INST:SEL CH1;MEAS:VOLT?", 1.456),
            (b"INST:SEL CH3;VOLT 1.456", None),
        ],
    ) as instr:
        instr.ch_1.voltage_setpoint = 1.456
        assert instr.ch_1.voltage_setpoint == 1.456
        assert instr.ch_1.voltage == 1.456
        instr.ch_3.voltage_setpoint = 1.456


def test_current():
    # instr.ch1.voltage should produce the following commands
    with expected_protocol(
        Keithley2200,
        [(b"INST:SEL CH3;CURR 1.456", None), (b"INST:SEL CH1;CURR 2.654", None)],
    ) as instr:
        instr.ch_3.current_limit = 1.456
        instr.ch_1.current_limit = 2.654


def test_output_enabled():
    with expected_protocol(
        Keithley2200,
        [(b"INST:SEL CH1;SOURCE:OUTP:ENAB 1", None)],
    ) as instr:
        instr.ch_1.output_enabled = True
