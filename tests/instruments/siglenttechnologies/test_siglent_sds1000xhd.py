from pymeasure.test import expected_protocol
from pymeasure.instruments.siglenttechnologies import SDS1000XHD


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
        assert inst.channel_1.visible is True


def test_channel_visible_setter():
    """Test setting channel visibility."""
    with expected_protocol(
            SDS1000XHD,
            [(b':CHANnel1:VISible OFF', None)],
    ) as inst:
        inst.channel_1.visible = False


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
    """Test getting acquisition mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:AMODe?', b'FAST')],
    ) as inst:
        assert inst.acq_acquisition_mode == 'FAST'


def test_acq_acquisition_mode_setter():
    """Test setting acquisition mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:AMODe SLOW', None)],
    ) as inst:
        inst.acq_acquisition_mode = 'SLOW'


def test_acq_interpolation_getter():
    """Test getting acquisition interpolation."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:INTerpolation?', b'ON')],
    ) as inst:
        assert inst.acq_interpolation is True


def test_acq_interpolation_setter():
    """Test setting acquisition interpolation."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:INTerpolation OFF', None)],
    ) as inst:
        inst.acq_interpolation = False


def test_acq_memory_mgmt_getter():
    """Test getting memory management mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MMANagement?', b'AUTO')],
    ) as inst:
        assert inst.acq_memory_mgmt == 'AUTO'


def test_acq_memory_mgmt_setter():
    """Test setting memory management mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MMANagement FSRate', None)],
    ) as inst:
        inst.acq_memory_mgmt = 'FSRate'


def test_acq_plot_mode_getter():
    """Test getting plot mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MODE?', b'YT')],
    ) as inst:
        assert inst.acq_plot_mode == 'YT'


def test_acq_plot_mode_setter():
    """Test setting plot mode."""
    with expected_protocol(
            SDS1000XHD,
            [(b':ACQuire:MODE XY', None)],
    ) as inst:
        inst.acq_plot_mode = 'XY'


def test_timebase_scale_getter():
    """Test getting timebase scale."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:SCALe?', b'1.000000e-03')],
    ) as inst:
        assert inst.timebase_scale == 1e-3


def test_timebase_scale_setter():
    """Test setting timebase scale."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:SCALe 1.000000e-03', None)],
    ) as inst:
        inst.timebase_scale = 1e-3


def test_timebase_delay_getter():
    """Test getting timebase delay."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:DELay?', b'0.000000e+00')],
    ) as inst:
        assert inst.timebase_delay == 0.0


def test_timebase_delay_setter():
    """Test setting timebase delay."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:DELay 1.000000e-06', None)],
    ) as inst:
        inst.timebase_delay = 1e-6


def test_timebase_reference_getter():
    """Test getting timebase reference."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:REFerence?', b'DELay')],
    ) as inst:
        assert inst.timebase_reference == 'DELay'


def test_timebase_reference_setter():
    """Test setting timebase reference."""
    with expected_protocol(
            SDS1000XHD,
            [(b':TIMebase:REFerence POSition', None)],
    ) as inst:
        inst.timebase_reference = 'POSition'


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
