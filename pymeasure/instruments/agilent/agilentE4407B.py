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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set, truncated_range

from io import StringIO
import numpy as np
import pandas as pd


class AgilentE4407B(Instrument):
    """ Represents the AgilentE4407B Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums
    """


    #frequency Setting commands
    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?;", ":SENS:FREQ:STAR %e Hz;",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=[9000, 26500000000],
        cast=int

    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?;", ":SENS:FREQ:STOP %e Hz;",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=[9000, 26500000000],
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
        """,
        validator=truncated_range,
        values=[9000, 26500000000],
        cast=int
    )
   
    span = Instrument.control(
        ":SENS:FREQ:SPAN?;", ":SENS:FREQ:SPAN %e Hz;",
        """ A floating point property that represents the span
        in Hz. This property can be set.
        """
    )
    full_span = Instrument.setting(
        ":SENS:FREQ:SPAN:FULL;", """
        A command that sets the span to the full span of the instrument.
     """
    ) 
    last_span = Instrument.setting(
        ":SENS:FREQ:SPAN:PREV;", """
        A command that sets the span to the previous span.
        """
    )
    #sweep commands
    frequency_points = Instrument.control(
        ":SENSe:SWEEp:POINts?;", ":SENSe:SWEEp:POINts %d;",
        """ An integer property that represents the number of frequency
        points in the sweep. This property can take values from 101 to 8192.
        """,
        validator=truncated_range,
        values=[101, 8192],
        cast=int
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?;", ":SENS:SWE:TIME %.2e;",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """
    )
    number_of_segments = Instrument.measurement(
        ":SENS:SWEep:SEGMent:COUNT?;",
        """ An integer property that represents the number of segments
        in the sweep. This property is read-only.
        """
    )
    set_all_segments_sst = Instrument.control(
        ":SENS:SWE:SEGM:DATA? SST", ":SENS:SWE:SEGM:DATA SST,%s;",
        """ A command that sets all the segments of a sweep, at once, with a string.
        format is start, stop, rbw, vbw, points, time
        """
    )
    set_all_segments_csp = Instrument.control(
        ":SENS:SWE:SEGM:DATA? CSP", ":SENS:SWE:SEGM:DATA CSP,%s;",
        """ A command that sets all the segments of a sweep, at once, with a string.
        format is center, span, rbw, vbw, points, time
        """
    )
    merge_segments_sst = Instrument.setting(
        ":SENS:SWE:SEGM:DATA:MERge SST", """
        A command that merges the data with current the segments of a sweep with a string.
        format is start, stop, rbw, vbw, points, time
        """
    )
    merge_segments_csp = Instrument.setting(
        ":SENS:SWE:SEGM:DATA:MERge CSP", """
        A command that merges the data with current the segments of a sweep with a string.
        format is center, span, rbw, vbw, points, time
        """
    )
    


    
    #dectector commands
    resolution_bandwidth = Instrument.control(
        ":SENS:BAND:RES?;", ":SENS:BAND:RES %e Hz;",
        """ A floating point property that represents the resolution bandwidth
        in Hz. This property can be set.
        """
    )
    video_bandwidth = Instrument.control(
        ":SENS:BAND:VID?;", ":SENS:BAND:VID %e Hz;",
        """ A floating point property that represents the video bandwidth
        in Hz. This property can be set.
        """
    )
    resolution_bandwidth_auto = Instrument.control(
        ":SENS:BAND:RES:AUTO?;", ":SENS:BAND:RES:AUTO %d;",
        """ A boolean property that represents the resolution bandwidth
        auto mode. This property can be set.
        """
    )
    video_bandwidth_auto = Instrument.control(
        ":SENS:BAND:VID:AUTO?;", ":SENS:BAND:VID:AUTO %d;",
        """ A boolean property that represents the video bandwidth
        auto mode. This property can be set.
        """
    )
    video_resolution_bandwidth_ratio = Instrument.control(
        ":SENS:BAND:VID:RAT?;", ":SENS:BAND:VID:RAT %e;",
        """ A floating point property that represents the video to resolution
        bandwidth ratio. This property can be set.
        """
    )
    video_resolution_bandwidth_ratio_auto = Instrument.control(
        ":SENS:BAND:VID:RAT:AUTO?;", ":SENS:BAND:VID:RAT:AUTO %d;",
        """ A boolean property that represents the video to resolution
        bandwidth ratio auto mode. This property can be set.
        """
    )
    detector_auto = Instrument.control(
        ":SENS:DET:AUTO?;", ":SENS:DET:AUTO %d;",
        """ A boolean property that represents the detector auto mode.
        This property can be set.
        """
    )
    detector_type = Instrument.control(
        ":SENS:DET:?;", ":SENS:DET %s;",
        """ A string property that represents the detector type.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=["NEG", "POS", "SAMPL", "AVER", "RMS"]
    )
    emi_detector_type = Instrument.control(
        ":SENS:DET:EMI?;", ":SENS:DET:EMI %s;",
        """ A string property that represents the detector type.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values = ["QPE","AVER","OFF"]  
    )
    emi_view_type = Instrument.control(
        ":SENS:DET:EMI:VIEW?;", ":SENS:DET:EMI:VIEW %s;",
        """ A string property that represents the detector type.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values = ["POS","EMI"] 
    )
    qp_detector_gain = Instrument.control(
        ":SENS:POW:QPG?;", ":SENS:POW:QPG %d;",
        """ A boolean property that represents the detector gain.
        This property can be set.
        """
    )
    input_attenuation = Instrument.control(
        ":SENS:POW:ATT?;", ":SENS:POW:ATT %e;",
        """ A floating point property that represents the input attenuation
        in dB. This property can be set.
        """,
        validator=truncated_discrete_set,
        values=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
    )
    input_attenuation_auto = Instrument.control(
        ":SENS:POW:ATT:AUTO?;", ":SENS:POW:ATT:AUTO %d;",
        """ A boolean property that represents the input attenuation
        auto mode. This property can be set.
        """
    )
    max_mixer_power = Instrument.control(
        ":SENS:POW:MIX:RANG?;", ":SENS:POW:MIX:RANG %e;",
        """ A floating point property that represents the maximum mixer power
        in dBm. This property can be set.
        """
    )


    



    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent E4407B Spectrum Analyzer",
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
            'Frequency (GHz)': self.frequencies * 1e-9,
            'Peak (dB)': self.trace(number)
        })
