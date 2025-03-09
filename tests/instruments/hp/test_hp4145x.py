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
from pymeasure.instruments.hp import HP4145x

import numpy as np
import pandas as pd


@pytest.mark.parametrize("integ_time, value", [("SHORT", 1), ("MEDIUM", 2), ("LONG", 3)])
def test_integration_time(integ_time, value):
    with expected_protocol(
            HP4145x,
            [
                ("IT%d" % (value), None)
            ],
    ) as instr:
        instr.integration_time = integ_time


@pytest.mark.parametrize("value", [True, False])
def test_auto_calibrate(value):
    with expected_protocol(
            HP4145x,
            [
                ("CA%d" % value, None)
            ],
    ) as instr:
        instr.auto_calibrate = value


@pytest.mark.parametrize("channel_function, channel_function_id",
                         [("VAR1", 1), ("VAR2", 2), ("CONST", 3), ("VARD", 4)])
@pytest.mark.parametrize("channel_mode, channel_mode_id", [("V", 1), ("I", 2), ("COM", 3)])
@pytest.mark.parametrize("channel", range(1, 5))
def test_channel_mode_and_channel_function(channel, channel_mode, channel_mode_id, channel_function,
                                           channel_function_id):
    with expected_protocol(
            HP4145x,
            [
                ("DE CH %d, '%s', '%s', %d, %d" %
                 (channel, "VBE", f"I{channel}", 3, 3), None),
                ("DE CH %d, '%s', '%s', %d, %d" %
                 (channel, "VBE", "IB", 3, 3), None),
                ("DE CH %d, '%s', '%s', %d, %d" %
                 (channel, "VBE", "IB", 3, channel_function_id), None),
                ("DE CH %d, '%s', '%s', %d, %d" %
                 (channel, "VBE", "IB", channel_mode_id, channel_function_id), None)
            ],
    ) as instr:
        getattr(instr, f"smu{channel}").voltage_name = "VBE"
        getattr(instr, f"smu{channel}").current_name = "IB"
        getattr(instr, f"smu{channel}").channel_function = channel_function
        getattr(instr, f"smu{channel}").channel_mode = channel_mode


@pytest.mark.parametrize("source_function, source_function_id",
                         [("VAR1", 1), ("VAR2", 2), ("CONST", 3), ("VARD", 4)])
@pytest.mark.parametrize("channel", range(1, 3))
def test_channel_function_vs(channel, source_function, source_function_id):
    with expected_protocol(
            HP4145x,
            [
                ("DE VS %d, '%s', %d" % (channel, "VBE", 3), None),
                ("DE VS %d, '%s', %d" % (channel, "VBE", source_function_id), None),
            ],
    ) as instr:
        getattr(instr, f"vsu{channel}").voltage_name = "VBE"
        getattr(instr, f"vsu{channel}").channel_function = source_function


@pytest.mark.parametrize("channel", range(1, 3))
def test_channel_function_vm(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE VM %d, '%s'" % (channel, "VBE"), None)
            ],
    ) as instr:
        getattr(instr, f"vmu{channel}").voltage_name = "VBE"


@pytest.mark.parametrize("channel", range(1, 5))
def test_smu_disabled(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE CH %d" % (channel), None)
            ],
    ) as instr:
        getattr(instr, f"smu{channel}").disable()


@pytest.mark.parametrize("channel", range(1, 3))
def test_vm_disabled(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE VM %d" % (channel), None)
            ],
    ) as instr:
        getattr(instr, f"vmu{channel}").disable()


@pytest.mark.parametrize("channel", range(1, 3))
def test_vs_disabled(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE VS %d" % (channel), None)
            ],
    ) as instr:
        getattr(instr, f"vsu{channel}").disable()


def test_get_data():
    with expected_protocol(
            HP4145x,
            [
                ("DO 'IC'", "N 54.00,N 55.00")
            ],
    ) as instr:
        assert instr.get_data('IC').equals(pd.DataFrame(data=np.array([54.00, 55.00]), index=None))
