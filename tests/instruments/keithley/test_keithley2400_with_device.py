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
from pymeasure.instruments.keithley import Keithley2400


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
    assert keithley2400.terminals == "front"

    # 18-6
    assert keithley2400.current_range == 1.05e-4
    assert keithley2400.current_range_auto is True
    assert keithley2400.current_nplc == 1
    assert keithley2400.compliance_current == 1.05e-4

    assert keithley2400.voltage_range == 21
    assert keithley2400.voltage_range_auto is True
    assert keithley2400.voltage_nplc == 1
    assert keithley2400.compliance_voltage == 21

    assert keithley2400.resistance_mode_auto is True
    assert keithley2400.resistance_range == 2.1e5
    assert keithley2400.resistance_range_auto is True
    assert keithley2400.resistance_nplc == 1

    assert keithley2400.filter_type == "repeat"
    assert keithley2400.filter_count == 10
    assert keithley2400.filter_enabled is False

    # 18-7
    assert keithley2400.auto_output_off is False
    assert keithley2400.source_mode == "voltage"
    assert keithley2400.source_delay == 0.001  # Different to manual
    assert keithley2400.source_delay_auto is True

    assert keithley2400.source_current_range == 1.05e-4
    assert keithley2400.source_current_range_auto is True
    assert keithley2400.source_current == 0

    assert keithley2400.source_voltage_range == 21
    assert keithley2400.source_voltage_range_auto is True
    assert keithley2400.source_voltage == 0

    # 18-9
    assert keithley2400.auto_zero is True

    # 18-11
    # TODO: Trigger


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
