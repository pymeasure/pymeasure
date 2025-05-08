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

import logging

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

from .buffer import KeithleyBuffer


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2182Channel(Channel):
    """Implementation of a Keithley 2182 channel.

    Channel 1 is the fundamental measurement channel, while channel 2 provides
    sense measurements. Channel 2 inputs are referenced to Channel 1 LO.
    Possible configurations are

    Voltage     (Channel 1)
    Temperature (Channel 1)
    Voltage     (Channel 1) and Voltage     (Channel 2)
    Voltage     (Channel 1) and Temperature (Channel 2)
    """

    def __init__(self, parent, id):
        """Set max voltage depending on channel."""
        if id == 1:
            self.voltage_range_values = (0, 120)
            self.voltage_offset_values = (-120, 120)
        else:
            self.voltage_range_values = (0, 12)
            self.voltage_offset_values = (-12, 12)
        super().__init__(parent, id)

    voltage_range = Channel.control(
        ":SENS:VOLT:CHAN{ch}:RANG?", ":SENS:VOLT:CHAN{ch}:RANG %g",
        """Control the positive full-scale measurement voltage range in Volts.
        The Keithley 2182 selects a measurement range based on the expected voltage.
        DCV1 has five ranges: 10 mV, 100 mV, 1 V, 10 V, and 100 V.
        DCV2 has three ranges: 100 mV, 1 V, and 10 V.
        Valid limits are from 0 to 120 V for Ch. 1, and 0 to 12 V for Ch. 2.
        Auto-range is automatically disabled when this property is set.""",
        validator=strict_range,
        values=(0, 120),
        dynamic=True,
    )

    voltage_range_auto_enabled = Channel.control(
        ":SENS:VOLT:CHAN{ch}:RANG:AUTO?", ":SENS:VOLT:CHAN{ch}:RANG:AUTO %d",
        """Control the auto voltage ranging option (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage_offset = Channel.control(
        ":SENS:VOLT:CHAN{ch}:REF?", ":SENS:VOLT:CHAN{ch}:REF %g",
        """Control the relative offset for measuring voltage.
        Displayed value = actual value - offset value.
        Valid ranges are -120 V to +120 V for Ch. 1, and -12 V to +12 V for Ch. 2.""",
        validator=strict_range,
        values=(-120, 120),
        dynamic=True,
    )

    temperature_offset = Channel.control(
        ":SENS:TEMP:CHAN{ch}:REF?", ":SENS:TEMP:CHAN{ch}:REF %g",
        """Control the relative offset for measuring temperature.
        Displayed value = actual value - offset value.
        Valid values are -273 C to 1800 C.""",
        validator=strict_range,
        values=(-273, 1800),
    )

    voltage_offset_enabled = Channel.control(
        ":SENS:VOLT:CHAN{ch}:REF:STAT?", ":SENS:VOLT:CHAN{ch}:REF:STAT %s",
        """Control whether voltage is measured as a relative or absolute value (bool).
        Enabled by default for Ch. 2 voltage, which is measured relative to Ch. 1
        voltage.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    temperature_offset_enabled = Channel.control(
        ":SENS:TEMP:CHAN{ch}:REF:STAT?", ":SENS:TEMP:CHAN{ch}:REF:STAT %s",
        """Control whether temperature is measured as a relative or absolute value (bool).
        Disabled by default.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    def setup_voltage(self, auto_range=True, nplc=5):
        """Set active channel and configure channel for voltage measurement.

        :param auto_range: Enables auto_range if True, else uses set voltage
            range
        :param nplc: Number of power line cycles (NPLC) from 0.01 to 50/60
        """
        self.write(":SENS:CHAN {ch};"
                   ":SENS:FUNC 'VOLT';"
                   f":SENS:VOLT:NPLC {nplc};")
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO 1")
        self.check_errors()

    def setup_temperature(self, nplc=5):
        """Change active channel and configure channel for temperature measurement.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 50/60
        """
        self.write(":SENS:CHAN {ch};"
                   ":SENS:FUNC 'TEMP';"
                   f":SENS:TEMP:NPLC {nplc}")
        self.check_errors()

    def acquire_temperature_reference(self):
        """Acquire a temperature measurement and store it as the relative offset value.

        Only acquires reference if temperature offset is enabled.
        """
        self.write(":SENS:TEMP:CHAN{ch}:REF:ACQ")

    def acquire_voltage_reference(self):
        """Acquire a voltage measurement and store it as the relative offset value.

        Only acquires reference if voltage offset is enabled.
        """
        self.write(":SENS:VOLT:CHAN{ch}:REF:ACQ")


class Keithley2182(SCPIMixin, KeithleyBuffer, Instrument):
    """Represents the Keithley 2182 Nanovoltmeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2182("GPIB::1")

        keithley.reset()                        # Return instrument settings to default
                                                  values
        keithley.thermocouple = 'S'             # Sets thermocouple type to S
        keithley.active_channel = 1             # Sets channel 1 for active measurement
        keithley.channel_function = 'voltage'   # Configures active channel for voltage
                                                  measurement
        print(keithley.voltage)                 # Prints the voltage in volts

        keithley.ch_1.setup_voltage()           # Set channel 1 active and prepare
                                                  voltage measurement
        keithley.ch_2.setup_temperature()       # Set channel 2 active and prepare
                                                  temperature measurement

    """

    def __init__(self, adapter, name="Keithley 2182 Nanovoltmeter",
                 read_termination='\r', **kwargs):
        super().__init__(adapter, name, read_termination=read_termination, **kwargs)

    ch_1 = Instrument.ChannelCreator(Keithley2182Channel, 1)
    ch_2 = Instrument.ChannelCreator(Keithley2182Channel, 2)

    #################
    # Configuration #
    #################

    auto_zero_enabled = Instrument.control(
        ":SYST:AZER:STAT?", ":SYST:AZER:STAT %d",
        """Control the auto zero option (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    line_frequency = Instrument.measurement(
        ":SYST:LFR?",
        """Get the line frequency in Hertz. Values are 50 or 60.
        Cannot be set on 2182.""",
    )

    display_enabled = Instrument.control(
        ":DISP:ENAB?", ":DISP:ENAB %d",
        """Control whether the front display of the voltmeter is enabled.
        Valid values are True and False.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    active_channel = Instrument.control(
        ":SENS:CHAN?", ":SENS:CHAN %d",
        """Control which channel is active for measurement.
        Valid values are 0 (internal temperature sensor), 1, and 2.""",
        validator=strict_discrete_set,
        values=(0, 1, 2),
        cast=int
    )

    channel_function = Instrument.control(
        ":SENS:FUNC?", "SENS:FUNC %s",
        """Control the measurement mode of the active channel.
        Valid options are `voltage` and `temperature`.""",
        validator=strict_discrete_set,
        values={'voltage': '"VOLT:DC"', 'temperature': '"TEMP"'},
        map_values=True
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """Measure the voltage in Volts, if active channel is configured for this
        reading."""
    )

    voltage_nplc = Instrument.control(
        ":SENS:VOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """Control the number of power line cycles (NPLC) for voltage measurements,
        which sets the integration period and measurement speed.
        Valid values are from 0.01 to 50 or 60, depending on the line frequency.
        Default is 5.""",
        validator=strict_range,
        values=(0.01, 60),
        dynamic=True,
    )

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(
        ":READ?",
        """Measure the temperature in Celsius, if active channel is configured for this
        reading."""
    )

    thermocouple = Instrument.control(
        ":SENS:TEMP:TC?", ":SENS:TEMP:TC %s",
        """Control the thermocouple type for temperature measurements.
        Valid options are B, E, J, K, N, R, S, and T.""",
        validator=strict_discrete_set,
        values=('B', 'E', 'J', 'K', 'N', 'R', 'S', 'T')
    )

    temperature_nplc = Instrument.control(
        ":SENS:TEMP:NPLC?", ":SENS:TEMP:NPLC %g",
        """Control the number of power line cycles (NPLC) for temperature measurements,
        which sets the integration period and measurement speed.
        Valid values are from 0.01 to 50 or 60, depending on the line frequency.
        Default is 5.""",
        validator=strict_range,
        values=(0.01, 60),
        dynamic=True,
    )

    temperature_reference_junction = Instrument.control(
        ":SENS:TEMP:RJUN:RSEL?", ":SENS:TEMP:RJUN:RSEL %s",
        """Control whether the thermocouple reference junction is internal (INT) or
        simulated (SIM). Default is INT.""",
        validator=strict_discrete_set,
        values=('SIM', 'INT'),
    )

    temperature_simulated_reference = Instrument.control(
        ":SENS:TEMP:RJUN:SIM?", ":SENS:TEMP:RJUN:SIM %g",
        """Control the value of the simulated thermocouple reference junction in
        Celsius. Default is 23 C.""",
        validator=strict_range,
        values=(0, 60),
    )

    internal_temperature = Instrument.measurement(
        ":SENS:TEMP:RTEM?",
        """Measure the internal temperature in Celsius."""
    )

    ##############
    # Statistics #
    ##############

    mean = Instrument.measurement(
        ":CALC2:FORM MEAN;:CALC2:STAT ON;:CALC2:IMM?;",
        """Get the calculated mean (average) from the buffer data."""
    )

    maximum = Instrument.measurement(
        ":CALC2:FORM MAX;:CALC2:STAT ON;:CALC2:IMM?;",
        """Get the calculated maximum from the buffer data."""
    )

    minimum = Instrument.measurement(
        ":CALC2:FORM MIN;:CALC2:STAT ON;:CALC2:IMM?;",
        """Get the calculated minimum from the buffer data."""
    )

    standard_dev = Instrument.measurement(
        ":CALC2:FORM SDEV;:CALC2:STAT ON;:CALC2:IMM?;",
        """Get the calculated standard deviation from the buffer data."""
    )

    ###########
    # Trigger #
    ###########

    trigger_count = Instrument.control(
        ":TRIG:COUN?", ":TRIG:COUN %d",
        """Control the trigger count which can take values from 1 to 9,999.
        Default is 1.""",
        validator=strict_range,
        values=(1, 9999),
        cast=int
    )

    trigger_delay = Instrument.control(
        ":TRIG:DEL?", ":TRIG:DEL %g",
        """Control the trigger delay in seconds, which can take values from 0 to
        999999.999 s. Default is 0.""",
        validator=strict_range,
        values=(0, 999999.999)
    )

    ###########
    # Methods #
    ###########

    def auto_line_frequency(self):
        """Set appropriate limits for NPLC voltage and temperature readings."""
        if self.line_frequency == 50:
            self.temperature_nplc_values = (0.01, 50)
            self.voltage_nplc_values = (0.01, 50)
        else:
            self.temperature_nplc_values = (0.01, 60)
            self.voltage_nplc_values = (0.01, 60)

    def reset(self):
        """Reset the instrument and clear the queue."""
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def trigger(self):
        """Execute a bus trigger, which can be used when :meth:`~.trigger_on_bus`
        is configured.
        """
        return self.write("*TRG")

    def trigger_immediately(self):
        """Configure measurements to be taken with the internal trigger at the maximum
        sampling rate.
        """
        self.write(":TRIG:SOUR IMM;")

    def trigger_on_bus(self):
        """Configure the trigger to detect events based on the bus trigger, which can be
        activated by :meth:`~.trigger`.
        """
        self.write(":TRIG:SOUR BUS")

    def sample_continuously(self):
        """Configure the instrument to continuously read samples
        and turn off any buffer or output triggering.
        """
        self.disable_buffer()
        self.trigger_immediately()
