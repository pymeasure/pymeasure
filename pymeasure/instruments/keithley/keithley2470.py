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

import logging
import time

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
from .buffer import KeithleyBuffer
from .keithley2450 import Keithley2450

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2470(Keithley2450):
    """ Represents the Keithely 2450 SourceMeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2470("GPIB::1")

        keithley.apply_current()                # Sets up to source current
        keithley.source_current_range = 10e-3   # Sets the source current range to 10 mA
        keithley.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        keithley.source_current = 0             # Sets the source current to 0 mA
        keithley.enable_source()                # Enables the source output

        keithley.measure_voltage()              # Sets up to measure voltage

        keithley.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(keithley.voltage)                 # Prints the voltage in Volts

        keithley.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    ###############
    # Voltage (V) #
    ###############

    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1100, 1100]
    )

    compliance_voltage = Instrument.control(
        ":SOUR:CURR:VLIM?", ":SOUR:CURR:VLIM %g",
        """ A floating point property that controls the compliance voltage
        in Volts. """,
        validator=truncated_range,
        values=[-1100, 1100]
    )

    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG:AUTO 0;:SOUR:VOLT:RANG %g",
        """ A floating point property that controls the source voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1100, 1100]
    )
