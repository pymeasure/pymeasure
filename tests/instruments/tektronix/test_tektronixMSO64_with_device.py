import pytest
from time import sleep
from pyvisa.errors import VisaIOError
from pymeasure.instruments.tektronix.tektronixMsoSeries import TektronixMSO64


class TestTektronixMSO64:
    """
        Unit tests for TektronixOscilloscope class.

        This test suite, needs the following setup to work properly:
            - A Tektronix MSO58 device should be connected to the computer;
            - The device's address must be set in the RESOURCE constant;
            - A TPP100 probe on Channel 1 to 8 must be connected.
        """

    #########################
    # PARAMETRIZATION CASES #
    #########################

    BOOLEANS = [False, True]
    BANDWIDTH_LIMITS = [20.0000E+6, 250.0000E+6, 1.0000E+9]
    CHANNEL_COUPLINGS = ["ac", "dc"]
    ACQUISITION_MODES = ["SAMPLE", "AVERAGE", "PEAKDETECT", "ENVELOPE"]
    TRIGGER_TYPES = ["EDGE","WIDTH","TIMEOUT","RUNT","WINDOW","LOGIC","SETHOLD","TRANSITION"]
    TRIGGER_LEVELS = [100.000E-3, 200.000E-3, 300.000E-3]
    TRIGGER_SLOPES = {"negative": "FALL", "positive": "RISE", "either": "EITHER"}
    TRIGGER_SOURCE = ['CH1', 'CH2', 'CH3', 'CH4']
    ACQUISITION_AVERAGE = [4, 16, 32, 64, 128, 256]
    ACQUISITION_STATE = ["RUN", "STOP"]
    CHANNELS = [1, 2, 3, 4]
    MEAS_SLOTS = {1: "PK2PK", 2: "PWIDTH", 3: "NWIDTH", 4: "FREQUENCY"}
    EXPECTED_MEAS_VALUES = {'PK2PK': 2.5, 'PWIDTH': 500.0000E-6, 'NWIDTH': 500.0000E-6,
                            'FREQUENCY': 1.0000E3}
    AFG_FUNCTIONS = ["SINE", "SQUARE", "PULSE", "RAMP", "NOISE", "DC", "SINC", "GAUSSIAN",
                     "LORENTZ", "ERISE", "EDECAY", "HAVERSINE", "CARDIAC", "ARBITRARY"]
    AFG_OUTPUT_MODES = ["OFF", "CONTINUOUS", "BURST"]
    AFG_OUTPUT_IMPEDANCE = ["FIFTY", "HIGHZ"]
    GATING_TYPE = ["NONE", "SCREEN", "CURSOR", "LOGIC", "SEARCH", "TIME"]

    ############
    # FIXTURES #
    ############

    @pytest.fixture(scope="module")
    def instrument(self, connected_device_address):
        return TektronixMSO64(connected_device_address)

    @pytest.fixture
    def resetted_instrument(self, instrument):
        instrument.reset()
        return instrument

    @pytest.fixture
    def autoscaled_instrument(self, instrument):
        instrument.reset()
        sleep(2)
        instrument.autoscale()
        sleep(2)
        return instrument

    @pytest.fixture
    def afg_instrument(self, instrument):
        instrument.reset()
        instrument.write("LICENSE:VALIDATE? \"SUP5-AFG\"")
        if instrument.read().strip('\n') == "0":
            pytest.skip("AFG license not installed")
        else:
            return instrument

    #########
    # TESTS #
    #########

    # noinspection PyTypeChecker
    def test_instrument_connection(self):
        bad_resource = "USB0::10893::45848::MY12345678::0::INSTR"
        # The pure python VISA library (pyvisa-py) raises a ValueError while the
        # PyVISA library raises a VisaIOError.
        with pytest.raises((ValueError, VisaIOError)):
            TektronixMSO64(bad_resource)

    # Channel
    def test_ch_current_configuration(self, resetted_instrument):
        resetted_instrument.ch_1.offset = 0
        resetted_instrument.ch_1.trigger_level = 0
        expected = {
            "channel": 1,
            "bandwidth_limit": 1.0E+9,
            "coupling": "dc",
            "offset": 0.0,
            "display": True,
            "unit": "V",
            "label": '\"\"',
            "volts_div": 100.0000E-3,
            "trigger_level": 0.0,
        }
        actual = resetted_instrument.channels[1].current_configuration
        assert actual == expected

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_display(self, instrument, ch_number, case):
        instrument.ch(ch_number).display = case
        assert instrument.channels[ch_number].display == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BANDWIDTH_LIMITS)
    def test_ch_bwlimit(self, instrument, ch_number, case):
        instrument.ch(ch_number).bwlimit = case
        assert instrument.channels[ch_number].bwlimit == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", CHANNEL_COUPLINGS)
    def test_ch_coupling(self, instrument, ch_number, case):
        instrument.ch(ch_number).coupling = case
        assert instrument.channels[ch_number].coupling == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_offset(self, instrument, ch_number):
        instrument.ch(ch_number).offset = 1
        assert instrument.channels[ch_number].offset == 1

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_probe_ext_attenuation(self, instrument, ch_number):
        instrument.ch(ch_number).probe_ext_attenuation = 2
        assert instrument.channels[ch_number].probe_ext_attenuation == 2

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_scale(self, instrument, ch_number):
        instrument.ch(ch_number).scale = 1
        assert instrument.channels[ch_number].scale == 1

    # Trigger
    def test_ch_trigger_level(self, resetted_instrument):
        for case in self.TRIGGER_LEVELS:
            resetted_instrument.ch_1.trigger_level = case
            assert resetted_instrument.ch_1.trigger_level == case

    @pytest.mark.parametrize("case", TRIGGER_TYPES)
    def test_trigger_type(self, case, instrument):
        instrument.trigger_type = case
        assert instrument.trigger_type == case

    @pytest.mark.parametrize("case", TRIGGER_SOURCE)
    def test_trigger_edge_source(self, case, instrument):
        instrument.trigger_edge_source = case
        assert instrument.trigger_edge_source == case

    @pytest.mark.parametrize("case", TRIGGER_SLOPES)
    def test_trigger_edge_slopes(self, case, instrument):
        instrument.trigger_edge_slope = case
        assert instrument.trigger_edge_slope == case
        with pytest.raises(ValueError):
            instrument.trigger_edge_slope = "rising"

    # Timebase
    def test_timebase_scale(self, resetted_instrument):
        resetted_instrument.timebase_scale = 1e-3
        assert resetted_instrument.timebase_scale == 1e-3
        with pytest.raises(ValueError):
            resetted_instrument.timebase_scale = 1500

    def test_timebase_offset(self, instrument):
        instrument.timebase_offset = 10
        assert instrument.timebase_offset == 10
        with pytest.raises(ValueError):
            instrument.timebase_offset = 110

    def test_timebase_setup(self, resetted_instrument):
        expected = resetted_instrument.timebase
        resetted_instrument.timebase_setup(scale=40.0E-09, offset=50.0)
        assert resetted_instrument.timebase == expected

    # Acquisition
    @pytest.mark.parametrize("case", ACQUISITION_MODES)
    def test_acquisition_mode(self, instrument, case):
        instrument.acquisition_mode = case
        assert instrument.acquisition_mode == case
        with pytest.raises(ValueError):
            instrument.acquisition_mode = "NONE"

    @pytest.mark.parametrize("case", ACQUISITION_AVERAGE)
    def test_acquisition_average(self, instrument, case):
        instrument.acquisition_average = case
        assert instrument.acquisition_average == case
        with pytest.raises(ValueError):
            instrument.acquisition_average = 1

    @pytest.mark.parametrize("case", ACQUISITION_STATE)
    def test_acquisition_state(self, instrument, case):
        instrument.acquisition_state = case
        assert instrument.acquisition_state == case
        with pytest.raises(ValueError):
            instrument.acquisition_state = 1

    def test_acquisition_single(self, resetted_instrument):
        resetted_instrument.single()
        sleep(1)
        assert resetted_instrument.acquisition_state == 'STOP'

    # Data
    def test_download_image(self, resetted_instrument):
        img = resetted_instrument.download_image()
        assert type(img) is bytearray
        if not img:
            print("empty image")

    # Measurement
    @pytest.mark.skip(reason="connect CH1 probe to ground and probe compensation connectors")
    def test_measurement_configure(self, autoscaled_instrument):
        for (slot, meas_type), (meas, value) in zip(self.MEAS_SLOTS.items(),
                                                    self.EXPECTED_MEAS_VALUES.items()):
            autoscaled_instrument.measurement_configure(slot, "CH1", "CH1", meas_type)
            sleep(0.5)
            assert autoscaled_instrument.measurement_result_curracq_mean(slot) ==\
                   pytest.approx(value, rel=0.3)

    @pytest.mark.parametrize("case", GATING_TYPE)
    def test_measurement_gating(self, case, autoscaled_instrument):
        with pytest.raises(ValueError):
            autoscaled_instrument.measurement_gating_type = "abdc"
        autoscaled_instrument.measurement_gating_type = case
        assert autoscaled_instrument.measurement_gating_type == case

    # AFG
    @pytest.mark.parametrize("case", AFG_FUNCTIONS)
    def test_afg_function(self, case, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_function = "NONE"
        afg_instrument.afg_function = case
        assert afg_instrument.afg_function == case

    @pytest.mark.parametrize("case", AFG_OUTPUT_MODES)
    def test_afg_output_mode(self, case, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_output_mode = "NONE"
        afg_instrument.afg_output_mode = case
        assert afg_instrument.afg_output_mode == case

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_afg_output_state(self, case, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_output_state = "NONE"
        afg_instrument.afg_output_state = case
        assert afg_instrument.afg_output_state == case

    @pytest.mark.parametrize("case", AFG_OUTPUT_IMPEDANCE)
    def test_afg_output_impedance(self, case, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_output_load_impedance = "50OMHS"
        afg_instrument.afg_output_load_impedance = case
        assert afg_instrument.afg_output_load_impedance == case

    @pytest.mark.parametrize("case", BOOLEANS)
    def test_afg_noise_state(self, case, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_noise_state = "NONE"
        afg_instrument.afg_noise_state = case
        assert afg_instrument.afg_noise_state == case

    def test_afg_noise_level(self, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_noise_level = 10.1
        afg_instrument.afg_noise_level = 11
        assert afg_instrument.afg_noise_level == 11

    def test_afg_ramp_symetry(self, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_rampsymetry = 10.01
        afg_instrument.afg_rampsymetry = 10.1
        assert afg_instrument.afg_rampsymetry == 10.1

    def test_afg_square_duty(self, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_squareduty = 10.01
        afg_instrument.afg_squareduty = 10.1
        assert afg_instrument.afg_squareduty == 10.1

    def test_afg_frequency(self, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_frequency = 100.000E6
        afg_instrument.afg_frequency = 1000
        assert afg_instrument.afg_frequency == 1.000E3

    def test_afg_period(self, afg_instrument):
        with pytest.raises(ValueError):
            afg_instrument.afg_period = 10.000E-9
        afg_instrument.afg_period = 2.0e-8
        assert afg_instrument.afg_period == 2.0E-8

    def test_afg_amplitude(self, afg_instrument):
        afg_instrument.afg_amplitude = 100.0000E-3
        assert afg_instrument.afg_amplitude == 100.0000E-3

    def test_afg_offset(self, afg_instrument):
        afg_instrument.afg_offset = 100.0000E-3
        assert afg_instrument.afg_offset == 100.0000E-3

    def test_afg_lowlvl(self, afg_instrument):
        afg_instrument.afg_lowlvl = 100.0000E-3
        assert afg_instrument.afg_lowlvl == 100.0000E-3

    def test_afg_highlvl(self, afg_instrument):
        afg_instrument.afg_highlvl = 100.0000E-3
        assert afg_instrument.afg_highlvl == 100.0000E-3

    def test_afg_pulsewidth(self, afg_instrument):
        afg_instrument.afg_pulsewidth = 1.0E-6
        assert afg_instrument.afg_pulsewidth == 1.0E-6
