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

import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.keysight.keysightE3631A import KeysightE3631A


def test_voltage_setpoint():
    """Verify the voltage setpoint setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 1;:VOLT 1.5", None),
         ("INST:NSEL 1;:VOLT?", "1.5")],
    ) as inst:
        inst.ch_1.voltage_setpoint = 1.5
        assert inst.ch_1.voltage_setpoint == 1.5


def test_current_limit():
    """Verify the current limit setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [("INST:NSEL 3;:CURR 0.5", None),
         ("INST:NSEL 3;:CURR?", "0.5")],
    ) as inst:
        inst.ch_3.current_limit = 0.5
        assert inst.ch_3.current_limit == 0.5


def test_current_limit_validator():
    """Verify the current limit validator."""
    with expected_protocol(
        KeysightE3631A,
        [],
    ) as inst:
        with pytest.raises(ValueError, match="not in range"):
            inst.ch_1.current_limit = 7


def test_output_enabled():
    """Verify the output enable setter and getter."""
    with expected_protocol(
        KeysightE3631A,
        [("OUTPut 1", None),
         ("OUTPut?", "0")],
    ) as inst:
        inst.output_enabled = True
        assert inst.output_enabled is False
