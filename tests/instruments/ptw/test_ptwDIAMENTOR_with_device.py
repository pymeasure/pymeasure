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

# Tested using serial port. call signature:
# $ pytest test_ptwDIAMENTOR_with_device.py --device-address ASRL4
#


import pytest
from pymeasure.instruments.ptw.ptwDIAMENTOR import ptwDIAMENTOR
from time import sleep

BAUD_RATES = [9600, 19200, 38400, 57600, 115200]
DAP_UNITS = ["cGycm2", "Gycm2", "uGym2", "Rcm2"]


@pytest.fixture(scope="module")
def diamentor(connected_device_address, baud_rate=9600):
    instr = ptwDIAMENTOR(connected_device_address, baud_rate=baud_rate)
    return instr


class TestPTWDiamentorMethods:
    """Tests for PTW DIAMENTOR dosemeter methods."""

    def test_execute_selftest(self, diamentor):
        diamentor.execute_selftest()

    def test_reset(self, diamentor):
        diamentor.reset()


class TestPTWDiamentorProperties:
    """Tests for PTW DIAMENTOR dosemeter properties."""

    def test_baudrate(self, diamentor):
        assert diamentor.baudrate in BAUD_RATES

    def test_constancy_check_passed(self, diamentor):
        assert type(diamentor.constancy_check_passed) is bool

    def test_is_calibrated(self, diamentor):
        assert type(diamentor.is_calibrated) is bool

    def test_is_eeprom_ok(self, diamentor):
        assert type(diamentor.is_eeprom_ok) is bool

    @pytest.mark.parametrize("pressure", [500, 1500, 1013])
    def test_pressure(self, diamentor, pressure):
        initial_pressure = diamentor.pressure  # get the current setting
        diamentor.pressure = pressure
        assert pressure == diamentor.pressure
        diamentor.pressure = initial_pressure  # restore the initial setting

    def test_id(self, diamentor):
        assert "CRS" in diamentor.id

    def test_measurement(self, diamentor):
        diamentor.reset()
        sleep(2)
        measurement = diamentor.measurement
        assert type(measurement["dap"]) is float
        assert type(measurement["dap_rate"]) is float
        assert type(measurement["time"]) is int

    def test_serial_number(self, diamentor):
        serial_number = diamentor.serial_number
        assert type(serial_number) is int
        assert serial_number in range(1000000)

    @pytest.mark.parametrize("temperature", [0, 70, 20])
    def test_temperature(self, diamentor, temperature):
        initial_temperature = diamentor.temperature  # get the current setting
        diamentor.temperature = temperature
        assert temperature == diamentor.temperature
        diamentor.temperature = initial_temperature  # restore the initial setting

    @pytest.mark.parametrize("dap_unit", DAP_UNITS)
    def test_dap_unit(self, diamentor, dap_unit):
        initial_dap_unit = diamentor.dap_unit  # get the current setting
        diamentor.dap_unit = dap_unit
        assert dap_unit == diamentor.dap_unit
        diamentor.dap_unit = initial_dap_unit  # restore the initial setting

    def test_calibration_factor(self, diamentor):
        assert 1E8 <= diamentor.calibration_factor <= 9.999E12

    def test_correction_factor(self, diamentor):
        assert 0 <= diamentor.correction_factor <= 9.999
