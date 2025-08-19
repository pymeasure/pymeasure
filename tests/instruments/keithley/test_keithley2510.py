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

from pymeasure.test import expected_protocol
from pymeasure.instruments.keithley.keithley2510 import Keithley2510


def test_init():
    with expected_protocol(Keithley2510, []):
        pass  # Verifies initialization.


def test_enable_source():
    with expected_protocol(Keithley2510, [(b"OUTPUT ON", None)]) as inst:
        inst.enable_source()


def test_disable_source():
    with expected_protocol(Keithley2510, [(b"OUTPUT OFF", None)]) as inst:
        inst.disable_source()


def test_temperature_setpoint_setter():
    with expected_protocol(Keithley2510, [(b":SOURce:TEMPerature 50", None)]) as inst:
        inst.temperature_setpoint = 50


def test_temperature_measurement():
    with expected_protocol(Keithley2510, [(b":MEASure:TEMPerature?", b"23.4\n")]) as inst:
        assert inst.temperature == 23.4


def test_current_measurement():
    with expected_protocol(Keithley2510, [(b":MEASure:CURRent?", b"0.02\n")]) as inst:
        assert inst.current == 0.02


def test_voltage_measurement():
    with expected_protocol(Keithley2510, [(b":MEASure:VOLTage?", b"3.3\n")]) as inst:
        assert inst.voltage == 3.3


def test_temperature_protection_enable():
    with expected_protocol(
        Keithley2510, [(b":SOURce:TEMPerature:PROTection:STATe ON", None)]
    ) as inst:
        inst.enable_temperature_protection()


def test_temperature_protection_disable():
    with expected_protocol(
        Keithley2510, [(b":SOURce:TEMPerature:PROTection:STATe OFF", None)]
    ) as inst:
        inst.disable_temperature_protection()


def test_temperature_protection_range():
    with expected_protocol(
        Keithley2510,
        [
            (b":SOURce:TEMPerature:PROTection:LOW 5", None),
            (b":SOURce:TEMPerature:PROTection:HIGH 100", None),
            (b":SOURce:TEMPerature:PROTection:LOW?", b"5\n"),
            (b":SOURce:TEMPerature:PROTection:HIGH?", b"100\n"),
        ],
    ) as inst:
        inst.temperature_protection_range = (5, 100)
        assert inst.temperature_protection_range == (5, 100)


def test_temperature_pid():
    with expected_protocol(
        Keithley2510,
        [
            (b":SOURce:TEMPerature:LCONstants:GAIN 1", None),
            (b":SOURce:TEMPerature:LCONstants:INTegral 2", None),
            (b":SOURce:TEMPerature:LCONstants:DERivative 3", None),
            (b":SOURce:TEMPerature:LCONstants:GAIN?", 1),
            (b":SOURce:TEMPerature:LCONstants:INTegral?", 2),
            (b":SOURce:TEMPerature:LCONstants:DERivative?", 3),
        ],
    ) as inst:
        inst.temperature_pid = (1, 2, 3)
        assert inst.temperature_pid == (1, 2, 3)
