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
from pymeasure.instruments.eurotest.eurotestHPP120256 import EurotestHPP120256


def test_voltage_setpoint():
    """Verify the communication of the voltage setter/getter."""
    with expected_protocol(
            EurotestHPP120256,
            [("U,1.200kV", None),
             ("STATUS,U", "U, RANGE=3.000kV, VALUE=2.458kV")],
    ) as inst:
        inst.voltage_setpoint = 1.200
        assert inst.voltage_setpoint == 2.458


def test_current_limit():
    """Verify the communication of the current setter/getter."""
    with expected_protocol(
            EurotestHPP120256,
            [("I,1.200mA", None),
             ("STATUS,I", "I, RANGE=5000mA, VALUE=1739mA")],
    ) as inst:
        inst.current_limit = 1.200
        assert inst.current_limit == 1739.0


def test_voltage_ramp():
    """Verify the communication of the ramp setter/getter."""
    with expected_protocol(
            EurotestHPP120256,
            [("RAMP,3000V/s", None),
             ("STATUS,RAMP", "RAMP, RANGE=3000V/s, VALUE=1000V/s")],
    ) as inst:
        inst.voltage_ramp = 3000
        assert inst.voltage_ramp == 1000.0


def test_voltage():
    """Verify the communication of the measure_voltage getter."""
    with expected_protocol(
            EurotestHPP120256,
            [("STATUS,MU", "UM, RANGE=3000V, VALUE=2.458kV")],
    ) as inst:
        assert inst.voltage == 2.458


def test_current():
    """Verify the communication of the measure_current getter."""
    with expected_protocol(
            EurotestHPP120256,
            [("STATUS,MI", "IM, RANGE=5000mA, VALUE=1739mA")],
    ) as inst:
        assert inst.current == 1739.0
