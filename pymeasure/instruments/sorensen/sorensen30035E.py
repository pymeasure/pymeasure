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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range

import time


class Sorensen30035E(Instrument):
    """ Represents the Sorensen300-3.5E power supply with GPIB option and provides a
    high-level interface for interacting with the instrument. Use good judgement and
    protect the power supply outputs with flyback and blocking diodes if you have an
    inductive load. See the Sorensen manual for advice.


    .. code-block:: python

        sorensen = Sorensen30035E("GPIB::1")

        sorensen.enable_source()                # Enables output of current
        sorensen.ramp_to_voltage(200,200)       # Ramp to 200 V in 200 seconds nominally

        print(sorensen.current)                 # Prints the actual current output in Amps

        sorensen.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    def __init__(self, adapter, **kwargs):
        super(Sorensen30035E, self).__init__(
            adapter, "Sorensen 300-3.5E DC Power Supply", **kwargs
        )

    source_delay = Instrument.control(
        "OUTPut:PROTection:DELay?", "OUTPut:PROTection:DELay %g",
        """ A floating point property that sets a manual delay for the source
        after the output is turned on before a measurement is taken and the reverse.
        between 0 [seconds] and 999.9999 [seconds].""",
        validator=strict_range,
        values=[0, 999.9999],
    )

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        "MEASure:CURRent?",
        """ Returns the actual current in Amps. Note that this is subject to the precision
        and calibration of the internal DMM.
        """
    )

    current_setpoint = Instrument.control(
        "SOUR:CURR?", "SOUR:CURR %g",
        """ A floating point property that immediately sets the desired current output
        in Amps, which can take floating point values between 0 and +3.5 A. """,
        validator=strict_range,
        values=[0, 3.5]
    )

    current_limit = Instrument.control(
        "SOUR:CURR:LIM?", "SOUR:CURR:LIM %g",
        """ Sets an upper soft limit on the programmed output current
        for the supply. Can take values floating point from 0 and +3.5 A. """,
        validator=strict_range,
        values=[0, 3.5]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """ Returns the actual voltage in Volts. Note that this is subject to the precision
        and calibration of the internal DMM.
        """
    )
    voltage_setpoint = Instrument.control(
        "SOUR:VOLT?", "SOUR:VOLT %g",
        """ A floating point property that immediately sets the desired voltage output
        in Volts, which can take floating point values between 300 and 300 V. """,
        validator=strict_range,
        values=[-300, 300]
    )

    voltage_limit = Instrument.control(
        "SOUR:VOLT:LIM?", "SOUR:VOLT:LIM %g",
        """ Sets an upper soft limit on the programmed output voltage
        for the supply. Can take values floating point from 0 and 300 V. """,
        validator=strict_range,
        values=[0, 300]
    )

    @property
    def output_enabled(self):
        return self.query("OUTPut:ISOLation?")

    @output_enabled.setter
    def output_enabled(self, state):
        if state:
            if not self.output_enabled:
                self.write("OUTPut:ISOLation 1")
        elif not state:
            if self.output_enabled:
                if self.current_setpoint > 0:
                    self.ramp_to_current(0, int(self.current_setpoint) * 20)
                    while self.current > 0.01:
                        time.sleep(.1)
                    self.write("OUTPut:ISOLation 0")

    def ramp_to_voltage(self, value, time=10):
        """ Utilizes built in ramp function of the power supply to ramp voltage
         to the specified value in the requested time. The large capacitance used to
         suppress ripple in the power supply may affect charging/discharging times for
         low currents/high impedance samples. """
        if value > 300:
            raise ValueError("Requested voltage too large, |V| must be 300 V or less")
        self.write("SOUR:VOLT:RAMP %g %g" % (value, time))

    def ramp_to_current(self, value, time=10):
        """ Utilizes built in ramp function of the power supply to ramp voltage
         to the specified value in the requested time. The large capacitance used to
         suppress ripple in the power supply may affect charging/discharging times for
         low currents/high impedance samples. """
        if value > 3.5:
            raise ValueError("Requested current too large, |I| must be 3.5 A or less")
        self.write("SOUR:CURR:RAMP %g %g" % (value, time))

    def abort_ramp(self):
        """ Aborts all in-progress ramps
        """
        self.write("SOUR:CURR:RAMP:ABOR")
        self.write("SOUR:VOLT:RAMP:ABOR")

    def shutdown(self):
        """ Disables the  output after ramping down at 1 V/s if voltage is non-zero."""
        voltage = self.voltage
        current = self.current
        if voltage > 0.1 or current > 0.008:
            self.ramp_to_voltage(0, voltage)
            i = 0
        while self.voltage > 0.1:
            time.sleep(1)
            i = i + 1
            if i > 3 * voltage:
                raise ValueError("Voltage has not reached zero in reasonable time,"
                                 "giving up, OUTPUT IS STILL LIVE")
        self.source_enable = False
