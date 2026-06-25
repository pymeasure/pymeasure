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

import numpy as np
import pytest

from pymeasure.adapters.adapter import Adapter
from pymeasure.instruments.keysight import Keysight81160A
from pymeasure.instruments.keysight.keysight81160A import WF_SHAPES
from pymeasure.test import expected_protocol

CHANNELS = [1, 2]
BOOLEANS = [True, False]


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("shape", WF_SHAPES)
def test_shape(channel, shape):
    """Test shape property."""
    with expected_protocol(
        Keysight81160A,
        [(f":FUNC{channel} {shape}", None), (f":FUNC{channel}?", shape)],
    ) as inst:
        inst.channels[channel].shape = shape
        assert inst.channels[channel].shape == shape


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("state", BOOLEANS)
def test_coupling_enabled(channel, state):
    """Test coupling property."""
    with expected_protocol(
        Keysight81160A,
        [(f":TRAC:CHAN{channel} {int(state)}", None), (f":TRAC:CHAN{channel}?", int(state))],
    ) as inst:
        inst.channels[channel].coupling_enabled = state
        assert inst.channels[channel].coupling_enabled == state


# Basic properties


@pytest.mark.parametrize("channel", CHANNELS)
def test_frequency(channel):
    """Test frequency property."""
    with expected_protocol(
        Keysight81160A,
        [(f":FREQ{channel} 1000.000000", None), (f":FREQ{channel}?", "1000")],
    ) as inst:
        inst.channels[channel].frequency = 1000
        assert inst.channels[channel].frequency == 1000


@pytest.mark.parametrize("channel", CHANNELS)
def test_amplitude(channel):
    """Test amplitude property."""
    with expected_protocol(
        Keysight81160A,
        [(f":VOLT{channel} 2.000000", None), (f":VOLT{channel}?", "2")],
    ) as inst:
        inst.channels[channel].amplitude = 2
        assert inst.channels[channel].amplitude == 2


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("unit", ["VPP", "VRMS", "DBM"])
def test_amplitude_unit(channel, unit):
    """Test amplitude_unit property."""
    with expected_protocol(
        Keysight81160A,
        [(f":VOLT{channel}:UNIT {unit}", None), (f":VOLT{channel}:UNIT?", unit)],
    ) as inst:
        inst.channels[channel].amplitude_unit = unit
        assert inst.channels[channel].amplitude_unit == unit


@pytest.mark.parametrize("channel", CHANNELS)
def test_offset(channel):
    """Test offset property."""
    with expected_protocol(
        Keysight81160A,
        [(f":VOLT{channel}:OFFS 0.500000", None), (f":VOLT{channel}:OFFS?", "0.5")],
    ) as inst:
        inst.channels[channel].offset = 0.5
        assert inst.channels[channel].offset == 0.5


@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_high(channel):
    """Test voltage_high property."""
    with expected_protocol(
        Keysight81160A,
        [(f":VOLT{channel}:HIGH 1.500000", None), (f":VOLT{channel}:HIGH?", "1.5")],
    ) as inst:
        inst.channels[channel].voltage_high = 1.5
        assert inst.channels[channel].voltage_high == 1.5


@pytest.mark.parametrize("channel", CHANNELS)
def test_voltage_low(channel):
    """Test voltage_low property."""
    with expected_protocol(
        Keysight81160A,
        [(f":VOLT{channel}:LOW -1.500000", None), (f":VOLT{channel}:LOW?", "-1.5")],
    ) as inst:
        inst.channels[channel].voltage_low = -1.5
        assert inst.channels[channel].voltage_low == -1.5


# Pulse properties


@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_period(channel):
    """Test pulse_period property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":PULS:PER{channel} 1.000000e-03", None),
            (f":PULS:PER{channel}?", "0.001"),
        ],
    ) as inst:
        inst.channels[channel].pulse_period = 1e-3
        assert inst.channels[channel].pulse_period == 1e-3


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("hold", ["WIDT", "WIDTH", "DCYC", "DCYCLE"])
def test_pulse_hold(channel, hold):
    """Test pulse_hold property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":PULS:HOLD{channel} {hold}", None),
            (f":PULS:HOLD{channel}?", hold),
        ],
    ) as inst:
        inst.channels[channel].pulse_hold = hold
        assert inst.channels[channel].pulse_hold == hold


@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_width(channel):
    """Test pulse_width property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":PULS:WIDT{channel} 1.000000e-04", None),
            (f":PULS:WIDT{channel}?", "0.0001"),
        ],
    ) as inst:
        inst.channels[channel].pulse_width = 1e-4
        assert inst.channels[channel].pulse_width == 1e-4


@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_dutycycle(channel):
    """Test pulse_dutycycle property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":PULS:DCYC{channel} 50.000000", None),
            (f":PULS:DCYC{channel}?", "50"),
        ],
    ) as inst:
        inst.channels[channel].pulse_dutycycle = 50
        assert inst.channels[channel].pulse_dutycycle == 50


@pytest.mark.parametrize("channel", CHANNELS)
def test_pulse_transition(channel):
    """Test pulse_transition property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":FUNC{channel}:PULS:TRAN 1.000000e-08", None),
            (f":FUNC{channel}:PULS:TRAN?", "1e-08"),
        ],
    ) as inst:
        inst.channels[channel].pulse_transition = 10e-9
        assert inst.channels[channel].pulse_transition == 1e-8


@pytest.mark.parametrize("channel", CHANNELS)
def test_square_dutycycle(channel):
    """Test square_dutycycle property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":FUNC{channel}:SQU:DCYC 50.000000", None),
            (f":FUNC{channel}:SQU:DCYC?", "50"),
        ],
    ) as inst:
        inst.channels[channel].square_dutycycle = 50
        assert inst.channels[channel].square_dutycycle == 50


@pytest.mark.parametrize("channel", CHANNELS)
def test_ramp_symmetry(channel):
    """Test ramp_symmetry property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":FUNC{channel}:RAMP:SYMM 50.000000", None),
            (f":FUNC{channel}:RAMP:SYMM?", "50"),
        ],
    ) as inst:
        inst.channels[channel].ramp_symmetry = 50
        assert inst.channels[channel].ramp_symmetry == 50


# Burst properties


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("state", BOOLEANS)
def test_burst_state(channel, state):
    """Test burst_state property.

    Note: the driver currently uses a list (``[True, False]``) for ``burst_state_values``,
    which combined with ``map_values=True`` maps ``True`` to ``0`` and ``False`` to ``1``.
    These tests assert the actual driver behavior, not the intended semantics.
    """
    mapped = 0 if state else 1
    with expected_protocol(
        Keysight81160A,
        [
            (f":BURS{channel}:STAT {mapped}", None),
            (f":BURS{channel}:STAT?", str(mapped)),
        ],
    ) as inst:
        inst.channels[channel].burst_state = state
        # reverse mapping: value at index `mapped`
        assert inst.channels[channel].burst_state == BOOLEANS[mapped]


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("mode", ["TRIG", "TRIGGERED", "GAT", "GATED"])
def test_burst_mode(channel, mode):
    """Test burst_mode property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":BURS{channel}:MODE {mode}", None),
            (f":BURS{channel}:MODE?", mode),
        ],
    ) as inst:
        inst.channels[channel].burst_mode = mode
        assert inst.channels[channel].burst_mode == mode


@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_period(channel):
    """Test burst_period property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":BURS{channel}:INT:PER 1.000000e-03", None),
            (f":BURS{channel}:INT:PER?", "0.001"),
        ],
    ) as inst:
        inst.channels[channel].burst_period = 1e-3
        assert inst.channels[channel].burst_period == 1e-3


@pytest.mark.parametrize("channel", CHANNELS)
def test_burst_ncycles(channel):
    """Test burst_ncycles property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":BURS{channel}:NCYC 5", None),
            (f":BURS{channel}:NCYC?", "5"),
        ],
    ) as inst:
        inst.channels[channel].burst_ncycles = 5
        assert inst.channels[channel].burst_ncycles == 5


# Limit properties


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("state", BOOLEANS)
def test_limit_state_enabled(channel, state):
    """Test limit_state_enabled property."""
    mapped = 1 if state else 0
    with expected_protocol(
        Keysight81160A,
        [
            (f":VOLT{channel}:LIM:STAT {mapped}", None),
            (f":VOLT{channel}:LIM:STAT?", str(mapped)),
        ],
    ) as inst:
        inst.channels[channel].limit_state_enabled = state
        assert inst.channels[channel].limit_state_enabled == state


@pytest.mark.parametrize("channel", CHANNELS)
def test_limit_high(channel):
    """Test limit_high property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":VOLT{channel}:LIM:HIGH 5.000000", None),
            (f":VOLT{channel}:LIM:HIGH?", "5"),
        ],
    ) as inst:
        inst.channels[channel].limit_high = 5
        assert inst.channels[channel].limit_high == 5


@pytest.mark.parametrize("channel", CHANNELS)
def test_limit_low(channel):
    """Test limit_low property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":VOLT{channel}:LIM:LOW -5.000000", None),
            (f":VOLT{channel}:LIM:LOW?", "-5"),
        ],
    ) as inst:
        inst.channels[channel].limit_low = -5
        assert inst.channels[channel].limit_low == -5


# Other properties


@pytest.mark.parametrize("channel", CHANNELS)
def test_output_load(channel):
    """Test output_load property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":OUTP{channel}:LOAD 5.000000e+01", None),
            (f":OUTP{channel}:LOAD?", "50"),
        ],
    ) as inst:
        inst.channels[channel].output_load = 50
        assert inst.channels[channel].output_load == 50


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize("mode", ["IMM", "INT2", "EXT", "MAN"])
def test_trigger_mode(channel, mode):
    """Test trigger_mode property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":ARM:SOUR{channel} {mode}", None),
            (f":ARM:SOUR{channel}?", mode),
        ],
    ) as inst:
        inst.channels[channel].trigger_mode = mode
        assert inst.channels[channel].trigger_mode == mode


@pytest.mark.parametrize("channel", CHANNELS)
def test_trigger_count(channel):
    """Test trigger_count property."""
    with expected_protocol(
        Keysight81160A,
        [
            (f":TRIG{channel}:COUN 5", None),
            (f":TRIG{channel}:COUN?", "5"),
        ],
    ) as inst:
        inst.channels[channel].trigger_count = 5
        assert inst.channels[channel].trigger_count == 5


@pytest.mark.parametrize("channel", CHANNELS)
def test_free_memory_slots(channel):
    """Test free_memory_slots measurement property."""
    with expected_protocol(
        Keysight81160A,
        [(f":DATA{channel}:NVOL:FREE?", "4")],
    ) as inst:
        assert inst.channels[channel].free_memory_slots == 4


@pytest.mark.parametrize("channel", CHANNELS)
def test_waveforms(channel):
    """Test waveforms measurement property.

    The reply is preprocessed (quotes and newlines stripped) and then split into a list
    of waveform names on commas.
    """
    with expected_protocol(
        Keysight81160A,
        [(f":DATA{channel}:NVOL:CAT?", '"test1,test2\n"')],
    ) as inst:
        assert inst.channels[channel].waveforms == ["test1", "test2"]


# Methods: apply_*


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_dc(channel):
    """Test apply_dc method."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:DC DEF, DEF, 1.5", None)],
    ) as inst:
        inst.channels[channel].apply_dc(1.5)


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_noise(channel):
    """Test apply_noise method."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:NOIS DEF, 2, 0", None)],
    ) as inst:
        inst.channels[channel].apply_noise(2, 0)


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_pulse(channel):
    """Test apply_pulse method."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:PULS 1000, 2, 0", None)],
    ) as inst:
        inst.channels[channel].apply_pulse(1000, 2, 0)


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_sin(channel):
    """Test apply_sin method."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:SIN 1000, 2, 0", None)],
    ) as inst:
        inst.channels[channel].apply_sin(1000, 2, 0)


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_square(channel):
    """Test apply_square method."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:SQU 1000, 2, 0", None)],
    ) as inst:
        inst.channels[channel].apply_square(1000, 2, 0)


@pytest.mark.parametrize("channel", CHANNELS)
def test_apply_user_waveform(channel):
    """Test apply_user_waveform method."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:USER 1000, 2, 0", None)],
    ) as inst:
        inst.channels[channel].apply_user_waveform(1000, 2, 0)


# Methods: waveform memory


def _expected_volatile_command(channel, waveform):
    """Build the expected binary command for the waveform_volatile setter."""
    adapter = object.__new__(Adapter)
    data = np.array(waveform, dtype=np.float64)
    data_normed = data / data.max()
    data_int = np.round(data_normed * 8191).astype(int)
    block = adapter._format_binary_values(
        list(data_int), datatype="h", is_big_endian=True
    )
    return f":DATA{channel}:DAC VOLATILE,".encode() + block


@pytest.mark.parametrize("channel", CHANNELS)
def test_waveform_volatile_setter(channel):
    """Test waveform_volatile setter writes binary data."""
    waveform = [2.0, -2.0]
    expected = _expected_volatile_command(channel, waveform)
    with expected_protocol(
        Keysight81160A,
        [(expected, None)],
    ) as inst:
        inst.channels[channel].waveform_volatile = waveform
        np.testing.assert_array_equal(
            inst.channels[channel].waveform_volatile, waveform
        )


@pytest.mark.parametrize("channel", CHANNELS)
def test_waveform_volatile_unset(channel):
    """Test waveform_volatile getter returns None if not set."""
    with expected_protocol(
        Keysight81160A,
        [],
    ) as inst:
        assert inst.channels[channel].waveform_volatile is None


@pytest.mark.parametrize("channel", CHANNELS)
def test_save_waveform(channel):
    """Test save_waveform method sets volatile then copies to non-volatile memory."""
    waveform = [2.0, -2.0]
    expected_binary = _expected_volatile_command(channel, waveform)
    with expected_protocol(
        Keysight81160A,
        [
            (expected_binary, None),
            (f":DATA{channel}:COPY test, VOLATILE", None),
        ],
    ) as inst:
        inst.channels[channel].save_waveform(waveform, "test")


@pytest.mark.parametrize("channel", CHANNELS)
def test_delete_waveform(channel):
    """Test delete_waveform method upper-cases the name and writes DEL."""
    with expected_protocol(
        Keysight81160A,
        [(f":DATA{channel}:DEL TEST", None)],
    ) as inst:
        inst.channels[channel].delete_waveform("test")


# Validator edge cases


@pytest.mark.parametrize("channel", CHANNELS)
@pytest.mark.parametrize(
    "method,kwargs",
    [
        ("apply_noise", {"amplitude": 4, "offset": 2}),
        ("apply_pulse", {"frequency": 1000, "amplitude": 4, "offset": 2}),
        ("apply_sin", {"frequency": 1000, "amplitude": 4, "offset": 2}),
        ("apply_square", {"frequency": 1000, "amplitude": 4, "offset": 2}),
        ("apply_user_waveform", {"frequency": 1000, "amplitude": 4, "offset": 2}),
    ],
)
def test_check_voltages_raises(channel, method, kwargs):
    """Test that |amplitude| + |offset| > 5 V raises ValueError."""
    with expected_protocol(Keysight81160A, []) as inst:
        with pytest.raises(ValueError, match="exceed maximal voltage"):
            getattr(inst.channels[channel], method)(**kwargs)


@pytest.mark.parametrize("channel", CHANNELS)
def test_check_sin_params_raises(channel):
    """Test that freq > 330 MHz with amplitude > 3 V raises ValueError for apply_sin."""
    with expected_protocol(Keysight81160A, []) as inst:
        with pytest.raises(ValueError, match="amplitude below"):
            inst.channels[channel].apply_sin(400e6, 4, 0)


@pytest.mark.parametrize("channel", CHANNELS)
def test_check_sin_params_within_limits(channel):
    """Test apply_sin succeeds when freq > 330 MHz but amplitude <= 3 V."""
    with expected_protocol(
        Keysight81160A,
        [(f":APPL{channel}:SIN 400000000.0, 2, 0", None)],
    ) as inst:
        inst.channels[channel].apply_sin(400e6, 2, 0)
