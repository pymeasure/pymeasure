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

from pymeasure.errors import Error
from pymeasure.instruments.keithley.keithley2400 import Keithley2400


@pytest.fixture(scope="module")
def keithley2400(connected_device_address):
    instr = Keithley2400(connected_device_address)
    instr.clear()
    instr.reset()
    yield instr
    if e := instr.check_errors():
        raise Error(e)
    instr.clear()
    instr.reset()


def test_reset(keithley2400):
    # Comments reference table numbers of default parameters from the Keithley2400 manual

    # 18-4
    assert keithley2400.source_enabled is False
    assert keithley2400.output_off_state == "normal"

    # 18-5
    assert keithley2400.front_terminals_enabled is True

    # 18-6
    assert keithley2400.current_range == 1.05e-4
    assert keithley2400.current_range_auto_enabled is True
    assert keithley2400.current_nplc == 1
    assert keithley2400.compliance_current == 1.05e-4

    assert keithley2400.voltage_range == 21
    assert keithley2400.voltage_range_auto_enabled is True
    assert keithley2400.voltage_nplc == 1
    assert keithley2400.compliance_voltage == 21

    assert keithley2400.resistance_mode_auto_enabled is True
    assert keithley2400.resistance_range == 2.1e5
    assert keithley2400.resistance_range_auto_enabled is True
    assert keithley2400.resistance_nplc == 1

    assert keithley2400.repeat_filter_enabled is True
    assert keithley2400.filter_count == 10
    assert keithley2400.filter_enabled is False

    # 18-7
    assert keithley2400.auto_output_off_enabled is False
    assert keithley2400.source_mode == "voltage"
    assert keithley2400.source_delay == 0.001  # Different to manual
    assert keithley2400.source_delay_auto_enabled is True

    assert keithley2400.source_current_range == 1.05e-4
    assert keithley2400.source_current_range_auto_enabled is True
    assert keithley2400.source_current == 0

    assert keithley2400.source_voltage_range == 21
    assert keithley2400.source_voltage_range_auto_enabled is True
    assert keithley2400.source_voltage == 0

    # 18-9
    assert keithley2400.auto_zero_enabled is True


def test_current_source(keithley2400):
    source_current = 10e-3

    keithley2400.source_mode = "current"
    keithley2400.source_current = source_current
    keithley2400.source_enabled = True

    measurements = keithley2400.measure_all()
    current = measurements["current"]
    voltage = measurements["voltage"]
    resistance = measurements["resistance"]

    assert keithley2400.source_mode == "current"
    assert keithley2400.source_current == source_current
    assert keithley2400.source_enabled is True

    assert voltage == pytest.approx(current * resistance)


def test_voltage_source(keithley2400):
    source_voltage = 1

    keithley2400.source_mode = "voltage"
    keithley2400.source_voltage = source_voltage
    keithley2400.source_enabled = True

    measurements = keithley2400.measure_all()
    current = measurements["current"]
    voltage = measurements["voltage"]
    resistance = measurements["resistance"]

    assert keithley2400.source_mode == "voltage"
    assert keithley2400.source_voltage == source_voltage
    assert keithley2400.source_enabled is True

    assert voltage == pytest.approx(current * resistance)


@pytest.mark.parametrize(
    "attr, value",
    [
        ("source_enabled", True),
        ("source_enabled", False),
        ("source_mode", "voltage"),
        ("source_mode", "current"),
        ("source_delay", 0.1),
        ("source_delay_auto_enabled", True),
        ("source_delay_auto_enabled", False),
        ("auto_zero_enabled", True),
        ("auto_zero_enabled", True),
        ("output_off_state", "disconnected"),
        ("output_off_state", "normal"),
        ("output_off_state", "zero"),
        ("output_off_state", "guard"),
        ("auto_output_off_enabled", True),
        ("auto_output_off_enabled", False),
        ("filter_enabled", True),
        ("filter_enabled", False),
        ("repeat_filter_enabled", True),
        ("repeat_filter_enabled", False),
        ("filter_count", 10),
        ("current_range", 0.000105),
        ("current_range_auto_enabled", True),
        ("current_range_auto_enabled", False),
        ("current_nplc", 1.0),
        ("compliance_current", 0.01),
        ("source_current", 0.002),
        ("source_current_range", 0.0105),
        ("source_current_range_auto_enabled", True),
        ("source_current_range_auto_enabled", False),
        # ("voltage_range", 21),  # Invalid with source readback on, needs configuration after reset
        ("voltage_range_auto_enabled", True),
        ("voltage_range_auto_enabled", False),
        ("voltage_nplc", 1.0),
        ("compliance_voltage", 1.0),
        ("source_voltage", 1.5),
        ("source_voltage_range", 2.1),
        ("source_voltage_range_auto_enabled", True),
        ("source_voltage_range_auto_enabled", False),
        ("resistance_mode_auto_enabled", True),
        ("resistance_mode_auto_enabled", False),
        ("resistance_range", 2100.0),
        ("resistance_range_auto_enabled", True),
        ("resistance_range_auto_enabled", False),
        ("resistance_nplc", 1.0),
        ("trigger_delay", 0.5),
        ("arm_timer", 1.0),
        ("trigger_source", "immediate"),
        ("trigger_source", "trigger_link"),
        ("arm_source", "immediate"),
        ("arm_source", "trigger_link"),
        ("arm_source", "timer"),
        ("arm_source", "manual"),
        ("arm_source", "bus"),
        ("trigger_output_event", "source"),
        ("trigger_output_event", "delay"),
        ("trigger_output_event", "sense"),
        ("trigger_output_event", "none"),
        ("arm_output_event", "trigger_enter"),
        ("arm_output_event", "trigger_exit"),
        ("arm_output_event", "none"),
        ("trigger_input_line", 2),
        ("arm_input_line", 3),
        ("trigger_output_line", 4),
        ("arm_output_line", 1),
        ("display_enabled", True),
        ("display_enabled", False),
        ("four_wire_enabled", True),
        ("four_wire_enabled", False),
        ("line_frequency", 60),
        ("line_frequency_auto_enabled", True),
        ("line_frequency_auto_enabled", False),
        ("front_terminals_enabled", True),
        ("front_terminals_enabled", False),
    ],
)
def test_setters_and_getters(keithley2400, attr, value):
    keithley2400.reset()
    setattr(keithley2400, attr, value)
    assert getattr(keithley2400, attr) == value
    if e := keithley2400.check_errors():
        raise Error(e)
