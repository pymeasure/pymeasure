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
import logging

import pytest
import numpy as np
from pymeasure.instruments.keysight.keysightDSOX1102G import KeysightDSOX1102G
from pyvisa.errors import VisaIOError

pytest.skip('Only work with connected hardware', allow_module_level=True)


class TestKeysightDSOX1102G:
    """
    Unit tests for KeysightDSOX1102G class.

    This test suite, needs the following setup to work properly:
        - A KeysightDSOX1102G device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
        - A probe on Channel 1 must be connected to the Demo output of the oscilloscope.
    """

    ##################################################
    # KeysightDSOX1102G device address goes here:
    RESOURCE = "USB0::10893::6039::CN57266430::INSTR"
    ##################################################

    #########################
    # PARAMETRIZATION CASES #
    #########################

    BOOLEANS = [False, True]
    CHANNEL_COUPLINGS = ["ac", "dc"]
    CHANNEL_LABELS = [["label", "LABEL"], ["quite long label", "QUITE LONG"],
                      [12345, "12345"]]
    TIMEBASE_MODES = ["main", "window", "xy", "roll"]
    ACQUISITION_TYPES = ["normal", "average", "hresolution", "peak"]
    ACQUISITION_MODES = ["realtime", "segmented"]
    DIGITIZE_SOURCES = ["channel1", "channel2", "function", "math", "fft",
                        "abus", "ext"]
    WAVEFORM_POINTS_MODES = ["normal", "maximum", "raw"]
    WAVEFORM_POINTS = [100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000,
                       62500]
    WAVEFORM_SOURCES = ["channel1", "channel2", "function", "fft", "wmemory1",
                        "wmemory2", "ext"]
    WAVEFORM_FORMATS = ["ascii", "word", "byte"]
    DOWNLOAD_SOURCES = ["channel1", "channel2", "function", "fft", "ext"]
    CHANNELS = [1, 2]

    SCOPE = KeysightDSOX1102G(RESOURCE)

    ############
    # FIXTURES #
    ############

    @pytest.fixture
    def make_reseted_cleared_scope(self):
        self.SCOPE.reset()
        self.SCOPE.clear_status()
        return self.SCOPE

    #########
    # TESTS #
    #########

    def test_scope_connection(self, make_reseted_cleared_scope):
        bad_resource = "USB0::10893::45848::MY12345678::0::INSTR"
        # The pure python VISA library (pyvisa-py) raises a ValueError while the
        # PyVISA library raises a VisaIOError.
        with pytest.raises((ValueError, VisaIOError)):
            KeysightDSOX1102G(bad_resource)

    def test_autoscale(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        scope.write(":timebase:position 1")
        # Autoscale should turn off the zoomed (delayed) time mode
        assert scope.ask(":timebase:position?") == "+1.000000000000E+00\n"
        scope.autoscale()
        assert scope.ask(":timebase:position?") != "+1.000000000000E+00\n"

    # Channel
    def test_ch_current_configuration(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        expected = {"OFFS": 0.0, "COUP": "DC", "IMP": "ONEM", "DISP": True,
                    "BWL": False, "INV": False, "UNIT": "VOLT", "PROB": 10.0,
                    "PROB:SKEW": 0.0, "STYP": "SING", "CHAN": 1, "RANG": 40.0}
        actual = scope.ch(1).current_configuration
        assert actual == expected

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_bwlimit(self, make_reseted_cleared_scope, ch_number, case):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).bwlimit = case
        assert scope.ch(ch_number).bwlimit == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", CHANNEL_COUPLINGS)
    def test_ch_coupling(self, make_reseted_cleared_scope, ch_number, case):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).coupling = case
        assert scope.ch(ch_number).coupling == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_display(self, make_reseted_cleared_scope, ch_number, case):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).display = case
        assert scope.ch(ch_number).display == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_invert(self, make_reseted_cleared_scope, ch_number, case):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).invert = case
        assert scope.ch(ch_number).invert == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case, expected", CHANNEL_LABELS)
    def test_ch_label(self, make_reseted_cleared_scope, ch_number, case, expected):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).label = case
        assert scope.ch(ch_number).label == expected

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_offset(self, make_reseted_cleared_scope, ch_number):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).offset = 1
        assert scope.ch(ch_number).offset == 1

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_probe_attenuation(self, make_reseted_cleared_scope, ch_number):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).probe_attenuation = 10
        assert scope.ch(ch_number).probe_attenuation == 10

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_range(self, make_reseted_cleared_scope, ch_number):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).range = 10
        assert scope.ch(ch_number).range == 10

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_scale(self, make_reseted_cleared_scope, ch_number):
        scope = make_reseted_cleared_scope
        scope.ch(ch_number).scale = 0.1
        assert scope.ch(ch_number).scale == 0.1

    # Timebase
    def test_timebase(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        expected = {"REF": "CENT", "MAIN:RANG": +1.000E-03, "POS": 0.0,
                    "MODE": "MAIN"}
        actual = scope.timebase
        assert actual == expected

    @pytest.mark.parametrize("case", TIMEBASE_MODES)
    def test_timebase_mode(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.timebase_mode = case
        assert scope.timebase_mode == case

    def test_timebase_offset(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        scope.timebase_offset = 1
        assert scope.timebase_offset == 1

    def test_timebase_range(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        scope.timebase_range = 10
        assert scope.timebase_range == 10

    def test_timebase_scale(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        scope.timebase_scale = 0.1
        assert scope.timebase_scale == 0.1

    # Acquisition
    @pytest.mark.parametrize("case", ACQUISITION_TYPES)
    def test_acquisition_type(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.acquisition_type = case
        assert scope.acquisition_type == case

    @pytest.mark.parametrize("case", ACQUISITION_MODES)
    def test_acquisition_mode(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.acquisition_mode = case
        assert scope.acquisition_mode == case

    @pytest.mark.parametrize("case", WAVEFORM_POINTS_MODES)
    def test_waveform_points_mode(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.waveform_points_mode = case
        assert scope.waveform_points_mode == case

    @pytest.mark.parametrize("case", WAVEFORM_POINTS)
    def test_waveform_points(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.waveform_points_mode = "raw"
        scope.waveform_points = case
        assert scope.waveform_points == case

    @pytest.mark.parametrize("case", WAVEFORM_SOURCES)
    def test_waveform_source(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.waveform_source = case
        assert scope.waveform_source == case

    @pytest.mark.parametrize("case", WAVEFORM_FORMATS)
    def test_waveform_format(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        scope.waveform_format = case
        assert scope.waveform_format == case

    def test_waveform_preamble(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        scope.waveform_format = "ascii"
        scope.waveform_source = "channel1"
        expected_preamble = {"count": 1, "format": "ASCII", "points": 62500,
                             "type": "NORMAL", "xincrement": 1.6e-08, "xorigin": -0.0005,
                             "xreference": 0, "yincrement": 0.0007851759,
                             "yorigin": 0, "yreference": 32768.0}
        preamble = scope.waveform_preamble
        assert preamble == expected_preamble

    @pytest.mark.parametrize("case", DIGITIZE_SOURCES)
    def test_digitize(self, make_reseted_cleared_scope, case):
        scope = make_reseted_cleared_scope
        # Here, we only assert that no error arrises when using the expected parameters.
        # Success of digitize operation is evaluated through test_waveform_data
        scope.digitize(case)
        sleep(2)  # Account for Digitize operation duration

    def test_waveform_data(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        scope.digitize("channel1")
        sleep(2)  # Account for Digitize operation duration
        scope.waveform_format = "ascii"
        value = scope.waveform_data
        assert type(value) is list
        assert len(value) > 0
        assert all(isinstance(n, float) for n in value)

    def test_system_setup(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        initial_setup = scope.system_setup
        scope.ch(1).display = not scope.ch(1).display
        scope.ch(2).display = not scope.ch(2).display
        # Assert that setup block is different
        assert scope.system_setup != initial_setup
        # Assert that the setup was successful
        scope.system_setup = initial_setup
        assert scope.system_setup == initial_setup

    # Setup methods
    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_channel_setup(self, make_reseted_cleared_scope, ch_number, caplog):
        # Using caplog to check content of log.
        caplog.set_level(logging.WARNING)
        scope = make_reseted_cleared_scope

        # Not testing the actual values assignment since different combinations of
        # parameters can play off each other.
        expected = scope.ch(ch_number).current_configuration
        scope.ch(ch_number).setup()
        assert scope.ch(ch_number).current_configuration == expected
        with pytest.raises(ValueError):
            scope.ch(3)
        scope.ch(ch_number).setup(1, vertical_range=1, scale=1)
        assert 'Both "vertical_range" and "scale" are specified. Specified "scale" has priority.' in caplog.text  # noqa

    def test_timebase_setup(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        expected = scope.timebase
        scope.timebase_setup()
        assert scope.timebase == expected

    # Download methods
    def test_download_image_default_arguments(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        img = scope.download_image()
        assert type(img) is bytearray

    @pytest.mark.parametrize("format", ["bmp", "bmp8bit", "png"])
    @pytest.mark.parametrize("color_palette", ["color", "grayscale"])
    def test_download_image(self, make_reseted_cleared_scope, format, color_palette):
        scope = make_reseted_cleared_scope
        img = scope.download_image(format_=format, color_palette=color_palette)
        assert type(img) is bytearray

    def test_download_data_missingArgument(self, make_reseted_cleared_scope):
        scope = make_reseted_cleared_scope
        with pytest.raises(TypeError):
            scope.download_data()

    @pytest.mark.parametrize("case1", DOWNLOAD_SOURCES)
    @pytest.mark.parametrize("case2", WAVEFORM_POINTS)
    def test_download_data(self, make_reseted_cleared_scope, case1, case2):
        scope = make_reseted_cleared_scope
        data, preamble = scope.download_data(source=case1, points=case2)
        assert type(data) is np.ndarray
        # Returned length is not always as specified. Problem seems to be from scope itself.
        # assert len(data) == case2
        assert type(preamble) is dict
