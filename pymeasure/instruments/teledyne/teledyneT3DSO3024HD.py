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

from pymeasure.instruments import Channel, Instrument, InstrumentProperty
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class T3DSO3024HDChannel(Channel):
    """Implementation of an analog channel on the :class:`T3DSO3024HD` oscilloscope."""

    bwlimit = Channel.control(
        ":CHANnel{ch}:BWLimit?", ":CHANnel{ch}:BWLimit %s",
        """Control the bandwidth limit of the channel (str), strictly in 'FULL', '20M', '200M'.""",
        validator=strict_discrete_set,
        values=["FULL", "20M", "200M"],
        cast=str,
    )

    coupling = Channel.control(
        ":CHANnel{ch}:COUPling?", ":CHANnel{ch}:COUPling %s",
        """Control the coupling of the channel (str), strictly in 'DC', 'AC', 'GND'.""",
        validator=strict_discrete_set,
        values=["DC", "AC", "GND"],
        cast=str,
    )

    scale = Channel.control(
        ":CHANnel{ch}:SCALe?", ":CHANnel{ch}:SCALe %.2E",
        """Control the vertical scale of the channel in Volts/div (float).""",
        validator=strict_range,
        values=[500e-6, 1e1],
        cast=float,
        dynamic=True,
    )

    _impedance: InstrumentProperty[bool] = Channel.control(
        ":CHANnel{ch}:IMPedance?", ":CHANnel{ch}:IMPedance %s",
        """Control the input impedance of the channel 'True' for high impedance (1e6 Ohm),
        'False' for low impedance (50 Ohm).""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: "FIFTy", True: "ONEMeg"},
        cast=str,
    )

    @property
    def high_impedance_enabled(self) -> bool:
        """Control the input impedance of the channel 'True' for high impedance (1e6 Ohm),
        'False' for low impedance (50 Ohm)."""
        return self._impedance

    @high_impedance_enabled.setter
    def high_impedance_enabled(self, value):
        self._impedance = value
        self.scale_values = [500e-6, 1.0] if not value else [500e-6, 1e1]

    invert: InstrumentProperty[bool] = Channel.control(
        ":CHANnel{ch}:INVert?", ":CHANnel{ch}:INVert %s",
        """Control whether or not to mathematically invert the input signal for the
        specified channel.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    @staticmethod
    def strict_length(value, max_length):
        """Validator that ensures a string does not exceed max_length characters."""
        value = str(value)
        if len(value) > max_length:
            raise ValueError(
                f"Value '{value}' exceeds maximum length of {max_length} characters "
                f"(length={len(value)})"
            )
        return value

    label = Channel.control(
        ":CHANnel{ch}:LABel?", ":CHANnel{ch}:LABel %s",
        """Control the selected channel label to ON or OFF.
        Bool value 'True' or 'False'""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    label_text = Channel.control(
        ":CHANnel{ch}:LABel:TEXT?", ":CHANnel{ch}:LABel:TEXT %s",
        """Control the selected channel label to the string specified.""",
        validator=strict_length,
        values=20,
        cast=str,
    )

    skew = Channel.control(
        ":CHANnel{ch}:SKEW?", ":CHANnel{ch}:SKEW %.2E",
        """Control the channel-to-channel skew factor label specified.
        The range of the value is [-1.00E-07, 1.00E-07].""",
        validator=strict_range,
        values=[-1e-7, 1e-7],
        cast=float,
    )

    switch = Channel.control(
        ":CHANnel{ch}:SWITch?", ":CHANnel{ch}:SWITch %s",
        """Control the display of the specified channel ON or OFF.
        Boolean value True or False.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    offset = Channel.control(
        ":CHANnel{ch}:OFFSet?", ":CHANnel{ch}:OFFSet %.3E",
        """Control the vertical offset of the channel in Volts (float).

        Note: the range of legal values depends on the current
        :attr:`scale` setting of the channel.""",
        cast=float,
    )

    unit = Channel.control(
        ":CHANnel{ch}:UNIT?", ":CHANnel{ch}:UNIT %s",
        """Control the unit of the input signal of the channel (str), strictly 'V' or 'A'.""",
        validator=strict_discrete_set,
        values=["V", "A"],
        cast=str,
    )

    probe = Channel.control(
        ":CHANnel{ch}:PROBe?", ":CHANnel{ch}:PROBe VALue,%.2E",
        """Control the probe attenuation factor of the channel (float), strictly in
        range [1e-6, 1e6].

        Note: the instrument also supports setting this to 'DEFault' (1x) via
        the raw SCPI command, which is not exposed through this property.""",
        validator=strict_range,
        values=[1e-6, 1e6],
        cast=float,
    )

    visible = Channel.control(
        ":CHANnel{ch}:VISible?", ":CHANnel{ch}:VISible %s",
        """Control to whether display the waveform of
        the specified channel or not (ON or OFF). Boolean value True or False. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )


class TeledyneT3DSO3024HD(SCPIMixin, Instrument):
    """Represents the Teledyne T3DSO3024HD oscilloscope."""

    channel_1 = Instrument.ChannelCreator(T3DSO3024HDChannel, "1")
    channel_2 = Instrument.ChannelCreator(T3DSO3024HDChannel, "2")
    channel_3 = Instrument.ChannelCreator(T3DSO3024HDChannel, "3")
    channel_4 = Instrument.ChannelCreator(T3DSO3024HDChannel, "4")

    def __init__(self, adapter, name="Teledyne T3DSO3024HD Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)

    acquisition_rate_mode = Instrument.control(
        ":ACQuire:AMODe?", ":ACQuire:AMODe %s",
        """Control the waveform capture rate mode (str), strictly 'FAST' or 'SLOW'.

        FAST provides a high-speed waveform capture rate to help capture
        signal anomalies; SLOW is the normal capture rate.
        """,
        validator=strict_discrete_set,
        values=["FAST", "SLOW"],
        cast=str,
    )

    def clear_sweep(self):
        """Clear the sweep and restart acquisition.

        Equivalent to the "Clear Sweeps" button on the front panel.

        Note: this is a write-only command; there is no corresponding query.
        """
        self.write(":ACQuire:CSWeep")

    interpolation = Instrument.control(
        ":ACQuire:INTerpolation?", ":ACQuire:INTerpolation %s",
        """Control whether sinx/x (sinc) interpolation is used (bool).

        True selects sinx/x (sinc) interpolation, False selects linear
        interpolation.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    mode = Instrument.control(
        ":ACQuire:MODE?", ":ACQuire:MODE %s",
        """Control the acquisition mode of the oscilloscope (str), strictly in
        'YT', 'XY', 'ROLL'.

        - YT plots amplitude (Y) vs. time (T).
        - XY plots channel X vs. channel Y (Lissajous curve).
        - ROLL plots amplitude (Y) vs. time (T) like YT, but writes the
          waveform from the right-hand side of the display, like a strip
          chart recorder. Suited for slow events.
        """,
        validator=strict_discrete_set,
        values=["YT", "XY", "ROLL"],
        cast=str,
    )

    _memory_depth = Instrument.control(
        ":ACQuire:MDEPth?", ":ACQuire:MDEPth %s",
        """Control the maximum memory depth (str).

        Legal values depend on if the oscilloscope mode is
        in single- or dual-channel mode (Single Channel Mode: Only one of C1/C2/C3/C4
        is turned on. Dual-Channel Mode: One of C1&C2 or C3&C4 are turned on.
        Quad-channel Mode: Three or four of C1/C2/C3/C4 are turned on.)
        T3DSO3000 Models:
        e.g. '2k', '10k', '20k', '100k', '200k', '1M', '2M', '10M', '20M', '100M', '200M', '400M'
        for single-channel T3DSO3000 models,
        or '2k', '10k', '20k', '100k', '200k', '1M', '2M', '10M', '20M', '100M', '200M'
        for dual-channel T3DSO3000 models,
        or '1k', '5k', '10k', '50k', '100k', '500k', '1M', '5M', '10M', '50M', '100M'
        for quad-channel T3DSO3000 models.

        Note: turning on digital channels, setting the acquisition type to
        AVERage/ERES, or setting the acquisition mode to ROLL will limit the
        available memory depth.
        """,
        validator=strict_discrete_set,
        dynamic=True,
        map_values=True,
        values={2e3: "2k", 10e3: "10k", 20e3: "20k", 100e3: "100k", 200e3: "200k",  1e6: "1M",
                2e6: "2M", 10e6: "10M", 20e6: "20M", 100e6: "100M",  200e6: "200M",  400e6: "400M"},
        cast=str,
    )

    def _get_channel_mode(self):
        """Determine whether the scope is in single-, dual- or quad channel mode."""
        pair_12_on = sum([self.channel_1.switch, self.channel_2.switch])
        pair_34_on = sum([self.channel_3.switch, self.channel_4.switch])
        total_on = pair_12_on + pair_34_on

        if (total_on >= 3) or (pair_12_on == 2) or (pair_34_on == 2):
            return "QUAD"
        if pair_12_on == 1 and pair_34_on == 1:
            return "DUAL"
        return "SINGLE"

    @property
    def memory_depth(self) -> float:
        """Control the input impedance of the channel in Ohms, strictly 50 or 1e6 (float)."""
        return self._memory_depth

    @memory_depth.setter
    def memory_depth(self, value):
        ch_mode = self._get_channel_mode()
        if ch_mode == "SINGLE":
            self._memory_depth_values = {2e3: "2k", 10e3: "10k", 20e3: "20k", 100e3: "100k",
                                         200e3: "200k",  1e6: "1M", 2e6: "2M", 10e6: "10M",
                                         20e6: "20M", 100e6: "100M",  200e6: "200M",  400e6: "400M"}
        elif ch_mode == "DUAL":
            self._memory_depth_values = {2e3: "2k", 10e3: "10k", 20e3: "20k", 100e3: "100k",
                                         200e3: "200k",  1e6: "1M", 2e6: "2M", 10e6: "10M",
                                         20e6: "20M", 100e6: "100M",  200e6: "200M"}
        elif ch_mode == "QUAD":
            self._memory_depth_values = {1e3: "1k", 5e3: "5k", 10e3: "10k", 50e3: "50k",
                                         100e3: "100k", 500e3: "500k", 1e6: "1M", 5e6: "5M",
                                         10e6: "10M", 50e6: "50M", 100e6: "100M"}
        self._memory_depth = value

    points = Instrument.measurement(
        ":ACQuire:POINts?",
        """Get the number of sampled points of the current waveform on the
        screen (float).""",
        cast=float,
    )

    sequence = Instrument.control(
        ":ACQuire:SEQuence?", ":ACQuire:SEQuence %s",
        """Control whether sequence acquisition mode is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    sequence_count = Instrument.control(
        ":ACQuire:SEQuence:COUNt?", ":ACQuire:SEQuence:COUNt %d",
        """Control the number (int) of memory segments to acquire. The maximum
        number of segments may be limited by the memory depth of your oscilloscope.

        The maximum number of segments may be limited by the memory depth
        of the oscilloscope and by the current timebase; consult the
        instrument manual for details.
        """,
        cast=int,
    )

    sample_rate = Instrument.measurement(
        ":ACQuire:SRATe?",
        """Get the current sampling rate in Sa/s (float).""",
        cast=float,
    )

    _acquisition_type = Instrument.control(
        ":ACQuire:TYPE?", ":ACQuire:TYPE %s",
        """Control the raw acquisition type string, e.g. 'NORMal', 'PEAK',
        'AVERage,16', 'ERES,2.0'.""",
        cast=str,
        maxsplit=0,
    )

    @property
    def acquisition_type(self):
        """Control the type of data acquisition (tuple of (str, float | None)).

        The first element is strictly one of 'NORMAL', 'PEAK', 'AVERAGE',
        'ERES'. The second element is:

        - None for 'NORMAL' and 'PEAK'
        - the number of averages (one of 4, 16, 32, 64, 128, 256, 512, 1024)
          for 'AVERAGE'
        - the number of enhanced-resolution bits (one of 0.5, 1.0, 1.5, 2.0,
          2.5, 3.0) for 'ERES'

        Note: AVERAGE/ERES are not available while in sequence acquisition
        mode (see :attr:`sequence`).

        Example::

            scope.acquisition_type = ("AVERAGE", 16)
            scope.acquisition_type = ("NORMAL", None)
            aq_type, param = scope.acquisition_type
        """
        raw = self._acquisition_type
        parts = raw.split(",")
        aq_type = parts[0].upper()
        if len(parts) > 1:
            return aq_type, float(parts[1])
        return aq_type

    @acquisition_type.setter
    def acquisition_type(self, value):
        aq_type, param = value if isinstance(value, tuple) else (value, None)
        aq_type = strict_discrete_set(aq_type.upper(), ["NORMAL", "PEAK", "AVERAGE", "ERES"])
        scpi_names = {"NORMAL": "NORMal", "PEAK": "PEAK",
                      "AVERAGE": "AVERage", "ERES": "ERES"}
        command = scpi_names[aq_type]
        if aq_type == "AVERAGE":
            if param is None:
                raise ValueError("AVERAGE acquisition type requires a <times> value")
            param = strict_discrete_set(param, [4, 16, 32, 64, 128, 256, 512, 1024])
            command += f",{int(param)}"
        elif aq_type == "ERES":
            if param is None:
                raise ValueError("ERES acquisition type requires a <bits> value")
            param = strict_discrete_set(param, [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
            command += f",{param}"
        elif param is not None:
            raise ValueError(f"{aq_type} acquisition type does not take a parameter")
        self._acquisition_type = command

    timebase_scale = Instrument.control(
        ":TIMebase:SCALe?", ":TIMebase:SCALe %.2E",
        """Control the horizontal scale per division for the main window, in
        seconds/div (float).

        Note: the valid range varies by model; consult the datasheet. If you
        set a value smaller than the instrument's minimum, the instrument
        automatically clamps to the smallest settable time base.
        """,
        cast=float,
    )

    _timebase_delay = Instrument.control(
        ":TIMebase:DELay?", ":TIMebase:DELay %.2E",
        """Control the main timebase delay in seconds (float) — the time
        between the trigger event and the delay reference point on screen.

        Note: the legal range depends on the current :attr:`timebase_scale`
        setting: [-5000 * scale, 5 * scale].
        """,
        cast=float,
        validator=strict_range,
        values=[-5000, 5],
        dynamic=True,
    )

    @property
    def timebase_delay(self) -> float:
        """Control the main timebase delay in seconds (float) — the time
        between the trigger event and the delay reference point on screen.

        Note: the legal range depends on the current :attr:`timebase_scale`
        setting: [-5000 * scale, 5 * scale].
        """
        return self._timebase_delay

    @timebase_delay.setter
    def timebase_delay(self, value):
        timebase_scale = self.timebase_scale
        self._timebase_delay_values = [-5000 * timebase_scale, 5 * timebase_scale]
        self._timebase_delay = value

    timebase_window = Instrument.control(
        ":TIMebase:WINDow?", ":TIMebase:WINDow %s",
        """Control whether the zoomed (delayed) time base window is enabled
        (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    timebase_window_delay = Instrument.control(
        ":TIMebase:WINDow:DELay?", ":TIMebase:WINDow:DELay %.2E",
        """Control the horizontal position (delay) of the zoomed window
        relative to the main sweep, in seconds (float).

        Note: the legal range is limited by the main sweep range/position so
        that the zoomed window stays within the main sweep. Out-of-range
        values are automatically clamped by the instrument to the nearest
        legal value, rather than rejected.
        """,
        cast=float,
    )

    timebase_window_scale = Instrument.control(
        ":TIMebase:WINDow:SCALe?", ":TIMebase:WINDow:SCALe %.2E",
        """Control the horizontal scale of the zoomed window, in seconds/div
        (float).

        Note: cannot exceed :attr:`timebase_scale`. If set greater, the
        instrument automatically clamps it to the main window's scale rather
        than rejecting the value.
        """,
        cast=float,
    )

    trigger_mode = Instrument.control(
        ":TRIGger:MODE?", ":TRIGger:MODE %s",
        """Control the trigger mode of the oscilloscope (str), strictly in
        'SINGLE', 'NORMAL', 'AUTO'.""",
        validator=strict_discrete_set,
        map_values=True,
        values={"SINGLE": "SINGle", "NORMAL": "NORMal", "AUTO": "AUTO"},
        cast=str,
    )

    def trigger_run(self):
        """Set the oscilloscope to run (start acquisition).
        """
        self.write(":TRIGger:RUN")

    trigger_status = Instrument.measurement(
        ":TRIGger:STATus?",
        """Get the current state of the trigger (str), one of 'Arm', 'Ready',
        'Auto', "Trig'd", 'Stop', 'Roll'.""",
        cast=str,
    )

    def trigger_stop(self):
        """Set the oscilloscope from run to stop.
        """
        self.write(":TRIGger:STOP")

    trigger_type = Instrument.control(
        ":TRIGger:TYPE?", ":TRIGger:TYPE %s",
        """Control the type of trigger (str), strictly in 'EDGE', 'PULSE',
        'SLOPE', 'INTERVAL', 'PATTERN', 'RUNT', 'QUALIFIED', 'WINDOW',
        'DROPOUT', 'VIDEO', 'IIC', 'SPI', 'UART', 'LIN', 'CAN', 'FLEXRAY',
        'CANFD', 'IIS'.

        Note: this class only implements the parameters for the 'EDGE'
        trigger type (see the ``trigger_edge_*`` attributes). Selecting any
        other type here does not expose its associated parameters.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={"EDGE": "EDGE", "PULSE": "PULSe", "SLOPE": "SLOPe", "INTERVAL": "INTerval",
                "PATTERN": "PATTern", "RUNT": "RUNT", "QUALIFIED": "QUALified", "WINDOW": "WINDow",
                "DROPOUT": "DROPout", "VIDEO": "VIDeo", "IIC": "IIC", "SPI": "SPI", "UART": "UART",
                "LIN": "LIN", "CAN": "CAN", "FLEXRAY": "FLEXray", "CANFD": "CANFd", "IIS": "IIS"},
        cast=str,
    )

    trigger_edge_coupling = Instrument.control(
        ":TRIGger:EDGE:COUPling?", ":TRIGger:EDGE:COUPling %s",
        """Control the coupling mode of the edge trigger (str), strictly in
        'DC', 'AC', 'LF_REJECT', 'HF_REJECT'.""",
        validator=strict_discrete_set,
        map_values=True,
        values={"DC": "DC", "AC": "AC", "LF_REJECT": "LFREJect", "HF_REJECT": "HFREJect"},
        cast=str,
    )

    trigger_edge_holdoff_events = Instrument.control(
        ":TRIGger:EDGE:HLDEVent?", ":TRIGger:EDGE:HLDEVent %d",
        """Control the number of holdoff events of the edge trigger (int),
        strictly in range [1, 100000000].""",
        validator=strict_range,
        values=[1, 100000000],
        cast=int,
    )

    trigger_edge_holdoff_time = Instrument.control(
        ":TRIGger:EDGE:HLDTime?", ":TRIGger:EDGE:HLDTime %.2E",
        """Control the holdoff time of the edge trigger in seconds (float).

        Note: the valid range varies by model; for T3DSO2000A/T3DSO3000 it
        is [8.00E-09, 3.00E+01].
        """,
        validator=strict_range,
        values=[8e-9, 3e1],
        cast=float,
    )

    trigger_edge_holdoff_type = Instrument.control(
        ":TRIGger:EDGE:HOLDoff?", ":TRIGger:EDGE:HOLDoff %s",
        """Control the holdoff type of the edge trigger (str), strictly in
        'OFF', 'EVENTS', 'TIME'.

        - OFF turns off the holdoff.
        - EVENTS holds off based on a number of trigger events (see
          :attr:`trigger_edge_holdoff_events`).
        - TIME holds off for a fixed duration (see
          :attr:`trigger_edge_holdoff_time`).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={"OFF": "OFF", "EVENTS": "EVENts", "TIME": "TIME"},
        cast=str,
    )

    trigger_edge_holdoff_start = Instrument.control(
        ":TRIGger:EDGE:HSTart?", ":TRIGger:EDGE:HSTart %s",
        """Control the initial position of the edge trigger holdoff (str),
        strictly in 'LAST_TRIG', 'ACQ_START'.""",
        validator=strict_discrete_set,
        values=["LAST_TRIG", "ACQ_START"],
        cast=str,
    )

    _trigger_edge_level = Instrument.control(
        ":TRIGger:EDGE:LEVel?", ":TRIGger:EDGE:LEVel %.2E",
        """Control the trigger level of the edge trigger, in Volts (float).

        Note: the legal range depends on the vertical scale and offset of
        the current trigger source channel (see :attr:`trigger_edge_source`):
        [-4.1 * vertical_scale - vertical_offset,
        4.1 * vertical_scale - vertical_offset].
        """,
        cast=float,
        validator=strict_range,
        values=[-float("inf"), float("inf")],  # Overwritten in setter
        dynamic=True,
    )

    def _get_trigger_source_channel(self):
        """Return the Channel object for the current edge-trigger source,
        or None if the source is not an analog channel (e.g. 'EX', 'LINE', 'D<n>')."""
        source = self.trigger_edge_source
        if source in ("C1", "C2", "C3", "C4"):
            return getattr(self, f"channel_{source[1]}")
        return None

    @property
    def trigger_edge_level(self) -> float:
        """Control the trigger level of the edge trigger, in Volts (float).

        Note: the legal range depends on the vertical scale and offset of
        the current trigger source channel (see :attr:`trigger_edge_source`):
        [-4.1 * vertical_scale - vertical_offset,
        4.1 * vertical_scale - vertical_offset].
        """
        return self._trigger_edge_level

    @trigger_edge_level.setter
    def trigger_edge_level(self, value):
        channel = self._get_trigger_source_channel()
        if channel is not None:
            scale = channel.scale
            offset = channel.offset
            self._trigger_edge_level_values = [
                -4.1 * scale - offset,
                4.1 * scale - offset,
            ]
        else:
            # z.B. EX/EX5/LINE/D<n> - validator deactivated, because of no scale and offset values
            self._trigger_edge_level_values = [-float("inf"), float("inf")]
        self._trigger_edge_level = value

    trigger_edge_noise_reject = Instrument.control(
        ":TRIGger:EDGE:NREJect?", ":TRIGger:EDGE:NREJect %s",
        """Control whether noise rejection is enabled for the edge trigger
        (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    trigger_edge_slope = Instrument.control(
        ":TRIGger:EDGE:SLOPe?", ":TRIGger:EDGE:SLOPe %s",
        """Control the slope of the edge trigger (str), strictly in 'RISING',
        'FALLING', 'ALTERNATE'.""",
        validator=strict_discrete_set,
        map_values=True,
        values={"RISING": "RISing", "FALLING": "FALLing", "ALTERNATE": "ALTernate"},
        cast=str,
    )

    trigger_edge_source = Instrument.control(
        ":TRIGger:EDGE:SOURce?", ":TRIGger:EDGE:SOURce %s",
        """Control the trigger source of the edge trigger (str).

        Legal values are 'C<x>' (analog channel, e.g. 'C1'), 'D<n>' (digital
        channel, e.g. 'D0'), 'EX', 'EX5', or 'LINE'.
        """,
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "D0", "D1", "D2", "D3", "D4", "D5", "D6",
                "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "EX",
                "EX5", "LINE"],
        cast=str,
    )

    measure = Instrument.control(
        ":MEASure?", ":MEASure %s",
        """Control the state of the measurement function. Strictly in bool 'True' or 'False'.""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    measure_mode = Instrument.control(
        ":MEASure:MODE?", ":MEASure:MODE %s",
        """Control the mode of measurement (str), strictly in 'SIMPLE' and 'ADVANCED'""",
        validator=strict_discrete_set,
        values={"SIMPLE": "SIMPle", "ADVANCED": "ADVanced"},
        map_values=True,
        cast=str,
    )

    MEASURE_PARAMETERS = {
        # Vertical (amplitude) measurements
        "PEAK_TO_PEAK": "PKPK",                 # Vertical peak-to-peak
        "MAXIMUM": "MAX",                       # Maximum vertical value
        "MINIMUM": "MIN",                       # Minimum vertical value
        "AMPLITUDE": "AMPL",                    # Vertical amplitude
        "TOP": "TOP",                           # Waveform top value
        "BASE": "BASE",                         # Waveform base value
        "LEVEL_AT_TRIGGER": "LEVELX",           # Level measured at the trigger position
        "MEAN_FIRST_CYCLE": "CMEAN",            # Average value in the first cycle
        "MEAN": "MEAN",                         # Average value
        "STD_DEV": "STDEV",                     # Standard deviation of the data
        "STD_DEV_FIRST_CYCLE": "VSTD",          # Standard deviation of the first cycle
        "RMS": "RMS",                           # RMS value
        "RMS_FIRST_CYCLE": "CRMS",              # RMS value in the first cycle
        "MEDIAN": "MEDIAN",                     # Value with 50% of samples above/below
        "MEDIAN_FIRST_CYCLE": "CMEDIAN",        # Median of the first cycle
        "OVERSHOOT_FALLING": "OVSN",            # Overshoot of a falling edge
        "PRESHOOT_FALLING": "FPRE",             # Preshoot of a falling edge
        "OVERSHOOT_RISING": "OVSP",             # Overshoot of a rising edge
        "PRESHOOT_RISING": "RPRE",              # Preshoot of a rising edge

        # Time / frequency measurements
        "PERIOD": "PER",                        # Period
        "FREQUENCY": "FREQ",                    # Frequency
        "TIME_OF_MAXIMUM": "TMAX",              # Time of maximum value
        "TIME_OF_MINIMUM": "TMIN",              # Time of minimum value
        "POSITIVE_PULSE_WIDTH": "PWID",         # Positive pulse width
        "NEGATIVE_PULSE_WIDTH": "NWID",         # Negative pulse width
        "WIDTH": "WID",                         # First rising edge to last falling edge @ 50%
        "POSITIVE_DUTY_CYCLE": "DUTY",          # Positive duty cycle
        "NEGATIVE_DUTY_CYCLE": "NDUTY",         # Negative duty cycle
        "NEGATIVE_WIDTH": "NBWID",              # First falling edge to last rising edge @ 50%
        "DELAY": "DELAY",                       # Trigger to first transition @ 50%
        "TIME_TO_EACH_RISING_EDGE": "TIMEL",    # Trigger to each rising edge @ 50%
        "RISE_TIME": "RISE",                    # Duration of rising edge, 10-90%
        "FALL_TIME": "FALL",                    # Duration of falling edge, 10-90%
        "RISE_TIME_20_80": "RISE20T80",         # Duration of rising edge, 20-80%
        "FALL_TIME_80_20": "FALL80T20",         # Duration of falling edge, 80-20%
        "PERIOD_JITTER": "CCJ",                 # Difference between two continuous periods

        # Area measurements
        "AREA_ABOVE_ZERO": "PAREA",             # Area of the waveform above zero
        "AREA_BELOW_ZERO": "NAREA",             # Area of the waveform below zero
        "AREA": "AREA",                         # Area of the waveform
        "ABSOLUTE_AREA": "ABSAREA",             # Absolute area of the waveform

        # Counting measurements
        "CYCLES": "CYCLES",                     # Number of cycles in a periodic waveform
        "RISING_EDGES": "REDGES",               # Number of rising edges
        "FALLING_EDGES": "FEDGES",              # Number of falling edges
        "EDGES": "EDGES",                       # Number of edges in a waveform
        "POSITIVE_PULSES": "PPULSES",           # Number of positive pulses (see note above)
        "NEGATIVE_PULSES": "NPULSES",           # Number of negative pulses (see note above)
    }
    """Mapping of descriptive measurement names to the SCPI parameter keywords
    accepted by :meth:`set_measurement_item`, as documented in the "Description
    of Parameters" table of the programming guide."""

    measurement_simple_source = Instrument.control(
        ":MEASure:SIMPle:SOURce?", ":MEASure:SIMPle:SOURce %s",
        """Control the source of the simple measurement (str), strictly one
        of the analog channels ('C1'..'C4'), zoomed waveforms ('Z1'..'Z4'),
        math functions ('F1'..'F4'), digital channels ('D0'..'D15'), zoomed
        digital channels ('ZD0'..'ZD15'), or reference waveforms
        ('REFA'..'REFD').

        Note: 'Z<x>'/'ZD<m>' are only valid while Zoom is on.
        """,
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4",
                "Z1", "Z2", "Z3", "Z4",
                "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15",
                "ZD0", "ZD1", "ZD2", "ZD3", "ZD4", "ZD5", "ZD6", "ZD7",
                "ZD8", "ZD9", "ZD10", "ZD11", "ZD12", "ZD13", "ZD14", "ZD15",
                "REFA", "REFB", "REFC", "REFD"],
        cast=str,
    )

    def set_measurement_item(self, parameter, enabled=True):
        """Add or remove a parameter from the simple measurement window.

        :param parameter: one of the keys in :attr:`MEASURE_PARAMETERS` (str),
            e.g. 'FREQUENCY', 'AMPLITUDE', 'RISE_TIME'.
        :param enabled: whether to enable (True) or disable (False) it in the
            simple measurement window.
        """
        parameter = strict_discrete_set(parameter.upper(), self.MEASURE_PARAMETERS.keys())
        scpi_param = self.MEASURE_PARAMETERS[parameter]
        state = "ON" if enabled else "OFF"
        self.write(f":MEASure:SIMPle:ITEM {scpi_param},{state}")

    def measurement_value(self, parameter):
        """Get the current value of the given simple-measurement parameter.

        :param parameter: one of the keys in :attr:`MEASURE_PARAMETERS` (str),
            e.g. 'FREQUENCY', 'AMPLITUDE', 'RISE_TIME', or 'ALL' to get all
            measurement values at once (except delay measurements).
        :return: the measured value in the parameter's native unit (float), or,
            if ``parameter == 'ALL'``, the raw response string as returned by
            the instrument (comma-separated values, one per active item).

        Note: for a parameter to return a meaningful value, it typically needs
        to be enabled first via :meth:`set_measurement_item`.
        """
        parameter = strict_discrete_set(
            parameter.upper(), list(self.MEASURE_PARAMETERS.keys()) + ["ALL"]
        )
        scpi_param = "ALL" if parameter == "ALL" else self.MEASURE_PARAMETERS[parameter]
        response = self.ask(f":MEASure:SIMPle:VALue? {scpi_param}").strip()
        if parameter == "ALL":
            return response
        return float(response)
