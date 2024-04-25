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
from pymeasure.instruments.keithley.keithley2281S import Keithley2281S

init_comm = [(":SYST:LFR?", "50")]  # communication during init
init_comm_us = [(":SYST:LFR?", "60")]  # communication during init


def test_init():
    with expected_protocol(
        Keithley2281S,
        init_comm
    ) as inst:
        assert inst._PLC_RANGE == [0.002, 12]


def test_init_us():
    with expected_protocol(
        Keithley2281S,
        init_comm_us
    ) as inst:
        assert inst._PLC_RANGE == [0.002, 15]


def test_function_modes():
    with expected_protocol(
        Keithley2281S,
        init_comm +
        [(":ENTR:FUNC?", "POWER"),
         (":ENTR:FUNC TEST", None),
         (":ENTR:FUNC SIMULATOR", None),
         ],
    ) as inst:
        assert inst.cm_function_mode == "POWER"
        inst.cm_function_mode = "TEST"
        inst.cm_function_mode = "SIMULATOR"


def test_ps_output():
    with expected_protocol(
        Keithley2281S,
        init_comm +
        [(":OUTP:STAT?", "OFF"),
         (":OUTP:STAT ON", None),
         ],
    ) as inst:
        assert inst.ps_output_enabled is False
        inst.ps_output_enabled = True


# Same for bs_output_enabled
def test_bt_output():
    with expected_protocol(
        Keithley2281S,
        init_comm +
        [(":BATT:OUTP?", "OFF"),
         (":BATT:OUTP ON", None),
         ],
    ) as inst:
        assert inst.bt_output_enabled is False
        inst.bt_output_enabled = True
