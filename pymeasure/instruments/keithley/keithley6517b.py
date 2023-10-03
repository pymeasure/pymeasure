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
import re

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range
from .buffer import KeithleyBuffer

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley6517B(KeithleyBuffer, Instrument):
    """ Represents the Keithley 6517B ElectroMeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley6517B("GPIB::1")

        keithley.apply_voltage()              # Sets up to source current
        keithley.source_voltage_range = 200   # Sets the source voltage
                                              # range to 200 V
        keithley.source_voltage = 20          # Sets the source voltage to 20 V
        keithley.enable_source()              # Enables the source output

        keithley.measure_resistance()         # Sets up to measure resistance

        keithley.ramp_to_voltage(50)          # Ramps the voltage to 50 V
        print(keithley.resistance)            # Prints the resistance in Ohms

        keithley.shutdown()                   # Ramps the voltage to 0 V
                                              # and disables output

    """

    source_enabled = Instrument.measurement(
        "OUTPUT?",
        """ Reads a boolean value that is True if the source is enabled. """,
        cast=bool
    )

    @staticmethod
    def extract_value(result):
        """ extracts the physical value from a result object returned
            by the instrument """
        m = re.fullmatch(r'([+\-0-9E.]+)[A-Z]{4}', result[0])
        if m:
            return float(m.group(1))
        return None

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":MEAS?",
        """ Reads the current in Amps, if configured for this reading.
        """, get_process=extract_value
    )

    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ A floating point property that controls the measurement current
        range in Amps, which can take values between -20 and +20 mA.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-20e-3, 20e-3]
    )

    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %g",
        """ A floating point property that controls the number of power
        line cycles (NPLC) for the DC current measurements, which sets the
        integration period and measurement speed. Takes values from 0.01 to
        10, where 0.1, 1, and 10 are Fast, Medium, and Slow respectively. """,
        values=[0.01, 10]
    )

    source_current_resistance_limit = Instrument.control(
        ":SOUR:CURR:RLIM?", ":SOUR:CURR:RLIM %g",
        """ Boolean property which enables or disables resistance
        current limit """,
        cast=bool
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":MEAS:VOLT?",
        """ Reads the voltage in Volts, if configured for this reading.
        """, get_process=extract_value
    )

    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -1000 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1000, 1000]
    )

    voltage_nplc = Instrument.control(
        ":SENS:VOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """ A floating point property that controls the number of power
        line cycles (NPLC) for the DC voltage measurements, which sets the
        integration period and measurement speed. Takes values from 0.01 to
        10, where 0.1, 1, and 10 are Fast, Medium, and Slow respectively. """
    )

    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT:LEV %g",
        """ A floating point property that controls the source voltage
        in Volts. """
    )

    source_voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG:AUTO 0;:SOUR:VOLT:RANG %g",
        """ A floating point property that controls the source voltage
        range in Volts, which can take values from -1000 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-1000, 1000]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Reads the resistance in Ohms, if configured for this reading.
        """, get_process=extract_value
    )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ A floating point property that controls the resistance range
        in Ohms, which can take values from 0 to 100e18 Ohms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 100e18]
    )
    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?", ":SENS:RES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the
        integration period and measurement speed. Takes values from 0.01
        to 10, where 0.1, 1, and 10 are Fast, Medium, and Slow respectively.
        """
    )

    buffer_points = Instrument.control(
        ":TRAC:POIN?", ":TRAC:POIN %d",
        """ An integer property that controls the number of buffer points. This
        does not represent actual points in the buffer, but the configuration
        value instead. """,
        validator=truncated_range,
        values=[1, 6875000],
        cast=int
    )

    ####################
    # Methods        #
    ####################

    def __init__(self, adapter, name="Keithley 6517B Electrometer/High Resistance Meter", **kwargs):
        super().__init__(
            adapter, name,
            **kwargs
        )

    def enable_source(self):
        """ Enables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTPUT ON")

    def disable_source(self):
        """ Disables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTPUT OFF")

    def measure_resistance(self, nplc=1, resistance=2.1e5, auto_range=True):
        """ Configures the measurement of resistance.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param resistance: Upper limit of resistance in Ohms,
                           from -210 POhms to 210 POhms
        :param auto_range: Enables auto_range if True, else uses the
                           resistance_range attribut
        """
        log.info("%s is measuring resistance.", self.name)
        self.write(":SENS:FUNC 'RES';"
                   ":SENS:RES:NPLC %f;" % nplc)
        if auto_range:
            self.write(":SENS:RES:RANG:AUTO 1;")
        else:
            self.resistance_range = resistance
        self.check_errors()

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -1000 V to 1000 V
        :param auto_range: Enables auto_range if True, else uses the
                           voltage_range attribut
        """
        log.info("%s is measuring voltage.", self.name)
        self.write(":SENS:FUNC 'VOLT';"
                   ":SENS:VOLT:NPLC %f;" % nplc)
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO 1;")
        else:
            self.voltage_range = voltage
        self.check_errors()

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -21 mA to 21 mA
        :param auto_range: Enables auto_range if True, else uses the
                           current_range attribut
        """
        log.info("%s is measuring current.", self.name)
        self.write(":SENS:FUNC 'CURR';"
                   ":SENS:CURR:NPLC %f;" % nplc)
        if auto_range:
            self.write(":SENS:CURR:RANG:AUTO 1;")
        else:
            self.current_range = current
        self.check_errors()

    def auto_range_source(self):
        """ Configures the source to use an automatic range.
        """
        self.write(":SOUR:VOLT:RANG:AUTO 1")

    def apply_voltage(self, voltage_range=None):
        """ Configures the instrument to apply a source voltage, and
        uses an auto range unless a voltage range is specified.

        :param voltage_range: A :attr:`~.Keithley6517B.voltage_range` value
                              or None (activates auto range)
        """
        log.info("%s is sourcing voltage.", self.name)
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.check_errors()

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
            log.info("Keithley 6517B reported error: %d, %s", code, message)
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 6517B error retrieval.")

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("*RST;:stat:pres;:*CLS;")

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
        self.write(":TRIG:SOUR IMM;")

    def trigger_on_bus(self):
        """ Configures the trigger to detect events based on the bus
        trigger, which can be activated by :meth:`~.trigger`.
        """
        self.write(":TRIG:SOUR BUS;")

    def shutdown(self):
        """ Ensures that the current or voltage is turned to zero
        and disables the output. """
        log.info("Shutting down %s.", self.name)
        self.ramp_to_voltage(0.0)
        self.stop_buffer()
        self.disable_source()
        super().shutdown()
