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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.adapters import VISAAdapter
from pymeasure.instruments.validators import (
    truncated_discrete_set, strict_discrete_set,
    truncated_range
)
from time import sleep, time
import numpy as np
import re


class AMI430(Instrument):
    """ Represents the AMI 430 Power supply
    and provides a high-level for interacting with the instrument.

    .. code-block:: python

        magnet = AMI430("TCPIP::web.address.com::7180::SOCKET")

        
        magnet.coilconst = 1.182                 # kGauss/A
        magnet.voltage_limit = 2.2               # Sets the voltage limit in V

        magnet.target_current = 10               # Sets the target current to 10 A
        magnet.target_field = 1                  # Sets target field to 1 kGauss

        magnet.ramp_rate_current = 0.0357       # Sets the ramp rate in A/s
        magnet.ramp_rate_field = 0.0422         # Sets the ramp rate in kGauss/s
        magnet.ramp                             # Initiates the ramping
        magnet.pause                            # Pauses the ramping
        magnet.status                           # Returns the status of the magnet
    
        magnet.ramp_to_current(5)             # Ramps the current to 5 A

        magnet.shutdown()                     # Ramps the current to zero and disables output

    """
    def __init__(self, resourceName, **kwargs):
        adapter = VISAAdapter(resourceName, read_termination='\n')
        super(ami430, self).__init__(
            adapter,
            "AMI superconducting magnet power supply.",
            includeSCPI=True,
            **kwargs
        )
        # Read twice in order to remove welcome/connect message
        self.read()
        self.read()

    maximumfield = 1.00
    maximumcurrent = 50.63

    coilconst = Instrument.control(
        "COIL?", "CONF:COIL %g",
        """ A floating point property that sets the coil contant
        in kGauss/A. """
    )

    voltage_limit = Instrument.control(
        "VOLT:LIM?", "CONF:VOLT:LIM %g",
        """ A floating point property that sets the voltage limit
        for charging/discharging the magnet. """
    )

    target_current = Instrument.control(
        "CURR:TARG?", "CONF:CURR:TARG %g",
        """ A floating point property that sets the target current
        in A for the magnet. """
    )

    target_field = Instrument.control(
        "FIELD:TARG?", "CONF:FIELD:TARG %g",
        """ A floating point property that sets the target field
        in kGauss for the magnet. """
    )

    ramp_rate_current = Instrument.control(
        "RAMP:RATE:CURR:1?", "CONF:RAMP:RATE:CURR 1,%g",
        """ A floating point property that sets the current ramping 
        rate in A/s. """
    )

    ramp_rate_field = Instrument.control(
        "RAMP:RATE:FIELD:1?", "CONF:RAMP:RATE:FIELD 1,%g,1.00",
        """ A floating point property that sets the field ramping 
        rate in kGauss/s. """
    )

    magnet_current = Instrument.measurement("CURR:MAG?",
        """ Reads the current in Amps of the magnet.
        """
    )

    supply_current = Instrument.measurement("CURR:SUPP?",
        """ Reads the current in Amps of the power supply.
        """
    )

    field = Instrument.measurement("FIELD:MAG?",
        """ Reads the field in kGauss of the magnet.
        """
    )

    state = Instrument.measurement("STATE?",
        """ Reads the field in kGauss of the magnet.
        """
    )

    def zero(self):
        """ Initiates the ramping of the magnetic field to zero
        current/field with ramping rate previously set. """
        self.write("ZERO")

    def pause(self):
        """ Pauses the ramping of the magnetic field. """
        self.write("PAUSE")

    def ramp(self):
        """ Initiates the ramping of the magnetic field to set
        current/field with ramping rate previously set.
        """
        self.write("RAMP")

    def has_persistent_switch_enabled(self):
        """ Returns a boolean if the persistent switch is enabled. """
        return bool(self.ask("PSwitch?"))

    def enable_persistent_switch(self):
        """ Enables the persistent switch. """
        self.write("PSwitch 1")

    def disable_persistent_switch(self):
        """ Disables the persistent switch. """
        self.write("PSwitch 0")

    @property
    def magnet_status(self):
        STATES = {
            1: "RAMPING",
            2: "HOLDING",
            3: "PAUSED",
            4: "Ramping in MANUAL UP",
            5: "Ramping in MANUAL DOWN",
            6: "ZEROING CURRENT in progress",
            7: "QUENCH!!!",
            8: "AT ZERO CURRENT",
            9: "Heating Persistent Switch",
            10: "Cooling Persistent Switch"
        }
        return STATES[self.state]

    def ramp_to_current(self, current, rate):
        """ Heats up the persistent switch and
        ramps the current with set ramp rate.
        """
        self.enable_persistent_switch()

        self.target_current = current
        self.ramp_rate_current = rate

        self.wait_for_holding()

        self.ramp()

    def ramp_to_field(self, field, rate):
        """ Heats up the persistent switch and
        ramps the current with set ramp rate.
        """
        self.enable_persistent_switch()

        self.target_field = field

        self.ramp_rate_field = rate

        self.wait_for_holding()

        self.ramp()

    def wait_for_holding(self, should_stop=lambda: False,
                         timeout=800, interval=0.1):
        """
        """
        t = time()
        while self.state != 2 and self.state != 3 and self.state != 8:
            sleep(interval)
            if should_stop():
                return
            if (time()-t) > timeout:
                raise Exception("Timed out waiting for AMI430 switch to warm up.")

    def shutdown(self, ramp_rate=0.0357):
        """ Turns on the persistent switch,
        ramps down the current to zero, and turns off the persistent switch.
        """
        self.enable_persistent_switch()
        self.wait_for_holding()
        self.ramp_rate_current = ramp_rate
        self.zero()
        self.wait_for_holding()
        self.disable_persistent_switch()
