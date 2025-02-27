#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from time import sleep, time

import numpy as np

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class Keithley2510(SCPIMixin, Instrument):
    """Represents the Keithley 2510 TEC Sourcemeter and provides a high-level interface for
    interacting with the instrument.
    """

    def __init__(self, adapter, name="Keithley 2510 TEC SourceMeter", **kwargs):
        super().__init__(adapter, name, **kwargs)

    ###########
    # Control #
    ###########

    source_enabled = Instrument.control(
        "OUTPut?",
        "OUTPut %d",
        """Control whether the source is enabled (bool).
        The convenience methods :meth:`~.Keithley2510.enable_source`
        and :meth:`~.Keithley2510.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    temperature_setpoint = Instrument.control(
        ":SOURce:TEMPerature?",
        ":SOURce:TEMPerature %g",
        """Control the temperature setpoint, in degrees centigrade.
        Takes values from -50 to 225.""",
        validator=truncated_range,
        values=[-50, 225],
    )

    ################
    # Measurements #
    ################

    temperature = Instrument.measurement(
        ":MEASure:TEMPerature?",
        """Measure the temperature using the thermistor, in degrees centigrade.""",
    )

    current = Instrument.measurement(
        ":MEASure:CURRent?",
        """Measure the DC current through the thermoelectric cooler, in Amps.""",
    )

    voltage = Instrument.measurement(
        ":MEASure:VOLTage?",
        """Measure the DC voltage through the thermoelectric cooler, in Volts.""",
    )

    ##########################
    # Temperature Protection #
    ##########################

    temperature_protection_enabled = Instrument.control(
        ":SOURce:TEMPerature:PROTection:STATe?",
        ":SOURce:TEMPerature:PROTection:STATe %d",
        """Control whether temperature protection is enabled. Takes values True or False.
        The convenience methods :meth:`~.Keithley2510.enable_temperature_protection`
        and :meth:`~.Keithley2510.disable_temperature_protection` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    temperature_protection_low = Instrument.control(
        ":SOURce:TEMPerature:PROTection:LOW?",
        ":SOURce:TEMPerature:PROTection:LOW %g",
        """Control the lower temperature limit in degrees centigrade.
        Takes values from -50 to 250.""",
        validator=truncated_range,
        values=[-50, 250],
    )

    temperature_protection_high = Instrument.control(
        ":SOURce:TEMPerature:PROTection:HIGH?",
        ":SOURce:TEMPerature:PROTection:HIGH %g",
        """Control the upper temperature limit in degrees centigrade.
        Takes values from -50 to 250.""",
        validator=truncated_range,
        values=[-50, 250],
    )

    @property
    def temperature_protection_range(self):
        """Control the lower and upper temperature limits in degrees centigrade.
        Two-tuple of floats (lower_limit, upper_limit) which can take values from -50 to 250."""
        return (self.temperature_protection_low, self.temperature_protection_high)

    @temperature_protection_range.setter
    def temperature_protection_range(self, temp_range):
        self.temperature_protection_low = temp_range[0]
        self.temperature_protection_high = temp_range[1]

    ###########
    # Methods #
    ###########

    def enable_source(self):
        """Enables the source."""
        self.write("OUTPUT ON")

    def disable_source(self):
        """Disables the source."""
        self.write("OUTPUT OFF")

    def enable_temperature_protection(self):
        """Enable temperature protection."""
        self.write(":SOURce:TEMPerature:PROTection:STATe ON")

    def disable_temperature_protection(self):
        """Disable temperature protection."""
        self.write(":SOURce:TEMPerature:PROTection:STATe OFF")

    def is_temperature_stable(self, tolerance=0.1, period=10, points=64):
        """Determine whether the temperature is stable at the temperature setpoint over a specified
        period.

        :param tolerance: Maximum allowed deviation from temperature setpoint,
            in degrees Centigrade.
        :param period: Time period over which stability is checked, in seconds.
        :param points: Number of points to collect within the period.
        :return: True if stable, False otherwise.
        """

        delay = period / points

        temp_array = []

        for i in range(points):
            temp_array.append(self.temperature)
            sleep(delay)

        return np.all(abs(temp_array - self.temperature_setpoint) < tolerance)

    def wait_for_temperature_stable(
        self,
        tolerance=0.1,
        period=10,
        points=64,
        should_stop=lambda: False,
        timeout=60,
    ):
        """Block the program, waiting for the temperature to stabilize at the temperature setpoint.

        :param tolerance: Maximum allowed deviation from temperature setpoint,
            in degrees Centigrade.
        :param period: Time period over which stability is checked, in seconds.
        :param points: Number of points to collect within the period.
        :param should_stop: Function that returns True to stop waiting.
        :param timeout: Maximum waiting time, in seconds.
        """

        delay = period / points

        temp_array = np.full(points, np.inf)

        count = 0
        t_start = time()

        while time() - t_start < timeout:

            temp_array[count % points] = self.temperature

            if np.all(abs(temp_array - self.temperature_setpoint) < tolerance):
                return True

            if should_stop():
                return False

            sleep(delay)
            count += 1

        raise TimeoutError("Timed out waiting for temperature to stabilize.")
