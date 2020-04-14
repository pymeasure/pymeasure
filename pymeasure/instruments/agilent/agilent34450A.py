#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
from time import sleep

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class Agilent34450A(Instrument):
    """
    Represent the HP/Agilent/Keysight 34450A and related multimeters.

    #TODO: Complete documentation, add implementation example.
    """

    # Implementation based on current keithley2000 implementation.

    # TODO: test modes implementation
    MODES = {
        'current': 'CURR:DC', 'current ac': 'CURR:AC',
        'voltage': 'VOLT:DC', 'voltage ac': 'VOLT:AC',
        'resistance': 'RES', 'resistance 4W': 'FRES',
        'frequency': 'FREQ', 'continuity': 'CONT',
        'diode': 'DIOD', 'temperature': 'TEMP'
    }

    mode = Instrument.control(
        ":CONF?", ":CONF:%s",
        """ A string property that controls the configuration mode for measurements,
        which can take the values: :code:'current' (DC), :code:'current ac',
        :code:'voltage' (DC),  :code:'voltage ac', :code:'resistance' (2-wire),
        :code:'resistance 4W' (4-wire), :code:'frequency', :code:'continuity',
        :code:'diode', and :code:'temperature'. """,
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )

    # TODO: Test methods for current
    #TODO: Figure out is "measurement" allows for both numbers and strings.
    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(":READ?",
                                     """ Reads a DC or AC current measurement in Amps, based on the
                                     active :attr:`~.Agilent34450A.mode`. """
                                     )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %s",
        """ A property that controls the DC current range in
        Amps, which can take values 100E-6, 1E-3, 10E-3, 100E-3, 1, 10, 
        as well as MIN (100 uA), DEF (100 mA), and MAX (10 A).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-6, 1E-3, 10E-3, 100E-3, 1, 10, "MIN", "DEF", "MAX"]
    )
    current_resolution = Instrument.control(
        ":SENS:CURR:RES?", ":SENS:CURR:RES %s",
        """ A property that controls the resolution in the DC current
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?", ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %s",
        """ A property that controls the AC current range in
        Amps, which can take values 10E-3, 100E-3, 1, 10, as well as MIN (10 mA), 
        MAX (10 A), and DEF (100 mA).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10E-3, 100E-3, 1, 10, "MIN", "MAX", "DEF"]
    )
    current_ac_resolution = Instrument.control(
        ":SENS:CURR:AC:RES?", ":SENS:CURR:AC:RES %s",
        """ An property that controls the resolution in the AC current
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN (1.50E-6), MAX (3.00E-5), and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    # TODO: Test methods
    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(":READ?",
                                     """ Reads a DC or AC voltage measurement in Volts, based on the
                                     active :attr:`~.Agilent34450A.mode`. """
                                     )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %s",
        """ A property that controls the DC voltage range in
        Volts, which can take values 100E-3, 1, 10, 100, 1000, 
        as well as MIN, MAX, and DEF (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 1000, "MAX", "MIN", "DEF"]
    )
    voltage_resolution = Instrument.control(
        ":SENS:VOLT:RES?", ":SENS:VOLT:RES %s",
        """ A property that controls the resolution in the DC voltage
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG %s",
        """ A property that controls the AC voltage range in
        Volts, which can take values 100E-3, 1, 10, 100, 750, 
        as well as MIN, MAX, and DEF (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 750, "MAX", "MIN", "DEF"]
    )
    voltage_ac_resolution = Instrument.control(
        ":SENS:VOLT:AC:RES?", ":SENS:VOLT:AC:RES %s",
        """ A property that controls the resolution in the AC voltage
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    # TODO: Test methods
    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(":READ?",
                                        """ Reads a resistance measurement in Ohms for both 2-wire and 4-wire
                                        configurations, based on the active :attr:`~.Agilent34450A.mode`. """
                                        )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %s",
        """ A property that controls the 2-wire resistance range
        in Ohms, which can take values 100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, 
        as well as MIN, MAX, and DEF (1E3).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, "MAX", "MIN", "DEF"]
    )
    resistance_resolution = Instrument.control(
        ":SENS:RES:RES?", ":SENS:RES:RES %s",
        """ A property that controls the resolution in the 2-wire
        resistance readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    resistance_4W_range = Instrument.control(
        ":SENS:FRES:RANG?", ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %s",
        """ A property that controls the 4-wire resistance range
        in Ohms, which can take values 100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, 
        as well as MIN, MAX, and DEF (1E3).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, "MAX", "MIN", "DEF"]
    )
    resistance_4W_resolution = Instrument.control(
        ":SENS:FRES:RES?", ":SENS:FRES:RES %s",
        """ A property that controls the resolution in the 4-wire
        resistance readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    # TODO: Test methods
    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(":READ?",
                                       """ Reads a frequency measurement in Hz, based on the
                                       active :attr:`~.Agilent34450A.mode`. """
                                       )
    frequency_resolution = Instrument.control(
        ":SENS:FREQ:RES?", ":SENS:FREQ:RES %s",
        """ A property that controls the resolution in the frequency
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits), 
        as well as MIN, MAX, and DEF (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    frequency_aperture = Instrument.control(
        ":SENS:FREQ:APER?", ":SENS:FREQ:APER %s",
        """ A property that controls the frequency aperture in seconds,
        which sets the integration period and measurement speed. Takes values
        100 ms, 1 s, as well as MIN, MAX, and DEF (1 s). """,
        validator=strict_discrete_set,
        values=[100E-3, 1, "MIN", "MAX", "DEF"]
    )

    # TODO: Test methods
    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(":READ?",
                                         """ Reads a temperature measurement in Celsius, based on the
                                         active :attr:`~.Agilent34450A.mode`. """
                                         )

    # TODO: test methods
    #############
    # Diode (V) #
    #############

    diode = Instrument.measurement(":READ?",
                                   """ Reads a diode measurement in Volts, based on the 
                                   active :attr:`~.Agilent34450A.mode`. """
                                   )

    # TODO: Test methods
    ###################
    # Capacitance (F) #
    ###################

    capacitance = Instrument.measurement(":READ?",
                                         """ Reads a capacitance measurement in Farads, 
                                         based on the active :attr:`~.Agilent34450A.mode`. """
                                         )
    capacitance_range = Instrument.control(
        ":SENS:CAP:RANG?", ":SENS:CAP:RANG:AUTO 0;:SENS:CAP:RANG %s",
        """ A property that controls the capacitance range
        in Farads, which can take values 1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 
        1E-3, 10E-3, as well as MIN, MAX, and DEF (1E-6).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 1E-3, 10E-3, "MAX", "MIN", "DEF"]
    )

    # TODO: Test method
    ####################
    # Continuity (Ohm) #
    ####################

    continuity = Instrument.measurement(":READ?",
                                        """ Reads a continuity measurement in Ohms, 
                                        based on the active :attr:`~.Agilent34450A.mode`. """
                                        )

    def __init__(self, adapter, **kwargs):
        super(Agilent34450A, self).__init__(
            adapter, "HP/Agilent/Keysight 34450A Multimeter", **kwargs
        )

        self.check_errors()

    # TODO: Clean up error checking
    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 34450A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
            else:
                break

    # TODO: Test method
    def configure_voltage(self, max_voltage="DEF", ac=False, resolution="DEF"):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range,
        a boolean flag to determine if DC or AC is required,
        and the desired resolution.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        :param resolution: Desired resolution
        """
        if ac:
            self.mode = 'voltage ac'
            self.voltage_ac_range = max_voltage
            self.voltage_ac_resolution = resolution
        else:
            self.mode = 'voltage'
            self.voltage_range = max_voltage
            self.voltage_resolution = resolution

    # TODO: Test method
    def configure_current(self, max_current="DEF", ac=False, resolution="DEF'"):
        """ Configures the instrument to measure current,
        based on a maximum current to set the range,
        a boolean flag to determine if DC or AC is required,
        and the desired resolution.

        :param max_current: A current in Amps to set the current range
        :param ac: False for DC current, and True for AC current
        :param resolution: Desired resolution
        """
        if ac:
            self.mode = 'current ac'
            self.current_ac_range = max_current
            self.current_ac_resolution = resolution
        else:
            self.mode = 'current'
            self.current_range = max_current
            self.current_resolution = resolution

    # TODO: Test method
    def configure_resistance(self, max_resistance="DEF", wires=2, resolution="DEF"):
        """ Configures the instrument to measure resistance,
        based on a maximum resistance to set the range,
        the number of wires, and the desired measurement resolution.

        :param max_resistance: A resistance in Ohms to set the resistance range
        :param wires: Number of wires used for measurement
        :param resolution: Desired resolution
        """
        if wires == 2:
            self.mode = 'resistance'
            self.resistance_range = max_resistance
            self.resistance_resolution = resolution
        elif wires == 4:
            self.mode = 'resistance 4W'
            self.resistance_4W_range = max_resistance
            self.resistance_4W_resolution =resolution
        else:
            raise ValueError("Agilent 34450A only supports 2 or 4 wire"
                             "resistance meaurements.")

    # TODO: Test method
    def configure_frequency(self, aperture="DEF", resolution="DEF"):
        """ Configures the instrument to measure frequency,
        based on an aperture time and the desired resolution.

        :param aperture: Aperture time in Seconds
        :param resolution: Desired resolution
        """
        self.mode = 'frequency'
        self.frequency_aperture = aperture
        self.frequency_resolution = resolution

    # TODO: Test method
    def configure_temperature(self):
        """ Configures the instrument to measure temperature.
        """
        self.mode = 'temperature'

    # TODO: Test method
    def configure_diode(self):
        """ Configures the instrument to measure diode voltage.
        """
        self.mode = 'diode'

    # TODO: Test method
    def configure_capacitance(self, max_capacitance="DEF"):
        """ Configures the instrument to measure capacitance,
        based on a maximum capacitance to set the range.

        :param max_capacitance: A capacitance in Farads to set the capacitance range
        """
        self.mode = 'capacitance'
        self.capacitance_range = max_capacitance

    # TODO: Test method
    def configure_continuity(self):
        """ Configures the instrument to measure continuity.
        """
        self.mode = 'continuity'

    def _mode_command(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    # TODO: Test method
    def auto_range(self, mode=None):
        """ Sets the active mode to use auto-range,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Agilent34450A.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:RANG:AUTO 1" % self._mode_command(mode))

    # TODO: Command is not is not in reference
    def local(self):
        """ Returns control to the instrument panel, and enables
        the panel if disabled. """
        self.write(":SYST:LOC")

    # TODO: Command is not is not in reference
    def remote(self):
        """ Places the instrument in the remote state, which is
        does not need to be explicity called in general. """
        self.write(":SYST:REM")

    # TODO: Command is not is not in reference
    def remote_lock(self):
        """ Disables and locks the front panel controls to prevent
        changes during remote operations. This is disabled by
        calling :meth:`~.Keithley2000.local`.  """
        self.write(":SYST:RWL")

    # TODO: Test method
    def reset(self):
        """ Resets the instrument state. """
        self.write("*RST")

    # TODO: Test method
    def beep(self, frequency, duration):
        """ Sounds a system beep.
        """
        self.write(":SYST:BEEP")


