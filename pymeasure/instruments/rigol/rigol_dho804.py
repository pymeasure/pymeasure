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
import numpy as np
from pyvisa.util import from_ieee_block

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DHO804Channel(Channel):
    """A single analog input channel of the Rigol DHO804."""

    display = Channel.control(
        ":CHAN{ch}:DISP?",
        ":CHAN{ch}:DISP %d",
        """Control whether the channel is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    coupling = Channel.control(
        ":CHAN{ch}:COUP?",
        ":CHAN{ch}:COUP %s",
        """Control the input coupling: ``"AC"``, ``"DC"``, or ``"GND"``.""",
        validator=strict_discrete_set,
        values=["AC", "DC", "GND"],
    )

    bandwidth_limit = Channel.control(
        ":CHAN{ch}:BWL?",
        ":CHAN{ch}:BWL %s",
        """Control the bandwidth limit: ``"OFF"``, ``"20M"``, or ``"100M"``.""",
        validator=strict_discrete_set,
        values=["OFF", "20M", "100M"],
    )

    scale = Channel.control(
        ":CHAN{ch}:SCAL?",
        ":CHAN{ch}:SCAL %g",
        """Control the vertical scale in V/div (float).

        Valid range: 500 µV/div – 10 V/div for a 1x probe.
        """,
        validator=strict_range,
        values=[500e-6, 10.0],
        cast=float,
    )

    offset = Channel.control(
        ":CHAN{ch}:OFFS?",
        ":CHAN{ch}:OFFS %g",
        """Control the vertical offset in Volts (float).""",
        cast=float,
    )

    probe = Channel.control(
        ":CHAN{ch}:PROB?",
        ":CHAN{ch}:PROB %g",
        """Control the probe attenuation ratio (float, e.g. 1, 10, 100).""",
        validator=strict_discrete_set,
        values=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5,
                10, 20, 50, 100, 200, 500, 1000],
        cast=float,
    )

    invert = Channel.control(
        ":CHAN{ch}:INV?",
        ":CHAN{ch}:INV %s",
        """Control whether the channel waveform is inverted (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    units = Channel.control(
        ":CHAN{ch}:UNIT?",
        ":CHAN{ch}:UNIT %s",
        """Control the unit of the vertical axis: ``"VOLT"``, ``"WATT"``,
        ``"AMP"``, or ``"UNKN"``.""",
        validator=strict_discrete_set,
        values=["VOLT", "WATT", "AMP", "UNKN"],
    )

    label = Channel.control(
        ":CHAN{ch}:LAB:CONT?",
        ":CHAN{ch}:LAB:CONT %s",
        """Control the label content shown for the channel (string, max 10 chars).""",
    )

    label_show = Channel.control(
        ":CHAN{ch}:LAB:SHOW?",
        ":CHAN{ch}:LAB:SHOW %s",
        """Control whether the label is shown on screen (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )


class DHO804(SCPIMixin, Instrument):
    """PyMeasure driver for the **Rigol DHO804** 4-channel 12-bit oscilloscope."""

    name = "Rigol DHO804"

    ch_1 = Instrument.ChannelCreator(DHO804Channel, 1)
    ch_2 = Instrument.ChannelCreator(DHO804Channel, 2)
    ch_3 = Instrument.ChannelCreator(DHO804Channel, 3)
    ch_4 = Instrument.ChannelCreator(DHO804Channel, 4)

    def __init__(self, resource_name, **kwargs):
        kwargs.setdefault("name", self.name)
        super().__init__(resource_name, **kwargs)
        
    def wait_for_opc(self, timeout=10):
        """Block until the oscilloscope reports operation complete."""
        self.ask("*OPC?")
    
    def clear_status(self):
        """Clear the event status register (CLS)."""
        self.write("*CLS")
    
    @property
    def status_byte(self):
        """Return the status byte (STB, int)."""
        return int(self.ask("*STB?"))

    # ================================================================== #
    #  ACQUISITION                                                        #
    # ================================================================== #

    acquisition_type = Instrument.control(
        ":ACQ:TYPE?",
        ":ACQ:TYPE %s",
        """Control the acquisition mode:

        * ``"NORM"``     – Normal (default)
        * ``"AVER"``     – Average
        * ``"PEAK"``     – Peak detect
        * ``"ULTR"``     – UltraAcquire (DHO-series specific)
        """,
        validator=strict_discrete_set,
        values=["NORM", "AVER", "PEAK", "ULTR"],
    )

    acquisition_averages = Instrument.control(
        ":ACQ:AVER?",
        ":ACQ:AVER %d",
        """Control the number of averages (2 … 65536, powers of 2).""",
        validator=strict_discrete_set,
        values=[2**n for n in range(1, 17)],
        cast=int,
    )

    acquisition_memory_depth = Instrument.control(
        ":ACQ:MDEP?",
        ":ACQ:MDEP %s",
        """Control the memory depth per channel.

        Accepted values: ``"AUTO"``, 1000, 10000, 100000, 1000000,
        10000000, 25000000, 50000000, 100000000, 200000000.
        """,
        validator=strict_discrete_set,
        values=["AUTO", 1_000, 10_000, 100_000, 1_000_000,
                10_000_000, 25_000_000, 50_000_000,
                100_000_000, 200_000_000],
    )

    @property
    def sample_rate(self):
        """Return the current sample rate in Sa/s (read-only, float)."""
        return float(self.ask(":ACQ:SRAT?"))

    # ================================================================== #
    #  TIMEBASE                                                           #
    # ================================================================== #

    timebase_scale = Instrument.control(
        ":TIM:MAIN:SCAL?",
        ":TIM:MAIN:SCAL %g",
        """Control the horizontal (timebase) scale in s/div (float).

        Valid range: 1 ns/div – 1000 s/div.
        """,
        validator=strict_range,
        values=[1e-9, 1000.0],
        cast=float,
    )

    timebase_offset = Instrument.control(
        ":TIM:MAIN:OFFS?",
        ":TIM:MAIN:OFFS %g",
        """Control the horizontal offset (trigger delay) in seconds (float).""",
        cast=float,
    )

    timebase_mode = Instrument.control(
        ":TIM:MODE?",
        ":TIM:MODE %s",
        """Control the timebase mode: ``"MAIN"``, ``"XY"``, or ``"ROLL"``.""",
        validator=strict_discrete_set,
        values=["MAIN", "XY", "ROLL"],
    )

    # ================================================================== #
    #  TRIGGER                                                            #
    # ================================================================== #

    trigger_mode = Instrument.control(
        ":TRIG:MODE?",
        ":TRIG:MODE %s",
        """Control the trigger mode: ``"EDGE"``, ``"PULS"``, ``"RUNT"``,
        ``"WIND"``, ``"NEDG"``, ``"SLOP"``, ``"VID"``, ``"PATT"``,
        ``"DEL"``, ``"TIM"``, ``"DUR"``, ``"SHOL"``,
        ``"RS232"``, ``"IIC"``, ``"SPI"``, ``"CAN"``, ``"LIN"``.""",
        validator=strict_discrete_set,
        values=["EDGE", "PULS", "RUNT", "WIND", "NEDG", "SLOP",
                "VID", "PATT", "DEL", "TIM", "DUR",
                "SHOL", "RS232", "IIC", "SPI", "CAN", "LIN"],
    )

    trigger_sweep = Instrument.control(
        ":TRIG:SWE?",
        ":TRIG:SWE %s",
        """Control the trigger sweep mode: ``"AUTO"``, ``"NORM"``,
        or ``"SING"``.""",
        validator=strict_discrete_set,
        values=["AUTO", "NORM", "SING"],
    )

    trigger_source = Instrument.control(
        ":TRIG:EDGE:SOUR?",
        ":TRIG:EDGE:SOUR %s",
        """Control the edge trigger source channel: ``"CHAN1"`` … ``"CHAN4"``, ``"AC"``, or ``"EXT"``.""",
        validator=strict_discrete_set,
        values=(
            ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "AC", "EXT"]
        ),
    )

    trigger_slope = Instrument.control(
        ":TRIG:EDGE:SLOP?",
        ":TRIG:EDGE:SLOP %s",
        """Control the edge trigger slope: ``"POS"`` (rising), ``"NEG"``
        (falling), or ``"RFAL"`` (either).""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "RFAL"],
    )

    trigger_level = Instrument.control(
        ":TRIG:EDGE:LEV?",
        ":TRIG:EDGE:LEV %g",
        """Control the trigger level in Volts (float).""",
        cast=float,
    )

    trigger_coupling = Instrument.control(
        ":TRIG:COUP?",
        ":TRIG:COUP %s",
        """Control the trigger coupling: ``"AC"``, ``"DC"``, ``"LFR"``,
        or ``"HFR"``.""",
        validator=strict_discrete_set,
        values=["AC", "DC", "LFR", "HFR"],
    )

    trigger_holdoff = Instrument.control(
        ":TRIG:HOLD?",
        ":TRIG:HOLD %g",
        """Control the trigger holdoff time in seconds (float).""",
        cast=float,
    )

    @property
    def trigger_status(self):
        """Return the current trigger status string (read-only).

        Possible values: ``"TD"``, ``"WAIT"``, ``"RUN"``, ``"AUTO"``,
        ``"STOP"``.
        """
        return self.ask(":TRIG:STAT?").strip()

    # ================================================================== #
    #  RUN CONTROL                                                        #
    # ================================================================== #

    def run(self):
        """Start continuous acquisition."""
        self.write(":RUN")

    def stop(self):
        """Stop acquisition."""
        self.write(":STOP")

    def single(self):
        """Trigger a single acquisition."""
        self.write(":SING")

    def force_trigger(self):
        """Force a trigger event."""
        self.write(":TFOR")

    def autoset(self):
        """Execute AUTOSET to automatically configure timebase, channels, and
        trigger based on the input signals."""
        self.write(":AUTO")

    # ================================================================== #
    #  MEASUREMENTS                                                       #
    # ================================================================== #

    def measure(self, item, source="CHAN1"):
        """Query a built-in automatic measurement.

        :param item: Measurement item string, e.g. ``"VMAX"``, ``"VMIN"``,
            ``"VPP"``, ``"VRMS"``, ``"VAVG"``, ``"PER"``, ``"FREQ"``,
            ``"RISE"``, ``"FALL"``, ``"NWID"``, ``"PWID"``, ``"PDUT"``,
            ``"NDUT"``.
        :param source: Source channel string, e.g. ``"CHAN1"``.
        :returns: Measured value as float, or ``float("nan")`` if the
            measurement is not available.
        """
        result = self.ask(f":MEAS:ITEM? {item},{source}").strip()
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

    display_type = Instrument.control(
        ":DISP:TYPE?",
        ":DISP:TYPE %s",
        """Control the waveform display type: ``"VECT"`` (vector) or
        ``"DOTS"``.""",
        validator=strict_discrete_set,
        values=["VECT", "DOTS"],
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
        """Return the waveform preamble for *channel* as a dict.

        The preamble encodes scaling information needed to convert raw
        samples to physical units.

        :param channel: Channel number 1-4.
        :returns: dict with keys ``format``, ``type``, ``points``,
            ``count``, ``xincrement``, ``xorigin``, ``xreference``,
            ``yincrement``, ``yorigin``, ``yreference``.
        """
        self._set_waveform_source(channel)
        raw = self.ask(":WAV:PRE?").strip()
        parts = raw.split(",")
        keys = [
            "format", "type", "points", "count",
            "xincrement", "xorigin", "xreference",
            "yincrement", "yorigin", "yreference",
        ]
        preamble = {}
        for key, val in zip(keys, parts):
            try:
                preamble[key] = float(val)
            except ValueError:
                preamble[key] = val
        preamble["points"] = int(preamble["points"])
        preamble["count"] = int(preamble["count"])
        preamble["xreference"] = int(preamble["xreference"])
        preamble["yreference"] = int(preamble["yreference"])
        return preamble

    def get_waveform(self, channel=1, mode="NORM", fmt="BYTE"):
        """Download a waveform from the oscilloscope.

        The scope must be stopped (or in single mode) before calling this
        method to ensure a stable waveform.

        :param channel: Channel number 1-4.
        :param mode: Waveform mode:

            * ``"NORM"``   – points shown on screen (up to 1200)
            * ``"MAX"``    – all points in memory (slow)
            * ``"RAW"``    – raw ADC samples from memory

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
                f"mode must be 'NORM', 'MAX', or 'RAW', got '{mode}'"
            )

        self._set_waveform_source(channel)
        self.write(f":WAV:MODE {mode}")
        self.write(f":WAV:FORM {fmt}")

        # Read preamble for scaling coefficients
        pre = self.get_waveform_preamble(channel)

        datatype = "B" if fmt == "BYTE" else "H"   # uint8 or uint16
        # handle IEEE encoded values via PyVISA function
        samples = self.adapter.connection.query_binary_values(
            ":WAV:DATA?", 
            datatype=datatype, 
            container=np.array,
            is_big_endian=False
        )

        # Convert to physical values using preamble
        voltage = (samples - pre["yorigin"] - pre["yreference"]) * pre["yincrement"]
        time = (
            np.arange(len(samples)) * pre["xincrement"]
            + pre["xorigin"]
        )

        return time, voltage

    def get_waveform_ascii(self, channel=1):
        """Download a waveform in ASCII format (slower).

        :param channel: Channel number 1-4.
        :returns: Tuple ``(time_array, voltage_array)``.
        """
        self._set_waveform_source(channel)
        self.write(":WAV:MODE NORM")
        self.write(":WAV:FORM ASC")

        pre = self.get_waveform_preamble(channel)
        raw = self.ask(":WAV:DATA?").strip()

        # ASCII response may start with a '#' block header or plain CSV
        if raw.startswith("#"):
            n_digits = int(raw[1])
            raw = raw[2 + n_digits:]

        voltage = np.array([float(v) for v in raw.split(",") if v])
        time = np.arange(len(voltage)) * pre["xincrement"] + pre["xorigin"]
        return time, voltage
