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
from pymeasure.instruments.agilent.agilent33500 import Agilent33500
from math import pi, sin


pytest.skip('Only works with connected hardware', allow_module_level=True)
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
        generator.channels[channel].output = "off"
        generator.channels[channel].amplitude = 0.1
        generator.channels[channel].offset = 0.1
        generator.channels[channel].frequency = 60


########
# DATA #
########
BOOLEANS = [True, False]
CHANNELS = [1, 2]
WF_SHAPES = ["SIN", "SQU", "TRI", "RAMP", "PULS", "PRBS", "NOIS", "ARB", "DC"]
AMPLITUDE_RANGE = [0.01, 10]
PHASE_RANGE = [-360, 360]
AMPLITUDE_UNIT = ["VPP", "VRMS", "DBM"]
OFFSET_RANGE = [-4.995, 4.995]
VOLTAGE_HIGH_RANGE = [-4.999, 5]
VOLTAGE_LOW_RANGE = [-5, 4.999]
SQUARE_DUTYCYCLE_RANGE = [0.01, 99.98]
RAMP_SYMMETRY_RANGE = [0, 100]
PULSE_PERIOD_RANGE = [33e-9, 1e6]
PULSE_HOLD_RANGE = [["WIDT", "WIDT"], ["WIDTH", "WIDT"], ["DCYC", "DCYC"], ["DCYCLE", "DCYC"]]
PULSE_WIDTH_RANGE = [16e-9, 1e6]
PULSE_DUTYCYCLE_RANGE = [0.1, 100]
PULSE_TRANSITION_RANGE = [8.4e-9, 1e-6]
BURST_MODES = [["TRIG", "TRIG"], ["TRIGGERED", "TRIG"], ["GAT", "GAT"], ["GATED", "GAT"]]
BURST_PERIOD = [1e-6, 8000]
BURST_NCYCLES = [1, 99999]
SRATE = [1e-6, 1.6e8]


def generate_simple_harmonic_waveform(harmonic, distortion):
    """
    Generates a waveform with onlhy one harmonic
    :param: harmonic: Harmonic number
    :param: distortion: Distortion of the harmonic in %
    """
    samples_per_cycle = 2048
    number_of_cycles = 4
    frequency = 60
    fundamental_amplitude = 0.707  # in ptp
    time_step = (1 / frequency) / samples_per_cycle
    waveform = []
    time = 0

    while time < ((1 / frequency) * number_of_cycles):
        fundamental = fundamental_amplitude * sin(2 * pi * frequency * time)
        harmonic_amplitude = (
                (distortion / 100) *
                fundamental_amplitude *
                sin(harmonic * 2 * pi * frequency * time)
        )
        waveform.append(fundamental + harmonic_amplitude)
        time += time_step

    return waveform

#########
# TESTS #
#########

#####################
# NON-CHANNEL TESTS #
#####################


def test_get_instrument_id(generator):
    assert "Agilent Technologies" in generator.id


def test_turn_on(generator):
    generator.output = "on"
    assert generator.output


@pytest.mark.parametrize("shape", WF_SHAPES)
def test_shape(generator, shape):
    generator.shape = shape
    assert shape == generator.shape


@pytest.mark.parametrize("frequency", [0.1, 1, 10, 100, 1000])
def test_frequency(generator, frequency):
    generator.frequency = frequency
    assert frequency == pytest.approx(generator.frequency, 0.01)


@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
def test_amplitude(generator, amplitude):
    generator.amplitude = amplitude
    assert amplitude == pytest.approx(generator.amplitude, 0.01)


@pytest.mark.xfail
@pytest.mark.parametrize("amplitude_unit", AMPLITUDE_UNIT)
def test_amplitude_unit(generator, amplitude_unit):
    generator.amplitude_unit = amplitude_unit
    assert amplitude_unit == generator.amplitude_unit


@pytest.mark.parametrize("offset", OFFSET_RANGE)
def test_offset(generator, offset):
    generator.offset = offset
    assert offset == pytest.approx(generator.offset, 0.01)


@pytest.mark.parametrize("voltage_high", VOLTAGE_HIGH_RANGE)
def test_voltage_high(
        generator,
        voltage_high,
):
    generator.voltage_high = voltage_high
    assert voltage_high == pytest.approx(generator.voltage_high, 0.01)


@pytest.mark.parametrize("voltage_low", VOLTAGE_LOW_RANGE)
def test_voltage_low(
        generator,
        voltage_low,
):
    generator.voltage_low = voltage_low
    assert voltage_low == pytest.approx(generator.voltage_low, 0.01)


@pytest.mark.parametrize("phase", range(PHASE_RANGE[0], PHASE_RANGE[1], 10))
def test_phase(generator, phase):
    generator.phase = phase
    assert phase == pytest.approx(generator.phase, 0.01)


@pytest.mark.parametrize("square_dutycycle", SQUARE_DUTYCYCLE_RANGE)
def test_square_dutycycle(generator, square_dutycycle):
    generator.square_dutycycle = square_dutycycle
    assert square_dutycycle == pytest.approx(generator.square_dutycycle, 0.01)


@pytest.mark.parametrize("ramp_symmetry", RAMP_SYMMETRY_RANGE)
def test_ramp_symmetry(generator, ramp_symmetry):
    generator.ramp_symmetry = ramp_symmetry
    assert ramp_symmetry == pytest.approx(generator.ramp_symmetry, 0.01)


@pytest.mark.xfail  # seems like my device 33500B only supports a min of 5e-08 range period
@pytest.mark.parametrize("pulse_period", PULSE_PERIOD_RANGE)
def test_pulse_period(generator, pulse_period):
    generator.pulse_period = pulse_period
    assert pulse_period == pytest.approx(generator.pulse_period, 0.01)


@pytest.mark.parametrize("pulse_hold, expected", PULSE_HOLD_RANGE)
def test_pulse_hold(generator, pulse_hold, expected):
    generator.pulse_hold = pulse_hold
    assert expected == generator.pulse_hold


@pytest.mark.parametrize("pulse_width", PULSE_WIDTH_RANGE)
def test_pulse_width(generator, pulse_width):
    generator.pulse_width = pulse_width
    assert pulse_width == pytest.approx(generator.pulse_width, 0.01)


# 33500B minimum dutycycle seems to be 0.1
@pytest.mark.parametrize("pulse_dutycycle", PULSE_DUTYCYCLE_RANGE)
def test_pulse_dutycycle(generator, pulse_dutycycle):
    generator.pulse_dutycycle = pulse_dutycycle
    assert pulse_dutycycle == pytest.approx(generator.pulse_dutycycle, 0.1)


@pytest.mark.parametrize("pulse_transition", PULSE_TRANSITION_RANGE)
def test_pulse_transition(generator, pulse_transition):
    generator.pulse_transition = pulse_transition
    assert pulse_transition == pytest.approx(generator.pulse_transition, 0.1)


@pytest.mark.parametrize("output_load", [1, 10000, "INF"])
def test_output_load(generator, output_load):
    generator.output_load = output_load
    if output_load == "INF":
        assert generator.output_load == 9.9e37
    else:
        assert output_load == generator.output_load


@pytest.mark.xfail
@pytest.mark.parametrize("boolean", BOOLEANS)
def test_burst_state(generator, boolean):
    generator.burst_state = boolean
    assert boolean == generator.burst_state


@pytest.mark.parametrize("burst_mode, expected", BURST_MODES)
def test_burst_mode(generator, burst_mode, expected):
    generator.burst_mode = burst_mode
    assert expected == generator.burst_mode


@pytest.mark.parametrize("burst_period", BURST_PERIOD)
def test_burst_period(generator, burst_period):
    generator.burst_period = burst_period
    assert burst_period == generator.burst_period


@pytest.mark.parametrize("burst_ncycles", BURST_NCYCLES)
def test_burst_ncycles(generator, burst_ncycles):
    generator.burst_ncycles = burst_ncycles
    assert burst_ncycles == generator.burst_ncycles


def test_arb_file_should_not_be_empty(generator):
    file = generator.arb_file
    assert file != ""


@pytest.mark.parametrize("srate", SRATE)
def test_arb_srate(generator, srate):
    generator.arb_srate = srate
    assert srate == generator.arb_srate


def test_uploaded_arb_file(generator):
    waveform = generate_simple_harmonic_waveform(3, 10)
    generator.shape = "ARB"
    generator.data_arb("test", waveform, data_format="float")
    generator.arb_file = "test"
    assert '"TEST"' == generator.arb_file


#################
# CHANNEL TESTS #
#################


@pytest.mark.parametrize("channel", CHANNELS)
def test_turn_on_channel(generator, channel):
    generator.channels[channel].output = "on"
    assert generator.channels[channel].output


@pytest.mark.parametrize("shape", WF_SHAPES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_shape_channel(generator, shape, channel):
    generator.channels[channel].shape = shape
    assert shape == generator.channels[channel].shape


@pytest.mark.parametrize("frequency", [0.1, 1, 10, 100, 1000])
@pytest.mark.parametrize("channel", CHANNELS)
def test_frequency_channel(generator, frequency, channel):
    generator.channels[channel].frequency = frequency
    assert frequency == pytest.approx(generator.channels[channel].frequency, 0.01)


@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_amplitude_channel(generator, amplitude, channel):
    generator.channels[channel].amplitude = amplitude
    assert amplitude == pytest.approx(generator.channels[channel].amplitude, 0.01)


@pytest.mark.xfail
@pytest.mark.parametrize("amplitude_unit", AMPLITUDE_UNIT)
@pytest.mark.parametrize("channel", CHANNELS)
def test_amplitude_unit_channel(generator, amplitude_unit, channel):
    generator.channels[channel].amplitude_unit = amplitude_unit
    assert amplitude_unit == generator.channels[channel].amplitude_unit


@pytest.mark.parametrize("offset", OFFSET_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_offset_channel(generator, offset, channel):
    generator.channels[channel].offset = offset
    assert offset == pytest.approx(generator.channels[channel].offset, 0.01)


@pytest.mark.parametrize("voltage_high", VOLTAGE_HIGH_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_high_channel(generator, voltage_high, channel):
    generator.channels[channel].voltage_high = voltage_high
    assert voltage_high == pytest.approx(generator.channels[channel].voltage_high, 0.01)


@pytest.mark.parametrize("voltage_low", VOLTAGE_LOW_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_low_channel(generator, voltage_low, channel):
    generator.channels[channel].voltage_low = voltage_low
    assert voltage_low == pytest.approx(generator.channels[channel].voltage_low, 0.01)


@pytest.mark.parametrize("phase", range(PHASE_RANGE[0], PHASE_RANGE[1], 10))
@pytest.mark.parametrize("channel", CHANNELS)
def test_phase_channel(generator, phase, channel):
    generator.channels[channel].phase = phase
    assert phase == pytest.approx(generator.channels[channel].phase, 0.01)


@pytest.mark.parametrize("square_dutycycle", SQUARE_DUTYCYCLE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_square_dutycycle_channel(generator, square_dutycycle, channel):
    generator.channels[channel].square_dutycycle = square_dutycycle
    assert square_dutycycle == pytest.approx(generator.channels[channel].square_dutycycle, 0.01)


@pytest.mark.parametrize("ramp_symmetry", RAMP_SYMMETRY_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_ramp_symmetry_channel(generator, ramp_symmetry, channel):
    generator.channels[channel].ramp_symmetry = ramp_symmetry
    assert ramp_symmetry == pytest.approx(generator.channels[channel].ramp_symmetry, 0.01)


@pytest.mark.xfail  # seems like my device 33500B only supports a min of 5e-08 range period
@pytest.mark.parametrize("pulse_period", PULSE_PERIOD_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_period_channel(generator, pulse_period, channel):
    generator.channels[channel].pulse_period = pulse_period
    assert pulse_period == pytest.approx(generator.channels[channel].pulse_period, 0.01)


@pytest.mark.parametrize("pulse_hold, expected", PULSE_HOLD_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_hold_channel(generator, pulse_hold, expected, channel):
    generator.channels[channel].pulse_hold = pulse_hold
    assert expected == generator.channels[channel].pulse_hold


@pytest.mark.parametrize("pulse_width", PULSE_WIDTH_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_width_channel(generator, pulse_width, channel):
    generator.channels[channel].pulse_width = pulse_width
    assert pulse_width == pytest.approx(generator.channels[channel].pulse_width, 0.01)


# 33500B minimum dutycycle seems to be 0.1
@pytest.mark.parametrize("pulse_dutycycle", PULSE_DUTYCYCLE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_dutycycle_channel(generator, pulse_dutycycle, channel):
    generator.channels[channel].pulse_dutycycle = pulse_dutycycle
    assert pulse_dutycycle == pytest.approx(generator.channels[channel].pulse_dutycycle, 0.1)


@pytest.mark.parametrize("pulse_transition", PULSE_TRANSITION_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_transition_channel(generator, pulse_transition, channel):
    generator.channels[channel].pulse_transition = pulse_transition
    assert pulse_transition == pytest.approx(generator.channels[channel].pulse_transition, 0.1)


@pytest.mark.parametrize("output_load", [1, 10000, "INF"])
@pytest.mark.parametrize("channel", CHANNELS)
def test_output_load_channel(generator, channel, output_load):
    generator.channels[channel].output_load = output_load
    if output_load == "INF":
        assert generator.channels[channel].output_load == 9.9e37
    else:
        assert output_load == generator.channels[channel].output_load


@pytest.mark.xfail
@pytest.mark.parametrize("boolean", BOOLEANS)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_state_channel(generator, boolean, channel):
    generator.channels[channel].burst_state = boolean
    assert boolean == generator.channels[channel].burst_state


@pytest.mark.parametrize("burst_mode, expected", BURST_MODES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_mode_channel(generator, burst_mode, expected, channel):
    generator.channels[channel].burst_mode = burst_mode
    assert expected == generator.channels[channel].burst_mode


@pytest.mark.parametrize("burst_period", BURST_PERIOD)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_period_channel(generator, burst_period, channel):
    generator.channels[channel].burst_period = burst_period
    assert burst_period == generator.channels[channel].burst_period


@pytest.mark.parametrize("burst_ncycles", BURST_NCYCLES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_ncycles_channel(generator, burst_ncycles, channel):
    generator.channels[channel].burst_ncycles = burst_ncycles
    assert burst_ncycles == generator.channels[channel].burst_ncycles


@pytest.mark.parametrize("channel", CHANNELS)
def test_arb_file_channel(generator, channel):
    file = generator.channels[channel].arb_file
    assert file != ""


@pytest.mark.parametrize("srate", SRATE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_arb_srate_channel(generator, channel, srate):
    generator.channels[channel].arb_srate = srate
    assert srate == generator.channels[channel].arb_srate


@pytest.mark.parametrize("channel", CHANNELS)
def test_uploaded_arb_file_channel(generator, channel):
    waveform = generate_simple_harmonic_waveform(3, 10)
    generator.channels[channel].shape = "ARB"
    generator.channels[channel].data_arb("test", waveform, data_format="float")
    generator.channels[channel].arb_file = "test"
    assert '"TEST"' == generator.channels[channel].arb_file


def test_phase_sync(generator):
    generator.phase_sync()
