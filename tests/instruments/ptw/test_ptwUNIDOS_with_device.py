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

# Tested using SCPI over telnet (via ethernet). call signature:
# $ pytest test_ptwUNIDOS_with_device.py --device-address "TCPIP::172.23.19.1::8123::SOCKET"
# make sure the lock symbol on the display is closed so that write access is possible
#
# tested with a PTW UNIDOS Tango dosemeter


import pytest
from pymeasure.instruments.ptw.ptwUNIDOS import ptwUNIDOS
from time import sleep


RANGES = ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH']
LEVELS = ['LOW', 'MEDIUM', 'HIGH']

############
# FIXTURES #
############


@pytest.fixture(scope="module")
def unidos(connected_device_address):
    instr = ptwUNIDOS(connected_device_address)
    instr.write_enabled = 1
    return instr


class TestPTWUnidosProperties:
    """Tests for PTW UNIDOS dosemeter properties."""

    def test_write_enabled(self, unidos):
        assert unidos.write_enabled is True

    @pytest.mark.parametrize("level", LEVELS)
    def test_autostart_level(self, unidos, level):
        unidos.autostart_level = level
        sleep(1)
        assert unidos.autostart_level == level

    def test_id(self, unidos):
        name, type_nr, fw_ver, hw_rev = unidos.id
        assert 'UNIDOS' in name
        assert len(type_nr) == 7
        assert len(fw_ver) > 0
        assert len(hw_rev) == 3

    @pytest.mark.parametrize("time", [1, 10])
    def test_integration_time(self, unidos, time):
        unidos.integration_time = time
        assert unidos.integration_time == time

    def test_mac_address(self, unidos):
        assert len(unidos.mac_address) == 17

    def test_meas_result(self, unidos):
        result = unidos.meas_result
        assert type(result['status']) is str

    @pytest.mark.parametrize("range", RANGES)
    def test_range(self, unidos, range):
        unidos.range = range
        sleep(2)
        assert unidos.range == range

    def test_range_max(self, unidos):
        result = unidos.range_max
        assert result['range'] in RANGES
        assert type(result['current']) is float
        assert type(result['doserate']) is float
        assert type(result['timebase']) is str

    def test_range_res(self, unidos):
        res = unidos.range_res
        assert res['range'] in RANGES
        assert type(res['charge']) is float
        assert type(res['dose']) is float
        assert type(res['current']) is float
        assert type(res['doserate']) is float
        assert type(res['timebase']) is str

    def test_selftest_result(self, unidos):
        result = unidos.selftest_result
        assert type(result['status']) is str
        assert type(result['time_remaining']) is float
        assert type(result['time_total']) is float
        assert type(result['LOW']) is float
        assert type(result['MEDIUM']) is float
        assert type(result['HIGH']) is float

    def test_serial_number(self, unidos):
        assert type(unidos.serial_number) is int

    def test_status(self, unidos):
        assert unidos.status in ['RES', 'MEAS', 'HOLD', 'INT', 'INTHLD', 'ZERO',
                                 'AUTO', 'AUTO_MEAS', 'AUTO_HOLD', 'EOM', 'WAIT',
                                 'INIT', 'ERROR', 'SELF_TEST', 'TST']

    def test_tfi(self, unidos):
        assert type(unidos.tfi) is str

    @pytest.mark.parametrize("state", [True, False])
    def test_use_autostart(self, unidos, state):
        unidos.use_autostart = state
        assert unidos.use_autostart == state

    @pytest.mark.parametrize("state", [True, False])
    def test_use_autoreset(self, unidos, state):
        unidos.use_autoreset = state
        assert unidos.use_autoreset == state

    @pytest.mark.parametrize("state", [True, False])
    def test_use_electrical_units(self, unidos, state):
        unidos.use_electrical_units = state
        assert unidos.use_electrical_units == state

    @pytest.mark.parametrize("voltage", [0, -1, 1])
    def test_voltage(self, unidos, voltage):
        unidos.voltage = voltage
        assert unidos.voltage == voltage

    def test_zero_result(self, unidos):
        result = unidos.zero_result
        assert type(result['status']) is str
        assert type(result['time_remaining']) is float
        assert type(result['time_total']) is float


class TestPTWUnidosMethods:
    """Tests for PTW UNIDOS dosemeter methods."""

    def test_reset(self, unidos):
        unidos.reset()
        assert unidos.status == 'RES'

    def test_measure_hold(self, unidos):
        unidos.measure()
        sleep(5)
        assert unidos.status == 'MEAS'
        unidos.hold()
        sleep(1)
        assert unidos.status == 'HOLD'

    def test_clear(self, unidos):
        assert len(unidos.meas_history) > 0  # a measurement should exist from the test before
        unidos.clear()
        assert len(unidos.meas_history) == 0

    @pytest.mark.parametrize("time", [2, 10])
    def test_intervall(self, unidos, time):
        unidos.intervall(time)
        sleep(0.1 * time)
        assert unidos.status in ['INT']
        assert unidos.integration_time == time


class TestPTWUnidosJSON:
    '''Tests for the JSON configuration structure'''

    def test_read_detector(self, unidos):
        detectors = unidos.read_detector('all')
        assert type(detectors) is list
        assert type(detectors[0]) is dict

    def test_read_first_detector(self, unidos):
        guid = unidos.read_detector('all')[0]['guid']
        detector = unidos.read_detector(guid)
        assert type(detector) is dict

    def test_meas_history(self, unidos):
        history = unidos.meas_history
        assert type(history) is list
        if len(history):
            assert type(history[0]) is dict

    def test_meas_parameters(self, unidos):
        assert type(unidos.meas_parameters) is dict

    def test_system_settings(self, unidos):
        assert type(unidos.system_settings) is dict

    def test_system_info(self, unidos):
        assert type(unidos.system_info) is dict

    def test_wlan_config(self, unidos):
        assert type(unidos.wlan_config) is dict

    def test_lan_config(self, unidos):
        assert type(unidos.lan_config) is dict
