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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class Agilent8257D(Instrument):
    """Represents the Agilent 8257D Signal Generator and 
    provides a high-level interface for interacting with 
    the instrument.

    .. code-block:: python

        generator = Agilent8257D("GPIB::1")

        generator.power = 0                     # Sets the output power to 0 dBm
        generator.frequency = 5                 # Sets the output frequency to 5 GHz
        generator.enable()                      # Enables the output

    """

    power = Instrument.control(
        ":POW?;", ":POW %g dBm;",
        """ A floating point property that represents the output power
        in dBm. This property can be set.
        """
    )
    frequency = Instrument.control(
        ":FREQ?;", ":FREQ %e Hz;",
        """ A floating point property that represents the output frequency
        in Hz. This property can be set.
        """
    )
    start_frequency = Instrument.control(
        ":SOUR:FREQ:STAR?", ":SOUR:FREQ:STAR %e Hz",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """
    )
    center_frequency = Instrument.control(
        ":SOUR:FREQ:CENT?", ":SOUR:FREQ:CENT %e Hz;",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """
    )
    stop_frequency = Instrument.control(
        ":SOUR:FREQ:STOP?", ":SOUR:FREQ:STOP %e Hz",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """
    )
    start_power = Instrument.control(
        ":SOUR:POW:STAR?", ":SOUR:POW:STAR %e dBm",
        """ A floating point property that represents the start power
        in dBm. This property can be set.
        """
    )
    start_power = Instrument.control(
        ":SOUR:POW:STOP?", ":SOUR:POW:STOP %e dBm",
        """ A floating point property that represents the stop power
        in dBm. This property can be set.
        """
    )
    dwell_time = Instrument.control(
        ":SOUR:SWE:DWEL1?", ":SOUR:SWE:DWEL1 %.3f",
        """ A floating point property that represents the settling time
        in seconds at the current frequency or power setting. 
        This property can be set.
        """
    )
    step_points = Instrument.control(
        ":SOUR:SWE:POIN?", ":SOUR:SWE:POIN %d",
        """ An integer number of points in a step sweep. This property
        can be set.
        """
    )
    is_enabled = Instrument.measurement(":OUTPUT?",
        """ Reads a boolean value that is True if the output is on. """,
        cast=bool
    )
    has_modulation = Instrument.measurement(":OUTPUT:MOD?",
        """ Reads a boolean value that is True if the modulation is enabled. """,
        cast=bool
    )

    ########################
    # Amplitude modulation #
    ########################

    has_amplitude_modulation = Instrument.measurement(":SOUR:AM:STAT?",
        """ Reads a boolean value that is True if the amplitude modulation is enabled. """,
        cast=bool
    )
    amplitude_depth = Instrument.control(
        ":SOUR:AM:DEPT?", ":SOUR:AM:DEPT %g",
        """ A floating point property that controls the amplitude modulation
        in precent, which can take values from 0 to 100 %. """,
        validator=truncated_range,
        values=[0, 100]
    )
    AMPLITUDE_SOURCES = {
        'internal':'INT', 'internal 2':'INT2', 
        'external':'EXT', 'external 2':'EXT2'
    }
    amplitude_source = Instrument.control(
        ":SOUR:AM:SOUR?", ":SOUR:AM:SOUR %s",
        """ A string property that controls the source of the amplitude modulation
        signal, which can take the values: 'internal', 'internal 2', 'external', and
        'external 2'. """,
        validator=strict_discrete_set,
        values=AMPLITUDE_SOURCES,
        map_values=True
    )

    ####################
    # Pulse modulation #
    ####################

    has_pulse_modulation = Instrument.measurement(":SOUR:PULM:STAT?",
        """ Reads a boolean value that is True if the pulse modulation is enabled. """,
        cast=bool
    )
    PULSE_SOURCES = {
        'internal':'INT', 'external':'EXT', 'scalar':'SCAL'
    }
    pulse_source = Instrument.control(
        ":SOUR:PULM:SOUR?", ":SOUR:PULM:SOUR %s",
        """ A string property that controls the source of the pulse modulation
        signal, which can take the values: 'internal', 'external', and
        'scalar'. """,
        validator=strict_discrete_set,
        values=PULSE_SOURCES,
        map_values=True
    )
    PULSE_INPUTS = {
        'square':'SQU', 'free-run':'FRUN',
        'triggered':'TRIG', 'doublet':'DOUB', 'gated':'GATE'
    }
    pulse_input = Instrument.control(
        ":SOUR:PULM:SOUR:INT?", ":SOUR:PULM:SOUR:INT %s",
        """ A string property that controls the internally generated modulation
        input for the pulse modulation, which can take the values: 'square', 'free-run',
        'triggered', 'doublet', and 'gated'.
        """,
        validator=strict_discrete_set,
        values=PULSE_INPUTS,
        map_values=True
    )
    pulse_frequency = Instrument.control(
        ":SOUR:PULM:INT:FREQ?", ":SOUR:PULM:INT:FREQ %g",
        """ A floating point property that controls the pulse rate frequency in Hertz,
        which can take values from 0.1 Hz to 10 MHz. """,
        validator=truncated_range,
        values=[0.1, 10e6]
    )

    ########################
    # Low-Frequency Output #
    ########################

    low_freq_out_amplitude = Instrument.control(
        ":SOUR:LFO:AMPL? ", ":SOUR:LFO:AMPL %g VP",
        """A floating point property that controls the peak voltage (amplitude) of the
        low frequency output in volts, which can take values from 0-3.5V""",
        validator=truncated_range,
        values=[0,3.5]
    )

    LOW_FREQUENCY_SOURCES = {
        'internal':'INT', 'internal 2':'INT2', 'function':'FUNC', 'function 2':'FUNC2'
    }

    low_freq_out_source = Instrument.control(
        ":SOUR:LFO:SOUR?", ":SOUR:LFO:SOUR %s",
        """A string property which controls the source of the low frequency output, which
        can take the values 'internal [2]' for the inernal source, or 'function [2]' for an internal
        function generator which can be configured.""",
        validator=strict_discrete_set,
        values=LOW_FREQUENCY_SOURCES,
        map_values=True
    )

    def enable_low_freq_out(self):
        """Enables low frequency output"""
        self.write(":SOUR:LFO:STAT ON")

    def disable_low_freq_out(self):
        """Disables low frequency output"""
        self.write(":SOUR:LFO:STAT OFF")

    def config_low_freq_out(self, source='internal', amplitude=3):
        """ Configures the low-frequency output signal.

        :param source: The source for the low-frequency output signal.
        :param amplitude: Amplitude of the low-frequency output
        """
        self.enable_low_freq_out()
        self.low_freq_out_source = source
        self.low_freq_out_amplitude = amplitude

    #######################
    # Internal Oscillator #
    #######################

    internal_frequency = Instrument.control(
        ":SOUR:AM:INT:FREQ?", ":SOUR:AM:INT:FREQ %g",
        """ A floating point property that controls the frequency of the internal
        oscillator in Hertz, which can take values from 0.5 Hz to 1 MHz. """,
        validator=truncated_range,
        values=[0.5, 1e6]
    )
    INTERNAL_SHAPES = {
        'sine':'SINE', 'triangle':'TRI', 'square':'SQU', 'ramp':'RAMP', 
        'noise':'NOIS', 'dual-sine':'DUAL', 'swept-sine':'SWEP'
    }
    internal_shape = Instrument.control(
        ":SOUR:AM:INT:FUNC:SHAP?", ":SOUR:AM:INT:FUNC:SHAP %s",
        """ A string property that controls the shape of the internal oscillations,
        which can take the values: 'sine', 'triangle', 'square', 'ramp', 'noise',
        'dual-sine', and 'swept-sine'. """,
        validator=strict_discrete_set,
        values=INTERNAL_SHAPES,
        map_values=True
    )

    def __init__(self, adapter, delay=0.02, **kwargs):
        super(Agilent8257D, self).__init__(
            adapter, "Agilent 8257D RF Signal Generator", **kwargs
        )

    def enable(self):
        """ Enables the output of the signal. """
        self.write(":OUTPUT ON;")

    def disable(self):
        """ Disables the output of the signal. """
        self.write(":OUTPUT OFF;")

    def enable_modulation(self):
        self.write(":OUTPUT:MOD ON;")
        self.write(":lfo:sour int; :lfo:ampl 2.0vp; :lfo:stat on;")

    def disable_modulation(self):
        """ Disables the signal modulation. """
        self.write(":OUTPUT:MOD OFF;")
        self.write(":lfo:stat off;")

    def config_amplitude_modulation(self, frequency=1e3, depth=100.0, shape='sine'):
        """ Configures the amplitude modulation of the output signal.

        :param frequency: A modulation frequency for the internal oscillator
        :param depth: A linear depth precentage
        :param shape: A string that describes the shape for the internal oscillator
        """
        self.enable_amplitude_modulation()
        self.amplitude_source = 'internal'
        self.internal_frequency = frequency
        self.internal_shape = shape
        self.amplitude_depth = depth

    def enable_amplitude_modulation(self):
        """ Enables amplitude modulation of the output signal. """
        self.write(":SOUR:AM:STAT ON")

    def disable_amplitude_modulation(self):
        """ Disables amplitude modulation of the output signal. """
        self.write(":SOUR:AM:STAT OFF")

    def config_pulse_modulation(self, frequency=1e3, input='square'):
        """ Configures the pulse modulation of the output signal.

        :param frequency: A pulse rate frequency in Hertz
        :param input: A string that describes the internal pulse input
        """
        self.enable_pulse_modulation()
        self.pulse_source = 'internal'
        self.pulse_input = input
        self.pulse_frequency = frequency

    def enable_pulse_modulation(self):
        """ Enables pulse modulation of the output signal. """
        self.write(":SOUR:PULM:STAT ON")

    def disable_pulse_modulation(self):
        """ Disables pulse modulation of the output signal. """
        self.write(":SOUR:PULM:STAT OFF")

    def config_step_sweep(self):
        """ Configures a step sweep through frequency """
        self.write(":SOUR:FREQ:MODE SWE;"
                   ":SOUR:SWE:GEN STEP;"
                   ":SOUR:SWE:MODE AUTO;")

    def enable_retrace(self):
        self.write(":SOUR:LIST:RETR 1")

    def disable_retrace(self):
        self.write(":SOUR:LIST:RETR 0")

    def single_sweep(self):
        self.write(":SOUR:TSW")

    def start_step_sweep(self):
        """ Starts a step sweep. """
        self.write(":SOUR:SWE:CONT:STAT ON")

    def stop_step_sweep(self):
        """ Stops a step sweep. """
        self.write(":SOUR:SWE:CONT:STAT OFF")

    def shutdown(self):
        """ Shuts down the instrument by disabling any modulation
        and the output signal.
        """
        self.disable_modulation()
        self.disable()
