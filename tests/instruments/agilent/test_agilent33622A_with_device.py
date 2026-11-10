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

# Tested over USB and LAN.
# Setup: nothing needs to be connected to the outputs, they stay disabled.

import pytest

from pymeasure.instruments.agilent import Agilent33622A

CHANNELS = [1, 2]


@pytest.fixture(scope="module")
def connected_generator(connected_device_address):
    # *RST takes about 4.5 s
    generator = Agilent33622A(connected_device_address, timeout=10000)
    yield generator
    generator.reset()
    generator.ask("*OPC?")
    generator.adapter.close()


@pytest.fixture
def generator(connected_generator):
    connected_generator.reset()
    connected_generator.clear()
    connected_generator.ask("*OPC?")
    yield connected_generator
    errors = connected_generator.check_errors()
    assert errors == []


def test_id(generator):
    assert "33622A" in generator.id


@pytest.mark.parametrize("channel", CHANNELS)
def test_outputs_disabled(generator, channel):
    assert generator.channels[channel].output is False


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("amplitude", [1e-3, 10])
def test_amplitude_50_ohm(generator, channel, amplitude):
    ch = generator.channels[channel]
    ch.amplitude = amplitude
    assert ch.amplitude == pytest.approx(amplitude)


@pytest.mark.parametrize("channel", CHANNELS)
def test_amplitude_high_impedance(generator, channel):
    ch = generator.channels[channel]
    ch.output_load = "INF"
    ch.offset = 0
    ch.amplitude = 20
    assert ch.amplitude == pytest.approx(20)


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("offset", [-10, 10])
def test_offset_high_impedance(generator, channel, offset):
    ch = generator.channels[channel]
    ch.output_load = "INF"
    ch.shape = "DC"
    ch.offset = offset
    assert ch.offset == pytest.approx(offset)


@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_high_low_high_impedance(generator, channel):
    ch = generator.channels[channel]
    ch.output_load = "INF"
    ch.voltage_low = -10
    ch.voltage_high = 10
    assert ch.voltage_low == pytest.approx(-10)
    assert ch.voltage_high == pytest.approx(10)


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("dutycycle", [0.01, 99.98])
def test_square_dutycycle(generator, channel, dutycycle):
    ch = generator.channels[channel]
    ch.shape = "SQU"
    ch.frequency = 1e3
    ch.square_dutycycle = dutycycle
    assert ch.square_dutycycle == pytest.approx(dutycycle)


@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_minimum_timing(generator, channel):
    ch = generator.channels[channel]
    ch.shape = "PULS"
    ch.amplitude = 1
    # Shrink edges before width and width before period, otherwise the instrument adjusts them
    ch.pulse_transition = 2.9e-9
    ch.pulse_width = 5e-9
    ch.pulse_period = 10e-9
    assert ch.pulse_transition == pytest.approx(2.9e-9)
    assert ch.pulse_width == pytest.approx(5e-9)
    assert ch.pulse_period == pytest.approx(10e-9)


@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_ncycles_maximum(generator, channel):
    ch = generator.channels[channel]
    ch.frequency = 1e6
    ch.burst_ncycles = 100_000_000
    assert ch.burst_ncycles == 100_000_000


@pytest.mark.parametrize("channel", CHANNELS)
def test_arb_srate_maximum(generator, channel):
    ch = generator.channels[channel]
    ch.shape = "ARB"
    ch.arb_filter = "NORM"
    ch.arb_srate = 1e9
    assert ch.arb_srate == pytest.approx(1e9)
