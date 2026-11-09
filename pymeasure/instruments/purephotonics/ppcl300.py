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

"""Driver for Pure Photonics PPCL300 tunable lasers."""

import re
from enum import IntEnum

from pymeasure.instruments import AdapterType, Instrument
from pymeasure.instruments.purephotonics.itla import ITLA, _signed
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class OperationMode(IntEnum):
    """Low noise modes of Pure Photonics lasers (register 0x90).

    Clean sweep requires a low noise mode (NO_DITHER or WHISPER).
    According to the Pure Photonics feature guide, some firmware versions treat NO_DITHER as
    WHISPER.
    """

    DITHER = 0  #: Standard operation with frequency dither (all control loops active).
    NO_DITHER = 1  #: No-dither operation ("clean mode").
    WHISPER = 2  #: Whisper mode, (almost) all control loops disabled, lowest noise.


class PPCL300(ITLA):
    """Pure Photonics PPCL300 tunable laser (C-band, also used on the PPCL500/550 boards).

    The laser has an OIF-ITLA-MSA interface (3.3 V serial, 9600 Bd 8N1 by default), usually
    accessed via an USB-serial converter or the PPEB evaluation board.

    .. code-block:: python

        from pymeasure.instruments.purephotonics import PPCL300

        laser = PPCL300("ASRL/dev/ttyUSB0::INSTR")
        print(laser.id)
        laser.power_setpoint = 13  # dBm
        laser.first_channel_frequency = 193.5e12  # Hz, output has to be disabled
        laser.channel = 1
        laser.emission_enabled = True
        laser.wait_until_ready()
        print(laser.frequency, laser.power)

        # clean sweep (firmware 8.0.9 and later)
        laser.operation_mode = laser.OperationMode.WHISPER  # low noise mode
        laser.wait_until_ready()
        laser.sweep_range = 20e9  # Hz
        laser.sweep_rate = 5e9  # Hz/s
        laser.sweep_enabled = True
        print(laser.sweep_offset)
        laser.sweep_enabled = False

        laser.emission_enabled = False

    The features beyond the MSA depend on the firmware line of the laser, according to the
    Pure Photonics feature guide:

    ==========================  ===================
    Feature                     Firmware
    ==========================  ===================
    Low noise modes             8.0.x, 8.1.x, 8.2.x
    Clean sweep (up to 75 GHz)  8.0.9 and later
    ==========================  ===================

    Implemented are the MSA functions, the low noise modes and the clean sweep. Other Pure
    Photonics features (clean jump, clean scan, extended clean sweep) need laser specific
    calibration files and are not implemented.
    Unsupported registers raise an :class:`.ITLAExecutionError` with error :attr:`.ITLAError.RNI`.
    """

    OperationMode = OperationMode

    def __init__(self, adapter: AdapterType, name: str = "Pure Photonics PPCL300", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self._firmware_version: str | None = None

    @property
    def firmware_version(self) -> str:
        """Get the firmware version, e.g. ``"8.0.9"`` (str).

        Taken from the ``FW`` field of :attr:`release` and cached after the first query."""
        if self._firmware_version is None:
            match = re.search(r"FW\s*([0-9A-Za-z]+\.[0-9A-Za-z]+\.[0-9A-Za-z]+)", self.release)
            if match is None:
                raise ValueError(f"No firmware version in release '{self.release}'.")
            self._firmware_version = match.group(1)
        return self._firmware_version

    @property
    def tec_current(self) -> float:
        """Measure the TEC current in A (float)."""
        return self.currents[0]

    @property
    def diode_current(self) -> float:
        """Measure the laser diode current in A (float)."""
        return self.currents[1]

    @property
    def diode_temperature(self) -> float:
        """Measure the laser diode temperature in °C (float)."""
        return self.temperatures[0]

    @property
    def case_temperature(self) -> float:
        """Measure the case temperature in °C (float)."""
        return self.temperatures[1]

    operation_mode = Instrument.control(
        "R,0x90",
        "W,0x90,%d",
        """Control the low noise operation mode (:class:`OperationMode`).

        Changing the mode can take several seconds, use :meth:`wait_until_ready`.""",
        validator=strict_discrete_set,
        values=tuple(OperationMode),
        get_process=lambda v: OperationMode(int(v)),
        set_process=int,
    )

    # Clean sweep (firmware 8.0.9 and later)
    sweep_range = Instrument.control(
        "R,0xE4",
        "W,0xE4,%d",
        """Control the clean sweep range in Hz (float, resolution 1 GHz).

        The module accepts at most 75 GHz; larger values raise an :class:`.ITLAExecutionError`
        (RVE).""",
        get_process=lambda v: v * 1e9,
        set_process=lambda v: round(v / 1e9),
    )

    sweep_enabled = Instrument.control(
        "R,0xE5",
        "W,0xE5,%d",
        """Control whether the clean sweep is running (bool).

        Requires enabled output and a low noise :attr:`operation_mode`. The laser ramps to
        +:attr:`sweep_range`/2, then to -:attr:`sweep_range`/2 and repeats until disabled.
        After stopping, the frequency returns to the center frequency. The first seconds after
        starting may show transients of frequency and power.""",
        validator=strict_discrete_set,
        values=(True, False),
        get_process=lambda v: bool(int(v)),
        set_process=int,
    )

    sweep_offset = Instrument.measurement(
        "R,0xE6",
        """Measure the current frequency offset of the clean sweep in Hz (float, resolution
        100 MHz).

        Only meaningful while the sweep is running. The offset sweeps between about
        +/- :attr:`sweep_range` / 2.""",
        # The operating guide (vE) describes the encoding (value - 2000) * 0.1 GHz, but the newer
        # feature guide and firmware 8.0.9 use a signed value in units of 0.1 GHz.
        get_process=lambda v: _signed(v) * 1e8,
    )

    sweep_rate = Instrument.setting(
        "W,0xF1,%d",
        """Set the maximum clean sweep rate in Hz/s (float, resolution 1 MHz/s).

        Set the rate before enabling the sweep; without a written rate, the sweep may run far too
        slowly or drift beyond the range. The actual rate can be about 10 % below the setting.
        Pure Photonics recommends 20 GHz/s. Only available in the clean sweep firmware (8.0.x),
        the register cannot be read. In the clean scan firmware, this register sets a filter
        temperature instead.""",
        # Not register 0xE7 as for the PPCL600/700: writing it on a PPCL300 changes the sweep
        # behavior in an undocumented way until the laser is power cycled.
        validator=strict_range,
        values=(0, 65.535e9),
        set_process=lambda v: round(v / 1e6),
    )
