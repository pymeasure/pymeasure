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
    truncated_discrete_set, strict_discrete_set,
    truncated_range
)
from time import sleep
import numpy as np
import re


class Yokogawa7651(Instrument):
    """ Represents the Yokogawa 7651 Programmable DC Source
    and provides a high-level for interacting with the instrument.

    .. code-block:: python

        yoko = Yokogawa7651("GPIB::1")

        yoko.apply_current()                # Sets up to source current
        yoko.source_current_range = 10e-3   # Sets the current range to 10 mA
        yoko.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        yoko.source_current = 0             # Sets the source current to 0 mA

        yoko.enable_source()                # Enables the current output
        yoko.ramp_to_current(5e-3)          # Ramps the current to 5 mA

        yoko.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    @staticmethod
    def _find(v, key):
        """ Returns a value by parsing a current panel setting output
        string array, which is returned with a call to "OS;E". This
        is used for Instrument.control methods, and should not be
        called directly by the user.
        """
        status = ''.join(v.split("\r\n\n")[1:-1])
        keys = re.findall(r'[^\dE+.-]+', status)
        values = re.findall(r'[\dE+.-]+', status)
        if key not in keys:
            raise ValueError("Invalid key used to search for status of Yokogawa 7561")
        else:
            return values[keys.index(key)]

    source_voltage = Instrument.control(
        "OD;E", "S%g;E",
        """ A floating point property that controls the source voltage
        in Volts, if that mode is active. """
    )
    source_current = Instrument.control(
        "OD;E", "S%g;E",
        """ A floating point property that controls the source current
        in Amps, if that mode is active. """
    )
    source_voltage_range = Instrument.control(
        "OS;E", "R%d;E",
        """ A floating point property that sets the source voltage range
        in Volts, which can take values: 10 mV, 100 mV, 1 V, 10 V, and 30 V.
        Voltages are truncted to an appropriate value if needed. """,
        validator=truncated_discrete_set,
        values={10e-3:2, 100e-3:3, 1:4, 10:5, 30:6},
        map_values=True,
        get_process=lambda v: int(Yokogawa7651._find(v, 'R'))
    )
    source_current_range = Instrument.control(
        "OS;E", "R%d;E",
        """ A floating point property that sets the current voltage range
        in Amps, which can take values: 1 mA, 10 mA, and 100 mA.
        Currents are truncted to an appropriate value if needed. """,
        validator=truncated_discrete_set,
        values={1e-3:4, 10e-3:5, 100e-3:6},
        map_values=True,
        get_process=lambda v: int(Yokogawa7651._find(v, 'R'))
    )
    source_mode = Instrument.control(
        "OS;E", "F%d;E",
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. The convenience methods
        :meth:`~.Yokogawa7651.apply_current` and :meth:`~.Yokogawa7651.apply_voltage`
        can also be used. """,
        validator=strict_discrete_set,
        values={'current':5, 'voltage':1},
        map_values=True,
        get_process=lambda v: int(Yokogawa7651._find(v, 'F'))
    )
    compliance_voltage = Instrument.control(
        "OS;E", "LV%g;E",
        """ A floating point property that sets the compliance voltage
        in Volts, which can take values between 1 and 30 V. """,
        validator=truncated_range,
        values=[1, 30],
        get_process=lambda v: int(Yokogawa7651._find(v, 'LV'))
    )
    compliance_current = Instrument.control(
        "OS;E", "LA%g;E",
        """ A floating point property that sets the compliance current
        in Amps, which can take values from 5 to 120 mA. """,
        validator=truncated_range,
        values=[5e-3, 120e-3],
        get_process=lambda v: float(Yokogawa7651._find(v, 'LA'))*1e-3, # converts A to mA
        set_process=lambda v: v*1e3, # converts mA to A
    )

    def __init__(self, adapter, **kwargs):
        super(Yokogawa7651, self).__init__(
            adapter, "Yokogawa 7651 Programmable DC Source", **kwargs
        )

        self.write("H0;E") # Set no header in output data

    @property
    def id(self):
        """ Returns the identification of the instrument """
        return self.ask("OS;E").split('\r\n\n')[0]

    @property
    def source_enabled(self):
        """ Reads a boolean value that is True if the source is enabled,
        determined by checking if the 5th bit of the OC flag is a binary 1.
        """
        oc = int(self.ask("OC;E")[5:])
        return oc & 0b10000

    def enable_source(self):
        """ Enables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("O1;E")

    def disable_source(self):
        """ Disables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("O0;E")

    def apply_current(self, max_current=1e-3, complinance_voltage=1):
        """ Configures the instrument to apply a source current, which can
        take optional parameters that defer to the :attr:`~.Yokogawa7651.source_current_range`
        and :attr:`~.Yokogawa7651.compliance_voltage` properties. """
        self.source_mode = 'current'
        self.source_current_range = max_current
        self.complinance_voltage = complinance_voltage

    def apply_voltage(self, max_voltage=1, complinance_current=10e-3):
        """ Configures the instrument to apply a source voltage, which can
        take optional parameters that defer to the :attr:`~.Yokogawa7651.source_voltage_range`
        and :attr:`~.Yokogawa7651.compliance_current` properties. """
        self.source_mode = 'voltage'
        self.source_voltage_range = max_voltage
        self.complinance_current = compliance_current

    def ramp_to_current(self, current, steps=25, duration=0.5):
        """ Ramps the current to a value in Amps by traversing a linear spacing
        of current steps over a duration, defined in seconds.

        :param steps: A number of linear steps to traverse
        :param duration: A time in seconds over which to ramp
        """
        start_current = self.source_current
        stop_current = current
        pause = duration/steps
        if (start_current != stop_current):
            currents = np.linspace(start_current, stop_current, steps)
            for current in currents:
                self.source_current = current
                sleep(pause)

    def ramp_to_voltage(self, voltage, steps=25, duration=0.5):
        """ Ramps the voltage to a value in Volts by traversing a linear spacing
        of voltage steps over a duration, defined in seconds.

        :param steps: A number of linear steps to traverse
        :param duration: A time in seconds over which to ramp
        """
        start_voltage = self.source_voltage
        stop_voltage = voltage
        pause = duration/steps
        if (start_voltage != stop_voltage):
            voltages = np.linspace(start_voltage, stop_voltage, steps)
            for voltage in voltages:
                self.source_voltage = voltage
                sleep(pause)

    def shutdown(self):
        """ Shuts down the instrument, and ramps the current or voltage to zero
        before disabling the source. """

        # Since voltage and current are set the same way, this
        # ramps either the current or voltage to zero
        self.ramp_to_current(0.0, steps=25)
        self.source_current = 0.0
        self.disable_source()
        super(Yokogawa7651, self).shutdown()
