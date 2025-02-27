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

from pymeasure.instruments.validators import strict_discrete_set


class TSL570(SCPIMixin, Instrument):
    """Represents the Santec TSL-570 Tunable Laser and provides a high-level interface for
    interacting with the instrument."""

    def __init__(self):
        """Set the device to use SCPI commands."""
        Instrument.write(self, ":SYSTem:COMMunicate:CODe 1")

    shutter_closed = Instrument.control(
        ":POWer:SHUTter?",
        ":POWer:SHUTter %d",
        """A boolean property that controls whether shutter is closed.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    wavelength = Instrument.control(
        ":WAVelength?", ":WAVelength %e", """Set the output wavelength, in m."""
    )

    frequency = Instrument.control(
        ":FREQuency?", "FREQuency %e", """Set the output wavelength in optical frequency, in Hz."""
    )

    # TODO
    # power_setpoint
    # power_reading
    # power_unit
    # wavelength_start
    # wavelength_stop
    # wavelength_step
    # frequency_start
    # frequency_stop
    # frequency_step
    # sweep_mode
    # sweep_speed
    # sweep_dwell
    # sweep_delay
    # single_sweep
    # repeat_sweep
    # sweep_status
