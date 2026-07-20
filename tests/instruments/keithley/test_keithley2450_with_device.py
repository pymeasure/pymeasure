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

from pymeasure.instruments.keithley import Keithley2450

BOOLEANS = [True, False]


@pytest.fixture(scope="module")
def keithley2450(connected_device_address):
    instr = Keithley2450(connected_device_address)
    return instr


@pytest.fixture(autouse=True)
def reset(keithley2450):
    keithley2450.reset()  # ensure the device is in a defined state before each test


def test_id(keithley2450):
    assert (
        "KEITHLEY INSTRUMENTS,MODEL 2400" in keithley2450.id
        or "KEITHLEY INSTRUMENTS,MODEL 2450" in keithley2450.id
    )  # support SCPI 2400 mode as well


@pytest.mark.parametrize("source_mode", ["voltage", "current"])
def test_source_mode(keithley2450, source_mode):
    keithley2450.source_mode = source_mode
    assert keithley2450.source_mode == source_mode


@pytest.mark.parametrize("current_range", [10e-9, 1.0])
def test_current_range(keithley2450, current_range):
    keithley2450.current_range = current_range
    assert keithley2450.current_range == current_range


@pytest.mark.parametrize("nplc", [0.01, 10])
def test_current_nplc(keithley2450, nplc):
    keithley2450.current_nplc = nplc
    assert keithley2450.current_nplc == nplc


@pytest.mark.parametrize("compliance_current", [1.05, 10e-9])
def test_compliance_current(keithley2450, compliance_current):
    keithley2450.compliance_current = compliance_current
    assert keithley2450.compliance_current == compliance_current


@pytest.mark.parametrize("source_current", [-1.05, -0.5, 0, 0.5, 1.05])
def test_source_current(keithley2450, source_current):
    keithley2450.source_current = source_current
    assert keithley2450.source_current == source_current


@pytest.mark.parametrize("source_current_range", [10e-9, 1.0])
def test_source_current_range(keithley2450, source_current_range):
    keithley2450.source_current_range = source_current_range
    assert keithley2450.source_current_range == source_current_range


@pytest.mark.parametrize("delay", [0, 0.5, 1000])
def test_source_current_delay(keithley2450, delay):
    keithley2450.source_current_delay = delay
    assert keithley2450.source_current_delay == delay


@pytest.mark.parametrize("auto_delay", BOOLEANS)
def test_source_current_delay_auto(keithley2450, auto_delay):
    keithley2450.source_current_delay_auto = auto_delay
    assert keithley2450.source_current_delay_auto == auto_delay


@pytest.mark.parametrize("voltage_range", [20e-3, 200])
def test_voltage_range(keithley2450, voltage_range):
    keithley2450.apply_current()  # switch to current source mode
    keithley2450.voltage_range = voltage_range
    assert keithley2450.voltage_range == voltage_range


@pytest.mark.parametrize("nplc", [0.01, 10])
def test_voltage_nplc(keithley2450, nplc):
    keithley2450.voltage_nplc = nplc
    assert keithley2450.voltage_nplc == nplc


@pytest.mark.parametrize("compliance_voltage", [20e-3, 210])
def test_compliance_voltage(keithley2450, compliance_voltage):
    keithley2450.compliance_voltage = compliance_voltage
    assert keithley2450.compliance_voltage == compliance_voltage


@pytest.mark.parametrize("source_voltage", [-210, 0, 210])
def test_source_voltage(keithley2450, source_voltage):
    keithley2450.source_voltage = source_voltage
    assert keithley2450.source_voltage == source_voltage


@pytest.mark.parametrize("source_voltage_range", [20e-3, 200])
def test_source_voltage_range(keithley2450, source_voltage_range):
    keithley2450.source_voltage_range = source_voltage_range
    assert keithley2450.source_voltage_range == source_voltage_range


@pytest.mark.parametrize("delay", [0, 1000])
def test_source_voltage_delay(keithley2450, delay):
    keithley2450.source_voltage_delay = delay
    assert keithley2450.source_voltage_delay == delay


@pytest.mark.parametrize("auto_delay", BOOLEANS)
def test_source_voltage_delay_auto(keithley2450, auto_delay):
    keithley2450.source_voltage_delay_auto = auto_delay
    assert keithley2450.source_voltage_delay_auto == auto_delay


@pytest.mark.parametrize("resistance_range", [2, 200e6])
def test_resistance_range(keithley2450, resistance_range):
    keithley2450.resistance_range = resistance_range
    assert keithley2450.resistance_range == resistance_range


@pytest.mark.parametrize("nplc", [0.01, 10])
def test_resistance_nplc(keithley2450, nplc):
    keithley2450.resistance_nplc = nplc
    assert keithley2450.resistance_nplc == nplc


@pytest.mark.parametrize("wires", [2, 4])
def test_wires(keithley2450, wires):
    keithley2450.wires = wires
    assert keithley2450.wires == wires


@pytest.mark.parametrize("points", [10, 5211488])
def test_buffer_points(keithley2450, points):
    keithley2450.buffer_points = points
    assert keithley2450.buffer_points == points


@pytest.mark.parametrize("filter_type", ["REP", "MOV"])
def test_current_filter_type(keithley2450, filter_type):
    keithley2450.current_filter_type = filter_type
    assert keithley2450.current_filter_type == filter_type


@pytest.mark.parametrize("count", [1, 100])
def test_current_filter_count(keithley2450, count):
    keithley2450.current_filter_count = count
    assert keithley2450.current_filter_count == count


@pytest.mark.parametrize("state", ["ON", "OFF"])
def test_current_filter_state(keithley2450, state):
    responses = {"ON": 1.0, "OFF": 0.0}
    keithley2450.current_filter_state = state
    assert keithley2450.current_filter_state == responses[state]


@pytest.mark.parametrize("filter_type", ["REP", "MOV"])
def test_voltage_filter_type(keithley2450, filter_type):
    keithley2450.voltage_filter_type = filter_type
    assert keithley2450.voltage_filter_type == filter_type


@pytest.mark.parametrize("count", [1, 100])
def test_voltage_filter_count(keithley2450, count):
    keithley2450.voltage_filter_count = count
    assert keithley2450.voltage_filter_count == count


@pytest.mark.parametrize("off_state", ["HIMP", "NORM", "ZERO", "GUAR"])
def test_current_output_off_state(keithley2450, off_state):
    keithley2450.current_output_off_state = off_state
    assert keithley2450.current_output_off_state == off_state


@pytest.mark.parametrize("off_state", ["HIMP", "NORM", "ZERO", "GUAR"])
def test_voltage_output_off_state(keithley2450, off_state):
    keithley2450.voltage_output_off_state = off_state
    assert keithley2450.voltage_output_off_state == off_state


def test_apply_voltage(keithley2450):
    keithley2450.apply_voltage(voltage_range=20, compliance_current=0.01)
    assert keithley2450.source_mode == "voltage"
    assert keithley2450.source_voltage_range == 20
    assert keithley2450.compliance_current == 0.01


def test_apply_current(keithley2450):
    keithley2450.apply_current(current_range=0.001, compliance_voltage=5)
    assert keithley2450.source_mode == "current"
    assert keithley2450.source_current_range == 0.001
    assert keithley2450.compliance_voltage == 5


def test_enable_source(keithley2450):
    keithley2450.enable_source()
    assert keithley2450.source_enabled is True


def test_disable_source(keithley2450):
    keithley2450.disable_source()
    assert keithley2450.source_enabled is False


def test_measure_voltage(keithley2450):
    keithley2450.measure_voltage(nplc=1, auto_range=True)
    assert True


def test_measure_current(keithley2450):
    keithley2450.measure_current(nplc=1, auto_range=True)
    assert True


def test_measure_resistance(keithley2450):
    keithley2450.measure_resistance(nplc=1, auto_range=True)
    assert True


@pytest.mark.parametrize("state", ["ON", "OFF"])
def test_current_autozero(keithley2450, state):
    responses = {"ON": 1.0, "OFF": 0.0}
    keithley2450.current_autozero = state
    assert keithley2450.current_autozero == responses[state]


@pytest.mark.parametrize("autorange", BOOLEANS)
def test_current_autorange(keithley2450, autorange):
    keithley2450.current_autorange = autorange
    assert keithley2450.current_autorange == autorange


@pytest.mark.parametrize("count", [1, 300000])
def test_sense_count(keithley2450, count):
    keithley2450.sense_count = count
    assert keithley2450.sense_count == count


@pytest.mark.parametrize("state", ["ON", "OFF"])
def test_source_voltage_readback(keithley2450, state):
    responses = {"ON": 1.0, "OFF": 0.0}
    keithley2450.source_voltage_readback = state
    assert keithley2450.source_voltage_readback == responses[state]


@pytest.mark.parametrize("state", ["BLAC", "ON25", "ON75", "ON100", "ON50"])
def test_display_light_state(keithley2450, state):
    keithley2450.display_light_state = state
    assert keithley2450.display_light_state == state


def test_error_count(keithley2450):
    assert keithley2450.error_count == 0


def test_next_error(keithley2450):
    assert isinstance(keithley2450.next_error, list)


def test_trace_actual_end(keithley2450):
    assert isinstance(keithley2450.trace_actual_end, int)


def test_auto_range_source_current(keithley2450):
    keithley2450.source_mode = "current"
    keithley2450.auto_range_source()


def test_auto_range_source_voltage(keithley2450):
    keithley2450.source_mode = "voltage"
    keithley2450.auto_range_source()


def test_use_rear_terminals(keithley2450):
    keithley2450.use_rear_terminals()


def test_use_front_terminals(keithley2450):
    keithley2450.use_front_terminals()


def test_clear_status(keithley2450):
    keithley2450.clear_status()


def test_autozero_once(keithley2450):
    keithley2450.autozero_once()


def test_ramp_to_current(keithley2450):
    keithley2450.apply_current(current_range=0.01, compliance_voltage=5)
    keithley2450.enable_source()
    keithley2450.ramp_to_current(1e-3, steps=5)
    assert abs(keithley2450.source_current - 1e-3) < 1e-9


def test_ramp_to_voltage(keithley2450):
    keithley2450.apply_voltage(voltage_range=5, compliance_current=0.01)
    keithley2450.enable_source()
    keithley2450.ramp_to_voltage(1.0, steps=5)
    assert abs(keithley2450.source_voltage - 1.0) < 1e-6
