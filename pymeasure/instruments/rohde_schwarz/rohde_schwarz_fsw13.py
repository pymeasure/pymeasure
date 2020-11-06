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

class RS_FSW13(SpectrumAnalyzer):
    REFERENCE_LEVEL_RANGE_MIN_dBm = -40
    REFERENCE_LEVEL_RANGE_MAX_dBm = 27
    REFERENCE_LEVEL_RANGE_dBm = [REFERENCE_LEVEL_RANGE_MIN_dBm, REFERENCE_LEVEL_RANGE_MAX_dBm]

    FREQUENCY_MIN_Hz = 1
    FREQUENCY_MAX_Hz = 13.6e9
    FREQUENCY_SPAN_RANGE_Hz = [0, FREQUENCY_MAX_Hz]

    RESOLUTION_BW_RANGE_MIN_Hz = 1
    RESOLUTION_BW_RANGE_MAX_Hz = 10e6
    RESOLUTION_BW_RANGE_Hz = [RESOLUTION_BW_RANGE_MIN_Hz, RESOLUTION_BW_RANGE_MAX_Hz]

    INPUT_ATTENUATION_RANGE_dB = [0, 70] # This limit is not clear in the datasheet

    SWEEP_POINTS_RANGE = [101, 100001]

    DETECTOR_VALUES=["APE", "NEG", "POS", "QPE", "SAMP", "RMS", "AVER", "CAV", "CRMS"],


    TRACE_MODE_COMMAND = "DISPLAY:TRACe:MODE"
    trace_mode = SpectrumAnalyzer.control(
        TRACE_MODE_COMMAND + "?;",  TRACE_MODE_COMMAND + " %s;",
        """ A string property that enable you to set how trace information is stored and displayed.
        allowed values are "WRITE", "MAXHOLD", "MINHOLD", "VIEW", "BLANK"
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=["WRITE", "MAXHOLD", "MINHOLD", "VIEW", "BLANK"],
        cast=str
    )

    input_attenuation = SpectrumAnalyzer.control(
        ":INPut:ATTenuation?;", ":INPut:ATTenuation %d;",
        """ An integer property that represents the instrument the input attenuation in dB.
        This property can be set.
        """,
        validator=truncated_range,
        values=INPUT_ATTENUATION_RANGE_dB,
        cast=int
    )

    def __init__(self, resourceName, **kwargs):
        super(RS_FSW13, self).__init__(
            resourceName,
            "R&S FSW Spectrum Analyzer FSW-13",
            **kwargs
        )
