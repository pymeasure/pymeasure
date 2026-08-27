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
