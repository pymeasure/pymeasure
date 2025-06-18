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

from time import sleep

import numpy as np
import pytest
from pyvisa.errors import VisaIOError

from pymeasure.instruments.siglenttechnologies.siglent_sds1000xhd import SDS1000xHD


class TestSDS1000xHDWithDevice:
    """
    Device tests for SDS1000xHD class.

    This test suite needs the following setup to work properly:
        - A Siglent SDS1000xHD oscilloscope should be connected to the computer;
        - The device's address must be set via --device-address option
          (e.g., TCPIP::192.168.1.93::INSTR);
        - Test signals should be connected to channels for measurement verification.
    """

    #########################
    # PARAMETRIZATION CASES #
    #########################

    CHANNELS = [1, 2, 3, 4]
    CHANNEL_NAMES = ["C1", "C2", "C3", "C4"]
    BOOLEANS = [False, True]
    COUPLING_MODES = ["AC", "DC", "GND"]
    ACQUISITION_TYPES = ["NORM", "AVER", "PEAK", "HRES"]
    TRIGGER_SLOPES = ["NEG", "POS", "RFAL"]

    ############
    # FIXTURES #
    ############

    @pytest.fixture(scope="module")
    def instrument(self, connected_device_address):
        """Connect to the oscilloscope."""
        return SDS1000xHD(connected_device_address)

    @pytest.fixture
    def resetted_instrument(self, instrument):
        """Reset the instrument to default state."""
        instrument.reset()
        sleep(2)  # Allow time for reset to complete        return instrument

    @pytest.fixture
    def configured_instrument(self, resetted_instrument):
        """Configure the instrument for testing."""
        # Enable channels 1-3 for testing
        resetted_instrument.channel_1.visible = True
        resetted_instrument.channel_2.visible = True
        resetted_instrument.channel_3.visible = True
        resetted_instrument.channel_4.visible = False
        
        # Set reasonable time and voltage scales
        resetted_instrument.time_scale = 1e-3  # 1 ms/div
        resetted_instrument.channel_1.scale = 0.1  # 100 mV/div
        resetted_instrument.channel_2.scale = 0.1  # 100 mV/div
        resetted_instrument.channel_3.scale = 0.1  # 100 mV/div
        
        sleep(1)  # Allow settings to stabilize
        return resetted_instrument

    #########
    # TESTS #
    #########

    def test_instrument_connection(self):
        """Test that connection errors are properly raised."""
        bad_resource = "TCPIP::192.168.99.99::INSTR"
        with pytest.raises((ValueError, VisaIOError)):
            SDS1000xHD(bad_resource)

    def test_identification(self, instrument):
        """Test instrument identification."""
        idn = instrument.id
        assert "Siglent" in idn or "SDS" in idn, f"Unexpected identification: {idn}"

    def test_reset(self, instrument):
        """Test instrument reset functionality."""
        # Change some settings
        instrument.channel_1_enabled = False
        instrument.time_scale = 5e-3
        
        # Reset and verify
        instrument.reset()
        sleep(2)        # Check that settings are back to defaults
        assert instrument.channel_1.visible is True  # Default should be enabled
        assert abs(instrument.time_scale - 1e-3) < 1e-6  # Should be close to default

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_channel_enable_disable(self, resetted_instrument, channel):
        """Test enabling/disabling channels."""
        channel_obj = getattr(resetted_instrument, f"channel_{channel}")
        
        # Test enabling
        channel_obj.visible = True
        assert channel_obj.visible is True
        
        # Test disabling
        channel_obj.visible = False
        assert channel_obj.visible is False

    @pytest.mark.parametrize("channel", CHANNELS)
    @pytest.mark.parametrize("coupling", COUPLING_MODES)
    def test_channel_coupling(self, resetted_instrument, channel, coupling):
        """Test channel coupling settings."""
        prop_name = f"channel_{channel}_coupling"
        setattr(resetted_instrument, prop_name, coupling)
        assert getattr(resetted_instrument, prop_name) == coupling

    @pytest.mark.parametrize("channel", CHANNELS)
    def test_channel_scale(self, resetted_instrument, channel):
        """Test channel scale settings."""
        prop_name = f"channel_{channel}_scale"
        test_scales = [0.001, 0.01, 0.1, 1.0, 10.0]
        
        for scale in test_scales:
            setattr(resetted_instrument, prop_name, scale)
            read_scale = getattr(resetted_instrument, prop_name)
            assert abs(read_scale - scale) / scale < 0.1, \
                f"Scale mismatch: set {scale}, got {read_scale}"

    def test_time_scale(self, resetted_instrument):
        """Test time scale settings."""
        test_scales = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
        
        for scale in test_scales:
            resetted_instrument.time_scale = scale
            read_scale = resetted_instrument.time_scale
            assert abs(read_scale - scale) / scale < 0.1, \
                f"Time scale mismatch: set {scale}, got {read_scale}"

    @pytest.mark.parametrize("acq_type", ACQUISITION_TYPES)
    def test_acquisition_type(self, resetted_instrument, acq_type):
        """Test acquisition type settings."""
        resetted_instrument.acquisition_type = acq_type
        assert resetted_instrument.acquisition_type == acq_type

    def test_trigger_source(self, resetted_instrument):
        """Test trigger source settings."""
        sources = ["C1", "C2", "C3", "C4", "EXT", "EXT5", "LINE"]
        
        for source in sources:
            resetted_instrument.trigger_source = source
            assert resetted_instrument.trigger_source == source

    @pytest.mark.parametrize("slope", TRIGGER_SLOPES)
    def test_trigger_slope(self, resetted_instrument, slope):
        """Test trigger slope settings."""
        resetted_instrument.trigger_slope = slope
        assert resetted_instrument.trigger_slope == slope

    def test_trigger_level(self, resetted_instrument):
        """Test trigger level settings."""
        test_levels = [-1.0, -0.5, 0.0, 0.5, 1.0]
        
        for level in test_levels:
            resetted_instrument.trigger_level = level
            read_level = resetted_instrument.trigger_level
            assert abs(read_level - level) < 0.1, \
                f"Trigger level mismatch: set {level}, got {read_level}"

    def test_simple_measurements(self, configured_instrument):
        """Test simple measurement functionality."""
        # Enable simple measurements
        configured_instrument.enable_simple_measurements()
        assert configured_instrument.simple_measurements_enabled is True
        
        # Set up some measurements
        configured_instrument.set_simple_measurement("C1", "MEAN")
        configured_instrument.set_simple_measurement("C2", "PKPK")
        configured_instrument.set_simple_measurement("C3", "FREQ")
        
        sleep(1)  # Allow measurements to stabilize
        
        # Read measurements
        measurements = configured_instrument.get_all_measurements()
        assert isinstance(measurements, dict)
        assert len(measurements) > 0        # Verify specific measurements can be read
        mean_c1 = configured_instrument.get_simple_measurement("C1", "MEAN")
        assert isinstance(mean_c1, (int, float))

    def test_advanced_measurements_multi_channel(self, configured_instrument):
        """
        Test advanced measurements for multiple channels
        (similar to read_mean_channels_advanced.py).
        This tests the same functionality as the reference script.
        """
        channels = ["CHANnel1", "CHANnel2", "CHANnel3"]
        
        # Set measurement mode to advanced
        configured_instrument.simple_measurement.mode = "ADVanced"
        assert configured_instrument.simple_measurement.mode == "ADVanced"
        
        # Set up measurements for multiple channels using the measurement configs
        measurement_configs = []
        for idx, channel in enumerate(channels, 1):
            config = {
                'position': idx,
                'type': 'MEAN',
                'source1': channel
            }
            measurement_configs.append(config)
        
        # Configure advanced measurements
        configured_instrument.setup_advanced_measurements(measurement_configs)
        
        sleep(2)  # Allow measurements to stabilize
        
        # Get measurement values
        positions = [1, 2, 3]
        values = configured_instrument.get_advanced_measurement_values(positions)
        
        # Verify we got measurements for all positions
        assert len(values) == len(positions)
        for pos in positions:
            assert pos in values
            assert isinstance(values[pos], (int, float))
            print(f"Position P{pos} measurement value: {values[pos]:.6f} V")

    def test_waveform_acquisition(self, configured_instrument):
        """Test waveform data acquisition."""
        # Set up for waveform acquisition
        configured_instrument.waveform_source = "C1"
        configured_instrument.waveform_points_mode = "NOR"
        configured_instrument.waveform_points = 1000
        
        # Acquire waveform
        waveform_data = configured_instrument.get_waveform()
        
        # Verify waveform data
        assert isinstance(waveform_data, np.ndarray)
        assert len(waveform_data) > 0
        assert waveform_data.dtype in [np.float32, np.float64]
        
        print(f"Acquired waveform with {len(waveform_data)} points")
        print(f"Waveform range: {waveform_data.min():.6f} to {waveform_data.max():.6f}")

    def test_statistics_measurements(self, configured_instrument):
        """Test statistics measurement functionality."""
        # Enable statistics
        configured_instrument.statistics_enabled = True
        assert configured_instrument.statistics_enabled is True
        
        # Set up a simple measurement for statistics
        configured_instrument.enable_simple_measurements()
        configured_instrument.set_simple_measurement("C1", "MEAN")
        
        sleep(2)  # Allow statistics to accumulate
        
        # Read statistics
        stats = configured_instrument.get_statistics_values()
        assert isinstance(stats, dict)
        
        # Statistics should contain keys like CURRENT, AVERAGE, MIN, MAX, etc.
        expected_keys = ["CURRENT", "AVERAGE", "MIN", "MAX"]
        for key in expected_keys:
            assert key in stats, f"Missing statistics key: {key}"

    def test_memory_depth(self, resetted_instrument):
        """Test memory depth settings."""
        depths = ["1K", "10K", "100K", "1M", "10M"]
        
        for depth in depths:
            try:
                resetted_instrument.memory_depth = depth
                read_depth = resetted_instrument.memory_depth
                # Allow for instrument rounding/adjustment
                assert depth in read_depth or read_depth in depth
            except Exception as e:
                # Some depths might not be available on all models
                print(f"Memory depth {depth} not supported: {e}")

    def test_acquisition_start_stop(self, configured_instrument):
        """Test acquisition control."""
        # Stop acquisition
        configured_instrument.stop_acquisition()
        sleep(0.5)
        
        # Start acquisition
        configured_instrument.start_acquisition()
        sleep(0.5)
        
        # Single acquisition
        configured_instrument.single_acquisition()
        sleep(1)
        
        # Verify we can still read measurements after acquisition control
        configured_instrument.enable_simple_measurements()
        configured_instrument.set_simple_measurement("C1", "MEAN")
        sleep(1)
        
        mean_value = configured_instrument.get_simple_measurement("C1", "MEAN")
        assert isinstance(mean_value, (int, float))

    def test_bandwidth_limit(self, resetted_instrument):
        """Test bandwidth limit functionality."""
        for channel in [1, 2, 3, 4]:
            prop_name = f"channel_{channel}_bandwidth_limit"
            
            # Test enabling bandwidth limit
            setattr(resetted_instrument, prop_name, True)
            assert getattr(resetted_instrument, prop_name) is True
            
            # Test disabling bandwidth limit
            setattr(resetted_instrument, prop_name, False)
            assert getattr(resetted_instrument, prop_name) is False

    def test_probe_attenuation(self, resetted_instrument):
        """Test probe attenuation settings."""
        attenuations = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
        
        for channel in [1, 2]:  # Test first two channels
            prop_name = f"channel_{channel}_probe_attenuation"
            
            for atten in attenuations:
                setattr(resetted_instrument, prop_name, atten)
                read_atten = getattr(resetted_instrument, prop_name)
                assert abs(read_atten - atten) / atten < 0.1, \
                    f"Attenuation mismatch: set {atten}, got {read_atten}"
