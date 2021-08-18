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
    """ Represents a generic SCPI Spectrum Analyzer and provides a high-level interface for controlling basic instrument parameters and caputring traces.

    The interface is intentionally simple in order to be adapted to wide range
    of spectrum analyzers.
    This class is normally subclassed to implement specific instruments. Other use case include the basic management of spectrum analyzer not yet implemented.

Example of initialization

.. code-block:: python

    # Example for Agilent E4440A Spectrum Analyzer
    from pymeasure.instruments.agilent import AgilentE4440A

    sa = AgilentE4440A('GPIB0::18::INSTR')
    # Read instrument ID
    sa.id
    # 'Agilent Technologies, E4440A, MY44022480, A.11.13'


Single sweep acquisition and peak value calculation

.. code-block:: python

    sa.reset()
    sa.reference_level = 0.0
    sa.resolution_bw = 100000
    sa.center_frequency = 868e6
    sa.frequency_span = 100e6
    sa.sweep_mode_continuous = "OFF"
    sa.trace_mode = "WRITE"
    
    # Make a single sweep
    sa.sweep_single()

    # Acquire trace
    trace = sa.trace()

    # Find peak in the trace
    peak = max(trace)

    # check if any error occurred
    sa.check_errors()


    """

    reference_level = Instrument.control(
        ":DISPlay:WINDow:TRACe:Y:RLEVel?;", ":DISPlay:WINDow:TRACe:Y:RLEVel %e dBm;",
        """ A floating point property that represents the absolute amplitude of the top graticule line on the display (the
        reference level) in dBm. This property can be set.
        """,
        validator=truncated_range,
        values=(-170, 30),
        dynamic=True
    )

    resolution_bw = Instrument.control(
        ":SENSe:BANDwidth?;", ":SENSe:BANDwidth %d Hz;",
        """ A floating point property that represents the instrument resolution bandwidth (RBW) in Hz.
        This property can be set.
        """,
        validator=truncated_range,
        values=(1, 8e6),
        dynamic=True
    )

    input_attenuation = Instrument.control(
        ":SENSe:POWer:ATTenuation?;", ":SENSe:POWer:ATTenuation %d;",
        """ An integer property that represents the instrument the input attenuation in dB.
        This property can be set.
        """,
        validator=truncated_range,
        values=(0, 70),
        dynamic=True
    )

    frequency_span = Instrument.control(
        ":SENS:FREQ:SPAN?;", ":SENS:FREQ:SPAN %d Hz;",
        """ An integer property that represents the frequency span
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=(0, 26.5e9),
        dynamic=True
    )

    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?;", ":SENS:FREQ:STAR %e Hz;",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """,
        dynamic=True
    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?;", ":SENS:FREQ:STOP %e Hz;",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """,
        dynamic=True
    )
    frequency_points = Instrument.control(
        ":SENSe:SWEEp:POINts?;", ":SENSe:SWEEp:POINts %d;",
        """ An integer property that represents the number of frequency
        points in the sweep. This property can take values from 101 to 8192.
        """,
        validator=truncated_range,
        values=(101, 8192),
        cast=int,
        dynamic=True
    )
    frequency_step = Instrument.control(
        ":SENS:FREQ:CENT:STEP:INCR?;", ":SENS:FREQ:CENT:STEP:INCR %g Hz;",
        """ A floating point property that represents the frequency step
        in Hz. This property can be set.
        """,
        dynamic=True
    )
    center_frequency = Instrument.control(
        ":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e Hz;",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """,
        dynamic=True
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?;", ":SENS:SWE:TIME %.2e;",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """,
        dynamic=True
    )

    detector = Instrument.control(
        ":SENSe:DETector?;", ":SENSe:DETector %s;",
        """ A string property that allows you to select a specific type of detector
        in seconds. This property can be set.
        """,
        validator=strict_discrete_set,
        values=("NORM", "AVER", "POS", "SAMP", "NEG", "RMS"),
        dynamic=True
    )

    sweep_mode_continuous = Instrument.control(
        ":INITiate:CONTinuous?;", ":INITiate:CONTinuous %s;",
        """ A boolean property that allows you to switches the analyzer between continuous-sweep and single-sweep mode.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values={"ON" : 1,
                "OFF" : 0},
        cast = int,
        map_values = True,
        dynamic=True
    )

    trace_mode = Instrument.control(
        ":TRACe:MODE?;",  ":TRACe:MODE %s;",
        """ A string property that enable you to set how trace information is stored and displayed.
        allowed values are "WRITE", "MAXHOLD", "MINHOLD", "VIEW", "BLANK"
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=("WRITE", "MAXHOLD", "MINHOLD", "VIEW", "BLANK"),
        cast=str,
        dynamic=True        
    )

    average_type = Instrument.control(
        "AVERage:TYPE?;",  "AVERage:TYPE %s;",
        """ A string property that enable you to set and read the averaging type.
        Allowed values are:
        - "POWER": Sets Power (RMS) averaging
        - "VOLTAGE": Sets Voltage averaging (linear)
        - "VIDEO": Sets Log-Power (video) averaging
        This property can be set.
        """,
        validator=strict_discrete_set,
        values={"POWER" : "RMS",
                "VOLTAGE" : "SCAL",
                "VIDEO" : "LOG"
            },
        map_values = True,
        dynamic=True
    )

    sweep_type = Instrument.control(
        ":SWEep:TYPE?;",  ":SWEep:TYPE %s;",
        """ A string property that enable you to set and read the sweep type.
        Allowed values are:
        - "": Sets Power (RMS) averaging
        - "VOLTAGE": Sets Voltage averaging (linear)
        - "VIDEO": Sets Log-Power (video) averaging
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=("SWEEP", "FFT"),
        dynamic=True
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

    def sweep_single(self):
        """ Perform a single sweep and wait for completion. 'sweep_mode_continuous' must be OFF """
        self.write("INIT:IMM")
        self.complete
