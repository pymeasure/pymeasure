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
from pymeasure.instruments.siglenttechnologies.siglent_spd1168x import SPD1168X


def test_enable_4W_mode():
    with expected_protocol(
        SPD1168X,
        [("MODE:SET 4W", None),
         ("MODE:SET 2W", None)]
    ) as inst:
        inst.enable_4W_mode(True)
        inst.enable_4W_mode(False)


def test_save_config():
    with expected_protocol(
        SPD1168X,
        [("*SAV 1", None),
         ("*SAV 5", None)]
    ) as inst:
        inst.save_config(1)
        inst.save_config(5)


def test_recall_config():
    with expected_protocol(
        SPD1168X,
        [("*RCL 1", None),
         ("*RCL 5", None)]
    ) as inst:
        inst.recall_config(1)
        inst.recall_config(5)


def test_set_current():
    with expected_protocol(
        SPD1168X,
        [("CH1:CURR 0.5", None),
         ("CH1:CURR?", "0.5")]
    ) as inst:
        inst.ch_1.current_limit = 0.5
        assert inst.ch_1.current_limit == 0.5


def test_set_current_trunc():
    with expected_protocol(
        SPD1168X,
        [("CH1:CURR 8", None),
         ("CH1:CURR?", "8")]
    ) as inst:
        inst.ch_1.current_limit = 10  # too large, gets truncated
        assert inst.ch_1.current_limit == 8


def test_enable_output():
    with expected_protocol(
        SPD1168X,
        [("INST CH1", None),
         ("OUTP CH1,ON", None),
         ("INST CH1", None),
         ("OUTP CH1,OFF", None)]
    ) as inst:
        inst.ch_1.enable_output()
        inst.ch_1.enable_output(False)


def test_enable_timer():
    with expected_protocol(
        SPD1168X,
        [("TIME CH1,ON", None),
         ("TIME CH1,OFF", None)]
    ) as inst:
        inst.ch_1.enable_timer()
        inst.ch_1.enable_timer(False)


def test_configure_timer():
    with expected_protocol(
        SPD1168X,
        [("TIME:SET CH1,1,5.001,8.000,30", None)]
    ) as inst:
        inst.ch_1.configure_timer(1, 5.001, 8.55, 30)
