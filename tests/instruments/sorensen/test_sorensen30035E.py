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
import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.sorensen.sorensen30035E import Sorensen30035E


def test_output_delay():
    with expected_protocol(
        Sorensen30035E,
        [("OUTPut:PROTection:DELay?", "5.0"),
         ("OUTPut:PROTection:DELay 234.1", None)
         ],
    ) as inst:
        assert inst.output_delay == pytest.approx(5.0)
        inst.output_delay = 234.1


def test_current_read():
    with expected_protocol(
        Sorensen30035E,
        [("MEAS:CURRent?", "2.41")],
    ) as inst:
        assert inst.current == pytest.approx(2.41)


def test_current_setpoint():
    with expected_protocol(
        Sorensen30035E,
        [("SOUR:CURR?", "2.41"),
         ("SOUR:CURR 1.3", None)],
    ) as inst:
        assert inst.current_setpoint == pytest.approx(2.41)
        inst.current_setpoint = 1.3
        

def test_current_limit():
    with expected_protocol(
        Sorensen30035E,
        [("SOUR:CURR:LIM 1.3", None),
         ("SOUR:CURR:LIM?", "2.41")],
    ) as inst:
        inst.current_limit = 1.3
        assert inst.current_limit == pytest.approx(2.41)


def test_voltage_read():
    with expected_protocol(
        Sorensen30035E,
        [("MEAS:VOLT?", "250.1")],
    ) as inst:
        assert inst.voltage == pytest.approx(250.1)


def test_voltage_setpoint():
    with expected_protocol(
        Sorensen30035E,
        [("SOUR:VOLT 100.1", None),
         ("SOUR:VOLT?", "250.1")],
    ) as inst:
        inst.voltage_setpoint = 100.1
        assert inst.voltage_setpoint == pytest.approx(250.1)


def test_voltage_limit():
    with expected_protocol(
        Sorensen30035E,
        [("SOUR:VOLT:LIM 300", None),
         ("SOUR:VOLT:LIM?", "300")],
    ) as inst:
        inst.voltage_limit = 300
        assert inst.voltage_limit == pytest.approx(300)


def test_ramp_to_current():
    with expected_protocol(
        Sorensen30035E,
        [("SOUR:CURR:RAMP 3.5 10", None)],
    ) as inst:
        inst.ramp_to_current(3.5)


def test_ramp_to_voltage():
    with expected_protocol(
        Sorensen30035E,
        [("SOUR:VOLT:RAMP 300 10", None)],
    ) as inst:
        inst.ramp_to_voltage(300)


def test_output_enabled():
    with expected_protocol(
        Sorensen30035E,
        [("OUTPut:ISOLation?", 0)],
    ) as inst:
        assert inst.output_enabled == False
