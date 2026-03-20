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

from pymeasure.instruments.rohdeschwarz.fsseries import FSL


@pytest.fixture(scope="module")
def fsl(connected_device_address):
    instr = FSL(connected_device_address)
    return instr


@pytest.fixture
def fsl_default_state(fsl):
    """
    Return an FSL instrument in its default state.
    """

    fsl.reset()
    return fsl


@pytest.fixture
def fsl_with_channels(fsl):
    """Return an FSL instrument with 3 channels = Spectrum:SANALYZER, Test
    Spectrum: SANALYZER and
    Test Phase Noise: PNOISE

    """
    fsl.reset()
    fsl.create_channel("SANALYZER", "Test Spectrum")
    fsl.create_channel("PNOISE", "Test Phase Noise")

    return fsl


def test_create_channels(fsl):
    """Create two channels one to get spectrum and the other to get phase
    noise."""

    fsl.create_channel("SANALYZER", "Test Spectrum")
    fsl.create_channel("PNOISE", "Test Phase Noise")

    assert fsl.available_channels == {
        "Spectrum": "SANALYZER",
        "Test Spectrum": "SANALYZER",
        "Test Phase Noise": "PNOISE",
    }


def test_activating_channel(fsl):
    """Activate the "Test Spectrum" channel and check that the
    channel_type is "SANALYZER" for it."""

    fsl.activate_channel = "Test Spectrum"
    assert fsl.available_channels.get(fsl.active_channel) == "SANALYZER"
    fsl.reset()


def test_renaming_channel(fsl):
    """Rename the "Test Phase Noise" channel to "Test pnoise" """

    fsl.rename_channel("Test Phase Noise", "Test pnoise")
    assert fsl.active_channel == "Test pnoise"
    fsl.reset()


def test_deleting_channels(fsl):
    """Delete the channel "Spectrum" and check the available
    channels"""

    fsl.delete_channel("Spectrum")
    assert fsl.available_channels == {
        "Test Spectrum": "SANALYZER",
        "Test Phase Noise": "PNOISE",
    }
    fsl.reset()
