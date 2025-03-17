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
from pymeasure.instruments.keysight.keysightB2900 import KeysightB2900

def test_output_enabled():
    with expected_protocol(
        KeysightB2900,
        [
            ("OUTPut1 1", None),
            ("OUTPut1?", "1"),
        ],
    ) as inst:
        inst.output_enabled = True
        assert inst.output_enabled == True

def test_output_enabled_write_invalid():
    with expected_protocol(KeysightB2900, []) as inst:
        with pytest.raises(ValueError):
            inst.output_enabled = 2

def test_output_mode():
    with expected_protocol(
        KeysightB2900,
        [
            (":SOURce1:FUNCtion:MODE CURR", None),
            (":SOURce1:FUNCtion:MODE?", "CURR"),
        ],
    ) as inst:
        inst.output_mode = "CURR"
        assert inst.output_mode == "CURR"

def test_voltage_limit():
    with expected_protocol(
        KeysightB2900,
        [
            (":SENSe1:VOLTage:DC:PROTection:LEVel 5", None),
            (":SENSe1:VOLTage:DC:PROTection:LEVel?", 5),
        ],
    ) as inst:
        inst.voltage_limit = 5
        assert inst.voltage_limit == 5

def test_voltage_limit_invalid():
    with expected_protocol(KeysightB2900, []) as inst:
        with pytest.raises(ValueError):
            inst.voltage_limit = 15

def test_current_limit():
    with expected_protocol(
        KeysightB2900,
        [
            (":SENSe1:CURRent:DC:PROTection:LEVel 0.5", None),
            (":SENSe1:CURRent:DC:PROTection:LEVel?", 0.5),
        ],
    ) as inst:
        inst.current_limit = 0.5
        assert inst.current_limit == 0.5

def test_voltage_setpoint():
    with expected_protocol(
        KeysightB2900,
        [
            (":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude 5", None),
            (":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?", 5),
        ],
    ) as inst:
        inst.voltage_setpoint = 5
        assert inst.voltage_setpoint == 5

def test_current_setpoint():
    with expected_protocol(
        KeysightB2900,
        [
            (":SOURce1:CURRent:LEVel:IMMediate:AMPLitude 0.5", None),
            (":SOURce1:CURRent:LEVel:IMMediate:AMPLitude?", 0.5),
        ],
    ) as inst:
        inst.current_setpoint = 0.5
        assert inst.current_setpoint == 0.5

def test_voltage_measure():
    with expected_protocol(
        KeysightB2900,
        [
            (":MEASure:VOLTage:DC? (@1)", 2.5),
        ],
    ) as inst:
        assert inst.voltage_measure == 2.5

def test_current_measure():
    with expected_protocol(
        KeysightB2900,
        [
            (":MEASure:CURRent:DC? (@1)", 0.25),
        ],
    ) as inst:
        assert inst.current_measure == 0.25

def test_output_filter_state():
    with expected_protocol(
        KeysightB2900,
        [
            (":OUTPut1:FILTer:LPASs:STATe 1", None),
            (":OUTPut1:FILTer:LPASs:STATe?", 1),
        ],
    ) as inst:
        inst.output_filter_state = True
        assert inst.output_filter_state == True

def test_output_filter_auto():
    with expected_protocol(
        KeysightB2900,
        [
            (":OUTPut1:FILTer:LPASs:AUTO 1", None),
            (":OUTPut1:FILTer:LPASs:AUTO?", 1),
        ],
    ) as inst:
        inst.output_filter_auto = True
        assert inst.output_filter_auto == True


def test_output_filter_frequency():
    with expected_protocol(
        KeysightB2900,
        [
            (":OUTPut:FILTer:LPASs:FREQuency 15000", None),
            (":OUTPut:FILTer:LPASs:FREQuency?", 15000),
        ],
    ) as inst:
        inst.output_filter_frequency = 15000
        assert inst.output_filter_frequency == 15000

def test_output_filter_time_constant():
    with expected_protocol(
        KeysightB2900,
        [
            (":OUTPut1:FILTer:LPASs:TCONstant 0.0005", None),
            (":OUTPut1:FILTer:LPASs:TCONstant?", 0.0005),
        ],
    ) as inst:
        inst.output_filter_time_constant = 0.0005
        assert inst.output_filter_time_constant == 0.0005

def test_sense_remote():
    with expected_protocol(
        KeysightB2900,
        [
            (":SENSe1:REMote 1", None),
            (":SENSe1:REMote?", 1),
        ],
    ) as inst:
        inst.sense_remote = True
        assert inst.sense_remote == True

def test_output_isolation():
    with expected_protocol(
        KeysightB2900,
        [
            (":OUTPut1:LOW FLO", None),
            (":OUTPut1:LOW?", "FLO"),
        ],
    ) as inst:
        inst.output_isolation = "FLO"
        assert inst.output_isolation == "FLO"
