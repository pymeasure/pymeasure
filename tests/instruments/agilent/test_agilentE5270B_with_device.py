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

# Call signature:
# $ pytest test_agilentE5270B_with_device.py --device-address "GPIB0::17::INSTR"

# The test uses slot 1 as test SMU
# Disconnect all loads from E5270B SMUs before test.

import pytest
from pymeasure.instruments.agilent.agilentE5270B import AgilentE5270B


############
# FIXTURES #
############

@pytest.fixture(scope="module")
def e5270b(connected_device_address,
           timeout=2000,
           ):
    instr = AgilentE5270B(connected_device_address)
    instr.reset()
    return instr


class TestMain:
    def test_clear(self, e5270b):
        with pytest.raises(NotImplementedError):
            e5270b.clear()

    @pytest.mark.parametrize("error_code, error_message",
                             [(100, "Undefined GPIB command."),
                              (121, "Channel number must be 1 to 2, or 1 to 8."),
                              (200, "Channel output switch must be ON."),
                              (620, "TGP specified incorrect I/O port."),
                              ])
    def test_get_error_message(self, e5270b, error_code, error_message):
        got = e5270b.get_error_message(error_code)
        assert error_message == got

    def test_check_errors(self, e5270b):
        assert [] == e5270b.check_errors()
        e5270b.write("unknown_command")
        assert [100] == e5270b.check_errors()
        assert [] == e5270b.check_errors()

    def test_options(self, e5270b):
        # with pytest.raises(NotImplementedError):
        options = e5270b.options
        assert type(options) is list
        assert 8 == len(options)
        assert "E52" in ",".join(options)


class TestSMU:
    def test_voltage(self, e5270b):
        e5270b.smu1.enabled = True
        e5270b.smu1.voltage_setpoint = (0, 1, 0.01)
        assert e5270b.smu1.voltage == pytest.approx(1, rel=1e-3)
        # expect ~0 A with open terminal
        assert abs(e5270b.smu1.current) < 10e-6
        e5270b.smu1.enabled = False

    def test_current(self, e5270b):
        e5270b.smu1.enabled = True
        e5270b.smu1.current_setpoint = (0, 0.001, 0.2)
        # expect ~0 A with open terminal
        assert e5270b.smu1.current == pytest.approx(0, abs=1e-3)
        # expect 0.2V  (voltage compliance)
        assert e5270b.smu1.voltage == pytest.approx(0.2, rel=1e-3)
        e5270b.smu1.enabled = False


class TestDisplay:
    @pytest.mark.parametrize("enabled", [True, False])
    def test_enabled(self, e5270b, enabled):
        assert [] == e5270b.check_errors()
        e5270b.display.enabled = enabled
        assert [] == e5270b.check_errors()
