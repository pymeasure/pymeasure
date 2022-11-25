#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.agilent.agilent33500 import Agilent33500


# from pyvisa.errors import VisaIOError

############
# FIXTURES #
############

@pytest.fixture(scope="session")
def generator():
    try:
        generator = Agilent33500("TCPIP::192.168.225.208::inst0::INSTR")
    except IOError:
        print("Not able to connect to waveform generator")
        assert False

    yield generator
    for channel in 1, 2:
        generator.ch[channel].output = 'off'
        generator.ch[channel].amplitude = 0.1
        generator.ch[channel].offset = 0.1
        generator.ch[channel].frequency = 60


########
# DATA #
########
BOOLEANS = [True, False]
CHANNELS = [1, 2]
WF_SHAPES = ['SIN', 'SQU', 'TRI', 'RAMP', 'PULS', 'PRBS', 'NOIS', 'ARB', 'DC']
AMPLITUDE_RANGE = [0.01, 10]
PHASE_RANGE = [-360, 360]
AMPLITUDE_UNIT = ["VPP", "VRMS", "DBM"]
OFFSET_RANGE = [-4.995, 4.995]
VOLTAGE_HIGH_RANGE = [-4.99, 5]
VOLTAGE_LOW_RANGE = [-5, 4.99]
SQUARE_DUTYCYCLE_RANGE = [0.01, 99.98]
RAMP_SYMMETRY_RANGE = [0, 100]
PULSE_PERIOD_RANGE = [33e-9, 1e6]
PULSE_HOLD_RANGE = [
    ["WIDT", "WIDT"],
    ["WIDTH", "WIDT"],
    ["DCYC", "DCYC"],
    ["DCYCLE", "DCYC"]
]
PULSE_WIDTH_RANGE = [16e-9, 1e6]
PULSE_DUTYCYCLE_RANGE = [0.1, 100]
PULSE_TRANSITION_RANGE = [8.4e-9, 1e-6]

#########
# TESTS #
#########


def test_get_instrument_id(generator):
    assert "Agilent Technologies" in generator.id


@pytest.mark.parametrize('channel', CHANNELS)
def test_turn_on_channel(generator, channel):
    generator.ch[channel].output = 'on'
    assert generator.ch[channel].output


@pytest.mark.parametrize('shape', WF_SHAPES)
@pytest.mark.parametrize('channel', CHANNELS)
def test_shape_channel(generator, shape, channel):
    generator.ch[channel].shape = shape
    assert shape == generator.ch[channel].shape


@pytest.mark.parametrize('frequency', [0.1, 1, 10, 100, 1000])
@pytest.mark.parametrize('channel', CHANNELS)
def test_frequency_channel(generator, frequency, channel):
    generator.ch[channel].frequency = frequency
    assert frequency == pytest.approx(generator.ch[channel].frequency, 0.01)


@pytest.mark.parametrize('amplitude', AMPLITUDE_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_amplitude_channel(generator, amplitude, channel):
    generator.ch[channel].amplitude = amplitude
    assert amplitude == pytest.approx(generator.ch[channel].amplitude, 0.01)


@pytest.mark.parametrize('amplitude_unit', AMPLITUDE_UNIT)
@pytest.mark.parametrize('channel', CHANNELS)
def test_amplitude_unit_channel(generator, amplitude_unit, channel):
    generator.ch[channel].amplitude_unit = amplitude_unit
    assert amplitude_unit == generator.ch[channel].amplitude_unit


@pytest.mark.parametrize('offset', OFFSET_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_offset_channel(generator, offset, channel):
    generator.ch[channel].offset = offset
    assert offset == pytest.approx(generator.ch[channel].offset, 0.01)


@pytest.mark.parametrize('voltage_high', VOLTAGE_HIGH_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_voltage_high_channel(generator, voltage_high, channel):
    generator.ch[channel].voltage_high = voltage_high
    assert voltage_high == pytest.approx(generator.ch[channel].voltage_high, 0.01)


@pytest.mark.parametrize('voltage_low', VOLTAGE_LOW_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_voltage_low_channel(generator, voltage_low, channel):
    generator.ch[channel].voltage_low = voltage_low
    assert voltage_low == pytest.approx(generator.ch[channel].voltage_low, 0.01)


@pytest.mark.parametrize('phase', range(PHASE_RANGE[0], PHASE_RANGE[1], 10))
@pytest.mark.parametrize('channel', CHANNELS)
def test_phase_channel(generator, phase, channel):
    generator.ch[channel].phase = phase
    assert phase == pytest.approx(generator.ch[channel].phase, 0.01)


@pytest.mark.parametrize('square_dutycycle', SQUARE_DUTYCYCLE_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_square_dutycycle_channel(generator, square_dutycycle, channel):
    generator.ch[channel].square_dutycycle = square_dutycycle
    assert square_dutycycle == pytest.approx(generator.ch[channel].square_dutycycle, 0.01)


@pytest.mark.parametrize('ramp_symmetry', RAMP_SYMMETRY_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_ramp_symmetry_channel(generator, ramp_symmetry, channel):
    generator.ch[channel].ramp_symmetry = ramp_symmetry
    assert ramp_symmetry == pytest.approx(generator.ch[channel].ramp_symmetry, 0.01)


@pytest.mark.xfail  # seems like my device 33500B only supports a min of 5e-08 range period
@pytest.mark.parametrize('pulse_period', PULSE_PERIOD_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_pulse_period_channel(generator, pulse_period, channel):
    generator.ch[channel].pulse_period = pulse_period
    assert pulse_period == pytest.approx(generator.ch[channel].pulse_period, 0.01)


@pytest.mark.parametrize('pulse_hold, expected', PULSE_HOLD_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_pulse_hold_channel(generator, pulse_hold, expected, channel):
    generator.ch[channel].pulse_hold = pulse_hold
    assert expected == generator.ch[channel].pulse_hold


@pytest.mark.parametrize('pulse_width', PULSE_WIDTH_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_pulse_width_channel(generator, pulse_width, channel):
    generator.ch[channel].pulse_width = pulse_width
    assert pulse_width == pytest.approx(generator.ch[channel].pulse_width, 0.01)


# 33500B minimum dutycycle seems to be 0.1
@pytest.mark.parametrize('pulse_dutycycle', PULSE_DUTYCYCLE_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_pulse_dutycycle_channel(generator, pulse_dutycycle, channel):
    generator.ch[channel].pulse_dutycycle = pulse_dutycycle
    assert pulse_dutycycle == pytest.approx(generator.ch[channel].pulse_dutycycle, 0.1)


@pytest.mark.parametrize('pulse_transition', PULSE_TRANSITION_RANGE)
@pytest.mark.parametrize('channel', CHANNELS)
def test_pulse_transition_channel(generator, pulse_transition, channel):
    generator.ch[channel].pulse_transition = pulse_transition
    assert pulse_transition == pytest.approx(generator.ch[channel].pulse_transition, 0.1)


@pytest.mark.parametrize('output_load', [1, 10000, 'INF'])
@pytest.mark.parametrize('channel', CHANNELS)
def test_output_load_channel(generator, channel, output_load):
    generator.ch[channel].output_load = output_load
    if output_load == 'INF':
        assert generator.ch[channel].output_load == 9.9e+37
    else:
        assert output_load == generator.ch[channel].output_load


@pytest.mark.parametrize('boolean', BOOLEANS)
@pytest.mark.parametrize('channel', CHANNELS)
def test_burst_state_channel(generator, boolean, channel):
    generator.ch[channel].burst_state = boolean
    assert boolean == generator.ch[channel].burst_state
