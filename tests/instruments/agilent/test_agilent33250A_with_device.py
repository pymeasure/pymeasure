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

# Call signature:
# python -m pytest tests/instruments/agilent/test_agilent33250A_with_device.py
#   --device-address "GPIB::10::INSTR"

import math

import pytest

from pymeasure.instruments.agilent import Agilent33250A


@pytest.fixture(scope="module")
def generator(connected_device_address):
    """Create a waveform generator instance for tests with real hardware."""
    return Agilent33250A(connected_device_address)


@pytest.fixture(autouse=True)
def force_output_off(generator):
    """Ensure output is off before and after each test."""
    generator.output_enabled = False
    yield
    try:
        generator.output_enabled = False
    except Exception:
        pass


def test_idn_contains_33250a(generator):
    """Panel should identify the instrument model as 33250A in the ID string."""
    assert "33250A" in generator.id.upper()


def test_front_panel_sine_1khz(generator):
    """Panel should show SIN, 1.000 kHz, 200 mVpp, and 0 V offset."""
    generator.reset()
    generator.clear()
    generator.output_enabled = False

    generator.shape = "SIN"
    generator.frequency = 1e3
    generator.amplitude_unit = "VPP"
    generator.amplitude = 0.2
    generator.offset = 0.0
    generator.output_load = 50
    generator.output_enabled = True

    assert generator.shape == "SIN"
    assert generator.frequency == pytest.approx(1e3, rel=1e-6, abs=1e-9)
    assert generator.amplitude_unit == "VPP"
    assert generator.amplitude == pytest.approx(0.2, rel=1e-3, abs=1e-6)
    assert generator.offset == pytest.approx(0.0, abs=1e-6)
    assert generator.output_enabled is True


def test_front_panel_square_duty(generator):
    """Panel should show SQU at 10.000 kHz with 200 mVpp and duty cycle 30%."""
    generator.reset()
    generator.clear()
    generator.output_enabled = False

    generator.shape = "SQU"
    generator.frequency = 10e3
    generator.amplitude_unit = "VPP"
    generator.amplitude = 0.2
    generator.offset = 0.0
    generator.square_dutycycle = 30.0
    generator.output_enabled = True

    assert generator.shape == "SQU"
    assert generator.frequency == pytest.approx(10e3, rel=1e-6, abs=1e-6)
    assert generator.amplitude == pytest.approx(0.2, rel=1e-3, abs=1e-6)
    assert generator.square_dutycycle == pytest.approx(30.0, rel=1e-3, abs=1e-3)


def test_front_panel_pulse(generator):
    """Panel should show PULS with 1 ms period, 100 us width, and 1 us transition."""
    generator.reset()
    generator.clear()
    generator.output_enabled = False

    generator.shape = "PULS"
    generator.amplitude_unit = "VPP"
    generator.amplitude = 0.2
    generator.offset = 0.0
    generator.pulse_period = 1e-3
    generator.pulse_width = 100e-6
    generator.pulse_transition = 1e-6
    generator.output_enabled = True

    assert generator.shape == "PULS"
    assert generator.amplitude == pytest.approx(0.2, rel=1e-3, abs=1e-6)
    assert generator.pulse_period == pytest.approx(1e-3, rel=1e-3, abs=1e-9)
    assert generator.pulse_width == pytest.approx(100e-6, rel=1e-3, abs=1e-9)
    assert generator.pulse_transition == pytest.approx(1e-6, rel=1e-3, abs=1e-9)


def test_burst_bus_trigger_safe(generator):
    """Panel should show burst TRIG mode with BUS source and emit a short triggered burst."""
    generator.reset()
    generator.clear()
    generator.output_enabled = False

    generator.shape = "SIN"
    generator.frequency = 1e3
    generator.amplitude_unit = "VPP"
    generator.amplitude = 0.2
    generator.offset = 0.0

    generator.burst_enabled = True
    generator.burst_mode = "TRIG"
    generator.burst_ncycles = 3
    generator.trigger_source = "BUS"

    generator.output_enabled = True
    generator.trigger()
    generator.wait_for_trigger(timeout=5)
    generator.output_enabled = False

    assert generator.burst_enabled is True
    assert generator.burst_mode in ("TRIG", "TRIGGERED")
    assert generator.burst_ncycles == 3
    assert generator.trigger_source == "BUS"
    assert generator.output_enabled is False


def test_output_load_inf_or_50(generator):
    """Panel should switch output load between 50 ohm and high impedance (INF)."""
    generator.reset()
    generator.clear()
    generator.output_enabled = False

    generator.output_load = 50
    measured_50 = generator.output_load
    assert measured_50 == pytest.approx(50.0, rel=1e-3, abs=1e-3)

    generator.output_load = "INF"
    measured_inf = generator.output_load
    assert math.isinf(measured_inf) or measured_inf >= 9.9e37
