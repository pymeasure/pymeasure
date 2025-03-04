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

from pymeasure.instruments.validators import strict_range, strict_discrete_set


class TSL570(SCPIMixin, Instrument):
    """Represents the Santec TSL-570 Tunable Laser and provides a high-level interface for
    interacting with the instrument."""

    # TODO: I am unsure of the implementation of the validators. I have implemented them according
    #       to my interpretation of the documentation, but this will need to be tested with the
    #       instrument to validate this.

    def __init__(self, adapter, name="Yokogawa AQ3670D OSA", **kwargs):
        super().__init__(adapter, name, **kwargs)
        Instrument.write(self, ":SYSTem:COMMunicate:CODe 1")  # Set the device to use SCPI commands

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

    wavelength_start = Instrument.control(
        ":WAVelength:SWEep:STARt?",
        ":WAVelength:SWEep:STARt %e",
        """Control the sweep start wavelength, in m.""",
    )

    wavelength_stop = Instrument.control(
        ":WAVelength:SWEep:STOP?",
        ":WAVelength:SWEep:STOP %e",
        """Control the sweep stop wavelength, in m.""",
    )

    wavelength = Instrument.control(
        ":WAVelength?",
        ":WAVelength %e",
        """Control the output wavelength, in m.""",
    )

    # --- Optical frequency control ---

    frequency_min = Instrument.measurement(
        ":FREQency:SWEep:RANGe:MINimum?",
        """Get the minimum frequency in the configurable sweep range
        at the current sweep speed.""",
    )

    frequency_max = Instrument.measurement(
        ":FREQency:SWEep:RANGe:MAXimum?",
        """Get the maximum frequency in the configurable sweep range
        at the current sweep speed.""",
    )

    frequency_start = Instrument.control(
        ":FREQency:SWEep:STARt?",
        ":FREQency:SWEep:STARt %e",
        """Control the sweep start frequency, in m.""",
    )

    frequency_stop = Instrument.control(
        ":FREQency:SWEep:STOP?",
        ":FREQency:SWEep:STOP %e",
        """Control the sweep stop frequency, in m.""",
    )

    frequency = Instrument.control(
        ":FREQency?",
        ":FREQency %e",
        """Control the output frequency, in m.""",
    )

    # --- Optical power control ---

    shutter_closed = Instrument.control(
        ":POWer:SHUTter?",
        ":POWer:SHUTter %d",
        """A boolean property that controls whether shutter is closed.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    power_unit = Instrument.control(
        ":POWer:UNIT?",
        ":POWer:UNIT %d",
        """Control the unit of power, dBm or mW.""",
        validator=strict_discrete_set,
        values={"dBm": 0, "mW": 1},
        map_values=True,
    )

    power_setpoint = Instrument.control(
        ":POWer?",
        ":Power %e",
        """Control the output optical power, units defined by power_unit.""",
    )

    power_reading = Instrument.measurement(
        ":POWer:ACTual?",
        """Measure the monitored optical power, units defined by power_unit.""",
    )

    # TODO
    # sweep_mode
    # sweep_speed
    # sweep_dwell
    # sweep_delay
    # single_sweep
    # repeat_sweep
    # sweep_status


if __name__ == "__main__":
    laser = TSL570("GPIB1::8::INSTR")

    laser.wavelength = 1500e-9
