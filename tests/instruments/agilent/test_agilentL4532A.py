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
import math
import numpy as np


import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.agilent.agilentL4532A import AgilentL4532A

def test_init():
    with expected_protocol(
        AgilentL4532A,
        [],
    ) as instr:
        assert len(instr.channels) == 2

def test_instr_init():
    """
    Test Agilent L4532A init function
    """
    with expected_protocol(
        AgilentL4532A,
        [
            ("INIT", None),
        ],
    ) as inst:
        inst.init()

@pytest.mark.parametrize("samples", [8, 120000000])
def test_set_samples(samples):
    """
    Test Agilent L4532A set samples property
    """
    with expected_protocol(
        AgilentL4532A,
        [
            ("CONF:ACQ:SCO?", samples),
            (f"CONF:ACQ:SCO {samples}", None)
        ],
    ) as inst:
        assert inst.samples_per_record == samples
        inst.samples_per_record = samples

@pytest.mark.parametrize("filter", [ 'LP_20_MHZ', 'LP_2_MHZ', 'LP_200_KHZ' ])
def test_set_filter(filter):
    """
    Test Agilent L4532A set filter property
    """
    with expected_protocol(
        AgilentL4532A,
        [
            ("CONF:CHAN:FILT? (@1)", filter),
            (f"CONF:CHAN:FILT (@1),{filter}", None)
        ],
    ) as inst:
        assert inst.channels[1].filter == filter
        inst.channels[1].filter = filter


@pytest.mark.parametrize("length", [ 5, 1024, 1000000 ])
def test_get_voltage(length):
    """
    Test Agilent L4532A get voltage property
    """

    data = np.arange(length, dtype=np.float32)
    bytes = data.tobytes()
    count = len(bytes)
    digits = int(math.log10(count))+1
    with expected_protocol(
        AgilentL4532A,
        [
            ("FETC:WAV:VOLT? (@1)", f'#{digits}{count}'.encode() + bytes)
        ],
    ) as inst:
        assert np.array_equal(inst.channels[1].voltage, data)


@pytest.mark.parametrize("length", [ 5, 1024 ])
def test_get_adc(length):
    """
    Test Agilent L4532A get ADC property
    """

    data = np.arange(length, dtype=np.int16)
    bytes = data.tobytes()
    count = len(bytes)
    digits = int(math.log10(count))+1
    with expected_protocol(
        AgilentL4532A,
        [
            ("FETC:WAV:ADC? (@1)", f'#{digits}{count}'.encode() + bytes)
        ],
    ) as inst:
        assert np.array_equal(inst.channels[1].adc, data)