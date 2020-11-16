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

class RS_FSCx(SpectrumAnalyzer):
    REFERENCE_LEVEL_RANGE_MIN_dBm = -80
    REFERENCE_LEVEL_RANGE_MAX_dBm = 30
    REFERENCE_LEVEL_RANGE_dBm = [REFERENCE_LEVEL_RANGE_MIN_dBm, REFERENCE_LEVEL_RANGE_MAX_dBm]

    FREQUENCY_MIN_Hz = 1
    FREQUENCY_MAX_Hz = 6e9
    FREQUENCY_SPAN_RANGE_Hz = [10, FREQUENCY_MAX_Hz]

    RESOLUTION_BW_RANGE_MIN_Hz = 10
    RESOLUTION_BW_RANGE_MAX_Hz = 3e6
    RESOLUTION_BW_RANGE_Hz = [RESOLUTION_BW_RANGE_MIN_Hz, RESOLUTION_BW_RANGE_MAX_Hz]

    INPUT_ATTENUATION_RANGE_dB = [0, 40]

    SWEEP_POINTS_RANGE = [631, 631]

    DETECTOR_VALUES=["APE", "NEG", "POS", "SAMP", "RMS"],

    input_attenuation = SpectrumAnalyzer.control(
        ":INPut:ATTenuation?;", ":INPut:ATTenuation %d;",
        """ An integer property that represents the instrument the input attenuation in dB.
        This property can be set.
        """,
        validator=truncated_range,
        values=INPUT_ATTENUATION_RANGE_dB,
        cast=int
    )

    def __init__(self, resourceName, description, **kwargs):
        super(RS_FSCx, self).__init__(
            resourceName,
            description,
            **kwargs
        )
class RS_FSC6(RS_FSCx):
    FREQUENCY_MAX_Hz = 6e9
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "R&S FSC6 Spectrum Analyzer",
            **kwargs
        )

class RS_FSC3(RS_FSCx):
    FREQUENCY_MAX_Hz = 3e9
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "R&S FSC3 Spectrum Analyzer",
            **kwargs
        )
