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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range, joined_validators

# Capitalize string arguments to allow for better conformity with other WFG's
def capitalize_string(string: str, *args, **kwargs):
    return string.upper()

# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class SignalGenerator(Instrument):
    """Represents a generic analog Signal Generator and 
    provides a high-level interface for interacting with 
    the instrument.
    """
    POWER_RANGE_MIN_dBm = -130.0
    POWER_RANGE_MAX_dBm = 30.0
    POWER_RANGE_dBm = [POWER_RANGE_MIN_dBm, POWER_RANGE_MAX_dBm]

    FREQUENCY_MIN_Hz = 1
    FREQUENCY_MAX_Hz = 1e9
    FREQUENCY_RANGE_Hz = [FREQUENCY_MIN_Hz, FREQUENCY_MAX_Hz]

    power = Instrument.control(
        ":POW?;", ":POW %g dBm;",
        """ A floating point property that represents the output power
        in dBm. This property can be set.
        """,
        #validator=strict_range,
        #values=lambda x: (getattr(x, 'POWER_RANGE_MIN_dBm'), getattr(x, 'POWER_RANGE_MAX_dBm'))
    )
    frequency = Instrument.control(
        ":FREQ?;", ":FREQ %e Hz;",
        """ A floating point property that represents the output frequency
        in Hz. This property can be set.
        """,
        validator=strict_range,
        values=FREQUENCY_RANGE_Hz
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
    stop_power = Instrument.control(
        ":SOUR:POW:STOP?", ":SOUR:POW:STOP %e dBm",
        """ A floating point property that represents the stop power
        in dBm. This property can be set.
        """
    )
    step_points = Instrument.control(
        ":SOUR:SWE:POIN?", ":SOUR:SWE:POIN %d",
        """ An integer number of points in a step sweep. This property
        can be set.
        """
    )
    rf_enable = Instrument.control(
        ":OUTPUT?", ":OUTPUT %d", 
        """ A boolean property that tell if RF output is enabled or not. 
        This property can be set. """,
        cast=int
    )

    ########################
    # Amplitude modulation #
    ########################

    amplitude_modulation_enable = Instrument.control(
        ":SOUR:AM:STAT?", ":SOUR:AM:STAT %s", 
        """ A boolean property that enables or disables the amplitude modulation for the selected path. 
        This property can be set. """,
        validator=strict_discrete_set,
        values=["ON", "OFF"],
    )
    amplitude_depth = Instrument.control(
        ":SOUR:AM:DEPT?", ":SOUR:AM:DEPT %g",
        """ A floating point property that controls the amplitude modulation
        in percent, which can take values from 0 to 100 %. """,
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

    pulse_modulation_enable = Instrument.control(
        ":SOUR:PULM:STAT?", ":SOUR:PULM:STAT %s",
        """ A boolean property that enables or disables the operating state of the pulse modulation source.
        This property can be set. """,
        validator=strict_discrete_set,
        values=["ON", "OFF"],
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

    low_freq_out_enable = Instrument.control(
        ":SOUR:LFO:STAT? ", ":SOUR:LFO:STAT %d",
        """ A boolean property that tell if RF modulation output is enabled or not. 
        This property can be set. """,
        cast=int
    )

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

    def config_low_freq_out(self, source='internal', amplitude=3):
        """ Configures the low-frequency output signal.

        :param source: The source for the low-frequency output signal.
        :param amplitude: Amplitude of the low-frequency output
        """
        self.low_freq_out_enable = 1
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

    def __init__(self, adapter, description, **kwargs):
        super(SignalGenerator, self).__init__(
            adapter, description, **kwargs
        )

    def enable_modulation(self):
        self.low_freq_out_source = 'internal'
        self.low_freq_out_amplitude = 2.0
        self.low_freq_out_enable = 1

    def disable_modulation(self):
        """ Disables the signal modulation. """
        self.modulation_enable = 0
        self.low_freq_out_enable = 0

    def config_amplitude_modulation(self, frequency=1e3, depth=100.0, shape='sine'):
        """ Configures the amplitude modulation of the output signal.

        :param frequency: A modulation frequency for the internal oscillator
        :param depth: A linear depth precentage
        :param shape: A string that describes the shape for the internal oscillator
        """
        self.amplitude_modulation_enable = 1
        self.amplitude_source = 'internal'
        self.internal_frequency = frequency
        self.internal_shape = shape
        self.amplitude_depth = depth

    def config_pulse_modulation(self, frequency=1e3, input='square'):
        """ Configures the pulse modulation of the output signal.

        :param frequency: A pulse rate frequency in Hertz
        :param input: A string that describes the internal pulse input
        """
        self.pulse_modulation_enable = 1
        self.pulse_source = 'internal'
        self.pulse_input = input
        self.pulse_frequency = frequency

    def data_load_repeated(self, bitsequence, spacing, repetitions):
        """ Load digital data into signal generator for transmission, the parameters are:
        bitsequence: string of '1' or '0' in transmission order
        repetitions: integer, how many times the bit sequence is repeated
        spacing: integer, gap between repetition expressed in number of bit
        """
        self.data_load((bitsequence,)*repetitions, (spacing,)*repetitions)

    def data_load(self, bitsequences, spacings):
        """ Load data into signal generator for transmission, the parameters are:
        bitsequences: list of items. Each item is a string of '1' or '0' in transmission order
        spacings: integer list, gap to be inserted between each bitsequence  expressed in number of bit
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")

    def data_trigger_setup(self, mode='SINGLE'):
        """ Configure the trigger system for bitsequence transmission
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")

    def data_trigger(self):
        """ Trigger a bitsequence transmission
        """
        # Subclasses should implement this
        raise Exception ("Not supported/implemented")

    def shutdown(self):
        """ Shuts down the instrument by disabling any modulation
        and the output signal.
        """
        self.disable_modulation()
        self.disable()
 
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
        
