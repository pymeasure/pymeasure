import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.siglenttechnologies import SDS1000xHD


class TestVoltageChannel:
    """Test voltage channel controls."""

    def test_scale_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:SCALe 1.000e-01", None)],
        ) as inst:
            inst.channel_1.scale = 0.1

    def test_scale_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:SCALe?", "1.000E-01")],
        ) as inst:
            assert inst.channel_1.scale == 0.1

    def test_coupling_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:COUPling DC", None)],
        ) as inst:
            inst.channel_1.coupling = "DC"

    def test_coupling_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:COUPling?", "DC")],
        ) as inst:
            assert inst.channel_1.coupling == "DC"

    def test_probe_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:PROBe 10", None)],
        ) as inst:
            inst.channel_1.probe = 10

    def test_probe_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:PROBe?", "10.0")],
        ) as inst:
            assert inst.channel_1.probe == 10.0

    def test_offset_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:OFFSet 0.500000", None)],
        ) as inst:
            inst.channel_1.offset = 0.5

    def test_offset_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:OFFSet?", "0.500000")],
        ) as inst:
            assert inst.channel_1.offset == 0.5

    def test_visible_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:VISible ON", None)],
        ) as inst:
            inst.channel_1.visible = True

    def test_visible_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:VISible?", "ON")],
        ) as inst:
            assert inst.channel_1.visible is True

    def test_bandwidth_limit_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:BWLimit ON", None)],
        ) as inst:
            inst.channel_1.bandwidth_limit = True

    def test_bandwidth_limit_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:BWLimit?", "OFF")],
        ) as inst:
            assert inst.channel_1.bandwidth_limit is False

    def test_invert_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:INVert ON", None)],
        ) as inst:
            inst.channel_1.invert = True

    def test_invert_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:INVert?", "OFF")],
        ) as inst:
            assert inst.channel_1.invert is False

    def test_label_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:LABel:TEXT 'Test Channel'", None)],
        ) as inst:
            inst.channel_1.label = "Test Channel"

    def test_label_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:LABel:TEXT?", "\"Test Channel\"")],
        ) as inst:
            assert inst.channel_1.label == "Test Channel"

    def test_unit_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:UNIT V", None)],
        ) as inst:
            inst.channel_1.unit = "V"

    def test_unit_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":CHANnel1:UNIT?", "V")],
        ) as inst:
            assert inst.channel_1.unit == "V"

    def test_get_waveform(self):
        with expected_protocol(
            SDS1000xHD,
            [(":WAVeform:SOURce CHANnel1", None),
             (":WAVeform:FORMat BYTE", None),
             (":WAVeform:DATA?", "#9000001024" + "x" * 1024)],
        ) as inst:
            time_data, voltage_data = inst.channel_1.get_waveform()
            assert len(time_data) == 1024
            assert len(voltage_data) == 1024

    def test_get_mean_voltage(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:MODE SIMPle", None),
             (":MEASure:SIMPle:SOURce CHANnel1", None),
             (":MEASure:SIMPle:ITEM MEAN,ON", None),
             (":MEASure:SIMPle:ITEM? MEAN", "1.234E-01")],
        ) as inst:
            assert inst.channel_1.get_mean_voltage() == 0.1234


class TestSimpleMeasurement:
    """Test simple measurement controls."""

    def test_mode_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:MODE SIMPle", None)],
        ) as inst:
            inst.simple_measurement.mode = "SIMPle"

    def test_mode_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:MODE?", "SIMPle")],
        ) as inst:
            assert inst.simple_measurement.mode == "SIMPle"

    def test_source_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:SIMPle:SOURce CHANnel1", None)],
        ) as inst:
            inst.simple_measurement.source = "CHANnel1"

    def test_source_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:SIMPle:SOURce?", "CHANnel1")],
        ) as inst:
            assert inst.simple_measurement.source == "CHANnel1"

    def test_clear(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:SIMPle:CLEar", None)],
        ) as inst:
            inst.simple_measurement.clear()

    def test_set_item(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:SIMPle:ITEM MEAN,ON", None)],
        ) as inst:
            inst.simple_measurement.set_item("MEAN", "ON")

    def test_get_value(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:SIMPle:ITEM? MEAN", "1.234E-01")],
        ) as inst:
            assert inst.simple_measurement.get_value("MEAN") == 0.1234


class TestAdvancedMeasurement:
    """Test advanced measurement controls."""

    def test_clear(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:CLEar", None)],
        ) as inst:
            inst.advanced_measurement.clear()

    def test_set_line_number(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:LINenumber 5", None)],
        ) as inst:
            inst.advanced_measurement.set_line_number(5)

    def test_configure_parameter_single_source(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:P1:TYPE MEAN", None),
             (":MEASure:ADVanced:P1:SOURce1 CHANnel1", None)],
        ) as inst:
            inst.advanced_measurement.configure_parameter(1, "MEAN", "CHANnel1")

    def test_configure_parameter_dual_source(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:P2:TYPE PHASE", None),
             (":MEASure:ADVanced:P2:SOURce1 CHANnel1", None),
             (":MEASure:ADVanced:P2:SOURce2 CHANnel2", None)],
        ) as inst:
            inst.advanced_measurement.configure_parameter(2, "PHASE", "CHANnel1", "CHANnel2")

    def test_enable_parameter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:P1 ON", None)],
        ) as inst:
            inst.advanced_measurement.enable_parameter(1, "ON")

    def test_get_parameter_value(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:P1:VALue?", "2.345E-01")],
        ) as inst:
            assert inst.advanced_measurement.get_parameter_value(1) == 0.2345

    def test_enable_statistics(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:P1:STATistics ON", None)],
        ) as inst:
            inst.advanced_measurement.enable_statistics(1, "ON")

    def test_reset_statistics(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:STATistics:RESet", None)],
        ) as inst:
            inst.advanced_measurement.reset_statistics()

    def test_set_statistics_style(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:STATistics:STYLe DISPlay", None)],
        ) as inst:
            inst.advanced_measurement.set_statistics_style("DISPlay")


class TestMeasurementGate:
    """Test measurement gate controls."""

    def test_gate_a_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:GATE:GA 1.000000e-03", None)],
        ) as inst:
            inst.measurement_gate.gate_a = 1e-3

    def test_gate_a_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:GATE:GA?", "1.000000E-03")],
        ) as inst:
            assert inst.measurement_gate.gate_a == 1e-3

    def test_gate_b_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:GATE:GB 2.000000e-03", None)],
        ) as inst:
            inst.measurement_gate.gate_b = 2e-3

    def test_gate_b_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:GATE:GB?", "2.000000E-03")],
        ) as inst:
            assert inst.measurement_gate.gate_b == 2e-3


class TestMeasurementThreshold:
    """Test measurement threshold controls."""

    def test_source_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:SOURce CHANnel1", None)],
        ) as inst:
            inst.measurement_threshold.source = "CHANnel1"

    def test_source_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:SOURce?", "CHANnel1")],
        ) as inst:
            assert inst.measurement_threshold.source == "CHANnel1"

    def test_type_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:TYPE ABSolute", None)],
        ) as inst:
            inst.measurement_threshold.type = "ABSolute"

    def test_type_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:TYPE?", "PERCent")],
        ) as inst:
            assert inst.measurement_threshold.type == "PERCent"

    def test_set_absolute_thresholds(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:TYPE ABSolute", None),
             (":MEASure:THReshold:ABSolute:HIGH 0.8", None),
             (":MEASure:THReshold:ABSolute:MIDDle 0.5", None),
             (":MEASure:THReshold:ABSolute:LOW 0.2", None)],
        ) as inst:
            inst.measurement_threshold.set_absolute_thresholds(0.8, 0.5, 0.2)

    def test_set_percent_thresholds(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:TYPE PERCent", None),
             (":MEASure:THReshold:PERCent:HIGH 90", None),
             (":MEASure:THReshold:PERCent:MIDDle 50", None),
             (":MEASure:THReshold:PERCent:LOW 10", None)],
        ) as inst:
            inst.measurement_threshold.set_percent_thresholds(90, 50, 10)


class TestSDS1000xHD:
    """Test main instrument controls."""

    def test_time_scale_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TIMebase:SCALe 1.000000e-03", None)],
        ) as inst:
            inst.time_scale = 1e-3

    def test_time_scale_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TIMebase:SCALe?", "1.000000E-03")],
        ) as inst:
            assert inst.time_scale == 1e-3

    def test_time_delay_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TIMebase:DELay 5.000000e-04", None)],
        ) as inst:
            inst.time_delay = 5e-4

    def test_time_delay_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TIMebase:DELay?", "5.000000E-04")],
        ) as inst:
            assert inst.time_delay == 5e-4

    def test_time_reference_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TIMebase:REFerence CENTer", None)],
        ) as inst:
            inst.time_reference = "CENTer"

    def test_time_reference_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TIMebase:REFerence?", "CENTer")],
        ) as inst:
            assert inst.time_reference == "CENTer"

    def test_acquisition_mode_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE NORMal", None)],
        ) as inst:
            inst.acquisition_mode = "NORMal"

    def test_acquisition_mode_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE?", "NORMal")],
        ) as inst:
            assert inst.acquisition_mode == "NORMal"

    def test_memory_depth_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:MDEPth 140K", None)],
        ) as inst:
            inst.memory_depth = "140K"

    def test_memory_depth_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:MDEPth?", "140K")],
        ) as inst:
            assert inst.memory_depth == "140K"

    # Test acquisition controls
    def test_analog_mode_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:AMODe RTIMe", None)],
        ) as inst:
            inst.analog_mode = "RTIMe"

    def test_analog_mode_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:AMODe?", "RTIMe")],
        ) as inst:
            assert inst.analog_mode == "RTIMe"

    def test_interpolation_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:INTerpolation ON", None)],
        ) as inst:
            inst.interpolation = True

    def test_interpolation_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:INTerpolation?", "OFF")],
        ) as inst:
            assert inst.interpolation is False

    def test_memory_management_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:MMANagement AUTO", None)],
        ) as inst:
            inst.memory_management = "AUTO"

    def test_memory_management_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:MMANagement?", "AUTO")],
        ) as inst:
            assert inst.memory_management == "AUTO"

    def test_legacy_mode_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:MODE COMPatible", None)],
        ) as inst:
            inst.legacy_mode = "COMPatible"

    def test_legacy_mode_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:MODE?", "COMPatible")],
        ) as inst:
            assert inst.legacy_mode == "COMPatible"

    def test_num_acquisitions_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:NUMAcq 100", None)],
        ) as inst:
            inst.num_acquisitions = 100

    def test_num_acquisitions_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:NUMAcq?", "100")],
        ) as inst:
            assert inst.num_acquisitions == 100

    def test_points_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:POINts 1000", None)],
        ) as inst:
            inst.points = 1000

    def test_points_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:POINts?", "1000")],
        ) as inst:
            assert inst.points == 1000

    def test_resolution_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:RESolution 12", None)],
        ) as inst:
            inst.resolution = 12

    def test_resolution_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:RESolution?", "12")],
        ) as inst:
            assert inst.resolution == 12

    def test_sequence_mode_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:SEQuence ON", None)],
        ) as inst:
            inst.sequence_mode = True

    def test_sequence_mode_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:SEQuence?", "ON")],
        ) as inst:
            assert inst.sequence_mode is True

    def test_sequence_count_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:SEQuence:COUNt 10", None)],
        ) as inst:
            inst.sequence_count = 10

    def test_sequence_count_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:SEQuence:COUNt?", "10")],
        ) as inst:
            assert inst.sequence_count == 10

    def test_average_number_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:AVERages 16", None)],
        ) as inst:
            inst.average_number = 16

    def test_average_number_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:AVERages?", "16")],
        ) as inst:
            assert inst.average_number == 16

    def test_sample_rate_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:SRATe?", "1.000000E+09")],
        ) as inst:
            assert inst.sample_rate == 1e9

    # Test high-level convenience methods
    def test_configure_acquisition(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE NORMal", None),
             (":ACQuire:MDEPth 140K", None),
             (":ACQuire:AMODe RTIMe", None)],
        ) as inst:
            inst.configure_acquisition(acq_type="NORMal", memory_depth="140K", analog_mode="RTIMe")

    def test_setup_sequence_acquisition(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:SEQuence ON", None),
             (":ACQuire:SEQuence:COUNt 5", None)],
        ) as inst:
            inst.setup_sequence_acquisition(count=5)

    def test_setup_averaging(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE AVERages", None),
             (":ACQuire:AVERages 32", None)],
        ) as inst:
            inst.setup_averaging(count=32)

    def test_setup_high_resolution(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE HRESolution", None),
             (":ACQuire:RESolution 12", None)],
        ) as inst:
            inst.setup_high_resolution(bits=12)

    def test_setup_peak_detect(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE PEAK", None)],
        ) as inst:
            inst.setup_peak_detect()

    def test_clear_sweeps(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:CSWeep", None)],
        ) as inst:
            inst.clear_sweeps()

    def test_get_acquisition_status(self):
        with expected_protocol(
            SDS1000xHD,
            [(":ACQuire:TYPE?", "NORMal"),
             (":ACQuire:MDEPth?", "140K"),
             (":ACQuire:SRATe?", "1.000000E+09"),
             (":ACQuire:POINts?", "1400")],
        ) as inst:
            status = inst.get_acquisition_status()
            assert status["type"] == "NORMal"
            assert status["memory_depth"] == "140K"
            assert status["sample_rate"] == 1e9
            assert status["points"] == 1400

    def test_get_all_measurements(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:MODE SIMPle", None),
             (":MEASure:SIMPle:SOURce CHANnel1", None),
             (":MEASure:SIMPle:ITEM MEAN,ON", None),
             (":MEASure:SIMPle:ITEM? MEAN", "1.234E-01"),
             (":MEASure:SIMPle:ITEM PKPK,ON", None),
             (":MEASure:SIMPle:ITEM? PKPK", "2.345E-01"),
             (":MEASure:SIMPle:ITEM RMS,ON", None),
             (":MEASure:SIMPle:ITEM? RMS", "3.456E-01")],
        ) as inst:
            measurements = inst.get_all_measurements("CHANnel1", ["MEAN", "PKPK", "RMS"])
            assert measurements["MEAN"] == 0.1234
            assert measurements["PKPK"] == 0.2345
            assert measurements["RMS"] == 0.3456

    def test_setup_advanced_measurements(self):
        configs = [
            {'position': 1, 'type': 'MEAN', 'source1': 'CHANnel1'},
            {'position': 2, 'type': 'PHASE', 'source1': 'CHANnel1', 'source2': 'CHANnel2'},
        ]
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:MODE ADVanced", None),
             (":MEASure:ADVanced:CLEar", None),
             (":MEASure:ADVanced:P1:TYPE MEAN", None),
             (":MEASure:ADVanced:P1:SOURce1 CHANnel1", None),
             (":MEASure:ADVanced:P1 ON", None),
             (":MEASure:ADVanced:P2:TYPE PHASE", None),
             (":MEASure:ADVanced:P2:SOURce1 CHANnel1", None),
             (":MEASure:ADVanced:P2:SOURce2 CHANnel2", None),
             (":MEASure:ADVanced:P2 ON", None)],
        ) as inst:
            inst.setup_advanced_measurements(configs)

    def test_get_advanced_measurement_values(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:ADVanced:P1:VALue?", "1.234E-01"),
             (":MEASure:ADVanced:P2:VALue?", "2.345E-01")],
        ) as inst:
            values = inst.get_advanced_measurement_values([1, 2])
            assert values == [0.1234, 0.2345]

    def test_setup_measurement_gate(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:GATE:GA 1.000000e-03", None),
             (":MEASure:GATE:GB 2.000000e-03", None)],
        ) as inst:
            inst.setup_measurement_gate(gate_a=1e-3, gate_b=2e-3)

    def test_setup_measurement_thresholds_absolute(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:SOURce CHANnel1", None),
             (":MEASure:THReshold:TYPE ABSolute", None),
             (":MEASure:THReshold:ABSolute:HIGH 0.8", None),
             (":MEASure:THReshold:ABSolute:MIDDle 0.5", None),
             (":MEASure:THReshold:ABSolute:LOW 0.2", None)],
        ) as inst:
            inst.setup_measurement_thresholds("CHANnel1", "ABSolute", high=0.8, middle=0.5, low=0.2)

    def test_setup_measurement_thresholds_percent(self):
        with expected_protocol(
            SDS1000xHD,
            [(":MEASure:THReshold:SOURce CHANnel1", None),
             (":MEASure:THReshold:TYPE PERCent", None),
             (":MEASure:THReshold:PERCent:HIGH 90", None),
             (":MEASure:THReshold:PERCent:MIDDle 50", None),
             (":MEASure:THReshold:PERCent:LOW 10", None)],
        ) as inst:
            inst.setup_measurement_thresholds("CHANnel1", "PERCent", high=90, middle=50, low=10)

    # Test trigger controls
    def test_trigger_source_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:SOURce CHANnel1", None)],
        ) as inst:
            inst.trigger_source = "CHANnel1"

    def test_trigger_source_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:SOURce?", "CHANnel1")],
        ) as inst:
            assert inst.trigger_source == "CHANnel1"

    def test_trigger_mode_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:MODE NORMal", None)],
        ) as inst:
            inst.trigger_mode = "NORMal"

    def test_trigger_mode_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:MODE?", "NORMal")],
        ) as inst:
            assert inst.trigger_mode == "NORMal"

    def test_trigger_level_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:LEVel 0.500000", None)],
        ) as inst:
            inst.trigger_level = 0.5

    def test_trigger_level_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:LEVel?", "5.000000E-01")],
        ) as inst:
            assert inst.trigger_level == 0.5

    def test_trigger_slope_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:SLOPe POSitive", None)],
        ) as inst:
            inst.trigger_slope = "POSitive"

    def test_trigger_slope_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:SLOPe?", "POSitive")],
        ) as inst:
            assert inst.trigger_slope == "POSitive"

    def test_trigger_coupling_setter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:COUPling DC", None)],
        ) as inst:
            inst.trigger_coupling = "DC"

    def test_trigger_coupling_getter(self):
        with expected_protocol(
            SDS1000xHD,
            [(":TRIGger:COUPling?", "DC")],
        ) as inst:
            assert inst.trigger_coupling == "DC"

    # Test parametric tests for multiple values
    @pytest.mark.parametrize("comm_pairs, value", [
        ([(":CHANnel1:SCALe 1.000e-03", None)], 0.001),
        ([(":CHANnel1:SCALe 1.000e-01", None)], 0.1),
        ([(":CHANnel1:SCALe 1.000e+00", None)], 1.0),
    ])
    def test_scale_setter_parametric(self, comm_pairs, value):
        with expected_protocol(
            SDS1000xHD,
            comm_pairs,
        ) as inst:
            inst.channel_1.scale = value

    @pytest.mark.parametrize("comm_pairs, value", [
        ([(":CHANnel1:COUPling DC", None)], "DC"),
        ([(":CHANnel1:COUPling AC", None)], "AC"),
        ([(":CHANnel1:COUPling GND", None)], "GND"),
    ])
    def test_coupling_setter_parametric(self, comm_pairs, value):
        with expected_protocol(
            SDS1000xHD,
            comm_pairs,
        ) as inst:
            inst.channel_1.coupling = value

    @pytest.mark.parametrize(
        "comm_pairs, value",
        [
            ([(":ACQuire:TYPE NORMal", None)], "NORMal"),
            ([(":ACQuire:TYPE AVERages", None)], "AVERages"),
            ([(":ACQuire:TYPE PEAK", None)], "PEAK"),
            ([(":ACQuire:TYPE HRESolution", None)], "HRESolution"),
        ]
    )
    def test_acquisition_mode_setter_parametric(self, comm_pairs, value):
        with expected_protocol(
            SDS1000xHD,
            comm_pairs,
        ) as inst:
            inst.acquisition_mode = value