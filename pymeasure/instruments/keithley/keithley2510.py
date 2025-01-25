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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
from pymeasure.instruments.keithley.buffer import KeithleyBuffer


class Keithley2510(KeithleyBuffer, SCPIMixin, Instrument):
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
        """A boolean property that controls whether the source is enabled, takes values True or
        False. The convenience methods :meth:`~.Keithley2510.enable_source` and
        :meth:`~.Keithley2510.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    temperature_setpoint = Instrument.control(
        ":SOURce:TEMPerature?",
        ":SOURce:TEMPerature %g",
        """A floating point property that controls the temperature setpoint in degrees centigrade,
        which can take values from -50 to 225.""",
        validator=truncated_range,
        values=[-50, 225],
    )

    ################
    # Measurements #
    ################

    temperature = Instrument.measurement(
        ":MEASure:TEMPerature?",
        """Query the temperature measured using the thermistor, in degrees centigrade.""",
    )

    current = Instrument.measurement(
        ":MEASure:CURRent?",
        """Query the DC current through the thermoelectric cooler, in Amps.""",
    )

    voltage = Instrument.measurement(
        ":MEASure:VOLTage?",
        """Query the DC voltage through the thermoelectric cooler, in Volts.""",
    )

    ##########################
    # Temperature Protection #
    ##########################

    temperature_protection_enabled = Instrument.control(
        ":SOURce:TEMPerature:PROTection:STATe?",
        ":SOURce:TEMPerature:PROTection:STATe %d",
        """A boolean property that controls whether temperature protection is enabled. The 
        convenience methods :meth:`~.Keithley2510.enable_temperature_protection` and
        :meth:`~.Keithley2510.disable_temperature_protection` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    temperature_protection_low = Instrument.control(
        ":SOURce:TEMPerature:PROTection:LOW?",
        ":SOURce:TEMPerature:PROTection:LOW %g",
        """A floating point property that controls the lower temperature limit in degrees
        centigrade, which can take values from -50 to 250.""",
        validator=truncated_range,
        values=[-50, 250],
    )

    temperature_protection_high = Instrument.control(
        ":SOURce:TEMPerature:PROTection:HIGH?",
        ":SOURce:TEMPerature:PROTection:HIGH %g",
        """A floating point property that controls the upper temperature limit in degrees
        centigrade, which can take values from -50 to 250.""",
        validator=truncated_range,
        values=[-50, 250],
    )

    @property
    def temperature_protection_range(self):
        """A double tuple property that controls the lower and upper temperature limits in degrees
        centigrade, which can take values from -50 to 250."""
        return (self.temperature_protection_low(), self.temperature_protection_high())

    @temperature_protection_range.setter
    def temperature_protection_range_setter(self, temp_range):
        self.temperature_protection_low = temp_range[0]
        self.temperature_protection_high = temp_range[1]

    #######################
    # Buffer calculations #
    #######################

    means = Instrument.measurement(
        ":CALC3:FORM MEAN;:CALC3:DATA?;",
        """ Reads the calculated means (averages) for voltage,
        current, and resistance from the buffer data  as a list. """,
    )
    maximums = Instrument.measurement(
        ":CALC3:FORM MAX;:CALC3:DATA?;",
        """ Returns the calculated maximums for voltage, current, and
        resistance from the buffer data as a list. """,
    )
    minimums = Instrument.measurement(
        ":CALC3:FORM MIN;:CALC3:DATA?;",
        """ Returns the calculated minimums for voltage, current, and
        resistance from the buffer data as a list. """,
    )
    standard_devs = Instrument.measurement(
        ":CALC3:FORM SDEV;:CALC3:DATA?;",
        """ Returns the calculated standard deviations for voltage,
        current, and resistance from the buffer data as a list. """,
    )

    @property
    def mean_temperature(self):
        """Returns the mean temperature from the buffer"""
        return self.means[0]

    @property
    def max_temperature(self):
        """Returns the maximum temperature from the buffer"""
        return self.maximums[0]

    @property
    def min_temperature(self):
        """Returns the minimum temperature from the buffer"""
        return self.minimums[0]

    @property
    def std_temperature(self):
        """Returns the temperature standard deviation from the buffer"""
        return self.standard_devs[0]

    @property
    def mean_voltage(self):
        """Returns the mean voltage from the buffer"""
        return self.means[1]

    @property
    def max_voltage(self):
        """Returns the maximum voltage from the buffer"""
        return self.maximums[1]

    @property
    def min_voltage(self):
        """Returns the minimum voltage from the buffer"""
        return self.minimums[1]

    @property
    def std_voltage(self):
        """Returns the voltage standard deviation from the buffer"""
        return self.standard_devs[1]

    @property
    def mean_current(self):
        """Returns the mean current from the buffer"""
        return self.means[2]

    @property
    def max_current(self):
        """Returns the maximum current from the buffer"""
        return self.maximums[2]

    @property
    def min_current(self):
        """Returns the minimum current from the buffer"""
        return self.minimums[2]

    @property
    def std_current(self):
        """Returns the current standard deviation from the buffer"""
        return self.standard_devs[2]

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
        """Determines whether the temperature is stable to within :code:``tolerance`` degrees
        centigrade over :code:``period`` seconds using the Keithley's internal buffer."""

        delay = period / points
        if self.trigger_delay != delay or self.buffer_points != points:
            self.stop_buffer()
            self.reset_buffer()
        self.config_buffer(points=points, delay=delay)  #
        self.start_buffer()

        self.wait_for_buffer()

        if self.max_temperature - self.min_temperature > tolerance:
            return False
        else:
            return True

    def wait_for_temperature_stable(
        self,
        tolerance=0.1,
        period=10,
        points=64,
        should_stop=lambda: False,
        timeout=60,
        interval=0.1,
    ):
        """Blocks the program, waiting for the temperature to be stable. This function
        returns early if the :code:`should_stop` function returns True or the timeout is reached
        before the temperature is stable.
        """

        t = time()
        delay = period / points
        while not self.is_temperature_stable():
            sleep(delay)
            if should_stop():
                return
            if (time() - t) > timeout:
                raise Exception("Timed out waiting for temperature to stabilize.")


# Example usage
if __name__ == "__main__":
    tec_gpib_address = "GPIB:10"
    tec = Keithley2510(tec_gpib_address)

    tec.temperature_protection_range = (0, 70)
    tec.enable_temperature_protection()
    tec.temperature_setpoint = 55
    tec.enable_source()

    tec.wait_for_temperature_stable()

    print("Temperature stable!")
