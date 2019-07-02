#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range

from io import StringIO
import numpy as np
import pandas as pd


class AgilentE4408B(Instrument):
    """ Represents the AgilentE4408B Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums
    """

    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?;", ":SENS:FREQ:STAR %e Hz;",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """
    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?;", ":SENS:FREQ:STOP %e Hz;",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """
    )
    frequency_points = Instrument.control(
        ":SENSe:SWEEp:POINts?;", ":SENSe:SWEEp:POINts %d;",
        """ An integer property that represents the number of frequency
        points in the sweep. This property can take values from 101 to 8192.
        """,
        validator=truncated_range,
        values=[101, 8192],
        cast=int
    )
    frequency_step = Instrument.control(
        ":SENS:FREQ:CENT:STEP:INCR?;", ":SENS:FREQ:CENT:STEP:INCR %g Hz;",
        """ A floating point property that represents the frequency step
        in Hz. This property can be set.
        """
    )
    center_frequency = Instrument.control(
        ":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e Hz;",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?;", ":SENS:SWE:TIME %.2e;",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """
    )

    def __init__(self, resourceName, **kwargs):
        super(AgilentE4408B, self).__init__(
            resourceName,
            "Agilent E4408B Spectrum Analyzer",
            **kwargs
        )

    @property
    def frequencies(self):
        """ Returns a numpy array of frequencies in Hz that 
        correspond to the current settings of the instrument.
        """
        return np.linspace(
            self.start_frequency, 
            self.stop_frequency,
            self.frequency_points,
            dtype=np.float64
        )

    def trace(self, number=1):
        """ Returns a numpy array of the data for a particular trace
        based on the trace number (1, 2, or 3).
        """
        self.write(":FORMat:TRACe:DATA ASCII;")
        data = np.loadtxt(
            StringIO(self.ask(":TRACE:DATA? TRACE%d;" % number)),
            delimiter=',',
            dtype=np.float64
        )
        return data

    def trace_df(self, number=1):
        """ Returns a pandas DataFrame containing the frequency
        and peak data for a particular trace, based on the 
        trace number (1, 2, or 3).
        """
        return pd.DataFrame({
            'Frequency (GHz)': self.frequencies*1e-9,
            'Peak (dB)': self.trace(number)
        })
        
