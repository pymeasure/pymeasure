#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
import logging
from pymeasure.instruments.easttester import ET3510
# from pymeasure.generator import Generator

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


@pytest.fixture(scope="module", autouse=True)
def et3510(connected_device_address):
    # generator = Generator()
    # instr = generator.instantiate(ET3510, connected_device_address, 'easttester',
    #                               timeout=5000, adapter_kwargs={'baud_rate': 115200})
    instr = ET3510(connected_device_address, timeout=5000, baud_rate=115200)
    instr.clear()
    instr.trigger_source = ET3510.TriggerSource.BUS
    yield instr
    # generator.write_file("et3510_protocol_tests.py")


def test_correct_model_by_idn(et3510):
    assert "ET3510" in et3510.id

#
# AMPLitude subsystem
#


@pytest.mark.parametrize("enabled", [True, False])
def test_automatic_level_control(et3510, enabled):
    et3510.voltage = 1  # ALC not supported with voltages greater than 1V
    et3510.automatic_level_control = enabled
    assert et3510.automatic_level_control == enabled

#
# APERture subsystem
#


@pytest.mark.parametrize("speed", [
    ET3510.MeasurementSpeed.SLOW,
    ET3510.MeasurementSpeed.FAST,
    ET3510.MeasurementSpeed.MEDIUM,
])
def test_measurement_speed(et3510, speed):
    et3510.measurement_speed = speed
    assert et3510.measurement_speed == speed

#
# BIAS subsystem
#


@pytest.mark.parametrize("source", [
    ET3510.BiasSource.EXTERNAL,
    ET3510.BiasSource.INTERNAL,
])
def test_bias_source(et3510, source):
    et3510.bias_source = source
    assert et3510.bias_source == source


@pytest.mark.parametrize("voltage", [-2, 2, 1.5, -1, 0])
def test_bias_voltage(et3510, voltage):
    et3510.bias_voltage = voltage
    assert et3510.bias_voltage == voltage

#
# FETCh subsystem
#


def test_impedance(et3510):
    assert len(et3510.impedance) == 2


def test_monitor_voltage_ac(et3510):
    assert et3510.monitor_voltage_ac > 0


def test_monitor_current_ac(et3510):
    assert et3510.monitor_current_ac > 0


def test_monitor_voltage_dc_bias(et3510):
    volt = et3510.monitor_voltage_dc_bias
    assert volt

#
# FREQuency subsystem
#


@pytest.mark.parametrize("frequency", [10, 100, 203.25, 1000000, 5000])
def test_frequency(et3510, frequency):
    et3510.frequency = frequency
    assert et3510.frequency == frequency

#
# FUNCtion subsystem
#


@pytest.mark.parametrize("mtype", [e for e in ET3510.MeasurementType])
def test_measurement_type(et3510, mtype):
    et3510.measurement_type = mtype
    assert et3510.measurement_type == mtype


@pytest.mark.parametrize("state", [True, False])
def test_measurement_auto_range(et3510, state):
    et3510.measurement_auto_range = state
    assert et3510.measurement_auto_range == state


@pytest.mark.parametrize("rnge", [e for e in ET3510.MeasurementRange])
def test_measurement_range(et3510, rnge):
    et3510.measurement_range = rnge
    assert et3510.measurement_range == rnge

#
# SYSTem subsystem
#


@pytest.mark.parametrize("enabled", [False, True])
def test_beeper_enabled(et3510, enabled):
    et3510.beeper_enabled = enabled
    assert et3510.beeper_enabled == enabled


@pytest.mark.parametrize("locked", [True, False])
def test_keypad_lock(et3510, locked):
    et3510.keypad_lock = locked
    assert et3510.keypad_lock == locked


def test_beep(et3510):
    et3510.beep()

#
# TRIGger subsystem
#


@pytest.mark.parametrize("source", [
    ET3510.TriggerSource.INTERNAL,
    ET3510.TriggerSource.EXTERNAL,
    ET3510.TriggerSource.MANUAL,
    ET3510.TriggerSource.BUS,
])
def test_trigger_source(et3510, source):
    et3510.trigger_source = source
    assert et3510.trigger_source == source


@pytest.mark.parametrize("delay", [1, 5, 10, 0])
def test_trigger_delay(et3510, delay):
    et3510.trigger_delay = delay
    assert et3510.trigger_delay == delay


def test_trigger(et3510):
    et3510.trigger()

#
# VOLTage subsystem
#


@pytest.mark.parametrize("voltage", [10e-03, 100e-03, 1, 2])
def test_voltage(et3510, voltage):
    et3510.voltage = voltage
    assert et3510.voltage == voltage
