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
from pymeasure.instruments.validators import (
    truncated_range, truncated_discrete_set,
    strict_discrete_set
)
from pymeasure.adapters import VISAAdapter
from .buffer import KeithleyBuffer


class Keithley2000(Instrument, KeithleyBuffer):
    """ Represents the Keithley 2000 Multimeter and provides a high-level
    interface for interacting with the instrument.

    .. code-block:: python

        meter = Keithley2000("GPIB::1")
        meter.measure_voltage()
        print(meter.voltage)

    """
    MODES = {
        'current':'CURR:DC', 'current ac':'CURR:AC',
        'voltage':'VOLT:DC', 'voltage ac':'VOLT:AC',
        'resistance':'RES', 'resistance 4W':'FRES',
        'period':'PER', 'frequency':'FREQ',
        'temperature':'TEMP', 'diode':'DIOD',
        'continuity':'CONT'
    }

    mode = Instrument.control(
        ":CONF?", ":CONF:%s",
        """ A string property that controls the configuration mode for measurements,
        which can take the values: :code:'current' (DC), :code:'current ac',
        :code:'voltage' (DC),  :code:'voltage ac', :code:'resistance' (2-wire),
        :code:'resistance 4W' (4-wire), :code:'period', :code:'frequency',
        :code:'temperature', :code:'diode', and :code:'frequency'. """,
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )

    beep_state = Instrument.control(
        ":SYST:BEEP:STAT?",
        ":SYST:BEEP:STAT %g",
        """ A string property that enables or disables the system status beeper,
        which can take the values: :code:'enabled' and :code:'disabled'. """,
        validator=strict_discrete_set,
        values={'enabled':1, 'disabled':0},
        map_values=True
    )

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(":READ?",
        """ Reads a DC or AC current measurement in Amps, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ A floating point property that controls the DC current range in
        Amps, which can take values from 0 to 3.1 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 3.1]
    )
    current_reference = Instrument.control(
        ":SENS:CURR:REF?", ":SENS:CURR:REF %g",
        """ A floating point property that controls the DC current reference
        value in Amps, which can take values from -3.1 to 3.1 A. """,
        validator=truncated_range,
        values=[-3.1, 3.1]
    )
    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    current_digits = Instrument.control(
        ":SENS:CURR:DIG?", ":SENS:CURR:DIG %d",
        """ An integer property that controls the number of digits in the DC current
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int,
    )
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?", ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %g",
        """ A floating point property that controls the AC current range in
        Amps, which can take values from 0 to 3.1 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 3.1]
    )
    current_ac_reference = Instrument.control(
        ":SENS:CURR:AC:REF?", ":SENS:CURR:AC:REF %g",
        """ A floating point property that controls the AC current reference
        value in Amps, which can take values from -3.1 to 3.1 A. """,
        validator=truncated_range,
        values=[-3.1, 3.1]
    )
    current_ac_nplc = Instrument.control(
        ":SENS:CURR:AC:NPLC?", ":SENS:CURR:AC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the AC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    current_ac_digits = Instrument.control(
        ":SENS:CURR:AC:DIG?", ":SENS:CURR:AC:DIG %d",
        """ An integer property that controls the number of digits in the AC current
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    current_ac_bandwidth = Instrument.control(
        ":SENS:CURR:AC:DET:BAND?", ":SENS:CURR:AC:DET:BAND %g",
        """ A floating point property that sets the AC current detector
        bandwidth in Hz, which can take the values 3, 30, and 300 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 30, 300]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(":READ?",
        """ Reads a DC or AC voltage measurement in Volts, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the DC voltage range in
        Volts, which can take values from 0 to 1010 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1010]
    )
    voltage_reference = Instrument.control(
        ":SENS:VOLT:REF?", ":SENS:VOLT:REF %g",
        """ A floating point property that controls the DC voltage reference
        value in Volts, which can take values from -1010 to 1010 V. """,
        validator=truncated_range,
        values=[-1010, 1010]
    )
    voltage_nplc = Instrument.control(
        ":SENS:CURRVOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    voltage_digits = Instrument.control(
        ":SENS:VOLT:DIG?", ":SENS:VOLT:DIG %d",
        """ An integer property that controls the number of digits in the DC voltage
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG %g",
        """ A floating point property that controls the AC voltage range in
        Volts, which can take values from 0 to 757.5 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 757.5]
    )
    voltage_ac_reference = Instrument.control(
        ":SENS:VOLT:AC:REF?", ":SENS:VOLT:AC:REF %g",
        """ A floating point property that controls the AC voltage reference
        value in Volts, which can take values from -757.5 to 757.5 Volts. """,
        validator=truncated_range,
        values=[-757.5, 757.5]
    )
    voltage_ac_nplc = Instrument.control(
        ":SENS:VOLT:AC:NPLC?", ":SENS:VOLT:AC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the AC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    voltage_ac_digits = Instrument.control(
        ":SENS:VOLT:AC:DIG?", ":SENS:VOLT:AC:DIG %d",
        """ An integer property that controls the number of digits in the AC voltage
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    voltage_ac_bandwidth = Instrument.control(
        ":SENS:VOLT:AC:DET:BAND?", ":SENS:VOLT:AC:DET:BAND %g",
        """ A floating point property that sets the AC voltage detector
        bandwidth in Hz, which can take the values  3, 30, and 300 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 30, 300]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(":READ?",
        """ Reads a resistance measurement in Ohms for both 2-wire and 4-wire
        configurations, based on the active :attr:`~.Keithley2000.mode`. """
    )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ A floating point property that controls the 2-wire resistance range
        in Ohms, which can take values from 0 to 120 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_reference = Instrument.control(
        ":SENS:RES:REF?", ":SENS:RES:REF %g",
        """ A floating point property that controls the 2-wire resistance
        reference value in Ohms, which can take values from 0 to 120 MOhms. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?", ":SENS:RES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    resistance_digits = Instrument.control(
        ":SENS:RES:DIG?", ":SENS:RES:DIG %d",
        """ An integer property that controls the number of digits in the 2-wire
        resistance readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    resistance_4W_range = Instrument.control(
        ":SENS:FRES:RANG?", ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %g",
        """ A floating point property that controls the 4-wire resistance range
        in Ohms, which can take values from 0 to 120 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_4W_reference = Instrument.control(
        ":SENS:FRES:REF?", ":SENS:FRES:REF %g",
        """ A floating point property that controls the 4-wire resistance
        reference value in Ohms, which can take values from 0 to 120 MOhms. """,
        validator=truncated_range,
        values=[0, 120e6]
    )
    resistance_4W_nplc = Instrument.control(
        ":SENS:FRES:NPLC?", ":SENS:FRES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 4-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    resistance_4W_digits = Instrument.control(
        ":SENS:FRES:DIG?", ":SENS:FRES:DIG %d",
        """ An integer property that controls the number of digits in the 4-wire
        resistance readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )

    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(":READ?",
        """ Reads a frequency measurement in Hz, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    frequency_reference = Instrument.control(
        ":SENS:FREQ:REF?", ":SENS:FREQ:REF %g",
        """ A floating point property that controls the frequency reference
        value in Hz, which can take values from 0 to 15 MHz. """,
        validator=truncated_range,
        values=[0, 15e6]
    )
    frequency_digits = Instrument.control(
        ":SENS:FREQ:DIG?", ":SENS:FREQ:DIG %d",
        """ An integer property that controls the number of digits in the frequency
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    frequency_threshold = Instrument.control(
        ":SENS:FREQ:THR:VOLT:RANG?", ":SENS:FREQ:THR:VOLT:RANG %g",
        """ A floating point property that controls the voltage signal threshold
        level in Volts for the frequency measurement, which can take values
        from 0 to 1010 V. """,
        validator=truncated_range,
        values=[0, 1010]
    )
    frequency_aperature = Instrument.control(
        ":SENS:FREQ:APER?", ":SENS:FREQ:APER %g",
        """ A floating point property that controls the frequency aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )

    ##############
    # Period (s) #
    ##############

    period = Instrument.measurement(":READ?",
        """ Reads a period measurement in seconds, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    period_reference = Instrument.control(
        ":SENS:PER:REF?", ":SENS:PER:REF %g",
        """ A floating point property that controls the period reference value
        in seconds, which can take values from 0 to 1 s. """,
        validator=truncated_range,
        values=[0, 1]
    )
    period_digits = Instrument.control(
        ":SENS:PER:DIG?", ":SENS:PER:DIG %d",
        """ An integer property that controls the number of digits in the period
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
    )
    period_threshold = Instrument.control(
        ":SENS:PER:THR:VOLT:RANG?", ":SENS:PRE:THR:VOLT:RANG %g",
        """ A floating point property that controls the voltage signal threshold
        level in Volts for the period measurement, which can take values
        from 0 to 1010 V. """,
        validator=truncated_range,
        values=[0, 1010]
    )
    period_aperature = Instrument.control(
        ":SENS:PER:APER?", ":SENS:PER:APER %g",
        """ A floating point property that controls the period aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(":READ?",
        """ Reads a temperature measurement in Celsius, based on the
        active :attr:`~.Keithley2000.mode`. """
    )
    temperature_reference = Instrument.control(
        ":SENS:TEMP:REF?", ":SENS:TEMP:REF %g",
        """ A floating point property that controls the temperature reference value
        in Celsius, which can take values from -200 to 1372 C. """,
        validator=truncated_range,
        values=[-200, 1372]
    )
    temperature_nplc = Instrument.control(
        ":SENS:TEMP:NPLC?", ":SENS:TEMP:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the temperature measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """
    )
    temperature_digits = Instrument.control(
        ":SENS:TEMP:DIG?", ":SENS:TEMP:DIG %d",
        """ An integer property that controls the number of digits in the temperature
        readings, which can take values from 4 to 7. """,
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int
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
        in seconds, which can take values from 1 to 9,999,999.999 s. """,
        validator=truncated_range,
        values=[0, 999999.999]
    )

    def __init__(self, adapter, **kwargs):
        super(Keithley2000, self).__init__(
            adapter, "Keithley 2000 Multimeter", **kwargs
        )
        # Set up data transfer format
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.config(
                is_binary=False,
                datatype='float32',
                converter='f',
                separator=','
            )

    # TODO: Clean up error checking
    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Keithley 2000: %s: %s" % (err[0],err[1])
                log.error(errmsg + '\n')
            else:
                break

    def measure_voltage(self, max_voltage=1, ac=False):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if ac:
            self.mode = 'voltage ac'
            self.voltage_ac_range = max_voltage
        else:
            self.mode = 'voltage'
            self.voltage_range = max_voltage

    def measure_current(self, max_current=10e-3, ac=False):
        """ Configures the instrument to measure current,
        based on a maximum current to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_current: A current in Volts to set the current range
        :param ac: False for DC current, and True for AC current
        """
        if ac:
            self.mode = 'current ac'
            self.current_ac_range = max_current
        else:
            self.mode = 'current'
            self.current_range = max_current

    def measure_resistance(self, max_resistance=10e6, wires=2):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if wires == 2:
            self.mode = 'resistance'
            self.resistance_range = max_resistance
        elif wires == 4:
            self.mode = 'resistance 4W'
            self.resistance_4W_range = max_resistance
        else:
            raise ValueError("Keithley 2000 only supports 2 or 4 wire"
                             "resistance meaurements.")

    def measure_period(self):
        """ Configures the instrument to measure the period. """
        self.mode = 'period'

    def measure_frequency(self):
        """ Configures the instrument to measure the frequency. """
        self.mode = 'frequency'

    def measure_temperature(self):
        """ Configures the instrument to measure the temperature. """
        self.mode = 'temperature'

    def measure_diode(self):
        """ Configures the instrument to perform diode testing.  """
        self.mode = 'diode'

    def measure_continuity(self):
        """ Configures the instrument to perform continuity testing. """
        self.mode = 'continuity'

    def _mode_command(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    def auto_range(self, mode=None):
        """ Sets the active mode to use auto-range,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:RANG:AUTO 1" % self._mode_command(mode))

    def enable_reference(self, mode=None):
        """ Enables the reference for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:REF:STAT 1" % self._mode_command(mode))

    def disable_reference(self, mode=None):
        """ Disables the reference for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:REF:STAT 0" % self._mode_command(mode))

    def acquire_reference(self, mode=None):
        """ Sets the active value as the reference for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:REF:ACQ" % self._mode_command(mode))

    def enable_filter(self, mode=None, type='repeat', count=1):
        """ Enables the averaging filter for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        :param type: The type of averaging filter, either 'repeat' or 'moving'.
        :param count: A number of averages, which can take take values from 1 to 100
        """
        self.write(":SENS:%s:AVER:STAT 1")
        self.write(":SENS:%s:AVER:TCON %s")
        self.write(":SENS:%s:AVER:COUN %d")

    def disable_filter(self, mode=None):
        """ Disables the averaging filter for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Keithley2000.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:AVER:STAT 0" % self._mode_command(mode))

    def local(self):
        """ Returns control to the instrument panel, and enables
        the panel if disabled. """
        self.write(":SYST:LOC")

    def remote(self):
        """ Places the instrument in the remote state, which is
        does not need to be explicity called in general. """
        self.write(":SYST:REM")

    def remote_lock(self):
        """ Disables and locks the front panel controls to prevent
        changes during remote operations. This is disabled by
        calling :meth:`~.Keithley2000.local`.  """
        self.write(":SYST:RWL")

    def reset(self):
        """ Resets the instrument state. """
        self.write(":STAT:QUEUE:CLEAR;*RST;:STAT:PRES;:*CLS;")

    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(":SYST:BEEP %g, %g" % (frequency, duration))
