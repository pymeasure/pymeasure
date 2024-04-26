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
from pymeasure.instruments.proterial.rod4 import ROD4


def test_mfc_range():
    with expected_protocol(
        ROD4,
        [("\x0201SFK400", "OK"),
         ("\x0202RFK", "200")],
    ) as inst:
        inst.ch_1.mfc_range = 400
        assert inst.ch_2.mfc_range == 200


def test_valve_mode():
    with expected_protocol(
        ROD4,
        [("\x0203SVM0", "OK"),
         ("\x0204RVM", "1")],
    ) as inst:
        inst.ch_3.valve_mode = 'flow'
        assert inst.ch_4.valve_mode == 'close'


def test_setpoint():
    with expected_protocol(
        ROD4,
        [("\x0201SFD33.3", "OK"),
         ("\x0202RFD", "50.4")],
    ) as inst:
        inst.ch_1.setpoint = 33.3
        assert inst.ch_2.setpoint == 50.4


def test_actual_flow():
    with expected_protocol(
        ROD4,
        [("\x0203RFX", "40.1")],
    ) as inst:
        assert inst.ch_3.actual_flow == 40.1
