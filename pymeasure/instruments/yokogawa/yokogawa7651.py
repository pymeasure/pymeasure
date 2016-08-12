#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument

import math
import time
import numpy as np


class Yokogawa7651(Instrument):
    """ Represents the Yokogawa 7651 Programmable DC Source
    and provides a high-level for interacting with the instrument.
    """

    source_voltage = Instrument.control(
        "OD;E", "S%g;E",
        """ A floating point property that controls the source voltage
        in Volts, if that mode is active. """
    )
    source_current = Instrument.control(
        "OD;E", "S%g;E",
        """ A floating point property that controls the source current
        in Amps, if that mode is active. """
    )
    voltage = source_voltage
    current = source_current

    def __init__(self, resourceName, **kwargs):
        super(Yokogawa7651, self).__init__(
            resourceName,
            "Yokogawa 7651 Programmable DC Source",
            **kwargs
        )
        
        self.write("H0;E") # Set no header in output data
        #self.adapter.config() - Removed, unclear of usage
        
    @property
    def id(self):
        """ Returns the identification of the instrument """
        return self.ask("OS;E")
        
    @property
    def source_enabled(self):
        """ Reads a boolean value that is True if the source is enabled, 
        determined by checking if the 5th bit of the OC flag is a binary 1.
        """
        oc = int(self.ask("OC;E")[5:])
        return oc & 0b10000

    def enable_source(self):
        """ Enables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("O1;E")

    def disable_source(self):
        """ Disables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("O0;E")
        
    def config_current_source(self, max_current, cycle=False):
        """ Configures the instrument to source current based on a maximum current
        in Amps, which can take the value of 1, 10, and 100 mA. This function 
        automatically rounds up to the necessary range."""

        index = int(math.log10(max_current*0.95e3)+5.0)
        if (index < 4):
            index = 4
        elif (index > 6):
            index = 6

        # Turn off output first, then set the source and turn on again
        if cycle:
            self.disable_source()
        self.write("F5;R%d;E" % index)
        if cycle:
            self.enable_source()

    def config_voltage_source(self, max_voltage, cycle=False):
        """ Configures the instrument to source voltage based on a maximum voltage
        in Volts, which can take the value of 10 mV, 100 mV, 1 V, 10 V, and 30 V.
        This function automatically rounds up to the necessary range."""

        index = int(math.log10(max_voltage*0.95e3)+2.0)
        if (index < 2):
            index = 2
        elif (index > 6):
            index = 6

        # Turn off output first, then set the source and turn on again
        if cycle:
            self.disable_source()
        self.write("F1;R%d;E" % index)
        if cycle:
            self.enable_source()

    def ramp_to_current(self, current, steps=25, duration=0.5):
        """ Ramps the current to a value in Amps by traversing a linear spacing
        of current steps over a duration, defined in seconds.
        """
        start_current = self.source_current
        stop_current = current
        pause = duration/steps
        if (start_current != stop_current):
            currents = np.linspace(start_current, stop_current, steps)
            for current in currents:
                self.source_current = current
                time.sleep(pause)

    def ramp_to_voltage(self, voltage, steps=25, duration=0.5):
        """ Ramps the voltage to a value in Volts by traversing a linear spacing
        of voltage steps over a duration, defined in seconds.
        """
        start_voltage = self.source_voltage
        stop_voltage = voltage
        pause = duration/steps
        if (start_voltage != stop_voltage):
            voltages = np.linspace(start_voltage, stop_voltage, steps)
            for voltage in voltages:
                self.source_voltage = voltage
                time.sleep(pause)

    def shutdown(self):
        super(Yokogawa7651, self).shutdown()
        # TODO: Check if current or voltage is being sourced
        self.ramp_to_current(0.0, steps=25)
        self.source_current = 0.0
        self.disable_source()
