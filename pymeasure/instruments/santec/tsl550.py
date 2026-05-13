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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set
from pymeasure.instruments.santec.tsl500series import (  # noqa: F401
    SweepMode,
    SweepPattern,
    SweepRouting,
    SweepStatus,
    mode_to_pattern,
    mode_to_routing,
    combine_pattern_routing,
    TSL500Series,
)


class TSL550(TSL500Series):
    """Represents the Santec TSL-550 Tunable Laser and provides a high-level interface for
    interacting with the instrument.

    Unless otherwise stated, units of wavelength are in nm, and THz for optical frequency."""

    def __init__(self, adapter, name="Santec TSL-550", **kwargs):
        super().__init__(adapter, name, **kwargs)

    laser_enabled = Instrument.control(
        ":POWer:STATe?",
        ":POWer:STATe %d",
        """Control whether laser diode is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    output_enabled = Instrument.control(
        ":POWer:SHUTter?",
        ":POWer:SHUTter %d",
        """Control whether output is enabled through the internal shutter (bool).""",
        validator=strict_discrete_set,
        values={True: 0, False: 1},
        map_values=True,
    )

    sweep_speed = Instrument.control(
        ":WAVelength:SWEep:SPEed?",
        ":WAVelength:SWEep:SPEed %f",
        """Control the sweep speed, in nm/s
        (float strictly in range 0.5 to 100; rounds to 1 decimal place).""",
        validator=strict_range,
        values=[0.5, 100],
        set_process=lambda v: round(v, 1),
    )
