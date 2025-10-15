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

import math
import struct

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.siglenttechnologies import SDS1000XHD

"""
Siglent SDS1000XHD Oscilloscope Test Coverage
=============================================
"""


def test_init():
    """Test instrument initialization."""
    with expected_protocol(
            SDS1000XHD,
            [],
    ):
        pass  # Verify the expected communication.


def test_channel_scale_getter():
    """Test getting channel scale."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:SCALe?', b'5.00E-01')],
    ) as inst:
        assert inst.channel_1.scale == 0.5


def test_channel_scale_setter():
    """Test setting channel scale."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:SCALe 5.000e-01', None)],
    ) as inst:
        inst.channel_1.scale = 0.5


def test_channel_coupling_getter():
    """Test getting channel coupling."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:COUPling?', b'DC')],
    ) as inst:
        assert inst.channel_1.coupling == 'DC'


def test_channel_coupling_setter():
    """Test setting channel coupling."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:COUPling AC', None)],
    ) as inst:
        inst.channel_1.coupling = 'AC'


def test_channel_probe_getter():
    """Test getting channel probe attenuation."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:PROBe?', b'10')],
    ) as inst:
        assert inst.channel_1.probe == 10.0


def test_channel_probe_setter():
    """Test setting channel probe attenuation."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:PROBe 10', None)],
    ) as inst:
        inst.channel_1.probe = 10


def test_channel_offset_getter():
    """Test getting channel offset."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:OFFSet?', b'0.000000')],
    ) as inst:
        assert inst.channel_1.offset == 0.0


def test_channel_offset_setter():
    """Test setting channel offset."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:OFFSet 0.100000', None)],
    ) as inst:
        inst.channel_1.offset = 0.1


def test_channel_visible_getter():
    """Test getting channel visibility."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:VISible?', b'ON')],
    ) as inst:
        assert inst.channel_1.visible_enabled is True


def test_channel_visible_setter():
    """Test setting channel visibility."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:VISible OFF', None)],
    ) as inst:
        inst.channel_1.visible_enabled = False


def test_waveform_source_getter():
    """Test getting waveform source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce?', b'C1')],
    ) as inst:
        assert inst.wf_C1.source == 'C1'


def test_waveform_start_point_getter():
    """Test getting waveform start point."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:STARt?', b'0')],
    ) as inst:
        assert inst.wf_C1.start_point == 0


def test_waveform_start_point_setter():
    """Test setting waveform start point."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:STARt 100', None)],
    ) as inst:
        inst.wf_C1.start_point = 100


def test_waveform_point_getter():
    """Test getting waveform point count."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:POINt?', b'1000')],
    ) as inst:
        assert inst.wf_C1.point == 1000


def test_waveform_point_setter():
    """Test setting waveform point count."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:POINt 2000', None)],
    ) as inst:
        inst.wf_C1.point = 2000


def test_waveform_width_getter():
    """Test getting waveform data width."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:WIDTh?', b'BYTE')],
    ) as inst:
        assert inst.wf_C1.width == 'BYTE'


def test_waveform_width_setter():
    """Test setting waveform data width."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:WIDTh WORD', None)],
    ) as inst:
        inst.wf_C1.width = 'WORD'


def test_waveform_max_point():
    """Test getting maximum waveform points."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:MAXPoint?', b'14000000')],
    ) as inst:
        assert inst.wf_C1.max_point == 14000000.0


def test_acq_acquisition_mode_getter():
    """Test getting acquisition fast mode enabled."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:AMODe?', b'FAST')],
    ) as inst:
        assert inst.acquisition.fast_mode_enabled is True


def test_acq_acquisition_mode_setter():
    """Test setting acquisition fast mode enabled."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:AMODe SLOW', None)],
    ) as inst:
        inst.acquisition.fast_mode_enabled = False


def test_acq_interpolation_getter():
    """Test getting acquisition interpolation."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:INTerpolation?', b'ON')],
    ) as inst:
        assert inst.acquisition.interpolation_enabled is True


def test_acq_interpolation_setter():
    """Test setting acquisition interpolation."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:INTerpolation OFF', None)],
    ) as inst:
        inst.acquisition.interpolation_enabled = False


def test_acq_memory_mgmt_getter():
    """Test getting memory management mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MMANagement?', b'AUTO')],
    ) as inst:
        assert inst.acquisition.memory_management == 'AUTO'


def test_acq_memory_mgmt_setter():
    """Test setting memory management mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MMANagement FSRate', None)],
    ) as inst:
        inst.acquisition.memory_management = 'FSRate'


def test_acq_plot_mode_getter():
    """Test getting plot mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MODE?', b'YT')],
    ) as inst:
        assert inst.acquisition.plot_mode == 'YT'


def test_acq_plot_mode_setter():
    """Test setting plot mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MODE XY', None)],
    ) as inst:
        inst.acquisition.plot_mode = 'XY'


def test_acq_resolution_high_enabled_getter():
    """Test getting resolution high enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:RESolution?', b'10Bits')],
    ) as inst:
        assert inst.acquisition.resolution_high_enabled is True


def test_acq_resolution_high_enabled_setter():
    """Test setting resolution high enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:RESolution 8Bits', None)],
    ) as inst:
        inst.acquisition.resolution_high_enabled = False


def test_timebase_scale_getter():
    """Test getting timebase scale."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:SCALe?', b'1.000000e-03')],
    ) as inst:
        assert inst.timebase.scale == 1e-3


def test_timebase_scale_setter():
    """Test setting timebase scale."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:SCALe 1.000000e-03', None)],
    ) as inst:
        inst.timebase.scale = 1e-3


def test_timebase_delay_getter():
    """Test getting timebase delay."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:DELay?', b'0.000000e+00')],
    ) as inst:
        assert inst.timebase.delay == 0.0


def test_timebase_delay_setter():
    """Test setting timebase delay."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:DELay 1.000000e-06', None)],
    ) as inst:
        inst.timebase.delay = 1e-6


def test_timebase_reference_getter():
    """Test getting timebase reference."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:REFerence?', b'DELay')],
    ) as inst:
        assert inst.timebase.reference == 'DELay'


def test_timebase_reference_setter():
    """Test setting timebase reference."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:REFerence POSition', None)],
    ) as inst:
        inst.timebase.reference = 'POSition'


def test_auto_setup():
    """Test auto setup command."""
    with expected_protocol(
            SDS1000XHD,
            [(b':AUToset', None)],
    ) as inst:
        inst.auto_setup()


def test_clear_sweeps_acq():
    """Test clear sweeps command."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:CSWeep', None)],
    ) as inst:
        inst.clear_sweeps_acq()


def test_multiple_channels():
    """Test that all channels are accessible."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel2:SCALe?', b'1.00E+00'),
             (b':CHANnel3:SCALe?', b'2.00E+00'),
             (b':CHANnel4:SCALe?', b'5.00E-01')],
    ) as inst:
        # Test that all channels are accessible
        assert inst.channel_2.scale == 1.0
        assert inst.channel_3.scale == 2.0
        assert inst.channel_4.scale == 0.5


# Additional AnalogChannel tests
def test_channel_switch_getter():
    """Test getting channel switch state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:SWITch?', b'ON')],
    ) as inst:
        assert inst.channel_1.display_enabled is True


def test_channel_switch_setter():
    """Test setting channel switch state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:SWITch OFF', None)],
    ) as inst:
        inst.channel_1.display_enabled = False


def test_channel_bandwidth_limit_getter():
    """Test getting channel bandwidth limit."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:BWLimit?', b'OFF')],
    ) as inst:
        assert inst.channel_1.bandwidth_limit_enabled is False


def test_channel_bandwidth_limit_setter():
    """Test setting channel bandwidth limit."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:BWLimit ON', None)],
    ) as inst:
        inst.channel_1.bandwidth_limit_enabled = True


def test_channel_invert_getter():
    """Test getting channel invert state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:INVert?', b'OFF')],
    ) as inst:
        assert inst.channel_1.invert is False


def test_channel_invert_setter():
    """Test setting channel invert state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:INVert ON', None)],
    ) as inst:
        inst.channel_1.invert = True


def test_channel_label_getter():
    """Test getting channel label."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:LABel:TEXT?', b'"Channel 1"')],
    ) as inst:
        assert inst.channel_1.label == 'Channel 1'


def test_channel_label_setter():
    """Test setting channel label."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:LABel:TEXT \'Test Label\'', None)],
    ) as inst:
        inst.channel_1.label = 'Test Label'


def test_channel_unit_getter():
    """Test getting channel unit."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:UNIT?', b'V')],
    ) as inst:
        assert inst.channel_1.unit == 'V'


def test_channel_unit_setter():
    """Test setting channel unit."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:UNIT A', None)],
    ) as inst:
        inst.channel_1.unit = 'A'


# WaveformChannel tests
def test_waveform_interval_getter():
    """Test getting waveform interval."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C1', None),
             (b':WAVeform:INTerval?', b'1')],
    ) as inst:
        inst.wf_C1.source = 'C1'
        assert inst.wf_C1.interval == 1


def test_waveform_interval_setter():
    """Test setting waveform interval."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C1', None),
             (b':WAVeform:INTerval 2', None)],
    ) as inst:
        inst.wf_C1.source = 'C1'
        inst.wf_C1.interval = 2


# Additional waveform tests with proper source setting
def test_waveform_source_setter():
    """Test setting waveform source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C2', None)],
    ) as inst:
        inst.wf_C1.source = 'C2'


def test_waveform_properties_with_source_setting():
    """Test accessing waveform properties after setting source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C1', None),
             (b':WAVeform:STARt?', b'0'),
             (b':WAVeform:POINt?', b'1000'),
             (b':WAVeform:WIDTh?', b'BYTE'),
             (b':WAVeform:INTerval?', b'1')],
    ) as inst:
        inst.wf_C1.source = 'C1'
        assert inst.wf_C1.start_point == 0
        assert inst.wf_C1.point == 1000
        assert inst.wf_C1.width == 'BYTE'
        assert inst.wf_C1.interval == 1


def test_waveform_get_data_requires_source():
    """Test that get_data method properly handles source setting."""
    # Note: This test verifies the get_data method exists and can be called
    # The actual binary data handling is complex and noted in the file header
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C1', None)],
    ) as inst:
        inst.wf_C1.source = 'C1'
        # Verify the method exists (actual data testing would require complex binary mocking)
        assert hasattr(inst.wf_C1, 'get_data')
        assert callable(inst.wf_C1.get_data)


def test_waveform_preamble_requires_source():
    """Test accessing preamble property with source set."""

    header_len = 11
    mock_data_array = bytearray(b'#9000000000' + b'\x00' * 400)

    # Set specific byte values at the expected offsets
    struct.pack_into('<f', mock_data_array, header_len + 0x9c, 1.0)   # v_scale
    struct.pack_into('<f', mock_data_array, header_len + 0xa0, 0.0)   # v_offset
    struct.pack_into('<f', mock_data_array, header_len + 0xb0, 1e-9)  # interval
    struct.pack_into('<f', mock_data_array, header_len + 0xa4, 25.0)  # code_per_div
    struct.pack_into('<h', mock_data_array, header_len + 0xac, 8)     # adc_bit
    struct.pack_into('<d', mock_data_array, header_len + 0xb4, 0.0)   # delay
    struct.pack_into('<h', mock_data_array, header_len + 0x144, 10)   # tdiv_index
    struct.pack_into('<f', mock_data_array, header_len + 0x148, 10.0)  # probe

    mock_data = bytes(mock_data_array)

    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C1', None),
             (b':WAVeform:PREamble?', mock_data)],
    ) as inst:
        inst.wf_C1.source = 'C1'
        result = inst.wf_C1.preamble
        assert result['vdiv'] == pytest.approx(10.0)
        assert result['adc_bit'] == 8


def test_measure_get_simple_value_frequency():
    """Test getting specific simple measurement value (frequency)."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:VALue? FREQ', b'1.000E+03')],
    ) as inst:
        result = inst.measure.get_simple_value("FREQ")
        assert result == 1000.0


def test_measure_get_simple_value_period():
    """Test getting specific simple measurement value (period)."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:VALue? PERIOD', b'1.000E-03')],
    ) as inst:
        result = inst.measure.get_simple_value("PERIOD")
        assert result == 0.001


def test_advanced_measurement_multiple_channels():
    """Test advanced measurements on multiple channels."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P2:SOURce1?', b'C2'),
             (b':MEASure:ADVanced:P3:SOURce1?', b'C3'),
             (b':MEASure:ADVanced:P4:SOURce1?', b'C4')],
    ) as inst:
        assert inst.measure.advanced_p2.source1 == 'C2'
        assert inst.measure.advanced_p3.source1 == 'C3'
        assert inst.measure.advanced_p4.source1 == 'C4'


def test_trigger_edge_complete_configuration():
    """Test complete edge trigger configuration."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:SOURce C1', None),
             (b':TRIGger:EDGE:LEVel 1.000000e+00', None),
             (b':TRIGger:EDGE:SLOPe RISing', None),
             (b':TRIGger:EDGE:COUPling DC', None),
             (b':TRIGger:EDGE:NREJect ON', None)],
    ) as inst:
        inst.trigger.edge_source = 'C1'
        inst.trigger.edge_level = 1.0
        inst.trigger.edge_slope = 'RISing'
        inst.trigger.edge_coupling = 'DC'
        inst.trigger.edge_noise_reject = True


def test_channel_complete_configuration():
    """Test complete channel configuration."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:SCALe 1.000e+00', None),
             (b':CHANnel1:COUPling DC', None),
             (b':CHANnel1:PROBe 10', None),
             (b':CHANnel1:OFFSet 0.000000', None),
             (b':CHANnel1:VISible ON', None),
             (b':CHANnel1:SWITch ON', None),
             (b':CHANnel1:BWLimit OFF', None),
             (b':CHANnel1:INVert OFF', None),
             (b':CHANnel1:LABel:TEXT \'CH1\'', None),
             (b':CHANnel1:UNIT V', None)],
    ) as inst:
        inst.channel_1.scale = 1.0
        inst.channel_1.coupling = 'DC'
        inst.channel_1.probe = 10
        inst.channel_1.offset = 0.0
        inst.channel_1.visible_enabled = True
        inst.channel_1.display_enabled = True
        inst.channel_1.bandwidth_limit_enabled = False
        inst.channel_1.invert = False
        inst.channel_1.label = 'CH1'
        inst.channel_1.unit = 'V'


def test_acquisition_complete_configuration():
    """Test complete acquisition configuration."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:AMODe FAST', None),
             (b':ACQuire:INTerpolation ON', None),
             (b':ACQuire:MMANagement AUTO', None),
             (b':ACQuire:MODE YT', None),
             (b':ACQuire:MDEPth AUTO', None),
             (b':ACQuire:RESolution 8Bits', None),
             (b':ACQuire:SEQuence OFF', None),
             (b':ACQuire:TYPE NORMal', None)],
    ) as inst:
        inst.acquisition.fast_mode_enabled = True
        inst.acquisition.interpolation_enabled = True
        inst.acquisition.memory_management = 'AUTO'
        inst.acquisition.plot_mode = 'YT'
        inst.acquisition.memory_depth = 'AUTO'
        inst.acquisition.resolution_high_enabled = False
        inst.acquisition.sequence_mode = False
        inst.acquisition.type = 'NORMal'


def test_timebase_complete_configuration():
    """Test complete timebase configuration."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:SCALe 1.000000e-03', None),
             (b':TIMebase:DELay 0.000000e+00', None),
             (b':TIMebase:REFerence DELay', None),
             (b':TIMebase:REFerence:POSition 50', None),
             (b':TIMebase:WINDow OFF', None)],
    ) as inst:
        inst.timebase.scale = 1e-3
        inst.timebase.delay = 0.0
        inst.timebase.reference = 'DELay'
        inst.timebase.reference_position = 50
        inst.timebase.window = False


# Trigger tests
def test_trigger_frequency():
    """Test getting trigger frequency."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:FREQuency?', b'1.000e+03')],
    ) as inst:
        assert inst.trigger.frequency == 1000.0


def test_trigger_mode_getter():
    """Test getting trigger mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:MODE?', b'AUTO')],
    ) as inst:
        assert inst.trigger.mode == 'AUTO'


def test_trigger_mode_setter():
    """Test setting trigger mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:MODE NORMal', None)],
    ) as inst:
        inst.trigger.mode = 'NORMal'


def test_trigger_status():
    """Test getting trigger status."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:STATus?', b'STOP')],
    ) as inst:
        assert inst.trigger.status == 'STOP'


def test_trigger_type():
    """Test getting trigger type."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:TYPE?', b'EDGE')],
    ) as inst:
        assert inst.trigger.type == 'EDGE'


def test_trigger_edge_coupling_getter():
    """Test getting edge trigger coupling."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:COUPling?', b'DC')],
    ) as inst:
        assert inst.trigger.edge_coupling == 'DC'


def test_trigger_edge_coupling_setter():
    """Test setting edge trigger coupling."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:COUPling AC', None)],
    ) as inst:
        inst.trigger.edge_coupling = 'AC'


def test_trigger_edge_level_getter():
    """Test getting edge trigger level."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:LEVel?', b'0.500000')],
    ) as inst:
        assert inst.trigger.edge_level == 0.5


def test_trigger_edge_level_setter():
    """Test setting edge trigger level."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:LEVel 1.000000e+00', None)],
    ) as inst:
        inst.trigger.edge_level = 1.0


def test_trigger_edge_slope_getter():
    """Test getting edge trigger slope."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:SLOPe?', b'RISing')],
    ) as inst:
        assert inst.trigger.edge_slope == 'RISing'


def test_trigger_edge_slope_setter():
    """Test setting edge trigger slope."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:SLOPe FALLing', None)],
    ) as inst:
        inst.trigger.edge_slope = 'FALLing'


def test_trigger_edge_source_getter():
    """Test getting edge trigger source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:SOURce?', b'C1')],
    ) as inst:
        assert inst.trigger.edge_source == 'C1'


def test_trigger_edge_source_setter():
    """Test setting edge trigger source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:SOURce C2', None)],
    ) as inst:
        inst.trigger.edge_source = 'C2'


def test_trigger_force():
    """Test forcing a trigger."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:FORce', None)],
    ) as inst:
        inst.trigger.force_trigger()


def test_trigger_run():
    """Test running trigger."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:RUN', None)],
    ) as inst:
        inst.trigger.run()


def test_trigger_stop():
    """Test stopping trigger."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:STOP', None)],
    ) as inst:
        inst.trigger.stop()


# Measurement tests
def test_measure_enabled_getter():
    """Test getting measurement enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure?', b'ON')],
    ) as inst:
        assert inst.measure.enabled is True


def test_measure_enabled_setter():
    """Test setting measurement enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure OFF', None)],
    ) as inst:
        inst.measure.enabled = False


def test_measure_mode_getter():
    """Test getting measurement mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:MODE?', b'SIMPle')],
    ) as inst:
        assert inst.measure.advanced_mode_enabled is False


def test_measure_mode_setter():
    """Test setting measurement mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:MODE ADVanced', None)],
    ) as inst:
        inst.measure.advanced_mode_enabled = True


def test_measure_advanced_line_number_getter():
    """Test getting advanced measurement line number."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:LINenumber?', b'5')],
    ) as inst:
        assert inst.measure.advanced_line_number == 5


def test_measure_advanced_line_number_setter():
    """Test setting advanced measurement line number."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:LINenumber 8', None)],
    ) as inst:
        inst.measure.advanced_line_number = 8


def test_measure_statistics_enabled_getter():
    """Test getting statistics enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:STATistics?', b'OFF')],
    ) as inst:
        assert inst.measure.statistics_enabled is False


def test_measure_statistics_enabled_setter():
    """Test setting statistics enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:STATistics ON', None)],
    ) as inst:
        inst.measure.statistics_enabled = True


def test_measure_simple_source_getter():
    """Test getting simple measurement source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:SOURce?', b'CHANnel1')],
    ) as inst:
        assert inst.measure.simple_source == 'CHANnel1'


def test_measure_simple_source_setter():
    """Test setting simple measurement source."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:SOURce CHANnel2', None)],
    ) as inst:
        inst.measure.simple_source = 'CHANnel2'


def test_measure_simple_value_all():
    """Test getting all simple measurement values using simple_value_all property."""
    all_values = ('FREQ:1.00kHz,PERIOD:1.00ms,PKPK:2.00V,MAX:1.00V,MIN:-1.00V,AMPL:2.00V,'
                  'TOP:1.00V,BASE:-1.00V,MEAN:0.00V')
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:VALue? ALL', all_values)],
    ) as inst:
        # Get all measurement values at once using the property
        result = inst.measure.simple_value_all

        # Check that the property returns the string value
        assert result == all_values


def test_measure_simple_value_error_case():
    """Test error handling in simple_value when a non-string response is received."""
    with expected_protocol(
        SDS1000XHD,
        [
            # Simulate a non-string response for a numeric return
            (b':MEASure:SIMPle:VALue? FREQ', 42.0),  # Return a number directly
        ],
    ) as inst:
        # Call the method with a parameter other than ALL
        result = inst.measure.get_simple_value("FREQ")

        # It should convert the numeric response to a float
        assert result == 42.0
        assert isinstance(result, float)


def test_measure_clear_simple():
    """Test clearing simple measurements."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:CLEar', None)],
    ) as inst:
        inst.measure.clear_simple()


def test_measure_clear_advanced():
    """Test clearing advanced measurements."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:CLEar', None)],
    ) as inst:
        inst.measure.clear_advanced()


def test_measure_reset_statistics():
    """Test resetting measurement statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:STATistics:RESet', None)],
    ) as inst:
        inst.measure.reset_statistics()


# Advanced measurement item tests
def test_advanced_measurement_enabled_getter():
    """Test getting advanced measurement item enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1?', b'ON')],
    ) as inst:
        assert inst.measure.advanced_p1.enabled is True


def test_advanced_measurement_enabled_setter():
    """Test setting advanced measurement item enabled state."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1 OFF', None)],
    ) as inst:
        inst.measure.advanced_p1.enabled = False


def test_advanced_measurement_source1_getter():
    """Test getting advanced measurement source1."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:SOURce1?', b'C1')],
    ) as inst:
        assert inst.measure.advanced_p1.source1 == 'C1'


def test_advanced_measurement_source1_setter():
    """Test setting advanced measurement source1."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:SOURce1 C2', None)],
    ) as inst:
        inst.measure.advanced_p1.source1 = 'C2'


def test_advanced_measurement_statistics_current():
    """Test getting advanced measurement current statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? CURRent', b'1.234E+00')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_current == 1.234


def test_advanced_measurement_statistics_mean():
    """Test getting advanced measurement mean statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? MEAN', b'1.500E+00')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_mean == 1.5


def test_advanced_measurement_value():
    """Test getting advanced measurement value."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:VALue?', b'2.500E+00')],
    ) as inst:
        assert inst.measure.advanced_p1.value == 2.5


# Test waveform channels access
def test_waveform_channel_c2_access():
    """Test accessing different waveform channels."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce C2', None),
             (b':WAVeform:SOURce?', b'C2'),
             (b':WAVeform:STARt?', b'0')],
    ) as inst:
        inst.wf_C2.source = 'C2'
        assert inst.wf_C2.source == 'C2'
        assert inst.wf_C2.start_point == 0


def test_waveform_channel_f1_access():
    """Test accessing function waveform channels."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce F1', None),
             (b':WAVeform:SOURce?', b'F1'),
             (b':WAVeform:WIDTh?', b'BYTE')],
    ) as inst:
        inst.wf_F1.source = 'F1'
        assert inst.wf_F1.source == 'F1'
        assert inst.wf_F1.width == 'BYTE'


def test_waveform_channel_d0_access():
    """Test accessing digital waveform channels."""
    with expected_protocol(
            SDS1000XHD,
            [(b':WAVeform:SOURce D0', None),
             (b':WAVeform:SOURce?', b'D0'),
             (b':WAVeform:POINt?', b'1000')],
    ) as inst:
        inst.wf_D0.source = 'D0'
        assert inst.wf_D0.source == 'D0'
        assert inst.wf_D0.point == 1000


# Additional trigger tests for edge trigger properties
def test_trigger_edge_noise_reject_getter():
    """Test getting edge trigger noise rejection."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:NREJect?', b'OFF')],
    ) as inst:
        assert inst.trigger.edge_noise_reject is False


def test_trigger_edge_noise_reject_setter():
    """Test setting edge trigger noise rejection."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:NREJect ON', None)],
    ) as inst:
        inst.trigger.edge_noise_reject = True


def test_trigger_edge_impedance_getter():
    """Test getting edge trigger high impedance setting."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:IMPedance?', b'ONEMeg')],
    ) as inst:
        assert inst.trigger.edge_high_impedance is True


def test_trigger_edge_impedance_setter():
    """Test setting edge trigger high impedance setting."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:IMPedance FIFTy', None)],
    ) as inst:
        inst.trigger.edge_high_impedance = False


def test_trigger_edge_hld_event_getter():
    """Test getting edge trigger holdoff event count."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HLDEVent?', b'1')],
    ) as inst:
        assert inst.trigger.edge_hld_event == 1


def test_trigger_edge_hld_event_setter():
    """Test setting edge trigger holdoff event count."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HLDEVent 10', None)],
    ) as inst:
        inst.trigger.edge_hld_event = 10


def test_trigger_edge_hld_time_getter():
    """Test getting edge trigger holdoff time."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HLDTime?', b'1.000000e-06')],
    ) as inst:
        assert inst.trigger.edge_hld_time == 1e-6


def test_trigger_edge_hld_time_setter():
    """Test setting edge trigger holdoff time."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HLDTime 2.000000e-06', None)],
    ) as inst:
        inst.trigger.edge_hld_time = 2e-6


def test_trigger_edge_hld_off_getter():
    """Test getting edge trigger holdoff type."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HOLDoff?', b'OFF')],
    ) as inst:
        assert inst.trigger.edge_hld_off == 'OFF'


def test_trigger_edge_hld_off_setter():
    """Test setting edge trigger holdoff type."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HOLDoff TIME', None)],
    ) as inst:
        inst.trigger.edge_hld_off = 'TIME'


def test_trigger_edge_hld_start_getter():
    """Test getting edge trigger holdoff start."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HSTart?', b'LAST_TRIG')],
    ) as inst:
        assert inst.trigger.edge_hld_start == 'LAST_TRIG'


def test_trigger_edge_hld_start_setter():
    """Test setting edge trigger holdoff start."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TRIGger:EDGE:HSTart ACQ_START', None)],
    ) as inst:
        inst.trigger.edge_hld_start = 'ACQ_START'


# Additional advanced measurement tests
def test_advanced_measurement_source2_getter():
    """Test getting advanced measurement source2."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:SOURce2?', b'C2')],
    ) as inst:
        assert inst.measure.advanced_p1.source2 == 'C2'


def test_advanced_measurement_source2_setter():
    """Test setting advanced measurement source2."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:SOURce2 C3', None)],
    ) as inst:
        inst.measure.advanced_p1.source2 = 'C3'


def test_advanced_measurement_statistics_all():
    """Test getting advanced measurement all statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? ALL', b'CUR,1.234E+00,MEAN,1.500E+00')],
    ) as inst:
        result = inst.measure.advanced_p1.statistics_all
        # The result should consistently be a string
        assert result == 'CUR,1.234E+00,MEAN,1.500E+00'


def test_advanced_measurement_statistics_maximum():
    """Test getting advanced measurement maximum statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? MAXimum', b'2.000E+00')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_maximum == 2.0


def test_advanced_measurement_statistics_minimum():
    """Test getting advanced measurement minimum statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? MINimum', b'0.500E+00')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_minimum == 0.5


def test_advanced_measurement_statistics_stddev():
    """Test getting advanced measurement standard deviation statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? STDev', b'0.100E+00')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_stddev == 0.1


def test_advanced_measurement_statistics_count():
    """Test getting advanced measurement count statistics."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? COUNt', b'100')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_count == 100


def test_advanced_measurement_type_getter():
    """Test getting advanced measurement type."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:TYPE?', b'P1')],
    ) as inst:
        assert inst.measure.advanced_p1.type == 'P1'


def test_advanced_measurement_type_setter():
    """Test setting advanced measurement type."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:TYPE FREQ', None)],
    ) as inst:
        inst.measure.advanced_p1.type = 'FREQ'


# Test multiple advanced measurement items
def test_advanced_measurement_p12_access():
    """Test accessing different advanced measurement items."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P12?', b'OFF'),
             (b':MEASure:ADVanced:P5:SOURce1?', b'C4')],
    ) as inst:
        assert inst.measure.advanced_p12.enabled is False
        assert inst.measure.advanced_p5.source1 == 'C4'


# Test error handling for statistics when disabled
def test_advanced_measurement_statistics_disabled():
    """Test advanced measurement statistics when disabled."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:ADVanced:P1:STATistics? CURRent', b'OFF')],
    ) as inst:
        assert inst.measure.advanced_p1.statistics_current == 'OFF'


# Test simple measurement item setting
def test_measure_simple_item():
    """Test setting simple measurement item."""
    with expected_protocol(
            SDS1000XHD,
            [(b':MEASure:SIMPle:ITEM PKPK,ON', None)],
    ) as inst:
        inst.measure.simple_item = ('PKPK', 'ON')


# Edge case tests for validation
def test_channel_probe_boundary_values():
    """Test channel probe with boundary values."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:PROBe 0.001', None),
             (b':CHANnel1:PROBe 1000', None)],
    ) as inst:
        inst.channel_1.probe = 0.001  # Minimum value
        inst.channel_1.probe = 1000   # Maximum value


def test_timebase_scale_boundary_values():
    """Test timebase scale with boundary values."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:SCALe 2.000000e-10', None),  # 200e-12 (minimum)
             (b':TIMebase:SCALe 1.000000e+03', None)],  # 1000 (maximum)
    ) as inst:
        inst.timebase.scale = 200e-12  # Minimum value
        inst.timebase.scale = 1000     # Maximum value


# Tests for WaveformChannel preamble property and get_data method
def test_parse_preamble_descriptor_basic():
    """Test parsing preamble descriptor with simplified mock binary data."""
    import pytest
    from pymeasure.instruments.siglenttechnologies import SDS1000XHD
    from pymeasure.test import expected_protocol

    with expected_protocol(
            SDS1000XHD,
            [],
    ) as inst:
        # The preamble has a header like b'#9000000000' (11 bytes)
        # The parsing function slices this off, so offsets for packing
        # must account for this header length.
        header_len = 11
        mock_data_array = bytearray(b'#9000000000' + b'\x00' * 400)

        # Set specific byte values at the expected offsets
        # All offsets are relative to the start of the data block (after the header)
        # The pack_into offset needs to be relative to the start of the whole array
        struct.pack_into('<f', mock_data_array, header_len + 0x9c, 1.0)   # v_scale
        struct.pack_into('<f', mock_data_array, header_len + 0xa0, 0.0)   # v_offset
        struct.pack_into('<f', mock_data_array, header_len + 0xb0, 1e-9)  # interval
        struct.pack_into('<f', mock_data_array, header_len + 0xa4, 25.0)  # code_per_div
        struct.pack_into('<h', mock_data_array, header_len + 0xac, 8)     # adc_bit
        struct.pack_into('<d', mock_data_array, header_len + 0xb4, 0.0)   # delay
        struct.pack_into('<h', mock_data_array, header_len + 0x144, 10)   # tdiv_index
        struct.pack_into('<f', mock_data_array, header_len + 0x148, 10.0)  # probe

        mock_data = bytes(mock_data_array)

        # Call the method directly
        result = inst.wf_C1._parse_preamble_descriptor(mock_data)

        # Verify the parsed values
        assert result['vdiv'] == pytest.approx(10.0)
        assert result['voffset'] == pytest.approx(0.0)
        assert result['interval'] == pytest.approx(1e-9)
        assert result['trdl'] == pytest.approx(0.0)
        assert result['tdiv'] == pytest.approx(500e-9)
        assert result['vcode_per'] == pytest.approx(25.0)
        assert result['adc_bit'] == 8
        assert result['probe'] == pytest.approx(10.0)


def test_waveform_get_data_comprehensive():
    """Test comprehensive waveform data retrieval with mock binary data."""

    # Create mock preamble binary data (similar to existing test)
    header_len = 11
    mock_preamble_array = bytearray(b'#9000000000' + b'\x00' * 400)

    # Set specific byte values at the expected offsets for preamble
    struct.pack_into('<f', mock_preamble_array, header_len + 0x9c, 0.05)   # v_scale (50mV/div)
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa0, 0.0)    # v_offset
    struct.pack_into('<f', mock_preamble_array, header_len + 0xb0, 2e-10)  # interval
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa4, 25.0)   # code_per_div
    struct.pack_into('<h', mock_preamble_array, header_len + 0xac, 8)      # adc_bit
    struct.pack_into('<d', mock_preamble_array, header_len + 0xb4, 0.0)    # delay
    struct.pack_into('<h', mock_preamble_array, header_len + 0x144, 10)    # tdiv_index
    struct.pack_into('<f', mock_preamble_array, header_len + 0x148, 10.0)   # probe

    mock_preamble_data = bytes(mock_preamble_array)

    # Create mock binary data for a simple waveform (sine wave pattern)
    # For 8-bit ADC, using signed bytes from -128 to 127
    sample_points = 100  # Small sample for testing
    binary_data = bytearray()

    # Generate a simple sine wave pattern in signed byte format
    for i in range(sample_points):
        # Create a sine wave with amplitude around 50 (within -128 to 127 range)
        value = int(50 * math.sin(2 * math.pi * i / 20))
        binary_data.append(value & 0xFF)  # Convert to unsigned byte representation

    # Format as IEEE 488.2 data block: #<length_digits><length><data>
    data_length = len(binary_data)
    length_str = str(data_length)
    length_digits = len(length_str)

    # Create the complete data block
    data_block = f"#{length_digits}{length_str}".encode() + binary_data + b'\n'

    with expected_protocol(
            SDS1000XHD,
            [
                # Set up waveform channel source
                (b':WAVeform:SOURce C1', None),
                # Reset start point to 0 (first operation in get_data)
                (b':WAVeform:STARt 0', None),
                # Get preamble
                (b':WAVeform:PREamble?', mock_preamble_data),
                # Get acquisition points
                (b':ACQuire:POINts?', b'100'),
                # Get max point for chunking
                (b':WAVeform:MAXPoint?', b'1000'),
                # Since points (100) <= max_point (1000), no need to set point
                # Set data width to BYTE (8-bit) - adc_bit = 8
                (b':WAVeform:WIDTh BYTE', None),
                # Set start point for data retrieval (loop iteration)
                (b':WAVeform:STARt 0', None),
                # Get waveform data
                (b'WAV:DATA?', data_block),
            ],
    ) as instr:
        # Set up waveform channel
        waveform_ch = instr.wf_C1
        waveform_ch.source = "C1"

        # Get the waveform data
        time_values, volt_values = waveform_ch.get_data()

        # Verify we got the expected number of points
        assert len(time_values) == sample_points
        assert len(volt_values) == sample_points

        # Verify time values are calculated correctly
        # Time calculation: -(tdiv * HORI_NUM / 2) + idx * interval + trdl
        # With tdiv_index=10 -> tdiv=500e-9, HORI_NUM=10, interval=2.00E-10, trdl=0.0
        expected_time_start = -(500e-9 * 10 / 2) + 0 * 2.00E-10 + 0.0
        assert abs(time_values[0] - expected_time_start) < 1e-10

        # Verify voltage values are calculated correctly
        # Voltage calculation: convert_data[idx] / vcode_per * vdiv - voffset
        # With vcode_per=25, vdiv=0.05, voffset=0.0
        # First point should be: (converted_value / 25) * 0.05 - 0.0
        expected_first_voltage = (struct.unpack("b", binary_data[0:1])[0] / 25.0) * 0.05 - 0.0
        assert abs(volt_values[0] - expected_first_voltage) < 1e-6


def test_waveform_get_data_chunked():
    """Test waveform data retrieval with chunked data (points > max_point)."""

    # Create mock preamble binary data
    header_len = 11
    mock_preamble_array = bytearray(b'#9000000000' + b'\x00' * 400)

    # Set specific byte values at the expected offsets for preamble
    struct.pack_into('<f', mock_preamble_array, header_len + 0x9c, 0.05)   # v_scale (50mV/div)
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa0, 0.0)    # v_offset
    struct.pack_into('<f', mock_preamble_array, header_len + 0xb0, 2e-10)  # interval
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa4, 25.0)   # code_per_div
    struct.pack_into('<h', mock_preamble_array, header_len + 0xac, 8)      # adc_bit
    struct.pack_into('<d', mock_preamble_array, header_len + 0xb4, 0.0)    # delay
    struct.pack_into('<h', mock_preamble_array, header_len + 0x144, 10)    # tdiv_index
    struct.pack_into('<f', mock_preamble_array, header_len + 0x148, 10.0)   # probe

    mock_preamble_data = bytes(mock_preamble_array)

    # Create mock binary data that will require chunking
    # Total points > max_point to trigger line 330
    total_points = 1500
    max_points_per_chunk = 1000

    # Generate binary data for each chunk
    chunk1_data = bytearray()
    chunk2_data = bytearray()

    for i in range(max_points_per_chunk):
        value = int(30 * math.sin(2 * math.pi * i / 100))
        chunk1_data.append(value & 0xFF)

    for i in range(total_points - max_points_per_chunk):
        value = int(30 * math.sin(2 * math.pi * (i + max_points_per_chunk) / 100))
        chunk2_data.append(value & 0xFF)

    # Format as IEEE 488.2 data blocks
    def create_data_block(data):
        data_length = len(data)
        length_str = str(data_length)
        length_digits = len(length_str)
        return f"#{length_digits}{length_str}".encode() + data + b'\n'

    data_block1 = create_data_block(chunk1_data)
    data_block2 = create_data_block(chunk2_data)

    with expected_protocol(
            SDS1000XHD,
            [
                # Set up waveform channel source
                (b':WAVeform:SOURce C2', None),
                # Reset start point to 0 (first operation in get_data)
                (b':WAVeform:STARt 0', None),
                # Get preamble
                (b':WAVeform:PREamble?', mock_preamble_data),
                # Get acquisition points
                (b':ACQuire:POINts?', b'1500'),
                # Get max point for chunking
                (b':WAVeform:MAXPoint?', b'1000'),
                # Since points (1500) > max_point (1000), set point = max_point
                (b':WAVeform:POINt 1000', None),
                # Set data width to BYTE (8-bit) - adc_bit = 8
                (b':WAVeform:WIDTh BYTE', None),
                # First chunk - set start point to 0
                (b':WAVeform:STARt 0', None),
                # Get first chunk of waveform data
                (b'WAV:DATA?', data_block1),
                # Second chunk - set start point to 1000
                (b':WAVeform:STARt 1000', None),
                # Get second chunk of waveform data
                (b'WAV:DATA?', data_block2),
            ],
    ) as instr:
        # Set up waveform channel
        waveform_ch = instr.wf_C2
        waveform_ch.source = "C2"

        # Get the waveform data
        time_values, volt_values = waveform_ch.get_data()

        # Verify we got the expected number of points
        assert len(time_values) == total_points
        assert len(volt_values) == total_points

        # Verify time values are calculated correctly
        expected_time_start = -(500e-9 * 10 / 2) + 0 * 2.00E-10 + 0.0
        assert abs(time_values[0] - expected_time_start) < 1e-10

        # Verify voltage values are calculated correctly
        # Check first point from first chunk
        first_raw_value = struct.unpack("b", chunk1_data[0:1])[0]
        expected_first_voltage = (first_raw_value / 25.0) * 0.05 - 0.0
        assert abs(volt_values[0] - expected_first_voltage) < 1e-6

        # Check first point from second chunk
        second_chunk_start_idx = max_points_per_chunk
        second_chunk_raw_value = struct.unpack("b", chunk2_data[0:1])[0]
        expected_second_chunk_voltage = (second_chunk_raw_value / 25.0) * 0.05 - 0.0
        assert abs(volt_values[second_chunk_start_idx] - expected_second_chunk_voltage) < 1e-6


def test_waveform_get_data_16bit():
    """Test waveform data retrieval with 16-bit ADC (covers WORD format)."""

    # Create mock preamble binary data for 16-bit ADC
    header_len = 11
    mock_preamble_array = bytearray(b'#9000000000' + b'\x00' * 400)

    # Set specific byte values at the expected offsets for preamble
    struct.pack_into('<f', mock_preamble_array, header_len + 0x9c, 0.1)     # v_scale (100mV/div)
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa0, 0.0)     # v_offset
    struct.pack_into('<f', mock_preamble_array, header_len + 0xb0, 1e-9)    # interval
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa4, 6553.0)  # code_per_div
    struct.pack_into('<h', mock_preamble_array, header_len + 0xac, 16)      # adc_bit (16-bit)
    struct.pack_into('<d', mock_preamble_array, header_len + 0xb4, 0.0)     # delay
    struct.pack_into('<h', mock_preamble_array, header_len + 0x144, 10)     # tdiv_index
    struct.pack_into('<f', mock_preamble_array, header_len + 0x148, 1.0)    # probe

    mock_preamble_data = bytes(mock_preamble_array)

    # Create mock binary data for 16-bit waveform
    sample_points = 50
    binary_data = bytearray()

    # Generate a simple sine wave pattern in signed 16-bit format
    for i in range(sample_points):
        # Create a sine wave with amplitude around 1000 (within -32768 to 32767 range)
        value = int(1000 * math.sin(2 * math.pi * i / 10))
        # Pack as signed 16-bit little-endian
        binary_data.extend(struct.pack("<h", value))

    # Format as IEEE 488.2 data block
    data_length = len(binary_data)
    length_str = str(data_length)
    length_digits = len(length_str)

    data_block = f"#{length_digits}{length_str}".encode() + binary_data + b'\n'

    with expected_protocol(
            SDS1000XHD,
            [
                # Set up waveform channel source
                (b':WAVeform:SOURce C3', None),
                # Reset start point to 0 (first operation in get_data)
                (b':WAVeform:STARt 0', None),
                # Get preamble
                (b':WAVeform:PREamble?', mock_preamble_data),
                # Get acquisition points
                (b':ACQuire:POINts?', b'50'),
                # Get max point for chunking
                (b':WAVeform:MAXPoint?', b'1000'),
                # Since points (50) <= max_point (1000), no need to set point
                # Set data width to BYTE first (line 333)
                (b':WAVeform:WIDTh BYTE', None),
                # Then set data width to WORD (16-bit) - adc_bit = 16 (this covers line 335)
                (b':WAVeform:WIDTh WORD', None),
                # Set start point for data retrieval (loop iteration)
                (b':WAVeform:STARt 0', None),
                # Get waveform data
                (b'WAV:DATA?', data_block),
            ],
    ) as instr:
        # Set up waveform channel
        waveform_ch = instr.wf_C3
        waveform_ch.source = "C3"

        # Get the waveform data
        time_values, volt_values = waveform_ch.get_data()

        # Verify we got the expected number of points
        assert len(time_values) == sample_points
        assert len(volt_values) == sample_points

        # Verify time values are calculated correctly
        expected_time_start = -(500e-9 * 10 / 2) + 0 * 1e-9 + 0.0
        assert abs(time_values[0] - expected_time_start) < 1e-10

        # Verify voltage values are calculated correctly for 16-bit data
        # With vcode_per=6553.0, vdiv=0.1, voffset=0.0
        first_raw_value = struct.unpack("<h", binary_data[0:2])[0]
        expected_first_voltage = (first_raw_value / 6553.0) * 0.1 - 0.0
        assert abs(volt_values[0] - expected_first_voltage) < 1e-6


def test_waveform_get_data_16bit_odd_buffer():
    """Test 16-bit data with odd buffer size (tests buffer truncation logic)."""

    # Create mock preamble binary data for 16-bit ADC
    header_len = 11
    mock_preamble_array = bytearray(b'#9000000000' + b'\x00' * 400)

    # Set specific byte values at the expected offsets for preamble
    struct.pack_into('<f', mock_preamble_array, header_len + 0x9c, 0.05)    # v_scale (50mV/div)
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa0, 0.0)     # v_offset
    struct.pack_into('<f', mock_preamble_array, header_len + 0xb0, 2e-10)   # interval
    struct.pack_into('<f', mock_preamble_array, header_len + 0xa4, 6553.0)  # code_per_div
    struct.pack_into('<h', mock_preamble_array, header_len + 0xac, 16)      # adc_bit (16-bit)
    struct.pack_into('<d', mock_preamble_array, header_len + 0xb4, 0.0)     # delay
    struct.pack_into('<h', mock_preamble_array, header_len + 0x144, 10)     # tdiv_index
    struct.pack_into('<f', mock_preamble_array, header_len + 0x148, 1.0)    # probe

    mock_preamble_data = bytes(mock_preamble_array)

    # Create mock binary data with odd number of bytes (not divisible by 2)
    # This will test the buffer truncation logic in get_data (lines 355-366)
    sample_points = 25
    binary_data = bytearray()

    # Generate 16-bit data
    for i in range(sample_points):
        value = int(500 * math.sin(2 * math.pi * i / 10))
        binary_data.extend(struct.pack("<h", value))

    # Add one extra byte to make it odd (this should be truncated)
    binary_data.append(0xFF)

    # Format as IEEE 488.2 data block
    data_length = len(binary_data)
    length_str = str(data_length)
    length_digits = len(length_str)

    data_block = f"#{length_digits}{length_str}".encode() + binary_data + b'\n'

    with expected_protocol(
            SDS1000XHD,
            [
                # Set up waveform channel source
                (b':WAVeform:SOURce C4', None),
                # Reset start point to 0 (first operation in get_data)
                (b':WAVeform:STARt 0', None),
                # Get preamble
                (b':WAVeform:PREamble?', mock_preamble_data),
                # Get acquisition points
                (b':ACQuire:POINts?', b'25'),
                # Get max point for chunking
                (b':WAVeform:MAXPoint?', b'1000'),
                # Since points (25) <= max_point (1000), no need to set point
                # Set data width to BYTE first (line 333)
                (b':WAVeform:WIDTh BYTE', None),
                # Then set data width to WORD (16-bit)
                (b':WAVeform:WIDTh WORD', None),
                # Set start point for data retrieval (loop iteration)
                (b':WAVeform:STARt 0', None),
                # Get waveform data
                (b'WAV:DATA?', data_block),
            ],
    ) as instr:
        # Set up waveform channel
        waveform_ch = instr.wf_C4
        waveform_ch.source = "C4"

        # Get the waveform data
        time_values, volt_values = waveform_ch.get_data()

        # Verify we got the expected number of points (should be 25, not 26)
        # The method should handle the odd buffer size by truncating
        assert len(time_values) == sample_points
        assert len(volt_values) == sample_points

        # Verify time values are calculated correctly
        expected_time_start = -(500e-9 * 10 / 2) + 0 * 2e-10 + 0.0
        assert abs(time_values[0] - expected_time_start) < 1e-10

        # Verify voltage values are calculated correctly
        # Remove the extra byte that was added for testing
        truncated_binary_data = binary_data[:-1]
        first_raw_value = struct.unpack("<h", truncated_binary_data[0:2])[0]
        expected_first_voltage = (first_raw_value / 6553.0) * 0.05 - 0.0
        assert abs(volt_values[0] - expected_first_voltage) < 1e-6
