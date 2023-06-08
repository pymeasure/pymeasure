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

import numpy as np

import pytest
from pymeasure.instruments.agilent.agilentL4534A import AgilentL4534A
from pymeasure.units import ureg

@pytest.fixture(scope="module")
def make_resetted_dig(connected_device_address):
    dig = AgilentL4534A(connected_device_address)
    dig.reset()
    dig.clear()
    return dig


def test_idn(make_resetted_dig: AgilentL4534A):
    dig = make_resetted_dig
    assert dig.id.startswith('Agilent Technologies,L4534A')


def test_selftest(make_resetted_dig: AgilentL4534A):
    dig = make_resetted_dig
    test = dig.tst(45)
    assert int(test) == 0, dig.check_errors()
    dig.clear_display()


def test_disp(make_resetted_dig: AgilentL4534A):
    dig = make_resetted_dig
    dig.display = 'PyMeasure'
    assert dig.display == 'PyMeasure'
    dig.clear_display()
    assert dig.display == ''


def test_acquisition_config(make_resetted_dig: AgilentL4534A):
    dig = make_resetted_dig
    settings = {
        'sample_rate': ureg.Quantity(1000000, ureg.Hz),
        'samples_per_record': int(1024),
        'pre_trig_samples': int(4),
        'num_records': int(1),
        'trigger_holdoff': ureg.Quantity(0.1, ureg.s),
        'trigger_delay': ureg.Quantity(0, ureg.s)
    }
    dig.acquisition = settings
    assert dig.acquisition == settings


def test_channel_config(make_resetted_dig: AgilentL4534A):
    dig = make_resetted_dig
    settings = {
        'range': 0.5 * ureg.V,
        'coupling': 'DC',
        'filter': 'LP_2_MHZ'
    }
    for ch in range(1,5):
        dig.channels[ch].config = settings
        assert dig.channels[ch].config == settings


def test_measure(make_resetted_dig: AgilentL4534A):
    dig = make_resetted_dig
    # Set acquisition settings
    settings = {
        'sample_rate': ureg.Quantity(1000000, ureg.Hz),
        'samples_per_record': int(1024),
        'pre_trig_samples': int(0),
        'num_records': int(1),
        'trigger_holdoff': ureg.Quantity(0, ureg.s),
        'trigger_delay': ureg.Quantity(0, ureg.s)
    }
    dig.acquisition = settings
    # Prepare to capture
    dig.init()
    # Wait for capture to complete
    assert int(dig.complete) == 1
    # Read back both processed and raw results for each channel and check the data looks as is expected
    for ch in range(1,5):
        result = dig.channels[ch].voltage
        assert result.m.dtype == np.dtype('>f4')
        assert result.size == 1024
        result = dig.channels[ch].adc
        assert result.size == 1024
        assert result.dtype == np.dtype('>i2')
