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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    truncated_range
)
from time import sleep
import numpy as np



class Chroma62024p6008(Instrument):
    """ Represents the Chroma ATE 62000P Programmable DC Source
    and provides a high-level for interacting with the instrument.

    .. code-block:: python

        chroma = Chroma62024P6008("GPIB::1")

        chroma.apply_current()                # Sets up to source current
        chroma.source_current_range = 10e-3   # Sets the current range to 10 mA
        chroma.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        chroma.source_current = 0             # Sets the source current to 0 mA

        chroma.enable_source()                # Enables the current output
        chroma.ramp_to_current(5e-3)          # Ramps the current to 5 mA

        chroma.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    def __init__(self, adapter, **kwargs):
        super(Chroma62024p6008, self).__init__(
            adapter, "Chroma 62000P Programmable DC Source", **kwargs
        )

    output_current_limit = Instrument.control(
        "SOUR:CURR?", "SOUR:CURR %g",
        """ A floating point property that controls the output current limit setting of the instrument.
        """,
        validator=truncated_range,
        values=[0, 8]
    )

    get_output_status = Instrument.measurement("CONF:OUTP?", "This function queries the output state of the instrument.")

    output_voltage_level = Instrument.control(
        "SOUR:VOLT?", "SOUR:VOLT %g",
        """This function control the output voltage limit of the instrument.
         """,
        validator=truncated_range,
        values=[0, 600]
    )

    output_ovp_limit = Instrument.control(
        "SOUR:VOLT:PROT:HIGH?", "SOUR:VOLT:PROT:HIGH %g",
        """This function control the output current limit of the instrument.
         """,
        validator=truncated_range,
        values=[0, 660]
    )

    output_ocp_limit = Instrument.control(
        "SOUR:CURR:PROT:HIGH?", "SOUR:CURR:PROT:HIGH %ga",
        """This function control the output current of the instrument.
         """,
        validator=truncated_range,
        values=[0, 8.8]
    )

    output_voltage = Instrument.measurement("FETC:VOLT?", "DC output voltage, in Volts")

    output_current = Instrument.measurement("FETC:CURR?", "DC output voltage, in Amps")

    output_slew_rate = Instrument.control(
        "SOUR:VOLT:SLEW?", "SOUR:VOLT:SLEW %g",
        """This function control the output voltage slew rate.
         """,
        validator=truncated_range,
        values=[0.001, 10] # 62012P-600-8: 0.001V/ms - 10V/ms
    )

    def output_enable(self):
        self.write("CONF:OUTP ON")

    def output_disable(self):
        self.write("CONF:OUTP OFF")

    def ramp_to_current(self, current, steps=25, duration=0.5):
        """ Ramps the current to a value in Amps by traversing a linear spacing
        of current steps over a duration, defined in seconds.

        :param steps: A number of linear steps to traverse
        :param duration: A time in seconds over which to ramp
        """
        start_current = self.output_current
        stop_current = current
        pause = duration/steps
        if start_current != stop_current:
            currents = np.linspace(start_current, stop_current, steps)
            for current in currents:
                self.output_current_limit = current
                sleep(pause)

    def ramp_to_voltage(self, voltage, steps=25, duration=0.5):
        """ Ramps the voltage to a value in Volts by traversing a linear spacing
        of voltage steps over a duration, defined in seconds.

        :param steps: A number of linear steps to traverse
        :param duration: A time in seconds over which to ramp
        """
        start_voltage = self.output_voltage
        stop_voltage = voltage
        pause = duration/steps
        if start_voltage != stop_voltage:
            voltages = np.linspace(start_voltage, stop_voltage, steps)
            for voltage in voltages:
                self.output_voltage_level= voltage
                sleep(pause)

    def shutdown(self):
        """ Shuts down the instrument, and ramps the current or voltage to zero
        before disabling the source. """

        # Since voltage and current are set the same way, this
        # ramps either the current or voltage to zero
        self.ramp_to_current(0.0, steps=25)
        self.output_voltage_level = 0.0
        self.output_disable
        self.shutdown()