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

    # CHANnel Commands
    #
    #   (✓)   :CHANnel<n>:BWLimit
    #   (✓)   :CHANnel<n>:COUPling
    #   (✓)   :CHANnel<n>:IMPedance
    #   (✓)   :CHANnel<n>:INVert
    #   (✓)   :CHANnel<n>:LABel
    #   (✓)   :CHANnel<n>:LABel:TEXT
    #   (✓)   :CHANnel<n>:OFFSet
    #   (✓)   :CHANnel<n>:PROBe
    #   (✓)   :CHANnel<n>:SCALe
    #   (✓)   :CHANnel<n>:SKEW
    #   (✓)   :CHANnel<n>:SWITch
    #   (✓)   :CHANnel<n>:UNIT
    #   (✓)   :CHANnel<n>:VISible

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

    _impedance: InstrumentProperty[float] = Channel.control(
        ":CHANnel{ch}:IMPedance?", ":CHANnel{ch}:IMPedance %s",
        """Control the input impedance of the channel in Ohms, strictly 50 or 1e6 (float).""",
        validator=strict_discrete_set,
        map_values=True,
        values={50.0: "FIFTy", 1e6: "ONEMeg"},
        cast=str,
    )

    @property
    def impedance(self) -> float:
        """Control the input impedance of the channel in Ohms, strictly 50 or 1e6 (float)."""
        return self._impedance

    @impedance.setter
    def impedance(self, value):
        self._impedance = value
        self.scale_values = [500e-6, 1.0] if value == 50.0 else [500e-6, 1e1]

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
        """Set the selected channel label to ON or OFF.
        Bool value 'True' or 'False'""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        cast=str,
    )

    label_text = Channel.control(
        ":CHANnel{ch}:LABel:TEXT?", ":CHANnel{ch}:LABel:TEXT %s",
        """Set the selected channel label to the string specified.""",
        validator=strict_length,
        values=20,
        cast=str,
    )

    skew = Channel.control(
        ":CHANnel{ch}:SKEW?", ":CHANnel{ch}:SKEW %.2E",
        """Set the channel-to-channel skew factor label specified.
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


class T3DSO3024HD(SCPIMixin, Instrument):
    """Represents the Teledyne T3DSO3024HD oscilloscope."""

    channel_1 = Instrument.ChannelCreator(T3DSO3024HDChannel, "1")
    channel_2 = Instrument.ChannelCreator(T3DSO3024HDChannel, "2")
    channel_3 = Instrument.ChannelCreator(T3DSO3024HDChannel, "3")
    channel_4 = Instrument.ChannelCreator(T3DSO3024HDChannel, "4")

    def __init__(self, adapter, name="Teledyne T3DSO3024HD Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)
