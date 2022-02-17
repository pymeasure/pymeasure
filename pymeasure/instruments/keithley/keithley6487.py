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


    
    #####################
    #   Voltage (V)     #
    #####################
    source_enables = Instrument.control(
        ":SOUR:STAT?", ":SOUR:STAT %s",
        """A string property that controls whether the voltage source is
        enabled, takes values OFF or ON. The convenience methods :meth:
        `~.Keithley6487.enable_source` and
        :meth:`~Keithley6487.disable_source` can also be used""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
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
    
