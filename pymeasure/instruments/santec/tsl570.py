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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (
    strict_range,
    strict_discrete_range,
    strict_discrete_set,
)


class InstrumentError(Exception):
    """Exception raised for errors reported by the instrument."""


class TSL570(SCPIMixin, Instrument):
    """Represents the Santec TSL-570 Tunable Laser and provides a high-level interface for
    interacting with the instrument."""

    def __init__(self, adapter, name="Santec TSL-570", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.write(":SYSTem:COMMunicate:CODe 1")  # Set the device to use SCPI commands
        self.check_errors()  # Clear the error queue

    def check_instr_errors(self):
        """Checks the instrument for errors, and raises an exeption if any are present."""
        errors = self.check_errors()
        if errors:
            raise InstrumentError(errors)

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
        ":Power %e",
        """Control the output optical power, units defined by power_unit.""",
        check_instr_errors=True,
    )

    power_reading = Instrument.measurement(
        ":POWer:ACTual?",
        """Measure the monitored optical power, units defined by power_unit.""",
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

    wavelength = Instrument.control(
        ":WAVelength?",
        ":WAVelength %e",
        """Control the output wavelength, in m.""",
        check_instr_errors=True,
    )

    wavelength_start = Instrument.control(
        ":WAVelength:SWEep:STARt?",
        ":WAVelength:SWEep:STARt %e",
        """Control the sweep start wavelength, in m.""",
        check_instr_errors=True,
    )

    wavelength_stop = Instrument.control(
        ":WAVelength:SWEep:STOP?",
        ":WAVelength:SWEep:STOP %e",
        """Control the sweep stop wavelength, in m.""",
        check_instr_errors=True,
    )

    wavelength_step = Instrument.control(
        ":WAVelength:SWEep:STEP?",
        ":WAVelength:SWEep:STEP %e",
        """Control the sweep step wavelength when in step sweep mode, in m.""",
        check_instr_errors=True,
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

    frequency = Instrument.control(
        ":FREQuency?",
        ":FREQuency %e",
        """Control the output frequency, in m.""",
        check_instr_errors=True,
    )

    frequency_start = Instrument.control(
        ":FREQuency:SWEep:STARt?",
        ":FREQuency:SWEep:STARt %e",
        """Control the sweep start frequency, in m.""",
        check_instr_errors=True,
    )

    frequency_stop = Instrument.control(
        ":FREQuency:SWEep:STOP?",
        ":FREQuency:SWEep:STOP %e",
        """Control the sweep stop frequency, in m.""",
        check_instr_errors=True,
    )

    frequency_step = Instrument.control(
        ":FREQuency:SWEep:STEP?",
        ":FREQuency:SWEep:STEP %e",
        """Control the sweep step frequency when in step sweep mode, in m.""",
        check_instr_errors=True,
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
        """Get the current sweep status, "Stopped", "Running", "Standing by trigger",
        or "Preparation for sweep start".""",
        values={
            "Stopped": 0,
            "Running": 1,
            "Standing by trigger": 3,
            "Preparation for sweep start": 4,
        },
        map_values=True,
    )

    sweep_mode = Instrument.control(
        ":WAVelength:SWEep:MODe?",
        ":WAVelength:SWEep:MODe %d",
        """Control the sweep mode.""",
        validator=strict_discrete_set,
        values={
            "Stepped One-way": 0,
            "Continuous One-way:": 1,
            "Stepped Two-way": 2,
            "Continuous Two-way": 3,
        },
        map_values=True,
    )

    # Properties to independantly control sweep pattern (stepped vs continuous)
    # and routing (one-way vs two-way)

    @property
    def sweep_pattern(self):
        """Control the sweep pattern, "Stepped" or "Continuous"."""
        return self.sweep_mode.split()[0]

    @sweep_pattern.setter
    def sweep_pattern(self, pattern):
        self.sweep_mode = " ".join([pattern, self.sweep_mode.split()[1]])

    @property
    def sweep_routing(self):
        """Control the sweep routing, "One-way" or "Two-way"."""
        return self.sweep_mode.split()[1]

    @sweep_routing.setter
    def sweep_routing(self, routing):
        self.sweep_mode = " ".join([self.sweep_mode.split()[0], routing])

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
        ":WAVelength:SWEep:COUNt?", """Get the current number of completed sweeps."""
    )
