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
#
# DISCONNECT ALL DUTS FROM THE 4200 BEFORE STARTING THIS TEST
#
# Test using LAN port:
# $ pytest test_keithley4200_with_device.py --device-address "TCPIP::192.168.1.20::1225::SOCKET"

import pytest
from pymeasure.instruments.keithley import Keithley4200
from pymeasure.instruments.keithley.keithley4200 import StatusCode


###########
# FIXTURE #
###########


@pytest.fixture(scope="module")
def keithley4200(connected_device_address):
    instr = Keithley4200(connected_device_address)
    instr.clear()
    return instr


class TestKeithley4200:
    """Tests for Keithley4200 class."""

    def test_id(self, keithley4200):
        assert "KI4200" in keithley4200.id

    def test_status(self, keithley4200):
        assert type(keithley4200.status) is StatusCode

    def test_options(self, keithley4200):
        options = keithley4200.options
        assert type(options) is list
        for element in options:
            assert type(element) is str


class TestKeithley4200SMU:
    """Tests for Keithley4200 SMU class."""

    @pytest.mark.parametrize("voltage", [1, 20.65, -3.27, 43.1, 1.2e1, -99.7, 0])
    def test_voltage(self, keithley4200, voltage):
        keithley4200.clear()
        assert keithley4200.status == StatusCode.NONE
        keithley4200.smu1.voltage_setpoint = (0, voltage, 1e-3)  # range, value, compliance
        assert keithley4200.status == StatusCode.NONE
        got = keithley4200.smu1.voltage
        assert keithley4200.status == StatusCode.DATA_READY
        assert got == pytest.approx(voltage, rel=1e-3, abs=1e-4)

        # The voltage setting has to be applied again after a measurement if we change the
        # measured quantity.
        keithley4200.smu1.voltage_setpoint = (0, voltage, 1e-3)  # range, value, compliance
        got = keithley4200.smu1.current
        assert keithley4200.status == StatusCode.DATA_READY

        # With open terminals we should always get ~0A as current measurement result.
        assert abs(got) == pytest.approx(0, rel=1e-3, abs=1e-4)
        keithley4200.clear()

    @pytest.mark.parametrize("current", [1e-3, -0.0256, 1.467e-2, 1.243e-6])
    def test_current(self, keithley4200, current):
        compliance = 1
        keithley4200.clear()
        assert keithley4200.status == StatusCode.NONE
        keithley4200.smu1.current_setpoint = (0, current, compliance)  # range, value, compliance
        assert keithley4200.status == StatusCode.NONE
        got = keithley4200.smu1.current
        assert keithley4200.status == StatusCode.DATA_READY
        # With open terminals we should always get ~0A.
        assert got == pytest.approx(0, abs=1e-6)

        # The current setting has to be applied again after a measurement if we change the
        # measured quantity.
        keithley4200.smu1.current_setpoint = (0, current, compliance)  # range, value, compliance
        got = keithley4200.smu1.voltage
        assert keithley4200.status == StatusCode.DATA_READY

        # With open terminals we should always get the compliance as voltage measurement result
        assert abs(got) == pytest.approx(compliance, rel=1e-3, abs=1e-4)
        keithley4200.clear()
