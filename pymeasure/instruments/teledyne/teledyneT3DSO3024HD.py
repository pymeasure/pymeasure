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

from pymeasure.instruments import Channel, Instrument
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
    
    scale = Channel.control(
        ":CHANnel{ch}:SCALe?", ":CHANnel{ch}:SCALe %.3E",
        """Control the vertical scale of the channel in Volts/div (float).""",
        validator=strict_range,
        values=[500e-6, 1e2],
        cast=float,
    )


class T3DSO3024HD(SCPIMixin, Instrument):
    """Represents the Teledyne T3DSO3024HD oscilloscope."""

    channel_1 = Instrument.ChannelCreator(T3DSO3024HDChannel, "1")
    channel_2 = Instrument.ChannelCreator(T3DSO3024HDChannel, "2")
    channel_3 = Instrument.ChannelCreator(T3DSO3024HDChannel, "3")
    channel_4 = Instrument.ChannelCreator(T3DSO3024HDChannel, "4")

    def __init__(self, adapter, name="Teledyne T3DSO3024HD Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)
