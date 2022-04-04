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

# from pymeasure.instruments import Instrument

import logging
import time

import numpy as np

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Keithley6487(Instrument, KeithleyBuffer):
    """Represents the Keithley 6487 Picoammeter and provides a 
    high-level interface for interactin gwith the instrument
    
    .. code-block:: python
        
        keithley = Keithley6487("GPIB::1")
        
        keithley.apply_voltage()                # Sets up a source voltage
        keithley.source_voltage_range = 10e-3   # Sets the voltage range
        to 10 mV
        keithley.compliance_voltage = 10        # Sets the compliance voltage
        to 10 V
        keithley.enable_source()                # Enables the source output

        keithley.measure_current()              # Sets up to measure current

        keithley.ramp_to_voltage(1)             # Ramps voltage to 1 V

        keithley.shutdown()                     # Ramps the voltage to 0 V and
        disables output
        """
    
    auto_zero = Instrument.control(
        ":SYST:AZER:STAT?", ":SYST:AZER:STAT %s",
        """ A property that controls the auto zero option. Valid values are
        True (enabled) and False (disabled) and 'ONCE' (force immediate). """,
        values={True: 1, False: 0, "ONCE": "ONCE"},
        map_values=True,
    )

    line_frequency = Instrument.control(
        ":SYST:LFR?", ":SYST:LFR %d",
        """ An integer property that controls the line frequency in Hertz.
        Valid values are 50 and 60. """,
        validator=strict_discrete_set,
        values=[50, 60],
        cast=int,
    )

    line_frequency_auto = Instrument.control(
        ":SYST:LFR:AUTO?", ":SYST:LFR:AUTO %d",
        """ A boolean property that enables or disables auto line frequency.
        Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )
    
    #####################
    #   Voltage (V)     #
    #####################
    source_enabled = Instrument.control(
        ":SOUR:VOLT:STAT?", ":SOUR:VOLT:STAT %s",
        """A string property that controls whether the voltage source is
        enabled, takes values OFF or ON. The convenience methods :meth:
        `~.Keithley6487.enable_source` and
        :meth:`~Keithley6487.disable_source` can also be used""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    auto_output_off = Instrument.control(
        ":SOUR:CLE:AUTO?", ":SOUR:CLE:AUTO %d",
        """ A boolean property that enables or disables the auto output-off.
        Valid values are True (output off after measurement) and False (output
        stays on after measurement). """,
        values={True: 1, False: 0},
        map_values=True,
    )
    
    source_delay = Instrument.control(
        ":SOUR:VOLT:DEL?", ":SOUR:VOLT:DEL %g",
        """ A floating point property that sets a manual delay for the source
        after the output is turned on before a measurement is taken. When this
        property is set, the auto delay is turned off. Valid values are
        between 0 [seconds] and 999.9999 [seconds].""",
        validator=truncated_range,
        values=[0, 999.9999],
    )

    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT:LEV %g",
        """ A floating point property that controls the source voltage
        in Volts. """
    )

    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG:AUTO 0;:SOUR:VOLT:RANG %g",
        """ A floating point property that controls the source voltage
        range in Volts, which can take values of 10, 50, or 500V.
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10.0, 50.0, 500.0]
    )

    #####################
    #   Current (A)     #
    #####################

    current = Instrument.measurement(
        ":READ?",
        """ Reads the current in Amps.
        """
    )

    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0; :SEND:CURR:RANG %g",
        """A floating point property that controls the measurement the current
        range in Amps, which can take values between -0.021 and +0.021 A.
        Auto-range is disabled when this property is set""",
        validator=truncated_range,
        values=[-0.021, 0.021]
    )

    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.001 to 6.0 or 5.0, where 6.0
        is 60Hz and 5.0 is 50Hz"""
    )


    ####################
    #   Methods        #
    ####################

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Keithley 6487 Picoammeter", **kwargs
        )

    def enable_source(self):
        """Enables the source voltage of the instrument"""
        self.write(":SOUR:STAT ON")
    
    def disable_source(self):
        """Disables the source voltage of the instrument"""
        self.write(":SOUR:STAT: OFF")
    
