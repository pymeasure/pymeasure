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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from io import StringIO
import numpy as np
import pandas as pd


class SpectrumAnalyzer(Instrument):
    """ Represents a generic SCPI Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums
    """
    REFERENCE_LEVEL_RANGE_MIN_dBm = -170
    REFERENCE_LEVEL_RANGE_MAX_dBm = 30

    FREQUENCY_MIN_Hz = 1
    FREQUENCY_MAX_Hz = 26.5e9

    RESOLUTION_BW_RANGE_MIN_Hz = 1
    RESOLUTION_BW_RANGE_MAX_Hz = 8e6

    INPUT_ATTENUATION_RANGE_dB = [0, 70]

    SWEEP_POINTS_RANGE = [101, 8192]

    DETECTOR_VALUES=["NORM", "AVER", "POS", "SAMP", "NEG", "QPE", "EAV", "EPOS", "MPOS", "RMS"],

    reference_level = Instrument.control(
        ":DISPlay:WINDow:TRACe:Y:RLEVel?;", ":DISPlay:WINDow:TRACe:Y:RLEVel %e dBm;",
        """ A floating point property that represents the absolute amplitude of the top graticule line on the display (the
reference level) in dBm. This property can be set.
        """
    )

    resolution_bw = Instrument.control(
        ":SENSe:BANDwidth?;", ":SENSe:BANDwidth %d Hz;",
        """ A floating point property that represents the instrument resolution bandwidth (RBW) in Hz.
        This property can be set.
        """,
        #validator=truncated_range,
        #values=RESOLUTION_BW_RANGE_Hz,
        cast=int
    )

    input_attenuation = Instrument.control(
        ":SENSe:POWer:ATTenuation?;", ":SENSe:POWer:ATTenuation %d;",
        """ An integer property that represents the instrument the input attenuation in dB.
        This property can be set.
        """,
        #validator=truncated_range,
        #values=INPUT_ATTENUATION_RANGE_dB,
        cast=int
    )

    frequency_span = Instrument.control(
        ":SENS:FREQ:SPAN?;", ":SENS:FREQ:SPAN %d Hz;",
        """ An integer property that represents the frequency span
        in Hz. This property can be set.
        """,
        #validator=truncated_range,
        #values=FREQUENCY_SPAN_RANGE_Hz,
        cast=int
    )

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
        #validator=truncated_range,
        #values=SWEEP_POINTS_RANGE,
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

    detector = Instrument.control(
        ":SENSe:DETector?;", ":SENSe:DETector %s;",
        """ A string property that allows you to select a specific type of detector
        in seconds. This property can be set.
        """,
        #validator=strict_discrete_set,
        #values=DETECTOR_VALUES,
        cast=str
    )

    sweep_mode = Instrument.control(
        ":INITiate:CONTinuous?;", ":INITiate:CONTinuous %d;",
        """ A boolean property that allows you to switches the analyzer between continuous-sweep and single-sweep mode.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=[0, 1],
        cast=int
    )
    TRACE_MODE_COMMAND = ":TRACe:MODE"
    trace_mode = Instrument.control(
        TRACE_MODE_COMMAND + "?;",  TRACE_MODE_COMMAND + " %s;",
        """ A string property that enable you to set how trace information is stored and displayed.
        allowed values are "WRITE", "MAXHOLD", "MINHOLD", "VIEW", "BLANK"
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=["WRITE", "MAXHOLD", "MINHOLD", "VIEW", "BLANK"],
        cast=str
    )

    def __init__(self, resourceName, description, **kwargs):
        super(SpectrumAnalyzer, self).__init__(
            resourceName,
            description,
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
        self.write(":FORMat:DATA ASCII;")
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

    def sweep_start(self):
        pass

    def sweep_single(self):
        self.write("INIT:IMM")
        self.complete
        
    def check_errors(self):
        """Return any accumulated errors.
        """
        retVal = []
        while True:
            error = self.ask("SYSTEM:ERROR?")
            f = error.split(",")
            errorCode = int(f[0])
            if errorCode == 0:
                break
            else:
                retVal.append(error)
        return retVal
