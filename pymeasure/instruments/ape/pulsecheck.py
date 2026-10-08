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

import logging
import struct
import time

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

#: Trigger modes and the index the ``TF`` set-command expects for each.
TRIGGER_MODES = {"freerun": 0, "trigger": 1, "fringe": 2, "slow": 3}

#: The ``GTF`` get-command reports the mode bit-coded rather than by its index.
TRIGGER_MODE_CODES = {0: "freerun", 1: "trigger", 2: "fringe", 4: "slow"}


class PulseCheck(Instrument):
    """APE PulseCheck autocorrelator.

    Connection is made through an RS232 serial connection, 8 data bits, no
    parity, 1 stop bit, with commands terminated by a carriage return.

    The instrument silently discards a setting if the next command follows too
    closely, and occasionally even then. Leave at least 0.3 s after writing a
    property, and read the property back to confirm the setting arrived::

        def set_and_read(instrument, name, value, timeout=10):
            # write the property until the setting arrives, and return what it reads back
            deadline = time.monotonic() + timeout
            while True:
                setattr(instrument, name, value)
                time.sleep(0.3)
                read = getattr(instrument, name)
                if read == value or time.monotonic() > deadline:
                    return read

    :param adapter: pyvisa resource name of the instrument or an adapter instance.
    :param name: name of the instrument.
    :param baud_rate: baud rate of the serial connection.
    :param kwargs: any valid key-word argument for :class:`~pymeasure.instruments.Instrument`.
    """

    def __init__(self, adapter, name="APE PulseCheck", baud_rate=38400, **kwargs):
        self._last_command = ""
        kwargs.setdefault("write_termination", "\r")
        kwargs.setdefault("asrl", {}).setdefault("baud_rate", baud_rate)
        super().__init__(adapter, name, **kwargs)

    def write(self, command):
        """Write a command to the instrument, terminated by a carriage return.

        The device's replies are raw bytes without any framing that would
        identify their type or length, so the command is remembered for
        :meth:`read` to know how to decode the reply.

        :param command: command string, e.g. ``"GG"`` or ``"F2"``.
        """
        self._last_command = command
        super().write(command)

    def read(self):
        """Read the raw binary reply belonging to the most recently written command."""
        if self._last_command in ("GG", "GPM"):
            return str(struct.unpack(">H", self.read_bytes(2))[0])
        if self._last_command == "GRE":
            # the resolution is transmitted as its base-2 exponent
            return str(2 ** self.read_bytes(1)[0])
        return str(self.read_bytes(1)[0])

    resolution = Instrument.measurement(
        "GRE",
        """Get the number of samples per autocorrelation trace
        (int, one of 4, 8, 16, 32, 64, 128, 256).

        The instrument firmware does not support changing this remotely yet.
        """,
        cast=int,
    )

    gain = Instrument.control(
        "GG", "GN%d",
        """Control the detector gain (int strictly from 0 to 999).""",
        validator=strict_range,
        values=(0, 999),
        cast=int,
    )

    averages = Instrument.control(
        "GAV", "A%d",
        """Control the number of averages per autocorrelation trace
        (int, one of 1, 2, 4, 8, 16).""",
        validator=strict_discrete_set,
        values=[1, 2, 4, 8, 16],
        cast=int,
    )

    filter = Instrument.control(
        "GF", "F%d",
        """Control the low-pass filter setting (str, one of 'low', 'medium', 'high').""",
        validator=strict_discrete_set,
        values={"low": 1, "medium": 2, "high": 3},
        map_values=True,
        cast=int,
    )

    math_enabled = Instrument.control(
        "GM", "M%d",
        """Control whether the instrument's math/normalization function is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    measurement_running = Instrument.control(
        "GRS", "RS%d",
        """Control whether the instrument is currently running/scanning (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        cast=int,
    )

    scan_range = Instrument.control(
        "GSR", "SR%d",
        """Control the scan range in seconds
        (float, one of 0, 1.5e-12, 5e-12, 15e-12, 50e-12, 150e-12).""",
        validator=strict_discrete_set,
        values={0: 0, 1.5e-12: 1, 5e-12: 2, 15e-12: 3, 50e-12: 4, 150e-12: 5},
        map_values=True,
        cast=int,
    )

    alpha = Instrument.measurement(
        "GPM",
        """Get the current turning angle/phase-modulation position (int).

        Use :meth:`set_alpha` to move to an absolute position, since the
        instrument only accepts relative tuning steps.
        """,
        cast=int,
    )

    tau_register = Instrument.measurement(
        "GTA",
        """Get the raw value of the device's undocumented ``GTA`` register (int).

        Its meaning is not documented by the manufacturer; this mirrors the
        ``getTau`` method of the original MATLAB driver.
        """,
        cast=int,
    )

    sensitivity = Instrument.control(
        "GSY", "SY%d",
        """Control the (unit-free) input sensitivity (int, one of 1, 3, 10, 30, 100, 300).""",
        validator=strict_discrete_set,
        values={1: 1, 3: 2, 10: 3, 30: 4, 100: 5, 300: 6},
        map_values=True,
        cast=int,
    )

    trigger_mode = Instrument.control(
        "GTF", "TF%d",
        """Control the trigger mode (str, one of 'freerun', 'trigger', 'fringe', 'slow').

        Selecting 'trigger' forces :attr:`filter` to 'low', and leaves it there when
        another mode is selected again.
        """,
        validator=strict_discrete_set,
        values=list(TRIGGER_MODES),
        # get and set use different (bit-coded vs. index) encodings, so map manually
        # instead of via `map_values`, which assumes a single shared encoding.
        get_process=lambda code: TRIGGER_MODE_CODES.get(code, f"unknown ({code})"),
        set_process=lambda mode: TRIGGER_MODES[mode],
        cast=int,
    )

    @property
    def settings(self):
        """Get a dictionary of the instrument's current settings."""
        return {
            "sensitivity": self.sensitivity,
            "gain": self.gain,
            "scan_range": self.scan_range,
            "filter": self.filter,
            "averages": self.averages,
            "resolution": self.resolution,
            "alpha": self.alpha,
            "math_enabled": self.math_enabled,
            "trigger_mode": self.trigger_mode,
        }

    def tune(self, delta):
        """Adjust the turning angle/phase-modulation position by a relative amount.

        :param delta: relative tuning step (int).
        """
        self.write(f"TU{int(delta)}")

    def set_alpha(self, alpha, retries=1, timeout=60):
        """Move the turning angle/phase-modulation position to an absolute target.

        The instrument only accepts relative tuning steps via :meth:`tune`, so
        this polls :attr:`alpha` and nudges the position repeatedly until the
        target is reached. If the position does not change for two consecutive
        polls, tuning is retried up to `retries` times, mirroring the original
        MATLAB driver's stuck-detection.

        :param alpha: target turning angle/phase-modulation position (int).
        :param retries: number of additional attempts if tuning gets stuck.
        :param timeout: how long to keep tuning altogether, in s.
        :raises TimeoutError: if the target is not reached within `timeout`, or
            within the allowed number of attempts.
        """
        if retries < 0:
            raise ValueError(f"retries has to be zero or more, not {retries}.")
        deadline = time.monotonic() + timeout

        def raise_if_timed_out(position):
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"Tuning alpha to {alpha} timed out at {position} after {timeout} s."
                )

        total_attempts = retries + 1
        for attempt in range(1, total_attempts + 1):
            current = self.alpha
            # don't send a tuning command once the deadline has passed
            raise_if_timed_out(current)
            self.tune(alpha - current)

            time.sleep(1)
            current = self.alpha
            raise_if_timed_out(current)
            stuck = False
            while current != alpha:
                log.debug("alpha = %d", current)
                raise_if_timed_out(current)
                time.sleep(0.5)
                if self.alpha == current:
                    time.sleep(0.5)
                    if self.alpha == current:
                        stuck = True
                        break
                current = self.alpha
            if not stuck:
                raise_if_timed_out(current)
                return
            log.warning("Tuning got stuck at alpha = %d (attempt %d/%d).",
                        current, attempt, total_attempts)
        raise TimeoutError(
            f"Tuning alpha to {alpha} got stuck after {total_attempts} attempt(s)."
        )

    def raw_acf(self):
        """Measure one autocorrelation trace as raw (unscaled) detector counts.

        The number of samples returned equals :attr:`resolution`.

        :returns: list of int, the raw detector counts.
        """
        n_samples = self.resolution
        # No other command may be written between write() and read_bytes() below
        # (e.g. from another thread), since the device sends the raw trace
        # immediately after "GAC" with no framing to identify it.
        self.write("GAC")
        raw = self.read_bytes(2 * n_samples)
        return [value >> 6 for value in struct.unpack(f">{n_samples}H", raw)]

    @property
    def acf(self):
        """Get one autocorrelation trace together with its delay axis, as a tuple
        ``(delay, acf)`` of numpy arrays; the delay axis is in seconds, the
        autocorrelation is in raw detector counts.

        With :attr:`scan_range` set to 0 the delay drive is parked, so every sample
        is taken at zero delay and the delay axis is all zeros; use :meth:`raw_acf`
        for the samples themselves.
        """
        acf = np.array(self.raw_acf())
        scan_range = self.scan_range
        delay = np.linspace(-scan_range / 2, scan_range / 2, len(acf))
        return delay, acf
