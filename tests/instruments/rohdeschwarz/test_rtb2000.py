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

from pymeasure.test import expected_protocol

from pymeasure.instruments.rohdeschwarz.rtb2000 import RTB200X, RTB2004, Coupling, Bandwidth, \
    WaveformColor, ThresholdHysteresis

from pymeasure.instruments.rohdeschwarz.rtb2000 import AcquisitionState


class TestRTB200X:

    @pytest.mark.parametrize("enum", [e for e in AcquisitionState])
    def test_acquisition_state(self, enum):
        with expected_protocol(
                RTB200X,
                [
                    ("ACQuire:STATe %s" % enum, None),
                    ("ACQuire:STATe?", enum)
                ],
        ) as instr:
            instr.acquisition_state = enum
            assert instr.acquisition_state == enum

    def test_autoscale(self):
        with expected_protocol(
                RTB200X,
                [
                    ("AUToscale", None)
                ],
        ) as instr:
            instr.autoscale()


class TestRTB200XAnalogChannel:
    DUT = RTB2004

    @pytest.mark.parametrize("on_off,state", [("ON", True), ("OFF", False)])
    def test_on_off(self, on_off, state):
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:STATe %s" % on_off, None),
                    ("CHANnel1:STATe?", on_off)
                ],
        ) as instr:
            instr.ch1.state = state
            assert instr.ch1.state == state

    @pytest.mark.parametrize("attr,value,command", [
        ("scale", 2.0, "SCALe"),
        ("range", 2.0, "RANGe"),
        ("position", 5, "POSition"),
        ("offset", 2, "OFFSet"),
        ("skew", 2, "SKEW"),
        ("zero_offset", 2, "ZOFFset"),
        ("threshold", 2, "THReshold")
    ])
    def test_value_control(self, attr, value, command):
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:%s %g" % (command, value), None),
                    ("CHANnel1:%s?" % command, value)
                ],
        ) as instr:
            setattr(instr.ch1, attr, value)
            assert getattr(instr.ch1, attr) == value

    @pytest.mark.parametrize("enum,attr,command", [
        (Coupling, "coupling", "COUPling"),
        (Bandwidth, "bandwidth", "BANDwidth"),
        (WaveformColor, "waveform_color", "WCOLor"),
        (ThresholdHysteresis, "threshold_hysteresis", "THReshold:HYSTeresis")
    ])
    def test_enumeration_attributes(self, enum, attr, command):
        value = [e for e in enum][0]
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:%s %s" % (command, value), None),
                    ("CHANnel1:%s?" % command, value)
                ],
        ) as instr:
            setattr(instr.ch1, attr, value)
            assert getattr(instr.ch1, attr) == value

    @pytest.mark.parametrize("on_off,state", [("INV", True), ("NORM", False)])
    def test_polarity_inversion_active(self, on_off, state):
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:POLarity %s" % on_off, None),
                    ("CHANnel1:POLarity?", on_off)
                ],
        ) as instr:
            instr.ch1.polarity_inversion_active = state
            assert instr.ch1.polarity_inversion_active == state

    def test_find_threshold(self):
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:THReshold:FINDlevel", None)
                ],
        ) as instr:
            instr.ch1.find_threshold()

    def test_label(self):
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:LABel ABCDEFGH", None)
                ],
        ) as instr:
            instr.ch1.label = "ABCDEFGH"

class TestGeneral:
    @pytest.mark.parametrize("channel", ["ch1", "ch2", "ch3", "ch4"])
    def test_rtb2004_channels(self, channel):
        with expected_protocol(
                RTB2004,
                []
        ) as instr:
            assert hasattr(instr, channel)

    @pytest.mark.parametrize("channel", ["ch1", "ch2"])
    def test_rtb2002_channels(self, channel):
        with expected_protocol(
                RTB2004,
                []
        ) as instr:
            assert hasattr(instr, channel)
