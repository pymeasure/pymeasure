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


@pytest.mark.parametrize("channel", range(1, 5))
def test_voltage_and_current_compliance(channel):
    with expected_protocol(
            HP4145x,
            [
                ("US", None),
                ("DV %s, 0, %f, %f" % (channel, 99.9, 10e-3), None)
            ],
    ) as instr:
        instr.mode = 'USER_MODE'
        getattr(instr, f"SMU{channel}").current_compliance = 10e-3
        getattr(instr, f"SMU{channel}").voltage = 99.9


@pytest.mark.parametrize("channel", range(1, 5))
def test_current_and_voltage_compliance(channel):
    with expected_protocol(
            HP4145x,
            [
                ("US", None),
                ("DI %s, 0, %f, %f" % (channel, 10e-3, 10), None)
            ],
    ) as instr:
        instr.mode = 'USER_MODE'
        getattr(instr, f"SMU{channel}").voltage_compliance = 10
        getattr(instr, f"SMU{channel}").current = 10e-3


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


@pytest.mark.parametrize("source_function, source_function_id", [("VAR1", 1), ("VAR2", 2), ("CONST", 3), ("VAR1'", 4)])
@pytest.mark.parametrize("source_mode, source_mode_id", [("V", 1), ("I", 2), ("COM", 3)])
@pytest.mark.parametrize("channel", range(1, 5))
def test_channel_mode_and_channel_function(channel, source_mode, source_mode_id, source_function, source_function_id):
    with expected_protocol(
            HP4145x,
            [
                ("DE CH %d, '%s', '%s', %d, %d" % (channel, "VBE", f"I{channel}", 3, 3), None),
                ("DE CH %d, '%s', '%s', %d, %d" % (channel, "VBE", "IB", 3, 3), None),
                ("DE CH %d, '%s', '%s', %d, %d" % (channel, "VBE", "IB", 3, source_function_id), None),
                ("DE CH %d, '%s', '%s', %d, %d" % (channel, "VBE", "IB", source_mode_id, source_function_id), None)
            ],
    ) as instr:
        getattr(instr, f"SMU{channel}").voltage_name = "VBE"
        getattr(instr, f"SMU{channel}").current_name = "IB"
        getattr(instr, f"SMU{channel}").channel_function = source_function
        getattr(instr, f"SMU{channel}").channel_mode = source_mode


@pytest.mark.parametrize("source_function, source_function_id", [("VAR1", 1), ("VAR2", 2), ("CONST", 3), ("VAR1'", 4)])
@pytest.mark.parametrize("channel", range(1, 3))
def test_channel_function_vs(channel, source_function, source_function_id):
    with expected_protocol(
            HP4145x,
            [
                ("DE VS %d, '%s', %d" % (channel, "VBE", 3), None),
                ("DE VS %d, '%s', %d" % (channel, "VBE", source_function_id), None),
            ],
    ) as instr:
        getattr(instr, f"VS{channel}").voltage_name = "VBE"
        getattr(instr, f"VS{channel}").channel_function = source_function


@pytest.mark.parametrize("channel", range(1, 3))
def test_channel_function_vm(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE VM %d, '%s'" % (channel, "VBE"), None)
            ],
    ) as instr:
        getattr(instr, f"VM{channel}").voltage_name = "VBE"


@pytest.mark.parametrize("channel", range(1, 5))
def test_smu_disabled(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE CH %d" % (channel), None)
            ],
    ) as instr:
        getattr(instr, f"SMU{channel}").disabled = True


@pytest.mark.parametrize("channel", range(1, 3))
def test_vm_disabled(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE VM %d" % (channel), None)
            ],
    ) as instr:
        getattr(instr, f"VM{channel}").disabled = True


@pytest.mark.parametrize("channel", range(1, 3))
def test_vs_disabled(channel):
    with expected_protocol(
            HP4145x,
            [
                ("DE VS %d" % (channel), None)
            ],
    ) as instr:
        getattr(instr, f"VS{channel}").disabled = True


def test_get_trace():
    with expected_protocol(
            HP4145x,
            [
                ("DO 'IC'", "N 54.00,N 55.00")
            ],
    ) as instr:
        assert instr.get_trace('IC') == [54.00, 55.00]
