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
from pymeasure.test import expected_protocol
from pymeasure.instruments.agilent.agilent4294A import Agilent4294A


@pytest.mark.parametrize("freq", [40, 140E6])
def test_set_start_freq(freq):
    """ Test Agilent 4294A start frequency setter """
    with expected_protocol(Agilent4294A, [(f"STAR {freq:.0f} HZ", None), ],) as inst:
        inst.start_frequency = freq


@pytest.mark.parametrize("freq", [40, 140E6])
def test_get_start_freq(freq):
    """ Test Agilent 4294A start frequency getter """
    with expected_protocol(Agilent4294A, [("STAR?", freq), ],) as inst:
        assert freq == inst.start_frequency


@pytest.mark.parametrize("freq", [40, 140E6])
def test_set_stop_freq(freq):
    """ Test Agilent 4294A stop frequency setter """
    with expected_protocol(Agilent4294A, [(f"STOP {freq:.0f} HZ", None), ],) as inst:
        inst.stop_frequency = freq


@pytest.mark.parametrize("freq", [40, 140E6])
def test_get_stop_freq(freq):
    """ Test Agilent 4294A stop frequency getter """
    with expected_protocol(Agilent4294A, [("STOP?", freq), ],) as inst:
        assert freq == inst.stop_frequency
