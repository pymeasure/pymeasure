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
            ("auto_couple", "AUTOCPL"),
            ("exchange_traces", "AXB"),
            ("subtract_display_line_from_trace_b", "BML"),
            ("continuous_sweep", "CONTS"),
            ("full_span", "FS"),
            ("linear_scale", "LN"),
            ("marker_to_center_frequency", "MKCF"),
            ("marker_minimum", "MKMIN"),
            ("marker_to_reference_level", "MKRL"),
            ("marker_delta_to_span", "MKSP"),
            ("marker_to_center_frequency_step_size", "MKSS"),
            ("preset", "IP"),
            ("recall_open_short_average", "RCLOSCAL"),
            ("recall_thru", "RCLTHRU"),
            ("single_sweep", "SNGLS"),
            ("store_open", "STOREOPEN"),
            ("store_short", "STORESHORT"),
            ("store_thru", "STORETHRU"),
            ("adjust_all", "ADJALL"),
            ("crt_adjustment_pattern", "ADJCRT"),
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
                [("%s %.11E" % (command, max_freq), None),
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
    def test_demodulation_agc(self, on_off, boole):
        with expected_protocol(
                HP856Xx,
                [("DEMODAGC " + on_off, None),
                 ("DEMODAGC?", on_off)]
        ) as instr:
            instr.demodulation_agc = boole
            assert instr.demodulation_agc == boole

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
    def test_display_line_strings(self, string_params):
        with expected_protocol(
                HP856Xx,
                [
                    ("DL 1.00000000000E+01", None),
                    ("DL " + string_params, None),
                    ("DL?", "1.00000000000E+01")
                ]
        ) as instr:
            instr.display_line = 1.0e01
            instr.display_line = string_params
            assert instr.display_line == 10

    def test_done(self):
        with expected_protocol(
                HP856Xx,
                [("DONE?", "1")],
        ) as instr:
            assert instr.done

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

    def test_frequency_display(self):
        with expected_protocol(
                HP856Xx,
                [("FDSP?", "0")]
        ) as instr:
            assert instr.frequency_display is False

    def test_fft(self):
        with expected_protocol(
                HP856Xx,
                [("FFT TRA,TRB,TRA", None)]
        ) as instr:
            instr.fft(Trace.A, Trace.B, Trace.A)

    def test_fft_exceptions(self):
        with expected_protocol(
                HP856Xx,
                []
        ) as instr:
            with pytest.raises(TypeError):
                instr.fft(0, 4, 5)

            with pytest.raises(ValueError):
                instr.fft("TRAZ", "zuo", "TEWST")

    @pytest.mark.parametrize("frequency_reference", [e for e in FrequencyReference])
    def test_frequecy_reference(self, frequency_reference):
        with expected_protocol(
                HP856Xx,
                [("FREF " + frequency_reference, None),
                 ("FREF?", frequency_reference)]
        ) as instr:
            instr.frequency_reference = frequency_reference
            assert instr.frequency_reference == frequency_reference

    @pytest.mark.parametrize(
        "function, command",
        [
            ("graticule", "GRAT"),
            ("marker_signal_tracking", "MKTRACK"),
            ("marker_noise_mode", "MKNOISE"),
            ("normalize_trace_data", "NORMLIZE"),
            ("protect_state", "PSTATE"),
            ("trace_a_minus_b", "AMB"),
            ("trace_a_minus_b_plus_dl", "AMBPL"),
            ("annotation", "ANNOT")
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
                [("LG 1", None),
                 ("LG?", "10")]
        ) as instr:
            instr.logarithmic_scale = 1
            assert instr.logarithmic_scale == 10

    @pytest.mark.parametrize(
        "function, cmdstr",
        [
            ("minimum_hold", "MINH"),
            ("maximum_hold", "MXMH")
        ]
    )
    @pytest.mark.parametrize("trace", [e for e in Trace])
    def test_hold(self, trace, function, cmdstr):
        with expected_protocol(
                HP856Xx,
                [(cmdstr + " " + trace, None)]
        ) as instr:
            getattr(instr, function)(trace)

    @pytest.mark.parametrize("function", ["minimum_hold", "maximum_hold"])
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
                    ("MKD %.11E" % 28, None),
                    ("MKD?", 2.8e7)
                ]
        ) as instr:
            instr.marker_delta = 2.8e1
            assert instr.marker_delta == 2.8e7

    def test_marker_frequency(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKF %.11E" % 1, None),
                    ("MKF?", 0.5)
                ]
        ) as instr:
            instr.marker_frequency = 1
            assert instr.marker_frequency == 0.5

    def test_frequency_counter_mode(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKFC OFF", None),
                    ("MKFC ON", None)
                ]
        ) as instr:
            instr.frequency_counter_mode(False)
            instr.frequency_counter_mode(True)

    def test_frequency_counter_resolution(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKFCR %d" % 1e3, None),
                    ("MKFCR?", 1e4)
                ]
        ) as instr:
            instr.frequency_counter_resolution = 1e3
            assert instr.frequency_counter_resolution == 1e4

    @pytest.mark.parametrize("all_markers, cmdstring", [(True, " ALL"), (False, "")])
    def test_marker_off(self, all_markers, cmdstring):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKOFF%s" % cmdstring, None),
                ]
        ) as instr:
            instr.marker_off(all_markers)

    @pytest.mark.parametrize("mode", [e for e in PeakSearchMode])
    def test_minimum_hold(self, mode):
        with expected_protocol(
                HP856Xx,
                [("MKPK " + mode, None)]
        ) as instr:
            instr.peak_search(mode)

    def test_marker_threshold(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKPT %d" % -30, None),
                    ("MKPT?", -70)
                ]
        ) as instr:
            instr.marker_threshold = -30
            assert instr.marker_threshold == -70

    def test_peak_excursion(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("MKPX %g" % 10.3, None),
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
                    ("ML -30", None),
                    ("ML?", "-30")
                ]
        ) as instr:
            instr.mixer_level = -30
            assert instr.mixer_level == -30

    def test_normalized_reference_level(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("NRL -30", None),
                    ("NRL?", "-30")
                ]
        ) as instr:
            instr.normalized_reference_level = -30
            assert instr.normalized_reference_level == -30

    def test_normalized_reference_position(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("NRPOS 8.000000", None),
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
            assert instr.power_bandwidth(Trace.A, 99.2) == 1e3

    def test_resolution_bandwidth(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RB 30", None),
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

    def test_revision(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("REV?", "901101")
                ]
        ) as instr:
            assert instr.revision == datetime.strptime("11-01-1990", '%m-%d-%Y').date()

    def test_reference_level(self):
        with expected_protocol(
                HP856Xx,
                [
                    ("RL 10", None),
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
                [("SQUELCH 10", None),
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
            instr.service_request(StatusRegister.COMMAND_COMPLETE | StatusRegister.ERROR_PRESENT)

    def test_sweep_time(self):
        with expected_protocol(
                HP856Xx,
                [("ST 1.000E+01", None),
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
                [("TH 1.00E+01", None),
                 ("TH ON", None),
                 ("TH?", "10.00")]
        ) as instr:
            instr.threshold = 10
            instr.threshold = "ON"
            assert instr.threshold == 10

    def test_title(self):
        with expected_protocol(
                HP856Xx,
                [("TITLE@%s@" % "TestString", None)]
        ) as instr:
            instr.title("TestString")

    @pytest.mark.parametrize("mode", [e for e in TriggerMode])
    def test_trigger_mode(self, mode):
        with expected_protocol(
                HP856Xx,
                [("TM " + mode, None),
                 ("TM?", mode)]
        ) as instr:
            instr.trigger_mode = mode
            assert instr.trigger_mode == mode

    @pytest.mark.parametrize("function, cmd", [("trace_data_a", "TRA"), ("trace_data_b", "TRB")])
    def test_trace_data(self, function, cmd):
        data = [-31.83, -89.16, -66.33, -94.66, -68.16, -88.83, -67.66, -89.33, -67.50, -89.16,
                -67.66, -87.50, -68.83, -90.16, -68.83, -87.00, -68.16, -90.00, -67.16, -87.33,
                -68.50, -89.16, -68.00, -91.50, -67.83, -88.00, -68.16, -89.00, -68.00, -89.83,
                -67.33, -91.33, -68.16, -90.33, -68.83, -92.66, -67.66, -87.83, -70.00, -92.00,
                -69.33, -89.50, -67.66, -91.33, -66.83, -88.66, -68.00, -90.66, -68.00, -88.33,
                -68.66, -89.50, -61.00, -91.16, -68.16, -88.50, -65.50, -90.66, -66.16, -88.83,
                -68.50, -86.16, -10.50, -91.83, -66.83, -93.33, -68.50, -92.16, -68.83, -89.50,
                -68.50, -89.33, -67.33, -90.50, -68.33, -91.16, -68.16, -89.00, -68.16, -90.16,
                -67.50, -89.66, -69.00, -89.00, -68.33, -89.16, -68.66, -88.66, -67.00, -91.66,
                -69.66, -91.00, -68.00, -91.33, -68.16, -91.00, -67.83, -89.16, -67.66, -88.83,
                -67.50, -89.33, -68.16, -92.66, -66.66, -89.33, -68.83, -89.33, -68.16, -89.83,
                -67.33, -89.66, -68.83, -90.66, -68.16, -90.16, -68.66, -90.50, -68.33, -89.00,
                -67.83, -87.83, -68.00, -89.50, -45.16, -92.33, -68.00, -88.33, -66.83, -89.16,
                -66.83, -90.66, -67.66, -90.66, -67.83, -88.16, -67.33, -87.33, -68.16, -91.16,
                -67.00, -90.16, -67.66, -88.33, -68.33, -88.66, -68.00, -89.66, -67.50, -89.66,
                -67.83, -88.16, -68.66, -91.00, -68.00, -90.16, -68.16, -89.00, -68.00, -90.83,
                -67.00, -92.00, -67.50, -89.33, -67.66, -88.50, -68.33, -89.33, -68.16, -90.50,
                -68.16, -88.83, -68.50, -89.50, -68.33, -90.83, -67.00, -88.83, -69.00, -92.33,
                -67.66, -89.00, -68.33, -91.16, -68.33, -90.16, -67.50, -90.00, -59.50, -87.83,
                -69.00, -90.83, -67.50, -88.50, -68.66, -91.66, -68.16, -90.16, -68.33, -90.66,
                -68.66, -87.83, -68.00, -89.16, -68.00, -87.66, -68.16, -90.00, -67.66, -89.50,
                -68.50, -92.16, -67.66, -89.16, -68.16, -89.16, -67.16, -89.50, -68.00, -89.66,
                -67.50, -87.16, -67.33, -90.66, -68.16, -91.50, -68.16, -90.16, -68.66, -87.66,
                -68.33, -89.83, -68.83, -90.33, -68.66, -86.33, -68.00, -91.00, -65.66, -92.33,
                -69.33, -90.66, -67.33, -92.00, -68.16, -90.66, -68.00, -90.33, -68.50, -85.66,
                -61.33, -88.50, -67.83, -92.16, -67.16, -90.00, -67.16, -87.33, -67.83, -93.00,
                -67.66, -89.83, -66.00, -91.66, -68.33, -90.83, -69.33, -91.00, -67.33, -88.50,
                -67.33, -90.00, -67.83, -91.00, -67.16, -93.16, -67.50, -87.00, -67.33, -88.33,
                -67.66, -88.33, -67.33, -88.33, -66.66, -87.66, -68.33, -90.66, -68.00, -88.83,
                -68.66, -88.83, -67.66, -88.16, -67.66, -90.66, -67.50, -92.50, -67.83, -90.33,
                -68.66, -89.16, -66.83, -91.66, -67.83, -87.83, -68.16, -89.16, -67.33, -88.00,
                -67.33, -89.00, -61.83, -88.00, -68.00, -89.50, -68.50, -90.66, -67.16, -88.83,
                -67.16, -87.66, -67.83, -92.66, -68.83, -91.16, -68.00, -91.00, -68.16, -90.33,
                -67.83, -91.16, -67.66, -94.83, -67.00, -91.16, -68.00, -87.83, -67.66, -90.00,
                -66.66, -90.33, -68.16, -87.66, -67.00, -88.66, -67.66, -87.50, -67.66, -88.66,
                -67.33, -89.16, -67.00, -91.33, -68.16, -89.66, -67.83, -91.00, -67.83, -89.33,
                -68.33, -88.33, -67.83, -88.16, -65.50, -86.83, -67.16, -90.33, -68.16, -86.83,
                -67.83, -89.33, -67.83, -91.33, -63.50, -89.16, -66.83, -93.00, -67.66, -89.83,
                -68.00, -89.00, -67.50, -90.00, -66.16, -89.33, -66.00, -88.83, -68.00, -88.33,
                -66.50, -88.16, -67.00, -88.66, -67.66, -91.50, -67.33, -88.83, -68.33, -90.50,
                -67.66, -88.33, -68.33, -90.66, -68.16, -89.83, -67.33, -89.83, -66.66, -91.33,
                -68.16, -90.33, -66.33, -89.33, -67.00, -89.00, -68.16, -89.16, -68.50, -90.83,
                -66.50, -89.83, -66.66, -90.33, -67.16, -90.83, -67.50, -90.16, -65.00, -89.33,
                -66.16, -86.33, -68.00, -89.50, -66.50, -89.00, -67.50, -88.33, -64.66, -90.83,
                -67.66, -88.16, -68.66, -89.00, -67.50, -91.16, -67.50, -91.33, -67.66, -92.00,
                -67.00, -89.16, -66.33, -89.50, -67.16, -89.16, -68.00, -85.83, -67.16, -89.83,
                -67.33, -89.16, -67.66, -88.83, -67.33, -90.33, -68.33, -87.83, -66.83, -89.33,
                -69.00, -90.16, -67.16, -90.16, -66.33, -92.16, -67.50, -89.66, -64.83, -90.00,
                -66.50, -88.83, -66.50, -88.33, -66.66, -89.50, -66.83, -88.83, -66.00, -88.66,
                -67.66, -89.00, -66.16, -89.00, -67.16, -90.16, -67.16, -90.50, -67.33, -89.50,
                -66.83, -89.00, -68.00, -89.50, -68.33, -89.50, -66.66, -88.50, -66.33, -89.83,
                -68.33, -89.16, -68.16, -89.33, -68.33, -88.16, -66.33, -87.50, -67.00, -90.00,
                -68.50, -86.50, -67.66, -89.00, -66.00, -88.83, -68.33, -88.66, -66.83, -87.00,
                -68.00, -88.33, -67.50, -93.83, -67.66, -88.83, -67.50, -93.00, -66.50, -89.00,
                -68.33, -91.66, -67.00, -88.83, -66.00, -92.33, -67.66, -92.66, -67.66, -92.66,
                -67.66, -88.66, -68.00, -89.83, -69.00, -89.66, -68.00, -90.00, -67.50, -90.33,
                -67.66, -91.00, -67.00, -88.16, -66.66, -92.00, -67.66, -87.16, -67.83, -89.50,
                -68.00, -91.33, -67.50, -91.00, -66.66, -86.83, -66.66, -88.50, -66.00, -89.33,
                -68.16, -90.33, -67.33, -91.83, -67.16, -90.33, -67.50, -89.00, -65.16, -89.66,
                -67.00, -91.00, -67.83, -87.83, -66.50, -91.00, -67.66, -91.16, -67.00, -88.83,
                -65.66]
        with expected_protocol(
                HP856Xx,
                [(cmd + " %s" % ','.join([str(i) for i in data]), None),
                 (cmd + "?", ','.join([str(i) for i in data]))]
        ) as instr:
            setattr(instr, function, data)
            assert getattr(instr, function) == data

    def test_fft_trace_window(self):
        with expected_protocol(
                HP856Xx,
                [("TWNDOW TRA,FLATTOP", None)]
        ) as instr:
            instr.fft_trace_window(Trace.A, WindowType.Flattop)

    @pytest.mark.parametrize("str_param", ["ON", "OFF"])
    def test_video_average(self, str_param):
        with expected_protocol(
                HP856Xx,
                [("VAVG 89", None),
                 ("VAVG " + str_param, None),
                 ("VAVG?", "89")]
        ) as instr:
            instr.video_average = 89
            instr.video_average = str_param
            assert instr.video_average == 89

    def test_video_bandwidth(self):
        with expected_protocol(
                HP856Xx,
                [("VB 70", None),
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
                [("VBR 5.000E-03", None),
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
                [("VTL -200.780", None),
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
                [("SRCPOFS 10", None),
                 ("SRCPOFS?", "10")]
        ) as instr:
            instr.source_power_offset = 10
            assert instr.source_power_offset == 10

    def test_source_power_step(self):
        with expected_protocol(
                HP8560A,
                [("SRCPSTP 10.10", None),
                 ("SRCPSTP?", "10.10")]
        ) as instr:
            instr.source_power_step = 10.1
            assert instr.source_power_step == 10.1

    def test_source_power_sweep(self):
        with expected_protocol(
                HP8560A,
                [("SRCPSWP 10.00", None),
                 ("SRCPSWP OFF", None),
                 ("SRCPSWP?", "10.00")]
        ) as instr:
            instr.source_power_sweep = 10
            instr.source_power_sweep = "OFF"
            assert instr.source_power_sweep == 10

    def test_source_power(self):
        with expected_protocol(
                HP8560A,
                [("SRCPWR 2.00", None),
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
            instr.source_peak_tracking()


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
                [("CNVLOSS 10.2", None),
                 ("CNVLOSS?", "10.3")]
        ) as instr:
            instr.conversion_loss = 10.2
            assert instr.conversion_loss == 10.3

    def test_fullband(self):
        with expected_protocol(
                HP8561B,
                [("FULLBAND K", None)]
        ) as instr:
            instr.fullband("K")

    def test_fullband_exceptions(self):
        with expected_protocol(
                HP8561B,
                []
        ) as instr:
            with pytest.raises(TypeError):
                instr.fullband(1)

            with pytest.raises(ValueError):
                instr.fullband("Z")

    @pytest.mark.parametrize("string_params", ["ON", "OFF"])
    def test_harmonic_number_lock(self, string_params):
        with expected_protocol(
                HP8561B,
                [("HNLOCK 10", None),
                 ("HNLOCK %s" % string_params, None),
                 ("HNLOCK?", "10")]
        ) as instr:
            instr.harmonic_number_lock = 10
            instr.harmonic_number_lock = string_params
            assert instr.harmonic_number_lock == 10

    @pytest.mark.parametrize(
        "function, command",
        [
            ("harmonic_number_unlock", "HUNLK"),
            ("signal_identification_to_center_frequency", "IDCF"),
            ("preselector_peak", "PP")
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

    @pytest.mark.parametrize("string_params", ["ON", "OFF"])
    def test_mixer_bias(self, string_params):
        with expected_protocol(
                HP8561B,
                [("MBIAS -9.9", None),
                 ("MBIAS %s" % string_params, None),
                 ("MBIAS?", "5.5")]
        ) as instr:
            instr.mixer_bias = -9.9
            instr.mixer_bias = string_params
            assert instr.mixer_bias == 5.5

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
