#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.instruments.agilent.agilent4156 import Agilent4156


def test_init():
    with expected_protocol(Agilent4156, []):
        pass  # verify init


def test_smu_channel_mode():
    with expected_protocol(
        Agilent4156, [(":PAGE:CHAN:SMU1:MODE?", "V"), ("SYST:ERR?", '0,"No error"')]
    ) as inst:
        assert inst.smu1.channel_mode == "V"


def test_smu_channel_mode_setter():
    with expected_protocol(
        Agilent4156, [(":PAGE:CHAN:SMU1:MODE V", None), ("SYST:ERR?", '0,"No error"')]
    ) as inst:
        inst.smu1.channel_mode = "V"


def test_smu_channel_function():
    with expected_protocol(
        Agilent4156, [(":PAGE:CHAN:SMU1:FUNC?", "VAR1"), ("SYST:ERR?", '0,"No error"')]
    ) as inst:
        assert inst.smu1.channel_function == "VAR1"


def test_smu_channel_function_setter():
    with expected_protocol(
        Agilent4156,
        [(":PAGE:CHAN:SMU1:FUNC VAR1", None), ("SYST:ERR?", '0,"No error"')],
    ) as inst:
        inst.smu1.channel_function = "VAR1"


def test_smu_sres():
    with expected_protocol(
        Agilent4156,
        [(":PAGE:CHAN:SMU1:SRES?", "10KOHM"), ("SYST:ERR?", '0,"No error"')],
    ) as inst:
        assert inst.smu1.series_resistance == "10KOHM"


def test_smu_sres_setter():
    with expected_protocol(
        Agilent4156,
        [(":PAGE:CHAN:SMU1:SRES 10KOHM", None), ("SYST:ERR?", '0,"No error"')],
    ) as inst:
        inst.smu1.series_resistance = "10KOHM"


@pytest.mark.parametrize("channel", ("smu1", "smu2", "vmu1", "vsu2"))
def test_voltage_name(channel):
    with expected_protocol(
        Agilent4156, [(f"PAGE:CHAN:{channel.upper()}:VNAME?", "value")]
    ) as inst:
        ch = getattr(inst, channel)
        assert ch.voltage_name == "value"


@pytest.mark.parametrize("channel", ("smu1", "smu2", "vmu1", "vsu2"))
def test_voltage_name_setter(channel):
    with expected_protocol(
        Agilent4156, [(f":PAGE:CHAN:{channel.upper()}:VNAME 'value'", None)]
    ) as inst:
        ch = getattr(inst, channel)
        ch.voltage_name = "value"


@pytest.mark.parametrize("channel", ("smu1", "smu2"))
def test_current_name(channel):
    with expected_protocol(
        Agilent4156, [(f"PAGE:CHAN:{channel.upper()}:INAME?", "value")]
    ) as inst:
        ch = getattr(inst, channel)
        assert ch.current_name == "value"


@pytest.mark.parametrize("channel", ("smu1", "smu2"))
def test_current_name_setter(channel):
    with expected_protocol(
        Agilent4156, [(f":PAGE:CHAN:{channel.upper()}:INAME 'value'", None)]
    ) as inst:
        ch = getattr(inst, channel)
        ch.current_name = "value"


def test_vmu_disable():
    with expected_protocol(
        Agilent4156, [(":PAGE:CHAN:VMU1:DIS", None), ("SYST:ERR?", '0,"No error"')]
    ) as inst:
        assert inst.vmu1.disable is None
