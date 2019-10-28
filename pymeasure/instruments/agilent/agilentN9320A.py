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
from pymeasure.instruments.validators import strict_range, strict_discrete_set

from time import sleep
import numpy as np
import pandas as pd

class AgilentN9320A(Instrument):
    """ Represents the AgilentN9320A Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums
    """

    FREQ_LIMIT = [9e3, 3.08e9] #Frequency limit in Hz
    SPAN_LIMIT = [0, 3e9]      #In zero span the X axis represents time
    REF_LIMIT = [-100, 50]     #Reference level limit in dBm
    ATT_LIMIT = [0, 70]        #Input attenuator limit in dB
    RES_LIMIT = [10, 30, 100, 300, 1000, 3000,
                10000, 30000, 100000, 300000]      #RBW values
    VID_LIMIT = RES_LIMIT       #VBW values
    PEAK_TH = -70.             #Peak threshold for peak recognition in dBm

    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?", ":SENS:FREQ:STAR %e Hz",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """,
		validator=strict_range,
		values=FREQ_LIMIT
    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?", ":SENS:FREQ:STOP %e Hz",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """,
		validator=strict_range,
		values=FREQ_LIMIT
    )
    center_frequency = Instrument.control(
        ":SENS:FREQ:CENT?", ":SENS:FREQ:CENT %eHz",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """,
		validator=strict_range,
		values=FREQ_LIMIT
    )
    span = Instrument.control(
        ":SENS:FREQ:SPAN?", ":SENS:FREQ:SPAN %eHz",
        """ A floating point property that represents the frequency span
        in Hz. This property can be set.
        """,
		validator=strict_range,
		values=SPAN_LIMIT
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?", ":SENS:SWE:TIME %.2e",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """
    )
    ref_level = Instrument.control(
        ":DISP:WIND:TRAC:Y:SCAL:RLEV?", ":DISP:WIND:TRAC:Y:SCAL:RLEV %.2f",
        """ A floating point property that represents the reference level
        in dBm. This property can be set.
        """,
        validator=strict_range,
        values=REF_LIMIT
    )
    att = Instrument.control(
        ":SENS:POW:RF:ATT?", ":SENS:POW:RF:ATT %d",
        """ A floating point property that represents the input attenuator
        in dB. This property can be set.
        """,
        validator=strict_range,
        values=ATT_LIMIT
    )
    res_bw = Instrument.control(
        ":SENS:BAND:RES?", ":SENS:BAND:RES %e",
        """ A floating point property that represents the reference level
        in dBm. This property can be set.
        """,
        validator=strict_discrete_set,
        values=RES_LIMIT
    )
    vid_bw = Instrument.control(
        ":SENS:BAND:VID?", ":SENS:BAND:VID %e",
        """ A floating point property that represents the reference level
        in dBm. This property can be set.
        """,
        validator=strict_discrete_set,
        values=VID_LIMIT
    )

    def __init__(self, resourceName, **kwargs):
        super(AgilentN9320A, self).__init__(
            resourceName,
            "Agilent AgilentN9320A Spectrum Analyzer",
            **kwargs
        )

    def opc(self):
        return self.ask("*OPC?")

    def peak(self, center=True, number=1):
        """ Returns the frequency and the intensity of the highest peak.
        It can center the central frequency to the central peak.
        """
        self.write("CALC:MARK:PEAK:THR %f" % self.PEAK_TH)
        sleep(2*self.sweep_time)
        self.write("CALC:MARK:MAX")
        if center:
            self.write("CALC:MARK:SET:CENT")
        sleep(2*self.sweep_time)
        return self.ask("CALC:MARK:Y?")


    def trace(self, number=1):
        """ Returns two numpy arrays, data and frequency, for a particular
        trace based on the trace number (1, 2, or 3).
        """
        data = [float(i) for i in self.ask(":TRACE:DATA? TRACE%d" %
                number).split(',')[:-1]]

        frequency = np.linspace(
            self.start_frequency,
            self.stop_frequency,
            len(data),
            dtype=np.float64
        )
        return np.array(data), frequency

    def trace_df(self, number=1):
        """ Returns a pandas DataFrame containing the frequency
        and peak data for a particular trace, based on the
        trace number (1, 2, or 3).
        """
        return pd.DataFrame({
            'Frequency (Hz)': self.trace(number)[1],
            'Amplitude (dBm)': self.trace(number)[0]
        })