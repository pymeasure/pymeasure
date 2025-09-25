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

from enum import IntEnum

import random
import colorsys
from time import time, sleep

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (
    strict_range,
    strict_discrete_range,
    strict_discrete_set,
)


class MzmMode(IntEnum):
    OFF = 0
    AUTOPEAK = 1
    AUTONULL = 2
    AUTOQUADPOS = 3
    AUTOQUADNEG = 4
    HOLDQUADPOS = 5
    HOLDQUADNEG = 6
    MANUAL = 7
    AUTOPOWERPOS = 8
    AUTOPOWERNEG = 9


class VoaMode(IntEnum):
    CONSTATTEN = 0
    CONSTPOWER = 1


class LedPowerMode(IntEnum):
    OFF = 0
    RGB = 1
    WHITE = 2


class ThorlabsMBXSeries(SCPIMixin, Instrument):
    """Represents Thorlabs MBX Series Modulator Bias Controllers.

    Abbreviations:
        MZM - Mach Zender Modulator
        VOA - Variable Optical Attenuator
    """

    def __init__(self, adapter, name="ThorlabsMBXSeries modulator bias controller", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # === MACH-ZENDER INTERFEROMETER (MZM) ===

    def calibrate_mzm(self):
        """Run a MZM bias calibration."""
        self.ask("MZM:RESET")

    is_mzm_calibrating = Instrument.measurement(
        "MZM:CALIBRATING?",
        """Get whether the MZM is currently being calibrated (bool).""",
        cast=bool,
    )

    is_mzm_stable = Instrument.measurement(
        "MZM:SETPOINT?",
        """Get whether the MZM is stable and at the setpoint.""",
        cast=bool,
    )

    mzm_mode = Instrument.control(
        "MZM:MODE?",
        "MZM:MODE %d",
        """Control the MZM bias mode as an MzmMode enum.""",
        get_process=lambda v: MzmMode(v),
        set_process=lambda v: v.value,
    )

    mzm_ratio_setpoint = Instrument.control(
        "MZM:HOLD:RATIO?",
        "MZM:HOLD:RATIO %d",
        """Control the input to output power ratio setpoint
        when `mzm_mode` is set to `MzmMode.AUTOPOWERPOS` or `MzmMode.AUTOPOWERNEG`
        (float strictly in range 2.5 to 100).""",
        validator=strict_range,
        values=(2.5, 100),
        get_process=lambda v: v / 100,
        set_process=lambda v: round(v * 100),
    )

    mzm_voltage_setpoint = Instrument.control(
        "MZM:HOLD:RATIO?",
        "MZM:HOLD:RATIO %d",
        """Control the MZM voltage setpoint, in V, when `mzm_mode` is set to MzmMode.MANUAL
        (float strictly in range -10 to 10).""",
        validator=strict_range,
        values=(-10, 10),
        get_process=lambda v: v / 1000,
        set_process=lambda v: round(v * 1000),
    )

    mzm_voltage = Instrument.measurement(
        "MZM:VOLTAGE?",
        """Measure the current MZM bias voltage, in V (float).""",
    )

    mzm_power = Instrument.measurement(
        "MZM:TAP:MW?",
        """Measure the MZM output optical power, in mW (float).""",
    )

    # === VARIABLE OPTICAL ATTENUATOR (VOA) ===

    voa_enabled = Instrument.control(
        "VOA:POWER?",
        "VOA:POWER: %d",
        """Control whether the VOA is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    is_voa_stable = Instrument.measurement(
        "VOA:SETPOINT?",
        """Get whether the VOA attenuation is withing 0.1dB of the setpoint (bool).""",
        cast=bool,
    )

    # TODO: `VOA:MODE %d` returns `1` on receipt of either command. Could this be a problem?
    voa_mode = Instrument.control(
        "VOA:MODE?",
        "VOA:MODE %d",
        """Control the VOA mode as a VoaMode enum.""",
        get_process=lambda v: MzmMode(v),
        set_process=lambda v: v.value,
    )

    voa_attenuation_setpoint = Instrument.control(
        "VOA:ATTEN?",
        "VOA:ATTEN %g",
        """Control the VOA optical attenuation setpoint, in dB
        (float strictly in range 0.5 to 20)""",
        validator=strict_range,
        values=(0.5, 20),
    )

    voa_attenuation = Instrument.measurement(
        "VOA:ERROR?",
        """Measure the VOA optical attenuation, in dB (float).""",
    )

    voa_attenuation_error = Instrument.measurement(
        "VOA:MEASURED?",
        """Measure the difference between the setpoint and the measured value
        for the VOA optical attenuation, in dB (float).""",
    )

    voa_power_setpoint = Instrument.control(
        "VOA:OUTPUT:MW?",
        "VOA:OUTPUT: %g",
        """Control the VOA output power setpoint, in mW.""",
        validator=strict_range,
        values=(0.01, 100),
    )

    voa_power = Instrument.measurement(
        "VOA:TAP:MW?",
        """Measure the VOA output optical power, in mW (float).""",
    )

    # === THE MOST IMPORTANT PART OF THE INSTRUMENT ===

    rgb_power = Instrument.control(
        "RGB:POWER:?",
        "RGB:POWER %d",
        """Control the under-chassis LED accent lighting mode as an LedPowerMode enum.""",
        get_process=lambda v: LedPowerMode(v),
        set_process=lambda v: v.value,
    )

    rgb_red = Instrument.control(
        "RGB:RED?",
        "RGB:RED %d",
        """Control the brightness of the red under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=strict_discrete_range,
        values=(0, 100),
        step=1,
    )

    rgb_green = Instrument.control(
        "RGB:GREEN?",
        "RGB:GREEN %d",
        """Control the brightness of the green under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=strict_discrete_range,
        values=(0, 100),
        step=1,
    )

    rgb_blue = Instrument.control(
        "RGB:BLUE?",
        "RGB:BLUE %d",
        """Control the brightness of the blue under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=strict_discrete_range,
        values=(0, 100),
        step=1,
    )

    rgb_white = Instrument.control(
        "RGB:BLUE?",
        "RGB:BLUE %d",
        """Control the brightness of the white under-chassis accent lighting
        (int, strictly in range 0 to 100).""",
        validator=strict_discrete_range,
        values=(0, 100),
        step=1,
    )

    def disco_mode(self, duration=10, pause=0.5):
        self.rgb_power = LedPowerMode.RGB

        t0 = time()
        while time() < t0 + duration:
            r, g, b = colorsys.hsv_to_rgb(random.random(), 1, 1)
            self.rgb_red, self.rgb_green, self.rgb_blue = [int(x * 100) for x in (r, g, b)]
            sleep(pause)

        self.rgb_power = LedPowerMode.OFF
