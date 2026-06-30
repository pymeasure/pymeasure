#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import truncated_range

from io import StringIO
import numpy as np
import pandas as pd


class AgilentE4408B(SCPIMixin, Instrument):
    """Represents the AgilentE4408B Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums.
    """

    def __init__(self, adapter, name="Agilent E4408B Spectrum Analyzer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?;", ":SENS:FREQ:STAR %e Hz;",
        """Control the start frequency in Hz (float).""",
    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?;", ":SENS:FREQ:STOP %e Hz;",
        """Control the stop frequency in Hz (float).""",
    )
    frequency_points = Instrument.control(
        ":SENSe:SWEEp:POINts?;", ":SENSe:SWEEp:POINts %d;",
        """Control the number of frequency points in the sweep
        (int, truncated from 101 to 8192).""",
        validator=truncated_range,
        values=[101, 8192],
        cast=int
    )
    frequency_step = Instrument.control(
        ":SENS:FREQ:CENT:STEP:INCR?;", ":SENS:FREQ:CENT:STEP:INCR %g Hz;",
        """Control the frequency step in Hz (float).""",
    )
    center_frequency = Instrument.control(
        ":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e Hz;",
        """Control the center frequency in Hz (float).""",
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?;", ":SENS:SWE:TIME %.2e;",
        """Control the sweep time in seconds (float).""",
    )

    @property
    def frequencies(self):
        """Get a numpy array of frequencies in Hz corresponding to the current settings."""
        return np.linspace(
            self.start_frequency,
            self.stop_frequency,
            self.frequency_points,
            dtype=np.float64
        )

    def trace(self, number: int = 1):
        """Get a numpy array of the data for a particular trace.

        :param number: Trace number (1, 2, or 3).
        """
        self.write(":FORMat:TRACe:DATA ASCII;")
        data = np.loadtxt(
            StringIO(self.ask(f":TRACE:DATA? TRACE{number};")),
            delimiter=',',
            dtype=np.float64
        )
        return data

    def trace_df(self, number=1):
        """Get a pandas DataFrame containing the frequency and peak data for a particular trace."""
        return pd.DataFrame({
            'Frequency (GHz)': self.frequencies * 1e-9,
            'Peak (dB)': self.trace(number)
        })
