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
    ATTENUATION = 0
    POWER = 1


class RgbPowerMode(IntEnum):
    OFF = 0
    RGB = 1
    WHITE = 2


class ThorlabsMBXSeries(SCPIMixin, Instrument):
    """Represents Thorlabs MBX Series Modulator Bias Controllers.

    .. note::
       - Serial communication via the RS-232 port requires a null-modem connector.
       - Serial communication via the USB port requires a Silicon Labs® USB to UART DLL.

    Abbreviations:
        MZM - Mach Zender Modulator
        VOA - Variable Optical Attenuator
    """

    def __init__(self, adapter, name="ThorlabsMBXSeries modulator bias controller", **kwargs):

        kwargs.setdefault("baud_rate", 115200)
        kwargs.setdefault("timeout", 1)
        kwargs.setdefault("write_termination", "\r")
        kwargs.setdefault("read_termination", "\r")
        super().__init__(adapter, name, **kwargs)

    # === MACH-ZENDER INTERFEROMETER (MZM) ===

    def calibrate_mzm(self):
        """Run a MZM bias calibration."""
        self.ask("MZM:RESET")

    mzm_calibrating = Instrument.measurement(
        "MZM:CALIBRATING?",
        """Get whether the MZM is currently being calibrated (bool).""",
        cast=bool,
    )

    mzm_stable = Instrument.measurement(
        "MZM:SETPOINT?",
        """Get whether the MZM is stable and at the setpoint (bool).""",
        cast=bool,
    )

    mzm_mode = Instrument.control(
        "MZM:MODE?",
        "MZM:MODE: %d",
        """Control the MZM bias mode (MzmMode enum).""",
        get_process=lambda v: MzmMode(v),
        set_process=lambda v: v.value,
    )

    mzm_ratio_setpoint = Instrument.control(
        "MZM:HOLD:RATIO?",
        "MZM:HOLD:RATIO: %d",
        """Control the input to output power ratio setpoint
        when `mzm_mode` is set to `MzmMode.AUTOPOWERPOS` or `MzmMode.AUTOPOWERNEG`
        (float strictly in range 2.5 to 100).""",
        validator=strict_range,
        values=(2.5, 100),
        get_process=lambda v: v / 100,
        set_process=lambda v: round(v * 100),
    )

    mzm_voltage_setpoint = Instrument.control(
        "MZM:HOLD:VOLTAGE?",
        "MZM:HOLD:VOLTAGE: %d",
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

    voa_stable = Instrument.measurement(
        "VOA:SETPOINT?",
        """Get whether the VOA attenuation is withing 0.1dB of the setpoint (bool).""",
        cast=bool,
    )

    # Handled differently as "VOA:MODE: {0 or 1}" returns "1" on receipt of command

    @property
    def voa_mode(self):
        """Control the VOA mode (VoaMode enum)."""
        return MzmMode(int(self.ask("VOA:MODE?")))

    @voa_mode.setter
    def voa_mode(self, v):
        self.ask(f"VOA:MODE: {v.value}")

    voa_attenuation_setpoint = Instrument.control(
        "VOA:ATTEN?",
        "VOA:ATTEN: %g",
        """Control the VOA optical attenuation setpoint, in dB
        (float strictly in range 0.5 to 20)""",
        validator=strict_range,
        values=(0.5, 20),
    )

    voa_attenuation = Instrument.measurement(
        "VOA:MEASURED?",
        """Measure the VOA optical attenuation, in dB (float).""",
    )

    voa_attenuation_error = Instrument.measurement(
        "VOA:ERROR?",
        """Measure the difference between the setpoint and the measured value
        for the VOA optical attenuation, in dB (float).""",
    )

    voa_power_setpoint = Instrument.control(
        "VOA:OUTPUT:MW?",
        "VOA:OUTPUT:MW: %g",
        """Control the VOA output power setpoint, in mW.""",
        validator=strict_range,
        values=(0.01, 100),
    )

    voa_power = Instrument.measurement(
        "VOA:TAP:MW?",
        """Measure the VOA output optical power, in mW (float).""",
    )

    # === RGB CONTROL ===
    # This section is excluded from coverage because it is purely aesthetic

    rgb_power = Instrument.control(
        "RGB:POWER:?",
        "RGB:POWER: %d",
        """Control the under-chassis LED accent lighting mode (RgbPowerMode enum).""",
        get_process=lambda v: RgbPowerMode(v),
        set_process=lambda v: v.value,
    )  # pragma: no cover

    rgb_red = Instrument.control(
        "RGB:RED?",
        "RGB:RED: %d",
        """Control the brightness of the red under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )  # pragma: no cover

    rgb_green = Instrument.control(
        "RGB:GREEN?",
        "RGB:GREEN: %d",
        """Control the brightness of the green under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )  # pragma: no cover

    rgb_blue = Instrument.control(
        "RGB:BLUE?",
        "RGB:BLUE: %d",
        """Control the brightness of the blue under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )  # pragma: no cover

    rgb_white = Instrument.control(
        "RGB:BLUE?",
        "RGB:BLUE: %d",
        """Control the brightness of the white under-chassis accent lighting
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )  # pragma: no cover

    def disco(self, duration=10, pause=0.5):  # pragma: no cover
        self.rgb_power = RgbPowerMode.RGB

        t0 = time()
        while time() < t0 + duration:
            r, g, b = colorsys.hsv_to_rgb(random.random(), 1, 1)
            self.rgb_red, self.rgb_green, self.rgb_blue = [round(x * 100) for x in (r, g, b)]
            sleep(pause)

        self.rgb_power = RgbPowerMode.OFF

    def rainbow(self, duration=10, pause=0):  # pragma: no cover
        self.rgb_power = RgbPowerMode.RGB

        t0 = time()
        h = 0
        while time() < t0 + duration:
            r, g, b = colorsys.hsv_to_rgb(h % 600 / 600, 1, 1)
            self.rgb_red, self.rgb_green, self.rgb_blue = [round(x * 100) for x in (r, g, b)]
            h += 1
            sleep(pause)

        self.rgb_power = RgbPowerMode.OFF
