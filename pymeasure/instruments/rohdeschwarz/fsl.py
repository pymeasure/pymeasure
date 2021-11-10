#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

import logging

import numpy as np
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FSL(Instrument):
    """
    Represents a Rohde&Schwarz FSL spectrum analyzer.

    All physical values that can be set can either be as a string of a value
    and a unit (e.g. "1.2 GHz") or as a float value in the base units (Hz,
    dBm, etc.).
    """

    def __init__(self, resourceName, **kwargs):
        super(FSL, self).__init__(
            resourceName, "Rohde&Schwarz FSL", includeSCPI=True, **kwargs
        )

    # Frequency settings ------------------------------------------------------

    freq_span = Instrument.control(
        "FREQ:SPAN?",
        "FREQ:SPAN %s",
        "Frequency span in Hz.",
    )

    freq_center = Instrument.control(
        "FREQ:CENT?",
        "FREQ:CENT %s",
        "Center frequency in Hz.",
    )

    freq_start = Instrument.control(
        "FREQ:STAR?",
        "FREQ:STAR %s",
        "Start frequency in Hz.",
    )

    freq_stop = Instrument.control(
        "FREQ:STOP?",
        "FREQ:STOP %s",
        "Stop frequency in Hz.",
    )

    attenuation = Instrument.control(
        "INP:ATT?",
        "INP:ATT %s",
        "Attenuation in dB.",
    )

    @property
    def res_bandwidth(self):
        """Resolution bandwidth in Hz. Can be set to 'AUTO'."""
        return float(self.ask("BAND:RES?"))

    @res_bandwidth.setter
    def res_bandwidth(self, value):
        if type(value) is str and value.upper() == "AUTO":
            self.write("BAND:RES:AUTO ON")
        else:
            self.write(f"BAND:RES {value}")

    @property
    def video_bandwidth(self):
        """Video bandwidth in Hz. Can be set to 'AUTO'."""
        return float(self.ask("BAND:VID?"))

    @video_bandwidth.setter
    def video_bandwidth(self, value):
        if type(value) is str and value.upper() == "AUTO":
            self.write("BAND:VID:AUTO ON")
        else:
            self.write(f"BAND:VID {value}")

    # Sweeping ----------------------------------------------------------------

    @property
    def sweep_time(self):
        """Sweep time in s. Can be set to 'AUTO'."""
        return self.values("SWE:TIME?")[0]

    @sweep_time.setter
    def sweep_time(self, value):
        if type(value) is str and value.upper() == "AUTO":
            self.write("SWE:TIME:AUTO ON")
        else:
            self.write(f"SWE:TIME {value}")

    continuous_sweep = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %s",
        "Continuous (True) or single sweep (False)",
        validator=strict_discrete_set,
        values=[True, False],
        set_process=lambda x: "ON" if x else "OFF",
        get_process=lambda x: bool(x),
    )

    def single_sweep(self):
        """Perform a single sweep with synchronization."""
        self.write("INIT; *WAI")

    def continue_single_sweep(self):
        """Continue with single sweep with synchronization."""
        self.write("INIT:CONM; *WAI")

    # Traces ------------------------------------------------------------------

    def read_trace(self, n_trace=1):
        """
        Read trace data.

        :param n_trace: The trace number (1-6). Default is 1.
        :return: 2d numpy array of the trace data, [[frequency], [amplitude]].
        """
        y = np.array(self.values(f"TRAC{n_trace}? TRACE{n_trace}"))
        x = np.linspace(self.freq_start, self.freq_stop, len(y))
        return np.array([x, y])

    trace_mode = Instrument.control(
        "DISP:TRAC:MODE?",
        "DISP:TRAC:MODE %s",
        "Trace mode ('WRIT', 'MAXH', 'MINH', 'AVER' or 'VIEW')",
        validator=strict_discrete_set,
        values=["WRIT", "MAXH", "MINH", "AVER", "VIEW"],
    )

    # Markers -----------------------------------------------------------------

    def create_marker(self, num=1, is_delta_marker=False):
        """
        Create a marker.

        :param num: The marker number (1-4)
        :param is_delta_marker: True if the marker is a delta marker, default
            is False.
        :return: The marker object.
        """
        return self.Marker(self, num, is_delta_marker)

    class Marker:
        def __init__(self, instrument, num, is_delta_marker):
            """
            Marker and Delta Marker class.

            :param instrument: The FSL instrument.
            :param num: The marker number (1-4)
            :param is_delta_marker: True if the marker is a delta marker,
                defaults to False.
            """
            self.instrument = instrument
            self.is_delta_marker = is_delta_marker
            # Building the marker name for the commands.
            if self.is_delta_marker:
                # Smallest delta marker number is 2.
                self.name = "DELT" + str(max(2, num))
            else:
                self.name = "MARK"
                if num > 1:
                    # Marker 1 doesn't get a number.
                    self.name = self.name + str(num)

            self.activate()

        def write(self, command):
            self.instrument.write(f"CALC:{self.name}:{command}")

        def values(self, command, **kwargs):
            """
            Reads a set of values from the instrument through the adapter,
            passing on any keyword arguments.
            """
            return self.values(f"CALC:{self.name}:{command}", **kwargs)

        def activate(self):
            """Activate a marker."""
            self.write("STAT ON")

        def disable(self):
            """Disable a marker."""
            self.write("STAT OFF")

        x = Instrument.control(
            "X?", "X %s", "Position of marker on the frequency axis in Hz."
        )

        y = Instrument.control(
            "Y?", "Y %s", "Amplitude of the marker position in dBm."
        )

        peak_excursion = Instrument.control(
            "PEXC?",
            "PEXC %s",
            "Peak excursion in dB.",
        )

        def to_trace(self, n_trace=1):
            """
            Set marker to trace.

            :param n_trace: The trace number (1-6). Default is 1.
            """
            self.write(f"TRAC {n_trace}")

        def to_peak(self):
            """Set marker to highest peak within the span."""
            self.write("MAX")

        def to_next_peak(self, direction="right"):
            """
            Set marker to next peak.

            :param direction: Direction of the next peak ('left' or 'right' of
                the current position).
            """
            self.write(f"MAX:{direction}")

        def zoom(self, value):
            """
            Zoom in to a frequency span or by a factor.

            :param value: The value to zoom in by. If a number is passed it is
                interpreted as a factor. If a string (number with unit) is
                passed it is interpreted as a frequency span.
            """
            self.write(f"FUNC:ZOOM {value}; *WAI")
