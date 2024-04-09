from time import sleep
import pytest
from pyvisa.errors import VisaIOError
from pymeasure.instruments.tektronix.tektronixMsoSeries import TektronixMSO58,\
    TektronixMsoScopeMathChannel


class TestTektronixMSO58:
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
    TRIGGER_TYPES = ["edge", "pulse", "timeout", "runt", "window", "logic", "sethold",
                     "transition"]
    TRIGGER_LEVELS = [100.000E-3, 200.000E-3, 300.000E-3]
    TRIGGER_SLOPES = {"negative": "FALL", "positive": "RISE", "either": "EITHER"}
    TRIGGER_SOURCE = ['channel1', 'channel2', 'channel3', 'channel4', 'channel5', 'channel6', 'channel7', 'channel8']
    ACQUISITION_AVERAGE = [4, 16, 32, 64, 128, 256]
    ACQUISITION_STATE = ["RUN", "STOP"]
    CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    MEAS_SLOTS = {1: "pkpk", 2: "pwidth", 3: "nwidth", 4: "frequency"}
    MEASURABLE_PARAMETERS = ["amplitude", "base", "maximum", "mean", "minimum", "pkpk",
                             "rms", "top", "acrms", "area", "dutycylce", "delay",
                             "falltime", "risetime", "frequency", "period", "pwidth", "nwidth",
                             "skew", "phase", "holdtime", "setuptime", "burstwidth", "datarate",
                             "fallslewrate", "high", "hightime", "low", "lowtime",
                             "nduty", "novershoot", "nperiod", "phasenoise",
                             "povershoot", "tie", "timeoutsidelevel",
                             "timetomax", "timetomin", "unitinterval",
                             ]

    _MEASURABLE_PARAMETERS = {"amplitude": "AMPLITUDE", "base": "BASE", "maximum": "MAXIMUM",
                              "mean": "MEAN", "minimum": "MINIMUM", "pkpk": "PK2PK",
                              "rms": "RMS", "top": "TOP", "acrms": "ACRMS", "area": "AREA",
                              "dutycylce": "PDUTY", "delay": "DELAY", "falltime": "FALLTIME",
                              "risetime": "RISETIME", "frequency": "FREQUENCY", "period": "PERIOD",
                              "pwidth": "PWIDTH", "nwidth": "NWIDTH", "skew": "SKEW",
                              "phase": "PHASE", "holdtime": "HOLD", "setuptime": "SETUP",
                              "burstwidth": "BURSTWIDTH", "datarate": "DATARATE",
                              "fallslewrate": "FALLSLEWRATE", "high": "HIGH",
                              "hightime": "HIGHTIME", "low": "LOW", "lowtime": "LOWTIME",
                              "nduty": "NDUTY", "novershoot": "NOVERSHOOT",
                              "nperiod": "NPERIOD", "phasenoise": "PHASENOISE",
                              "povershoot": "POVERSHOOT", "tie": "TIE",
                              "timeoutsidelevel": "TIMEOUTSIDELEVEL", "timetomax": "TIMETOMAX",
                              "timetomin": "TIMETOMIN", "unitinterval": "UNITINTERVAL",
                              }

    EXPECTED_MEAS_VALUES = {'pkpk': 2.5, 'pwidth': 500.0000E-6, 'nwidth': 500.0000E-6,
                            'frequency': 1.0000E3}
    AFG_FUNCTIONS = ["SINE", "SQUARE", "PULSE", "RAMP", "NOISE", "DC", "SINC", "GAUSSIAN",
                     "LORENTZ", "ERISE", "EDECAY", "HAVERSINE", "CARDIAC", "ARBITRARY"]
    AFG_OUTPUT_MODES = ["OFF", "CONTINUOUS", "BURST"]
    AFG_OUTPUT_IMPEDANCE = ["FIFTY", "HIGHZ"]
    GATING_TYPE = ["NONE", "SCREEN", "CURSOR", "LOGIC", "SEARCH", "TIME"]
    MINIMUM_SAMPLE_RATE = ["AUTOMATIC", "3.125GS", "1.5625GS", "1.25GS", "625M", "312.5M",
                           "250M", "125M", "62.5M", "31.25M", "25M", "12.5M", "6.25M", "5M",
                           "3.125M", "2.5M", "1.25M", "1M", "625k", "500k", "312.5k", "250k",
                           "125k", "100k", "62.5k", "50k", "31.25k", "25k", "12.5k", "10k",
                           "6.25k", "5k", "3.125k", "2.5k", "1.25k", "1k", "625", "500",
                           "312.5", "250", "125", "100", "62.5", "50", "31.25", "25", "12.5",
                           "10", "6.25", "5", "3.125", "2.5", "1.5625"]
    MATH_BASIC_OPERATIONS = ['ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE']
    MATH_FFT_OUTPUT_TYPE = ["MAGNITUDE", "PHASE"]
    MATH_FFT_WINDOW_TYPE = ["RECTANGULAR", "HAMMING", "HANNING", "BLACKMANHARRIS",
                            "KAISERBESSEL", "GAUSSIAN", "FLATTOP2", "TEKEXPONENTIAL"]

    ############
    # FIXTURES #
    ############

    @pytest.fixture(scope="module")
    def instrument(self, connected_device_address):
        return TektronixMSO58(connected_device_address)

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
            TektronixMSO58(bad_resource)

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

    @pytest.mark.parametrize("case", TRIGGER_SOURCE)
    def test_trigger_width_source(self, case, instrument):
        instrument.trigger_width_source = case
        assert instrument.trigger_width_source == case

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

    @pytest.mark.parametrize("case", MINIMUM_SAMPLE_RATE)
    def test_horizontal_minsamplerate(self, instrument, case):
        instrument.horizontal_minsamplerate_value = case
        assert instrument.horizontal_minsamplerate_value == case

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
    @pytest.mark.parametrize("case", MEASURABLE_PARAMETERS)
    def test_measurement_add(self, instrument, case):
        instrument.measurement_clear_all()
        instrument.measurement_add = case
        assert instrument.ask("MEASUrement:MEAS1:TYPe?").strip() == self._MEASURABLE_PARAMETERS[case]

    # @pytest.mark.skip(reason="connect CH1 probe to ground and probe compensation connectors")
    def test_measurement_configure(self, autoscaled_instrument):
        for (slot, meas_type), (meas, value) in \
                zip(self.MEAS_SLOTS.items(), self.EXPECTED_MEAS_VALUES.items()):
            autoscaled_instrument.measurement_configure(slot, "channel1", "channel1", meas_type)
            sleep(0.5)
            assert autoscaled_instrument.measurement_result_curracq_mean(slot) ==\
                   pytest.approx(value, rel=0.3)

    @pytest.mark.parametrize("case", GATING_TYPE)
    def test_measurement_gating(self, case, autoscaled_instrument):
        with pytest.raises(ValueError):
            autoscaled_instrument.measurement_gating_type = "abdc"
        autoscaled_instrument.measurement_gating_type = case
        assert autoscaled_instrument.measurement_gating_type == case

    # Math Channel
    @pytest.mark.parametrize('operation', MATH_BASIC_OPERATIONS)
    def test_math_basic(self, instrument, operation):
        instrument.add_new_math(1)
        assert isinstance(instrument.math_1, TektronixMsoScopeMathChannel)
        instrument.maths[1].math_type = "BASIC"
        assert instrument.maths[1].math_type == "BASIC"
        instrument.math_1.math_source1 = "CH1"
        assert instrument.math_1.math_source1 == "CH1"
        instrument.math_1.math_source2 = "CH2"
        assert instrument.math_1.math_source2 == "CH2"
        instrument.math_1.math_basic_function = operation
        assert instrument.math_1.math_basic_function == operation

    @pytest.mark.parametrize('output_type', MATH_FFT_OUTPUT_TYPE)
    @pytest.mark.parametrize('window_type', MATH_FFT_WINDOW_TYPE)
    def test_math_fft(self, instrument, output_type, window_type):
        instrument.add_new_math(1)
        assert isinstance(instrument.math_1, TektronixMsoScopeMathChannel)
        instrument.maths[1].math_type = "FFT"
        assert instrument.math_1.math_type == "FFT"
        instrument.math_1.math_source1 = "CH1"
        assert instrument.math_1.math_source1 == "CH1"
        instrument.math_1.math_average_mode = True
        assert instrument.math_1.math_average_mode == 1
        instrument.math_1.math_average_sweeps = 10
        assert instrument.math_1.math_average_sweeps == 10
        instrument.math_1.math_FFT_horizontal_unit = "LOG"
        assert instrument.math_1.math_FFT_horizontal_unit == "LOG"
        instrument.math_1.math_FFT_vertical_unit = "LINEAR"
        assert instrument.math_1.math_FFT_vertical_unit == "LINEAR"
        instrument.math_1.math_FFT_view_autoscale = True
        assert instrument.math_1.math_FFT_view_autoscale == 1
        instrument.math_1.math_FFT_output_type = output_type
        assert instrument.math_1.math_FFT_output_type == output_type
        instrument.math_1.math_FFT_window_type = window_type
        assert instrument.math_1.math_FFT_window_type == window_type
        # instrument.math_delete_all()

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