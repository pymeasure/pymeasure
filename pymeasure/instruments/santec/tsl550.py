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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from pymeasure.instruments.santec.tsl570 import TSL570


class TSL550(TSL570):
    """Represents the Santec TSL-550 Tunable Laser and provides a high-level interface for
    interacting with the instrument."""

    def __init__(self, adapter, name="Santec TSL-550", **kwargs):
        super().__init__(adapter, name, **kwargs)

    @property
    def command_set(self):
        """Get the command set. The TSL-550 only accepts legacy commands.
        Legacy commands use units of nm and THz for wavelength and optical frequency
        respectively."""
        return "Legacy"

    @property
    def wavelength_min(self):
        """Control the minimum wavelength (not avaliable)."""
        raise AttributeError("TSL550.wavelength_min is not available.")

    @property
    def wavelength_max(self):
        """Control the maximum wavelength (not avaliable)."""
        raise AttributeError("TSL550.wavelength_max is not available.")

    @property
    def frequency_min(self):
        """Control the minimum frequency (not avaliable)."""
        raise AttributeError("TSL550.frequency_min is not available.")

    @property
    def frequency_max(self):
        """Control the maximum frequency (not avaliable)."""
        raise AttributeError("TSL550.frequency_max is not available.")

    sweep_speed = Instrument.control(
        ":WAVelength:SWEep:SPEed?",
        ":WAVelength:SWEep:SPEed %d",
        """Control the sweep speed, in nm/s
        (float strictly in range 0.5 to 100; rounds to 1 decimal place).""",
        validator=strict_range,
        values=[0.5, 100],
        set_process=lambda v: round(v, 1),
    )
