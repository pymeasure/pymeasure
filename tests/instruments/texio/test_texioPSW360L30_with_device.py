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
import time

import pytest
from pymeasure.instruments.texio.texioPSW360L30 import TexioPSW360L30


pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestTexioPSW360L30:
    """
    Unit tests for TEXIO PSW-360L30 class.

    This test suite, needs the following setup to work properly:
        - A TEXIO PSW-360L30 device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
    """

    ##################################################
    # TEXIO PSW-360L30 device address goes here:
    RESOURCE = "TCPIP::192.168.10.119::2268::SOCKET"
    ##################################################

    INSTR = TexioPSW360L30(RESOURCE)

    #########################
    # PARAMETRIZATION CASES #
    #########################

    CURRENT_LIMIT = [0.1, 0.5, 1]
    VOLTAGE_SETPOINT = [1, 2, 3, 4, 5]

    @pytest.fixture
    def instr(self):
        self.INSTR.reset()
        return self.INSTR

    @pytest.mark.parametrize("case", CURRENT_LIMIT)
    def test_current_limit_no_output(self, instr, case):
        instr.current_limit = case
        assert instr.current_limit == case

    @pytest.mark.parametrize("case", VOLTAGE_SETPOINT)
    def test_voltage_setpoint_no_output(self, instr, case):
        instr.voltage_setpoint = case
        assert instr.voltage_setpoint == case

    @pytest.mark.parametrize("voltage_setpoint", VOLTAGE_SETPOINT)
    @pytest.mark.parametrize("current_limit", CURRENT_LIMIT)
    def test_everything_without_apply(self, instr, voltage_setpoint, current_limit):
        instr.current_limit = current_limit
        instr.voltage_setpoint = voltage_setpoint
        instr.output_enabled = True
        time.sleep(1)
        assert instr.output_enabled is True
        assert instr.voltage_setpoint == voltage_setpoint
        assert instr.current_limit == current_limit
        assert instr.voltage == pytest.approx(voltage_setpoint, abs=0.1)
        assert instr.current == pytest.approx(0, abs=0.1)
        assert instr.power == pytest.approx(0, abs=0.1)
        instr.output_enabled = False
        assert instr.output_enabled is False

    @pytest.mark.parametrize("voltage_setpoint", VOLTAGE_SETPOINT)
    @pytest.mark.parametrize("current_limit", CURRENT_LIMIT)
    def test_everything_with_apply(self, instr, voltage_setpoint, current_limit):
        instr.applied = (voltage_setpoint, current_limit)
        instr.output_enabled = True
        time.sleep(1)
        assert instr.output_enabled is True
        assert instr.voltage_setpoint == voltage_setpoint
        assert instr.current_limit == current_limit
        assert instr.voltage == pytest.approx(voltage_setpoint, abs=0.1)
        assert instr.current == pytest.approx(0, abs=0.1)
        assert instr.power == pytest.approx(0, abs=0.1)
        instr.output_enabled = False
        assert instr.output_enabled is False
