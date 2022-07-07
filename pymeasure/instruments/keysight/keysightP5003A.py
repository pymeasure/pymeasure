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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from io import StringIO
import numpy as np


class KeysightP5003A(SpectrumAnalyzer):
    """ This class represent a Keysight P5003A VNA with S97090B	Spectrum analysis option  """

    # Customize parameters with values taken from datasheet/user manual 

    reference_level_values = (-500, 500)

    frequency_span_values = (1, 14e9)

    resolution_bw_values = (5, 3e6)

    input_attenuation_values = (0, 70)

    frequency_points_values = (1, 100003)

    detector_values = ("PEAK", "AVER", "SAMP", "NORM", "NEGP", "PSAM", "PAV")

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

    input_attenuation = Instrument.control(
        "SOURce:POWer:ATTenuation:RECeiver:TEST?;", "SOURce:POWer:ATTenuation:RECeiver:TEST %d;",
        """ An integer property that represents the instrument the input attenuation in dB.
        This property can be set.
        """,
        validator=truncated_range,
        values=(0, 70),
        dynamic=True
    )

    frequency_step = Instrument.control(
        "SENSe:FREQuency:CENTer:STEP:SIZE?;", "SENSe:FREQuency:CENTer:STEP:SIZE %g Hz;",
        """ A floating point property that represents the frequency step
        in Hz. This property can be set.
        """,
        dynamic=True
    )

    detector = Instrument.control(
        "SENSe:SA:DET:FUNC?;", "SENSe:SA:DET:FUNC %s;",
        """ A string property that allows you to select a specific type of detector
        in seconds. This property can be set.
        """,
        validator=strict_discrete_set,
        values=("PEAK", "AVER", "SAMP", "NORM", "NEGP", "PSAM", "PAV"),
        dynamic=True
    )

    trace_mode = Instrument.control(
        "CALCulate:MEASure:HOLD:TYPE?;",  "CALCulate:MEASure:HOLD:TYPE %s;",
        """ A string property that enable you to set how trace information is stored and displayed.
        allowed values are "OFF", "MAX", "MIN"
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=("OFF", "MIN", "MAX"),
        cast=str,
        dynamic=True        
    )

    average_type = Instrument.control(
        "SENSe:SA:BANDwidth:VIDeo:AVER:TYPE?;",  "SENSe:SA:BANDwidth:VIDeo:AVER:TYPE %s;",
        """ A string property that enable you to set and read the averaging type.
        Allowed values are:
        - "POWER": Sets Power (RMS) averaging
        - "VOLTAGE": Sets Voltage averaging (linear)
        - "VIDEO": Sets Log-Power (video) averaging
        """,
        validator=strict_discrete_set,
        values=("VOLT", "POW", "LOG", "VMAX", "VMIN"),
        cast=str,
        dynamic=True
    )

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
        self.write("*RST")
        """Reset disables Spectrum Analysis"""
        self.write("CALCulate1:MEASure1:DELete")
        self.write("CALCulate:MEASure:DEFine 'a1:Spectrum Analyzer'")
        self.write("DISP:MEAS:FEED 1")
