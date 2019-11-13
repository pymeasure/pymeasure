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

from time import sleep
import numpy as np
import pandas as pd
import logging
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class NoPeakError(Error):
    """Raised when no peak is found"""
    pass

class AgilentN9320A(Instrument):
    """ Represents the AgilentN9320A Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums."""

    FREQ_LIMIT = [9e3, 3.08e9] #Frequency limit in Hz
    SPAN_LIMIT = [0, 3e9]      #In zero span the X axis represents time
    REF_LIMIT = [-100, 50]     #Reference level limit in dBm
    ATT_LIMIT = [0, 70]        #Input attenuator limit in dB
    RES_LIMIT = [10, 30, 100, 300, 1000, 3000,
                10000, 30000, 100000, 300000]      #RBW values
    VID_LIMIT = RES_LIMIT       #VBW values
    PEAK_TH = -70.             #Peak threshold for peak recognition in dBm
    PEAK_EXC = 3               #Peak excursion
    D_FACTOR = 2               #A multiplicative factor for the sweep time in
                               #peak function
    DELAY = 0.2                #A delay in second can be useful


    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?", ":SENS:FREQ:STAR %e Hz",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.""",
		validator=strict_range,
		values=FREQ_LIMIT
    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?", ":SENS:FREQ:STOP %e Hz",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.""",
		validator=strict_range,
		values=FREQ_LIMIT
    )
    center_frequency = Instrument.control(
        ":SENS:FREQ:CENT?", ":SENS:FREQ:CENT %eHz",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.""",
		validator=strict_range,
		values=FREQ_LIMIT
    )
    span = Instrument.control(
        ":SENS:FREQ:SPAN?", ":SENS:FREQ:SPAN %eHz",
        """ A floating point property that represents the frequency span
        in Hz. This property can be set.""",
		validator=strict_range,
		values=SPAN_LIMIT
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?", ":SENS:SWE:TIME %.2e",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set."""
    )
    ref_level = Instrument.control(
        ":DISP:WIND:TRAC:Y:SCAL:RLEV?", ":DISP:WIND:TRAC:Y:SCAL:RLEV %.2f",
        """ A floating point property that represents the reference level
        in dBm. This property can be set.""",
        validator=strict_range,
        values=REF_LIMIT
    )
    attenuation = Instrument.control(
        ":SENS:POW:RF:ATT?", ":SENS:POW:RF:ATT %d",
        """ A floating point property that represents the input attenuator
        in dB. This property can be set.""",
        validator=strict_range,
        values=ATT_LIMIT
    )
    resolution_bandwidth = Instrument.control(
        ":SENS:BAND:RES?", ":SENS:BAND:RES %e",
        """ A floating point property that represents the resolution
        bandwidth in Hz. This property can be set.""",
        validator=strict_discrete_set,
        values=RES_LIMIT
    )
    video_bandwidth = Instrument.control(
        ":SENS:BAND:VID?", ":SENS:BAND:VID %e",
        """ A floating point property that represents the video
        bandwidth in Hz. This property can be set.""",
        validator=strict_discrete_set,
        values=VID_LIMIT
    )

    def __init__(self, adapter, **kwargs):
         (AgilentN9320A, self).__init__(
            adapter,
            "Agilent AgilentN9320A Spectrum Analyzer",
            **kwargs
        )

    def display_on(self):
        """Switch on the display"""
        self.write("DISP:ENAB 1")

    def display_off(self):
        """Switch off the display."""
        self.write("DISP:ENAB 0")

    def init_immediate(self):
        """This method initiates a sweep if not in a measurement. If
        in a measurement, it triggers the measurement."""
        self.write("INIT:IMM")

    def init_continuos(self):
        """Trigger system is continuosly initiated."""
        self.write("INIT:CONT 1")

    def init_single(self):
        """The sweep system remains in an idle state until init_continuos
        is set or init_immediate is received. When init_immediate
        command received, it will go through a single sweep cycle, and then
        return to the idle state."""
        self.write("INIT:CONT 0")

    def set_opc_sqr(self, timeout=10):
        """Set the instrument to generate SRQ when operation is complete:
        remember to run a *CLS before the command that you want
        to sync/wait for. Timeout in seconds."""
        self.adapter.timeout=timeout*1000
        self.write("*ESE 1;*SRE 32")

    def opc(self, timeout=10):
        """Operation complete? Returns 1 or 0. You may need to change the
        visa timeout (in ms) for long lasting operations.
        Timeout in seconds."""
        self.adapter.timeout=timeout*1000
        return int(self.ask("*OPC?"))

    def error_check(self, value=None):
        """It look for the last entry in the error queue. If value is defined
        it returns true if the last error corresponds to value."""
        if value==None:
            return self.ask("SYST:ERR?")
        else:
            return self.ask("SYST:ERR?")==value

    def marker_x(self, number=1):
        """Returns the frequency in Hz at marker position."""
        return float(self.ask("CALC:MARK%s:X?" % number))

    def marker_y(self, number=1):
        """Returns the amplitude in dBm at marker position."""
        return format(float(self.ask("CALC:MARK%s:Y?" % number)), '.4f')

    def average_number(self, value=10):
        """Set the number of averages."""
        self.write("SENS:AVER:COUN %d" % strict_range(value, [1, 1000]))

    def average_on(self):
        self.write("SENS:AVER:STAT ON")
        """Activate the averaging."""

    def average_off(self):
        """De-activate the averaging."""
        self.write("SENS:AVER:STAT OFF")

    def set_peak_max(self):
        """Peak search method: the max value of the trace is taken. Next peak
        commands always use threshold and excursion method."""
        self.write("CALC:MARK:PEAK:SEAR:MODE MAX")

    def set_peak_par(self, number=1, threshold=PEAK_TH, excursion=PEAK_EXC):
        """Peak search method using threshold and excursion."""
        self.write("CALC:MARK:PEAK:SEAR:MODE PAR")
        self.write("CALC:MARK:PEAK:THR:EXC %.2f" % excursion)
        self.write("CALC:MARK%s:PEAK:THR %.2f" % (number, threshold))
        self.write("CALC:MARK:PEAK:THR:STATE 1")

    def peak_search(self, number=1):
        """Peak search: the search method can be set with set_peak_par or
        set_peak_max."""
        self.write("CALC:MARK%s:MAX" % number)

    def next_peak_right(self,number=1):
        """Search the next peak on the right of the actual position of the
        marker. It always use threshold and excursion. """
        self.write("CALC:MARK%s:MAX:RIGHT" %number)

    def next_peak_left(self,number=1):
        """Search the next peak on the left of the actual position of the
        marker. It always use threshold and excursion. """
        self.write("CALC:MARK%s:MAX:LEFT" %number)

    def peak_exist(self,number=1):
        """Check if there is a peak in the trace. It has to be used after
        peak_search, next_peak_left or next_peak_right. If no error it returns
        [freq, amplitude] of the cursor number-th. If error it returns
        [NAN, NAN]."""
        if self.error_check('780 No Peak Found'):
            log.info('No peak found!')
            return False, [[float('NAN'), float('NAN')]]
        else:
            x =  self.marker_x(number)
            log.info('Peak found at %g Hz' %x)
            return True, [[x ,self.marker_y(number)]]

    def peak_output(self, number=1, avg=5, center=False, lr=False):
        """ Returns the frequency and the intensity of the highest peak.
        It can center the central frequency to the central peak.
        It can also look the first peaks at both left and right
        around the highest one."""
        self.set_opc_sqr(self, timeout=self.D_FACTOR*self.sweep_time*avg)
        self.init_single()
        self.average_on()
        self.average_number(avg)
        self.set_peak_par(number,self.PEAK_TH,self.PEAK_EXC)

        sleep(self.DELAY)

        self.write("*CLS")
        self.init_immediate()
        self.peak_search(number)
        is_there, peaks = self.peak_exist(number)

        if  is_there:
            if center:
                sleep(self.DELAY)
                self.write("CALC:MARK%s:SET:CENT" % number)
            if lr == True:
                self.next_peak_left(number)
                peaks.append(self.peak_exist(number)[1])
                sleep(self.DELAY)
                self.peak_search(number)
                self.next_peak_right(number)
                peaks.append(self.peak_exist(number)[1])
        else:
            log.info('No peak in the trace.')

        return peaks

            # if lr == True:
            #     self.write("CALC:MARK%s:MAX:LEFT" % number)
            #     sleep(self.DELAY)
            #     if self.ask("SYST:ERR?") == '780 No Peak Found':
            #         print('No peak at left')
            #         x = float('NAN')
            #         y = float('NAN')
            #     else:
            #         x = self.max_x(number)
            #         y = self.max_y(number)
            #         print('LEFT founded at %s Hz, amplitude %s dBm' % (x, y))
            #     peaks.append([x, y])
            #
            #     print('Back to max')
            #     self.max(number)
            #     print('Looking right')
            #     self.write("CALC:MARK%s:MAX:RIGHT" % number)
            #     sleep(self.DELAY)
            #     if self.ask("SYST:ERR?") == '780 No Peak Found':
            #         print('No peak at right')
            #         x = float('NAN')
            #         y = float('NAN')
            #     else:
            #         x = self.max_x(number)
            #         y = self.max_y(number)
            #         print('RIGHT founded at %s Hz, amplitude %s dBm' % (x, y))
            #     peaks.append([x, y])


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