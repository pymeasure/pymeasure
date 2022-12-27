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


def test_set_voltage_current():
    # instr.ch1.voltage should produce the following commands
    with expected_protocol(
        Keithley2200,
        [(b"INST:SEL CH1;VOLT 1.456", None)],
    ) as instr:
        instr.ch1.voltage = 1.456

    with expected_protocol(
        Keithley2200,
        [("INST:SEL CH1;VOLT?", 1.456)],
    ) as inst:
        val = inst.ch1.voltage
        assert val == 1.456

    with expected_protocol(
        Keithley2200,
        [("INST:SEL CH1;MEAS:VOLT?", 1.456)],
    ) as inst:
        val = inst.ch1.measure_voltage
        assert val == 1.456

    with expected_protocol(
        Keithley2200,
        [(b"INST:SEL CH3;VOLT 1.456", None)],
    ) as instr:
        instr.ch3.voltage = 1.456

    with expected_protocol(
        Keithley2200,
        [(b"INST:SEL CH1;CURR 2.654", None)],
    ) as instr:
        instr.ch1.current = 2.654

    with expected_protocol(
        Keithley2200,
        [(b"INST:SEL CH1;SOURCE:OUTP:ENAB 1", None)],
    ) as instr:
        instr.ch1.output_enabled = True