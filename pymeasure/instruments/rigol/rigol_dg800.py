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
from pymeasure.instruments.validators import truncated_discrete_set

from .rigol_generator import (
    RigolGenerator,
    RigolGeneratorChannel,
)


class VoltageChannel(RigolGeneratorChannel):
    """Represents a voltage channel of the DG800 signal generator."""

    # LEGACY! Set load='INF' for high impedance.
    high_impedance = Channel.setting(
        ":OUTP{ch}:IMP %s",
        """Control the output impedance to be HighZ.
        This means displayed voltages will be internally converted to
        correspond that seen by an infinite load, not 50 Ohms.
        See p. 82 of the manual for more information.""",
        validator=truncated_discrete_set,
        values={True: "INF", False: "50"},
        map_values=True,
    )

    noise = Channel.setting(
        ":SOUR{ch}:APPL:NOIS %f,%f",
        """
        Set the waveform generator to output noise of specified parameters
        :param ampl: (float) The peak to peak amplitude of the noise in V
        :param offset: (float) The DC offset of the noise in V
        """,
    )

    dc = Channel.setting(
        ":SOUR{ch}:APPL:DC 1,1,%f",
        """
        Set the waveform generator to output a DC voltage in V.
        """,
    )

    shape = Channel.control(
        ":SOUR{ch}:FUNC?",
        ":SOUR{ch}:FUNC %s",
        """Control the waveform type of the specified channel.""",
        cast=str,
    )


class DG800(RigolGenerator):
    """Represents a Rigol DG800-series waveform generator
    and provides a high-level for interacting with the instrument
    """

    def __init__(self, adapter, name="DG800", **kwargs):
        super().__init__(adapter, name, **kwargs)

    channel_1 = Instrument.ChannelCreator(VoltageChannel, "1")
    channel_2 = Instrument.ChannelCreator(VoltageChannel, "2")
