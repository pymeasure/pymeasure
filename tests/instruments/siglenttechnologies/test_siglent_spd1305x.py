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
from pymeasure.instruments.siglenttechnologies.siglent_spd1305x import SPD1305X


def test_set_current():
    with expected_protocol(
        SPD1305X,
        [("CH1:CURR 0.5", None),
         ("CH1:CURR?", "0.5")]
    ) as inst:
        inst.ch_1.current_limit = 0.5
        assert inst.ch_1.current_limit == 0.5


def test_set_current_trunc():
    with expected_protocol(
        SPD1305X,
        [("CH1:CURR 5", None),
         ("CH1:CURR?", "5")]
    ) as inst:
        inst.ch_1.current_limit = 10  # too large, gets truncated
        assert inst.ch_1.current_limit == 5


def test_set_voltage():
    with expected_protocol(
        SPD1305X,
        [("CH1:VOLT 0.5", None),
         ("CH1:VOLT?", "0.5")]
    ) as inst:
        inst.ch_1.voltage_setpoint = 0.5
        assert inst.ch_1.voltage_setpoint == 0.5


def test_set_voltage_trunc():
    with expected_protocol(
        SPD1305X,
        [("CH1:VOLT 30", None),
         ("CH1:VOLT?", "30")]
    ) as inst:
        inst.ch_1.voltage_setpoint = 35  # too large, gets truncated
        assert inst.ch_1.voltage_setpoint == 30


def test_configure_timer():
    with expected_protocol(
        SPD1305X,
        [("TIME:SET CH1,1,5.001,5.000,30", None)]
    ) as inst:
        inst.ch_1.configure_timer(1, 5.001, 8.55, 30)
