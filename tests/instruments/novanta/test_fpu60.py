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

from pymeasure.instruments.novanta import Fpu60


def test_disable_emission():
    with expected_protocol(Fpu60,
                           [("LASER=OFF", ""), ("LASER=ON", "")],
                           ) as inst:
        inst.disable_emission()


@pytest.mark.parametrize("string, value", (("ENABLED", True), ("DISABLED", False)))
def test_emission_enabled(string, value):
    with expected_protocol(Fpu60,
                           [("STATUS?", string)],
                           ) as inst:
        assert inst.emission_enabled is value


def test_power():
    with expected_protocol(Fpu60,
                           [("POWER?", " 12.345W")],
                           ) as inst:
        assert inst.power == 12.345


def test_power_setpoint():
    with expected_protocol(Fpu60,
                           [("POWER=12.345", ""), ("SETPOWER?", " 12.345W")],
                           ) as inst:
        inst.power_setpoint = 12.345
        assert inst.power_setpoint == 12.345


def test_shutter_open():
    with expected_protocol(Fpu60,
                           [("SHUTTER OPEN", ""), ("SHUTTER?", "SHUTTER OPEN")],
                           ) as inst:
        inst.shutter_open = True
        assert inst.shutter_open is True


def test_shutter_close():
    with expected_protocol(Fpu60,
                           [("SHUTTER CLOSE", ""), ("SHUTTER?", "SHUTTER CLOSED")],
                           ) as inst:
        inst.shutter_open = False
        assert inst.shutter_open is False


def test_shutter_close_read():
    with expected_protocol(Fpu60,
                           [("SHUTTER?", "SHUTTER CLOSED")],
                           ) as inst:
        assert inst.shutter_open is False


@pytest.mark.parametrize("string, value", (("ENABLED", True), ("DISABLED", False)))
def test_interlock(string, value):
    with expected_protocol(Fpu60,
                           [("INTERLOCK?", string)],
                           ) as inst:
        assert inst.interlock_enabled is value


def test_head_temperature():
    with expected_protocol(Fpu60,
                           [("HTEMP?", " 12.345C")],
                           ) as inst:
        assert inst.head_temperature == 12.345


def test_psu_temperature():
    with expected_protocol(Fpu60,
                           [("PSUTEMP?", " 12.345C")],
                           ) as inst:
        assert inst.psu_temperature == 12.345


def test_get_operation_times():
    with expected_protocol(
            Fpu60,
            [("TIMERS?", "PSU Time = 00594820 Mins"),
             (None, "Laser Enabled Time   =  00196700 Mins"),
             (None, "Laser Threshold Time =  00196500 Mins"),
             (None, "")],
    ) as inst:
        assert inst.get_operation_times() == {'psu': 594820,
                                              'laser': 196700,
                                              'laser_above_1A': 196500}


def test_current():
    with expected_protocol(Fpu60,
                           [("CURRENT?", " 12.3%")],
                           ) as inst:
        assert inst.current == 12.3


def test_serial_number():
    with expected_protocol(Fpu60,
                           [("SERIAL?", "1234567")],
                           ) as inst:
        assert inst.serial_number == "1234567"
