#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.kepco import KepcoBOP3612


def test_init():
    with expected_protocol(
            KepcoBOP3612,
            [],
    ):
        pass  # Verify the expected communication.


def test_bop_test_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'DIAG:TST?', b'0')],
    ) as inst:
        assert inst.bop_test == 0


def test_confidence_test_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'*TST?', b'0')],
    ) as inst:
        assert inst.confidence_test == 0


def test_current_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'MEASure:CURRent?', b'4.99E-3')],
    ) as inst:
        assert inst.current == 0.00499


def test_current_setpoint_setter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'CURRent 0.1', None)],
    ) as inst:
        inst.current_setpoint = 0.1


def test_current_setpoint_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'CURRent?', b'9.989E-2')],
    ) as inst:
        assert inst.current_setpoint == 0.09989


def test_id_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'*IDN?', b'KEPCO,BIT 4886 36-12  08-04-2023,H249977,4.04-1.82')],
    ) as inst:
        assert inst.id == 'KEPCO,BIT 4886 36-12  08-04-2023,H249977,4.04-1.82'


def test_output_enabled_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'OUTPut?', b'0')],
    ) as inst:
        assert inst.output_enabled is False


def test_voltage_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'MEASure:VOLTage?', b'8.0E-3')],
    ) as inst:
        assert inst.voltage == 0.008


def test_voltage_setpoint_setter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'VOLTage 0.1', None)],
    ) as inst:
        inst.voltage_setpoint = 0.1


def test_voltage_setpoint_getter():
    with expected_protocol(
            KepcoBOP3612,
            [(b'VOLTage?', b'1.000E-1')],
    ) as inst:
        assert inst.voltage_setpoint == 0.1


def test_beep():
    with expected_protocol(
            KepcoBOP3612,
            [(b'SYSTem:BEEP', None)],
    ) as inst:
        assert inst.beep() is None
