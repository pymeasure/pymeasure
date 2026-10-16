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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

import numpy as np

try:
    from scipy.signal import find_peaks
except ImportError:
    find_peaks = None


class SpectrumAnalyzer(Instrument):
    """Represents a generic SCPI Spectrum Analyzer

    The key features of the generic instrument implementation are as follow:
    - interface is intentionally simple to be easily adapted to wide range of
    spectrum analyzers.
    - all the functions that could efficiently implemented in python are not
    implemented (e.g. peak search, mathematical operations on the traces, unit
    translation, etc.), this can be referred as pure software implementation
    of part of the instrument.
    - all the features which are relevant for interactive use of the instrument
    are not implemented(e.g. markers, display control, multiple traces, etc.)
    - a default implementation using commands based on SCPI specification 1999
    is provided, but all properties are declared dynamic so subclasses
    can easily modify them.

    The default implementation could be good to address also spectrum
    analyzers not yet implemented, since the default SCPI commands are quite
    common with major vendors.

    This class is normally subclassed to implement specific instruments.

Example of initialization

.. code-block:: python

    # Example for Agilent E4440A
    from pymeasure.instruments.spectrum_analyzer import SpectrumAnalyzer

    sa = SpectrumAnalyzer('GPIB0::18::INSTR', "Generic/Unknown Spectrum Analyzer")
    # Read instrument ID
    sa.id
    # 'Agilent Technologies, E4440A, MY44022480, A.11.13'


Single sweep acquisition and peak value calculation

.. code-block:: python

    sa.reset()
    sa.input_attenuation = 10
    sa.resolution_bw     = 100000
    sa.frequency_center  = 868e6
    sa.frequency_span    = 100e6
    sa.sweep_mode_continuous = "OFF"
    sa.trace_mode = "WRITE"

    # Make a single sweep
    sa.sweep_single()

    # Acquire trace
    trace = sa.trace

    # Find peak in the trace
    peak = max(trace)

    # check if any error occurred
    sa.check_errors()


    """

    # Software part of the instrument
    @staticmethod
    def peaks(values, **kwargs):
        """Return peaks in waveform described by values list

        There are several algorithm to perform this, one of them using scipy.find_peaks method.

        This is part of the pure software implementaiton of the instrument.

        :param values: list of floating points numbers
        :param \\**kwargs: keyword arguments to be passed to find peak algorithm
        :return: a list of indexes identifing the peaks, the list indexes are
        sorted by peak magnitude
        """

        peaks_idx = None
        if find_peaks is not None:
            peaks_idx, _ = find_peaks(values, **kwargs)
            peaks_idx = list(peaks_idx)
            peaks_idx.sort(key=lambda x: values[x], reverse=True)

        return peaks_idx

    @property
    def x_axis(self):
        """ Returns a numpy array of x_axis values which can be frequencies(Hz) or time (seconds)
        in case of zero span.
        """
        if self.frequency_span == 0:
            x_min = 0
            x_max = self.sweep_time
        else:
            x_min = self.frequency_start
            x_max = self.frequency_stop

        return np.linspace(
            x_min,
            x_max,
            self.sweep_points,
            dtype=np.float64
        )

    # Instrument command interface part
    resolution_bw = Instrument.control(
        ":SENSe:BANDwidth?;", ":SENSe:BANDwidth %d Hz;",
        """ A floating point property that represents the instrument resolution bandwidth (RBW) in Hz.
        This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    video_bw = Instrument.control(
        ":SENSe:BANDwidth:VIDeo?;", ":SENSe:BANDwidth:VIDeo %d Hz;",
        """ A floating point property that represents the instrument video bandwidth (VBW) in Hz.
        This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    input_attenuation = Instrument.control(
        ":SENSe:POWer:ATTenuation?;", ":SENSe:POWer:ATTenuation %d;",
        """ An floating point property that represents the instrument the input attenuation in dB.
        This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    frequency_span = Instrument.control(
        ":SENS:FREQ:SPAN?;", ":SENS:FREQ:SPAN %d Hz;",
        """ An integer property that represents the frequency span
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    frequency_start = Instrument.control(
        ":SENS:FREQ:STAR?;", ":SENS:FREQ:STAR %e Hz;",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    frequency_stop = Instrument.control(
        ":SENS:FREQ:STOP?;", ":SENS:FREQ:STOP %e Hz;",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    frequency_center = Instrument.control(
        ":SENS:FREQ:CENT?;", ":SENS:FREQ:CENT %e Hz;",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    sweep_points = Instrument.control(
        ":SENSe:SWEEp:POINts?;", ":SENSe:SWEEp:POINts %d;",
        """ An integer property that represents the number of
        points in the sweep. This property can take values according to specific spectrum analyzer.
        """,
        validator=truncated_range,
        # Intentional very high upper limit but in reality limit not specified for generic
        # instrument
        values=(0, 10000000),
        cast=int,
        dynamic=True
    )

    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?;", ":SENS:SWE:TIME %.2e;",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """,
        validator=truncated_range,
        values=(0, float("inf")),  # Limit not specified for generic instrument
        dynamic=True
    )

    sweep_mode_continuous = Instrument.control(
        ":INITiate:CONTinuous?;", ":INITiate:CONTinuous %s;",
        """ A boolean property that allows you to switches the analyzer between continuous-sweep and
        single-sweep mode. This property can be set.
        """,
        validator=strict_discrete_set,
        values={"ON": 1,
                "OFF": 0},
        cast=int,
        map_values=True,
        dynamic=True
    )

    detector = Instrument.control(
        ":SENSe:DETector?;", ":SENSe:DETector %s;",
        """ A string property that allows you to select a specific type of detector.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=("NORM", "AVER", "POS", "SAMP", "NEG", "RMS"),
        dynamic=True
    )

    trace_mode = Instrument.control(
        ":TRACe:MODE?;",  ":TRACe:MODE %s;",
        """ A string property that enable you to set how trace information is stored and displayed.
        allowed values are "WRITE", "MAXHOLD", "MINHOLD"
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=("WRITE", "MAXHOLD", "MINHOLD"),
        cast=str,
        dynamic=True
    )

    trace = Instrument.measurement(
        ":TRACE:DATA? TRACE1;",
        """Read the instrument trace data""",
        dynamic=True
    )

    average_type = Instrument.control(
        "AVERage:TYPE?;",  "AVERage:TYPE %s;",
        """ A string property that enable you to set and read the averaging type.
        Allowed values are:
        - "POWER": Sets Power (RMS) averaging
        - "VOLTAGE": Sets Voltage averaging (linear)
        - "VIDEO": Sets Log-Power (video) averaging
        """,
        validator=strict_discrete_set,
        values={"POWER": "RMS",
                "VOLTAGE": "SCAL",
                "VIDEO": "LOG"},
        map_values=True,
        dynamic=True
    )

    def __init__(self, resourceName, description, **kwargs):
        super(SpectrumAnalyzer, self).__init__(
            resourceName,
            description,
            **kwargs
        )

        # Operate in ASCII mode
        self.write(":FORMat:DATA ASCII;")

    def sweep_single(self):
        """ Perform a single sweep and wait for completion. 'sweep_mode_continuous' must be OFF """
        self.write("INIT:IMM")
        self.complete
