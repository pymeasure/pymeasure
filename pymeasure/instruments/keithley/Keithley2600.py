#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

import numpy
import time

from pymeasure.adapters import FakeAdapter
from pymeasure.instruments import Instrument

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument, RangeException
from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer

import numpy as np
import time


class Keithley2600(Instrument):
    """Represents the Keithely 2600 Series SourceMeters and provides a
    high-level interface for interacting with the instrument.

    #Todo: Define and implement the required functions using TSP commands sent over the adapter
    #Idea: Define TSP_string and append commands to the script. Start, i.e. send to the instrument, with TSP_to_instrument ??

    .. code-block:: python

        keithley = Keithley2600("GPIB::1")

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

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "Keithley2600 SourceMeter",
            includeSCPI=False,
            **kwargs
        )

        #define startup and local variables here

        self._wait = wait
        self._tstart = 0
        self._voltage = 10
        self._output_voltage = 0
        self._time = 0
        self._wave = self.wave
        self._units = {'voltage': 'V',
                       'output_voltage': 'V',
                       'time': 's',
                       'wave': 'a.u.'}


    ###############
    # Current (A) #
    ###############




    ###############
    # Voltage (V) #
    ###############








    def get_time(self):
        """Get elapsed time"""
        if self._tstart == 0:
            self._tstart = time.time()
        self._time = time.time() - self._tstart
        return self._time

    def set_time(self, value):
        """
        Wait for the timer to reach the specified time.
        If value = 0, reset.
        """
        if value == 0:
            self._tstart = 0
        else:
            while self.time < value:
                time.sleep(0.001)

    def reset_time(self):
        """Reset the timer to 0 s."""
        self.time = 0
        self.get_time()

    time = property(fget=get_time, fset=set_time)

    def get_wave(self):
        """Get wave."""
        return float(numpy.sin(self.time))

    wave = property(fget=get_wave)

    def get_voltage(self):
        """Get the voltage."""
        time.sleep(self._wait)
        return self._voltage

    def __getitem__(self, keys):
        return keys

    voltage = property(fget=get_voltage)

    def get_output_voltage(self):
        return self._output_voltage

    def set_output_voltage(self, value):
        """Set the voltage."""
        time.sleep(self._wait)
        self._output_voltage = value

    output_voltage = property(fget=get_output_voltage, fset=set_output_voltage)