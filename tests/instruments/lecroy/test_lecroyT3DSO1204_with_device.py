#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from time import sleep

import numpy as np
import pytest
from pyvisa.errors import VisaIOError

from pymeasure.instruments.lecroy.lecroyT3DSO1204 import LeCroyT3DSO1204

pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestLeCroyT3DSO1204:
    """
    Unit tests for LeCroyT3DSO1204 class.

    This test suite, needs the following setup to work properly:
        - A LeCroyT3DSO1204 device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
        - A probe on Channel 1 must be connected to the Demo output of the oscilloscope.
    """

    ##################################################
    # LeCroyT3DSO1204 device address goes here:
    RESOURCE = "TCPIP::192.168.10.175::INSTR"
    ##################################################

    #########################
    # PARAMETRIZATION CASES #
    #########################

    BOOLEANS = [False, True]
    CHANNEL_COUPLINGS = ["AC 1M", "DC 1M", "GND"]
    ACQUISITION_TYPES = ["normal", "average", "peak", "highres"]
    TRIGGER_LEVELS = [0.125, 0.150, 0.175]
    TRIGGER_SLOPES = ["negative", "positive", "window"]
    ACQUISITION_AVERAGE = [4, 16, 32, 64, 128, 256]
    WAVEFORM_POINTS = [100, 1000, 10000]
    WAVEFORM_SOURCES = ["C1", "C2", "C3", "C4"]
    CHANNELS = [1, 2, 3, 4]

    SCOPE = LeCroyT3DSO1204(RESOURCE)

    ############
    # FIXTURES #
    ############

    @pytest.fixture
    def make_scope(self):
        return self.SCOPE

    @pytest.fixture
    def make_reseted_scope(self):
        self.SCOPE.reset()
        sleep(7)
        return self.SCOPE

    @pytest.fixture
    def make_autoscale_scope(self):
        self.SCOPE.reset()
        sleep(7)
        self.SCOPE.autoscale()
        sleep(7)
        return self.SCOPE

    #########
    # TESTS #
    #########

    # noinspection PyTypeChecker
    def test_scope_connection(self):
        bad_resource = "USB0::10893::45848::MY12345678::0::INSTR"
        # The pure python VISA library (pyvisa-py) raises a ValueError while the
        # PyVISA library raises a VisaIOError.
        with pytest.raises((ValueError, VisaIOError)):
            LeCroyT3DSO1204(bad_resource)

    # Channel
    def test_ch_current_configuration(self, make_autoscale_scope):
        scope = make_autoscale_scope
        scope.ch1.offset = 0
        expected = {"channel": 1,
                    "attenuation": 1.,
                    "bandwidth_limit": False,
                    "coupling": "DC 1M",
                    "offset": 0.,
                    "skew_factor": 0.,
                    "display": True,
                    "unit": "V",
                    "volts_div": 0.05,
                    "inverted": False,
                    "trigger_coupling": "dc",
                    "trigger_level": 0.150,
                    "trigger_level2": 0.150,
                    "trigger_slope": "positive"
                    }
        sleep(1)
        actual = scope.ch(1).current_configuration
        assert actual == expected

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_bwlimit(self, make_scope, ch_number, case):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).bwlimit = case
        sleep(1)
        assert scope.ch(ch_number).bwlimit == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", CHANNEL_COUPLINGS)
    def test_ch_coupling(self, make_scope, ch_number, case):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).coupling = case
        sleep(1)
        assert scope.ch(ch_number).coupling == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_display(self, make_scope, ch_number, case):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).display = case
        sleep(1)
        assert scope.ch(ch_number).display == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_invert(self, make_scope, ch_number, case):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).invert = case
        sleep(1)
        assert scope.ch(ch_number).invert == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_offset(self, make_scope, ch_number):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).offset = 1
        sleep(1)
        assert scope.ch(ch_number).offset == 1

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_probe_attenuation(self, make_scope, ch_number):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).probe_attenuation = 10
        sleep(1)
        assert scope.ch(ch_number).probe_attenuation == 10

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_scale(self, make_scope, ch_number):
        scope = make_scope
        sleep(1)
        scope.ch(ch_number).scale = 1
        sleep(1)
        assert scope.ch(ch_number).scale == 1

    def test_ch_trigger_level(self, make_autoscale_scope):
        scope = make_autoscale_scope
        for case in self.TRIGGER_LEVELS:
            sleep(1)
            scope.ch1.trigger_level = case
            sleep(1)
            assert scope.ch1.trigger_level == case

    def test_ch_trigger_level2(self, make_autoscale_scope):
        scope = make_autoscale_scope
        for case in self.TRIGGER_LEVELS:
            sleep(1)
            scope.ch1.trigger_level2 = case
            sleep(1)
            assert scope.ch1.trigger_level2 == case

    def test_ch_trigger_slope(self, make_autoscale_scope):
        scope = make_autoscale_scope
        with pytest.raises(ValueError):
            scope.ch1.trigger_slope = "abcd"
        sleep(1)
        scope.trigger_select = ("edge", "C1", "OFF")
        for case in self.TRIGGER_SLOPES:
            sleep(1)
            scope.ch1.trigger_slope = case
            sleep(1)
            assert scope.ch1.trigger_slope == case

    # Timebase
    def test_timebase(self, make_autoscale_scope):
        scope = make_autoscale_scope
        scope.timebase_hor_magnify = 5e-6
        sleep(1)
        scope.timebase_hor_position = 0
        sleep(1)
        expected = {
            "seconds_div": 5e-4,
            "delay": 0.,
            "hor_magnify": 5e-6,
            "hor_position": 0.
        }
        actual = scope.timebase
        for key, val in actual.items():
            assert pytest.approx(val, 0.1) == expected[key]

    def test_timebase_scale(self, make_reseted_scope):
        scope = make_reseted_scope
        sleep(1)
        scope.timebase_scale = 1e-3
        sleep(1)
        assert scope.timebase_scale == 1e-3

    def test_timebase_offset(self, make_scope):
        scope = make_scope
        sleep(1)
        scope.timebase_offset = 1e-3
        sleep(1)
        assert scope.timebase_offset == 1e-3

    def test_timebase_hor_magnify(self, make_scope):
        scope = make_scope
        sleep(1)
        scope.timebase_hor_magnify = 1e-4
        sleep(1)
        assert scope.timebase_hor_magnify == 1e-4

    def test_timebase_hor_position(self, make_scope):
        scope = make_scope
        sleep(1)
        scope.timebase_hor_position = 5e-4
        sleep(1)
        assert pytest.approx(scope.timebase_hor_position, 0.1) == 5e-4

    # Acquisition
    @pytest.mark.parametrize("case", ACQUISITION_TYPES)
    def test_acquisition_type(self, make_reseted_scope, case):
        scope = make_reseted_scope
        if case == "average":
            sleep(1)
            scope.acquisition_type = case
            sleep(1)
            scope.acquisition_average = 16
            assert scope.acquisition_type == ["AVERAGE", 16]
        else:
            sleep(1)
            scope.acquisition_type = case
            sleep(1)
            assert scope.acquisition_type == case

    @pytest.mark.parametrize("case", ACQUISITION_AVERAGE)
    def test_acquisition_average(self, make_scope, case):
        scope = make_scope
        sleep(1)
        scope.acquisition_average = case
        sleep(1)
        assert scope.acquisition_average == case

    def test_acquisition_status(self, make_autoscale_scope):
        scope = make_autoscale_scope
        sleep(1)
        assert scope.acquisition_status == "triggered"
        sleep(1)
        scope.stop()
        sleep(1)
        assert scope.acquisition_status == "stopped"

    def test_acquisition_sampling_rate(self, make_reseted_scope):
        scope = make_reseted_scope
        sleep(1)
        assert scope.acquisition_sampling_rate == 1e9

    @pytest.mark.parametrize("case", WAVEFORM_POINTS)
    def test_waveform_points(self, make_scope, case):
        scope = make_scope
        sleep(1)
        scope.waveform_points = case
        sleep(1)
        vals = scope.waveform_points
        # noinspection PyUnresolvedReferences
        assert vals[vals.index("NP") + 1] == case

    def test_waveform_preamble(self, make_autoscale_scope):
        scope = make_autoscale_scope
        sleep(1)
        scope.ch1.offset = 0
        sleep(1)
        scope.waveform_points = 0
        scope.waveform_first_point = 0
        scope.waveform_sparsing = 1
        scope.waveform_source = "C1"
        expected_preamble = {
            "sparsing": 1,
            "points": 0,
            "first_point": 0,
            "source": scope.waveform_source,
            "type": "normal",
            "average": 16,
            "sampling_rate": 250e6,
            "status": "triggered",
            "xdiv": 5e-4,
            "xoffset": -0.,
            "ydiv": 0.05,
            "yoffset": 0.
        }
        preamble = scope.waveform_preamble
        assert preamble == expected_preamble

    def test_waveform_data(self, make_scope):
        scope = make_scope
        sleep(1)
        scope.waveform_first_point = 0
        sleep(1)
        scope.waveform_points = 1000
        sleep(1)
        scope.waveform_sparsing = 1
        sleep(1)
        scope.single()
        sleep(1)
        value = scope.digitize("C1")
        assert isinstance(value, np.ndarray)
        assert len(value) == 1000
        assert all(isinstance(n, np.uint8) for n in value)

    # Setup methods
    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_channel_setup(self, make_scope, ch_number):
        # Only autoscale on the first channel
        scope = make_scope
        if ch_number == self.CHANNELS[0]:
            scope.reset()
            sleep(7)
            scope.autoscale()
            sleep(7)

        # Not testing the actual values assignment since different combinations of
        # parameters can play off each other.
        sleep(1)
        expected = scope.ch(ch_number).current_configuration
        sleep(1)
        scope.ch(ch_number).setup()
        sleep(1)
        assert scope.ch(ch_number).current_configuration == expected
        with pytest.raises(ValueError):
            scope.ch(5)
        sleep(1)
        scope.ch(ch_number).setup(
            bwlimit=False,
            coupling="DC 1M",
            display=True,
            invert=False,
            offset=0.,
            skew_factor=0.,
            probe_attenuation=1.,
            scale=0.05,
            unit="V",
            trigger_coupling="dc",
            trigger_level=0.150,
            trigger_level2=0.150,
            trigger_slope="positive"
        )
        expected = {"channel": ch_number,
                    "attenuation": 1.,
                    "bandwidth_limit": False,
                    "coupling": "DC 1M",
                    "offset": 0.,
                    "skew_factor": 0.,
                    "display": True,
                    "unit": "V",
                    "volts_div": 0.05,
                    "inverted": False,
                    "trigger_coupling": "dc",
                    "trigger_level": 0.150,
                    "trigger_level2": 0.150,
                    "trigger_slope": "positive"
                    }
        sleep(1)
        actual = scope.ch(ch_number).current_configuration
        assert actual == expected

    def test_timebase_setup(self, make_reseted_scope):
        scope = make_reseted_scope
        expected = scope.timebase
        scope.timebase_setup()
        assert scope.timebase == expected

    # Download methods
    def test_download_image_default_arguments(self, make_autoscale_scope):
        scope = make_autoscale_scope
        img = scope.download_image()
        assert type(img) is bytearray
        assert pytest.approx(len(img), 0.1) == 768067

    def test_download_data_missingArgument(self, make_reseted_scope):
        scope = make_reseted_scope
        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            scope.download_data()

    @pytest.mark.parametrize("case1", WAVEFORM_SOURCES)
    @pytest.mark.parametrize("case2", WAVEFORM_POINTS)
    def test_download_data(self, make_scope, case1, case2):
        scope = make_scope
        if case1 == self.WAVEFORM_SOURCES[0] and case2 == self.WAVEFORM_POINTS[0]:
            scope.reset()
            sleep(7)
            scope.autoscale()
            sleep(7)
        scope.ch(case1).display = True
        sleep(1)
        scope.single()
        sleep(1)
        data, preamble = scope.download_data(source=case1, points=case2, sparsing=1, first_point=1)
        assert type(data) is np.ndarray
        assert len(data) == case2
        assert type(preamble) is dict
        sleep(2)

    # Trigger
    def test_trigger_select(self, make_scope):
        scope = make_scope
        with pytest.raises(ValueError):
            scope.trigger_select = "edge"
        with pytest.raises(ValueError):
            scope.trigger_select = ("edge", "c2")
        with pytest.raises(ValueError):
            scope.trigger_select = ("edge", "c2", "time")
        with pytest.raises(ValueError):
            scope.trigger_select = ("ABCD", "c1", "time", 0)
        with pytest.raises(ValueError):
            scope.trigger_select = ("edge", "c1", "time", 1000)
        with pytest.raises(ValueError):
            scope.trigger_select = ("edge", "c1", "time", 0, 1)
        sleep(1)
        scope.trigger_select = ("edge", "c1", "off")
        sleep(1)
        scope.trigger_select = ("EDGE", "C1", "OFF")
        sleep(1)
        assert scope.trigger_select == ["edge", "c1", "off"]
        scope.trigger_select = ("glit", "c1", "p2", 1e-3, 2e-3)
        sleep(1)
        assert scope.trigger_select == ["glit", "c1", "p2", 1e-3, 2e-3]

    def test_trigger_setup(self, make_reseted_scope):
        scope = make_reseted_scope
        expected = scope.trigger
        scope.trigger_setup(**expected)
        assert scope.trigger == expected


if __name__ == '__main__':
    pytest.main()
