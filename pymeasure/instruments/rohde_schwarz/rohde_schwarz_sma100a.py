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

from pymeasure.instruments.signal_generator import SignalGenerator
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range

class RS_SMA100A(SignalGenerator):
    POWER_RANGE_MIN_dBm = -147.0
    POWER_RANGE_MAX_dBm = 18.0

    FREQUENCY_MIN_Hz = 9e3
    FREQUENCY_MAX_Hz = 6e9

    has_modulation = SignalGenerator.measurement(":MOD?",
        """ Reads a boolean value that is True if the modulation is enabled. """,
        cast=bool
    )
    AMPLITUDE_SOURCES = {
        'internal':'INT',
        'external':'EXT'
    }
    PULSE_SOURCES = {
        'internal':'INT', 'external':'EXT'
    }
    PULSE_INPUTS = {} # This parameter has no counterpart on SMA100A, needs to be checked

    low_freq_out_amplitude = SignalGenerator.control(
        ":SOUR:LFO:VOLT? ", ":SOUR:LFO:VOLT %g V",
        """A floating point property that controls the peak voltage (amplitude) of the
        low frequency output in volts, which can take values from 0-3.5V""",
        validator=truncated_range,
        values=[0,4.0]
    )

    LOW_FREQUENCY_SOURCES = {
        'internal':'LF1', 
        'internal 2':'LF2', 
        'both': 'LF12',
        'noise':'NOIS',
        'noise LF1':'LF1Noise',
        'noise LF2':'LF2Noise'
    }

    INTERNAL_SHAPES = {} # Unsupported ?

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Rohde & Schwarz SMA100A Signal Generator",
            **kwargs
        )

    def enable_modulation(self):
        self.write(":MOD ON;")
        self.write(":lfo:sour int; :lfo:ampl 2.0v; :lfo:stat on;")

    def disable_modulation(self):
        """ Disables the signal modulation. """
        self.write(":MOD OFF;")
        self.write(":lfo:stat off;")
