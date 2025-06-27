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

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range
from .buffer import KeithleyBuffer
import logging

# Set up logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KeithleyDAQ6510(KeithleyBuffer, SCPIMixin, Instrument):
    """ Represents the Keithley DAQ6510 Data Acquisition Logging Multimeter System
    and provides a high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = KeithleyDAQ6510("GPIB::1")
        keithley = KeithleyDAQ6510("TCPIP::192.168.1.1::INSTR")

        print(keithley.current)                 # Prints the current in Amps
        keithley.current_range = 10E-6          # Select the 10 uA range

        print(keithley.voltage)                 # Prints the voltage in Volts
        keithley.voltage_range = 100e-3         # Select the 100 mV range

        print(keithley.resistance)              # Prints the resistance in Ohms
        keithley.offset_compensated = "ON"      # Turns offset-compensated ohms on

        keithley.open_channels([134, 135])      # Open channels 134 and 135 on the MUX card
        keithley.close_channel(133)             # Close channel 133 on the MUX card

    """

    def __init__(self, adapter, name="Keithley DAQ6510", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    sense_mode = Instrument.control(
        ":SENS:FUNC?", ":SENS:FUNC \"%s\"",
        """ Control the reading mode, which can take the values 'current' or 'voltage'.
        The convenience methods :meth:`~.KeithleyDAQ6510.sense_current` and
        :meth:`~.KeithleyDAQ6510.sense_voltage` can also be used. """,
        validator=strict_discrete_set,
        values={'current': 'CURR', 'voltage': 'VOLT'},
        map_values=True
    )

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":READ?",
        """ Measure the current in Amps, if configured for this reading.
        """
    )

    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ Control the measurement current range in Amps. If the measurement function is DC,
        available ranges are 10E-6 A to 3A. If the measurement function is AC,
        available ranges are 100E-6 to 3A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[10E-6, 3]
    )

    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?", ":SENS:CURR:NPLC %g",
        """ Control the number of power line cycles (NPLC) for the DC current measurements,
        which sets the integration period and measurement speed.
        Takes values from 5E-4 to 15 (60 Hz) or 12 (50 Hz or 400 Hz). The smallest value is the
        shortest time, and results in the fastest reading rate, but increases the reading noise
        and decreases the number of usable digits. The largest value is the longest time, and
        results in the lowest reading rate, but increases the number of usable digits. """
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """ Measure the voltage in Volts, if configured for this reading.
        """
    )

    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ Control the measurement voltage range in Volts. If the measurement function is DC,
        available ranges are 100E-3 V to 1000 V. If the measurement function is AC, available
        ranges are 100E-3 to 750 V. Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[100E-3, 1000]
    )

    voltage_nplc = Instrument.control(
        ":SENS:VOLT:NPLC?", ":SENS:VOLT:NPLC %g",
        """ Control the number of power line cycles (NPLC) for the DC voltage measurements,
        which sets the integration period and measurement speed.
        Takes values from 5E-4 to 15 (60 Hz) or 12 (50 Hz or 400 Hz).
        The smallest value is the shortest time, and results in the fastest reading rate,
        but increases the reading noise and decreases the number of usable digits.
        The largest value is the longest time, and results in the lowest reading rate,
        but increases the number of usable digits. """
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Measure the resistance in Ohms, if configured for this reading.
        """
    )

    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ Control the resistance range in Ohms. If the measurement function is 2-wire,
        the available ranges are 10 to 100E6 Ohms. If the measurement function is
        4-wire resistance with offset compensation off, the available ranges
        are 1 to 100E6 Ohms. If the measurement function is 4-wire resistance
        with offset compensation on, the available ranges are 1 to 10E3 Ohms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[1, 100E6]
    )

    offset_compensated = Instrument.control(
        ":SENS:FRES:OCOM?", ":SENS:FRES:OCOM %s",
        """ Control if offset compensation is used or not.
        Valid values are OFF, ON, and AUTO. """,
        validator=strict_discrete_set,
        values=["OFF", "ON", "AUTO"],
        map_values=False
    )

    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?", ":SENS:RES:NPLC %g",
        """ Control the number of power line cycles (NPLC) for the 2-wire resistance measurements,
        which sets the integration period and measurement speed.
        Takes values from 5E-4 to 15 (60 Hz) or 12 (50 Hz or 400 Hz).
        The smallest value is the shortest time, and results in the fastest reading rate,
        but increases the reading noise and decreases the number of usable digits.
        The largest value is the longest time, and results in the lowest reading rate,
        but increases the number of usable digits. """
    )

    ####################
    # Methods        #
    ####################

    def measure_resistance(self, nplc=1, resistance=100e6, auto_range=True):
        """ Configure the measurement of resistance.

        :param nplc: Number of power line cycles (NPLC) from 5E-4 to 15 (60 Hz)
                     or 12 (50 Hz or 400 Hz).
        :param resistance: Upper limit of resistance in Ohms, from 10 to 100E6 (2-wire),
                           1 to 100E6 (4-wire with OCOM off), or 1 to 10E3 (4-wire with OCOM on).
        :param auto_range: A boolean value to enable auto_range if ``True``,
                           else uses the set resistance.
        """
        log.info(f"{self.name} is measuring resistance.")
        self.write(f":SENS:FUNC \"RES\";:SENS:RES:NPLC {nplc};")
        if auto_range:
            self.write(":SENS:RES:RANG:AUTO ON;")
        else:
            self.resistance_range = resistance
        self.check_errors()

    def measure_voltage(self, nplc=1, voltage=1000, auto_range=True):
        """ Configure the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 5E-4 to 15 (60 Hz)
                     or 12 (50 Hz or 400 Hz).
        :param voltage: Upper limit of voltage in Volts, from 100E-3 to 1000 V (DC)
                        or 100E-3 to 750 V (AC).
        :param auto_range: A boolean value to enable auto_range if ``True``,
                           else uses the set voltage.
        """
        log.info(f"{self.name} is measuring voltage.")
        self.write(f":SENS:FUNC \"VOLT\";:SENS:VOLT:NPLC {nplc};")
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO ON;")
        else:
            self.voltage_range = voltage
        self.check_errors()

    def measure_current(self, nplc=1, current=3, auto_range=True):
        """ Configure the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 5E-4 to 15 (60 Hz)
                     or 12 (50 Hz or 400 Hz).
        :param current: Upper limit of current in Amps, from 10E-6 to 3 A (DC)
                        or 100E-6 to 3A (AC).
        :param auto_range: A boolean value to enable auto_range if ``True``,
                           else uses the set current.
        """
        log.info(f"{self.name} is measuring current.")
        self.write(f":SENS:FUNC \"CURR\";:SENS:CURR:NPLC {nplc};")
        if auto_range:
            self.write(":SENS:CURR:RANG:AUTO ON;")
        else:
            self.current_range = current
        self.check_errors()

    def open_channel(self, channel):
        """
        Set a single channel to open.

        :param channel: Channel to be set to open.
        """
        self.write(f":ROUT:OPEN (@{channel})")

    def close_channel(self, channel):
        """
        Set a single channel to closed.

        :param channel: Channel to be set to closed.
        """
        self.write(f":ROUT:CLOS (@{channel})")

    def open_channels(self, channel_list):
        """
        Configure multiple channels to be open.

        :param channel_list: List of channels to be set to open.
        """
        for channel in channel_list:
            self.open_channel(channel)

    def close_channels(self, channel_list):
        """
        Configure multiple channels to be closed.

        :param channel_list: List of channels to be set to closed.
        """
        for channel in channel_list:
            self.close_channel(channel)

    def beep(self, frequency, duration):
        """
        Sound a system beep.

        :param frequency: A frequency in Hz from 20 and 8000 Hz
        :param duration: The amount of time to play the tone, between 0.001 s to 100 s
        :return: None
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")
