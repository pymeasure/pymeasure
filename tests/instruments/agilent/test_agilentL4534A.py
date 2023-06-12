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
from pymeasure.instruments.agilent.agilentL4534A import AgilentL4534A
from pymeasure.units import ureg


def test_init():
    with expected_protocol(
        AgilentL4534A,
        [],
    ) as instr:
        assert len(instr.channels) == 4


def test_instr_init():
    """
    Test Agilent L4534A init function
    """
    with expected_protocol(
        AgilentL4534A,
        [
            ("INIT", None),
        ],
    ) as inst:
        inst.init()


@pytest.mark.parametrize("samples", [8, 120000000])
def test_set_samples(samples):
    """
    Test Agilent L4534A set samples property
    """
    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:ACQ:SCO?", samples),
            (f"CONF:ACQ:SCO {samples}", None)
        ],
    ) as inst:
        assert inst.samples_per_record == samples
        inst.samples_per_record = samples


@pytest.mark.parametrize("filter", AgilentL4534A.DigitizerChannel.FILTER_VALUES)
def test_set_filter(filter):
    """
    Test Agilent L4534A set filter property
    """
    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:CHAN:FILT? (@1)", filter),
            (f"CONF:CHAN:FILT (@1),{filter}", None)
        ],
    ) as inst:
        assert inst.channels[1].filter == filter
        inst.channels[1].filter = filter


@pytest.mark.parametrize('source', AgilentL4534A.TRIGGER_SOURCE_VALUES)
def test_trigger_source(source):
    """
    Test Agilent L4534A trigger_source property
    """
    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:TRIG:SOUR?", source),
            (f"CONF:TRIG:SOUR {source}", None)
        ],
    ) as inst:
        assert inst.trigger_source == source
        inst.trigger_source = source


@pytest.mark.parametrize("length", [5, 1024])
def test_get_adc(length):
    """
    Test Agilent L4534A get ADC property
    """

    data = np.arange(length, dtype='>i2')
    bytes = data.tobytes()
    count = len(bytes)
    digits = int(math.log10(count))+1
    with expected_protocol(
        AgilentL4534A,
        [
            ("FETC:WAV:ADC? (@1)", f'#{digits}{count}'.encode() + bytes + b'\n')
        ],
    ) as inst:
        resp = inst.channels[1].adc
        assert resp.dtype == np.int16
        assert np.array_equal(resp, data)


@pytest.mark.parametrize("length", [5, 1024])
def test_get_voltage(length):
    """
    Test Agilent L4534A get Voltage property
    """

    data = np.arange(length, dtype='>f4')
    bytes = data.tobytes()
    count = len(bytes)
    digits = int(math.log10(count))+1
    with expected_protocol(
        AgilentL4534A,
        [
            ("FETC:WAV:VOLT? (@1)", f'#{digits}{count}'.encode() + bytes + b'\n')
        ],
    ) as inst:
        resp = inst.channels[1].voltage
        assert resp.dtype == np.float32
        assert np.array_equal(resp.m, data)

@pytest.mark.parametrize("rate", AgilentL4534A.SAMPLE_RATE_VALUES.magnitude.tolist())
def test_sample_rate(rate):
    """
    Test Agilent L4534A set samples property
    """
    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:ACQ:SRAT?", int(rate)),
            (f"CONF:ACQ:SRAT {rate}", None),
            ("CONF:ACQ:SRAT?", int(rate)),
            (f"CONF:ACQ:SRAT {rate}", None)
        ],
    ) as inst:
        assert inst.sample_rate.m == rate
        inst.sample_rate = rate
        assert inst.sample_rate == rate * ureg.Hz
        inst.sample_rate = rate * ureg.Hz


@pytest.mark.parametrize("range", AgilentL4534A.DigitizerChannel.VOLTAGE_RANGE_VALUES.m.tolist())
def test_voltage_range(range):
    """
    Test Agilent L4534A channel voltage range property
    """
    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:CHAN:RANG? (@1)", float(range)),
            (f"CONF:CHAN:RANG (@1),{range:g}", None),
            ("CONF:CHAN:RANG? (@1)", float(range)),
            (f"CONF:CHAN:RANG (@1),{range:g}", None)
        ],
    ) as inst:
        assert inst.channels[1].range.m == range
        inst.channels[1].range = range
        assert inst.channels[1].range == range * ureg.V
        inst.channels[1].range = range * ureg.V


def test_acquisition_config():
    """
    Test Agilent L4534A acquisition config
    """
    settings = {
        'sample_rate': ureg.Quantity(1000000, ureg.Hz),
        'samples_per_record': int(1024),
        'pre_trig_samples': int(4),
        'num_records': int(1),
        'trigger_holdoff': ureg.Quantity(0.1, ureg.s),
        'trigger_delay': ureg.Quantity(0, ureg.s)
    }

    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:ACQ:ATTR?", '1000000,1024,4,1,0.1,0'),
            ("CONF:ACQ:ATTR 1000000,1024,4,1,0.1,0", None)
        ],
    ) as inst:
        assert inst.acquisition == settings
        inst.acquisition = settings


def test_channel_config():
    settings = {
        'range': 0.5 * ureg.V,
        'coupling': 'DC',
        'filter': 'LP_2_MHZ'
    }

    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:CHAN:ATTR? (@1)", '0.5,DC,LP_2_MHZ'),
            ("CONF:CHAN:ATTR (@1),0.5,DC,LP_2_MHZ", None)
        ],
    ) as inst:
        assert inst.channels[1].config == settings
        inst.channels[1].config = settings


def test_trigger_output():
    output_config = {
        'event': 'TRIG',
        'drive_mode': 'POS_50'
    }
    with expected_protocol(
        AgilentL4534A,
        [
            ("CONF:EXT:TRIG:OUTP?", 'TRIG,POS_50'),
            ("CONF:EXT:TRIG:OUTP TRIG,POS_50", None)
        ],
    ) as inst:
        assert inst.trigger_output == output_config
        inst.trigger_output = output_config
