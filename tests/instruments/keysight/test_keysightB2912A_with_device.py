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

# Tested using ethernet. call signature:
#    pytest test_keysightB2912A_with_device.py --device-address 'TCPIP::192.168.2.232::INSTR'

import pytest
from pymeasure.instruments.keysight.keysightB2912A import KeysightB2912A
# from pyvisa.errors import VisaIOError

# pytest.skip("Only work with connected hardware", allow_module_level=True)


@pytest.fixture(scope="module")
def keysightB2912A(connected_device_address):
    instr = KeysightB2912A(connected_device_address)
    instr.clear()
    # ensure the device is in a defined state, e.g. by resetting it.
    yield instr
    instr.ch1.source_output_enabled = False  # pyright:ignore
    instr.ch2.source_output_enabled = False  # pyright:ignore


def test_source_output_enabled(keysightB2912A):
    keysightB2912A.ch1.source_output_enabled = True
    assert keysightB2912A.ch1.source_output_enabled
    keysightB2912A.ch2.source_output_enabled = True
    assert keysightB2912A.ch2.source_output_enabled


def test_source_output_mode(keysightB2912A):
    keysightB2912A.ch1.source_output_mode = "CURR"
    assert keysightB2912A.ch1.source_output_mode == "CURR"
    keysightB2912A.ch2.source_output_mode = "CURR"
    assert keysightB2912A.ch2.source_output_mode == "CURR"


def test_source_output_shape(keysightB2912A):
    keysightB2912A.ch1.source_output_shape = "DC"
    assert keysightB2912A.ch1.source_output_shape == "DC"
    keysightB2912A.ch2.source_output_shape = "PULS"
    assert keysightB2912A.ch2.source_output_shape == "PULS"


def test_source_current(keysightB2912A):
    keysightB2912A.ch1.source_current = 1e-3
    assert keysightB2912A.ch1.source_current == 1e-3
    keysightB2912A.ch2.source_current = 1e-3
    assert keysightB2912A.ch2.source_current == 1e-3


def test_triggered_source_current(keysightB2912A):
    keysightB2912A.ch1.triggered_source_current = 2e-3
    assert keysightB2912A.ch1.triggered_source_current == 2e-3
    keysightB2912A.ch2.triggered_source_current = 3e-3
    assert keysightB2912A.ch2.triggered_source_current == 3e-3


def test_source_voltage(keysightB2912A):
    keysightB2912A.ch1.source_voltage = 123e-3
    assert keysightB2912A.ch1.source_voltage == 123e-3
    keysightB2912A.ch2.source_voltage = 123e-3
    assert keysightB2912A.ch2.source_voltage == 123e-3


def test_triggered_source_voltage(keysightB2912A):
    keysightB2912A.ch1.triggered_source_voltage = 1.11
    assert keysightB2912A.ch1.triggered_source_voltage == 1.11
    keysightB2912A.ch2.triggered_source_voltage = 2.34
    assert keysightB2912A.ch2.triggered_source_voltage == 2.34


def test_pulse_delay(keysightB2912A):
    keysightB2912A.ch1.pulse_delay = 1
    assert keysightB2912A.ch1.pulse_delay == 1
    keysightB2912A.ch2.pulse_delay = 1e-3
    assert keysightB2912A.ch2.pulse_delay == 1e-3


def test_pulse_width(keysightB2912A):
    keysightB2912A.ch1.pulse_width = 1
    assert keysightB2912A.ch1.pulse_width == 1
    keysightB2912A.ch2.pulse_width = 1e-3
    assert keysightB2912A.ch2.pulse_width == 1e-3


# def test_measurement_mode(keysightB2912A):
#     keysightB2912A.ch1.measurement_mode = "CURR"
#     assert keysightB2912A.ch1.measurement_mode == "CURR"
#     keysightB2912A.ch2.measurement_mode = "CURR"
#     assert keysightB2912A.ch2.measurement_mode == "CURR"


def test_current_measurement_range_auto(keysightB2912A):
    keysightB2912A.ch1.current_measurement_range_auto = False
    assert not keysightB2912A.ch1.current_measurement_range_auto
    keysightB2912A.ch2.current_measurement_range_auto = False
    assert not keysightB2912A.ch2.current_measurement_range_auto


def test_current_measurement_range(keysightB2912A):
    keysightB2912A.current_measurement_range_auto = False
    keysightB2912A.ch1.current_measurement_range = 0.1
    assert keysightB2912A.ch1.current_measurement_range == 0.1
    keysightB2912A.ch2.current_measurement_range = 0.1
    assert keysightB2912A.ch2.current_measurement_range == 0.1


def test_current_measurement_speed(keysightB2912A):
    keysightB2912A.ch1.current_measurement_speed = 1e-4
    assert keysightB2912A.ch1.current_measurement_speed == 1e-4
    keysightB2912A.ch2.current_measurement_speed = 1e-4
    assert keysightB2912A.ch2.current_measurement_speed == 1e-4


def test_measured_current(keysightB2912A):
    c = keysightB2912A.ch1.measured_current
    assert isinstance(c, float)
    c = keysightB2912A.ch2.measured_current
    assert isinstance(c, float)


def test_measured_current_array(keysightB2912A):
    keysightB2912A.ch1.measured_current_array
    keysightB2912A.ch2.measured_current_array
    assert keysightB2912A.ask(":form?").strip() == "ASC"


def test_voltage_measurement_range_auto(keysightB2912A):
    keysightB2912A.ch1.voltage_measurement_range_auto = False
    assert not keysightB2912A.ch1.voltage_measurement_range_auto
    keysightB2912A.ch2.voltage_measurement_range_auto = False
    assert not keysightB2912A.ch2.voltage_measurement_range_auto


def test_voltage_measurement_range(keysightB2912A):
    keysightB2912A.ch1.voltage_measurement_range_auto = False
    keysightB2912A.ch1.voltage_measurement_range = 0.2
    assert keysightB2912A.ch1.voltage_measurement_range == 0.2
    keysightB2912A.ch2.voltage_measurement_range_auto = False
    keysightB2912A.ch2.voltage_measurement_range = 0.2
    assert keysightB2912A.ch2.voltage_measurement_range == 0.2


def test_voltage_measurement_speed(keysightB2912A):
    keysightB2912A.ch1.voltage_measurement_speed = 1e-4
    assert keysightB2912A.ch1.voltage_measurement_speed == 1e-4
    keysightB2912A.ch2.voltage_measurement_speed = 1e-4
    assert keysightB2912A.ch2.voltage_measurement_speed == 1e-4


def test_measured_voltage(keysightB2912A):
    v = keysightB2912A.ch1.measured_voltage
    assert isinstance(v, float)
    v = keysightB2912A.ch2.measured_voltage
    assert isinstance(v, float)


def test_measured_voltage_array(keysightB2912A):
    keysightB2912A.ch1.measured_voltage_array
    keysightB2912A.ch2.measured_voltage_array
    assert keysightB2912A.ask(":form?").strip() == "ASC"


def test_output_protection_enabled(keysightB2912A):
    keysightB2912A.ch1.output_protection_enabled = True
    assert keysightB2912A.ch1.output_protection_enabled
    keysightB2912A.ch2.output_protection_enabled = True
    assert keysightB2912A.ch2.output_protection_enabled
    keysightB2912A.ch1.output_protection_enabled = False
    assert not keysightB2912A.ch1.output_protection_enabled
    keysightB2912A.ch2.output_protection_enabled = False
    assert not keysightB2912A.ch2.output_protection_enabled


def test_compliance(keysightB2912A):
    keysightB2912A.ch1.compliance_voltage = 4
    assert keysightB2912A.ch1.compliance_voltage == 4
    keysightB2912A.ch1.compliance_current = 1e-6
    assert keysightB2912A.ch1.compliance_current == 1e-6
    keysightB2912A.ch2.compliance_voltage = 4
    assert keysightB2912A.ch2.compliance_voltage == 4
    keysightB2912A.ch2.compliance_current = 1e-6
    assert keysightB2912A.ch2.compliance_current == 1e-6


def test_reset(keysightB2912A):
    keysightB2912A.reset()


def test_trig_src(keysightB2912A):
    for ch in keysightB2912A.ch1, keysightB2912A.ch2:
        ch.trigger_source = "TIM"
        assert len(keysightB2912A.check_errors()) == 0  # TODO is this correct?


def test_trig_del(keysightB2912A):
    for ch in keysightB2912A.ch1, keysightB2912A.ch2:
        ch.source_trigger_delay = 1
        assert len(keysightB2912A.check_errors()) == 0  # TODO is this correct?
        ch.measurement_trigger_delay = 1
        assert len(keysightB2912A.check_errors()) == 0  # TODO is this correct?


def test_trig_count(keysightB2912A):
    for ch in keysightB2912A.ch1, keysightB2912A.ch2:
        ch.trigger_timer_count = 1
        assert len(keysightB2912A.check_errors()) == 0  # TODO is this correct?


def test_trig_period(keysightB2912A):
    for ch in keysightB2912A.ch1, keysightB2912A.ch2:
        ch.trigger_timer_period = 1
        assert len(keysightB2912A.check_errors()) == 0  # TODO is this correct?


def test_wait_for_complete(keysightB2912A):
    for ch in keysightB2912A.ch1, keysightB2912A.ch2:
        ch.trigger_source = "TIM"
        ch.source_trigger_delay = 0
        ch.measurement_trigger_delay = 0
        ch.trigger_timer_period = 1
        ch.trigger_timer_count = 10
        keysightB2912A.wait_for_complete(10)
        ch.initiate()
        keysightB2912A.wait_for_complete(11)
        assert len(keysightB2912A.check_errors()) == 0  # TODO is this correct?
