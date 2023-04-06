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
import pytest
from _decimal import Decimal

from pymeasure.test import expected_protocol

from pymeasure.instruments.hp import HP8560A, HP8561B
from pymeasure.instruments.hp.hp856Xx import Trace, MixerMode, CouplingMode, DemodulationMode, \
    DetectionModes, AmplitudeUnits
from pymeasure.instruments.hp.hp856Xx import HP856Xx


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
                 ("AT?", "70"),
                 ("AT AUTO", None),
                 ("AT?", "20"),
                 ("AT DN", None),
                 ("AT?", "10"),
                 ("AT UP", None),
                 ("AT?", "20"),
                 ("AT 20", None),
                 ("AT?", "20")],
        ) as instr:
            # test set and get of attenuation as integer
            instr.attenuation = 70
            assert instr.attenuation == 70
            # test string parameters
            instr.attenuation = "AUTO"
            assert instr.attenuation == 20
            instr.attenuation = "DN"
            assert instr.attenuation == 10
            instr.attenuation = "UP"
            assert instr.attenuation == 20
            # test truncation
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
        "function,command",
        [
            ("auto_couple", "AUTOCPL"),
            ("exchange_traces", "AXB"),
            ("subtract_display_line_from_trace_b", "BML"),
            ("continuous_sweep", "CONTS")
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

    @pytest.mark.parametrize("up_down", ["UP", "DN"])
    @pytest.mark.parametrize("hp_derivat,max_freq", [(HP8560A, 2.9e9), (HP8561B, 6.5e9)])
    def test_freq_center(self, hp_derivat, max_freq, up_down):
        with expected_protocol(
                hp_derivat,
                [("CF %s HZ" % ('%.11E' % Decimal(max_freq)).replace('+', ''), None),
                 ("CF " + up_down, None),
                 ("CF?", ('%.11E' % Decimal(max_freq)).replace('+', ''))]
        ) as instr:
            instr.freq_center = max_freq
            # TODO test external mixer mode of HP8561B
            instr.freq_center = up_down
            assert instr.freq_center == max_freq

    @pytest.mark.parametrize("trace", [e for e in Trace])
    def test_clear_write_trace(self, trace):
        with expected_protocol(
                HP856Xx,
                [("CLRW " + trace, None)]
        ) as instr:
            instr.clear_write_trace(trace)

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

    @pytest.mark.parametrize("up_down", ["UP", "DN"])
    def test_demodulation_time(self, up_down):
        with expected_protocol(
                HP8561B,
                [("DEMODT 1.02000000000E01", None),
                 ("DEMODT " + up_down, None),
                 ("DEMODT?", "1.03000000000E01")]
        ) as instr:
            instr.demodulation_time = 10.2
            instr.demodulation_time = up_down
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

    @pytest.mark.parametrize("up_down", ["UP", "DN"])
    def test_conversion_loss(self, up_down):
        with expected_protocol(
                HP8561B,
                [("CNVLOSS 10.2 DB", None),
                 ("CNVLOSS " + up_down, None),
                 ("CNVLOSS?", "10.3")]
        ) as instr:
            instr.conversion_loss = 10.2
            instr.conversion_loss = up_down
            assert instr.conversion_loss == 10.3
