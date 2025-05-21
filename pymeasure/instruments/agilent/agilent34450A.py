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

import re
import logging

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Agilent34450A(SCPIUnknownMixin, Instrument):
    """
    Represent the HP/Agilent/Keysight 34450A and related multimeters.

    .. code-block:: python

        dmm = Agilent34450A("USB0::...")
        dmm.reset()
        dmm.configure_voltage()
        print(dmm.voltage)
        dmm.shutdown()

    """

    BOOLS = {True: 1, False: 0}

    MODES = {'current': 'CURR', 'ac current': 'CURR:AC',
             'voltage': 'VOLT', 'ac voltage': 'VOLT:AC',
             'resistance': 'RES', '4w resistance': 'FRES',
             'current frequency': 'FREQ:ACI', 'voltage frequency': 'FREQ:ACV',
             'continuity': 'CONT',
             'diode': 'DIOD',
             'temperature': 'TEMP',
             'capacitance': 'CAP'}

    @property
    def mode(self):
        get_command = ":configure?"
        vals = self._conf_parser(self.values(get_command))
        # Return only the mode parameter
        inv_modes = {v: k for k, v in self.MODES.items()}
        mode = inv_modes[vals[0]]
        return mode

    @mode.setter
    def mode(self, value):
        """ A string parameter that sets the measurement mode of the multimeter. Can be "current",
        "ac current", "voltage", "ac voltage", "resistance", "4w resistance", "current frequency",
        "voltage frequency", "continuity", "diode", "temperature", or "capacitance"."""
        if value in self.MODES:
            if value not in ['current frequency', 'voltage frequency']:
                self.write(':configure:' + self.MODES[value])
            else:
                if value == 'current frequency':
                    self.mode = 'ac current'
                else:
                    self.mode = 'ac voltage'
                self.write(":configure:freq")
        else:
            raise ValueError(f'Value {value} is not a supported mode for this device.')

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(":READ?",
                                     """ Reads a DC current measurement in Amps, based on the
                                     active :attr:`~.Agilent34450A.mode`. """
                                     )
    current_ac = Instrument.measurement(":READ?",
                                        """ Reads an AC current measurement in Amps, based on the
                                        active :attr:`~.Agilent34450A.mode`. """
                                        )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?", ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %s",
        """ A property that controls the DC current range in
        Amps, which can take values 100E-6, 1E-3, 10E-3, 100E-3, 1, 10,
        as well as "MIN", "MAX", or "DEF" (100 mA).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-6, 1E-3, 10E-3, 100E-3, 1, 10, "MIN", "DEF", "MAX"]
    )
    current_auto_range = Instrument.control(
        ":SENS:CURR:RANG:AUTO?", ":SENS:CURR:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for DC current. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    current_resolution = Instrument.control(
        ":SENS:CURR:RES?", ":SENS:CURR:RES %s",
        """ A property that controls the resolution in the DC current
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
        as well as "MIN", "MAX", and "DEF" (3.00E-5). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?", ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %s",
        """ A property that controls the AC current range in Amps, which can take
        values 10E-3, 100E-3, 1, 10, as well as "MIN", "MAX", or "DEF" (100 mA).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10E-3, 100E-3, 1, 10, "MIN", "MAX", "DEF"]
    )
    current_ac_auto_range = Instrument.control(
        ":SENS:CURR:AC:RANG:AUTO?", ":SENS:CURR:AC:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for AC current. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    current_ac_resolution = Instrument.control(
        ":SENS:CURR:AC:RES?", ":SENS:CURR:AC:RES %s",
        """ An property that controls the resolution in the AC current
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
        as well as "MIN", "MAX", or "DEF" (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(":READ?",
                                     """ Reads a DC voltage measurement in Volts, based on the
                                     active :attr:`~.Agilent34450A.mode`. """
                                     )
    voltage_ac = Instrument.measurement(":READ?",
                                        """ Reads an AC voltage measurement in Volts, based on the
                                        active :attr:`~.Agilent34450A.mode`. """
                                        )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %s",
        """ A property that controls the DC voltage range in Volts, which
        can take values 100E-3, 1, 10, 100, 1000, as well as "MIN", "MAX", or
        "DEF" (10 V). Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 1000, "MAX", "MIN", "DEF"]
    )
    voltage_auto_range = Instrument.control(
        ":SENS:VOLT:RANG:AUTO?", ":SENS:VOLT:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for DC voltage. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    voltage_resolution = Instrument.control(
        ":SENS:VOLT:RES?", ":SENS:VOLT:RES %s",
        """ A property that controls the resolution in the DC voltage
        readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
        as well as "MIN", "MAX", or "DEF" (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?", ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG %s",
        """ A property that controls the AC voltage range in Volts, which can
        take values 100E-3, 1, 10, 100, 750, as well as "MIN", "MAX", or "DEF"
        (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 750, "MAX", "MIN", "DEF"]
    )
    voltage_ac_auto_range = Instrument.control(
        ":SENS:VOLT:AC:RANG:AUTO?", ":SENS:VOLT:AC:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for AC voltage. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    voltage_ac_resolution = Instrument.control(
        ":SENS:VOLT:AC:RES?", ":SENS:VOLT:AC:RES %s",
        """ A property that controls the resolution in the AC voltage readings,
        which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
        as well as "MIN", "MAX", or "DEF" (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(":READ?",
                                        """ Reads a resistance measurement in Ohms for 2-wire
                                        configuration, based on the active
                                        :attr:`~.Agilent34450A.mode`. """
                                        )
    resistance_4w = Instrument.measurement(":READ?",
                                           """ Reads a resistance measurement in Ohms for
                                           4-wire configuration, based on the active
                                           :attr:`~.Agilent34450A.mode`. """
                                           )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %s",
        """ A property that controls the 2-wire resistance range in Ohms, which can
        take values 100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, as well as "MIN", "MAX",
        or "DEF" (1E3).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, "MAX", "MIN", "DEF"]
    )
    resistance_auto_range = Instrument.control(
        ":SENS:RES:RANG:AUTO?", ":SENS:RES:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for 2-wire resistance. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    resistance_resolution = Instrument.control(
        ":SENS:RES:RES?", ":SENS:RES:RES %s",
        """ A property that controls the resolution in the 2-wire
        resistance readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
        as well as "MIN", "MAX", or "DEF" (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )
    resistance_4w_range = Instrument.control(
        ":SENS:FRES:RANG?", ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %s",
        """ A property that controls the 4-wire resistance range
        in Ohms, which can take values 100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6,
        as well as "MIN", "MAX", or "DEF" (1E3).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6, "MAX", "MIN", "DEF"]
    )
    resistance_4w_auto_range = Instrument.control(
        ":SENS:FRES:RANG:AUTO?", ":SENS:FRES:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for 4-wire resistance. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    resistance_4w_resolution = Instrument.control(
        ":SENS:FRES:RES?", ":SENS:FRES:RES %s",
        """ A property that controls the resolution in the 4-wire
        resistance readings, which can take values 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
        as well as "MIN", "MAX", or "DEF" (1.50E-6). """,
        validator=strict_discrete_set,
        values=[3.00E-5, 2.00E-5, 1.50E-6, "MAX", "MIN", "DEF"]
    )

    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(":READ?",
                                       """ Reads a frequency measurement in Hz, based on the
                                       active :attr:`~.Agilent34450A.mode`. """
                                       )
    frequency_current_range = Instrument.control(
        ":SENS:FREQ:CURR:RANG?", ":SENS:FREQ:CURR:RANG:AUTO 0;:SENS:FREQ:CURR:RANG %s",
        """ A property that controls the current range in Amps for frequency on AC current
        measurements, which can take values 10E-3, 100E-3, 1, 10, as well as "MIN",
        "MAX", or "DEF" (100 mA).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[10E-3, 100E-3, 1, 10, "MIN", "MAX", "DEF"]
    )
    frequency_current_auto_range = Instrument.control(
        ":SENS:FREQ:CURR:RANG:AUTO?", ":SENS:FREQ:CURR:RANG:AUTO %d",
        """ Boolean property that toggles auto ranging for AC current in frequency measurements.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    frequency_voltage_range = Instrument.control(
        ":SENS:FREQ:VOLT:RANG?", ":SENS:FREQ:VOLT:RANG:AUTO 0;:SENS:FREQ:VOLT:RANG %s",
        """ A property that controls the voltage range in Volts for frequency on AC voltage
        measurements, which can take values 100E-3, 1, 10, 100, 750,
        as well as "MIN", "MAX", or "DEF" (10 V).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[100E-3, 1, 10, 100, 750, "MAX", "MIN", "DEF"]
    )
    frequency_voltage_auto_range = Instrument.control(
        ":SENS:FREQ:VOLT:RANG:AUTO?", ":SENS:FREQ:VOLT:RANG:AUTO %d",
        """Boolean property that toggles auto ranging for AC voltage in frequency measurements. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )
    frequency_aperture = Instrument.control(
        ":SENS:FREQ:APER?", ":SENS:FREQ:APER %s",
        """ A property that controls the frequency aperture in seconds,
        which sets the integration period and measurement speed. Takes values
        100 ms, 1 s, as well as "MIN", "MAX", or "DEF" (1 s). """,
        validator=strict_discrete_set,
        values=[100E-3, 1, "MIN", "MAX", "DEF"]
    )

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(
        ":READ?",
        """ Reads a temperature measurement in Celsius, based on the active :attr:`~.Agilent34450A.mode`.
        """  # noqa: E501
    )

    #############
    # Diode (V) #
    #############

    diode = Instrument.measurement(
        ":READ?",
        """ Reads a diode measurement in Volts, based on the active :attr:`~.Agilent34450A.mode`.
        """
    )

    ###################
    # Capacitance (F) #
    ###################

    capacitance = Instrument.measurement(
        ":READ?",
        """ Reads a capacitance measurement in Farads, based on the active :attr:`~.Agilent34450A.mode`.
        """  # noqa: E501
    )
    capacitance_range = Instrument.control(
        ":SENS:CAP:RANG?", ":SENS:CAP:RANG:AUTO 0;:SENS:CAP:RANG %s",
        """ A property that controls the capacitance range
        in Farads, which can take values 1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6,
        1E-3, 10E-3, as well as "MIN", "MAX", or "DEF" (1E-6).
        Auto-range is disabled when this property is set. """,
        validator=strict_discrete_set,
        values=[1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 1E-3, 10E-3, "MAX", "MIN", "DEF"]
    )
    capacitance_auto_range = Instrument.control(
        ":SENS:CAP:RANG:AUTO?", ":SENS:CAP:RANG:AUTO %d",
        """ A boolean property that toggles auto ranging for capacitance. """,
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    ####################
    # Continuity (Ohm) #
    ####################

    continuity = Instrument.measurement(":READ?",
                                        """ Reads a continuity measurement in Ohms,
                                        based on the active :attr:`~.Agilent34450A.mode`. """
                                        )

    def __init__(self, adapter, name="HP/Agilent/Keysight 34450A Multimeter", **kwargs):
        super().__init__(
            adapter, name, timeout=10000, **kwargs
        )
        # Configuration changes can necessitate up to 8.8 secs (per datasheet)
        self.check_errors()

    def configure_voltage(self, voltage_range="AUTO", ac=False, resolution="DEF"):
        """ Configures the instrument to measure voltage.

        :param voltage_range: A voltage in Volts to set the voltage range.
                DC values can be 100E-3, 1, 10, 100, 1000, as well as "MIN", "MAX",
                "DEF" (10 V), or "AUTO". AC values can be 100E-3, 1, 10, 100, 750,
                as well as "MIN", "MAX", "DEF" (10 V), or "AUTO".
        :param ac: False for DC voltage, True for AC voltage
        :param resolution: Desired resolution, can be 3.00E-5, 2.00E-5,
                1.50E-6 (5 1/2 digits), as well as "MIN", "MAX", or "DEF" (1.50E-6).
        """
        if ac is True:
            self.mode = 'ac voltage'
            self.voltage_ac_resolution = resolution
            if voltage_range == "AUTO":
                self.voltage_ac_auto_range = True
            else:
                self.voltage_ac_range = voltage_range
        elif ac is False:
            self.mode = 'voltage'
            self.voltage_resolution = resolution
            if voltage_range == "AUTO":
                self.voltage_auto_range = True
            else:
                self.voltage_range = voltage_range
        else:
            raise TypeError('Value of ac should be a boolean.')

    def configure_current(self, current_range="AUTO", ac=False, resolution="DEF"):
        """ Configures the instrument to measure current.

        :param current_range: A current in Amps to set the current range.
                DC values can be 100E-6, 1E-3, 10E-3, 100E-3, 1, 10, as well as "MIN",
                "MAX", "DEF" (100 mA), or "AUTO". AC values can be 10E-3, 100E-3, 1, 10,
                as well as "MIN", "MAX", "DEF" (100 mA), or "AUTO".
        :param ac: False for DC current, and True for AC current
        :param resolution: Desired resolution, can be 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
                as well as "MIN", "MAX", or "DEF" (1.50E-6).
        """
        if ac is True:
            self.mode = 'ac current'
            self.current_ac_resolution = resolution
            if current_range == "AUTO":
                self.current_ac_auto_range = True
            else:
                self.current_ac_range = current_range
        elif ac is False:
            self.mode = 'current'
            self.current_resolution = resolution
            if current_range == "AUTO":
                self.current_auto_range = True
            else:
                self.current_range = current_range
        else:
            raise TypeError('Value of ac should be a boolean.')

    def configure_resistance(self, resistance_range="AUTO", wires=2, resolution="DEF"):
        """ Configures the instrument to measure resistance.

        :param resistance_range: A resistance in Ohms to set the resistance range, can be 100,
                1E3, 10E3, 100E3, 1E6, 10E6, 100E6, as well as "MIN", "MAX", "DEF" (1E3), or "AUTO".
        :param wires: Number of wires used for measurement, can be 2 or 4.
        :param resolution: Desired resolution, can be 3.00E-5, 2.00E-5, 1.50E-6 (5 1/2 digits),
                as well as "MIN", "MAX", or "DEF" (1.50E-6).
        """
        if wires == 2:
            self.mode = 'resistance'
            self.resistance_resolution = resolution
            if resistance_range == "AUTO":
                self.resistance_auto_range = True
            else:
                self.resistance_range = resistance_range
        elif wires == 4:
            self.mode = '4w resistance'
            self.resistance_4w_resolution = resolution
            if resistance_range == "AUTO":
                self.resistance_4w_auto_range = True
            else:
                self.resistance_4w_range = resistance_range
        else:
            raise ValueError("Incorrect wires value, Agilent 34450A only supports 2 or 4 wire"
                             "resistance measurement.")

    def configure_frequency(self, measured_from="voltage_ac",
                            measured_from_range="AUTO", aperture="DEF"):
        """ Configures the instrument to measure frequency.

        :param measured_from: "voltage_ac" or "current_ac"
        :param measured_from_range: range of measured_from. AC voltage can have ranges 100E-3,
                                    1, 10, 100, 750, as well as "MIN", "MAX", "DEF" (10 V),
                                    or "AUTO". AC current can have ranges 10E-3, 100E-3, 1, 10,
                                    as well as "MIN", "MAX", "DEF" (100 mA), or "AUTO".
        :param aperture: Aperture time in Seconds, can be 100 ms, 1 s, as well as "MIN", "MAX",
                        or "DEF" (1 s).
        """
        if measured_from == "voltage_ac":
            self.mode = "voltage frequency"
            if measured_from_range == "AUTO":
                self.frequency_voltage_auto_range = True
            else:
                self.frequency_voltage_range = measured_from_range
        elif measured_from == "current_ac":
            self.mode = "current frequency"
            if measured_from_range == "AUTO":
                self.frequency_current_auto_range = True
            else:
                self.frequency_current_range = measured_from_range
        else:
            raise ValueError('Incorrect value for measured_from parameter. Use '
                             '"voltage_ac" or "current_ac".')
        self.frequency_aperture = aperture

    def configure_temperature(self):
        """ Configures the instrument to measure temperature.
        """
        self.mode = 'temperature'

    def configure_diode(self):
        """ Configures the instrument to measure diode voltage.
        """
        self.mode = 'diode'

    def configure_capacitance(self, capacitance_range="AUTO"):
        """ Configures the instrument to measure capacitance.

        :param capacitance_range: A capacitance in Farads to set the capacitance range, can be
                                    1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 1E-3, 10E-3,
                                    as well as "MIN", "MAX", "DEF" (1E-6), or "AUTO".
        """
        self.mode = 'capacitance'
        if capacitance_range == "AUTO":
            self.capacitance_auto_range = True
        else:
            self.capacitance_range = capacitance_range

    def configure_continuity(self):
        """ Configures the instrument to measure continuity.
        """
        self.mode = 'continuity'

    def beep(self):
        """ Sounds a system beep.
        """
        self.write(":SYST:BEEP")

    def _conf_parser(self, conf_values):
        """
        Parse the string of configuration parameters read from Agilent34450A with
        command ":configure?" and returns a list of parameters.

        Use cases:

        ['"CURR +1.000000E-01', '+1.500000E-06"'] from Instrument.measurement or Instrument.control
        '"CURR +1.000000E-01,+1.500000E-06"'      from Instrument.ask

        becomes

        ["CURR", +1000000E-01, +1.500000E-06]
        """
        # If not already one string, get one string

        if isinstance(conf_values, list):
            one_long_string = ', '.join(map(str, conf_values))
        else:
            one_long_string = conf_values

        # Split string in elements
        list_of_elements = re.split(r'["\s,]', one_long_string)

        # Eliminate empty string elements
        list_without_empty_elements = list(filter(lambda v: v != '', list_of_elements))

        # Convert numbers from str to float, where applicable
        for i, v in enumerate(list_without_empty_elements):
            try:
                list_without_empty_elements[i] = float(v)
            except ValueError as e:
                log.error(e)

        return list_without_empty_elements
