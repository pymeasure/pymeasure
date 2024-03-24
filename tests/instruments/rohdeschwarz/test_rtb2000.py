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
    WaveformColor, ThresholdHysteresis, DecimationMode, AcquisitionMode, ArithmeticMethod, \
    InterpolationMode

from pymeasure.instruments.rohdeschwarz.rtb2000 import AcquisitionState

CHECK_ERROR = ("SYST:ERR?", "0,\"No error\"")


class TestRTB200X:

    @pytest.mark.parametrize("enum,attr,command", [
        (AcquisitionState, "acquisition_state", "ACQuire:STATe"),
        (AcquisitionMode, "acquisition_mode", "ACQuire:TYPE"),
        (InterpolationMode, "interpolation_mode", "ACQuire:INTerpolate")
    ])
    def test_enumeration_attributes(self, enum, attr, command):
        value = [e for e in enum][0]
        with expected_protocol(
                RTB200X,
                [
                    ("%s %s" % (command, value), None),
                    CHECK_ERROR,
                    ("%s?" % command, value)
                ],
        ) as instr:
            setattr(instr, attr, value)
            assert getattr(instr, attr) == value

    def test_autoscale(self):
        with expected_protocol(
                RTB200X,
                [
                    ("AUToscale", None)
                ],
        ) as instr:
            instr.autoscale()

    @pytest.mark.parametrize("attr,value,command", [
        ("horizontal_scale", 2, "TIMebase:SCALe"),
        ("horizontal_position", 2, "TIMebase:POSition"),
        ("timebase_reference", 50, "TIMebase:REFerence"),
        ("acquisition_time", 1, "TIMebase:ACQTime"),
        ("acquisition_points", 10000, "ACQuire:POINts:VALue"),
        ("acquisition_count", 10, "ACQuire:NSINgle:COUNt"),
        ("acquisition_average_count", 10, "ACQuire:AVERage:COUNt"),
        ("roll_minimum_time", 10, "TIMebase:ROLL:MTIMe")
    ])
    def test_value_control(self, attr, value, command):
        with expected_protocol(
                RTB200X,
                [
                    ("%s %s" % (command, str(value)), None),
                    CHECK_ERROR,
                    ("%s?" % command, value)
                ],
        ) as instr:
            setattr(instr, attr, value)
            assert getattr(instr, attr) == value

    @pytest.mark.parametrize("attr,value,command", [
        ("horizontal_divisions", 12, "TIMebase:DIVisions"),
        ("adc_sample_rate", 10000000, "ACQuire:POINts:ARATe"),
        ("sample_rate", 1000000, "ACQuire:SRATe")
    ])
    def test_value_measure(self, attr, value, command):
        with expected_protocol(
                RTB200X,
                [
                    ("%s?" % command, value)
                ],
        ) as instr:
            assert getattr(instr, attr) == value

    @pytest.mark.parametrize("attr, command", [
        ("acquisition_points_automatic", "ACQuire:POINts:AUTomatic"),
        ("roll_automatic_enabled", "TIMebase:ROLL:AUTomatic")
    ])
    @pytest.mark.parametrize("on_off,state", [("ON", True), ("OFF", False)])
    def test_on_off(self, on_off, state, attr, command):
        with expected_protocol(
                RTB200X,
                [
                    ("%s %s" % (command, on_off), None),
                    CHECK_ERROR,
                    ("%s?" % command, on_off)
                ],
        ) as instr:
            setattr(instr, attr, state)
            assert getattr(instr, attr) == state

    def test_average_complete(self):
        with expected_protocol(
                RTB200X,
                [
                    ("ACQuire:AVERage:COMPlete?", "1")
                ],
        ) as instr:
            assert instr.average_complete is True


class TestRTB200XAnalogChannel:
    DUT = RTB2004

    @pytest.mark.parametrize("attr, command", [
        ("state", "STATe"),
        ("label_active", "LABel:STATe")
    ])
    @pytest.mark.parametrize("on_off,state", [("ON", True), ("OFF", False)])
    def test_on_off(self, on_off, state, attr, command):
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:%s %s" % (command, on_off), None),
                    CHECK_ERROR,
                    ("CHANnel1:%s?" % command, on_off)
                ],
        ) as instr:
            setattr(instr.ch1, attr, state)
            assert getattr(instr.ch1, attr) == state

    @pytest.mark.parametrize("attr,value,command", [
        ("vertical_scale", 2, "CHANnel1:SCALe"),
        ("vertical_range", 2, "CHANnel1:RANGe"),
        ("vertical_position", 5, "CHANnel1:POSition"),
        ("vertical_offset", 2, "CHANnel1:OFFSet"),
        ("skew", 2, "CHANnel1:SKEW"),
        ("zero_offset", 2, "CHANnel1:ZOFFset"),
        ("threshold", 2, "CHANnel1:THReshold"),
        ("probe_unit", "V", "PROBe1:SETup:ATTenuation:UNIT"),
        ("probe_attenuation", 10, "PROBe1:SETup:ATTenuation:MANual"),
        ("probe_gain", 10, "PROBe1:SETup:GAIN:MANual")
    ])
    def test_value_control(self, attr, value, command):
        with expected_protocol(
                self.DUT,
                [
                    ("%s %s" % (command, str(value)), None),
                    CHECK_ERROR,
                    ("%s?" % command, value)
                ],
        ) as instr:
            setattr(instr.ch1, attr, value)
            assert getattr(instr.ch1, attr) == value

    @pytest.mark.parametrize("enum,attr,command", [
        (Coupling, "coupling", "COUPling"),
        (Bandwidth, "bandwidth", "BANDwidth"),
        (WaveformColor, "waveform_color", "WCOLor"),
        (ThresholdHysteresis, "threshold_hysteresis", "THReshold:HYSTeresis"),
        (DecimationMode, "decimation_mode", "TYPE"),
        (ArithmeticMethod, "arithmetics", "ARIThmetics")
    ])
    def test_enumeration_attributes(self, enum, attr, command):
        value = [e for e in enum][0]
        with expected_protocol(
                self.DUT,
                [
                    ("CHANnel1:%s %s" % (command, value), None),
                    CHECK_ERROR,
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
                    CHECK_ERROR,
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
                    ("CHANnel1:LABel \"ABCDEFGH\"", None),
                    CHECK_ERROR
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
