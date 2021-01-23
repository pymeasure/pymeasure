#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from pymeasure.instruments.spectrum_analyzer import SpectrumAnalyzer

class AgilentE4440A(SpectrumAnalyzer):
    """ This class represent an Agilent E4450 Spectrum Analyzer """

    # Customize parameters with values taken from datasheet/user manual 
    reference_level_values = (-170, 30)

    frequency_span_values = (10, 26.5e9)

    resolution_bw_values = (1, 8e6)

    input_attenuation_values = (0, 70)

    frequency_points_values = (101, 8192)

    detector_values = ("NORM", "AVER", "POS", "SAMP", "NEG", "QPE", "EAV", "EPOS", "MPOS", "RMS")

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent E4440A Spectrum Analyzer",
            **kwargs
        )


class AgilentE4445A(AgilentE4440A):
    """ Spectrum analyzer similar to E4440A, but with more limited frequency span """

    frequency_span_values = (10, 13.2e9)

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent E4445A Spectrum Analyzer",
            **kwargs
        )
