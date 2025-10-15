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

from time import time

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class Keithley2510(SCPIMixin, Instrument):
    """Represents the Keithley 2510 TEC Sourcemeter and provides a high-level interface for
    interacting with the instrument.
    """

    def __init__(self, adapter, name="Keithley 2510 TEC SourceMeter", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # === Control ===

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
        """Control the temperature setpoint, in degrees centigrade
        (float strictly from -50 to 225)""",
        validator=strict_range,
        values=[-50, 225],
    )

    # === Measurements ===

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

    # === Temperature protection ===

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
        """Control the lower temperature limit in degrees centigrade
        (float strictly from -50 to 225)""",
        validator=strict_range,
        values=[-50, 250],
    )

    temperature_protection_high = Instrument.control(
        ":SOURce:TEMPerature:PROTection:HIGH?",
        ":SOURce:TEMPerature:PROTection:HIGH %g",
        """Control the upper temperature limit in degrees centigrade
        (float strictly from -50 to 225)""",
        validator=strict_range,
        values=[-50, 250],
    )

    @property
    def temperature_protection_range(self):
        """Control the lower and upper temperature limits in degrees centigrade through the tuple
        (lower_limit, upper_limit)."""
        return (self.temperature_protection_low, self.temperature_protection_high)

    @temperature_protection_range.setter
    def temperature_protection_range(self, temp_range):
        self.temperature_protection_low, self.temperature_protection_high = temp_range

    # === PID Control ===

    temperature_pid_p = Instrument.control(
        ":SOURce:TEMPerature:LCONstants:GAIN?",
        ":SOURce:TEMPerature:LCONstants:GAIN %g",
        """Control the proportional constant of the temperature PID loop.""",
        validator=strict_range,
        values=[0, 1e5],
    )

    temperature_pid_i = Instrument.control(
        ":SOURce:TEMPerature:LCONstants:INTegral?",
        ":SOURce:TEMPerature:LCONstants:INTegral %g",
        """Control the integral constant of the temperature PID loop.""",
        validator=strict_range,
        values=[0, 1e5],
    )

    temperature_pid_d = Instrument.control(
        ":SOURce:TEMPerature:LCONstants:DERivative?",
        ":SOURce:TEMPerature:LCONstants:DERivative %g",
        """Control the derivative constant of the temperature PID loop.""",
        validator=strict_range,
        values=[0, 1e5],
    )

    @property
    def temperature_pid(self):
        """Control the temperature PID loop constants through the tuple
        (proportional_const, integral_const, derivative_const)."""
        return (self.temperature_pid_p, self.temperature_pid_i, self.temperature_pid_d)

    @temperature_pid.setter
    def temperature_pid(self, pid_consts):
        self.temperature_pid_p, self.temperature_pid_i, self.temperature_pid_d = pid_consts

    # === Methods ===

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

    def check_temperature_stability(self, tolerance=0.1, period=10, points=64):
        """Determine whether the temperature is stable at the temperature setpoint over a specified
        period.

        :param tolerance: Maximum allowed deviation from temperature setpoint,
            in degrees Centigrade.
        :param period: Time period over which stability is checked, in seconds.
        :return: True if stable, False otherwise.
        """

        t_start = time()

        while time() - t_start < period:
            if abs(self.temperature - self.temperature_setpoint) > tolerance:
                return False

        return True

    def wait_for_temperature_stable(
        self,
        tolerance=0.1,
        period=10,
        should_stop=lambda: False,
        timeout=60,
    ):
        """Block the program, waiting for the temperature to stabilize at the temperature setpoint.

        :param tolerance: Maximum allowed deviation from temperature setpoint,
            in degrees Centigrade.
        :param period: Time period over which stability is checked, in seconds.
        :param should_stop: Function that returns True to stop waiting.
        :param timeout: Maximum waiting time, in seconds.
        :return: True when stable, False if stopped by should_stop.
        :raises TimeoutError: If the temperature does not stabilize within the timeout period.
        """

        t_start_timeout = time()
        t_start_period = time()

        while time() - t_start_timeout < timeout:

            if abs(self.temperature - self.temperature_setpoint) > tolerance:
                t_start_period = time()

            if time() - t_start_period >= period:
                return True

            if should_stop():
                return False

        raise TimeoutError("Timed out waiting for temperature to stabilize.")
