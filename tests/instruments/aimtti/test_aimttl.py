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
from pymeasure.instruments.aimtti.aimttiPL import PLBase, PL303MQTP, PL303MQDP, PL601P


def test_voltage_setpoint():
    with expected_protocol(
        PLBase,
        [("V2V 1.2", None),
         ("V2?", "V2 1.2")
         ],
    ) as inst:
        inst.ch2.voltage_setpoint = 1.2
        assert inst.ch2.voltage_setpoint == 1.2


def test_voltage():
    with expected_protocol(
        PLBase,
        [("V2O?", "1.2V")
         ],
    ) as inst:
        assert inst.ch2.voltage == 1.2


def test_current_limit():
    with expected_protocol(
        PLBase,
        [("I2 0.1", None),
         ("I2?", "I2 0.1")
         ],
    ) as inst:
        inst.ch2.current_limit = 0.1
        assert inst.ch2.current_limit == 0.1


def test_current():
    with expected_protocol(
        PLBase,
        [("I2O?", "0.123A")
         ],
    ) as inst:
        assert inst.ch2.current == 0.123


def test_current_range():
    with expected_protocol(
        PLBase,
        [("IRANGE2 2", None),
         ("IRANGE2?", "2"),
         ("IRANGE2 1", None),
         ("IRANGE2?", "1")
         ],
    ) as inst:
        inst.ch2.current_range = "HIGH"
        assert inst.ch2.current_range == "HIGH"
        inst.ch2.current_range = "LOW"
        assert inst.ch2.current_range == "LOW"


def test_enable():
    with expected_protocol(
        PLBase,
        [("OP2 1", None),
         ("OP2 0", None),
         ("OPALL 1", None),
         ("OPALL 0", None)
         ],
    ) as inst:
        inst.ch2.enable()
        inst.ch2.disable()
        inst.enable()
        inst.disable()


def test_triple():
    with expected_protocol(
        PL303MQTP,
        [("V3O?", "1.2V")],
    ) as inst:
        assert inst.ch3.voltage == 1.2


def test_voltage_range():
    with expected_protocol(
        PL601P,
        [("V1V 60", None),
         ("V1?", "V1 60")
         ],
    ) as inst:
        inst.ch1.voltage_setpoint = 60
        assert inst.ch1.voltage_setpoint == 60


def test_strict_range_error():
    with expected_protocol(
        PL303MQDP,
        [],
    ) as inst:
        with pytest.raises(ValueError):
            inst.ch1.voltage_setpoint = 31

