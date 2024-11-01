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
