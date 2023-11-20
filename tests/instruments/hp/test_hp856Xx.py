#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from datetime import datetime

import pytest

from pymeasure.test import expected_protocol

from pymeasure.instruments.hp import HP8560A, HP8561B
from pymeasure.instruments.hp.hp856Xx import Trace, MixerMode, CouplingMode, DemodulationMode, \
    DetectionModes, AmplitudeUnits, HP856Xx, ErrorCode, FrequencyReference, PeakSearchMode, \
    StatusRegister, SourceLevelingControlMode, SweepCoupleMode, SweepOut, TraceDataFormat, \
    TriggerMode, WindowType


class TestHP856Xx:
    def test_id(self):
        with expected_protocol(
                HP856Xx,
                [("ID?", "HP8560A,002,H03")],
        ) as instr:
            assert instr.id == "HP8560A,002,H03"

    def test_attenuation(self):
        with expected_protocol(
                HP856Xx,
                [("AT 70", None),
                 ("AT?", "70")],
        ) as instr:
            # test set and get of attenuation as integer
            instr.attenuation = 70
            assert instr.attenuation == 70

    def test_attenuation_string_parameters(self):
        with expected_protocol(
                HP856Xx,
                [("AT AUTO", None),
                 ("AT?", "20"), ],
        ) as instr:
            # test string parameters
            instr.attenuation = "AUTO"
            assert instr.attenuation == 20

    def test_attenuation_truncation(self):
        with expected_protocol(
                HP856Xx,
                [("AT 20", None),
                 ("AT?", "20")],
        ) as instr:
            instr.attenuation = 16
            assert instr.attenuation == 20

    @pytest.mark.parametrize("amplitude_unit", [e for e in AmplitudeUnits])
    def test_amplitude_units(self, amplitude_unit):
        with expected_protocol(
                HP856Xx,
                [("AUNITS " + amplitude_unit, None),
                 ("AUNITS?", amplitude_unit)],
        ) as instr:
            instr.amplitude_unit = amplitude_unit
            assert instr.amplitude_unit == amplitude_unit

    @pytest.mark.parametrize(
        "function, command",
        [
            ("set_auto_couple", "AUTOCPL"),
            ("exchange_traces", "AXB"),
            ("subtract_display_line_from_trace_b", "BML"),
            ("set_continuous_sweep", "CONTS"),
            ("set_full_span", "FS"),
            ("set_linear_scale", "LN"),
            ("set_marker_to_center_frequency", "MKCF"),
            ("set_marker_minimum", "MKMIN"),
            ("set_marker_to_reference_level", "MKRL"),
            ("set_marker_delta_to_span", "MKSP"),
            ("set_marker_to_center_frequency_step_size", "MKSS"),
            ("preset", "IP"),
            ("recall_open_short_average", "RCLOSCAL"),
            ("recall_thru", "RCLTHRU"),
            ("sweep_single", "SNGLS"),
            ("store_open", "STOREOPEN"),
            ("store_short", "STORESHORT"),
            ("store_thru", "STORETHRU"),
            ("adjust_all", "ADJALL"),
            ("set_crt_adjustment_pattern", "ADJCRT"),
            ("trigger_sweep", "TS"),
        ]
    )
    def test_primitive_commands(self, command, function):
        """
        Tests primitive commands which have no parameter or query derivat
        """
        with expected_protocol(
                HP856Xx,
                [(command, None)]
        ) as instr:
            getattr(instr, function)()

    @pytest.mark.parametrize("trace", [e for e in Trace])
    def test_blank_trace(self, trace):
        with expected_protocol(
                HP856Xx,
                [("BLANK " + trace, None)]
        ) as instr:
            instr.blank_trace(trace)

    def test_blank_trace_exceptions(self):
        with expected_protocol(
                HP856Xx,
                []
        ) as instr:
            with pytest.raises(ValueError):
                instr.blank_trace("TEST")

            with pytest.raises(TypeError):
                instr.blank_trace(0)

    @pytest.mark.parametrize("function, command", [
        ("start_frequency", "FA"),
        ("center_frequency", "CF"),
        ("stop_frequency", "FB"),
        ("frequency_offset", "FOFFSET"),
        ("span", "SP")
    ])
    @pytest.mark.parametrize("hp_derivat, max_freq", [(HP8560A, 2.9e9), (HP8561B, 6.5e9)])
    def test_frequencies(self, function, command, hp_derivat, max_freq):
        with expected_protocol(
                hp_derivat,
                [("%s %.11E Hz" % (command, max_freq), None),
                 ("%s?" % command, '%.11E' % max_freq)]
        ) as instr:
            setattr(instr, function, max_freq)
            assert getattr(instr, function) == max_freq

    @pytest.mark.parametrize("trace", [e for e in Trace])
    def test_clear_write_trace(self, trace):
        with expected_protocol(
                HP856Xx,
                [("CLRW " + trace, None)]
        ) as instr:
            instr.clear_write_trace(trace)

    def test_clear_write_trace_exceptions(self):
        with expected_protocol(
                HP856Xx,
                []
        ) as instr:
            with pytest.raises(ValueError):
                instr.clear_write_trace("TEST")

            with pytest.raises(TypeError):
                instr.clear_write_trace(0)

    @pytest.mark.parametrize("coupling", [e for e in CouplingMode])
    def test_coupling(self, coupling):
        with expected_protocol(
                HP856Xx,
                [("COUPLE " + coupling, None),
                 ("COUPLE?", coupling)]
        ) as instr:
            instr.coupling = coupling
            assert instr.coupling == coupling

    @pytest.mark.parametrize("demod_mode", [e for e in DemodulationMode])
    def test_demodulation_mode(self, demod_mode):
        with expected_protocol(
                HP856Xx,
                [("DEMOD " + demod_mode, None),
                 ("DEMOD?", demod_mode)]
        ) as instr:
            instr.demodulation_mode = demod_mode
            assert instr.demodulation_mode == demod_mode

    @pytest.mark.parametrize("on_off, boole", [("1", True), ("0", False)])
    def test_demodulation_agc_enabled(self, on_off, boole):
        with expected_protocol(
                HP856Xx,
                [("DEMODAGC " + on_off, None),
                 ("DEMODAGC?", on_off)]
        ) as instr:
            instr.demodulation_agc_enabled = boole
            assert instr.demodulation_agc_enabled == boole

    def test_demodulation_time(self):
        with expected_protocol(
                HP856Xx,
                [("DEMODT 1.02000000000E+01", None),
                 ("DEMODT?", "1.03000000000E+01")]
        ) as instr:
            instr.demodulation_time = 10.2
            assert instr.demodulation_time == 10.3

    @pytest.mark.parametrize("detector_mode", [e for e in DetectionModes])
    def test_detector_mode(self, detector_mode):
        with expected_protocol(
                HP856Xx,
                [("DET " + detector_mode, None),
                 ("DET?", detector_mode)]
        ) as instr:
            instr.detector_mode = detector_mode
            assert instr.detector_mode == detector_mode

    @pytest.mark.parametrize("string_params", ["ON", "OFF"])
    def test_display_line_enabled(self, string_params):
        with expected_protocol(
                HP856Xx,
                [
                    ("DL " + string_params, None)
                ]
        ) as instr:
            instr.display_line_enabled = True if string_params == "ON" else False

    def test_check_done(self):
        with expected_protocol(
                HP856Xx,
                [("DONE?", "1")],
        ) as instr:
            instr.check_done()

    def test_errors(self):
        with expected_protocol(
                HP856Xx,
                [("ERR?", "112,101,111")],
        ) as instr:
            assert instr.errors == [ErrorCode(112), ErrorCode(101), ErrorCode(111)]

    def test_elapsed_time(self):
        with expected_protocol(
                HP856Xx,
                [("EL?", "1800")],
        ) as instr:
            assert instr.elapsed_time == 1800

    @pytest.mark.parametrize(
        "function, command",
        [
            ("sampling_frequency", "SMP"),
            ("lo_frequency", "LO"),
            ("mroll_frequency", "MROLL"),
            ("oroll_frequency", "OROLL"),
            ("xroll_frequency", "XROLL")
        ]
    )
    def test_fdiag_frequencies(self, function, command):
        with expected_protocol(
                HP856Xx,
                [("FDIAG %s,?" % command, '%.11E' % 2.8E8)]
        ) as instr:
            assert getattr(instr, function) == 2.8E8

    def test_sampler_harmonic_number(self):
        with expected_protocol(
                HP856Xx,
                [("FDIAG HARM,?", '%.11E' % 1.40000000000E1)]
        ) as instr:
            assert instr.sampler_harmonic_number == 14

    def test_frequency_display_enabled(self):
        with expected_protocol(
                HP856Xx,
                [("FDSP?", "0")]
        ) as instr:
            assert instr.frequency_display_enabled is False

    def test_fft(self):
        with expected_protocol(
                HP856Xx,
                [("FFT TRA,TRB,TRA", None)]
        ) as instr:
            instr.do_fft(Trace.A, Trace.B, Trace.A)

    def test_fft_exceptions(self):
        with expected_protocol(
                HP856Xx,
                []
        ) as instr:
            with pytest.raises(TypeError):
                instr.do_fft(0, 4, 5)

            with pytest.raises(ValueError):
                instr.do_fft("TRAZ", "zuo", "TEWST")

    @pytest.mark.parametrize("frequency_reference", [e for e in FrequencyReference])
    def test_frequency_reference_source(self, frequency_reference):
        with expected_protocol(
                HP856Xx,
                [("FREF " + frequency_reference, None),
                 ("FREF?", frequency_reference)]
        ) as instr:
            instr.frequency_reference_source = frequency_reference
            assert instr.frequency_reference_source == frequency_reference

    @pytest.mark.parametrize(
        "function, command",
        [
            ("graticule_enabled", "GRAT"),
            ("marker_signal_tracking_enabled", "MKTRACK"),
            ("marker_noise_mode_enabled", "MKNOISE"),
            ("normalize_trace_data_enabled", "NORMLIZE"),
            ("protect_state_enabled", "PSTATE"),
            ("trace_a_minus_b_enabled", "AMB"),
            ("trace_a_minus_b_plus_dl_enabled", "AMBPL"),
            ("annotation_enabled", "ANNOT")
        ]
    )
    def test_on_off_commands(self, function, command):
        with expected_protocol(
                HP856Xx,
                [(command + " 0", None),
                 (command + "?", "1")]
        ) as instr:
            setattr(instr, function, False)
            assert getattr(instr, function) is True

    @pytest.mark.parametrize("cmd", ["CURR", "FULL"])
    def test_adjust_if(self, cmd):
        with expected_protocol(
                HP856Xx,
                [("ADJIF 1", None),
                 ("ADJIF %s" % cmd, None),
                 ("ADJIF?", "1")]
        ) as instr:
            instr.adjust_if = True
            instr.adjust_if = cmd
            assert instr.adjust_if is True

    def test_logarithmic_scale(self):
        with expected_protocol(
                HP856Xx,
                [("LG 1 DB", None),
                 ("LG?", "10")]
        ) as instr:
            instr.logarithmic_scale = 1
            assert instr.logarithmic_scale == 10

    @pytest.mark.parametrize(
        "function, cmdstr",
        [
            ("set_minimum_hold", "MINH"),
            ("set_maximum_hold", "MXMH")
        ]
    )
    @pytest.mark.parametrize("trace", [e for e in Trace])
    def test_hold(self, trace, function, cmdstr):
        with expected_protocol(
                HP856Xx,
                [(cmdstr + " " + trace, None)]
        ) as instr:
            getattr(instr, function)(trace)

    @pytest.mark.parametrize("function", ["set_minimum_hold", "set_maximum_hold"])
    def test_hold_exceptions(self, function):
        with expected_protocol(
                HP856Xx,
                []
        ) as instr:
            with pytest.raises(ValueError):
                getattr(instr, function)("TEST")

            with pytest.raises(TypeError):
                getattr(instr, function)(0)

    def test_marker_amplitude(self):
        with expected_protocol(
                HP856Xx,
                [("MKA?", 2.8e7)]
        ) as instr:
            assert instr.marker_amplitude == 2.8e7

    def test_marker_delta(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKD %.11E Hz" % 28, None),
                    ("MKD?", 2.8e7)
                ]
        ) as instr:
            instr.marker_delta = 2.8e1
            assert instr.marker_delta == 2.8e7

    def test_marker_frequency(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKF %.11E Hz" % 1, None),
                    ("MKF?", 0.5)
                ]
        ) as instr:
            instr.marker_frequency = 1
            assert instr.marker_frequency == 0.5

    def test_frequency_counter_mode_enabled(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKFC OFF", None),
                    ("MKFC ON", None)
                ]
        ) as instr:
            instr.frequency_counter_mode_enabled = False
            instr.frequency_counter_mode_enabled = True

    def test_frequency_counter_resolution(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKFCR %d Hz" % 1e3, None),
                    ("MKFCR?", 1e4)
                ]
        ) as instr:
            instr.frequency_counter_resolution = 1e3
            assert instr.frequency_counter_resolution == 1e4

    @pytest.mark.parametrize("all_markers, cmdstring", [(True, " ALL"), (False, "")])
    def test_deactivate_marker(self, all_markers, cmdstring):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKOFF%s" % cmdstring, None),
                ]
        ) as instr:
            instr.deactivate_marker(all_markers)

    @pytest.mark.parametrize("mode", [e for e in PeakSearchMode])
    def test_minimum_hold(self, mode):
        with expected_protocol(
                HP856Xx,
                [("MKPK " + mode, None)]
        ) as instr:
            instr.search_peak(mode)

    def test_marker_threshold(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("AUNITS?", "DBM"),
                    ("MKPT %d DBM" % -30, None),
                    ("MKPT?", -70)
                ]
        ) as instr:
            instr.marker_threshold = -30
            assert instr.marker_threshold == -70

    def test_peak_excursion(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKPX %g DB" % 10.3, None),
                    ("MKPX?", 10.3)
                ]
        ) as instr:
            instr.peak_excursion = 10.3
            assert instr.peak_excursion == 10.3

    def test_marker_time(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKT %gS" % 10.3, None),
                    ("MKT?", 10.3)
                ]
        ) as instr:
            instr.marker_time = 10.3
            assert instr.marker_time == 10.3

    def test_mixer_level(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("ML -30 DB", None),
                    ("ML?", "-30")
                ]
        ) as instr:
            instr.mixer_level = -30
            assert instr.mixer_level == -30

    def test_normalized_reference_level(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("AUNITS?", "DBM"),
                    ("NRL -30 DBM", None),
                    ("NRL?", "-30")
                ]
        ) as instr:
            instr.normalized_reference_level = -30
            assert instr.normalized_reference_level == -30

    def test_normalized_reference_position(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("NRPOS 8.000000 DB", None),
                    ("NRPOS?", "8")
                ]
        ) as instr:
            instr.normalized_reference_position = 8
            assert instr.normalized_reference_position == 8

    def test_display_parameters(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("OP?", "72,16,712,766")
                ]
        ) as instr:
            assert instr.display_parameters == (72, 16, 712, 766)

    def test_plot(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("PLOT 72,16,712,766", None)
                ]
        ) as instr:
            instr.plot(72, 16, 712, 766)

    def test_power_bandwidth(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("PWRBW TRA,99.2?", "1.0e3")
                ]
        ) as instr:
            assert instr.get_power_bandwidth(Trace.A, 99.2) == 1e3

    def test_resolution_bandwidth(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RB 30 Hz", None),
                    ("RB AUTO", None),
                    ("RB?", "30")
                ]
        ) as instr:
            instr.resolution_bandwidth = 30
            instr.resolution_bandwidth = "AUTO"
            assert instr.resolution_bandwidth == 30

    def test_resolution_bandwidth_to_span_ratio(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RBR 0.014", None),
                    ("RBR?", "0.014")
                ]
        ) as instr:
            instr.resolution_bandwidth_to_span_ratio = 0.0140
            assert instr.resolution_bandwidth_to_span_ratio == 0.0140

    def test_recall_state(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RCLS LAST", None),
                    ("RCLS 8", None)
                ]
        ) as instr:
            instr.recall_state("LAST")
            instr.recall_state(8)

    def test_recall_trace(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RCLT TRA,6", None)
                ]
        ) as instr:
            instr.recall_trace(Trace.A, 6)

    def test_firmware_revision(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("REV?", "901101")
                ]
        ) as instr:
            assert instr.firmware_revision == datetime.strptime("11-01-1990", '%m-%d-%Y').date()

    def test_reference_level(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("AUNITS?", "DBM"),
                    ("RL 10 DBM", None),
                    ("RL?", "10")
                ]
        ) as instr:
            instr.reference_level = 10
            assert instr.reference_level == 10

    def test_reference_level_calibration(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RLCAL 33", None),
                    ("RLCAL?", "33")
                ]
        ) as instr:
            instr.reference_level_calibration = 33
            assert instr.reference_level_calibration == 33

    def test_request_service_conditions(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RQS 48", None),
                    ("RQS?", "48")
                ]
        ) as instr:
            instr.request_service_conditions = \
                StatusRegister.COMMAND_COMPLETE | StatusRegister.ERROR_PRESENT
            assert instr.request_service_conditions == \
                   StatusRegister.COMMAND_COMPLETE | StatusRegister.ERROR_PRESENT

    def test_save_state(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("SAVES 6", None)
                ]
        ) as instr:
            instr.save_state(6)

    def test_save_trace(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("SAVET TRA,6", None)
                ]
        ) as instr:
            instr.save_trace(Trace.A, 6)

    @pytest.mark.parametrize("param", ["FULL", "ZERO"])
    def test_span_string_params(self, param):
        with expected_protocol(
                HP856Xx,
                [
                    ("SP %s" % param, None)
                ]
        ) as instr:
            instr.span = param

    @pytest.mark.parametrize("string_params", ["ON", "OFF"])
    def test_squelch(self, string_params):
        with expected_protocol(
                HP856Xx,
                [("AUNITS?", "DBM"),
                 ("SQUELCH 10 DBM", None),
                 ("SQUELCH %s" % string_params, None),
                 ("SQUELCH?", "10")]
        ) as instr:
            instr.squelch = 10
            instr.squelch = string_params
            assert instr.squelch == 10

    def test_service_request(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("SRQ 48", None)
                ]
        ) as instr:
            instr.request_service(StatusRegister.COMMAND_COMPLETE | StatusRegister.ERROR_PRESENT)

    def test_sweep_time(self):
        with expected_protocol(
                HP856Xx,
                [("ST 10.000 S", None),
                 ("ST AUTO", None),
                 ("ST?", "10.00")]
        ) as instr:
            instr.sweep_time = 10
            instr.sweep_time = "AUTO"
            assert instr.sweep_time == 10

    @pytest.mark.parametrize("mode", [e for e in SweepCoupleMode])
    def test_sweep_couple(self, mode):
        with expected_protocol(
                HP856Xx,
                [("SWPCPL " + mode, None),
                 ("SWPCPL?", mode)]
        ) as instr:
            instr.sweep_couple = mode
            assert instr.sweep_couple == mode

    @pytest.mark.parametrize("mode", [e for e in SweepOut])
    def test_sweep_output(self, mode):
        with expected_protocol(
                HP856Xx,
                [("SWPOUT " + mode, None),
                 ("SWPOUT?", mode)]
        ) as instr:
            instr.sweep_output = mode
            assert instr.sweep_output == mode

    @pytest.mark.parametrize("mode", [e for e in TraceDataFormat])
    def test_trace_data_format(self, mode):
        with expected_protocol(
                HP856Xx,
                [("TDF " + mode, None),
                 ("TDF?", mode)]
        ) as instr:
            instr.trace_data_format = mode
            assert instr.trace_data_format == mode

    def test_threshold(self):
        with expected_protocol(
                HP856Xx,
                [("AUNITS?", "DBM"),
                 ("TH 1.00E+01 DBM", None),
                 ("TH?", "10.00")]
        ) as instr:
            instr.threshold = 10
            assert instr.threshold == 10

    def test_threshold_enabled(self):
        with expected_protocol(
                HP856Xx,
                [("TH ON", None)]
        ) as instr:
            instr.threshold_enabled = True

    def test_title(self):
        with expected_protocol(
                HP856Xx,
                [("TITLE@%s@" % "TestString", None)]
        ) as instr:
            instr.set_title("TestString")

    @pytest.mark.parametrize("mode", [e for e in TriggerMode])
    def test_trigger_mode(self, mode):
        with expected_protocol(
                HP856Xx,
                [("TM " + mode, None),
                 ("TM?", mode)]
        ) as instr:
            instr.trigger_mode = mode
            assert instr.trigger_mode == mode

    @pytest.mark.parametrize("function, cmd", [
        ("get_trace_data_a", "TRA"),
        ("get_trace_data_b", "TRB")
    ])
    def test_trace_data(self, function, cmd):
        data = [48, 61, 31, 73, 90, 82, 56, 48, 87, 78, 59, 103, 78, 76, 92, 52, 57, 72, 48, 82,
                108, 63, 52, 79, 44, 88, 95, 99, 74, 79, 63, 100, 51, 85, 96, 69, 97, 50, 105, 94,
                58, 98, 92, 92, 96, 59, 63, 34, 81, 56, 50, 94, 74, 61, 40, 48, 72, 69, 86, 114, 59,
                70, 83, 53, 67, 111, 110, 99, 112, 72, 100, 44, 80, 81, 65, 34, 56, 62, 55, 78, 86,
                68, 59, 66, 91, 91, 91, 63, 83, 90, 71, 94, 91, 46, 69, 70, 99, 52, 86, 63, 88, 75,
                55, 80, 97, 31, 40, 81, 92, 75, 30, 113, 83, 64, 98, 49, 51, 99, 102, 54, 57, 38,
                67, 84, 75, 59, 75, 78, 93, 47, 89, 107, 77, 42, 63, 98, 45, 81, 81, 98, 39, 39, 44,
                89, 72, 77, 99, 104, 84, 61, 105, 76, 80, 29, 66, 45, 88, 98, 54, 108, 89, 88, 54,
                79, 91, 38, 85, 98, 42, 66, 41, 94, 55, 49, 94, 57, 67, 69, 75, 96, 87, 75, 97, 101,
                52, 85, 76, 47, 53, 108, 61, 82, 61, 61, 64, 56, 88, 62, 54, 91, 54, 38, 37, 91, 65,
                60, 60, 70, 102, 97, 71, 93, 85, 92, 52, 85, 61, 77, 63, 96, 71, 40, 51, 65, 69, 78,
                65, 81, 56, 63, 68, 59, 43, 120, 77, 58, 57, 79, 90, 62, 47, 50, 76, 77, 87, 38,
                102, 72, 66, 74, 84, 73, 70, 64, 88, 86, 73, 83, 82, 98, 98, 93, 100, 114, 111, 116,
                121, 127, 132, 139, 148, 153, 160, 167, 174, 182, 190, 197, 205, 215, 224, 233, 244,
                255, 265, 275, 287, 300, 313, 325, 339, 354, 368, 383, 397, 414, 429, 443, 455, 466,
                472, 475, 474, 468, 458, 447, 434, 417, 402, 388, 373, 357, 343, 329, 316, 303, 291,
                279, 269, 259, 248, 239, 230, 220, 212, 204, 196, 189, 181, 175, 168, 162, 154, 147,
                143, 136, 128, 124, 120, 113, 104, 104, 98, 92, 86, 115, 96, 86, 112, 77, 92, 88,
                82, 79, 104, 49, 97, 73, 58, 68, 80, 84, 68, 78, 46, 74, 88, 81, 110, 80, 82, 89,
                83, 50, 62, 64, 97, 58, 48, 66, 47, 53, 38, 108, 94, 88, 116, 66, 103, 85, 41, 63,
                81, 58, 118, 50, 110, 93, 52, 43, 74, 42, 89, 71, 66, 50, 73, 89, 119, 86, 57, 100,
                55, 79, 71, 75, 90, 47, 86, 79, 110, 99, 87, 79, 87, 63, 76, 73, 62, 98, 107, 89,
                80, 90, 71, 44, 46, 50, 41, 66, 109, 47, 97, 70, 77, 75, 103, 120, 69, 67, 92, 90,
                81, 54, 95, 97, 86, 83, 71, 48, 53, 95, 62, 51, 85, 59, 71, 90, 63, 69, 108, 72, 75,
                25, 116, 60, 51, 90, 84, 74, 43, 88, 83, 60, 99, 86, 61, 72, 82, 77, 80, 64, 84,
                101, 108, 57, 107, 92, 77, 62, 81, 74, 69, 50, 46, 56, 51, 79, 49, 34, 101, 76, 55,
                111, 103, 92, 109, 123, 74, 50, 68, 56, 79, 43, 55, 43, 111, 46, 76, 103, 85, 70,
                53, 70, 88, 54, 117, 78, 85, 57, 72, 88, 89, 58, 98, 55, 68, 77, 71, 56, 75, 44, 53,
                76, 95, 81, 48, 40, 84, 38, 84, 110, 82, 67, 114, 79, 40, 52, 102, 103, 85, 80, 108,
                86, 40, 123, 66, 86, 93, 83, 78, 42, 74, 33, 79, 55, 67, 111, 77, 61, 89, 58, 89,
                103, 77, 77, 62, 57, 61, 54, 30]

        expected_data = [-82.0, -79.83, -84.83, -77.83, -75.0, -76.33, -80.67, -82.0, -75.5, -77.0,
                         -80.17, -72.83, -77.0, -77.33, -74.67, -81.33, -80.5, -78.0, -82.0, -76.33,
                         -72.0, -79.5, -81.33, -76.83, -82.67, -75.33, -74.17, -73.5, -77.67,
                         -76.83, -79.5, -73.33, -81.5, -75.83, -74.0, -78.5, -73.83, -81.67, -72.5,
                         -74.33, -80.33, -73.67, -74.67, -74.67, -74.0, -80.17, -79.5, -84.33,
                         -76.5, -80.67, -81.67, -74.33, -77.67, -79.83, -83.33, -82.0, -78.0, -78.5,
                         -75.67, -71.0, -80.17, -78.33, -76.17, -81.17, -78.83, -71.5, -71.67,
                         -73.5, -71.33, -78.0, -73.33, -82.67, -76.67, -76.5, -79.17, -84.33,
                         -80.67, -79.67, -80.83, -77.0, -75.67, -78.67, -80.17, -79.0, -74.83,
                         -74.83, -74.83, -79.5, -76.17, -75.0, -78.17, -74.33, -74.83, -82.33,
                         -78.5, -78.33, -73.5, -81.33, -75.67, -79.5, -75.33, -77.5, -80.83, -76.67,
                         -73.83, -84.83, -83.33, -76.5, -74.67, -77.5, -85.0, -71.17, -76.17,
                         -79.33, -73.67, -81.83, -81.5, -73.5, -73.0, -81.0, -80.5, -83.67, -78.83,
                         -76.0, -77.5, -80.17, -77.5, -77.0, -74.5, -82.17, -75.17, -72.17, -77.17,
                         -83.0, -79.5, -73.67, -82.5, -76.5, -76.5, -73.67, -83.5, -83.5, -82.67,
                         -75.17, -78.0, -77.17, -73.5, -72.67, -76.0, -79.83, -72.5, -77.33, -76.67,
                         -85.17, -79.0, -82.5, -75.33, -73.67, -81.0, -72.0, -75.17, -75.33, -81.0,
                         -76.83, -74.83, -83.67, -75.83, -73.67, -83.0, -79.0, -83.17, -74.33,
                         -80.83, -81.83, -74.33, -80.5, -78.83, -78.5, -77.5, -74.0, -75.5, -77.5,
                         -73.83, -73.17, -81.33, -75.83, -77.33, -82.17, -81.17, -72.0, -79.83,
                         -76.33, -79.83, -79.83, -79.33, -80.67, -75.33, -79.67, -81.0, -74.83,
                         -81.0, -83.67, -83.83, -74.83, -79.17, -80.0, -80.0, -78.33, -73.0, -73.83,
                         -78.17, -74.5, -75.83, -74.67, -81.33, -75.83, -79.83, -77.17, -79.5,
                         -74.0, -78.17, -83.33, -81.5, -79.17, -78.5, -77.0, -79.17, -76.5, -80.67,
                         -79.5, -78.67, -80.17, -82.83, -70.0, -77.17, -80.33, -80.5, -76.83, -75.0,
                         -79.67, -82.17, -81.67, -77.33, -77.17, -75.5, -83.67, -73.0, -78.0, -79.0,
                         -77.67, -76.0, -77.83, -78.33, -79.33, -75.33, -75.67, -77.83, -76.17,
                         -76.33, -73.67, -73.67, -74.5, -73.33, -71.0, -71.5, -70.67, -69.83,
                         -68.83, -68.0, -66.83, -65.33, -64.5, -63.33, -62.17, -61.0, -59.67,
                         -58.33, -57.17, -55.83, -54.17, -52.67, -51.17, -49.33, -47.5, -45.83,
                         -44.17, -42.17, -40.0, -37.83, -35.83, -33.5, -31.0, -28.67, -26.17,
                         -23.83, -21.0, -18.5, -16.17, -14.17, -12.33, -11.33, -10.83, -11.0, -12.0,
                         -13.67, -15.5, -17.67, -20.5, -23.0, -25.33, -27.83, -30.5, -32.83, -35.17,
                         -37.33, -39.5, -41.5, -43.5, -45.17, -46.83, -48.67, -50.17, -51.67,
                         -53.33, -54.67, -56.0, -57.33, -58.5, -59.83, -60.83, -62.0, -63.0, -64.33,
                         -65.5, -66.17, -67.33, -68.67, -69.33, -70.0, -71.17, -72.67, -72.67,
                         -73.67, -74.67, -75.67, -70.83, -74.0, -75.67, -71.33, -77.17, -74.67,
                         -75.33, -76.33, -76.83, -72.67, -81.83, -73.83, -77.83, -80.33, -78.67,
                         -76.67, -76.0, -78.67, -77.0, -82.33, -77.67, -75.33, -76.5, -71.67,
                         -76.67, -76.33, -75.17, -76.17, -81.67, -79.67, -79.33, -73.83, -80.33,
                         -82.0, -79.0, -82.17, -81.17, -83.67, -72.0, -74.33, -75.33, -70.67, -79.0,
                         -72.83, -75.83, -83.17, -79.5, -76.5, -80.33, -70.33, -81.67, -71.67,
                         -74.5, -81.33, -82.83, -77.67, -83.0, -75.17, -78.17, -79.0, -81.67,
                         -77.83, -75.17, -70.17, -75.67, -80.5, -73.33, -80.83, -76.83, -78.17,
                         -77.5, -75.0, -82.17, -75.67, -76.83, -71.67, -73.5, -75.5, -76.83, -75.5,
                         -79.5, -77.33, -77.83, -79.67, -73.67, -72.17, -75.17, -76.67, -75.0,
                         -78.17, -82.67, -82.33, -81.67, -83.17, -79.0, -71.83, -82.17, -73.83,
                         -78.33, -77.17, -77.5, -72.83, -70.0, -78.5, -78.83, -74.67, -75.0, -76.5,
                         -81.0, -74.17, -73.83, -75.67, -76.17, -78.17, -82.0, -81.17, -74.17,
                         -79.67, -81.5, -75.83, -80.17, -78.17, -75.0, -79.5, -78.5, -72.0, -78.0,
                         -77.5, -85.83, -70.67, -80.0, -81.5, -75.0, -76.0, -77.67, -82.83, -75.33,
                         -76.17, -80.0, -73.5, -75.67, -79.83, -78.0, -76.33, -77.17, -76.67,
                         -79.33, -76.0, -73.17, -72.0, -80.5, -72.17, -74.67, -77.17, -79.67, -76.5,
                         -77.67, -78.5, -81.67, -82.33, -80.67, -81.5, -76.83, -81.83, -84.33,
                         -73.17, -77.33, -80.83, -71.5, -72.83, -74.67, -71.83, -69.5, -77.67,
                         -81.67, -78.67, -80.67, -76.83, -82.83, -80.83, -82.83, -71.5, -82.33,
                         -77.33, -72.83, -75.83, -78.33, -81.17, -78.33, -75.33, -81.0, -70.5,
                         -77.0, -75.83, -80.5, -78.0, -75.33, -75.17, -80.33, -73.67, -80.83,
                         -78.67, -77.17, -78.17, -80.67, -77.5, -82.67, -81.17, -77.33, -74.17,
                         -76.5, -82.0, -83.33, -76.0, -83.67, -76.0, -71.67, -76.33, -78.83, -71.0,
                         -76.83, -83.33, -81.33, -73.0, -72.83, -75.83, -76.67, -72.0, -75.67,
                         -83.33, -69.5, -79.0, -75.67, -74.5, -76.17, -77.0, -83.0, -77.67, -84.5,
                         -76.83, -80.83, -78.83, -71.5, -77.17, -79.83, -75.17, -80.33, -75.17,
                         -72.83, -77.17, -77.17, -79.67, -80.5, -79.83, -81.0, -85.0]
        with expected_protocol(
                HP856Xx,
                [
                    ("TDF M", None),
                    ("AUNITS?", "DBM"),
                    ("RL?", "10.0"),
                    ("LG?", "10.0"),
                    (cmd + "?", ','.join([str(i) for i in data]))
                ]
        ) as instr:
            assert getattr(instr, function)() == expected_data

    def test_fft_trace_window(self):
        with expected_protocol(
                HP856Xx,
                [("TWNDOW TRA,FLATTOP", None)]
        ) as instr:
            instr.create_fft_trace_window(Trace.A, WindowType.Flattop)

    @pytest.mark.parametrize("param", [("ON", True), ("OFF", False)])
    def test_video_average_enabled(self, param):
        str_param, boolean = param
        with expected_protocol(
                HP856Xx,
                [("VAVG " + str_param, None)]
        ) as instr:
            instr.video_average_enabled = boolean

    def test_video_bandwidth(self):
        with expected_protocol(
                HP856Xx,
                [("VB 70 Hz", None),
                 ("VB?", "70")],
        ) as instr:
            instr.video_bandwidth = 70
            assert instr.video_bandwidth == 70

    def test_video_bandwidth_string_parameters(self):
        with expected_protocol(
                HP856Xx,
                [("VB AUTO", None),
                 ("VB?", "20"), ],
        ) as instr:
            instr.video_bandwidth = "AUTO"
            assert instr.video_bandwidth == 20

    def test_video_bandwidth_to_resolution_bandwidth(self):
        with expected_protocol(
                HP856Xx,
                [("VBR 0.005", None),
                 ("VBR?", "0.005")],
        ) as instr:
            instr.video_bandwidth_to_resolution_bandwidth = 0.005
            assert instr.video_bandwidth_to_resolution_bandwidth == 0.005

    @pytest.mark.parametrize("trace", [e for e in Trace])
    def test_view_trace(self, trace):
        with expected_protocol(
                HP856Xx,
                [("VIEW " + trace, None)]
        ) as instr:
            instr.view_trace(trace)

    def test_video_trigger_level(self):
        with expected_protocol(
                HP856Xx,
                [("AUNITS?", "DBM"),
                 ("VTL -200.780 DBM", None),
                 ("VTL?", "0.005")],
        ) as instr:
            instr.video_trigger_level = -200.78
            assert instr.video_trigger_level == 0.005


class TestHP8560A:

    @pytest.mark.parametrize("mode", [e for e in SourceLevelingControlMode])
    def test_source_leveling_control(self, mode):
        with expected_protocol(
                HP8560A,
                [("SRCALC " + mode, None),
                 ("SRCALC?", mode)]
        ) as instr:
            instr.source_leveling_control = mode
            assert instr.source_leveling_control == mode

    def test_tracking_adjust_coarse(self):
        with expected_protocol(
                HP8560A,
                [("SRCCRSTK 10", None),
                 ("SRCCRSTK?", "10")]
        ) as instr:
            instr.tracking_adjust_coarse = 10
            assert instr.tracking_adjust_coarse == 10

    def test_tracking_adjust_fine(self):
        with expected_protocol(
                HP8560A,
                [("SRCFINTK 10", None),
                 ("SRCFINTK?", "10")]
        ) as instr:
            instr.tracking_adjust_fine = 10
            assert instr.tracking_adjust_fine == 10

    def test_source_power_offset(self):
        with expected_protocol(
                HP8560A,
                [("AUNITS?", "DBM"),
                 ("SRCPOFS 10 DBM", None),
                 ("SRCPOFS?", "10")]
        ) as instr:
            instr.source_power_offset = 10
            assert instr.source_power_offset == 10

    def test_source_power_step(self):
        with expected_protocol(
                HP8560A,
                [("SRCPSTP 10.10 DB", None),
                 ("SRCPSTP?", "10.10")]
        ) as instr:
            instr.source_power_step = 10.1
            assert instr.source_power_step == 10.1

    def test_source_power_sweep(self):
        with expected_protocol(
                HP8560A,
                [("SRCPSWP 10.00 DB", None),
                 ("SRCPSWP?", "10.00")]
        ) as instr:
            instr.source_power_sweep = 10
            assert instr.source_power_sweep == 10

    def test_source_power_sweep_enabled(self):
        with expected_protocol(
                HP8560A,
                [("SRCPSWP OFF", None)]
        ) as instr:
            instr.source_power_sweep_enabled = False

    def test_source_power(self):
        with expected_protocol(
                HP8560A,
                [("AUNITS?", "DBM"),
                 ("SRCPWR 2.00 DBM", None),
                 ("SRCPWR ON", None),
                 ("SRCPWR?", "2.00")]
        ) as instr:
            instr.source_power = 2.0
            instr.source_power = "ON"
            assert instr.source_power == 2.0

    def test_source_peak_tracking(self):
        with expected_protocol(
                HP8560A,
                [("SRCTKPK", None)]
        ) as instr:
            instr.activate_source_peak_tracking()


class TestHP8561B:

    @pytest.mark.parametrize("mixer_mode", [e for e in MixerMode])
    def test_external_mixer(self, mixer_mode):
        with expected_protocol(
                HP8561B,
                [("MXRMODE " + mixer_mode, None),
                 ("MXRMODE?", mixer_mode)]
        ) as instr:
            instr.mixer_mode = mixer_mode
            assert instr.mixer_mode == mixer_mode

    def test_conversion_loss(self):
        with expected_protocol(
                HP8561B,
                [("CNVLOSS 10.2 DB", None),
                 ("CNVLOSS?", "10.3")]
        ) as instr:
            instr.conversion_loss = 10.2
            assert instr.conversion_loss == 10.3

    def test_fullband(self):
        with expected_protocol(
                HP8561B,
                [("FULLBAND K", None)]
        ) as instr:
            instr.set_fullband("K")

    def test_fullband_exceptions(self):
        with expected_protocol(
                HP8561B,
                []
        ) as instr:
            with pytest.raises(TypeError):
                instr.set_fullband(1)

            with pytest.raises(ValueError):
                instr.set_fullband("Z")

    def test_harmonic_number_lock(self):
        with expected_protocol(
                HP8561B,
                [("HNLOCK 10", None),
                 ("HNLOCK?", "10")]
        ) as instr:
            instr.harmonic_number_lock = 10
            assert instr.harmonic_number_lock == 10

    @pytest.mark.parametrize("params", [("ON", True), ("OFF", False)])
    def test_harmonic_number_lock_enabled(self, params):
        str_param, boolean = params
        with expected_protocol(
                HP8561B,
                [("HNLOCK %s" % str_param, None)]
        ) as instr:
            instr.harmonic_number_lock_enabled = boolean

    @pytest.mark.parametrize(
        "function, command",
        [
            ("unlock_harmonic_number", "HUNLK"),
            ("set_signal_identification_to_center_frequency", "IDCF"),
            ("peak_preselector", "PP")
        ]
    )
    def test_primitive_commands(self, command, function):
        """
        Tests primitive commands which have no parameter or query derivat
        """
        with expected_protocol(
                HP8561B,
                [(command, None)]
        ) as instr:
            getattr(instr, function)()

    def test_signal_identification_frequency(self):
        with expected_protocol(
                HP8561B,
                [("IDFREQ?", 2.7897e9)]
        ) as instr:
            assert instr.signal_identification_frequency == 2.7897e9

    def test_mixer_bias(self):
        with expected_protocol(
                HP8561B,
                [("MBIAS -9.900 MA", None),
                 ("MBIAS?", "5.5")]
        ) as instr:
            instr.mixer_bias = -9.9
            assert instr.mixer_bias == 5.5

    @pytest.mark.parametrize("params", [("ON", True), ("OFF", False)])
    def test_mixer_bias_enabled(self, params):
        str_param, boolean = params
        with expected_protocol(
                HP8561B,
                [("MBIAS %s" % str_param, None)]
        ) as instr:
            instr.mixer_bias_enabled = boolean

    def test_preselector_dac_number(self):
        with expected_protocol(
                HP8561B,
                [("PSDAC 10", None),
                 ("PSDAC?", "10")]
        ) as instr:
            instr.preselector_dac_number = 10
            assert instr.preselector_dac_number == 10

    def test_signal_identification(self):
        with expected_protocol(
                HP8561B,
                [("SIGID AUTO", None),
                 ("SIGID?", "1")]
        ) as instr:
            instr.signal_identification = "AUTO"
            assert instr.signal_identification is True
