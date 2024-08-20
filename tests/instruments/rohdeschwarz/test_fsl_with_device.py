# from time import sleep

import pytest
from pymeasure.instruments.rohdeschwarz.fsseries import FSL

pytest.skip("Only works with connected hardware", allow_module_level=True)
RESOURCE = "TCPIP::141.20.43.231::INSTR"


@pytest.fixture
def fsl_default_state():
    """
    Return an FSL instrument in its default state.
    """

    fsl = FSL(RESOURCE)
    fsl.reset()
    return fsl


@pytest.fixture
def fsl_with_channels():
    """Return an FSL instrument with 3 channels = Spectrum:SANALYZER, Test
    Spectrum: SANALYZER and
    Test Phase Noise: PNOISE

    """
    fsl = FSL(RESOURCE)
    fsl.reset()
    fsl.create_channel("SANALYZER", "Test Spectrum")
    fsl.create_channel("PNOISE", "Test Phase Noise")

    return fsl


def test_create_channels(fsl_default_state):
    """Create two channels one to get spectrum and the other to get phase
    noise."""

    fsl = fsl_default_state
    fsl.create_channel("SANALYZER", "Test Spectrum")
    fsl.create_channel("PNOISE", "Test Phase Noise")

    assert fsl.available_channels == {
        "Spectrum": "SANALYZER",
        "Test Spectrum": "SANALYZER",
        "Test Phase Noise": "PNOISE",
    }


def test_activating_channel(fsl_with_channels):

    """Activate the "Test Spectrum" channel and check that the
    channel_type is "SANALYZER" for it."""

    fsl = fsl_with_channels

    fsl.activate_channel = "Test Spectrum"
    assert fsl.available_channels.get(fsl.active_channel) == "SANALYZER"
    fsl.reset()


def test_renaming_channel(fsl_with_channels):
    """Rename the "Test Phase Noise" channel to "Test pnoise" """
    fsl = fsl_with_channels

    fsl.rename_channel("Test Phase Noise", "Test pnoise")
    assert fsl.active_channel == "Test pnoise"
    fsl.reset()


def test_deleting_channels(fsl_with_channels):
    """Delete the channel "Spectrum" and check the available
    channels"""

    fsl = fsl_with_channels
    fsl.delete_channel("Spectrum")
    assert fsl.available_channels == {
        "Test Spectrum": "SANALYZER",
        "Test Phase Noise": "PNOISE",
    }
    fsl.reset()
