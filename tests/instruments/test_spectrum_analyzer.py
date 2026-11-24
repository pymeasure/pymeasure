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
from pytest import approx
from pymeasure.instruments.spectrum_analyzer import SpectrumAnalyzer, find_peaks
import numpy as np
from math import sqrt, atan, pi


@pytest.mark.skipif("find_peaks is None")
def test_peak_search_with_sin():
    sin = np.sin

    def func(x):
        return sin(x) + sin(2*x)

    assert find_peaks is not None
    # Calculate peaks
    # temporary value
    val1 = 2*atan(sqrt(6-sqrt(33)))
    val2 = 2*atan(sqrt(6+sqrt(33)))
    # Peaks
    x_max = np.array([val1, 2*pi - val2])
    y_max = func(x_max)

    # make data
    x = np.linspace(0, 2*pi, 10000)
    y = func(x)

    peak_idx = SpectrumAnalyzer.peaks(y)

    x_peaks = [x[i] for i in peak_idx]
    y_peaks = [y[i] for i in peak_idx]

    # Check that only relevant peaks are detected
    assert len(peak_idx) == len(x_max)

    # Check maximum values found
    for i, (x, y) in enumerate(zip(x_max, y_max)):
        assert x_peaks[i] == approx(x, rel=0.001)
        assert y_peaks[i] == approx(y, rel=0.001)
