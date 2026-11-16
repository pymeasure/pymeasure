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

import os
import re
import warnings
from collections import Counter
from enum import IntEnum
from functools import cached_property
from pathlib import Path

from pymeasure.instruments import AdapterType, Instrument
from pymeasure.instruments.purephotonics.itla import (
    ITLA,
    ITLAError,
    ITLAExecutionError,
    _signed,
)
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

        # clean jump (clean jump firmware) with the calibration (.map) file of the laser
        laser.load_clean_jump_map("CRTN000001_1000_1_12_0_0.map")  # sets 10 dBm
        laser.emission_enabled = True
        laser.wait_until_ready()
        laser.operation_mode = laser.OperationMode.NO_DITHER
        laser.wait_until_ready()
        laser.clean_jump(192.05e12)  # sled temperature and diode current from the map
        print(laser.clean_jump_targets)  # (191.5e12, 191.55e12, ..., 196.25e12)
        laser.clean_jump_to_target(-1)  # 196.25 THz
        laser.clean_jump(192.05e12, sled_temperature=31.58, diode_current=0.0952)  # without map
        laser.stop_clean_jump()  # stays at 192.05 THz
        laser.emission_enabled = False
        laser.first_channel_frequency = 191.5e12  # the jump set it to the target

    The features beyond the MSA depend on the firmware line of the laser, according to the
    Pure Photonics feature guide:

    ==========================  =========================================
    Feature                     Firmware
    ==========================  =========================================
    Low noise modes             8.0.x, 8.1.x, 8.2.x
    Clean sweep (up to 75 GHz)  8.0.9 and later
    Clean jump                  clean jump firmware from Pure Photonics
    ==========================  =========================================

    Implemented are the MSA functions, the low noise modes, the clean sweep and the clean jump.
    The clean jump firmware may report the same version as the standard firmware,
    so :attr:`clean_sweep_available` and :attr:`clean_jump_available` test the registers instead.
    Clean scan and the extended clean sweep are not implemented.
    Unsupported registers raise an :class:`.ITLAExecutionError` with error :attr:`.ITLAError.RNI`.
    """

    OperationMode = OperationMode

    def __init__(self, adapter: AdapterType, name: str = "Pure Photonics PPCL300", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self._firmware_version: str | None = None
        self._clean_jump_map: dict[int, tuple[float, float]] = {}  # 100 MHz: (°C, A)
        self._clean_jump_power: float | None = None  # dBm

    def _register_implemented(self, register: int) -> bool:
        """Read `register` once and return False, if the module answers RNI."""
        try:
            with self._lock:
                self._transceive(register)
        except ITLAExecutionError as exc:
            if exc.error == ITLAError.RNI:
                return False
            raise
        return True

    @cached_property
    def clean_sweep_available(self) -> bool:
        """Get whether the firmware has the clean sweep (bool, tested once)."""
        return self._register_implemented(0xE4)

    @cached_property
    def clean_jump_available(self) -> bool:
        """Get whether the firmware has the clean jump (bool, tested once)."""
        return self._register_implemented(0xEA)

    @property
    def firmware_version(self) -> str:
        """Get the firmware version, e.g. ``"8.0.9"`` (str).

        Taken from the ``FW`` field of :attr:`release` and cached after the first query."""
        if self._firmware_version is not None:
            return self._firmware_version
        match = re.search(r"FW\s*([0-9A-Za-z]+\.[0-9A-Za-z]+\.[0-9A-Za-z]+)", self.release)
        if match is None:
            raise ValueError(f"No firmware version in release '{self.release}'.")
        version = match.group(1)
        self._firmware_version = version
        return version

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
        """Control the clean sweep range in Hz (float strictly from 0 to 75e9 in steps of 1e9).""",
        validator=strict_range,
        values=(0, 75e9),
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

    # Clean jump (clean jump firmware)
    def load_clean_jump_map(self, path: str | os.PathLike, check_serial: bool = True) -> None:
        """Load the clean jump calibration (``.map`` file of Pure Photonics) and set its power.

        Pure Photonics provides a map file per laser and power level, named
        ``<serial number>_<power in 0.01 dBm>_<date>.map``, with one line per channel::

            freq = 191.5 sled = 29.14 f1 = 75.966 f2 = 63.791 ... current = 918 power = 1000 ...

        (frequency in THz, sled temperature in °C, diode current in 0.1 mA, power in 0.01 dBm).
        Afterwards, :meth:`clean_jump` takes sled temperature and diode current from the map and
        :attr:`clean_jump_targets` lists all frequencies of the map. The map is valid for one
        power only (the power of the channels may differ by 0.01 dBm): :attr:`power_setpoint` is
        set to the power of the map, with a warning if it was different.

        :param path: Path of the map file.
        :param check_serial: Check that the file name starts with the :attr:`serial_number` of
            the laser (raises :class:`ValueError`).
        """
        path = Path(path)
        if check_serial:
            serial = self.serial_number.strip()
            if path.name.split("_")[0] != serial:
                raise ValueError(f"Map file '{path.name}' is not for laser {serial}.")
        points = {}
        powers = []
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            fields = dict(re.findall(r"(\w+)\s*=\s*(\S+)", line))
            try:
                key = round(float(fields["freq"]) * 1e4)  # 100 MHz
                points[key] = (float(fields["sled"]), float(fields["current"]) / 1e4)
                powers.append(round(float(fields["power"])) / 100)
            except (KeyError, ValueError) as exc:
                raise ValueError(f"Invalid line {number} in map file '{path.name}'.") from exc
        if not points:
            raise ValueError(f"No channels in map file '{path.name}'.")
        power = Counter(powers).most_common(1)[0][0]
        if max(abs(p - power) for p in powers) > 0.1:
            raise ValueError(
                f"Map file '{path.name}' contains several powers {sorted(set(powers))} dBm."
            )
        previous = self.power_setpoint
        if abs(previous - power) > 0.005:
            warnings.warn(
                f"Power setpoint changed from {previous:g} dBm to {power:g} dBm of the map.",
                stacklevel=2,
            )
            self.power_setpoint = power
        self._clean_jump_map = dict(sorted(points.items()))
        self._clean_jump_power = power

    @property
    def clean_jump_targets(self) -> tuple[float, ...]:
        """Get the frequencies of the loaded clean jump map in Hz, ascending (tuple of floats).

        Set by :meth:`load_clean_jump_map`; :meth:`clean_jump_to_target` jumps by index."""
        return tuple(key * 1e8 for key in self._clean_jump_map)

    def clean_jump_to_target(self, index: int, check: bool = True) -> float:
        """Jump to the frequency :attr:`clean_jump_targets` ``[index]`` and return it in Hz.

        See :meth:`clean_jump`."""
        frequency = self.clean_jump_targets[index]
        self.clean_jump(frequency, check=check)
        return frequency

    def clean_jump(
        self,
        frequency: float,
        sled_temperature: float | None = None,
        diode_current: float | None = None,
        check: bool = True,
    ) -> None:
        """Jump directly to a calibrated operating point (clean jump).

        Instead of tuning with all control loops, the laser sets the sled temperature and the
        diode current, calculates the filter temperatures for ``frequency`` and jumps there
        without passing other frequencies. The laser does not correct the
        frequency afterwards, the accuracy depends on the operating point. Without
        ``sled_temperature`` and ``diode_current``, they are taken from the map loaded with
        :meth:`load_clean_jump_map`, which contains only the channel frequencies (the operating
        points cannot be interpolated between channels). A jump with values from the map raises
        a :class:`ValueError`, if :attr:`power_setpoint` differs from the power of the map.

        Requires the clean jump firmware, enabled output and :attr:`OperationMode.NO_DITHER`. In
        :attr:`OperationMode.DITHER`, the laser acknowledges the commands but does not jump.
        After the jump, :attr:`frequency` reports the target frequency. Further jumps may follow;
        call :meth:`stop_clean_jump` before tuning otherwise. The driver does not enforce this,
        and the laser does not report whether a clean jump is active.

        .. note::

            The laser sets :attr:`first_channel_frequency` to the jump target, so channel 1 is
            the target afterwards, also after disabling the output. To tune with channels again,
            set :attr:`first_channel_frequency` and :attr:`channel` with disabled output.

        :param frequency: Target frequency in Hz (resolution 100 MHz).
        :param sled_temperature: Sled temperature in °C (resolution 0.01 °C).
        :param diode_current: Diode current in A (resolution 0.1 mA).
        :param check: Check before the jump that the laser is not in
            :attr:`OperationMode.DITHER` (raises :class:`ValueError`) and afterwards that
            :attr:`frequency` reports the target frequency (raises :class:`RuntimeError`).
        """
        map_power = None
        if sled_temperature is None and diode_current is None:
            map_power = self._clean_jump_power
            try:
                sled_temperature, diode_current = self._clean_jump_map[round(frequency / 1e8)]
            except KeyError:
                if not self._clean_jump_map:
                    raise ValueError("No clean jump map loaded.") from None
                raise ValueError(f"{frequency / 1e12} THz is not in the clean jump map.") from None
        elif sled_temperature is None or diode_current is None:
            raise ValueError("Give both sled_temperature and diode_current, or none of them.")
        strict_range(sled_temperature, (0, 655.35))
        strict_range(diode_current, (0, 6.5535))
        with self._lock:
            if not self.clean_jump_available:
                raise ITLAExecutionError(0xE9, ITLAError.RNI)  # before any other command
            if map_power is not None and abs(self.power_setpoint - map_power) > 0.005:
                raise ValueError(
                    f"Power setpoint differs from the power {map_power:g} dBm of the map."
                )
            strict_range(frequency, (self.frequency_min, self.frequency_max))
            if check and self.operation_mode == OperationMode.DITHER:
                raise ValueError("Clean jump requires a low noise operation mode (NO_DITHER).")
            self.write_register(0xE9, round(diode_current * 1e4))  # 0.1 mA
            self._set_frequency(0xEA, frequency)  # 0xEA THz, 0xEB 0.1 GHz
            self.write_register(0xEC, round(sled_temperature * 100))  # 0.01 °C
            # Four steps: store the operating point, calculate filter 1, calculate filter 2, jump.
            for _ in range(4):
                self.write_register(0xED, 1)
            if check:
                reported = self.frequency
                # the module may report the target 100 MHz lower
                if abs(reported - frequency) > 0.15e9:
                    raise RuntimeError(
                        f"Clean jump not executed: laser reports {reported / 1e12:.4f} THz "
                        f"instead of {frequency / 1e12:.4f} THz."
                    )

    def stop_clean_jump(self) -> None:
        """Stop the clean jump mode; the laser stays at the last jump target.

        Required before switching to :attr:`OperationMode.DITHER` and before tuning with
        :attr:`channel`, :attr:`first_channel_frequency` or :attr:`fine_tune_frequency`.
        """
        self.write_register(0xED, 0)
