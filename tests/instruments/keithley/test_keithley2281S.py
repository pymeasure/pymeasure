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

import pandas as pd

from pymeasure.test import expected_protocol
from pymeasure.instruments.keithley.keithley2281S import Keithley2281S, _PLC_RANGE

init_comm = [(":SYST:LFR?", "50")]  # communication during init for 50Hz line
init_comm_us = [(":SYST:LFR?", "60")]  # communication during init for 60Hz line
no_reading_comm = [(":STAT:MEAS:INST:ISUM:COND?", "0")]  # no reading available


def test_init():
    with expected_protocol(Keithley2281S, init_comm) as _:
        assert _PLC_RANGE == [0.002, 12]


def test_init_us():
    with expected_protocol(Keithley2281S, init_comm_us) as _:
        assert _PLC_RANGE == [0.002, 15]


def test_function_modes():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":ENTR:FUNC?", "POWER"),
            (":ENTR:FUNC TEST", None),
            (":ENTR:FUNC SIMULATOR", None),
        ],
    ) as inst:
        assert inst.function_mode == "POWER"
        inst.function_mode = "TEST"
        inst.function_mode = "SIMULATOR"


def test_ps_output():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":OUTP:STAT?", "0"),
            (":OUTP:STAT 1", None),
        ],
    ) as inst:
        assert inst.ps.output_enabled is False
        inst.ps.output_enabled = True


# Same for bs_output_enabled
def test_bt_output():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":BATT:OUTP?", "0"),
            (":BATT:OUTP 1", None),
        ],
    ) as inst:
        assert inst.bt.output_enabled is False
        inst.bt.output_enabled = True


def test_reading_availability():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":STAT:MEAS:INST:ISUM:COND?", "64"),
            (":STAT:MEAS:INST:ISUM:COND?", "0"),
        ],
    ) as inst:
        assert inst.reading_available is True
        assert inst.reading_available is False


def test_measurement_ongoging():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":STAT:OPER:INST:ISUM:COND?", "16"),
            (":STAT:OPER:INST:ISUM:COND?", "0"),
        ],
    ) as inst:
        assert inst.measurement_ongoing is True
        assert inst.measurement_ongoing is False


def test_ps_buffer():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":ENTR:FUNC POWER", None),
            (":ENTR:FUNC?", "POWER"),
        ]
        + no_reading_comm,
    ) as inst:
        inst.function_mode = "POWER"
        assert inst.buffer_data.equals(pd.DataFrame({"current": [], "voltage": [], "time": []}))


def test_bt_buffer():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":ENTR:FUNC TEST", None),
            (":ENTR:FUNC?", "TEST"),
        ]
        + no_reading_comm,
    ) as inst:
        inst.function_mode = "TEST"
        assert inst.buffer_data.equals(
            pd.DataFrame(
                {"current": [], "voltage": [], "capacity": [], "resistance": [], "time": []}
            )
        )


def test_bs_buffer():
    with expected_protocol(
        Keithley2281S,
        init_comm
        + [
            (":ENTR:FUNC SIMULATOR", None),
            (":ENTR:FUNC?", "SIMULATOR"),
        ]
        + no_reading_comm,
    ) as inst:
        inst.function_mode = "SIMULATOR"
        assert inst.buffer_data.equals(
            pd.DataFrame({"current": [], "voltage": [], "soc": [], "resistance": [], "time": []})
        )
