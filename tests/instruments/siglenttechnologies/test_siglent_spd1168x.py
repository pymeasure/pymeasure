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
from pymeasure.instruments.siglenttechnologies.siglent_spd1168x import SPD1168X


def test_set_4W_mode():
    with expected_protocol(
        SPD1168X,
        [("MODE:SET 4W", None)]
    ) as inst:
        inst.set_4W_mode = True


def test_set_current():
    with expected_protocol(
        SPD1168X,
        [("CH1:CURR 0.5", None),
         ("CH1:CURR?", "0.5")]
    ) as inst:
        inst.ch[1].set_current = 0.5
        assert inst.ch[1].set_current == 0.5


def test_set_current_trunc():
    with expected_protocol(
        SPD1168X,
        [("CH1:CURR 8", None),
         ("CH1:CURR?", "0.5")]
    ) as inst:
        inst.ch[1].set_current = 10  # too large, gets truncated
        assert inst.ch[1].set_current == 0.5


def test_enable_output():
    with expected_protocol(
        SPD1168X,
        [("INST CH1", None),
         ("OUTP CH1,ON", None),
         ("INST CH1", None),
         ("OUTP CH1,OFF", None)]
    ) as inst:
        inst.ch[1].enable()
        inst.ch[1].disable()
