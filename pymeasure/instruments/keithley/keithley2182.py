#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
import time

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2182(KeithleyBuffer, Instrument):
    """ Represents the Keithley 2182 Nanovoltmeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2182("GPIB::1")

        keithley.reset()                        # Return instrument settings to default values
        keithley.thermocouple = 'S'             # Sets thermocouple type to S
        keithley.active_channel = 1             # Sets channel 1 for active measurement
        keithley.channel_function = 'voltage'   # Configures active channel for voltage measurement
        print(keithley.voltage)                 # Prints the voltage in volts
        
        keithley.measure_voltage(1)             # Measure voltage on channel 1
        keithley.measure_temp(2)                # Measure temperature on channel 2

    """

    #################
    # Configuration #
    #################

    auto_zero = Instrument.control(
        ":SYST:AZER:STAT?", ":SYST:AZER:STAT %s",
        """ A property that controls the auto zero option. Valid values are
        True (enabled) and False (disabled). """,
        values={True: 1, False: 0},
        map_values=True,
    )
    line_frequency = Instrument.measurement(
        ":SYST:LFR?",
        """ Reads the line frequency in Hertz. Values are 50 or 60.
        Cannot be set on 2182. """,
    )
    display_enabled = Instrument.control(
        ":DISP:ENAB?", ":DISP:ENAB %d",
        """ A boolean property that controls whether or not the display of the
        voltmeter is enabled. Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )
    active_channel = Instrument.control(
        ":SENS:CHAN?", ":SENS:CHAN %d",
        """ An integer property that controls selected measurement channel.
        Valid values are 0 (internal temperature sensor), 1, and 2. """,
        validator=strict_discrete_set,
        values=[0, 1, 2],
        cast=int
    )
    channel_function = Instrument.control(
        ":SENS:FUNC?", "SENS:FUNC %s",
        """ A property that controls the measurement mode of the active channel.
        Valid options are voltage and temperature. """,
        validator=strict_discrete_set,
        values={'voltage': 'VOLT', 'temperature': 'TEMP'},
        map_values=True
        )
    

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """ Reads the voltage in Volts, if configured for this reading.
        """
    )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG %g",
        """ A floating point property that controls the positive full-scale 
        measurement voltage range in Volts, which can take values from 0 to
        120 V (Ch. 1) or 12 V (Ch. 2). Auto-range is disabled when this
        property is set. """,
        validator=truncated_range,
        values=[0, 120]
    )
    voltage_nplc = Instrument.control(
        ":SENS:VOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """ A floating point property that controls the number of power line
        cycles (NPLC) for voltage measurements, which sets the integration
        period and measurement speed. Takes values from 0.01 to 50 or 60, where
        0.1, 1, and 10 are Fast, Medium, and Slow respectively. """,
        validator=truncated_range,
        values=[0.01, 60]
    )

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(
        ":READ?",
        """ Reads the temperature in Celsius, if configured for this reading. """
    )
    thermocouple = Instrument.control(
        ":SENS:TEMP:TC?", ":SENSE:TEMP:TC %s",
        """A property that controls the thermocouple type for temperature
        measurements. Valid options are B, E, J, K, N, R, S, or T. """,
        validator=strict_discrete_set,
        values=['B','E','J','K','N','R','S','T']
        )
    temperature_reference = Instrument.control(
        ":SENS:TEMP:REF?", ":SENS:TEMP:REF %g",
        """ A floating point property that controls the relative temperature 
        offset value in Celsius, which can take values from -273 to 1800 C. """,
        validator=truncated_range,
        values=[-273, 1800]
    )
    temperature_nplc = Instrument.control(
        ":SENS:TEMP:NPLC?", ":SENS:TEMP:NPLC %g",
        """ A floating point property that controls the number of power line
        cycles (NPLC) for temperature measurements, which sets the integration
        period and measurement speed. Takes values from 0.01 to 50 or 60, where
        0.1, 1, and 10 are Fast, Medium, and Slow respectively. """,
        validator=truncated_range,
        values=[0.01, 60]
    )

    ##############
    # Statistics #
    ##############

    buffer_points = Instrument.control(
        ":TRAC:POIN?", ":TRAC:POIN %d",
        """ An integer property that controls the number of buffer points. This
        does not represent actual points in the buffer, but the configuration
        value instead. """,
        validator=truncated_range,
        values=[2, 1024],
        cast=int
    )
    mean = Instrument.measurement(
        ":CALC2:FORM MEAN;:CALC2:STAT ON;:CALC2:IMM?;",
        """ Returns the calculated mean (average) from the buffer data. """
    )
    maximum = Instrument.measurement(
        ":CALC2:FORM MAX;:CALC2:STAT ON;:CALC2:IMM?;",
        """ Returns the calculated maximum from the buffer data. """
    )
    minimum = Instrument.measurement(
        ":CALC2:FORM MIN;:CALC2:STAT ON;:CALC2:IMM?;",
        """ Returns the calculated minimum from the buffer data. """
    )
    standard_dev = Instrument.measurement(
        ":CALC2:FORM SDEV;:CALC2:STAT ON;:CALC2:IMM?;",
        """ Returns the calculated standard deviation from the buffer data. """
    )

    ###########
    # Trigger #
    ###########

    trigger_count = Instrument.control(
        ":TRIG:COUN?", ":TRIG:COUN %d",
        """ An integer property that controls the trigger count,
        which can take values from 1 to 9,999. """,
        validator=truncated_range,
        values=[1, 9999],
        cast=int
    )
    trigger_delay = Instrument.control(
        ":TRIG:SEQ:DEL?", ":TRIG:SEQ:DEL %g",
        """ A floating point property that controls the trigger delay
        in seconds, which can take values from 0 to 999999.999 s. """,
        validator=truncated_range,
        values=[0, 999999.999]
    )

    ###########
    # Methods #
    ###########

    def __init__(self, adapter, name="Keithley 2182 Nanovoltmeter", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    def measure_voltage(self, channel=1, nplc=1, voltage=120.0, auto_range=True):
        """ Configures and acquires voltage measurement.
        
        :param channel: Voltage measurement channel
        :param nplc: Number of power line cycles (NPLC) from 0.01 to 60
        :param voltage: Upper limit of measurement range in Volts, from 0 to 120 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        log.info("%s is measuring voltage." % self.name)
        self.write(":SENS:CHAN %d;"
                   ":SENS:FUNC 'VOLT';"
                   ":SENS:VOLT:NPLC %f;" % (channel, nplc))
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO 1;")
        else:
            self.voltage_range = voltage
        self.check_errors()

    def measure_temperature(self, channel=2, nplc=1, TC='S'):
        """ Configures and acquires temperature measurement.

        :param channel: Temperature measurement channel
        :param nplc: Number of power line cycles (NPLC) from 0.01 to 50/60
        :param TC: Thermocouple type
        """
        log.info("%s is measuring temperature." % self.name)
        self.write(":SENS:FUNC 'TEMP';"
                   ":SENS:CURR:NPLC %f;:FORM:ELEM CURR;" % nplc)

        self.check_errors()

    def auto_range_source(self):
        """ Configures the source to use an automatic range.
        """
        if self.source_mode == 'current':
            self.write(":SOUR:CURR:RANG:AUTO 1")
        else:
            self.write(":SOUR:VOLT:RANG:AUTO 1")

    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)

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
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def trigger(self):
        """ Executes a bus trigger, which can be used when
        :meth:`~.trigger_on_bus` is configured.
        """
        return self.write("*TRG")

    def trigger_immediately(self):
        """ Configures measurements to be taken with the internal
        trigger at the maximum sampling rate.
        """
        self.write(":ARM:SOUR IMM;:TRIG:SOUR IMM;")

    def trigger_on_bus(self):
        """ Configures the trigger to detect events based on the bus
        trigger, which can be activated by :meth:`~.trigger`.
        """
        self.write(":ARM:COUN 1;:ARM:SOUR BUS;:TRIG:SOUR BUS;")

    def set_trigger_counts(self, arm, trigger):
        """ Sets the number of counts for both the sweeps (arm) and the
        points in those sweeps (trigger), where the total number of
        points can not exceed 2500
        """
        if arm * trigger > 2500 or arm * trigger < 0:
            raise RangeException("Keithley 2400 has a combined maximum "
                                 "of 2500 counts")
        if arm < trigger:
            self.write(":ARM:COUN %d;:TRIG:COUN %d" % (arm, trigger))
        else:
            self.write(":TRIG:COUN %d;:ARM:COUN %d" % (trigger, arm))

    def sample_continuously(self):
        """ Causes the instrument to continuously read samples
        and turns off any buffer or output triggering
        """
        self.disable_buffer()
        self.disable_output_trigger()
        self.trigger_immediately()

    def set_timed_arm(self, interval):
        """ Sets up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points
        """
        if interval > 99999.99 or interval < 0.001:
            raise RangeException("Keithley 2400 can only be time"
                                 " triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)

    def trigger_on_external(self, line=1):
        """ Configures the measurement trigger to be taken from a
        specific line of an external trigger

        :param line: A trigger line from 1 to 4
        """
        cmd = ":ARM:SOUR TLIN;:TRIG:SOUR TLIN;"
        cmd += ":ARM:ILIN %d;:TRIG:ILIN %d;" % (line, line)
        self.write(cmd)

    def output_trigger_on_external(self, line=1, after='DEL'):
        """ Configures the output trigger on the specified trigger link
        line number, with the option of supplying the part of the
        measurement after which the trigger should be generated
        (default to delay, which is right before the measurement)

        :param line: A trigger line from 1 to 4
        :param after: An event string that determines when to trigger
        """
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    def disable_output_trigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")

    def status(self):
        return self.ask("status:queue?;")
