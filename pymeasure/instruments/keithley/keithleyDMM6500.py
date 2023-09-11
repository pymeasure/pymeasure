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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import (
    truncated_range,
    truncated_discrete_set,
    strict_discrete_set,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

BOOL_MAPPINGS = {True: 1, False: 0}

class ScannerCard2000Channel(Channel):

    MODES = {
        "voltage": "VOLT:DC",
        "voltage ac": "VOLT:AC",
        "resistance": "RES",
        "resistance 4W": "FRES",
        "diode": "DIOD",
        "capacitance": "CAP",
        "temperature": "TEMP",
        "continuity": "CONT",
        "period": "PER:VOLT",
        "frequency": "FREQ:VOLT",
        "voltage ratio": "VOLT:DC:RAT",
        "NONE": "NONE",
    }

    mode = Channel.control(
        ":SENS:FUNC? (@{ch})",
        ':SENS:FUNC "%s", (@{ch})',
        """ Control the configuration mode for measurements, which can take the values:
        ``current`` (DC), ``current ac``,
        ``voltage`` (DC),  ``voltage ac``,
        ``resistance`` (2-wire), ``resistance 4W`` (4-wire),
        ``diode``, ``capacitance``,
        ``temperature``, ``continuity``,
        ``period``, ``frequency``,
        and ``voltage ratio``.
        """,
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', ""),
    )

    nplc = Channel.control(
        "{function}:NPLC? (@{ch})",
        "{function}:NPLC %s, (@{ch})",
        """ Control the integration time in number of power line cycles (NPLC).
            Valid values: 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz)
            This command is valid only for ``voltage``, 2-wire ohms, and 4-wire ohms.

            .. note::

                Only ``voltage``, ``current``, ``resistance``, ``resistance 4W``, ``diode``,
                ``temperature``, and ``voltage ratio`` mode support NPLC setting. If current
                active mode doesn't support NPLC, this command will hang till adapter's
                timeout and cause -113 "Undefined header" error.

        """,
        validator=truncated_range,
        values=[0.0005, 15],
    )

    range_ = Instrument.control(
        "{function}:RANG? (@{ch})",
        "{function}:RANG %s, (@{ch})",
        """ Control measuring range for currently active mode. For ``frequency`` and ``period``
        measurements, :attr:`range_` applies to the signal's input voltage, not its frequency""",
    )

    autorange_enabled = Instrument.control(
        "{function}:RANG:AUTO? (@{ch})",
        "{function}:RANG:AUTO %d, (@{ch})",
        """ Control the autorange state for currently active mode.

        .. note::

            If current active mode doesn't support autorange, this command will hang
            till adapter's timeout and cause -113 "Undefined header" error.

        """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    def _mode_command(self, mode=None):
        """ Get SCPI's function name from mode."""
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    def enable_filter(self, mode=None, type="repeat", count=1):
        """ Enable the averaging filter for the active mode, or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode
        :param type: The type of averaging filter, could be ``REPeat``, ``MOVing``, or ``HYBRid``.
        :param count: A number of averages, which can take take values from 1 to 100

        :return: Filter status read from the instrument
        """
        mode_cmd = self._mode_command(mode)
        self.write(f":SENS:{mode_cmd}:AVER:STAT 1, (@{self.id})")
        self.write(f":SENS:{mode_cmd}:AVER:TCON {type}, (@{self.id})")
        self.write(f":SENS:{mode_cmd}:AVER:COUN {count}, (@{self.id})")
        return self.ask(f":SENS:{mode_cmd}:AVER:STAT? (@{self.id})")

    def disable_filter(self, mode=None):
        """ Disable the averaging filter for the active mode, or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode

        :return: Filter status read from the instrument
        """
        mode_cmd = self._mode_command(mode)
        self.write(f":SENS:{mode_cmd}:AVER:STAT 0, (@{self.id})")
        return self.ask(f":SENS:{mode_cmd}:AVER:STAT? (@{self.id})")

    def write(self, command):
        """ Write a command to the instrument."""
        if "{function}" in command:
            super().write(command.format(function = ScannerCard2000Channel.MODES[self.mode]))
        else:
            super().write(command)


class KeithleyDMM6500(Instrument):
    """ Represent the Keithely DMM6500 6½-Digit Multimeter and provide a
    high-level interface for interacting with the instrument.
    This class only uses "SCPI" command set (see also :attr:`command_set`) to
    communicate with the instrument.

    .. code-block:: python

        # Access via LAN
        ip_address = "xxx.xxx.xxx.xxx"
        dmm = KeithleyDMM6500(f"TCPIP::{ip_address}::inst0::INSTR")


    User can also use PyVISA to get DMM6500's USB port name and pass it to :class:`KeithleyDMM6500`

    .. code-block:: python

        import pyvisa
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()

        # assume there is only one USB instruments
        # Ex. ('USB0::1510::25856::01234567::0::INSTR')

        dmm = KeithleyDMM6500( resources[0] )

        # Measure voltage
        dmm.measure_voltage()
        print(dmm.voltage)

        # Measure AC voltage
        dmm.measure_voltage(ac=True)
        print(dmm.voltage)
    """

    MODES = {
        "voltage": "VOLT:DC",
        "voltage ac": "VOLT:AC",
        "current": "CURR:DC",
        "current ac": "CURR:AC",
        "resistance": "RES",
        "resistance 4W": "FRES",
        "diode": "DIOD",
        "capacitance": "CAP",
        "temperature": "TEMP",
        "continuity": "CONT",
        "period": "PER:VOLT",
        "frequency": "FREQ:VOLT",
        "voltage ratio": "VOLT:DC:RAT",
    }

    MODES_HAVE_AUTORANGE = (
        "current",
        "current ac",
        "voltage",
        "voltage ac",
        "resistance",
        "resistance 4W",
        "capacitance",
        "voltage ratio",
    )

    channels = Instrument.MultiChannelCreator(ScannerCard2000Channel, list(range(1, 11)))

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "Keithley DMM6500 6½-Digit Multimeter",
                         read_termination = "\n", **kwargs)

    def __exit__(self, exc_type, exc_value, traceback):
        """ Fully close the connection when the `with` code block finishes."""
        self.adapter.close()

    def close(self):
        """ Close the connection"""
        self.adapter.close()

    ###########
    # General #
    ###########

    command_set = Instrument.control(
        "*LANG?",
        "*LANG %s",
        """ Control the command set that to use with DMM6500. Reboot the instrument is needed
        after changing the command set. Available values are:
        :code:`SCPI`, :code:`TSP`, :code:`SCPI2000`, and :code:`SCPI34401`.
        The :attr:`KeithleyDMM6500` class was designed to use :code:`SCPI` command set only.
        """,
        validator=strict_discrete_set,
        values=["TSP", "SCPI", "SCPI2000", "SCPI34401"],
    )
    mode = Instrument.control(
        ":SENS:FUNC?",
        ':SENS:FUNC "%s"',
        """ Control the active measure function. Available values are:
        ``current`` (DC), ``current ac``, ``voltage`` (DC),  ``voltage ac``,
        ``resistance`` (2-wire), ``resistance 4W`` (4-wire),
        ``diode``, ``capacitance``, ``temperature``, ``continuity``,
        ``period``, ``frequency``, and ``voltage ratio``.
        """,
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', ""),
    )

    line_frequency = Instrument.measurement(
        ":SYST:LFR?",
        """ Get the power line frequency which automatically detected while the instrument is
        powered on.""",
    )

    range_ = Instrument.control(
        "{function}:RANG?",
        "{function}:RANG %s",
        """ Control the positive full-scale measure range for currently active mode.

        For frequency and period measurements, ranging applies to
        the signal's input voltage, not its frequency""",
    )

    autorange_enabled = Instrument.control(
        "{function}:RANG:AUTO?",
        "{function}:RANG:AUTO %d",
        """ Control the autorange state for currently active mode.

        .. note::

            If currently active mode doesn't support autorange, this command will hang
            till adapter's timeout and cause -113 "Undefined header" error.

        """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    nplc = Instrument.control(
        "{function}:NPLC?",
        "{function}:NPLC %s",
        """ Control the integration time in number of power line cycles (NPLC).
        Valid values are: 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz)

        .. note::

            Only ``voltage``, ``current``, ``resistance``, ``resistance 4W``, ``diode``,
            ``temperature``, and ``voltage ratio`` mode support NPLC setting. If current
            active mode doesn't support NPLC, this command will hang till adapter's timeout
            and cause -113 "Undefined header" error.

        """,
        validator=truncated_range,
        values=[0.0005, 15],
    )

    aperture = Instrument.control(
        "{function}:APER?",
        "{function}:APER %s",
        """ Control the aperture time of currently active mode.

        Valid values: ``MIN``, ``DEF``, ``MAX``, or number between 8.333u and 0.25 s.

        .. note::

            Only ``voltage``, ``current``, ``resistance``, ``resistance 4W``, ``diode``,
            ``temperature``, ``frequency``, ``period``, and ``voltage ratio`` mode support
            aperture setting. If current active mode doesn't support aperture, this command
            will hang till adapter's timeout and cause -113 "Undefined header" error.

        """,
    )

    relative_enabled = Instrument.control(
        "{function}:REL:STAT?",
        "{function}:REL:STAT %g",
        """ Control the relative offset value applied to new measurements of currently
        active mode.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    detector_bandwidth = Instrument.control(
        "{function}:DET:BAND?",
        "{function}:DET:BAND %s",
        """ Control the lowest frequency expected in the input signal in Hz
        ONLY for AC voltage and AC current measurement,

        Valid values: 3, 30, 300, ``MIN``, ``DEF``, ``MAX``.""",
        validator=strict_discrete_set,
        values=[3, 30, 300, "MIN", "DEF", "MAX"],
    )

    autozero_enabled = Instrument.control(
        "{function}:AZER?",
        "{function}:AZER %s",
        """ Control automatic updates to the internal reference measurements (autozero)
        of the instrument.
        """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    system_time = Instrument.control(
        ":SYST:TIME? 1",
        ":SYST:TIME %s",
        """ Control system time on the instrument.
        Format of set is: ``year, month, day, hour, minute, second`` or ``hour, minute, second``.
        Example: Using ``time`` package to set instrument's clock:
        ``dmm.system_time = time.strftime("%Y, %m, %d, %H, %M, %S")``
        """,
    )

    def trigger_single_autozero(self):
        """ Cause the instrument to refresh the reference and zero measurements once.

        Consequent autozero measurements are disabled."""
        self.write("AZER:ONCE")

    terminals_used = Instrument.measurement(
        "ROUT:TERM?",
        """ Get which set of input and output terminals the instrument is using.
            Return can be ``FRONT`` or ``REAR``.""",
        values={"FRONT": "FRON", "REAR": "REAR"},
        map_values=True,
    )

    ###########
    # Display #
    ###########

    display_screen = Instrument.setting(
        ":DISP:SCR %s",
        """ Set displayed front-panel screen by the name. Available names are:
        ``HOME`` (home), ``HOME_LARG`` (home screen with large readings), ``READ`` (reading table),
        ``HIST`` (histogram), ``SWIPE_FUNC`` (FUNCTIONS swipe screen),
        ``SWIPE_GRAP`` (GRAPH swipe screen), ``SWIPE_SEC`` (SECONDARY swipe screen),
        ``SWIPE_SETT`` (SETTINGS swipe screen), ``SWIPE_STAT`` (STATISTICS swipe screen),
        ``SWIPE_USER`` (USER swipe screen), ``SWIPE_CHAN`` (CHANNEL swipe screen),
        ``SWIPE_NONS`` (NONSWITCH swipe screen),
        ``SWIPE_SCAN`` (SCAN swipe screen), ``CHANNEL_CONT`` (Channel control screen),
        ``CHANNEL_SETT`` (Channel settings screen), ``CHANNEL_SCAN`` (Channel scan screen),
        or ``PROC`` (minimal CPU resources).
        """,
        validator=strict_discrete_set,
        values=(
            "HOME",
            "HOME_LARG",
            "READ",
            "HIST",
            "SWIPE_FUNC",
            "SWIPE_GRAP",
            "SWIPE_SEC",
            "SWIPE_SETT",
            "SWIPE_STAT",
            "SWIPE_USER",
            "SWIPE_CHAN",
            "SWIPE_NONS",
            "SWIPE_SCAN",
            "CHANNEL_CONT",
            "CHANNEL_SETT",
            "CHANNEL_SCAN",
            "PROC",
        ),
    )

    def displayed_text(self, top_line=None, bot_line=None):
        """ Display text messages on the front-panel USER swipe screen.
        If no messages were defined, screen will be cleared.

        :param top_line: 1st line message
        :param bot_line: 2nd line message

        :return: None
        """
        self.write(":DISP:CLE")
        self.display_screen = "SWIPE_USER"
        if top_line:
            self.write(f':DISP:USER1:TEXT "{top_line}"')
        if bot_line:
            self.write(f':DISP:USER2:TEXT "{bot_line}"')

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":READ?",
        """ Measure a DC or AC current measurement in Amps, based on the
        active :attr:`mode`. """,
    )
    current_range = Instrument.control(
        ":SENS:CURR:RANG?",
        ":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ Control the DC current full-scale measure range in Amps.
        Available ranges are 10e-6, 100e-6, 1e-3, 10e-3, 100e-3, 1, 3 Amps (for front terminals),
        and 10 Amps (for rear terminals). Auto-range is disabled when this property is set. """,
        validator=truncated_discrete_set,
        values=[10e-6, 100e-6, 1e-3, 10e-3, 100e-3, 1, 3, 10],
    )
    current_relative = Instrument.control(
        ":SENS:CURR:REL?",
        ":SENS:CURR:REL %g",
        """ Control the DC current relative value in Amps (float strictly from -3 to 3).
        When relative offset is enabled, all subsequent measured readings are offset by
        the value that is set for this command.
        If the instrument acquires the value, read this setting to return the value that
        was measured internally. """,
        validator=truncated_range,
        values=[-3.0, 3.0],
    )
    current_relative_enabled = Instrument.control(
        ":SENS:CURR:REL:STAT?",
        ":SENS:CURR:REL:STAT %g",
        """ Control a relative offset value applied to current measurement.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )
    current_nplc = Instrument.control(
        ":SENS:CURR:NPLC?",
        ":SENS:CURR:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )
    current_digits = Instrument.control(
        ":DISP:CURR:DIG?",
        ":DISP:CURR:DIG %d",
        """ An integer property that determines the number of digits in the DC current
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )

    # Current (AC)
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?",
        ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %g",
        """ A floating point property that controls the AC current range in
        Amps, which can take values from 0 to 3 A, and 10 A (available for rear terminals).
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 10],
    )
    current_ac_relative = Instrument.control(
        ":SENS:CURR:AC:REL?",
        ":SENS:CURR:AC:REL %g",
        """ A floating point property that controls the DC current relative value in Amps,
        which can take values from -3.0 to 3.0 A. When relative offset is enabled, all
        subsequent measured readings are offset by the value that is set for this command.
        If the instrument acquires the value, read this setting to return the value that
        was measured internally. """,
        validator=truncated_range,
        values=[-3.0, 3.0],
    )
    current_ac_relative_status = Instrument.control(
        ":SENS:CURR:AC:REL:STAT?",
        ":SENS:CURR:AC:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    current_ac_nplc = Instrument.control(
        ":SENS:CURR:AC:NPLC?",
        ":SENS:CURR:AC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the AC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.01 to 10, where 0.1, 1, and 10 are
        Fast, Medium, and Slow respectively. """,
    )
    current_ac_digits = Instrument.control(
        ":DISP:CURR:AC:DIG?",
        ":DISP:CURR:AC:DIG %d",
        """ An integer property that determines the number of digits in the AC current
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[4, 5, 6, 7],
        cast=int,
    )
    current_ac_bandwidth = Instrument.control(
        ":SENS:CURR:AC:DET:BAND?",
        ":SENS:CURR:AC:DET:BAND %g",
        """ A floating point property that sets the AC current detector
        bandwidth in Hz, which can take the values 3, 30, and 300 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 30, 300],
    )

    def measure_current(self, max_current=10e-3, ac=False):
        """ Configure the instrument to measure current,
        based on a maximum current to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_current: A current in Volts to set the current range
        :param ac: False for DC current, and True for AC current
        """
        if ac:
            self.mode = "current ac"
            self.current_ac_range = max_current
        else:
            self.mode = "current"
            self.current_range = max_current

    ###############
    # Voltage (V) #
    ###############

    # DC
    voltage = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC voltage measurement in Volts, based on the
        active :attr:`mode`. """,
    )
    voltage_range = Instrument.control(
        ":SENS:VOLT:RANG?",
        ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG %g",
        """ A floating point property that controls the DC voltage range in
        Volts, which can take values from 0 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_discrete_set,
        values=[0.1, 1, 10, 100, 1000],
    )
    voltage_relative = Instrument.control(
        ":SENS:VOLT:REL?",
        ":SENS:VOLT:REL %g",
        """ A floating point property that controls the DC voltage relative value in Volts,
        which can take values from -1000 to 1000 V. When relative offset is enabled, all
        subsequent measured readings are offset by the value that is set for this command.
        If the instrument acquires the value, read this setting to return the value that
        was measured internally. """,
        validator=truncated_range,
        values=[-1000, 1000],
    )
    voltage_relative_status = Instrument.control(
        ":SENS:VOLT:REL:STAT?",
        ":SENS:VOLT:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    voltage_nplc = Instrument.control(
        ":SENS:VOLT:NPLC?",
        ":SENS:VOLT:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )
    voltage_digits = Instrument.control(
        ":DISP:VOLT:DIG?",
        ":DISP:VOLT:DIG %d",
        """ An integer property that controls the number of digits in the DC voltage
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )
    # AC
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?",
        ":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG %g",
        """ A floating point property that controls the AC voltage range in
        Volts, which can take values from 0 to 750 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_discrete_set,
        values=[0.1, 1, 10, 100, 750],
    )
    voltage_ac_relative = Instrument.control(
        ":SENS:VOLT:AC:REL?",
        ":SENS:VOLT:AC:REL %g",
        """ A floating point property that controls the AC voltage relative value in Volts,
        which can take values from -750 to 750 V. When relative offset is enabled, all
        subsequent measured readings are offset by the value that is set for this command.
        If the instrument acquires the value, read this setting to return the value that
        was measured internally. """,
        validator=truncated_range,
        values=[-750, 750],
    )
    voltage_ac_relative_status = Instrument.control(
        ":SENS:VOLT:AC:REL:STAT?",
        ":SENS:VOLT:AC:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    voltage_ac_nplc = Instrument.control(
        ":SENS:VOLT:AC:NPLC?",
        ":SENS:VOLT:AC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )
    voltage_ac_digits = Instrument.control(
        ":DISP:VOLT:AC:DIG?",
        ":DISP:VOLT:AC:DIG %d",
        """ An integer property that controls the number of digits in the DC voltage
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )
    voltage_ac_bandwidth = Instrument.control(
        ":SENS:VOLT:AC:DET:BAND?",
        ":SENS:VOLT:AC:DET:BAND %g",
        """ A floating point property that sets the AC voltage detector
        bandwidth in Hz, which can take the values  3, 30, and 300 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 30, 300],
    )

    def measure_voltage(self, max_voltage=1, ac=False):
        """ Configure the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if ac:
            self.mode = "voltage ac"
            self.voltage_ac_range = max_voltage
        else:
            self.mode = "voltage"
            self.voltage_range = max_voltage

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Reads a resistance measurement in Ohms for both 2-wire and 4-wire
        configurations, based on the active :attr:`mode`. """,
    )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?",
        ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ A floating point property that controls the 2-wire resistance range
        in Ohms, which can take values from 10 to 100 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_discrete_set,
        values=[10, 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6],
    )
    resistance_relative = Instrument.control(
        ":SENS:RES:REL?",
        ":SENS:RES:REL %g",
        """ A floating point property that controls the 2-wire resistance
        relative value in Ohms, which can take values from -100M to 100 MOhms. """,
        validator=truncated_range,
        values=[-1e8, 1e8],
    )
    resistance_relative_status = Instrument.control(
        ":SENS:RES:REL:STAT?",
        ":SENS:RES:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?",
        ":SENS:RES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the integration period
        and measurement speed.  Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )
    resistance_digits = Instrument.control(
        ":DISP:RES:DIG?",
        ":DISP:RES:DIG %d",
        """ An integer property that controls the number of digits in the 2-wire
        resistance readings, which can take values from 3 to 6 representing dispaly
        digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )
    resistance_4W_range = Instrument.control(
        ":SENS:FRES:RANG?",
        ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %g",
        """ A floating point property that controls the 4-wire resistance range
        in Ohms, which can take values from 1 to 120 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_discrete_set,
        values=[1, 10, 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6],
    )
    resistance_4W_relative = Instrument.control(
        ":SENS:FRES:REL?",
        ":SENS:FRES:REL %g",
        """ A floating point property that controls the 4-wire resistance
        reference value in Ohms, which can take values from -100M to 100 MOhms. """,
        validator=truncated_range,
        values=[-1e8, 1e8],
    )
    resistance_4W_relative_status = Instrument.control(
        ":SENS:FRES:REL:STAT?",
        ":SENS:FRES:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    resistance_4W_nplc = Instrument.control(
        ":SENS:FRES:NPLC?",
        ":SENS:FRES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 4-wire resistance measurements, which sets the integration period
        and measurement speed.  Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )
    resistance_4W_digits = Instrument.control(
        ":DISP:FRES:DIG?",
        ":DISP:FRES:DIG %d",
        """ An integer property that controls the number of digits in the 4-wire
        resistance readings, which can take values from 3 to 6 representing dispaly
        digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )

    def measure_resistance(self, max_resistance=10e6, wires=2):
        """ Configure the instrument to measure resistance,
        based on a maximum resistance to set the range.

        :param max_resistance: A resistance in Ohms to set the resistance range
        :type max_resistance: float
        :param wires: ``2`` for normal resistance, and ``4`` for 4-wires resistance
        :type wires: int
        """
        if wires == 2:
            self.mode = "resistance"
            self.resistance_range = max_resistance
        elif wires == 4:
            self.mode = "resistance 4W"
            self.resistance_4W_range = max_resistance
        else:
            raise ValueError("Keithley DMM6500 only supports 2 or 4 wire" "resistance meaurements.")

    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(
        ":READ?",
        """ Reads a frequency measurement in Hz, based on the
        active :attr:`mode`. """,
    )
    frequency_relative = Instrument.control(
        ":SENS:FREQ:REL?",
        ":SENS:FREQ:REL %g",
        """ A floating point property that controls the frequency relative
        value in Hz, which can take values from -1 MHz to 1 MHz. """,
        validator=truncated_range,
        values=[-1e6, 1e6],
    )
    frequency_relative_status = Instrument.control(
        ":SENS:FREQ:REL:STAT?",
        ":SENS:FREQ:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    frequency_digits = Instrument.control(
        ":DISP:FREQ:DIG?",
        ":DISP:FREQ:DIG %d",
        """ An integer property that controls the number of digits in the frequency
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )
    frequency_threshold = Instrument.control(
        ":SENS:FREQ:THR:RANG?",
        ":SENS:FREQ:THR:RANG %g",
        """ A floating point property that controls the expected input level in Volts
        for the frequency measurement, which can take values from 0.1 to 750 V. """,
        validator=truncated_range,
        values=[0.1, 750],
    )
    frequency_threshold_auto = Instrument.control(
        ":SENS:FREQ:THR:RANG:AUTO?",
        ":SENS:FREQ:THR:RANG:AUTO %g",
        """ A property that determines if the threshold range is set manually or automatically,
        which takes string :code:`on`, bool :code:`True`, or number :code:`1` for enabling;
        string :code:`off`, bool :code:`False`, or :code:`0` for disabling.""",
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    frequency_aperature = Instrument.control(
        ":SENS:FREQ:APER?",
        ":SENS:FREQ:APER %g",
        """ A floating point property that controls the frequency aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 2 ms to 273 ms.""",
        validator=truncated_range,
        values=[0.002, 0.273],
    )

    def measure_frequency(self):
        """ Configure the instrument to measure frequency."""
        self.mode = "frequency"

    ##############
    # Period (s) #
    ##############

    period = Instrument.measurement(
        ":READ?",
        """ Reads a period measurement in seconds, based on the
        active :attr:`mode`. """,
    )
    period_relative = Instrument.control(
        ":SENS:PER:REL?",
        ":SENS:PER:REL %g",
        """ A floating point property that controls the period relative value
        in seconds, which can take values from -1 to 1 s. """,
        validator=truncated_range,
        values=[-1, 1],
    )
    period_relative_status = Instrument.control(
        ":SENS:PER:REL:STAT?",
        ":SENS:PER:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    period_digits = Instrument.control(
        ":DISP:PER:DIG?",
        ":DISP:PER:DIG %d",
        """ An integer property that controls the number of digits in the period
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )
    period_threshold = Instrument.control(
        ":SENS:PER:THR:RANG?",
        ":SENS:PRE:THR:RANG %g",
        """ A floating point property that controls the voltage signal threshold
        level in Volts for the period measurement, which can take values
        from 0.1 to 750 V. """,
        validator=truncated_range,
        values=[0.1, 750],
    )
    period_threshold_auto = Instrument.control(
        ":SENS:PER:THR:RANG:AUTO?",
        ":SENS:PER:THR:RANG:AUTO %g",
        """ A property that determines if the threshold range is set manually or automatically,
        which takes string :code:`"on"`, bool :code:`True`, or number :code:`1` for enabling;
        string :code:`"off"`, bool :code:`False`, or :code:`0` for disabling.""",
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    period_aperature = Instrument.control(
        ":SENS:PER:APER?",
        ":SENS:PER:APER %g",
        """ A floating point property that controls the period aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 2 ms to 273 ms.""",
        validator=truncated_range,
        values=[0.002, 0.273],
    )

    def measure_period(self):
        """ Configure the instrument to measure period."""
        self.mode = "period"

    ###################
    # Temperature (C) #
    ###################

    temperature = Instrument.measurement(
        ":READ?",
        """ Reads a temperature measurement in Celsius, based on the
        active :attr:`mode`. """,
    )
    temperature_relative = Instrument.control(
        ":SENS:TEMP:REL?",
        ":SENS:TEMP:REL %g",
        """ A floating point property that controls the temperature relative value
        in Celsius, which can take values from -3310 to 3310 C. """,
        validator=truncated_range,
        values=[-3310, 3310],
    )
    temperature_relative_status = Instrument.control(
        ":SENS:TEMP:REL:STAT?",
        ":SENS:TEMP:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    temperature_nplc = Instrument.control(
        ":SENS:TEMP:NPLC?",
        ":SENS:TEMP:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the temperature measurements, which sets the integration period
        and measurement speed.  Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )
    temperature_digits = Instrument.control(
        ":DISP:TEMP:DIG?",
        ":DISP:TEMP:DIG %d",
        """ An integer property that controls the number of digits in the temperature
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )

    def measure_temperature(self):
        """ Configure the instrument to measure temperature."""
        self.mode = "temperature"

    ###############
    # Capacitance #
    ###############

    capacitance = Instrument.measurement(
        ":READ?",
        """ Reads a capacitance value in Farad,
        based on the active :attr:`mode`. """,
    )
    capacitance_relative = Instrument.control(
        ":SENS:CAP:REL?",
        ":SENS:CAP:REL %g",
        """ A floating point property that controls the temperature relative value
        in Farad, which can take values from -0.001 to 0.001 F. """,
        validator=truncated_range,
        values=[-0.001, 0.001],
    )
    capacitance_relative_status = Instrument.control(
        ":SENS:CAP:REL:STAT?",
        ":SENS:CAP:REL:STAT %g",
        """ A property queries, enables or disables the application of a relative offset value
        to the measurement. Takes string :code:`on|True|1` or :code:`off|False|0`. """,
        validator=strict_discrete_set,
        values={"on": 1, "off": 0, True: 1, False: 0, 1: 1, 0: 0},
        map_values=True,
    )
    capacitance_range = Instrument.control(
        ":SENS:CAP:RANG?",
        ":SENS:CAP:RANG:AUTO 0;:SENS:CURR:RANG %g",
        """ A floating point property that controls the capacitance range in
        Farad, which can take values from 1n to 1m F.
        Auto-range is disabled when this property is set. """,
        validator=truncated_discrete_set,
        values=[1e-9, 10e-9, 100e-9, 1e-6, 10e-6, 100e-6, 1e-3],
    )
    capacitance_digits = Instrument.control(
        ":DISP:CAP:DIG?",
        ":DISP:CAP:DIG %d",
        """ An integer property that determines the number of digits in the capacitance
        readings, which can take values from 3 to 6 representing dispaly digits from 3.5 to 6.5.""",
        validator=truncated_discrete_set,
        values=[3, 4, 5, 6],
        cast=int,
    )

    def measure_capacitance(self, max_capacitance=1e-3):
        """ Configure the instrument to measure capacitance.

        :param max_capacitance: Set :attr:`capacitance_range` after changing mode
        :return: None
        """
        self.mode = "capacitance"
        self.capacitance_range = max_capacitance

    #########
    # Diode #
    #########

    diode = Instrument.measurement(
        ":READ?",
        """ Reads a diode's forward voltage drop of general-purpose diodes and the
        Zener voltage of Zener diodes on the 10V range with a constant test current (bias level),
        based on the active :attr:`mode`. """,
    )
    diode_bias = Instrument.control(
        ":SENS:DIOD:BIAS:LEV?",
        ":SENS:DIOD:BIAS:LEV %g",
        """ A integer property that controls the amount of current the instrument sources
        when it makes measurements, which can take values from 1e-5 (10uA) to 0.01 (10mA).""",
        validator=truncated_discrete_set,
        values=[1e-5, 0.0001, 0.001, 0.01],
    )
    diode_nplc = Instrument.control(
        ":SENS:DIOD:NPLC?",
        ":SENS:DIOD:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the diode measurements, which sets the integration period
        and measurement speed. Takes values from 0.0005 to 15 (60Hz) or 12 (50Hz or 400Hz).""",
        validator=truncated_range,
        values=[0.0005, 15],
    )

    def measure_diode(self):
        """ Configure the instrument to perform diode testing.

        :return: None
        """
        self.mode = "diode"

    ##############
    # Continuity #
    ##############

    def measure_continuity(self):
        """ Configure the instrument to perform continuity testing.

        :return: None
        """
        self.mode = "continuity"

    ##########
    # Buffer #
    ##########
    # Main buffer fuctions are inherited from `KeithleyBuffer` class

    buffer_points = buffer_size = Instrument.control(
        ":TRAC:POIN?",
        ":TRAC:POIN %d",
        """ An integer property that controls the number of buffer points. This
        does not represent actual points in the buffer, but the configuration
        value instead. `0` means the largest buffer possib based on the available
        memory when the bufer is created.""",
        validator=truncated_range,
        values=[0, 6_000_000],
        cast=int,
    )

    points_in_buffer = Instrument.measurement(
        "TRAC:ACT?",
        """ Query the number of readings stored in the buffer.""",
        cast=int,
    )

    ###########
    # Formats #
    ###########

    data_format = Instrument.control(
        "FORMAT:DATA?",
        "FORMAT:DATA %s",
        """ A string property that specify data format: ``ASC``, ``REAL``, or ``SRE``""",
        validator=strict_discrete_set,
        values=("asc", "ASC", "real", "REAL", "sre", "SRE"),
    )

    ################
    # Scanner Card #
    ################

    scan_id = Instrument.measurement(
        ":SYST:CARD1:IDN?",
        """ Return a string that contains information about the scanner card""",
        separator="|",
    )

    scan_vch_start = Instrument.measurement(
        "SYST:CARD1:VCH:STAR?",
        """ Return the first channel in the slot that supports voltage or 2-wire measurements""",
        cast=int,
    )

    scan_vch_end = Instrument.measurement(
        "SYST:CARD1:VCH:END?",
        """ Return the last channel in the slot that supports voltage or 2-wire measurements""",
        cast=int,
    )

    scan_card_vmax = Instrument.measurement(
        "SYST:CARD1:VMAX?", """ Return the maximum voltage of all channels.""", cast=int
    )

    enable_pseudo_scanner = Instrument.setting(
        ":SYST:PCAR1 %d",
        """ Enable or disable pseudo scanner card. After setting, user can check
        current scanner card by :attr:`scan_id`. If a scanner card is installed,
        this setting won't have any effect.""",
        validator=strict_discrete_set,
        values={True: 2000, False: 0},
        map_values=True,
    )

    scan_channels = Instrument.control(
        ":ROUT:SCAN:CRE?",
        ":ROUT:SCAN:CRE (@%s)",
        """ A channel list string property that deletes the existing scan list and
        creates a new list of channels to scan. An empty string will clear the list.
        Use comma to separate single channel and use a colon to separate the first
        and last channel in the list.
        Examples: ``1``, ``1,3,5``, ``1:2, 7:8``, or ``1:10``.
        """,
        get_process=lambda x: x[-1].replace(")", ""),
        separator="@",
    )

    @property
    def scan_channels_list(self):
        """ Expand :attr:`scan_channels` string to a list of integers.

        For example, when :attr:`scan_channels` is ``1,3:5,7:8,10``,
        this attribute will return ``[1,3,4,5,7,8,10]``. If ``scan_channels_list=[1,2,3,4,6]``,
        the :attr:`scan_channels` will be ``1:4,6``.
        """
        chan_str = self.scan_channels
        # Trans string to list of int, ex. "1,3:5,7:8,10" -> [1,3,4,5,7,8,10]
        chn_list = chan_str.split(",")
        for idx, ch in enumerate(chn_list):
            try:
                chn_list[idx] = int(ch)
            except ValueError:
                # process string "a:b" -> a, a+1, ..., b
                ch = list(map(int, ch.split(":")))
                ch[-1] += 1
                chn_list[idx: idx+1] = list(range(*ch))
        return chn_list

    @scan_channels_list.setter
    def scan_channels_list(self, new_channels):
        """ Set scan channels by a list or tuple."""
        if isinstance(new_channels, (list, tuple)):
            self.scan_channels = ",".join(map(str, new_channels))
        else:
            log.error("Not an acceptable list")

    scan_count = Instrument.control(
        ":ROUT:SCAN:COUN:SCAN?",
        ":ROUT:SCAN:COUN:SCAN %d",
        """ An int property that sets the number of times the scan is repeated.""",
        cast=int,
    )

    scan_interval = Instrument.control(
        ":ROUT:SCAN:INT?",
        ":ROUT:SCAN:INT %d",
        """ The interval time (0s to 100ks) between scan starts when the scan count
        is more than one.""",
        validator=truncated_range,
        values=[0, 100e3],
        cast=int,
    )

    def scanned_data(self, start_idx=None, end_idx=None, raw=False):
        """ Return a list of scanning values from the buffer.

        :param start_idx: A bool value which controls communication state while scanning.
            Default is ``True`` and the communication waits until the commands are complete
            to accept new commands
        :param end_idx: An alternative way to set :attr:`scan_count`
        :param raw: An alternative way to set :attr:`scan_interval` in second
        :return: A list of scan channels' measuredh
        :rtype: A list of channels' list
        """
        self.write(":FORM:DATA ASCII")
        if start_idx is None:
            start_idx = self.ask(":TRAC:ACT:STAR?")
        if end_idx is None:
            end_idx = self.ask(":TRAC:ACT:END?")
        data = self.values(f":TRAC:DATA? {start_idx}, {end_idx}")
        if raw:
            return data
        else:
            nums = len(self.scan_channels_list)
            # re-organize data to 2D list
            return [data[i::nums] for i in range(nums)]

    @property
    def scan_modes(self):
        """ Return a dictionary of every channel's mode."""
        res = dict()
        for i in range(self.scan_vch_start, self.scan_vch_end + 1):
            res[i] = self.channels[i].mode
        return res

    @scan_modes.setter
    def scan_modes(self, new_mode):
        """ Set all channles to the new mode. Ex: ``scan_modes = "voltage"``"""
        self.write(f':SENS:FUNC "{self._mode_command(new_mode)}", (@1:10)')

    @property
    def scan_iscomplete(self):
        """ Read Event Status Register (ESR) bit 0 to determine if previous works were
        completed.
        This properity is used while running time-consuming scanning operation."""
        res = int(self.ask("*ESR?")) & 1
        if res == 1:
            return True
        else:
            return False

    def scan_start(self, block_communication=True, count=None, interval=None):
        """ Start the scanner card to close each channel of :attr:`scan_channels` sequentially
        and to do measurements.

        If :attr:`scan_count` is larger than 1, the next scanning will start again
        after :attr:`scan_interval` seceond. Running large counts or long interval scanning
        is a time-consuming operation. It's better to set ``block_communication=False`` and
        use :attr:`scan_iscomplete` to check if the measurement is completed.

        :param block_communication: A bool value which controls communication state while
            scanning. Default is ``True`` and the communication waits until the commands
            are complete to accept new commands
        :param count: An alternative way to set :attr:`scan_count` before scanning.
        :param interval: An alternative way to set :attr:`scan_interval` in second before
            scanning.
        :return: None
        """
        if count:
            self.scan_count = count
        if interval:
            self.scan_interval = interval
        self.clear()
        if block_communication:
            self.write(":INIT;*WAI")
            log.info("Enable blocking communication.")
        else:
            self.write(":INIT")
            self.write("*OPC")
            log.info("Enable non-blocking communication.")
            log.info("Use `scan_iscomplete` to know the status.")

    def scan_stop(self):
        """ Abort the scanning measurement by stopping the measurement arming and
        triggering sequence.

        :return: None
        """
        self.write(":ABOR")

    ##########
    # Common #
    ##########

    def _mode_command(self, mode=None):
        """ Get SCPI's function name from mode."""
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    def auto_range_status(self, mode=None):
        """ Get the status of auto-range of active mode or another mode by its name.
        Only ``current`` (DC), ``current ac``, ``voltage`` (DC),  ``voltage ac``,
        ``resistance`` (2-wire), ``resistance 4W`` (4-wire), ``capacitance``,
        and ``voltage ratio`` support autorange. If chosen mode is not in these
        modes, this command will also return ``False``.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode
        :return: a bool value for auto-range enabled or disabled
        :rtype: bool

        """
        if mode is None:
            mode = self.mode
        if mode in self.MODES_HAVE_AUTORANGE:
            value = self.ask(f":SENS:{self._mode_command(mode)}:RANG:AUTO?")
            if value == "1":
                return True
            else:
                return False
        else:
            return False

    def auto_range(self, mode=None):
        """ Set the active mode to use auto-range, or can set another mode by its name.

        Only ``current`` (DC), ``current ac``, ``voltage`` (DC),  ``voltage ac``,
        ``resistance`` (2-wire), ``resistance 4W`` (4-wire), ``capacitance``,
        and ``voltage ratio`` support autorange. If chosen mode is not in these
        modes, this command will do nothing.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode

        """
        if mode is None:
            mode = self.mode
        if mode in self.MODES_HAVE_AUTORANGE:
            self.write(f":SENS:{self._mode_command(mode)}:RANG:AUTO 1")

    def enable_relative(self, mode=None):
        """ Enable the application of a relative offset value to the measurement
        for the active mode, or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode
        """
        self.write(f":SENS:{self._mode_command(mode)}:REL:STAT 1")

    def disable_relative(self, mode=None):
        """ Disable the application of a relative offset value to the measurement
        for the active mode, or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode
        """
        self.write(f":SENS:{self._mode_command(mode)}:REL:STAT 0")

    def acquire_relative(self, mode=None):
        """ Set the active value as the relative for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode

        :return: The relative value that was acquired

        """
        mode_cmd = self._mode_command(mode)
        self.write(f":SENS:{mode_cmd}:REL:ACQ")
        rel = float(self.ask(f":SENS:{mode_cmd}:REL?"))
        return rel

    def enable_filter(self, mode=None, type="repeat", count=1):
        """ Enable the averaging filter for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode
        :param type: The type of averaging filter, could be ``REPeat``, ``MOVing``, or ``HYBRid``.
        :param count: A number of averages, which can take take values from 1 to 100

        :return: Filter status read from the instrument
        """
        mode_cmd = self._mode_command(mode)
        self.write(f":SENS:{mode_cmd}:AVER:STAT 1")
        self.write(f":SENS:{mode_cmd}:AVER:TCON {type}")
        self.write(f":SENS:{mode_cmd}:AVER:COUN {count}")
        return self.ask(f":SENS:{mode_cmd}:AVER:STAT?")

    def disable_filter(self, mode=None):
        """ Disable the averaging filter for the active mode,
        or can set another mode by its name.

        :param mode: A valid :attr:`mode` name, or `None` for the active mode

        :return: Filter status read from the instrument
        """
        mode_cmd = self._mode_command(mode)
        self.write(f":SENS:{mode_cmd}:AVER:STAT 0")
        return self.ask(f":SENS:{mode_cmd}:AVER:STAT?")

    def beep(self, frequency, duration):
        """ Sound a system beep.

        :param frequency: A frequency in Hz between 20 Hz and 8000 Hz
        :param duration: The amount of time to play the tone between 0.001 s to 100 s
        :return: None
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")

    def write(self, command):
        """ Write a command to the instrument.

        :param command: A command
        :param type: str
        :return: None
        """
        if "{function}" in command:
            super().write(command.format(function = KeithleyDMM6500.MODES[self.mode]))
        else:
            super().write(command)
