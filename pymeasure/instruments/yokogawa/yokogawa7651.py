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

    def __init__(self, resourceName, **kwargs):
        super(Yokogawa7651, self).__init__(
            resourceName,
            "Yokogawa 7651 Programmable DC Source",
            **kwargs
        )
        
        self.write("H0;E") # Set no header in output data
        self.adapter.config()
        
        # Simple control parameters
        self.add_control("source_voltage", "OD;E", "S%g;E")
        self.add_control("source_current", "OD;E", "S%g;E")
        self.add_control("voltage", "OD;E", "S%g;E")
        self.add_control("current", "OD;E", "S%g;E")
        
    @property
    def id(self):
        return self.ask("OS;E")
        
    @property
    def enabled(self):
        """See if 5th bit is set in the OC flag."""
        oc = int(self.ask("OC;E")[5:])
        return True if (oc & 0b10000) else False

    @enabled.setter
    def enabled(self, value):
        if value:
            log.info("Enabling Yokogawa")
            self.write("O1;E")
        else:
            self.write("O0;E")
        
    def config_current_source(self, max_current, cycle=False):
        """For current range specified in A, set the device to the proper mode
        the options are 1mA, 10mA, 100mA. This function automatically rounds up
        to the necessary range."""

        index = int(math.log10(max_current*0.95e3)+5.0)
        if (index < 4):
            index = 4
        elif (index > 6):
            index = 6

        # Turn off output first, then set the source and turn on again
        if cycle:
            self.enabled = False
        self.write("F5;R%d;E" % index)
        if cycle:
            self.enabled = True

    def config_voltage_source(self, max_voltage, cycle=False):
        """For voltage range specified in V, set the device to the proper mode
        the options are 10mV, 100mV, 1V, 10V, 30V This function automatically
        rounds up to the necessary range."""

        index = int(math.log10(max_voltage*0.95e3)+2.0)
        if (index < 2):
            index = 2
        elif (index > 6):
            index = 6

        # Turn off output first, then set the source and turn on again
        if cycle:
            self.enabled = False
        self.write("F1;R%d;E" % index)
        if cycle:
            self.enabled = True

    def ramp_to_current(self, current, steps=25, duration=0.5):
        """ For current in A, time in seconds """
        start_current = self.source_current
        stop_current = current
        pause = duration/steps
        if (start_current != stop_current):
            currents = np.linspace(start_current, stop_current, steps)
            for current in currents:
                self.source_current = current
                time.sleep(pause)

    def ramp_to_voltage(self, voltage, steps=25, duration=0.5):
        """ For voltage in V, time in seconds """
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
        self.ramp_to_current(0.0, steps=25)
        self.source_current = 0.0
        self.enabled = False
