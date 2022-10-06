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

from pymeasure.instruments.spectrum_analyzer import SpectrumAnalyzer

from io import StringIO
import numpy as np


class KeysightP5003A(SpectrumAnalyzer):
    """ This class represents a Keysight P5003A VNA with S97090B Spectrum analysis option """

    # Customize parameters with values taken from datasheet/user manual

    reference_level_values = (-500, 500)

    frequency_span_values = (1, 14e9)

    resolution_bw_values = (5, 3e6)

    input_attenuation_values = (0, 70)

    frequency_points_values = (1, 100003)

    detector_values = ("PEAK", "AVER", "SAMP", "NORM", "NEGP", "PSAM", "PAV")

    trace_mode_values = ("OFF", "MIN", "MAX")

    average_type_values = {"VOLTAGE" : "VOLT", "POWER" : "POW", "VIDEO" : "LOG", "VMAX" : "VMAX", "VMIN" : "VMIN"}

    input_attenuation_get_command = "SOURce:POWer:ATTenuation:RECeiver:TEST?;"
    input_attenuation_set_command = "SOURce:POWer:ATTenuation:RECeiver:TEST %d;"

    frequency_step_get_command = "SENSe:FREQuency:CENTer:STEP:SIZE?;"
    frequency_step_set_command = "SENSe:FREQuency:CENTer:STEP:SIZE %g Hz;"

    detector_get_command = "SENSe:SA:DET:FUNC?;"
    detector_set_command = "SENSe:SA:DET:FUNC %s;"

    trace_mode_get_command = "CALCulate:MEASure:HOLD:TYPE?;"
    trace_mode_set_command = "CALCulate:MEASure:HOLD:TYPE %s;"

    average_type_get_command = "SENSe:SA:BANDwidth:VIDeo:AVER:TYPE?;"
    average_type_set_command = "SENSe:SA:BANDwidth:VIDeo:AVER:TYPE %s;"

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Keysight P5003A Spectrum Analyzer",
            **kwargs
        )
        """ Enable Spectrum Analysis """
        self.write("CALCulate1:MEASure1:DELete")
        self.write("CALCulate:MEASure:DEFine 'a1:Spectrum Analyzer'")
        self.write("DISP:MEAS:FEED 1")

    def trace(self, number=1):
        """ Returns a numpy array of the data for a particular trace
        based on the trace number (1, 2, or 3).
        """
        self.write(":FORMat:DATA ASCII;")
        data = np.loadtxt(
            StringIO(self.ask("CALCulate%d:MEASure%d:DATA:FDATA?;" % (number, number))),
            delimiter=',',
            dtype=np.float64
        )
        return data

    def reset(self):
        super().reset()
        """Reset disables Spectrum Analysis"""
        self.write("CALCulate1:MEASure1:DELete")
        self.write("CALCulate:MEASure:DEFine 'A:Spectrum Analyzer'")
        self.write("DISP:MEAS:FEED 1")
