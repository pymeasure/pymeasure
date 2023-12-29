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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set

import numpy as np
from time import time, sleep


class LakeShore421(Instrument):
    """
    Represents the Lake Shore 421 Gaussmeter and provides a high-level interface for interacting
    with the instrument.

    .. code-block:: python

        gaussmeter = LakeShore421("COM1")
        gaussmeter.unit = "T"               # Set units to Tesla
        gaussmeter.auto_range = True        # Turn on auto-range
        gaussmeter.fast_mode = True         # Turn on fast-mode


    A delay of 50 ms is ensured between subsequent writes, as the instrument cannot correctly
    handle writes any faster.
    """

    MULTIPLIERS = {1e3: 'k', 1: '', 1e-3: 'm', 1e-6: 'n'}
    PROBE_TYPES = {"High Sensitivity": 0,
                   "High Stability": 1,
                   "Ultra-High Sensitivity": 2}
    RANGES = [30e3, 3e3, 300, 30]  # in Gauss
    RANGE_MULTIPLIER_PROBE = [1, 10, 0.01]
    RANGE_MULTIPLIER_UNIT = {'G': 1, 'T': 1e-4}
    UNITS = ['G', 'T']
    WRITE_DELAY = 0.05

    def __init__(self, adapter, name="Lake Shore 421 Gaussmeter", baud_rate=9600, **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': baud_rate, 'data_bits': 7, 'stop_bits': 10, 'parity': 1},
            read_termination='\r',
            write_termination='\n',
            **kwargs
        )
        self.last_write_time = time()

    def _raw_to_field(self, field_raw, multiplier_name):
        if not field_raw == "OL":
            multiplier = getattr(self, multiplier_name)
            field = multiplier * field_raw
        else:
            field = np.nan

        return field

    def _field_to_raw(self, field, multiplier_name):
        multiplier = getattr(self, multiplier_name)
        return field / multiplier

    field_raw = Instrument.measurement(
        "FIELD?",
        """ Returns the field in the current units and multiplier
        """,
    )

    field_multiplier = Instrument.measurement(
        "FIELDM?",
        """ Returns the field multiplier for the returned magnetic field.
        """,
        values=MULTIPLIERS,
        map_values=True,
    )

    @property
    def field(self):
        """ Returns the field in the current units. This property takes into
        account the field multiplier. Returns np.nan if field is out of range.
        """
        return self._raw_to_field(self.field_raw, "field_multiplier")

    unit = Instrument.control(
        "UNIT?", "UNIT %s",
        """ A string property that controls the units used by the gaussmeter.
        Valid values are G (Gauss), T (Tesla). """,
        validator=strict_discrete_set,
        values=UNITS,
    )

    field_range_raw = Instrument.control(
        "RANGE?", "RANGE %d",
        """ A integer property that controls the field range of the
        meter. Valid values are 0 (highest) to 3 (lowest). """,
        validator=truncated_discrete_set,
        values=range(4),
        cast=int,
    )

    @property
    def field_range(self):
        """ A floating point property that controls the field range of the
        meter in the current unit (G or T). Valid values are 30e3, 3e3, 300,
        30 (when in Gauss), or 0.003, 0.03, 0.3, and 3 (when in Tesla).
        """
        probe_multiplier = self.RANGE_MULTIPLIER_PROBE[self.PROBE_TYPES[self.probe_type]]
        unit_multiplier = self.RANGE_MULTIPLIER_UNIT[self.unit]
        range = self.RANGES[self.field_range_raw]
        return np.round(range * probe_multiplier * unit_multiplier, 3)

    @field_range.setter
    def field_range(self, range):
        probe_multiplier = self.RANGE_MULTIPLIER_PROBE[self.PROBE_TYPES[self.probe_type]]
        unit_multiplier = self.RANGE_MULTIPLIER_UNIT[self.unit]
        ranges = np.array(self.RANGES) * probe_multiplier * unit_multiplier
        range = truncated_discrete_set(range, values=ranges)
        range = np.round(range / (probe_multiplier * unit_multiplier), 3)

        self.field_range_raw = self.RANGES.index(range)

    auto_range = Instrument.control(
        "AUTO?", "AUTO %d",
        """ A boolean property that controls the auto-range option of the
        meter. Valid values are True and False. Note that the auto-range is
        relatively slow and might not suffice for rapid measurements.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    fast_mode = Instrument.control(
        "FAST?", "FAST %d",
        """ A boolean property that controls the fast-mode option of the
        meter. Valid values are True and False. When enabled, the relative
        mode, Max Hold mode, alarms, and autorange are disabled. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    field_mode = Instrument.control(
        "ACDC?", "ACDC %d",
        """ A string property that controls whether the gaussmeter measures
        AC or DC magnetic fields. Valid values are "AC" and "DC". """,
        validator=strict_discrete_set,
        values={"DC": 0, "AC": 1},
        map_values=True,
    )

    def zero_probe(self, wait=True):
        """ Reset the probe value to 0. It is normally used with a zero gauss
        chamber, but may also be used with an open probe to cancel the Earth
        magnetic field. To cancel larger magnetic fields, the relative mode
        should be used.

        :param bool wait:
            Wait for 20 seconds after issuing the command to allow the
            resetting to finish.

        """
        self.write("ZCAL")
        if wait:
            sleep(20)

    probe_type = Instrument.measurement(
        "TYPE?",
        """ Returns type of field-probe used with the gaussmeter. Possible
        values are High Sensitivity, High Stability, or Ultra-High Sensitivity.
        """,
        values=PROBE_TYPES,
        map_values=True,
    )

    serial_number = Instrument.measurement(
        "SNUM?",
        """ Returns the serial number of the probe. """
    )

    display_filter_enabled = Instrument.control(
        "FILT?", "FILT %d",
        """ A boolean property that controls the display filter to make it
        more readable when the probe is exposed to a noisy field. The filter
        function makes a linear average of 8 readings and settles in
        approximately 2 seconds. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    front_panel_locked = Instrument.control(
        "LOCK?", "LOCK %d",
        """ A boolean property that locks or unlocks all front panel entries
        except pressing the Alarm key to silence alarms. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    front_panel_brightness = Instrument.control(
        "BRIGT?", "BRIGT %d",
        """ An integer property that controls the brightness of the from panel
        display. Valid values are 0 (dimmest) to 7 (brightest). """,
        validator=strict_discrete_set,
        values=range(8),
    )

    # MAX HOLD
    max_hold_enabled = Instrument.control(
        "MAX?", "MAX %d",
        """ A boolean property that enables or disables the Max Hold function to
        store the largest field since the last reset (with max_hold_reset). """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    max_hold_field_raw = Instrument.measurement(
        "MAXR?",
        """ Returns the largest field since the last reset in the current units
        and multiplier.
        """,
    )

    max_hold_multiplier = Instrument.measurement(
        "FIELDM?",
        """ Returns the multiplier for the returned max hold field.
        """,
        values=MULTIPLIERS,
        map_values=True,
    )

    @property
    def max_hold_field(self):
        """ Returns the largest field since the last reset in the current units.
        This property takes into account the field multiplier. Returns np.nan if
        field is out of range.
        """
        return self._raw_to_field(self.max_hold_field_raw, "max_hold_multiplier")

    def max_hold_reset(self):
        """ Clears the stored Max Hold value. """
        self.write("MAXC")

    # RELATIVE MODE
    relative_mode_enabled = Instrument.control(
        "REL?", "REL %d",
        """ A boolean property that enables or disables the relative mode to
        see small variations with respect to a given setpoint. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    relative_field_raw = Instrument.measurement(
        "RELR?",
        """ Returns the relative field in the current units and the current
        multiplier. """,
    )

    relative_multiplier = Instrument.measurement(
        "RELRM?",
        """ Returns the relative field multiplier for the returned magnetic
        field. """,
        values=MULTIPLIERS,
        map_values=True,
    )

    @property
    def relative_field(self):
        """ Returns the relative field in the current units. This property
        takes into account the field multiplier. Returns np.nan if field is
        out of range.
        """
        return self._raw_to_field(self.relative_field_raw, "relative_multiplier")

    relative_setpoint_raw = Instrument.control(
        "RELS?", "RELS %g",
        """ Property that controls the setpoint for the relative field mode in
        the current units and multiplier. """,
    )

    relative_setpoint_multiplier = Instrument.measurement(
        "RELRM?",
        """ Returns the multiplier for the setpoint field. """,
        values=MULTIPLIERS,
        map_values=True,
    )

    @property
    def relative_setpoint(self):
        """ Property that controls the setpoint for the relative field mode in
        the current units. This takes into account the field multiplier. """
        return self._raw_to_field(self.relative_setpoint_raw, "relative_setpoint_multiplier")

    @relative_setpoint.setter
    def relative_setpoint(self, value):
        self.relative_setpoint_raw = self._field_to_raw(value, "relative_setpoint_multiplier")

    # ALARM MODE
    alarm_mode_enabled = Instrument.control(
        "ALARM?", "ALARM %d",
        """ A boolean property that enables or disables the alarm mode. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    alarm_audible = Instrument.control(
        "ALMB?", "ALMB %d",
        """ A boolean property that enables or disables the audible alarm
        beeper. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    alarm_in_out = Instrument.control(
        "ALMB?", "ALMB %d",
        """ A string property that controls whether an active alarm is caused
        when the field reading is inside ("Inside") or outside ("Outside") of
        the high and low setpoint values. """,
        validator=strict_discrete_set,
        values={"Inside": 1, "Outside": 0},
        map_values=True,
    )

    alarm_active = Instrument.measurement(
        "ALMS?",
        """ A boolean property that returns whether the alarm is triggered. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    alarm_sort_enabled = Instrument.control(
        "ALMSORT?", "ALMSORT %d",
        """ A boolean property that enables or disables the alarm Sort Pass/Fail
        function. """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    alarm_low_raw = Instrument.measurement(
        "ALML?", "ALML %g",
        """ Property that controls the lower setpoint for the alarm mode in the
        current units and multiplier. """,
    )

    alarm_low_multiplier = Instrument.measurement(
        "ALMLM?",
        """ Returns the multiplier for the lower alarm setpoint field. """,
        values=MULTIPLIERS,
        map_values=True,
    )

    @property
    def alarm_low(self):
        """ Property that controls the lower setpoint for the alarm mode in the
        current units. This takes into account the field multiplier. """
        return self._raw_to_field(self.alarm_low_raw, "alarm_low_multiplier")

    @alarm_low.setter
    def alarm_low(self, value):
        self.alarm_low_raw = self._field_to_raw(value, "alarm_low_multiplier")

    alarm_high_raw = Instrument.measurement(
        "ALMH?", "ALMH %g",
        """ Property that controls the upper setpoint for the alarm mode in the
        current unit and multiplier. """,
    )

    alarm_high_multiplier = Instrument.measurement(
        "ALMHM?",
        """ Returns the multiplier for the upper alarm setpoint field. """,
        values=MULTIPLIERS,
        map_values=True,
    )

    @property
    def alarm_high(self):
        """ Property that controls the upper setpoint for the alarm mode in the
        current units. This takes into account the field multiplier. """
        return self._raw_to_field(self.alarm_high_raw, "alarm_high_multiplier")

    @alarm_high.setter
    def alarm_high(self, value):
        self.alarm_high_raw = self._field_to_raw(value, "alarm_high_multiplier")

    def shutdown(self):
        """ Closes the serial connection to the system. """
        self.adapter.connection.close()
        super().shutdown()

    ###################################################
    # Redefined methods to ensure time between writes #
    ###################################################

    def delay_write(self):
        if self.WRITE_DELAY is None:
            return

        while time() - self.last_write_time < self.WRITE_DELAY:
            sleep(self.WRITE_DELAY / 10)

        self.last_write_time = time()

    def write(self, command):
        self.delay_write()
        super().write(command)
