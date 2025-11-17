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
import time
from warnings import warn

import numpy as np

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.errors import RangeException
from pymeasure.instruments.validators import (
    strict_range,
    strict_discrete_range,
    strict_discrete_set,
)

from .buffer import KeithleyBuffer


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def _deprecate_process(msg):
    return lambda v: (warn(msg, FutureWarning), v)[1]


class Keithley2400(KeithleyBuffer, SCPIMixin, Instrument):
    """Represent the Keithley 2400 SourceMeter and provide a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        smu = Keithley2400("GPIB::1")
        smu.reset()                        # Resets the instrument

        smu.source_mode = "current"        # Sets up to source current
        smu.source_enabled = True          # Enables the source output

        smu.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(smu.voltage)                 # Prints the voltage in Volts

        smu.reset()                        # Resets the instrument
    """

    def __init__(self, adapter, name="Keithley 2400 SourceMeter", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.reset_data_format()

    def reset_data_format(self):
        """Resets the data format to the format expected by :class:`Keithley2400`.

        The expected data format is [<current>, <voltage>, <resistance>, <time>, <status>].

        .. caution::
           Changing the data format with the ":FORMAT:ELEMENTS" command after initialization
           may break parts of :class:`Keithley2400`.
        """
        self.write(":FORMAT:ELEMENTS VOLTAGE, CURRENT, RESISTANCE, TIME, STATUS")

    ##########
    # SOURCE #
    ##########

    source_enabled = Instrument.control(
        "OUTPUT?",
        "OUTPUT %d",
        """Control whether the source is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def enable_source(self):
        """Enable the source."""
        self.source_enabled = True

    def disable_source(self):
        """Disable the source."""
        self.source_enabled = False

    source_mode = Instrument.control(
        ":SOURCE:FUNCTION?",
        ":SOURCE:FUNCTION %s",
        """Control the source mode (str, strictly 'current' or 'voltage').""",
        validator=strict_discrete_set,
        values={"current": "CURR", "voltage": "VOLT"},
        map_values=True,
    )

    source_delay = Instrument.control(
        ":SOURCE:DELAY?",
        ":SOURCE:DELAY %g",
        """Control the manual delay in seconds for the source after the output is turned on
        before a measurement is taken (float strictly from 0 to 999.9999).

        When this property is set, :attr:`~.source_delay_auto_enabled` is implicitly set to False.
        """,
        validator=strict_range,
        values=[0, 999.9999],
    )

    source_delay_auto_enabled = Instrument.control(
        ":SOURCE:DELAY:AUTO?",
        ":SOURCE:DELAY:AUTO %d",
        """Control whether the source auto delay is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    source_delay_auto = Instrument.control(
        ":SOUR:DEL:AUTO?",
        ":SOUR:DEL:AUTO %d",
        """ Control the auto delay (boolean).

        .. deprecated:: 0.16
           Use :attr:`~.source_delay_auto_enabled`.""",
        values={True: 1, False: 0},
        map_values=True,
        get_process=_deprecate_process(
            "Deprecated to use `Keithley2400.source_delay_auto`, "
            "use `Keithley2400.source_delay_auto_enabled`.",
        ),
        set_process=_deprecate_process(
            "Deprecated to use `Keithley2400.source_delay_auto`, "
            "use `Keithley2400.source_delay_auto_enabled`.",
        ),
    )

    auto_zero_enabled = Instrument.control(
        ":SYSTEM:AZERO:STATE?",
        ":SYSTEM:AZERO:STATE %s",
        """Control whether auto zeroing is enabled (bool)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def auto_zero_once(self):
        self.write(":SYSTEM:AZERO:STATE ONCE")

    auto_zero = Instrument.control(
        ":SYST:AZER:STAT?",
        ":SYST:AZER:STAT %s",
        """ Control whether the auto zero option is enabled. Valid values are
        True (enabled) and False (disabled) and 'ONCE' (force immediate).

        .. deprecated:: 0.16
           Use :attr:`~.auto_zero_enabled` or :meth:`~.auto_zero_once`.""",
        values={True: 1, False: 0, "ONCE": "ONCE"},
        map_values=True,
        get_process=_deprecate_process(
            "Deprecated to use `Keithley2400.auto_zero`, "
            "use `Keithley2400.auto_zero_enabled` or `Keithley2400.auto_zero_once`",
        ),
        set_process=_deprecate_process(
            "Deprecated to use `Keithley2400.auto_zero`, "
            "use `Keithley2400.auto_zero_enabled` or `Keithley2400.auto_zero_once`",
        ),
    )

    output_off_state = Instrument.control(
        ":OUTPUT:SMODE?",
        ":OUTPUT:SMODE %s",
        """Control the output-off state.

        str:
        - 'disconnected': Output relay opens (do not use this state if output is turned on and off
          frequently to prevent excess wear on the relay)
        - 'normal': V-source is selected and set to 0V.
        - 'zero': Allows the sourcemeter to be used to measure current while off.
        - 'guard': I-source is selected and set to 0A.

        .. deprecated:: 0.16
           Deprecated to use 'HIMP', 'NORM', 'ZERO', or 'GUAR' with :attr:`~.output_off_state`.
        """,
        validator=strict_discrete_set,
        values={
            "disconnected": "HIMP",
            "normal": "NORM",
            "zero": "ZERO",
            "guard": "GUAR",
            "HIMP": "HIMP",  # included for backwards compatibility
            "NORM": "NORM",  # ''
            "ZERO": "ZERO",  # ''
            "GUAR": "GUAR",  # ''
        },
        map_values=True,
    )

    auto_output_off_enabled = Instrument.control(
        ":SOURCE:CLEAR:AUTO?",
        ":SOURCE:CLEAR:AUTO %d",
        """Control whether auto output-off is activated (bool).

        .. warning::
           With auto output-off disabled (False), the output will remain on after
           a source-measure operation is performed.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    auto_output_off = Instrument.control(
        ":SOUR:CLE:AUTO?",
        ":SOUR:CLE:AUTO %d",
        """Control whether auto output-off is activated.
        Valid values are True (output off after measurement) and False (output
        stays on after measurement).

        .. deprecated:: 0.16
           Use :attr:`~.auto_output_off_enabled`.""",
        values={True: 1, False: 0},
        map_values=True,
        get_process=_deprecate_process(
            "Deprecated to use `Keithley2400.auto_output_off`, "
            "use `Keithley2400.auto_output_off_enabled`.",
        ),
        set_process=_deprecate_process(
            "Deprecated to use `Keithley2400.auto_output_off_enabled`, "
            "use `Keithley2400.auto_output_off_enabled`.",
        ),
    )

    def auto_range_source(self):
        """Configure the source to use an automatic range.

        .. deprecated:: 0.16
           Control auto ranging for the desired source using
           :attr:`~.source_current_range_auto_enabled` or
           :attr:`~.source_voltage_range_auto_enabled`.
        """
        warn(
            """Deprecated to use `Keithley2400.auto_range_source`. Recommended to explicitly set the
            auto range for the desired source using `Keithley2400.source_current_range_auto_enabled`
            or `Keithley2400.source_voltage_range_auto_enabled`.""",
            FutureWarning,
        )
        if self.source_mode == "current":
            self.write(":SOUR:CURR:RANG:AUTO 1")
        else:
            self.write(":SOUR:VOLT:RANG:AUTO 1")

    ###############
    # Measurement #
    ###############

    filter_enabled = Instrument.control(
        ":SENSE:AVERAGE?",
        ":SENSE:AVERAGE %s",
        """Control whether the filter is active (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    filter_state = Instrument.control(
        ":SENS:AVER?",
        ":SENS:AVER %s",
        """ Control if the filter is active (string, strictly 'ON' or 'OFF').

        .. deprecated:: 0.16
           Use :attr:`~.filter_enabled`.""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        map_values=False,
        get_process=_deprecate_process(
            "Deprecated to use `Keithley2400.filter_state`, use `Keithley2400.filter_enabled`.",
        ),
        set_process=_deprecate_process(
            "Deprecated to use `Keithley2400.filter_state`, use `Keithley2400.filter_enabled`.",
        ),
    )

    repeat_filter_enabled = Instrument.control(
        ":SENSE:AVERAGE:TCONTROL?",
        ":SENSE:AVERAGE:TCONTROL %s",
        """Control whether repeat filter is enabled (bool). If False, moving filter is used.""",
        validator=strict_discrete_set,
        values={True: "REP", False: "MOV"},
        map_values=True,
    )

    filter_type = Instrument.control(
        ":SENS:AVER:TCON?",
        ":SENS:AVER:TCON %s",
        """ Control (String) the filter's type.
        REP : Repeating filter
        MOV : Moving filter

        .. deprecated:: 0.16
           Use :attr:`~.repeat_filter_enabled`.
        """,
        validator=strict_discrete_set,
        values=["REP", "MOV"],
        map_values=False,
        get_process=_deprecate_process(
            "Deprecated to use `Keithley2400.filter_type`, "
            "use `Keithley2400.repeat_filter_enabled`.",
        ),
        set_process=_deprecate_process(
            "Deprecated to use `Keithley2400.filter_type`, "
            "use `Keithley2400.repeat_filter_enabled`.",
        ),
    )

    filter_count = Instrument.control(
        ":SENSE:AVERAGE:COUNT?",
        ":SENSE:AVERAGE:COUNT %d",
        """Control the number of readings that are acquired and stored in the filter buffer
        (int, strictly from 1 to 100).""",
        validator=strict_range,
        values=[1, 100],
        cast=int,
    )

    def measure_all(self):
        """Measure current (A), voltage (V), resistance (Ohm), time (s), and status concurrently.

        .. note::
           Sets :attr:`~.resistance_mode_auto` to False

        Returns
        -------
        dict
            Dictionary with the following keys:
            - 'current' (float): Measured current in A.
            - 'voltage' (float): Measured voltage in V.
            - 'resistance' (float): Measured resistance in Ohms.
            - 'time' (float): Measurement time in s.
            - 'status' (int): Instrument status flag.
        """
        self.resistance_mode_auto_enabled = False
        self.write(":SENSE:FUNCTION:ALL")
        values = self.values(":READ?")
        values = [float("nan") if v == 9.91e37 else v for v in values]

        return {
            "voltage": values[0],
            "current": values[1],
            "resistance": values[2],
            "time": values[3],
            "status": int(values[4]),
        }

    ###############
    # Current (A) #
    ###############

    # Current measurement #

    current = Instrument.measurement(
        ":MEASURE:CURRENT?",
        """Measure the current in Amps (float).""",
        get_process_list=lambda v: v[1],
    )

    current_range = Instrument.control(
        ":SENSE:CURRENT:RANGE?",
        ":SENSE:CURRENT:RANGE %g",
        """Control the measurement current range in Amps (float, strictly from -1.05 to 1.05).

        When set, the range selected will be the most sensitive range that will accommodate the
        set value, and :attr:`~.current_range_auto_enabled` is implicitly set to False.
        """,
        validator=strict_range,
        values=[-1.05, 1.05],
    )

    current_range_auto_enabled = Instrument.control(
        ":SENSE:CURRENT:RANGE:AUTO?",
        ":SENSE:CURRENT:RANGE:AUTO %d",
        """Control whether current measurement auto-range is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    current_nplc = Instrument.control(
        ":SENSE:CURRENT:NPLCYCLES?",
        ":SENSE:CURRENT:NPLCYCLES %g",
        """Control the number of power line cycles (NPLC) (float, strictly from 0.01 to 10).

        .. note::
           This is a global command, implicitly setting :attr:`~.voltage_nplc`
           and :attr:`~.resistance_nplc`.
        """,
        validator=strict_range,
        values=[0.01, 10],
    )

    compliance_current = Instrument.control(
        ":SENSE:CURRENT:PROTECTION?",
        ":SENSE:CURRENT:PROTECTION %g",
        """Control the compliance current in Amps (float, strictly from -1.05 to 1.05).""",
        validator=strict_range,
        values=[-1.05, 1.05],
    )

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """Configure the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -1.05 A to 1.05 A
        :param auto_range: Enables auto_range if True, else uses the set current

        .. deprecated:: 0.16
           - Configuration to measure current is performed implicitly by
             :attr:`~.current`.
           - Control current nplc via :attr:`~.current_nplc`.
           - Control current range via :attr:`~.current_range`
             or :attr:`~.current_range_auto_enabled`.
        """
        warn(
            """Deprecated to use `Keithley2400.measure_current`, configuration to measure
            current is now performed implicitly by `Keithley2400.current`. Recommended to
            explicitly set the current nplc via `Keithley2400.current_nplc`, and the current
            range via `Keithley2400.current_range` or `Keithley2400.current_range_auto_enabled`.""",
            FutureWarning,
        )
        log.info("%s is measuring current." % self.name)
        self.write(":SENS:FUNC 'CURR';:SENS:CURR:NPLC %f;" % nplc)
        if auto_range:
            self.write(":SENS:CURR:RANG:AUTO 1;")
        else:
            self.current_range = current
        self.check_errors()

    # Current source #

    source_current = Instrument.control(
        ":SOURCE:CURRENT?",
        ":SOURCE:CURRENT %g",
        """Control the source current in Amps (float, strictly from -1.05 to 1.05).""",
        validator=strict_range,
        values=[-1.05, 1.05],
    )

    source_current_range = Instrument.control(
        ":SOURCE:CURRENT:RANGE?",
        ":SOURCE:CURRENT:RANGE %g",
        """Control the source current range in Amps (float, strictly from -1.05 to 1.05).

        When set, the range selected will be the most sensitive range that will accommodate the
        set value, and Auto-range is disabled.""",
        validator=strict_range,
        values=[-1.05, 1.05],
    )

    source_current_range_auto_enabled = Instrument.control(
        ":SOURCE:CURRENT:RANGE:AUTO?",
        ":SOURCE:CURRENT:RANGE:AUTO %d",
        """Control whether souce current auto-range is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def ramp_to_current(self, target_current, steps=30, pause=20e-3):
        """Ramp to a target current from the set current value over
        a certain number of linear steps, each separated by a pause duration.

        :param target_current: A current in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps
        """
        currents = np.linspace(self.source_current, target_current, steps)
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    def apply_current(self, current_range=None, compliance_voltage=0.1):
        """Configure the instrument to apply a source current, and
        uses an auto range unless a current range is specified.
        The compliance voltage is also set.

        :param compliance_voltage: A float in the correct range for a
                                   :attr:`~.compliance_voltage`
        :param current_range: A :attr:`~.current_range` value or None

        .. deprecated:: 0.16
           - Control source mode via :attr:`~.source_mode`.
           - Control source current range via :attr:`~.source_current_range` or
             :attr:`~.source_current_range_auto_enabled`.
           - Control compliance voltage via :attr:`~.compliance_voltage`
        """
        warn(
            """Deprecated to use `Keithley2400.apply_current`. Recommended to explicitly control
            source mode via `Keithley2400.source_mode`, current range via
            `Keithley2400.source_current_range` or `Keithley2400.source_current_range_auto_enabled`,
            and compliance voltage via `Keithley2400.compliance_voltage`.""",
            FutureWarning,
        )
        log.info("%s is sourcing current." % self.name)
        self.source_mode = "current"
        if current_range is None:
            self.auto_range_source()
        else:
            self.source_current_range = current_range
        self.compliance_voltage = compliance_voltage
        self.check_errors()

    ###############
    # Voltage (V) #
    ###############

    # Voltage measurement #

    voltage = Instrument.measurement(
        ":MEASURE:VOLTAGE?",
        """Measure the voltage in Volts (float).""",
        get_process_list=lambda v: v[0],
    )

    voltage_range = Instrument.control(
        ":SENSE:VOLTAGE:RANGE?",
        ":SENSE:VOLTAGE:RANGE %g",
        """Control the measurement voltage range in Volts (float, strictly from -210 to 210).

        When set, the range selected will be the most sensitive range that will accommodate the
        set value, and :attr:`~.voltage_range_auto_enabled` is implicitly set to False.
        """,
        validator=strict_range,
        values=[-210, 210],
    )

    voltage_range_auto_enabled = Instrument.control(
        ":SENSE:VOLTAGE:RANGE:AUTO?",
        ":SENSE:VOLTAGE:RANGE:AUTO %d",
        """Control whether voltage measurement auto-range is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    voltage_nplc = Instrument.control(
        ":SENSE:VOLTAGE:NPLCYCLES?",
        ":SENSE:VOLTAGE:NPLCYCLES %g",
        """Control the number of power line cycles (NPLC) (float, strictly from 0.01 to 10).

        .. note::
           This is a global command, implicitly setting :attr:`~.current_nplc`
           and :attr:`~.resistance_nplc`.
        """,
        validator=strict_range,
        values=[0.01, 10],
    )

    compliance_voltage = Instrument.control(
        ":SENSE:VOLTAGE:PROTECTION?",
        ":SENSE:VOLTAGE:PROTECTION %g",
        """Control the compliance voltage in Volts (float, strictly from -210 to 210).""",
        validator=strict_range,
        values=[-210, 210],
    )

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """Configure the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -210 V to 210 V
        :param auto_range: Enables auto_range if True, else uses the set voltage

        .. deprecated:: 0.16
           - Configuration to measure voltage is performed implicitly by
             :attr:`~.voltage`.
           - Control voltage nplc via :attr:`~.voltage_nplc`.
           - Control voltage range via :attr:`~.voltage_range`
             or :attr:`~.voltage_range_auto_enabled`.
        """
        warn(
            """Deprecated to use `Keithley2400.measure_voltage`, configuration to measure
            voltage is now performed implicitly by `Keithley2400.voltage`. Recommended to
            explicitly set the voltage nplc via `Keithley2400.voltage_nplc`, and the voltage
            range via `Keithley2400.voltage_range` or `Keithley2400.voltage_range_auto_enabled`.""",
            FutureWarning,
        )
        log.info("%s is measuring voltage." % self.name)
        self.write(":SENS:FUNC 'VOLT';:SENS:VOLT:NPLC %f;" % nplc)
        if auto_range:
            self.write(":SENS:VOLT:RANG:AUTO 1;")
        else:
            self.voltage_range = voltage
        self.check_errors()

    # Voltage source #

    source_voltage = Instrument.control(
        ":SOURCE:VOLTAGE?",
        ":SOURCE:VOLTAGE %g",
        """Control the source voltage in Volts (float, strictly from -210 to 210).""",
        validator=strict_range,
        values=[-210, 210],
    )

    source_voltage_range = Instrument.control(
        ":SOURCE:VOLTAGE:RANGE?",
        ":SOURCE:VOLTAGE:RANGE %g",
        """Control the source voltage range in Volts (float, strictly from -210 to 210).

        When set, the range selected will be the most sensitive range that will accommodate the
        set value, and Auto-range is disabled.""",
        validator=strict_range,
        values=[-210, 210],
    )

    source_voltage_range_auto_enabled = Instrument.control(
        ":SOURCE:VOLTAGE:RANGE:AUTO?",
        ":SOURCE:VOLTAGE:RANGE:AUTO %d",
        """Control whether source voltage auto-range is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def ramp_to_voltage(self, target_voltage, steps=30, pause=20e-3):
        """Ramp to a target voltage from the set voltage value over
        a certain number of linear steps, each separated by a pause duration.

        :param target_voltage: A voltage in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps
        """
        voltages = np.linspace(self.source_voltage, target_voltage, steps)
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def apply_voltage(self, voltage_range=None, compliance_current=0.1):
        """Configure the instrument to apply a source voltage, and
        uses an auto range unless a voltage range is specified.
        The compliance current is also set.

        :param compliance_current: A float in the correct range for a
                                   :attr:`~.compliance_current`
        :param voltage_range: A :attr:`~.voltage_range` value or None

        .. deprecated:: 0.16
           - Control source mode via :attr:`~.source_mode`.
           - Control source voltage range via :attr:`~.source_voltage_range` or
             :attr:`~.source_voltage_range_auto_enabled`.
           - Control compliance current via :attr:`~.compliance_current`
        """
        warn(
            """Deprecated to use `Keithley2400.apply_voltage`. Recommended to explicitly control
            source mode via `Keithley2400.source_mode`, voltage range via
            `Keithley2400.source_voltage_range` or `Keithley2400.source_voltage_range_auto_enabled`,
            and compliance current via `Keithley2400.compliance_current`.""",
            FutureWarning,
        )
        log.info("%s is sourcing voltage." % self.name)
        self.source_mode = "voltage"
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.compliance_current = compliance_current
        self.check_errors()

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":MEASURE:RESISTANCE?",
        """Measure the resistance in Ohms (float).""",
        get_process_list=lambda v: v[2],
    )

    resistance_mode_auto_enabled = Instrument.control(
        ":SENSE:RESISTANCE:MODE?",
        ":SENSE:RESISTANCE:MODE %s",
        """Control the resistance mode auto status (bool).

        When `True`, `source_current` and `voltage_range` depends on the `resistance_range`
        selected. When `False`, `source_current` and `voltage_range` are controlled manually.""",
        values={True: "AUTO", False: "MAN"},
        map_values=True,
    )

    resistance_range = Instrument.control(
        ":SENSE:RESISTANCE:RANGE?",
        ":SENSE:RESISTANCE:RANGE %g",
        """Control the resistance range in Ohms (float, strictly from 0 to 210e6).

        When set, the range selected will be the most sensitive range that will accommodate the
        set value, and :attr:`~.resistance_range_auto_enabled` is implicitly set to
        False.""",
        validator=strict_range,
        values=[0, 210e6],
    )

    resistance_range_auto_enabled = Instrument.control(
        ":SENSE:RESISTANCE:RANGE:AUTO?",
        ":SENSE:RESISTANCE:RANGE:AUTO %d",
        """Control whether resistance measurement auto-range is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    resistance_nplc = Instrument.control(
        ":SENSE:RESISTANCE:NPLCYCLES?",
        ":SENSE:RESISTANCE:NPLCYCLES %g",
        """Control the number of power line cycles (NPLC) (float, strictly from 0.01 to 10).

        .. note::
           This is a global command, implicitly setting :attr:`~.current_nplc`
           and :attr:`~.voltage_nplc`.
        """,
        validator=strict_range,
        values=[0.01, 10],
    )

    def measure_resistance(self, nplc=1, resistance=2.1e5, auto_range=True):
        """Configure the measurement of resistance.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param resistance: Upper limit of resistance in Ohms, from -210 MOhms to 210 MOhms
        :param auto_range: Enables auto_range if True, else uses the set resistance

        .. deprecated:: 0.16
           - Configuration to measure resistance is performed implicitly by
             :attr:`~.resistance`.
           - Control resistance nplc via :attr:`~.resistance_nplc`.
           - Control resistance range via :attr:`~.resistance_range`
             or :attr:`~.resistance_range_auto_enabled`.
        """
        warn(
            """Deprecated to use `Keithley2400.measure_resistance`, configuration to measure
            voltage is now performed implicitly by `Keithley2400.resistance`. Recommended to
            explicitly set the resistance nplc via `Keithley2400.resistance_nplc`, and the
            resistance range via `Keithley2400.resistance_range` or
            `Keithley2400.resistance_range_auto_enabled`.""",
            FutureWarning,
        )
        log.info("%s is measuring resistance." % self.name)
        self.write(":SENS:FUNC 'RES';:SENS:RES:MODE MAN;:SENS:RES:NPLC %f;" % nplc)
        if auto_range:
            self.write(":SENS:RES:RANG:AUTO 1;")
        else:
            self.resistance_range = resistance
        self.check_errors()

    ##########
    # Buffer #
    ##########

    means = Instrument.measurement(
        ":CALCULATE3:FORMAT MEAN;:CALCULATE3:DATA?;",
        """Get the calculated means for voltage, current, and resistance from the buffer data
        (list of floats).""",
    )

    maximums = Instrument.measurement(
        ":CALCULATE3:FORMAT MAX;:CALCULATE3:DATA?;",
        """Get the calculated maximums for voltage, current, and resistance from the buffer data
        (list of floats).""",
    )

    minimums = Instrument.measurement(
        ":CALCULATE3:FORMAT MIN;:CALCULATE3:DATA?;",
        """Get the calculated minimums for voltage, current, and resistance from the buffer data
        (list of floats).""",
    )

    standard_devs = Instrument.measurement(
        ":CALCULATE3:FORMAT SDEVIATION;:CALCULATE3:DATA?;",
        """Get the calculated standard deviations for voltage, current, and resistance from the
        buffer data (list of floats).""",
    )

    @property
    def mean_voltage(self):
        """Get the mean voltage from the buffer (float)."""
        return self.means[0]

    @property
    def max_voltage(self):
        """Get the maximum voltage from the buffer (float)."""
        return self.maximums[0]

    @property
    def min_voltage(self):
        """Get the minimum voltage from the buffer (float)."""
        return self.minimums[0]

    @property
    def std_voltage(self):
        """Get the voltage standard deviation from the bufferv."""
        return self.standard_devs[0]

    @property
    def mean_current(self):
        """Get the mean current from the buffer (float)."""
        return self.means[1]

    @property
    def max_current(self):
        """Get the maximum current from the buffer (float)."""
        return self.maximums[1]

    @property
    def min_current(self):
        """Get the minimum current from the buffer (float)."""
        return self.minimums[1]

    @property
    def std_current(self):
        """Get the current standard deviation from the buffer (float)."""
        return self.standard_devs[1]

    @property
    def mean_resistance(self):
        """Get the mean resistance from the buffer (float)."""
        return self.means[2]

    @property
    def max_resistance(self):
        """Get the maximum resistance from the buffer (float)."""
        return self.maximums[2]

    @property
    def min_resistance(self):
        """Get the minimum resistance from the buffer (float)."""
        return self.minimums[2]

    @property
    def std_resistance(self):
        """Get the resistance standard deviation from the buffer (float)."""
        return self.standard_devs[2]

    ###########
    # Trigger #
    ###########

    def trigger(self):
        """Execute a bus trigger, which can be used when :meth:`~.trigger_on_bus` is configured."""
        self.write("*TRG")

    def reset_trigger(self):
        """Reset the trigger system and return to an idle state."""
        self.write(":ABORT")

    def clear_trigger(self):
        """Clear any pending input triggers immediately."""
        self.write(":TRIGGER:CLEAR")

    @property
    def trigger_count(self):
        """Control the trigger layer count (int strictly in range 1 to 2500).
        The product of :attr:`trigger_count` and :attr:`arm_count` cannot exceed 2500."""
        return self.values(":TRIGGER:COUNT?")[0]

    @trigger_count.setter
    def trigger_count(self, v):
        v = strict_discrete_range(v, (1, 2500), 1)
        if v * self.arm_count > 2500:
            raise ValueError("Product of arm_count and trigger_count cannot exceed 2500.")
        self.write(f":TRIGGER:COUNT {v}")

    @property
    def arm_count(self):
        """Control the arm layer count (int strictly in range 1 to 2500).
        The product of :attr:`trigger_count` and :attr:`arm_count` cannot exceed 2500."""
        return self.values(":ARM:COUNT?")[0]

    @arm_count.setter
    def arm_count(self, v):
        v = strict_discrete_range(v, (1, 2500), 1)
        if v * self.trigger_count > 2500:
            raise ValueError("Product of arm_count and trigger_count cannot exceed 2500.")
        self.write(f":ARM:COUNT {v}")

    trigger_delay = Instrument.control(
        ":TRIGGER:DELAY?",
        ":TRIGGER:DELAY %g",
        """Control the trigger layer delay in seconds (float, strictly in range 0 to 999.9999).""",
        validator=strict_range,
        values=[0, 999.9999],
    )

    arm_timer = Instrument.control(
        ":ARM:TIMER?",
        ":ARM:TIMER %g",
        """Control the arm layer timer in seconds (float, strictly in range 0.001 to 99999.99).""",
        validator=strict_range,
        values=[0.001, 99999.99],
    )

    trigger_source = Instrument.control(
        ":TRIGGER:SOURCE?",
        ":TRIGGER:SOURCE %s",
        """Control the trigger layer event control source
        (str, strictly 'immediate' or 'trigger_link'.""",
        validator=strict_discrete_set,
        values={"immediate": "IMM", "trigger_link": "TLIN"},
        map_values=True,
    )

    arm_source = Instrument.control(
        ":ARM:SOURCE?",
        ":ARM:SOURCE %s",
        """Control the arm layer event control source
        (str, strictly 'immediate', 'trigger_link', 'timer', 'manual', or 'bus'.""",
        validator=strict_discrete_set,
        values={
            "immediate": "IMM",
            "trigger_link": "TLIN",
            "timer": "TIM",
            "manual": "MAN",
            "bus": "BUS",
        },
        map_values=True,
    )

    trigger_output_event = Instrument.control(
        ":TRIGGER:OUTPUT?",
        ":TRIGGER:OUTPUT %s",
        """Control when the trigger pulse occurs on the trigger layer output trigger line
        (str, strictly 'source', 'delay', 'sense', or 'none')""",
        validator=strict_discrete_set,
        values={
            "source": "SOUR",
            "delay": "DEL",
            "sense": "SENS",
            "none": "NONE",
        },
        map_values=True,
    )

    arm_output_event = Instrument.control(
        ":ARM:OUTPUT?",
        ":ARM:OUTPUT %s",
        """Control when the trigger pulse occurs on the arm layer output trigger line
        (str, strictly 'trigger_enter', 'trigger_exit', or 'none'.""",
        validator=strict_discrete_set,
        values={
            "trigger_enter": "TENT",
            "trigger_exit": "TEX",
            "none": "NONE",
        },
        map_values=True,
    )

    def disable_output_triggers(self):
        """Disable the output trigger for the Trigger layer"""
        self.arm_output_event = "none"
        self.trigger_output_event = "none"

    trigger_input_line = Instrument.control(
        ":TRIGGER:ILINE?",
        ":TRIGGER:ILINE %d",
        """Control the trigger layer input line (int, strictly in range 1 to 4).

        For normal operation, :attr:`~.trigger_input_line` should not share its value with
        :attr:`~.trigger_output_line` or :attr:`~.arm_output_line`.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(1, 4),
    )

    arm_input_line = Instrument.control(
        ":ARM:ILINE?",
        ":ARM:ILINE %d",
        """Control the arm layer input line (int, strictly in range 1 to 4).

        For normal operation, :attr:`~.arm_input_line` should not share its value with
        :attr:`~.trigger_output_line` or :attr:`~.arm_output_line`.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(1, 4),
    )

    trigger_output_line = Instrument.control(
        ":TRIGGER:OLINE?",
        ":TRIGGER:OLINE %d",
        """Control the trigger layer output line (int, strictly in range 1 to 4).

        For normal operation, :attr:`~.trigger_output_line` should not share its value with
        :attr:`~.trigger_input_line` or :attr:`~.arm_input_line`.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(1, 4),
    )

    arm_output_line = Instrument.control(
        ":ARM:OLINE?",
        ":ARM:OLINE %d",
        """Control the arm layer output line (int, strictly in range 1 to 4).

        For normal operation, :attr:`~.arm_output_line` should not share its value with
        :attr:`~.trigger_input_line` or :attr:`~.arm_input_line`.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(1, 4),
    )

    def trigger_on_bus(self):
        """Configure the trigger to detect events based on the bus trigger,
        which can be activated by :meth:`~.trigger`.
        """
        self.arm_count = 1
        self.arm_source = "bus"
        self.trigger_source = "immediate"

    def trigger_on_external(self, line=1):
        """Configure the measurement trigger to be taken from a specific line of an external trigger

        :param line: A trigger line from 1 to 4
        """
        self.arm_source = "trigger_link"
        self.trigger_source = "trigger_link"
        self.arm_input_line = line
        self.trigger_input_line = line

    def trigger_immediately(self):
        """Configure measurements to be taken with the internal trigger
        at the maximum sampling rate."""
        self.arm_source = "immediate"
        self.trigger_source = "immediate"

    def sample_continuously(self):
        """Cause the instrument to continuously read samples
        and turns off any buffer or output triggering.
        """
        self.disable_buffer()
        self.disable_output_triggers()
        self.trigger_immediately()

    def set_trigger_counts(self, arm, trigger):
        """Set the number of counts for both the sweeps (arm) and the
        points in those sweeps (trigger), where the total number of
        points can not exceed 2500

        .. deprecated:: 0.16
           Use :attr:`~.trigger_count` and/or :attr:`~.arm_count`
        """
        warn(
            """Deprecated to use `Keithley2400.set_trigger_counts`.
            Use `Keithley2400.trigger_count` and/or `Keithley2400.arm_count`.""",
            FutureWarning,
        )
        if arm * trigger > 2500 or arm * trigger < 0:
            raise RangeException("Keithley 2400 has a combined maximum of 2500 counts")
        if arm < trigger:
            self.write(":ARM:COUN %d;:TRIG:COUN %d" % (arm, trigger))
        else:
            self.write(":TRIG:COUN %d;:ARM:COUN %d" % (trigger, arm))

    def set_timed_arm(self, interval):
        """Set up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points

        .. deprecated:: 0.16
           Set :attr:`~.arm_source` to "time" and control interval using :attr:`~.arm_timer`.
        """
        warn(
            """Deprecated to use `Keithley2400.set_timed_arm`.
            Set `Keithley2400.arm_source` to "timer" and control interval using
            `Keithley2400.arm_timer`.""",
            FutureWarning,
        )
        if interval > 99999.99 or interval < 0.001:
            raise RangeException("Keithley 2400 can only be time triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)

    def disable_output_trigger(self):
        """Disable the output trigger for the Trigger layer

        .. deprecated:: 0.16
           Set :attr:`~.trigger_output_event` to "none" to turn off just trigger layer output
           triggering, or use `~.disable_output_triggers` to disable both trigger and
           arm layer output triggering.
        """
        warn(
            """Deprecated to use `Keithley2400.disable_output_trigger`.
            Set `Keithley2400.trigger_output_event` to "none" to turn off just trigger layer output
            triggering, or use `Keithley2400.disable_output_triggers` to disable both trigger and
            arm layer output triggering.""",
            FutureWarning,
        )
        self.write(":TRIG:OUTP NONE")

    def output_trigger_on_external(self, line=1, after="DEL"):
        """Configure the output trigger on the specified trigger link
        line number, with the option of supplying the part of the
        measurement after which the trigger should be generated
        (default to delay, which is right before the measurement)

        :param line: A trigger line from 1 to 4
        :param after: An event string that determines when to trigger

        .. deprecated:: 0.16
           Use :attr:`~.trigger_output_event` and :attr:`~.trigger_output_line`.
        """
        warn(
            """Deprecated to use `Keithley2400.output_trigger_on_external`.
            Use `Keithley2400.trigger_output_event` and `Keithley2400.trigger_output_line`.""",
            FutureWarning,
        )
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    ######
    # UI #
    ######

    display_enabled = Instrument.control(
        ":DISPLAY:ENABLE?",
        ":DISPLAY:ENABLE %d",
        """Control whether the display of the sourcemeter is enabled (bool).""",
        values={True: 1, False: 0},
        map_values=True,
    )

    def beep(self, frequency, duration):
        """Sound a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")

    def triad(self, base_frequency, duration):
        """Sound a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)

    ########
    # MISC #
    ########

    wires = Instrument.control(
        ":SYSTEM:RSENSE?",
        ":SYSTEM:RSENSE %d",
        """Control the number of wires in use for sourcing voltage, measuring voltage,
        or measuring resistance (int, strictly 2 or 4).""",
        validator=strict_discrete_set,
        values={4: 1, 2: 0},
        map_values=True,
    )

    line_frequency = Instrument.control(
        ":SYSTEM:LFREQUENCY?",
        ":SYSTEM:LFREQUENCY %d",
        """Control the line frequency in Hertz (int, strictly 50 or 60).""",
        validator=strict_discrete_set,
        values=[50, 60],
        cast=int,
    )

    line_frequency_auto_enabled = Instrument.control(
        ":SYSTEM:LFREQUENCY:AUTO?",
        ":SYSTEM:LFREQUENCY:AUTO %d",
        """Control whether the auto line frequency is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    line_frequency_auto = Instrument.control(
        ":SYST:LFR:AUTO?",
        ":SYST:LFR:AUTO %d",
        """ Control the auto line frequency (boolean).

        .. deprecated:: 0.16
           Use :attr:`~.auto_zero_enabled` or :meth:`~.auto_zero_once`.""",
        values={True: 1, False: 0},
        map_values=True,
        get_process=_deprecate_process(
            "Deprecated to use `Keithley2400.line_frequency_auto`, "
            "use `Keithley2400.line_frequency_auto_enabled`",
        ),
        set_process=_deprecate_process(
            "Deprecated to use `Keithley2400.line_frequency_auto`, "
            "use `Keithley2400.line_frequency_auto_enabled`",
        ),
    )

    front_terminals_enabled = Instrument.control(
        ":ROUTE:TERMINALS?",
        ":ROUTE:TERMINALS %s",
        """Control whether the to route to the front terminals (bool).
        When True the front terminals are routed to and the rear disconnected,
        and vice-versa when False.""",
        validator=strict_discrete_set,
        values={True: "FRON", False: "REAR"},
        map_values=True,
    )

    def use_rear_terminals(self):  # Included for backwards compatibility
        """Enable the rear terminals for measurement, and disable the front terminals."""
        self.front_terminals_enabled = False

    def use_front_terminals(self):  # Included for backwards compatibility
        """Enable the front terminals for measurement, and disable the rear terminals."""
        self.front_terminals_enabled = True

    def shutdown(self):
        """Ensure that the current or voltage is turned to zero and disable the output."""
        log.info("Shutting down %s." % self.name)
        if self.source_mode == "current":
            self.ramp_to_current(0.0)
        else:
            self.ramp_to_voltage(0.0)
        self.stop_buffer()
        self.disable_source()
        super().shutdown()

    @property
    def error(self):
        """Get the next error from the queue.

        .. deprecated:: 0.15
            Use `next_error` instead.
        """
        warn("Deprecated to use `error`, use `next_error` instead.", FutureWarning)
        return self.next_error
