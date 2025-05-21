#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
from unittest.mock import ANY

import numpy as np
import pytest
from pyvisa.errors import VisaIOError

from pymeasure.instruments.lecroy.lecroyT3DSO1204 import LeCroyT3DSO1204


class TestLeCroyT3DSO1204:
    """
    Unit tests for LeCroyT3DSO1204 class.

    This test suite, needs the following setup to work properly:
        - A LeCroyT3DSO1204 device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
        - A probe on Channel 1 must be connected to the Demo output of the oscilloscope.
    """

    #########################
    # PARAMETRIZATION CASES #
    #########################

    BOOLEANS = [False, True]
    CHANNEL_COUPLINGS = ["ac 1M", "dc 1M", "ground"]
    ACQUISITION_TYPES = ["normal", "average", "peak", "highres"]
    TRIGGER_LEVELS = [0.125, 0.150, 0.175]
    TRIGGER_SLOPES = ["negative", "positive", "window"]
    ACQUISITION_AVERAGE = [4, 16, 32, 64, 128, 256]
    WAVEFORM_POINTS = [100, 1000, 10000]
    WAVEFORM_SOURCES = ["C1", "C2", "C3", "C4"]
    CHANNELS = [1, 2, 3, 4]

    ############
    # FIXTURES #
    ############

    @pytest.fixture(scope="module")
    def instrument(self, connected_device_address):
        return LeCroyT3DSO1204(connected_device_address)

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

    # noinspection PyTypeChecker
    def test_instrument_connection(self):
        bad_resource = "USB0::10893::45848::MY12345678::0::INSTR"
        # The pure python VISA library (pyvisa-py) raises a ValueError while the
        # PyVISA library raises a VisaIOError.
        with pytest.raises((ValueError, VisaIOError)):
            LeCroyT3DSO1204(bad_resource)

    # Channel
    def test_ch_current_configuration(self, autoscaled_instrument):
        autoscaled_instrument.ch_1.offset = 0
        autoscaled_instrument.ch_1.trigger_level = 0
        autoscaled_instrument.ch_1.trigger_level2 = 0
        expected = {
            "channel": 1,
            "attenuation": 1.0,
            "bandwidth_limit": False,
            "coupling": "dc 1M",
            "offset": 0.0,
            "skew_factor": 0.0,
            "display": True,
            "unit": "V",
            "volts_div": 0.05,
            "inverted": False,
            "trigger_coupling": "dc",
            "trigger_level": 0.0,
            "trigger_level2": 0.0,
            "trigger_slope": "positive",
        }
        actual = autoscaled_instrument.ch(1).current_configuration
        assert actual == expected

    @pytest.mark.parametrize("ch_number", CHANNELS)
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_bwlimit(self, instrument, ch_number, case):
        instrument.ch(ch_number).bwlimit = case
        assert instrument.ch(ch_number).bwlimit == case

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
    @pytest.mark.parametrize("case", BOOLEANS)
    def test_ch_invert(self, instrument, ch_number, case):
        instrument.ch(ch_number).invert = case
        assert instrument.ch(ch_number).invert == case

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

    def test_ch_trigger_level2(self, autoscaled_instrument):
        for case in self.TRIGGER_LEVELS:
            autoscaled_instrument.ch_1.trigger_level2 = case
            assert autoscaled_instrument.ch_1.trigger_level2 == case

    def test_ch_trigger_slope(self, autoscaled_instrument):
        with pytest.raises(ValueError):
            autoscaled_instrument.ch_1.trigger_slope = "abcd"
        autoscaled_instrument.trigger_select = ("edge", "c1", "off")
        for case in self.TRIGGER_SLOPES:
            autoscaled_instrument.ch_1.trigger_slope = case
            assert autoscaled_instrument.ch_1.trigger_slope == case

    # Timebase
    def test_timebase(self, autoscaled_instrument):
        autoscaled_instrument.timebase_hor_magnify = 5e-6
        autoscaled_instrument.timebase_hor_position = 0
        expected = {
            "timebase_scale": 5e-4,
            "timebase_offset": 0.0,
            "timebase_hor_magnify": 5e-6,
            "timebase_hor_position": 0.0,
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

    def test_timebase_hor_magnify(self, instrument):
        instrument.timebase_hor_magnify = 1e-4
        assert instrument.timebase_hor_magnify == 1e-4

    def test_timebase_hor_position(self, instrument):
        instrument.timebase_hor_position = 5e-4
        assert pytest.approx(instrument.timebase_hor_position, 0.1) == 5e-4

    # Acquisition
    @pytest.mark.parametrize("case", ACQUISITION_TYPES)
    def test_acquisition_type(self, resetted_instrument, case):
        if case == "average":
            resetted_instrument.acquisition_type = case
            resetted_instrument.acquisition_average = 16
            assert resetted_instrument.acquisition_type == ["average", 16]
        else:
            resetted_instrument.acquisition_type = case
            assert resetted_instrument.acquisition_type == case

    @pytest.mark.parametrize("case", ACQUISITION_AVERAGE)
    def test_acquisition_average(self, instrument, case):
        instrument.acquisition_average = case
        assert instrument.acquisition_average == case

    def test_acquisition_status(self, autoscaled_instrument):
        assert autoscaled_instrument.acquisition_status == "triggered"
        autoscaled_instrument.stop()
        assert autoscaled_instrument.acquisition_status == "stopped"

    def test_acquisition_sampling_rate(self, resetted_instrument):
        assert resetted_instrument.acquisition_sampling_rate == 1e9

    @pytest.mark.parametrize("case", WAVEFORM_POINTS)
    def test_waveform_points(self, instrument, case):
        instrument.waveform_points = case
        assert instrument.waveform_points == case

    def test_waveform_preamble(self, autoscaled_instrument):
        autoscaled_instrument.acquisition_type = "normal"
        autoscaled_instrument.ch_1.offset = 0
        autoscaled_instrument.waveform_points = 0
        autoscaled_instrument.waveform_first_point = 0
        autoscaled_instrument.waveform_sparsing = 1
        autoscaled_instrument.waveform_source = "C1"
        expected_preamble = {
            "sparsing": 1.0,
            "requested_points": 0.0,
            "memory_size": 14e6,
            "sampled_points": 7e6,
            "transmitted_points": None,
            "first_point": 0.0,
            "source": autoscaled_instrument.waveform_source,
            "type": "normal",
            "average": None,
            "sampling_rate": 1e9,
            "grid_number": 14,
            "status": ANY,
            "xdiv": 5e-4,
            "xoffset": -0.0,
            "ydiv": 0.05,
            "yoffset": 0.0,
            "unit": "V",
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
            bwlimit=False,
            coupling="dc 1M",
            display=True,
            invert=False,
            offset=0.0,
            skew_factor=0.0,
            probe_attenuation=1.0,
            scale=0.05,
            unit="V",
            trigger_coupling="dc",
            trigger_level=0.150,
            trigger_level2=0.150,
            trigger_slope="positive",
        )
        expected = {
            "channel": ch_number,
            "attenuation": 1.0,
            "bandwidth_limit": False,
            "coupling": "dc 1M",
            "offset": 0.0,
            "skew_factor": 0.0,
            "display": True,
            "unit": "V",
            "volts_div": 0.05,
            "inverted": False,
            "trigger_coupling": "dc",
            "trigger_level": 0.150,
            "trigger_level2": 0.150,
            "trigger_slope": "positive",
        }
        actual = instrument.ch(ch_number).current_configuration
        assert actual == expected

    def test_timebase_setup(self, resetted_instrument):
        expected = resetted_instrument.timebase
        resetted_instrument.timebase_setup()
        assert resetted_instrument.timebase == expected

    # Download methods
    def test_download_image_default_arguments(self, autoscaled_instrument):
        img = autoscaled_instrument.download_image()
        assert type(img) is bytearray
        assert pytest.approx(len(img), 0.1) == 768067

    def test_download_data_missing_argument(self, resetted_instrument):
        with pytest.raises(TypeError):
            # noinspection PyArgumentList
            resetted_instrument.download_waveform()

    @pytest.mark.parametrize("case1", WAVEFORM_SOURCES)
    @pytest.mark.parametrize("case2", WAVEFORM_POINTS)
    def test_download_data(self, instrument, case1, case2):
        if case1 == self.WAVEFORM_SOURCES[0] and case2 == self.WAVEFORM_POINTS[0]:
            instrument.reset()
            sleep(7)
            instrument.autoscale()
            sleep(7)
        instrument.ch(case1).display = True
        instrument.single()
        sleep(1)
        data, time, preamble = instrument.download_waveform(
            source=case1, requested_points=case2, sparsing=0
        )
        assert type(data) is np.ndarray
        assert len(data) == case2
        assert type(time) is np.ndarray
        assert len(time) == case2
        assert type(preamble) is dict

    def test_download_single_point(self, instrument):
        instrument.acquisition_type = "normal"
        instrument.ch_1.display = True
        instrument.single()
        sleep(1)
        data, time, preamble = instrument.download_waveform(source="c1", requested_points=1)
        assert type(data) is np.ndarray
        assert len(data) == 1
        assert type(time) is np.ndarray
        assert len(time) == 1
        assert type(preamble) is dict
        assert preamble == {'average': None,
                            'first_point': 0,
                            'grid_number': 14,
                            'memory_size': 7000000.0,
                            'requested_points': 1,
                            'sampled_points': 3500000.0,
                            'sampling_rate': 500000000.0,
                            'source': 'C1',
                            'sparsing': 1.0,
                            'status': 'stopped',
                            'transmitted_points': 1,
                            'type': 'normal',
                            'unit': 'V',
                            'xdiv': 0.0005,
                            'xoffset': -0.0,
                            'ydiv': ANY,
                            'yoffset': ANY}

    @pytest.mark.skip(reason="A human is needed to check the output waveform")
    def test_download_data_all_points(self, instrument):
        from matplotlib import pyplot as plt

        instrument.ch_1.display = True
        instrument.single()
        sleep(3)
        data, time, preamble = instrument.download_waveform(source="c1", requested_points=0)
        assert type(data) is np.ndarray
        assert type(time) is np.ndarray
        assert type(preamble) is dict
        print(preamble)
        plt.scatter(x=time, y=data)
        plt.show()

    @pytest.mark.skip(reason="A human is needed to check the output waveform")
    def test_download_data_sparsing(self, instrument):
        from matplotlib import pyplot as plt

        instrument.ch_1.display = True
        instrument.single()
        sleep(1)
        data, time, preamble = instrument.download_waveform(
            source="c1", requested_points=7e5, sparsing=10
        )
        assert type(data) is np.ndarray
        assert len(data) == 7e5 or len(data) == 7e4
        assert type(time) is np.ndarray
        assert len(time) == 7e5 or len(time) == 7e4
        assert type(preamble) is dict
        assert preamble["type"] == "normal"
        assert preamble["sparsing"] == 10
        assert preamble["transmitted_points"] == 7e5 or preamble["transmitted_points"] == 7e4
        print(preamble)
        plt.scatter(x=time, y=data)
        plt.show()

    @pytest.mark.skip(reason="A human is needed to check the output waveform")
    def test_download_data_averaging_16(self, instrument):
        from matplotlib import pyplot as plt

        instrument.ch_1.display = True
        instrument.run()
        instrument.acquisition_type = "average"
        instrument.acquisition_average = 16
        instrument.single()
        sleep(1)
        data, time, preamble = instrument.download_waveform(
            source="c1", requested_points=1.75e5, sparsing=10
        )
        assert type(data) is np.ndarray
        assert len(data) == 1.75e5 or len(data) == 7e4
        assert type(time) is np.ndarray
        assert len(time) == 1.75e5 or len(time) == 7e4
        assert type(preamble) is dict
        assert preamble["type"] == ["average", 16]
        assert preamble["average"] == 16
        assert preamble["transmitted_points"] == 1.75e5 or preamble["transmitted_points"] == 7e4
        print(preamble)
        plt.scatter(x=time, y=data)
        plt.show()

    @pytest.mark.skip(reason="A human is needed to check the output waveform")
    def test_download_data_averaging_256(self, instrument):
        from matplotlib import pyplot as plt

        instrument.ch_1.display = True
        instrument.run()
        instrument.acquisition_type = "average"
        instrument.acquisition_average = 256
        instrument.single()
        sleep(1)
        data, time, preamble = instrument.download_waveform(
            source="c1", requested_points=1.75e5, sparsing=10
        )
        assert type(data) is np.ndarray
        assert len(data) == 1.75e5 or len(data) == 7e4
        assert type(time) is np.ndarray
        assert len(time) == 1.75e5 or len(time) == 7e4
        assert type(preamble) is dict
        assert preamble["type"] == ["average", 256]
        assert preamble["average"] == 256
        assert preamble["transmitted_points"] == 1.75e5 or preamble["transmitted_points"] == 7e4
        print(preamble)
        plt.scatter(x=time, y=data)
        plt.show()

    @pytest.mark.skip(reason="A human is needed to check the output waveform")
    def test_download_math(self, instrument):
        """ Be careful because there is no way to turn on and off the MATH function
        programmatically, so the user should push on the MATH button and make sure
        that the (white) math line is displayed before running this test. """
        from matplotlib import pyplot as plt

        instrument.single()
        sleep(1)
        data, time, preamble = instrument.download_waveform(
            source="math", requested_points=0, sparsing=10
        )
        assert type(data) is np.ndarray
        assert type(time) is np.ndarray
        assert type(preamble) is dict
        print(preamble)
        plt.scatter(x=time, y=data)
        plt.show()

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
