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

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.aimtti.aimttiPL import PL303QMTP, PL303QMDP


def test_voltage_setpoint():
    with expected_protocol(
        PL303QMTP,
        [("V2V 1.2", None),
         ("V2?", "V2 1.2")
         ],
    ) as inst:
        inst.ch_2.voltage_setpoint = 1.2
        assert inst.ch_2.voltage_setpoint == 1.2


def test_voltage():
    with expected_protocol(
        PL303QMTP,
        [("V2O?", "1.2V")
         ],
    ) as inst:
        assert inst.ch_2.voltage == 1.2


def test_current_limit():
    with expected_protocol(
        PL303QMTP,
        [("I2 0.1", None),
         ("I2?", "I2 0.1")
         ],
    ) as inst:
        inst.ch_2.current_limit = 0.1
        assert inst.ch_2.current_limit == 0.1


def test_current():
    with expected_protocol(
        PL303QMTP,
        [("I2O?", "0.123A")
         ],
    ) as inst:
        assert inst.ch_2.current == 0.123


def test_current_range():
    with expected_protocol(
        PL303QMTP,
        [("IRANGE2 2", None),
         ("IRANGE2?", "2"),
         ("IRANGE2 1", None),
         ("IRANGE2?", "1")
         ],
    ) as inst:
        inst.ch_2.current_range = "HIGH"
        assert inst.ch_2.current_range == "HIGH"
        inst.ch_2.current_range = "LOW"
        assert inst.ch_2.current_range == "LOW"


def test_enable():
    with expected_protocol(
        PL303QMTP,
        [("OP2 1", None),
         ("OP2?", "1"),
         ("OP2 0", None),
         ("OPALL 1", None),
         ("OPALL 0", None)
         ],
    ) as inst:
        inst.ch_2.output_enabled = True
        assert inst.ch_2.output_enabled is True
        inst.ch_2.output_enabled = False
        inst.all_outputs_enabled = True
        inst.all_outputs_enabled = False


def test_triple():
    with expected_protocol(
        PL303QMTP,
        [("V3O?", "1.2V")],
    ) as inst:
        assert inst.ch_3.voltage == 1.2


def test_strict_range_error():
    with expected_protocol(
        PL303QMDP,
        [],
    ) as inst:
        with pytest.raises(ValueError):
            inst.ch_1.voltage_setpoint = 31
