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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

class RS_FSC6(SpectrumAnalyzer):
    """ This class represent an Rohde&Schwarz FSC6 Spectrum Analyzer """

    # Customize parameters with values taken from datasheet/user manual 
    reference_level_values = (-80, 30)

    frequency_span_values = (10, 6e9)

    resolution_bw_values = (10, 3e6)

    input_attenuation_values = (0, 40)

    frequency_points_values = (631, 631)

    detector_values = ("APE", "NEG", "POS", "SAMP", "RMS"),

    input_attenuation_get_command = ":INPut:ATTenuation?;"
    input_attenuation_set_command = ":INPut:ATTenuation %d;"

    def __init__(self, resourceName, description, **kwargs):
        super(RS_FSCx, self).__init__(
            resourceName,
            description,
            **kwargs
        )


class RS_FSC3(RS_FSC6):
    """ Variant of FSC6 covering up to 3 GHz """

    frequency_span_values = (10, 3e9)
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "R&S FSC3 Spectrum Analyzer",
            **kwargs
        )
