#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.tektronix.mso44 import MSO44, MeasurementType


@pytest.fixture(scope="module")
def mso44(connected_device_address):
    instr = MSO44(connected_device_address)
    return instr


@pytest.fixture
def reset_mso44(mso44):
    mso44.reset()
    return mso44


def test_channel_enable(reset_mso44):
    reset_mso44.ch1.enabled = True
    assert reset_mso44.ch1.enabled is True
    reset_mso44.ch1.enabled = False
    assert reset_mso44.ch1.enabled is False


def test_timebase(reset_mso44):
    reset_mso44.timebase = 1e-3
    assert reset_mso44.timebase == pytest.approx(1e-3)


def test_acquire_waveform(reset_mso44):
    reset_mso44.ch1.enabled = True
    reset_mso44.ch1.scale = 0.1
    reset_mso44.timebase = 1e-3
    reset_mso44.trigger_level = 0.1
    reset_mso44.start_acquisition()
    channels = ["CH1"]
    sources, encoding, preamble, data = reset_mso44.get_waveforms(channels, width=2)
    waveforms = reset_mso44.process_waveforms(sources, encoding, preamble, data)
    assert len(waveforms) > 0
    ch1_data = waveforms['CH1']
    assert len(ch1_data) > 0
    reset_mso44.stop_acquisition()


def test_measurement_frequency(reset_mso44):
    reset_mso44.delete_all_measurements()
    reset_mso44.wait_for_idle()
    reset_mso44.ch1.enabled = True
    reset_mso44.ch1.scale = 2
    reset_mso44.timebase = 1e-3
    meas_count = reset_mso44.get_measurement_count()
    assert meas_count == 0
    meas = reset_mso44.add_measurement(MeasurementType.FREQUENCY, "CH1")
    reset_mso44.wait_for_idle(timeout=10)
    meas_count = reset_mso44.get_measurement_count()
    assert meas_count == 1
    reset_mso44.start_acquisition()
    reset_mso44.wait_for_idle()
    freq = meas.value
    #assert 0 < freq < 1e9
    reset_mso44.stop_acquisition()


def test_measurement_phase(reset_mso44):
    reset_mso44.display_mode = 'OVE'
    reset_mso44.ch1.enabled = True
    reset_mso44.ch2.enabled = True
    reset_mso44.ch1.scale = 2
    reset_mso44.ch2.scale = 1
    reset_mso44.timebase = 1e-3
    meas = reset_mso44.add_measurement(MeasurementType.PHASE, "CH1", "CH2")
    reset_mso44.wait_for_idle()
    reset_mso44.start_acquisition()
    reset_mso44.wait_for_idle()
    phase = meas.value
    #assert -180 <= phase <= 180
    reset_mso44.stop_acquisition()
