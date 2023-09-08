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

from time import sleep

from pymeasure.instruments.teledyne import TeledyneMAUI


class TestTeledyneMAUI:
    """
    Unit tests for TeledyneMAUI class.

    This test suite needs an actual device connected, compatible with the MAUI interface.
    Use the ``--device-address`` flag for pytest to define your device.
    """

    #########################
    # PARAMETRIZATION CASES #
    #########################

    BOOLEANS = [False, True]
    BANDWIDTH_LIMITS = ["OFF", "ON", "200MHZ"]
    CHANNEL_COUPLINGS = ["ac 1M", "dc 1M", "ground"]
    ACQUISITION_TYPES = ["normal", "average", "peak", "highres"]
    TRIGGER_LEVELS = [0.125, 0.150, 0.175]
    TRIGGER_SLOPES = ["negative", "positive"]
    ACQUISITION_AVERAGE = [4, 16, 32, 64, 128, 256]
    WAVEFORM_POINTS = [100, 1000, 10000]
    WAVEFORM_SOURCES = ["C1", "C2", "C3", "C4"]
    CHANNELS = [1, 2, 3, 4]

    ############
    # FIXTURES #
    ############

    @pytest.fixture(scope="module")
    def instrument(self, connected_device_address):
        return TeledyneMAUI(connected_device_address)

    @pytest.fixture
    def resetted_instrument(self, instrument):
        instrument.reset()
        sleep(7)
        return instrument

    @pytest.fixture
    def autoscaled_instrument(self, instrument):
        instrument.reset()
        sleep(7)
        instrument.autoscale()
        sleep(7)
        return instrument

    #########
    # TESTS #
    #########

    def test_instrument_connection(self, connected_device_address):
        instrument = TeledyneMAUI(connected_device_address)
        channel = instrument.ch(1)
        assert channel is not None

    def test_channel_autoset(self, instrument):
        instrument.ch(1).autoscale()
        sleep(0.1)

    def test_channel_measure_parameter(self, instrument):
        instrument.ch(1).measure_parameter("RMS")
        sleep(0.1)

    # Channel
    def test_ch_current_configuration(self, autoscaled_instrument):
        autoscaled_instrument.ch_1.offset = 0
        autoscaled_instrument.ch_1.trigger_level = 0
        expected = {
            "channel": 1,
            "attenuation": 1.0,
            "bandwidth_limit": "OFF",
            "coupling": "dc 1M",
            "offset": 0.0,
            "display": True,
            "volts_div": 0.05,
            "trigger_coupling": "dc",
            "trigger_level": 0.0,
            "trigger_slope": "positive",
        }
        actual = autoscaled_instrument.ch(1).current_configuration
        assert actual == expected

    @pytest.mark.parametrize("case", BANDWIDTH_LIMITS)
    def test_ch_bwlimit(self, instrument, case):
        instrument.bwlimit = case
        expected = {ch: case for ch in self.WAVEFORM_SOURCES}
        assert instrument.bwlimit == expected

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BANDWIDTH_LIMITS)
    def test_ch_bwlimit_channel(self, instrument, ch_number, case):
        instrument.ch(ch_number).bwlimit = case
        assert instrument.bwlimit[f"C{ch_number}"] == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", CHANNEL_COUPLINGS)
    def test_ch_coupling(self, instrument, ch_number, case):
        instrument.ch(ch_number).coupling = case
        assert instrument.ch(ch_number).coupling == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_display(self, instrument, ch_number, case):
        instrument.ch(ch_number).display = case
        assert instrument.ch(ch_number).display == case

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_offset(self, instrument, ch_number):
        instrument.ch(ch_number).offset = 1
        assert instrument.ch(ch_number).offset == 1

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_probe_attenuation(self, instrument, ch_number):
        instrument.ch(ch_number).probe_attenuation = 10
        assert instrument.ch(ch_number).probe_attenuation == 10

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_ch_scale(self, instrument, ch_number):
        instrument.ch(ch_number).scale = 1
        assert instrument.ch(ch_number).scale == 1

    def test_ch_trigger_level(self, autoscaled_instrument):
        for case in self.TRIGGER_LEVELS:
            autoscaled_instrument.ch_1.trigger_level = case
            assert autoscaled_instrument.ch_1.trigger_level == case

    def test_ch_trigger_slope(self, autoscaled_instrument):
        with pytest.raises(ValueError):
            autoscaled_instrument.ch_1.trigger_slope = "abcd"
        autoscaled_instrument.trigger_select = ("edge", "c1", "off")
        for case in self.TRIGGER_SLOPES:
            autoscaled_instrument.ch_1.trigger_slope = case
            assert autoscaled_instrument.ch_1.trigger_slope == case

    # Timebase

    def test_timebase(self, autoscaled_instrument):
        autoscaled_instrument.timebase_scale = 5e-4
        autoscaled_instrument.timebase_offset = 0
        expected = {
            "timebase_scale": 5e-4,
            "timebase_offset": 0.0,
        }
        actual = autoscaled_instrument.timebase
        for key, val in actual.items():
            assert pytest.approx(val, 0.1) == expected[key]

    def test_timebase_scale(self, resetted_instrument):
        resetted_instrument.timebase_scale = 1e-3
        assert resetted_instrument.timebase_scale == 1e-3

    def test_timebase_offset(self, instrument):
        instrument.timebase_offset = 1e-3
        assert instrument.timebase_offset == 1e-3

    # Acquisition

    @pytest.mark.parametrize("case", WAVEFORM_POINTS)
    def test_waveform_points(self, instrument, case):
        instrument.waveform_points = case
        assert instrument.waveform_points == case

    def test_waveform_preamble(self, autoscaled_instrument):
        autoscaled_instrument.ch_1.offset = 0
        autoscaled_instrument.waveform_points = 0
        autoscaled_instrument.waveform_first_point = 0
        autoscaled_instrument.waveform_sparsing = 1
        autoscaled_instrument.waveform_source = "C1"
        expected_preamble = {
            "sparsing": 1.0,
            "requested_points": 0.0,
            "memory_size": 2.5e6,
            "transmitted_points": None,
            "first_point": 0.0,
            "source": "C1",
            "grid_number": 14,
            "xdiv": 1e-6,
            "xoffset": 0.0,
            "ydiv": 0.05,
            "yoffset": 0.0,
        }
        preamble = autoscaled_instrument.waveform_preamble
        assert preamble == expected_preamble

    # Setup methods

    @pytest.mark.parametrize("ch_number", CHANNELS)
    def test_channel_setup(self, instrument, ch_number):
        # Only autoscale on the first channel
        instrument = instrument
        if ch_number == self.CHANNELS[0]:
            instrument.reset()
            sleep(7)
            instrument.autoscale()
            sleep(7)

        # Not testing the actual values assignment since different combinations of
        # parameters can play off each other.
        expected = instrument.ch(ch_number).current_configuration
        instrument.ch(ch_number).setup()
        assert instrument.ch(ch_number).current_configuration == expected
        with pytest.raises(AttributeError):
            instrument.ch(5)
        instrument.ch(ch_number).setup(
            bwlimit="ON",
            coupling="dc 1M",
            display=True,
            offset=0.0,
            probe_attenuation=1.0,
            scale=0.05,
            trigger_coupling="dc",
            trigger_level=0.150,
            trigger_slope="positive",
        )
        expected = {
            "channel": ch_number,
            "attenuation": 1.0,
            "bandwidth_limit": "ON",
            "coupling": "dc 1M",
            "offset": 0.0,
            "display": True,
            "volts_div": 0.05,
            "trigger_coupling": "dc",
            "trigger_level": 0.150,
            "trigger_slope": "positive",
        }
        actual = instrument.ch(ch_number).current_configuration
        assert actual == expected

    def test_timebase_setup(self, resetted_instrument):
        expected = resetted_instrument.timebase
        resetted_instrument.timebase_setup()
        assert resetted_instrument.timebase == expected

    # Download methods

    def test_hardcopy_setup(self, instrument):

        instrument.hardcopy_setup(
            device="BMP", format="PORTRAIT", background="Std", destination="FILE",
            area="GRIDONLY", directory="D:\\Waveforms\\temp"
        )
        config_expected = {
            "DEV": "BMP", "FORMAT": "PORTRAIT", "BCKG": "Std", "DEST": "FILE",
            "DIR": '"D:\\WAVEFORMS\\TEMP"', "AREA": "GRIDAREAONLY",
        }
        config = instrument.hardcopy_setup_current
        assert config_expected.items() <= config.items()

    def test_download_image_default_arguments(self, autoscaled_instrument):
        """Note: the path specified here must exist on the device already!"""
        img = autoscaled_instrument.download_image()
        assert type(img) is bytearray
        assert pytest.approx(len(img), 0.1) == 2734135

    # Trigger

    def test_trigger_select(self, resetted_instrument):
        with pytest.raises(ValueError):
            resetted_instrument.trigger_select = "edge"
        with pytest.raises(ValueError):
            resetted_instrument.trigger_select = ("edge", "c2")
        with pytest.raises(ValueError):
            resetted_instrument.trigger_select = ("edge", "c2", "time")
        with pytest.raises(ValueError):
            resetted_instrument.trigger_select = ("ABCD", "c1", "time", 0)
        with pytest.raises(ValueError):
            resetted_instrument.trigger_select = ("edge", "c1", "time", 1000)
        with pytest.raises(ValueError):
            resetted_instrument.trigger_select = ("edge", "c1", "time", 0, 1)
        resetted_instrument.trigger_select = ("edge", "c1", "off")
        resetted_instrument.trigger_select = ("EDGE", "C1", "OFF")
        assert resetted_instrument.trigger_select == ["edge", "c1", "off"]
        resetted_instrument.trigger_select = ("glit", "c1", "p2", 1e-3, 2e-3)
        assert resetted_instrument.trigger_select == ["glit", "c1", "p2", 1e-3, 2e-3]

    def test_trigger_setup(self, resetted_instrument):
        expected = resetted_instrument.trigger
        resetted_instrument.trigger_setup(**expected)
        assert resetted_instrument.trigger == expected


if __name__ == "__main__":
    pytest.main()
