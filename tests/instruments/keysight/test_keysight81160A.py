import pytest

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
