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


"""
PyMeasure driver for the Rigol DHO804 digital oscilloscope.

The DHO804 is a 4-channel, 12-bit, 250 MSa/s oscilloscope from the DHO800
series.  The driver follows the modern PyMeasure Channel-based pattern and
supports USB (USBTMC) and LAN (VXI-11 / raw socket) connections through
PyVISA.

Example usage::

    from pymeasure.instruments.rigol.dho804 import DHO804

    scope = DHO804("TCPIP::192.168.1.100::INSTR")

    # Configure channel 1
    ch1 = scope.ch_1
    ch1.display = True
    ch1.coupling = "DC"
    ch1.scale = 1.0      # 1 V/div
    ch1.offset = 0.0

    # Configure timebase
    scope.timebase_scale = 1e-3   # 1 ms/div
    scope.timebase_offset = 0.0

    # Configure trigger
    scope.trigger_source = "CHAN1"
    scope.trigger_level = 0.5
    scope.trigger_slope = "POS"
    scope.trigger_sweep = "AUTO"

    # Acquire a single trace
    scope.single()
    scope.wait_for_opc()

    # Download waveform from channel 1
    time, voltage = scope.get_waveform(1)
"""

import logging
import numpy as np

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DHO804Channel(Channel):
    """A single analogue input channel of the Rigol DHO804.

    Do not instantiate directly – use the channel accessors on
    :class:`DHO804` (``scope.ch_1``, ``scope.ch_2``, …).

    The channel prefix (e.g. ``:CHANnel1:``) is set by the
    :class:`DHO804` instrument via ``ChannelCreator``.  All command strings
    here are **relative** to that prefix – PyMeasure prepends it
    automatically before sending to the instrument.
    """

    # -- Display -------------------------------------------------------- #

    display = Channel.control(
        ":CHAN{ch}:DISPlay?",
        ":CHAN{ch}:DISPlay %d",
        """Control whether the channel is displayed (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    # -- Coupling ------------------------------------------------------- #

    coupling = Channel.control(
        ":CHAN{ch}:COUPling?",
        ":CHAN{ch}:COUPling %s",
        """Control the input coupling: ``"AC"``, ``"DC"``, or ``"GND"``.""",
        validator=strict_discrete_set,
        values=["AC", "DC", "GND"],
    )

    # -- Bandwidth limit ------------------------------------------------ #

    bandwidth_limit = Channel.control(
        ":CHAN{ch}:BWLimit?",
        ":CHAN{ch}:BWLimit %s",
        """Control the bandwidth limit: ``"OFF"``, ``"20M"``, or ``"100M"``.""",
        validator=strict_discrete_set,
        values=["OFF", "20M", "100M"],
    )

    # -- Vertical scale ------------------------------------------------- #

    scale = Channel.control(
        ":CHAN{ch}:SCALe?",
        ":CHAN{ch}:SCALe %g",
        """Control the vertical scale in V/div (float).

        Valid range: 500 µV/div – 10 V/div for a 1x probe.
        """,
        validator=strict_range,
        values=[500e-6, 10.0],
        cast=float,
    )

    # -- Vertical offset ------------------------------------------------ #

    offset = Channel.control(
        ":CHAN{ch}:OFFSet?",
        ":CHAN{ch}:OFFSet %g",
        """Control the vertical offset in Volts (float).""",
        cast=float,
    )

    # -- Probe ratio ---------------------------------------------------- #

    probe = Channel.control(
        ":CHAN{ch}:PROBe?",
        ":CHAN{ch}:PROBe %g",
        """Control the probe attenuation ratio (float, e.g. 1, 10, 100).""",
        validator=strict_discrete_set,
        values=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5,
                10, 20, 50, 100, 200, 500, 1000],
        cast=float,
    )

    # -- Invert --------------------------------------------------------- #

    invert = Channel.control(
        ":CHAN{ch}:INVert?",
        ":CHAN{ch}:INVert %s",
        """Control whether the channel waveform is inverted (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    # -- Units ---------------------------------------------------------- #

    units = Channel.control(
        ":CHAN{ch}:UNITs?",
        ":CHAN{ch}:UNITs %s",
        """Control the unit of the vertical axis: ``"VOLT"``, ``"WATT"``,
        ``"AMP"``, or ``"UNKN"``.""",
        validator=strict_discrete_set,
        values=["VOLT", "WATT", "AMP", "UNKN"],
    )

    # -- Label ---------------------------------------------------------- #

    label = Channel.control(
        ":CHAN{ch}:LABel?",
        ":CHAN{ch}:LABel %s",
        """Control the label shown for the channel (string, max 10 chars).""",
    )

    label_display = Channel.control(
        ":CHAN{ch}:LABel:DISPlay?",
        ":CHAN{ch}:LABel:DISPlay %s",
        """Control whether the label is shown on screen (bool).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )


class DHO804(SCPIMixin, Instrument):
    """PyMeasure driver for the **Rigol DHO804** 4-channel 12-bit oscilloscope.

    .. code-block:: python

        from pymeasure.instruments.rigol import DHO804

        scope = DHO804("TCPIP::192.168.1.100::INSTR")

        scope.ch_1.coupling = "DC"
        scope.ch_1.scale = 0.5
        scope.timebase_scale = 500e-6
        scope.trigger_source = "CHAN1"
        scope.trigger_level = 1.0
        scope.run()

        t, v = scope.get_waveform(1)

    :param resource_name: VISA resource string, e.g.
        ``"USB0::0x1AB1::0x044C::DHO804XXXXXX::INSTR"`` or
        ``"TCPIP::192.168.1.100::INSTR"``.
    :param kwargs: Passed on to :class:`~pymeasure.instruments.Instrument`.
    """

    name = "Rigol DHO804"

    # Channel container: ch_1 to ch_4
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
        """Clear the event status register (*CLS)."""
        self.write("*CLS")
    
    @property
    def status_byte(self):
        """Return the status byte (*STB?, int)."""
        return int(self.ask("*STB?"))

    # ================================================================== #
    #  ACQUISITION                                                        #
    # ================================================================== #

    acquisition_type = Instrument.control(
        ":ACQuire:TYPE?",
        ":ACQuire:TYPE %s",
        """Control the acquisition mode:

        * ``"NORMal"``   – Normal (default)
        * ``"AVERages"`` – Average
        * ``"PEAK"``     – Peak detect
        * ``"ULTRa"``    – UltraAcquire (DHO-series specific)
        """,
        validator=strict_discrete_set,
        values=["NORM", "AVER", "PEAK", "ULTR"],
    )

    acquisition_averages = Instrument.control(
        ":ACQuire:AVERages?",
        ":ACQuire:AVERages %d",
        """Control the number of averages (2 … 65536, powers of 2).""",
        validator=strict_discrete_set,
        values=[2**n for n in range(1, 17)],
        cast=int,
    )

    acquisition_memory_depth = Instrument.control(
        ":ACQuire:MDEPth?",
        ":ACQuire:MDEPth %s",
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
        return float(self.ask(":ACQuire:SRATe?"))

    # ================================================================== #
    #  TIMEBASE                                                           #
    # ================================================================== #

    timebase_scale = Instrument.control(
        ":TIMebase:MAIN:SCALe?",
        ":TIMebase:MAIN:SCALe %g",
        """Control the horizontal (timebase) scale in s/div (float).

        Valid range: 1 ns/div – 1000 s/div.
        """,
        validator=strict_range,
        values=[1e-9, 1000.0],
        cast=float,
    )

    timebase_offset = Instrument.control(
        ":TIMebase:MAIN:OFFSet?",
        ":TIMebase:MAIN:OFFSet %g",
        """Control the horizontal offset (trigger delay) in seconds (float).""",
        cast=float,
    )

    timebase_mode = Instrument.control(
        ":TIMebase:MODE?",
        ":TIMebase:MODE %s",
        """Control the timebase mode: ``"MAIN"``, ``"XY"``, or ``"ROLL"``.""",
        validator=strict_discrete_set,
        values=["MAIN", "XY", "ROLL"],
    )

    # ================================================================== #
    #  TRIGGER                                                            #
    # ================================================================== #

    trigger_mode = Instrument.control(
        ":TRIGger:MODE?",
        ":TRIGger:MODE %s",
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
        ":TRIGger:SWEep?",
        ":TRIGger:SWEep %s",
        """Control the trigger sweep mode: ``"AUTO"``, ``"NORM"``,
        or ``"SINGl"``.""",
        validator=strict_discrete_set,
        values=["AUTO", "NORM", "SINGl"],
    )

    trigger_source = Instrument.control(
        ":TRIGger:EDGE:SOURce?",
        ":TRIGger:EDGE:SOURce %s",
        """Control the edge trigger source channel: ``"CHAN1"`` … ``"CH4"``,
        ``"D0"`` … ``"D15"``, ``"AC"``, or ``"EXT"``.""",
        validator=strict_discrete_set,
        values=(
            ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "AC", "EXT"]
            + [f"D{n}" for n in range(16)]
        ),
    )

    trigger_slope = Instrument.control(
        ":TRIG:EDGE:SLOPe?",
        ":TRIG:EDGE:SLOPe %s",
        """Control the edge trigger slope: ``"POS"`` (rising), ``"NEG"``
        (falling), or ``"RFAL"`` (either).""",
        validator=strict_discrete_set,
        values=["POS", "NEG", "RFAL"],
    )

    trigger_level = Instrument.control(
        ":TRIGger:EDGE:LEVel?",
        ":TRIGger:EDGE:LEVel %g",
        """Control the trigger level in Volts (float).""",
        cast=float,
    )

    trigger_coupling = Instrument.control(
        ":TRIGger:COUPling?",
        ":TRIGger:COUPling %s",
        """Control the trigger coupling: ``"AC"``, ``"DC"``, ``"LFR"``,
        or ``"HFR"``.""",
        validator=strict_discrete_set,
        values=["AC", "DC", "LFR", "HFR"],
    )

    trigger_holdoff = Instrument.control(
        ":TRIGger:HOLDoff?",
        ":TRIGger:HOLDoff %g",
        """Control the trigger holdoff time in seconds (float).""",
        cast=float,
    )

    @property
    def trigger_status(self):
        """Return the current trigger status string (read-only).

        Possible values: ``"TD"``, ``"WAIT"``, ``"RUN"``, ``"AUTO"``,
        ``"STOP"``.
        """
        return self.ask(":TRIGger:STATus?").strip()

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
        self.write(":SINGle")

    def force_trigger(self):
        """Force a trigger event."""
        self.write(":TFORce")

    def autoset(self):
        """Execute AUTOSET to automatically configure timebase, channels, and
        trigger based on the input signals."""
        self.write(":AUTOset")

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
        result = self.ask(f":MEASure:ITEM? {item},{source}").strip()
        try:
            return float(result)
        except ValueError:
            return float("nan")

    def clear_measurements(self):
        """Remove all displayed measurements."""
        self.write(":MEASure:CLEar:ALL")

    # ================================================================== #
    #  CURSOR                                                             #
    # ================================================================== #

    cursor_mode = Instrument.control(
        ":CURSor:MODE?",
        ":CURSor:MODE %s",
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
        self.write(":DISPlay:CLEar")

    display_type = Instrument.control(
        ":DISPlay:TYPE?",
        ":DISPlay:TYPE %s",
        """Control the waveform display type: ``"VECT"`` (vector) or
        ``"DOTS"``.""",
        validator=strict_discrete_set,
        values=["VECT", "DOTS"],
    )

    display_grading_time = Instrument.control(
        ":DISPlay:GRADing:TIME?",
        ":DISPlay:GRADing:TIME %s",
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
        self.write(f":WAVeform:SOURce CHANnel{channel}")

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
        raw = self.ask(":WAVeform:PREamble?").strip()
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

    def get_waveform(self, channel=1, mode="NORMal", fmt="BYTE"):
        """Download a waveform from the oscilloscope.

        The scope must be stopped (or in single mode) before calling this
        method to ensure a stable waveform.

        :param channel: Channel number 1-4.
        :param mode: Waveform mode:

            * ``"NORMal"``   – points shown on screen (up to 1200)
            * ``"MAXimum"``  – all points in memory (slow)
            * ``"RAW"``      – raw ADC samples from memory

        :param fmt: Data format: ``"BYTE"`` (8-bit unsigned) or
            ``"WORD"`` (16-bit unsigned, higher precision).
        :returns: Tuple ``(time_array, voltage_array)`` where both arrays
            are :class:`numpy.ndarray` with the time axis in seconds and
            the voltage axis in Volts.
        """
        if fmt not in ("BYTE", "WORD"):
            raise ValueError(f"fmt must be 'BYTE' or 'WORD', got '{fmt}'")
        if mode not in ("NORMal", "MAXimum", "RAW"):
            raise ValueError(
                f"mode must be 'NORMal', 'MAXimum', or 'RAW', got '{mode}'"
            )

        self._set_waveform_source(channel)
        self.write(f":WAVeform:MODE {mode}")
        self.write(f":WAVeform:FORMat {fmt}")

        # Read preamble for scaling coefficients
        pre = self.get_waveform_preamble(channel)

        # Request binary waveform data
        self.write(":WAVeform:DATA?")
        raw = self.read_bytes(-1)  # read all available bytes

        # Parse IEEE 488.2 definite-length block header: #<N><N digits><data>
        if raw[0:1] != b"#":
            raise RuntimeError(
                "Unexpected waveform data header: expected '#', "
                f"got {raw[0:1]!r}"
            )
        n_digits = int(raw[1:2])
        n_bytes = int(raw[2: 2 + n_digits])
        data_start = 2 + n_digits
        raw_data = raw[data_start: data_start + n_bytes]

        # Unpack binary data
        if fmt == "BYTE":
            samples = np.frombuffer(raw_data, dtype=np.uint8).astype(float)
        else:  # WORD – little-endian 16-bit unsigned
            samples = np.frombuffer(raw_data, dtype="<u2").astype(float)

        # Convert to physical values using preamble
        voltage = (samples - pre["yorigin"] - pre["yreference"]) * pre["yincrement"]
        time = (
            np.arange(len(samples)) * pre["xincrement"]
            + pre["xorigin"]
        )

        return time, voltage

    def get_waveform_ascii(self, channel=1):
        """Download a waveform in ASCII format (slower but portable).

        :param channel: Channel number 1-4.
        :returns: Tuple ``(time_array, voltage_array)``.
        """
        self._set_waveform_source(channel)
        self.write(":WAVeform:MODE NORMal")
        self.write(":WAVeform:FORMat ASC")

        pre = self.get_waveform_preamble(channel)
        raw = self.ask(":WAVeform:DATA?").strip()

        # ASCII response may start with a '#' block header or plain CSV
        if raw.startswith("#"):
            n_digits = int(raw[1])
            raw = raw[2 + n_digits:]

        voltage = np.array([float(v) for v in raw.split(",") if v])
        time = np.arange(len(voltage)) * pre["xincrement"] + pre["xorigin"]
        return time, voltage

    # ================================================================== #
    #  SCREENSHOT                                                         #
    # ================================================================== #

    # def get_screenshot(self, filename=None):
    #     """Capture a screenshot from the oscilloscope.

    #     :param filename: If given, save the PNG data to this file path.
    #     :returns: Raw PNG bytes.
    #     """
    #     self.write(":DISPlay:DATA? ON,OFF,PNG")
    #     raw = self.read_bytes(-1)

    #     # Strip IEEE block header
    #     if raw[0:1] == b"#":
    #         n_digits = int(raw[1:2])
    #         n_bytes = int(raw[2: 2 + n_digits])
    #         data_start = 2 + n_digits
    #         png_data = raw[data_start: data_start + n_bytes]
    #     else:
    #         png_data = raw

    #     if filename is not None:
    #         with open(filename, "wb") as f:
    #             f.write(png_data)
    #         log.info("Screenshot saved to %s", filename)

    #     return png_data
