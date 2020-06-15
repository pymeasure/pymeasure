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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument, RangeException
from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


import numpy as np
import time
from io import BytesIO
import re


class Sorensen30035E(Instrument):
    """ Represents the Sorensen300-3.5E power supply with GPIB option and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        sorensen = Sorensen30035E("GPIB::1")

        sorensen.enable_source()                # Enables output of current
        sorensen.ramp_to_current(200,200)       # Ramp to 200 V in 200 seconds nominally
        
        print(sorensen.current)                 # Prints the actual current output in Amps

        sorensen.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    source_enable = Instrument.control(
        "OUTPut:PROTection:STATe?", "OUTPut:PROTection:STATe %d",
        """A boolean property that sets the ouput to zero or the programmed value,
        openning or closing the isolation relay. *RST value is ON. CAUTION: Ensure
        that suitable delays are incorporated to preclude hot switching of the isolation relay.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    source_isolation = Instrument.control(
        "OUTPut:ISOLation?", "OUTPut:ISOLation %d",
        """A boolean property that controls whether the isolation relay is enabled. 
        DO NOT disable if the current is non-zero, i.e. no hot-switching""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    polarity = Instrument.control(
        "OUTPut:POLarity?", "OUTPut:POLarity %d",
        """ A boolean property that enables switches the polarity of the power supply
        via a relay. source_enable (the isolation relay) must be False when switching this parameter or else
        an error will be generated. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    source_delay = Instrument.control(
        "OUTPut:PROTection:DELay?", "OUTPut:PROTection:DELay %g",
        """ A floating point property that sets a manual delay for the source
        after the output is turned on before a measurement is taken and the reverse.
        between 0 [seconds] and 999.9999 [seconds].""",
        validator=truncated_range,
        values=[0, 999.9999],
    )


    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        "MEASure:CURRent?",
        """ Returns the actual current in Amps.
        """
    )

    current_setpoint = Instrument.control(
        "SOUR:CURR?", "SOUR:CURR %g",
        """ A floating point property that immediately sets the desired current output 
        in Amps, which can take floating point values between -3.5 and +3.5 A. """,
        validator=truncated_range,
        values=[-3.5, 3.5]
    )

    current_limit = Instrument.control(
        "SOUR:CURR:LIM?", "SOUR:CURR:LIM %g",
        """ Sets an upper soft limit on the programmed output current
        for the supply. Can take values floating point from 0 and +3.5 A. """,
        validator=truncated_range,
        values=[0, 3.5]
    )    



    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """ Returns the actual voltage in Volts.
        """
    )
    voltage_setpoint = Instrument.control(
        "SOUR:VOLT?", "SOUR:VOLT %g",
        """ A floating point property that immediately sets the desired voltage output 
        in Volts, which can take floating point values between 300 and 300 V. """,
        validator=truncated_range,
        values=[-300, 300]
    )

    voltage_limit = Instrument.control(
        "SOUR:VOLT:LIM?", "SOUR:VOLT:LIM %g",
        """ Sets an upper soft limit on the programmed output voltage
        for the supply. Can take values floating point from 0 and 300 V. """,
        validator=truncated_range,
        values=[0, 300]
    )    


    def __init__(self, adapter, **kwargs):
        super(Sorenson30035E, self).__init__(
            adapter, "Sorenson 300-3.5E DC Power Supply", **kwargs
        )

    def ramp_to_voltage(self, value, time=10):
        """ Utilizes built in ramp function of the power supply to ramp voltage
         to the specified value in the requested time. The large capacitance used to
         suppress ripple in the power supply may affect charging/discharging times for
         low currents/high impedance samples. """
         if abs(value) > 300:
            raise ValueError("Requested voltage too large, |V| must be 300 V or less")
         self.write("SOUR:VOLT:RAMP %g %g" % (value, time))

    def ramp_to_current(self, value, time=10):
        """ Utilizes built in ramp function of the power supply to ramp voltage
         to the specified value in the requested time. The large capacitance used to
         suppress ripple in the power supply may affect charging/discharging times for
         low currents/high impedance samples. """
         if abs(value) > 3.5:
            raise ValueError("Requested current too large, |I| must be 3.5 A or less")
         self.write("SOUR:CURR:RAMP %g %g" % (value, time))

    def abort_ramp(self):
        """ Aborts all in-progress ramps
        """
        self.write("SOUR:CURR:RAMP:ABOR")

    def enable_source(self):
        """ Enables the output of the power supply (switch isolation relays on) """
        if self.source_enable == False:
            self.source_enable = True
        else:
            pass

    def disable_source(self):
        """ Disables the  output in an unprotected way. DO NOT use this carelessly, use shutdown,
        it's safer."""
        if self.source_enable == True:
            self.source_enable = False
        else:
            pass

    def shutdown(self):
        """ Disables the  output after ramping down at 1 V/s if voltage is non-zero."""
        if abs(self.voltage) >0.01 or abs(self.current) >0.0001:
            voltage = self.voltage
            self.ramp_to_voltage(0,voltage)
            i = 0
        while self.voltage >0.01:
            time.sleep(1)
            i = i+1
            if i > 3*voltage:
                raise ValueError("Voltage has not reached zero in reasonable time, giving up, OUTPUT IS STILL LIVE")
        self.source_enable = False

    

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', '')
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Keithley 2400 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2400 error retrieval.")

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("*RST;*CLS;")

