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

from pymeasure.instruments.keysight.keysight81160A import (
    AMPLITUDE_RANGE,
    BURST_NCYCLES,
    BURST_PERIOD,
    FREQUENCY_RANGE,
    FREQUENCY_SIN_RANGE,
    IMPEDANCE_RANGE,
    LIMIT_HIGH_RANGE,
    LIMIT_LOW_RANGE,
    OFFSET_RANGE,
    PULSE_DUTYCYCLE_RANGE,
    PULSE_PERIOD_RANGE,
    PULSE_TRANSITION_RANGE,
    PULSE_WIDTH_RANGE,
    SQUARE_DUTYCYCLE_RANGE,
    STATES,
    TRIGGER_COUNT,
    TRIGGER_MODES,
    VOLTAGE_HIGH_RANGE,
    VOLTAGE_LOW_RANGE,
    WF_SHAPES,
    Keysight81160A,
    array_to_string,
    generate_pulse_sequence,
)

pytest.skip("Only works with connected hardware", allow_module_level=True)


############
# FIXTURES #
############


@pytest.fixture(scope="module")
def keysight81160A(connected_device_address):
    instr = Keysight81160A(connected_device_address)
    return instr


@pytest.fixture(autouse=True)
def reset(keysight81160A):
    keysight81160A.reset()  # ensure the device is in a defined state before each test


########
# DATA #
########
BOOLEANS = [True, False]
CHANNELS = [1, 2]
PHASE_RANGE = [-360, 360]
AMPLITUDE_UNIT = ["VPP", "VRMS", "DBM"]
RAMP_SYMMETRY_RANGE = [0, 100]
PULSE_HOLD_RANGE = [
    ["WIDT", "WIDT"],
    ["WIDTH", "WIDT"],
    ["DCYC", "DCYC"],
    ["DCYCLE", "DCYC"],
]
OUTPUT_LOAD_RANGE = [3e-1, 1e6]
BURST_MODES = [
    ["TRIG", "TRIG"],
    ["TRIGGERED", "TRIG"],
    ["GAT", "GAT"],
    ["GATED", "GAT"],
]


#########
# TESTS #
#########

#####################
# NON-CHANNEL TESTS #
#####################


def test_get_instrument_id(keysight81160A):
    assert "Agilent Technologies,81160A" in keysight81160A.id


def test_turn_on(keysight81160A):
    keysight81160A.output = "on"
    assert keysight81160A.output


@pytest.mark.parametrize("shape", WF_SHAPES)
def test_shape(keysight81160A, shape):
    keysight81160A.shape = shape
    assert shape == keysight81160A.shape


@pytest.mark.parametrize("frequency", FREQUENCY_SIN_RANGE)
def test_frequency(keysight81160A, frequency):
    keysight81160A.frequency = frequency
    assert frequency == pytest.approx(keysight81160A.frequency, 0.01)


@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
def test_amplitude(keysight81160A, amplitude):
    keysight81160A.amplitude = amplitude
    assert amplitude == pytest.approx(keysight81160A.amplitude, 0.01)


@pytest.mark.parametrize("amplitude_unit", AMPLITUDE_UNIT)
def test_amplitude_unit(keysight81160A, amplitude_unit):
    keysight81160A.amplitude_unit = amplitude_unit
    assert amplitude_unit == keysight81160A.amplitude_unit


@pytest.mark.parametrize("offset", OFFSET_RANGE)
def test_offset(keysight81160A, offset):
    keysight81160A.offset = offset
    assert offset == pytest.approx(keysight81160A.offset, 0.01)


@pytest.mark.parametrize("voltage_high", VOLTAGE_HIGH_RANGE)
def test_voltage_high(
    keysight81160A,
    voltage_high,
):
    keysight81160A.voltage_high = voltage_high
    assert voltage_high == pytest.approx(keysight81160A.voltage_high, 0.01)


@pytest.mark.parametrize("voltage_low", VOLTAGE_LOW_RANGE)
def test_voltage_low(
    keysight81160A,
    voltage_low,
):
    keysight81160A.voltage_low = voltage_low
    assert voltage_low == pytest.approx(keysight81160A.voltage_low, 0.01)


@pytest.mark.parametrize("square_dutycycle", SQUARE_DUTYCYCLE_RANGE)
def test_square_dutycycle(keysight81160A, square_dutycycle):
    keysight81160A.square_dutycycle = square_dutycycle
    assert square_dutycycle == pytest.approx(keysight81160A.square_dutycycle, 0.01)


@pytest.mark.parametrize("ramp_symmetry", RAMP_SYMMETRY_RANGE)
def test_ramp_symmetry(keysight81160A, ramp_symmetry):
    keysight81160A.ramp_symmetry = ramp_symmetry
    assert ramp_symmetry == pytest.approx(keysight81160A.ramp_symmetry, 0.01)


@pytest.mark.parametrize("pulse_period", PULSE_PERIOD_RANGE)
def test_pulse_period(keysight81160A, pulse_period):
    keysight81160A.pulse_period = pulse_period
    assert pulse_period == pytest.approx(keysight81160A.pulse_period, 0.01)


@pytest.mark.parametrize("pulse_hold, expected", PULSE_HOLD_RANGE)
def test_pulse_hold(keysight81160A, pulse_hold, expected):
    keysight81160A.pulse_hold = pulse_hold
    assert expected == keysight81160A.pulse_hold


@pytest.mark.parametrize("pulse_width", PULSE_WIDTH_RANGE)
def test_pulse_width(keysight81160A, pulse_width):
    keysight81160A.pulse_width = pulse_width
    assert pulse_width == pytest.approx(keysight81160A.pulse_width, 0.01)


@pytest.mark.parametrize("pulse_dutycycle", PULSE_DUTYCYCLE_RANGE)
def test_pulse_dutycycle(keysight81160A, pulse_dutycycle):
    keysight81160A.pulse_dutycycle = pulse_dutycycle
    assert pulse_dutycycle == pytest.approx(keysight81160A.pulse_dutycycle, 0.1)


@pytest.mark.parametrize("pulse_transition", PULSE_TRANSITION_RANGE)
def test_pulse_transition(keysight81160A, pulse_transition):
    keysight81160A.pulse_transition = pulse_transition
    assert pulse_transition == pytest.approx(keysight81160A.pulse_transition, 0.1)


@pytest.mark.parametrize("output_load", OUTPUT_LOAD_RANGE)
def test_output_load(keysight81160A, output_load):
    keysight81160A.output_load = output_load
    assert output_load == keysight81160A.output_load


@pytest.mark.parametrize("boolean", BOOLEANS)
def test_burst_state(keysight81160A, boolean):
    keysight81160A.burst_state = boolean
    assert boolean == keysight81160A.burst_state


@pytest.mark.parametrize("burst_mode, expected", BURST_MODES)
def test_burst_mode(keysight81160A, burst_mode, expected):
    keysight81160A.burst_mode = burst_mode
    assert expected == keysight81160A.burst_mode


@pytest.mark.parametrize("burst_period", BURST_PERIOD)
def test_burst_period(keysight81160A, burst_period):
    keysight81160A.burst_period = burst_period
    assert burst_period == keysight81160A.burst_period


@pytest.mark.parametrize("burst_ncycles", BURST_NCYCLES)
def test_burst_ncycles(keysight81160A, burst_ncycles):
    keysight81160A.burst_ncycles = burst_ncycles
    assert burst_ncycles == keysight81160A.burst_ncycles


# #################
# # CHANNEL TESTS #
# #################


@pytest.mark.parametrize("channel", CHANNELS)
def test_turn_on_channel(keysight81160A, channel):
    keysight81160A.channels[channel].output = "on"
    assert keysight81160A.channels[channel].output


@pytest.mark.parametrize("shape", WF_SHAPES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_shape_channel(keysight81160A, shape, channel):
    keysight81160A.channels[channel].shape = shape
    assert shape == keysight81160A.channels[channel].shape


@pytest.mark.parametrize("frequency", FREQUENCY_SIN_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_frequency_channel(keysight81160A, frequency, channel):
    keysight81160A.channels[channel].frequency = frequency
    assert frequency == pytest.approx(keysight81160A.channels[channel].frequency, 0.01)


@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_amplitude_channel(keysight81160A, amplitude, channel):
    keysight81160A.channels[channel].amplitude = amplitude
    assert amplitude == pytest.approx(keysight81160A.channels[channel].amplitude, 0.01)


@pytest.mark.parametrize("amplitude_unit", AMPLITUDE_UNIT)
@pytest.mark.parametrize("channel", CHANNELS)
def test_amplitude_unit_channel(keysight81160A, amplitude_unit, channel):
    keysight81160A.channels[channel].amplitude_unit = amplitude_unit
    assert amplitude_unit == keysight81160A.channels[channel].amplitude_unit


@pytest.mark.parametrize("offset", OFFSET_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_offset_channel(keysight81160A, offset, channel):
    keysight81160A.channels[channel].offset = offset
    assert offset == pytest.approx(keysight81160A.channels[channel].offset, 0.01)


@pytest.mark.parametrize("voltage_high", VOLTAGE_HIGH_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_high_channel(keysight81160A, voltage_high, channel):
    keysight81160A.channels[channel].voltage_high = voltage_high
    assert voltage_high == pytest.approx(keysight81160A.channels[channel].voltage_high, 0.01)


@pytest.mark.parametrize("voltage_low", VOLTAGE_LOW_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_low_channel(keysight81160A, voltage_low, channel):
    keysight81160A.channels[channel].voltage_low = voltage_low
    assert voltage_low == pytest.approx(keysight81160A.channels[channel].voltage_low, 0.01)


@pytest.mark.parametrize("square_dutycycle", SQUARE_DUTYCYCLE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_square_dutycycle_channel(keysight81160A, square_dutycycle, channel):
    keysight81160A.channels[channel].square_dutycycle = square_dutycycle
    assert square_dutycycle == pytest.approx(
        keysight81160A.channels[channel].square_dutycycle, 0.01
    )


@pytest.mark.parametrize("ramp_symmetry", RAMP_SYMMETRY_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_ramp_symmetry_channel(keysight81160A, ramp_symmetry, channel):
    keysight81160A.channels[channel].ramp_symmetry = ramp_symmetry
    assert ramp_symmetry == pytest.approx(keysight81160A.channels[channel].ramp_symmetry, 0.01)


@pytest.mark.parametrize("pulse_period", PULSE_PERIOD_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_period_channel(keysight81160A, pulse_period, channel):
    keysight81160A.channels[channel].pulse_period = pulse_period
    assert pulse_period == pytest.approx(keysight81160A.channels[channel].pulse_period, 0.01)


@pytest.mark.parametrize("pulse_hold, expected", PULSE_HOLD_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_hold_channel(keysight81160A, pulse_hold, expected, channel):
    keysight81160A.channels[channel].pulse_hold = pulse_hold
    assert expected == keysight81160A.channels[channel].pulse_hold


@pytest.mark.parametrize("pulse_width", PULSE_WIDTH_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_width_channel(keysight81160A, pulse_width, channel):
    keysight81160A.channels[channel].pulse_width = pulse_width
    assert pulse_width == pytest.approx(keysight81160A.channels[channel].pulse_width, 0.01)


@pytest.mark.parametrize("pulse_dutycycle", PULSE_DUTYCYCLE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_dutycycle_channel(keysight81160A, pulse_dutycycle, channel):
    keysight81160A.channels[channel].pulse_dutycycle = pulse_dutycycle
    assert pulse_dutycycle == pytest.approx(keysight81160A.channels[channel].pulse_dutycycle, 0.1)


@pytest.mark.parametrize("pulse_transition", PULSE_TRANSITION_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_transition_channel(keysight81160A, pulse_transition, channel):
    keysight81160A.channels[channel].pulse_transition = pulse_transition
    assert pulse_transition == pytest.approx(keysight81160A.channels[channel].pulse_transition, 0.1)


@pytest.mark.parametrize("output_load", IMPEDANCE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_output_load_channel(keysight81160A, channel, output_load):
    keysight81160A.channels[channel].output_load = output_load
    assert output_load == keysight81160A.channels[channel].output_load


@pytest.mark.parametrize("boolean", STATES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_state_channel(keysight81160A, boolean, channel):
    keysight81160A.channels[channel].burst_state = boolean
    assert boolean == keysight81160A.channels[channel].burst_state


@pytest.mark.parametrize("burst_mode, expected", BURST_MODES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_mode_channel(keysight81160A, burst_mode, expected, channel):
    keysight81160A.channels[channel].burst_mode = burst_mode
    assert expected == keysight81160A.channels[channel].burst_mode


@pytest.mark.parametrize("burst_period", BURST_PERIOD)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_period_channel(keysight81160A, burst_period, channel):
    keysight81160A.channels[channel].burst_period = burst_period
    assert burst_period == keysight81160A.channels[channel].burst_period


@pytest.mark.parametrize("burst_ncycles", BURST_NCYCLES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_ncycles_channel(keysight81160A, burst_ncycles, channel):
    keysight81160A.channels[channel].burst_ncycles = burst_ncycles
    assert burst_ncycles == keysight81160A.channels[channel].burst_ncycles


@pytest.mark.xfail  # test fails if memory is full
@pytest.mark.parametrize("channel", CHANNELS)
def test_uploaded_user_waveform_channel(keysight81160A, channel):
    ch = keysight81160A.channels[channel]
    if not ch.memory_free:
        assert False
    waveform = generate_pulse_sequence(pulse_voltage=1, dc_voltage=0)
    waveform_string = array_to_string(waveform)
    name = "TEST_USER"
    ch.save_waveform(waveform=waveform_string, name=name)
    assert name in ch.waveforms
    ch.delete_waveform(name)
    assert name not in ch.waveforms


@pytest.mark.parametrize("state", BOOLEANS)
@pytest.mark.parametrize("channel", CHANNELS)
def test_coupling_channel(keysight81160A, state, channel):
    keysight81160A.channels[channel].coupling = state
    assert state == keysight81160A.channels[channel].coupling


@pytest.mark.parametrize("state", BOOLEANS)
@pytest.mark.parametrize("channel", CHANNELS)
def test_limit_state_channel(keysight81160A, state, channel):
    keysight81160A.channels[channel].limit_state = state
    assert state == keysight81160A.channels[channel].limit_state


@pytest.mark.parametrize("limit_high", LIMIT_HIGH_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_limit_high_channel(keysight81160A, limit_high, channel):
    keysight81160A.channels[channel].limit_high = limit_high
    assert limit_high == keysight81160A.channels[channel].limit_high


@pytest.mark.parametrize("limit_low", LIMIT_LOW_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_limit_low_channel(keysight81160A, limit_low, channel):
    keysight81160A.channels[channel].limit_low = limit_low
    assert limit_low == keysight81160A.channels[channel].limit_low


@pytest.mark.parametrize("trigger_mode", TRIGGER_MODES)
@pytest.mark.parametrize("channel", CHANNELS)
def test_trigger_mode_channel(keysight81160A, trigger_mode, channel):
    keysight81160A.channels[channel].trigger_mode = trigger_mode
    assert trigger_mode == keysight81160A.channels[channel].trigger_mode


@pytest.mark.parametrize("trigger_count", TRIGGER_COUNT)
@pytest.mark.parametrize("channel", CHANNELS)
def test_trigger_count_channel(keysight81160A, trigger_count, channel):
    keysight81160A.channels[channel].trigger_count = trigger_count
    assert trigger_count == keysight81160A.channels[channel].trigger_count


@pytest.mark.parametrize("offset", OFFSET_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_dc_channel(keysight81160A, offset, channel):
    keysight81160A.channels[channel].apply_dc(voltage=offset)
    assert "DC" == keysight81160A.channels[channel].shape
    assert offset == keysight81160A.channels[channel].offset


@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_noise_amplitude_channel(keysight81160A, amplitude, channel):
    keysight81160A.channels[channel].apply_noise(amplitude, offset=0)
    assert "NOIS" == keysight81160A.channels[channel].shape
    assert amplitude == keysight81160A.channels[channel].amplitude


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_noise_exception_channel(keysight81160A, channel):
    with pytest.raises(ValueError):
        keysight81160A.channels[channel].apply_noise(
            amplitude=AMPLITUDE_RANGE[-1], offset=OFFSET_RANGE[-1]
        )


@pytest.mark.parametrize("frequency", FREQUENCY_RANGE)
@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_pulse_channel(keysight81160A, frequency, amplitude, channel):
    keysight81160A.channels[channel].apply_pulse(frequency, amplitude, offset=0)
    assert "PULS" == keysight81160A.channels[channel].shape
    assert frequency == keysight81160A.channels[channel].frequency
    assert amplitude == keysight81160A.channels[channel].amplitude


@pytest.mark.parametrize("frequency", FREQUENCY_SIN_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_sin_frequency_channel(keysight81160A, frequency, channel):
    keysight81160A.channels[channel].apply_sin(frequency=frequency, amplitude=1.0, offset=0)
    assert "SIN" == keysight81160A.channels[channel].shape
    assert frequency == keysight81160A.channels[channel].frequency


@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_sin_amplitude_channel(keysight81160A, amplitude, channel):
    keysight81160A.channels[channel].apply_sin(frequency=1e6, amplitude=amplitude, offset=0)
    assert "SIN" == keysight81160A.channels[channel].shape
    assert amplitude == keysight81160A.channels[channel].amplitude


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_sin_exception_channel(keysight81160A, channel):
    with pytest.raises(ValueError):
        keysight81160A.channels[channel].apply_sin(
            frequency=FREQUENCY_SIN_RANGE[-1], amplitude=AMPLITUDE_RANGE[-1], offset=0
        )


@pytest.mark.parametrize("frequency", FREQUENCY_RANGE)
@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_square_channel(keysight81160A, frequency, amplitude, channel):
    keysight81160A.channels[channel].apply_square(frequency, amplitude, offset=0)
    assert "SQU" == keysight81160A.channels[channel].shape
    assert frequency == keysight81160A.channels[channel].frequency
    assert amplitude == keysight81160A.channels[channel].amplitude


@pytest.mark.new
@pytest.mark.parametrize("frequency", FREQUENCY_RANGE)
@pytest.mark.parametrize("amplitude", AMPLITUDE_RANGE)
@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_user_waveform_channel(keysight81160A, frequency, amplitude, channel):
    keysight81160A.channels[channel].apply_user_waveform(frequency, amplitude, offset=0)
    assert "USER" == keysight81160A.channels[channel].shape
    assert frequency == keysight81160A.channels[channel].frequency
    assert amplitude == keysight81160A.channels[channel].amplitude
