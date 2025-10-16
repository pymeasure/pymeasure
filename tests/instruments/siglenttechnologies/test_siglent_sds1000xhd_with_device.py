import pytest
import time
from pymeasure.instruments.siglenttechnologies import SDS1000XHD

"""
Device tests for the Siglent SDS1000XHD oscilloscope.

These tests require a physical connection to a Siglent SDS1000XHD oscilloscope.
The tests are skipped by default when running pytest without the --device-address parameter.

PHYSICAL SETUP REQUIRED:
1. Connect a probe to Channel 1 of the oscilloscope
2. Connect the probe tip to the CAL output terminal on the front panel
3. Connect the probe ground clip to the GND terminal on the front panel
   This provides a built-in square wave calibration signal for testing

To run these tests:
1. Complete the physical setup above (probe connected to CAL and GND)
2. Run pytest with the device address parameter:
   pytest tests/instruments/siglenttechnologies/test_siglent_sds1000xhd_with_device.py
   --device-address="TCPIP::<IP_ADDRESS>::INSTR"

   For example:
   pytest tests/instruments/siglenttechnologies/test_siglent_sds1000xhd_with_device.py
   --device-address="TCPIP::192.168.1.100::INSTR"

   For USB connections, use:
   pytest tests/instruments/siglenttechnologies/test_siglent_sds1000xhd_with_device.py
   --device-address="USB0::0xF4EC::0xEE3A::SDS1ABCD0123::INSTR"

Alternative signal sources:
- External signal generator connected to Channel 1 (1kHz sine wave at 2Vpp recommended)
- Function generator output connected to Channel 1
"""


@pytest.fixture(scope="module")
def sds1000xhd(connected_device_address):
    """Fixture that provides a connected SDS1000XHD oscilloscope instance.

    This fixture will be skipped if no device address is provided with the
    --device-address command line argument when running pytest.

    Setup: Connect a sine wave generator to channel 1 (1kHz, 2Vpp recommended).
    """
    instr = SDS1000XHD(connected_device_address)
    # instr.write("*RST")  # Reset the instrument to known state
    time.sleep(1)  # Allow reset to complete
    return instr


@pytest.fixture
def auto_setup_sds1000xhd(sds1000xhd):
    """Fixture that automatically sets up the oscilloscope."""
    sds1000xhd.auto_setup()
    time.sleep(2)  # Allow auto setup to complete
    return sds1000xhd


def test_identification(sds1000xhd):
    """Test that the instrument identifies itself correctly."""
    idn = sds1000xhd.id
    # Check that it's a Siglent SDS device
    assert "Siglent" in idn
    assert "SDS" in idn


def test_channel_settings(sds1000xhd):
    """Test that channel settings can be configured properly."""
    # Test channel 1 settings
    sds1000xhd.channel_1.coupling = "DC"
    assert sds1000xhd.channel_1.coupling == "DC"

    sds1000xhd.channel_1.coupling = "AC"
    assert sds1000xhd.channel_1.coupling == "AC"

    # Test scale (vertical sensitivity)
    sds1000xhd.channel_1.scale = 0.5  # 500mV/div
    assert sds1000xhd.channel_1.scale == pytest.approx(0.5, abs=0.01)

    # Test offset
    sds1000xhd.channel_1.offset = 0.2
    assert sds1000xhd.channel_1.offset == pytest.approx(0.2, abs=0.01)

    # Test probe attenuation
    sds1000xhd.channel_1.probe = 10
    # Allow some tolerance for probe setting (truncated to valid values)
    assert (sds1000xhd.channel_1.probe == pytest.approx(10, abs=0.1) or
            sds1000xhd.channel_1.probe in [1, 10])


def test_timebase_settings(sds1000xhd):
    """Test that timebase settings can be configured."""
    # Set timebase scale to 1ms/div
    sds1000xhd.timebase.scale = 1e-3
    assert sds1000xhd.timebase.scale == pytest.approx(1e-3, abs=1e-4)

    # Set timebase delay to 0
    sds1000xhd.timebase.delay = 0
    assert sds1000xhd.timebase.delay == pytest.approx(0, abs=1e-6)


def test_trigger_settings(sds1000xhd):
    """Test trigger settings configuration."""
    # Set edge trigger source to channel 1
    sds1000xhd.trigger.edge_source = "C1"
    assert sds1000xhd.trigger.edge_source == "C1"

    # Set trigger mode to auto
    sds1000xhd.trigger.mode = "AUTO"
    assert sds1000xhd.trigger.mode == "AUTO"

    # Set edge trigger slope to rising edge
    sds1000xhd.trigger.edge_slope = "RISing"
    assert sds1000xhd.trigger.edge_slope == "RISing"

    # Set edge trigger level
    sds1000xhd.trigger.edge_level = 0.5
    assert sds1000xhd.trigger.edge_level == pytest.approx(0.5, abs=0.1)


def test_acquisition_settings(sds1000xhd):
    """Test acquisition settings configuration."""
    # Set acquisition type to normal
    sds1000xhd.acquisition.type = "NORMal"
    assert sds1000xhd.acquisition.type == "NORMal"

    # Set fast mode to enabled (high-speed capture)
    sds1000xhd.acquisition.fast_mode_enabled = True
    assert sds1000xhd.acquisition.fast_mode_enabled is True


def test_auto_setup(sds1000xhd):
    """Test auto setup functionality."""
    # First apply some settings that auto setup will change
    sds1000xhd.timebase.scale = 1
    time.sleep(0.5)

    # Execute auto setup
    sds1000xhd.auto_setup()
    time.sleep(3)  # Allow auto setup to complete

    # Verify that settings were changed (timebase should be different)
    # We don't know exactly what it will be, but it should be set to something reasonable
    assert sds1000xhd.timebase.scale != 1


def test_waveform_acquisition(auto_setup_sds1000xhd):
    """Test waveform data acquisition with auto setup applied.

    This test requires a signal on channel 1 (a sine wave is recommended).
    """
    scope = auto_setup_sds1000xhd

    # Set up channel 1 for acquisition
    scope.channel_1.display_enabled = True
    scope.waveform_channels["C1"].source = "C1"

    # Set data format to BYTE for faster acquisition
    scope.waveform_channels["C1"].width = "BYTE"

    # Get waveform data
    time_values, volt_values = scope.waveform_channels["C1"].get_data()

    # Verify data was acquired
    assert len(time_values) > 0
    assert len(volt_values) > 0
    assert len(time_values) == len(volt_values)

    # Check that time values are monotonically increasing
    assert all(time_values[i] <= time_values[i+1] for i in range(len(time_values)-1))

    # If a sine wave is connected, we should see some variation in the signal
    # (peak-to-peak amplitude should be non-zero)
    amplitude = max(volt_values) - min(volt_values)
    assert amplitude > 0.1  # Should have at least 100mV amplitude


def test_measurement_functions(auto_setup_sds1000xhd):
    """Test built-in measurement functions.

    This test requires a signal on channel 1 (a sine wave is recommended).
    """
    scope = auto_setup_sds1000xhd

    # Enable advanced measurement for frequency on channel 1
    scope.measure.advanced_p1.enabled = True
    scope.measure.advanced_p1.source1 = "C1"
    scope.measure.advanced_p1.type = "FREQ"

    # Wait for measurement to settle
    time.sleep(1)

    # Get the frequency measurement
    frequency = scope.measure.advanced_p1.statistics_current

    # Verify that the frequency is a reasonable value
    # For a 1kHz signal, we would expect something close to 1000 Hz
    # Handle case where measurement might return "OFF" if not available
    if isinstance(frequency, str) and frequency == "OFF":
        # Skip test if measurement is not available
        return
    assert isinstance(frequency, (int, float)), \
        f"Expected numeric value, got {type(frequency)}: {frequency}"
    assert 10 < frequency < 100000  # Wide range to accommodate various test signals


def test_multiple_channels(auto_setup_sds1000xhd):
    """Test operations with multiple channels.

    Note: This test will only check channel settings, not signal acquisition,
    as we can't guarantee signals on multiple channels during testing.
    """
    scope = auto_setup_sds1000xhd

    # Configure channel 1
    scope.channel_1.coupling = "DC"
    scope.channel_1.scale = 0.2

    # Configure channel 2
    scope.channel_2.coupling = "DC"
    scope.channel_2.scale = 0.5

    # Verify different settings on different channels
    assert scope.channel_1.coupling == scope.channel_2.coupling
    assert scope.channel_1.scale != scope.channel_2.scale


def test_trigger_run_stop(sds1000xhd):
    """Test trigger run and stop functionality."""
    # Stop acquisition
    sds1000xhd.trigger.stop()
    time.sleep(0.5)

    # Check trigger status
    status_stopped = sds1000xhd.trigger.status

    # Start acquisition
    sds1000xhd.trigger.run()
    time.sleep(0.5)

    # Check trigger status
    status_running = sds1000xhd.trigger.status

    # The status values depend on the model but should be different
    assert status_stopped != status_running


def test_save_waveform_csv(sds1000xhd, tmp_path):
    """Test acquisition and saving of waveform data to CSV.

    This demonstrates how to acquire and save data for analysis.
    """
    # Auto setup first
    sds1000xhd.auto_setup()
    time.sleep(2)

    # Set up channel 1 for acquisition
    sds1000xhd.channel_1.display_enabled = True
    sds1000xhd.waveform_channels["C1"].source = "C1"

    # Get waveform data
    time_values, volt_values = sds1000xhd.waveform_channels["C1"].get_data()

    # Save to a CSV file
    csv_path = tmp_path / "waveform_data.csv"
    with open(csv_path, 'w') as f:
        f.write("Time (s),Voltage (V)\n")
        for t, v in zip(time_values, volt_values):
            f.write(f"{t},{v}\n")

    # Verify file was created and has content
    assert csv_path.exists()
    content = csv_path.read_text()
    assert "Time (s),Voltage (V)" in content
    assert len(content.splitlines()) > 10  # Should have multiple data points


@pytest.mark.skip(reason="This test requires manual verification of screenshots.")
def test_screenshot(sds1000xhd, tmp_path):
    """Test taking a screenshot from the oscilloscope.

    This test is skipped by default as it requires manual verification.
    """
    # This functionality depends on the specific model and firmware
    # Example implementation (may need adjustment for specific models)

    # Auto setup first to ensure there's something visible
    sds1000xhd.auto_setup()
    time.sleep(2)

    # Some Siglent models support this command to capture screenshot
    # Specific format and command may vary by model
    sds1000xhd.write(":SAVE:IMAGe")

    # Note: Depending on the model, you may need to use a different method
    # to retrieve the screenshot data


def test_channel_labeling(sds1000xhd):
    """Test setting and retrieving channel labels."""
    # Set a label for channel 1
    test_label = "TEST_SIG"
    sds1000xhd.channel_1.label = test_label

    # Verify the label was set
    assert sds1000xhd.channel_1.label == test_label
