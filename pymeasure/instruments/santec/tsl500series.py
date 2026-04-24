#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from enum import IntEnum
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (
    strict_range,
    strict_discrete_range,
    strict_discrete_set,
)


class SweepStatus(IntEnum):
    STOPPED = 0
    RUNNING = 1
    STANDING_BY_TRIGGER = 3
    PREPARATION_FOR_SWEEP_START = 4


class SweepMode(IntEnum):
    STEPPED_ONE_WAY = 0
    CONTINUOUS_ONE_WAY = 1
    STEPPED_TWO_WAY = 2
    CONTINUOUS_TWO_WAY = 3


class SweepRouting(IntEnum):
    ONE_WAY = 0
    TWO_WAY = 1


class SweepPattern(IntEnum):
    STEPPED = 0
    CONTINUOUS = 1


def mode_to_pattern(mode):
    # For mode values 0 and 2, the pattern is STEPPED; for 1 and 3, it's CONTINUOUS.
    return SweepPattern(mode % 2)


def mode_to_routing(mode):
    # For mode values 0 and 1, the routing is ONE_WAY; for 2 and 3, it's TWO_WAY.
    return SweepRouting(mode // 2)


def combine_pattern_routing(pattern, routing):
    # The composite mode is determined by the routing times 2 plus the pattern.
    return SweepMode(routing.value * 2 + pattern.value)


class TSL500Series(SCPIMixin, Instrument):
    """Represents a Santec TSL-500 Series Tunable Laser and provides a high-level interface for
    interacting with the instrument."""

    def __init__(self, adapter, name="Santec TSL-500 Series", **kwargs):
        super().__init__(adapter, name, **kwargs)

    command_set = Instrument.control(
        ":SYSTem:COMMunicate:CODe?",
        ":SYSTem:COMMunicate:CODe %d",
        """Control the command set, "Legacy" or "SCPI".
        Legacy commands use units of nm and THz for wavelength and optical frequency respectively.
        SCPI commands use units of m and Hz for wavelength and optical frequency respectively.""",
        validator=strict_discrete_set,
        values={"Legacy": 0, "SCPI": 1},
        map_values=True,
    )

    # --- Optical power control ---

    output_enabled = Instrument.control(
        ":POWer:STATe?",
        ":POWer:STATe %d",
        """Control whether output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    power_unit = Instrument.control(
        ":POWer:UNIT?",
        ":POWer:UNIT %d",
        """Control the unit of power (str dBm or mW)""",
        validator=strict_discrete_set,
        values={"dBm": 0, "mW": 1},
        map_values=True,
    )

    power_setpoint = Instrument.control(
        ":POWer?",
        ":POWer %g",
        """Control the output optical power, units determined by :attr:`~.power_unit`.""",
        check_set_errors=True,
    )

    power = Instrument.measurement(
        ":POWer:ACTual?",
        """Measure the monitored optical power, units determined by :attr:`~.power_unit`.""",
    )

    # --- Wavelength control ---

    wavelength_min = Instrument.measurement(
        ":WAVelength:SWEep:RANGe:MINimum?",
        """Get the minimum wavelength in the configurable sweep range
        at the current sweep speed.""",
    )

    wavelength_max = Instrument.measurement(
        ":WAVelength:SWEep:RANGe:MAXimum?",
        """Get the maximum wavelength in the configurable sweep range
        at the current sweep speed.""",
    )

    wavelength_setpoint = Instrument.control(
        ":WAVelength?",
        ":WAVelength %g",
        """Control the output wavelength, units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    wavelength_start = Instrument.control(
        ":WAVelength:SWEep:STARt?",
        ":WAVelength:SWEep:STARt %g",
        """Control the sweep start wavelength, units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    wavelength_stop = Instrument.control(
        ":WAVelength:SWEep:STOP?",
        ":WAVelength:SWEep:STOP %g",
        """Control the sweep stop wavelength, units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    wavelength_step = Instrument.control(
        ":WAVelength:SWEep:STEP?",
        ":WAVelength:SWEep:STEP %g",
        """Control the sweep step wavelength when in step sweep mode,
        units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    # --- Optical frequency control ---

    frequency_min = Instrument.measurement(
        ":FREQuency:SWEep:RANGe:MINimum?",
        """Get the minimum frequency in the configurable sweep range
        at the current sweep speed.""",
    )

    frequency_max = Instrument.measurement(
        ":FREQuency:SWEep:RANGe:MAXimum?",
        """Get the maximum frequency in the configurable sweep range
        at the current sweep speed.""",
    )

    frequency_setpoint = Instrument.control(
        ":FREQuency?",
        ":FREQuency %g",
        """Control the output frequency, units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    frequency_start = Instrument.control(
        ":FREQuency:SWEep:STARt?",
        ":FREQuency:SWEep:STARt %g",
        """Control the sweep start frequency, units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    frequency_stop = Instrument.control(
        ":FREQuency:SWEep:STOP?",
        ":FREQuency:SWEep:STOP %g",
        """Control the sweep stop frequency, units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    frequency_step = Instrument.control(
        ":FREQuency:SWEep:STEP?",
        ":FREQuency:SWEep:STEP %g",
        """Control the sweep step frequency when in step sweep mode,
        units determined by :attr:`~.command_set`.""",
        check_set_errors=True,
    )

    # --- Sweep settings ---

    def start_sweep(self):
        """Start a single wavelength sweep."""
        self.write(":WAVelength:SWEep 1")

    def start_repeat(self):
        """Start repeated wavelength sweeps."""
        self.write(":WAVelength:SWEep:REPeat")

    def stop_sweep(self):
        """Stop the wavelength sweep."""
        self.write(":WAVelength:SWEep 0")

    sweep_staus = Instrument.measurement(
        "WAVelength:SWEep?",
        """Get the current sweep status as a SweepStatus enum.""",
        get_process=lambda v: SweepStatus(v),
    )

    sweep_mode = Instrument.control(
        ":WAVelength:SWEep:MODe?",
        ":WAVelength:SWEep:MODe %d",
        """Control the sweep mode as a SweepMode enum.""",
        get_process=lambda v: SweepMode(v),
        set_process=lambda v: v.value,
    )

    # Properties to independantly control sweep pattern (stepped vs continuous)
    # and routing (one-way vs two-way)

    @property
    def sweep_pattern(self) -> SweepPattern:
        """Control the sweep pattern as a SweepPattern enum."""
        return mode_to_pattern(self.sweep_mode)

    @sweep_pattern.setter
    def sweep_pattern(self, pattern: SweepPattern):
        current_routing = mode_to_routing(self.sweep_mode)
        self.sweep_mode = combine_pattern_routing(pattern, current_routing)

    @property
    def sweep_routing(self) -> SweepRouting:
        """Control the sweep routing as a SweepRouting enum."""
        return mode_to_routing(self.sweep_mode)

    @sweep_routing.setter
    def sweep_routing(self, routing: SweepRouting):
        current_pattern = mode_to_pattern(self.sweep_mode)
        self.sweep_mode = combine_pattern_routing(current_pattern, routing)

    sweep_speed = Instrument.control(
        ":WAVelength:SWEep:SPEed?",
        ":WAVelength:SWEep:SPEed %d",
        """Control the sweep speed, in nm/s (int one of 1, 2, 5, 10, 20, 50, 100, 200).""",
        validator=strict_discrete_set,
        values={1, 2, 5, 10, 20, 50, 100, 200},
    )

    sweep_dwell = Instrument.control(
        ":WAVelength:SWEep:DWELl?",
        ":WAVelength:SWEep:DWELl %g",
        """Control the wait time between consequent steps in step sweep mode, in s.
        Does not include time for wavelength tuning. (float strictly in range 0 to 999.9)""",
        validator=strict_range,
        values=[0, 999.9],
    )

    sweep_delay = Instrument.control(
        ":WAVelength:SWEep:DELay?",
        ":WAVelength:SWEep:DELay %g",
        """Control the wait time between consequent scans, in s.
        (float strictly in range 0 to 999.9)""",
        validator=strict_range,
        values=[0, 999.9],
    )

    sweep_cycles = Instrument.control(
        ":WAVelength:SWEep:CYCLes?",
        ":WAVelength:SWEep:CYCLes %d",
        """Control the number of sweep repetitions.""",
        validator=lambda v, vs: strict_discrete_range(v, vs, step=1),
        values=[0, 999],
    )

    sweep_count = Instrument.measurement(
        ":WAVelength:SWEep:COUNt?",
        """Get the current number of completed sweeps.""",
    )
