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

# from pymeasure.instruments import Instrument

import logging
import time

import numpy as np

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Keithley6487(Instrument, KeithleyBuffer):
    """Represents the Keithley 6487 Picoammeter and provides a 
    high-level interface for interactin gwith the instrument
    
    .. code-block:: python
        
        keithley = Keithley6487("GPIB::1")
        
        keithley.apply_voltage()                # Sets up a source voltage
        keithley.source_voltage_range = 10e-3   # Sets the voltage range
        to 10 mV
        keithley.compliance_voltage = 10        # Sets the compliance voltage
        to 10 V
        keithley.enable_source()                # Enables the source output

        keithley.measure_current()              # Sets up to measure current

        keithley.ramp_to_voltage(1)             # Ramps voltage to 1 V

        keithley.shutdown()                     # Ramps the voltage to 0 V and
        disables output
        """
    
    auto_zero = Instrument.control(
        ":SYST:AZER:STAT?", ":SYST:AZER:STAT %s",
        """ A property that controls the auto zero option. Valid values are
        True (enabled) and False (disabled) and 'ONCE' (force immediate). """,
        values={True: 1, False: 0, "ONCE": "ONCE"},
        map_values=True,
    )

    line_frequency = Instrument.control(
        ":SYST:LFR?", ":SYST:LFR %d",
        """ An integer property that controls the line frequency in Hertz.
        Valid values are 50 and 60. """,
        validator=strict_discrete_set,
        values=[50, 60],
        cast=int,
    )

    line_frequency_auto = Instrument.control(
        ":SYST:LFR:AUTO?", ":SYST:LFR:AUTO %d",
        """ A boolean property that enables or disables auto line frequency.
        Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )
    
    #####################
    #   Voltage (V)     #
    #####################
    source_enabled = Instrument.control(
        ":SOUR:VOLT:STAT?", ":SOUR:VOLT:STAT %d",
        """A string property that controls whether the voltage source is
        enabled, takes values OFF or ON. The convenience methods :meth:
        `~.Keithley6487.enable_source` and
        :meth:`~Keithley6487.disable_source` can also be used""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    auto_output_off = Instrument.control(
        ":SOUR:CLE:AUTO?", ":SOUR:CLE:AUTO %d",
        """ A boolean property that enables or disables the auto output-off.
        Valid values are True (output off after measurement) and False (output
        stays on after measurement). """,
        values={True: 1, False: 0},
        map_values=True,
    )
    
    source_delay = Instrument.control(
        ":SOUR:VOLT:DEL?", ":SOUR:VOLT:DEL %f",
        """ A floating point property that sets a manual delay for the source
        after the output is turned on before a measurement is taken. When this
        property is set, the auto delay is turned off. Valid values are
        between 0 [seconds] and 999.9999 [seconds].""",
        validator=truncated_range,
        values=[0, 999.9999],
    )

    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT:LEV %f",
        """ A floating point property that controls the source voltage
        in Volts. """
    )

    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %f",
        """ A floating point property that controls the source voltage
        range in Volts, which can take values of 10, 50, or 500V.
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10, 50, 500]
    )

    #####################
    #   Current (A)     #
    #####################

    current = Instrument.measurement(
        ":MEAS?",
        """ Reads the current in Amps.
        """
    )

    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0; :SEND:CURR:RANG %f",
        """A floating point property that controls the measurement the current
        range in Amps, which can take values between -0.021 and +0.021 A.
        Auto-range is disabled when this property is set""",
        validator=truncated_range,
        values=[-0.021, 0.021]
    )

    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %f",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.001 to 6.0 or 5.0, where 6.0
        is 60Hz and 5.0 is 50Hz"""
    )

    ###########
    # Trigger #
    ###########

    trigger_count = Instrument.control(
        ":TRIG:COUN?", ":TRIG:COUN %d",
        """ An integer property that controls the trigger count,
        which can take values from 1 to 2048. """,
        validator=truncated_range,
        values=[1, 2048],
        cast=int
    )

    trigger_count_inf = Instrument.control(
        ":TRIG:COUNT?", "TRIG:COUNT %s",
        """A string that controls the trigger count,
        sets trigger count to INF mode instead of an integer""",
        validator=strict_discrete_set,
        values=['INF'],
        cast=str
    )

    trigger_delay = Instrument.control(
        ":TRIG:SEQ:DEL?", ":TRIG:SEQ:DEL %f",
        """ A floating point property that controls the trigger delay
        in seconds, which can take values from 0 to 999.9999 s. """,
        validator=truncated_range,
        values=[0, 999.9999]
    )

    ###########
    # Filters #
    ###########

    filter_type = Instrument.control(
        ":SENS:AVER:TCON?", ":SENS:AVER:TCON %s",
        """ A String property that controls the filter's type.
        REP : Repeating filter
        MOV : Moving filter""",
        validator=strict_discrete_set,
        values=['REP', 'MOV'],
        map_values=False)

    filter_count = Instrument.control(
        ":SENS:AVER:COUNT?", ":SENS:AVER:COUNT %d",
        """ A integer property that controls the number of readings that are
        acquired and stored in the filter buffer for the averaging""",
        validator=truncated_range,
        values=[2, 100],
        cast=int)

    filter_state = Instrument.control(
        ":SENS:AVER?", ":SENS:AVER %s",
        """ A string property that controls if the filter is active.""",
        validator=strict_discrete_set,
        values=['ON', 'OFF'],
        map_values=False)

    ####################
    #   Methods        #
    ####################

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Keithley 6487 Picoammeter", **kwargs
        )

    def enable_source(self):
        """Enables the source voltage of the instrument"""
        self.write(":SOUR:VOLT:STAT ON")
    
    def disable_source(self):
        """Disables the source voltage of the instrument"""
        self.write(":SOUR:VOLT:STAT OFF")
    
    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -0.021 A to 0.021 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        log.info("%s is measuring current." % self.name)
        self.write(":SENS:FUNC CURR;"
                   ":SENS:CURR:NPLC %f;:FORM:ELEM READ;" % nplc)
        if auto_range:
            self.write(":SENS:CURR:RANG:AUTO 1;")
        else:
            self.current_range = current
        self.check_errors()

    def auto_range_current(self):
        """ Configures the current measurement to use an automatic range.
        """
        self.write(":SENS:CURR:RANG:AUTO 1")

    display_enabled = Instrument.control(
        ":DISP:ENAB?", ":DISP:ENAB %d",
        """ A boolean property that controls whether or not the display of the
        sourcemeter is enabled. Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    @property

    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0].replace("\\x13",'')
        message = err[1].replace('\\x11', '')
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Keithley 6487 reported error: %s, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 6487 error retrieval.")
    
    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def ramp_to_voltage(self, target_voltage, steps=30, pause=20e-3):
        """ Ramps to a target voltage from the set voltage value over
        a certain number of linear steps, each separated by a pause duration.

        :param target_voltage: A voltage in Volts
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps
        """
        voltages = np.linspace(
            self.source_voltage,
            target_voltage,
            steps
        )
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

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
        points can not exceed 2048 for finite count measurements
        """
        if arm * trigger > 2048 or arm * trigger < 0:
            raise RangeException("Keithley 6487 has a combined maximum "
                                 "of 2048 counts")
        if arm < trigger:
            self.write(":ARM:COUN %d;:TRIG:COUN %d" % (arm, trigger))
        else:
            self.write(":TRIG:COUN %d;:ARM:COUN %d" % (trigger, arm))
    
    def set_trigger_counts_inf(self):
        """ Sets the number of counts for both sweeps and the points in those
        sweeps to INF"""
        self.write(":ARM:COUN INF;:TRIG:COUN INF")
    
    def sample_continuously(self):
        """ Causes the instrument to continuously read samples
        and turns off any buffer or output triggering
        """
        self.disable_buffer()
        self.disable_output_trigger()
        self.trigger_immediately()

    def disable_output_trigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")

    def set_timed_arm(self, interval):
        """ Sets up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points
        """
        if interval > 99999.99 or interval < 0.001:
            raise RangeException("Keithley 6487 can only be time"
                                 " triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)

    def trigger_on_external(self, line=1):
        """ Configures the measurement trigger to be taken from a
        specific line of an external trigger

        :param line: A trigger line from 1 to 6
        """
        cmd = ":ARM:SOUR TLIN;:TRIG:SOUR TLIN;"
        cmd += ":ARM:ILIN %d;:TRIG:ILIN %d;" % (line, line)
        self.write(cmd)

    def output_trigger_on_external(self, line=1, after='DEL'):
        """ Configures the output trigger on the specified trigger link
        line number, with the option of supplying the part of the
        measurement after which the trigger should be generated
        (default to delay, which is right before the measurement)

        :param line: A trigger line from 1 to 6
        :param after: An event string that determines when to trigger
        """
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    def disable_output_trigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")

    def shutdown(self):
        """ Ensures that the voltage is turned to zero
        and disables the output. """
        log.info("Shutting down %s." % self.name)
        self.ramp_to_voltage(0.0)
        self.stop_buffer()
        self.disable_source()