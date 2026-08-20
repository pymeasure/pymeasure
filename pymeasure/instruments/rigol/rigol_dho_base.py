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
import time
from enum import IntFlag

import numpy as np

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
)

from .rigol_oscilloscope import (
    RigolOscilloscope,
    RigolOscilloscopeChannel,
    _parse_ieee_block,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EventStatusByte(IntFlag):
    """Event Status Register (ESR) flags."""
    NONE = 0
    OPC = 1            # Bit 0: Operation Complete
    B1 = 2             # Bit 1: unused
    QYE = 4            # Bit 2: Query Error
    DDE = 8            # Bit 3: Device Specific Error
    EXE = 16           # Bit 4: Execution Error
    CME = 32           # Bit 5: Command Error
    B6 = 64            # Bit 6: unused
    PON = 128          # Bit 7: Power On


class StatusByte(IntFlag):
    """Status Byte (STB) flags."""
    NONE = 0
    B0 = 1             # Bit 0: unused
    B1 = 2             # Bit 1: unused
    ERR_QUEUE = 4      # Bit 2: Error(s) in Queue
    QDS = 8            # Bit 3: Questionable Data Summary
    MAV = 16           # Bit 4: Message Available
    SES = 32           # Bit 5: Standard Event Summary
    MSS = 64           # Bit 6: Master Summary Status
    OSR = 128          # Bit 7: Operation Status Register


class DHOBaseChannel(RigolOscilloscopeChannel):
    """A single analog input channel of the Rigol DHO series."""

    bandwidth_limit_values = ["OFF", "ON", "20M", "250M"]
    scale_validator = strict_range
    scale_values = [100e-6, 10.0]

    label = Channel.control(
        ":CHAN{ch}:LAB:CONT?",
        ":CHAN{ch}:LAB:CONT %s",
        """Control the label content shown for the channel (string, max
        10 chars).""",
        cast=str,
    )

    label_enabled = Channel.control(
        ":CHAN{ch}:LAB:SHOW?",
        ":CHAN{ch}:LAB:SHOW %s",
        """Control whether the label is shown on screen (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )


class DHOBase(RigolOscilloscope):
    """PyMeasure driver base class for the Rigol DHO series oscilloscopes."""

    name = "Rigol DHO"

    ch_1 = Instrument.ChannelCreator(DHOBaseChannel, 1)
    ch_2 = Instrument.ChannelCreator(DHOBaseChannel, 2)
    ch_3 = Instrument.ChannelCreator(DHOBaseChannel, 3)
    ch_4 = Instrument.ChannelCreator(DHOBaseChannel, 4)

    acquisition_memory_depth_values = [
        "AUTO",
        1_000,
        10_000,
        100_000,
        1_000_000,
        5_000_000,
        10_000_000,
        25_000_000,
        50_000_000,
        100_000_000,
        125_000_000,
        200_000_000,
        250_000_000,
        500_000_000,
    ]
    acquisition_type_values = ["NORM", "AVER", "PEAK", "HRES", "ULTR"]
    timebase_scale_validator = strict_range
    timebase_scale_values = [1e-9, 1000.0]
    edge_trigger_source_values = ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "AC", "EXT"]

    def __init__(self, adapter, name="Rigol DHO", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def wait_for_opc(self, timeout=10):
        """Block until the oscilloscope reports operation complete."""
        deadline = time.monotonic() + timeout
        while True:
            if self.ask("*OPC?").strip() == "1":
                return
            if time.monotonic() > deadline:
                raise TimeoutError(f"wait_for_opc timed out after {timeout} s")
            time.sleep(0.1)

    def clear_status(self):
        """Clear the event status register (CLS)."""
        self.write("*CLS")

    status_byte = Instrument.measurement(
        "*STB?",
        """Get the status byte (STB, IntFlag).""",
        cast=lambda v: StatusByte(int(v))
    )

    event_status = Instrument.measurement(
        "*ESR?",
        """Get and clear the Standard Event Status Register (ESR, IntFlag).""",
        cast=lambda v: EventStatusByte(int(v))
    )

    @property
    def trigger_source(self):
        """Control the Edge-trigger source as an alias for :attr:`edge_trigger_source`."""
        return self.edge_trigger_source

    @trigger_source.setter
    def trigger_source(self, value):
        self.edge_trigger_source = value

    @property
    def trigger_slope(self):
        """Control the Edge-trigger slope as an alias for :attr:`edge_trigger_slope`."""
        return self.edge_trigger_slope

    @trigger_slope.setter
    def trigger_slope(self, value):
        self.edge_trigger_slope = value

    @property
    def trigger_level(self):
        """Control the Edge-trigger level as an alias for :attr:`edge_trigger_level`."""
        return self.edge_trigger_level

    @trigger_level.setter
    def trigger_level(self, value):
        self.edge_trigger_level = value

    def autoset(self):
        """Execute AUTOSET to automatically configure timebase, channels, and
        trigger based on the input signals."""
        self.write(":AUTO")

    # ================================================================== #
    #  MEASUREMENTS                                                       #
    # ================================================================== #

    def measure(self, item, channel=1):
        """Query a built-in automatic measurement.

        :param item: Measurement item string, e.g. ``"VMAX"``, ``"VMIN"``,
            ``"VPP"``, ``"VRMS"``, ``"VAVG"``, ``"PER"``, ``"FREQ"``,
            ``"RISE"``, ``"FALL"``, ``"NWID"``, ``"PWID"``, ``"PDUT"``,
            ``"NDUT"``.
        :param channel: Channel number 1-4.
        :returns: Measured value as float, or ``float("nan")`` if the
            measurement is not available.
        """
        result = self.ask(f":MEAS:ITEM? {item},CHAN{channel}").strip()
        try:
            return float(result)
        except ValueError:
            return float("nan")

    def clear_measurements(self):
        """Remove all displayed measurements."""
        self.write(":MEAS:CLE:ALL")

    # ================================================================== #
    #  CURSOR                                                             #
    # ================================================================== #

    cursor_mode = Instrument.control(
        ":CURS:MODE?",
        ":CURS:MODE %s",
        """Control the cursor mode: ``"OFF"``, ``"MAN"``, ``"TRAC"``,
        or ``"XY"``.""",
        validator=strict_discrete_set,
        values=["OFF", "MAN", "TRAC", "XY"],
    )

    # ================================================================== #
    #  DISPLAY                                                            #
    # ================================================================== #

    def clear_screen(self):
        """Clear the waveform display area."""
        self.write(":DISP:CLE")

    display_type_vector_enabled = Instrument.control(
        ":DISP:TYPE?",
        ":DISP:TYPE %s",
        """Control the waveform display type: ``True`` for Vector or
        ``False`` for Dots.""",
        validator=strict_discrete_set,
        values={True: "VECT", False: "DOTS"},
        map_values=True,
    )

    display_grading_time = Instrument.control(
        ":DISP:GRAD:TIME?",
        ":DISP:GRAD:TIME %s",
        """Control the persistence time: ``"MIN"``, ``"0.1"``, ``"0.5"``,
        ``"1"``, ``"5"``, ``"10"``, or ``"INF"``.""",
        validator=strict_discrete_set,
        values=["MIN", "0.1", "0.5", "1", "5", "10", "INF"],
    )

    # ================================================================== #
    #  WAVEFORM DOWNLOAD                                                  #
    # ================================================================== #

    def _set_waveform_source(self, channel):
        """Set the waveform source to the given channel number (1-4)."""
        self.write(f":WAV:SOUR CHAN{channel}")

    def get_waveform_preamble(self, channel=1):
        """Get the waveform preamble for *channel* as a dict."""
        self._set_waveform_source(channel)
        preamble = self._query_waveform_preamble()
        return {
            "format": float(preamble["format"]),
            "type": float(preamble["type"]),
            "points": preamble["points"],
            "count": preamble["count"],
            "xincrement": preamble["x_increment"],
            "xorigin": preamble["x_origin"],
            "xreference": preamble["x_reference"],
            "yincrement": preamble["y_increment"],
            "yorigin": float(preamble["y_origin"]),
            "yreference": preamble["y_reference"],
        }

    def get_waveform(self, channel=1, mode="NORM", fmt="BYTE"):
        """Download a waveform from the oscilloscope.

        For ``"MAX"`` and ``"RAW"`` mode, the scope is automatically stopped
        before reading and restarted afterwards if it was running.

        :param channel: Channel number 1-4.
        :param mode: Waveform mode:

            * ``"NORM"``   - points shown on screen (up to 1000)
            * ``"MAX"``    - all points in memory (up to full memory depth)
            * ``"RAW"``    - raw ADC samples from memory

        :param fmt: Data format: ``"BYTE"`` (8-bit unsigned) or
            ``"WORD"`` (16-bit unsigned, higher precision).
        :returns: Tuple ``(time_array, voltage_array)`` where both arrays
            are :class:`numpy.ndarray` with the time axis in seconds and
            the voltage axis in Volts.
        """

        if fmt not in ("BYTE", "WORD"):
            raise ValueError(f"fmt must be 'BYTE' or 'WORD', got '{fmt}'")
        if mode not in ("NORM", "MAX", "RAW"):
            raise ValueError(
                f"mode must be 'NORM', 'MAX', or 'RAW', got '{mode}'")

        chunk_size = 1000
        dtype = "H" if fmt == "WORD" else "B"

        # Stop scope if needed, remember state to restore later
        was_running = self.trigger_status != "STOP"
        if mode in ("MAX", "RAW") and was_running:
            self.stop()
            time.sleep(0.1)  # wait for scope to be stopped

        try:
            self._set_waveform_source(channel)
            self.write(f":WAV:MODE {mode}")
            self.write(f":WAV:FORM {fmt}")

            pre = self.get_waveform_preamble(channel)

            if mode in ("MAX", "RAW"):
                try:
                    n_total = int(float(self.ask(":ACQ:MDEP?")))
                except (ValueError, TypeError):
                    # safe fallback for AUTO or unexpected response
                    n_total = pre["points"]
            else:
                n_total = pre["points"]

            all_samples = []

            if mode in ("MAX", "RAW"):
                for start in range(1, n_total + 1, chunk_size):
                    stop = min(start + chunk_size - 1, n_total)
                    self.write(f":WAV:STAR {start}")
                    self.write(f":WAV:STOP {stop}")
                    self.write(":WAV:DATA?")
                    raw = self._read_ieee_block("Waveform response")
                    all_samples.append(
                        np.frombuffer(raw, dtype=np.dtype(f"<{dtype}")))
            else:
                self.write(":WAV:STAR 1")
                self.write(f":WAV:STOP {min(n_total, chunk_size)}")
                self.write(":WAV:DATA?")
                raw = self._read_ieee_block("Waveform response")
                all_samples.append(
                    np.frombuffer(raw, dtype=np.dtype(f"<{dtype}")))

        # Restore previous state
        finally:
            if mode in ("MAX", "RAW") and was_running:
                self.run()

        samples = np.concatenate(all_samples)
        voltage = ((samples - pre["yorigin"] - pre["yreference"])
                   * pre["yincrement"])
        t = np.arange(len(samples)) * pre["xincrement"] + pre["xorigin"]
        return t, voltage

    def get_waveform_ascii(self, channel=1):
        """Download a waveform in ASCII format.

        Uses ``"NORM"`` mode, returning up to 1000 points shown on screen.
        For full memory depth use :meth:`get_waveform` with ``mode="MAX"``
        or ``mode="RAW"``.

        :param channel: Channel number 1-4.
        :returns: Tuple ``(time_array, voltage_array)`` where both arrays
            are :class:`numpy.ndarray` with the time axis in seconds and
            the voltage axis in Volts.
        """
        self._set_waveform_source(channel)
        self.write(":WAV:MODE NORM")
        self.write(":WAV:FORM ASC")

        pre = self.get_waveform_preamble(channel)
        self.write(":WAV:STAR 1")
        self.write(f":WAV:STOP {pre['points']}")
        raw = self.ask(":WAV:DATA?").strip()

        # ASCII response may start with a '#' block header or plain CSV
        if raw.startswith("#"):
            raw = _parse_ieee_block(raw.encode(), "ASCII waveform response").decode()

        voltage = np.array([float(v) for v in raw.split(",") if v])
        t = np.arange(len(voltage)) * pre["xincrement"] + pre["xorigin"]
        return t, voltage
