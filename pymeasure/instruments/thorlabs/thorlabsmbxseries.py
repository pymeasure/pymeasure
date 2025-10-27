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

from pymeasure.instruments import Channel, Instrument, SCPIMixin
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


class ThorlabsMBXSeriesMZM(Channel):
    """ThorlabsMBXSeries channel for control of the Mach-Zender Modulator (MZM)."""

    def calibrate(self):
        """Run a MZM bias calibration."""
        self.ask("MZM:RESET")

    is_calibrating = Instrument.measurement(
        "MZM:CALIBRATING?",
        """Get whether the MZM is currently being calibrated (bool).""",
        cast=bool,
    )

    is_stable = Instrument.measurement(
        "MZM:SETPOINT?",
        """Get whether the MZM is stable and at the setpoint (bool).""",
        cast=bool,
    )

    mode = Instrument.control(
        "MZM:MODE?",
        "MZM:MODE: %d",
        """Control the MZM bias mode (:class:`MzmMode` enum).""",
        validator=strict_discrete_set,
        values=MzmMode,
        get_process=lambda v: MzmMode(v),
    )

    ratio_setpoint = Instrument.control(
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

    voltage_setpoint = Instrument.control(
        "MZM:HOLD:VOLTAGE?",
        "MZM:HOLD:VOLTAGE: %d",
        """Control the MZM voltage setpoint, in V, when `mzm_mode` is set to MzmMode.MANUAL
        (float strictly in range -10 to 10).""",
        validator=strict_range,
        values=(-10, 10),
        get_process=lambda v: v / 1000,
        set_process=lambda v: round(v * 1000),
    )

    voltage = Instrument.measurement(
        "MZM:VOLTAGE?",
        """Measure the current MZM bias voltage, in V (float).""",
    )

    power = Instrument.measurement(
        "MZM:TAP:MW?",
        """Measure the MZM output optical power, in mW (float).""",
    )


class ThorlabsMBXSeriesVOA(Channel):
    """ThorlabsMBXSeries channel for control of the Variable Optical Attenuator (VOA)."""

    enabled = Instrument.control(
        "VOA:POWER?",
        "VOA:POWER: %d",
        """Control whether the VOA is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    is_stable = Instrument.measurement(
        "VOA:SETPOINT?",
        """Get whether the VOA attenuation is within 0.1dB of the setpoint (bool).""",
        cast=bool,
    )

    @property
    def mode(self):
        """Control the VOA mode (:class:`VoaMode` enum)."""
        return VoaMode(int(self.ask("VOA:MODE?")))

    @mode.setter
    def mode(self, v):
        strict_discrete_set(v, VoaMode)
        # Ask as "VOA:MODE: {0 or 1}" returns "1" on receipt of command
        self.ask(f"VOA:MODE: {v.value}")

    attenuation_setpoint = Instrument.control(
        "VOA:ATTEN?",
        "VOA:ATTEN: %g",
        """Control the VOA optical attenuation setpoint, in dB
        (float strictly in range 0.5 to 20)""",
        validator=strict_range,
        values=(0.5, 20),
    )

    attenuation = Instrument.measurement(
        "VOA:MEASURED?",
        """Measure the VOA optical attenuation, in dB (float).""",
    )

    attenuation_error = Instrument.measurement(
        "VOA:ERROR?",
        """Measure the difference between the setpoint and the measured value
        for the VOA optical attenuation, in dB (float).""",
    )

    power_setpoint = Instrument.control(
        "VOA:OUTPUT:MW?",
        "VOA:OUTPUT:MW: %g",
        """Control the VOA output power setpoint, in mW (float strictly in range 0.01 to 100).""",
        validator=strict_range,
        values=(0.01, 100),
    )

    power = Instrument.measurement(
        "VOA:TAP:MW?",
        """Measure the VOA output optical power, in mW (float).""",
    )


class ThorlabsMBXSeriesRGB(Channel):
    """ThorlabsMBXSeries channel for control of the asethetic RGB under-chassis lighting."""

    mode = Instrument.control(
        "RGB:POWER?",
        "RGB:POWER: %d",
        """Control the under-chassis LED accent lighting mode (:class:`RgbPowerMode` enum).""",
        validator=strict_discrete_set,
        values=RgbPowerMode,
        get_process=lambda v: RgbPowerMode(v),
    )

    red = Instrument.control(
        "RGB:RED?",
        "RGB:RED: %d",
        """Control the brightness of the red under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )

    green = Instrument.control(
        "RGB:GREEN?",
        "RGB:GREEN: %d",
        """Control the brightness of the green under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )

    blue = Instrument.control(
        "RGB:BLUE?",
        "RGB:BLUE: %d",
        """Control the brightness of the blue under-chassis accent lighting LEDs
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )

    @property
    def rgb(self):
        """Control the brightness of the red, green, and blue under-chassis accent lighting LEDs
        (tuple of ints, strictly in range 0 to 100)."""
        return (self.red, self.green, self.blue)

    @rgb.setter
    def rgb(self, vals):
        self.red, self.green, self.blue = vals

    white = Instrument.control(
        "RGB:WHITE?",
        "RGB:WHITE: %d",
        """Control the brightness of the white under-chassis accent lighting
        (int, strictly in range 0 to 100).""",
        validator=lambda v, vs: strict_discrete_range(v, vs, 1),
        values=(0, 100),
    )


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

        kwargs.setdefault("timeout", 1000)
        super().__init__(
            adapter, name, baud_rate=115200, write_termination="\r", read_termination="\r", **kwargs
        )

    mzm = Instrument.ChannelCreator(ThorlabsMBXSeriesMZM, "")
    voa = Instrument.ChannelCreator(ThorlabsMBXSeriesVOA, "")
    rgb = Instrument.ChannelCreator(ThorlabsMBXSeriesRGB, "")
