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

import pytest
from pymeasure.instruments.agilent.agilent33500 import Agilent33500
from pyvisa.errors import VisaIOError

############
# FIXTURES #
############

@pytest.fixture(scope="session")
def generator():
    try:
        generator = Agilent33500("TCPIP::192.168.225.208::inst0::INSTR")
    except IOError:
        print("Not able to connect to waveform generator")
        assert False

    yield generator
    generator.ch[1].output = 'off'
    generator.ch[2].output = 'off'

#########
# TESTS #
#########


def test_get_instrument_id(generator):
    assert "Agilent Technologies" in generator.id


@pytest.mark.parametrize('channel', [1, 2])
def test_turn_on_channel(generator, channel):
    generator.ch[channel].output = 'on'
    assert generator.ch[channel].output


@pytest.mark.parametrize('shape', ['SIN', 'SQU', 'TRI', 'RAMP', 'PULS', 'PRBS', 'NOIS', 'ARB', 'DC'])
@pytest.mark.parametrize('channel', [1,2])
def test_shape_channel(generator, shape, channel):
    generator.ch[channel].shape = shape
    assert shape == generator.ch[channel].shape


@pytest.mark.parametrize('frequency', [0.1, 1, 10, 100, 1000])
@pytest.mark.parametrize('channel', [1,2])
def test_frequency_channel(generator, frequency, channel):
    generator.ch[channel].frequency = frequency
    assert frequency == pytest.approx(generator.ch[channel].frequency, 0.1)