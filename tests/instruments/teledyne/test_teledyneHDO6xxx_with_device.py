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

from pymeasure.instruments.teledyne import TeledyneHDO6xxx


class TestTeledyneHDO6xxx:
    """
    Unit tests for TeledyneHDO6xxx class.

    This test suite, needs the following setup to work properly:
        - A TeledyneHDO6xxx device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
        - A probe on Channel 1 must be connected to the Demo output of the oscilloscope.
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
        return TeledyneHDO6xxx(connected_device_address)

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
        instrument = TeledyneHDO6xxx(connected_device_address)
        channel = instrument.ch(1)
        return

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

    def test_removed_property(self, instrument):
        """Verify the behaviour of a removed property."""
        props = ["trigger_level2", "skew_factor", "unit", "invert"]
        for prop in props:
            with pytest.raises(NotImplementedError):
                _ = getattr(instrument.ch(1), prop)

    @pytest.mark.parametrize("case", BANDWIDTH_LIMITS)
    def test_ch_bwlimit(self, instrument, case):
        instrument.bwlimit = case
        expected = {ch: case for ch in TestTeledyneHDO6xxx.WAVEFORM_SOURCES}
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


if __name__ == "__main__":
    pytest.main()