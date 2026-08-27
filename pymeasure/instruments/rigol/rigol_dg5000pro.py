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

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class VoltageChannel(Channel):
    """Represents a channel of the signal generator."""

    output_enabled = Channel.control(
        ":OUTPut{ch}:STATE?",
        ":OUTPut{ch}:STATe %s",
        """Control the status of the channel.
         True if the channel is on and False if not.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    frequency = Channel.control(
        ":SOURce{ch}:FREQuency?",
        ":SOURce{ch}:FREQuency %f",
        """Control the output frequency (Hz) of the channel.""",
        validator=strict_range,
        values=(1e-6, 500e6),
    )

    amplitude = Channel.control(
        ":SOURce{ch}:VOLTage?",
        ":SOURce{ch}:VOLTage %f",
        """Control the output amplitude""",
    )

    phase = Channel.control(
        ":SOURce{ch}:PHASe?",
        ":SOURce{ch}:PHASe %f",
        """Control channel phase""",
        validator=strict_range,
        values=(-360, 360),
    )

    function = Channel.control(
        ":SOURce{ch}:FUNCtion?",
        ":SOURce{ch}:FUNCtion %s",
        """Control Channel waveform (SIN,SQU,RAMP,PULS,NOIS,ARB,HARM,DC)""",
        validator=strict_discrete_set,
        values={"SIN", "SQU", "RAMP", "PULS", "NOIS", "ARB", "HARM", "DC"},
        cast=str
    )

    offset = Channel.control(
        ":SOURce{ch}:VOLTage:OFFset?",
        ":SOURce{ch}:VOLTage:OFFset %f",
        """Channel offset""",
    )

    voltage_unit = Channel.control(
        ":SOURce{ch}:VOLTage:UNIT?",
        ":SOURce{ch}:VOLTage:UNIT %s",
        """Control Channel voltage unit (VPP/VRMS/DBM)""",
        validator=strict_discrete_set,
        values={"VPP", "VRMS", "DBM"},
        cast=str
    )

    load = Channel.control(
        ":OUTPut{ch}:LOAD?",
        ":OUTPut{ch}:LOAD %s",
        """Control Channel load (1-10000 or Infinity)""",
    )

    psk_state = Channel.control(
        ":SOURce{ch}:PSKey:STATe?",
        ":SOURce{ch}:PSKey:STATe %s",
        """Control Channel PSK modulation (ON/OFF)""",
       validator=strict_discrete_set,
       values={True: 1, False: 0},
       map_values=True,
    )

    psk_phase = Channel.control(
        ":SOURce{ch}:PSKey:PHASe?",
        ":SOURce{ch}:PSKey:PHASe %f",
        """Control Channel PSK phase""",
        validator=strict_range,
        values=(0, 360),
    )

    psk_polarity = Channel.control(
        ":SOURce{ch}:PSKey:POLarity?",
        ":SOURce{ch}:PSKey:POLarity %s",
        """ Control Channel PSK polarity (POS/NEG)""",
        validator=strict_discrete_set,
        values={"POS", "NEG"},
        cast=str
    )

    psk_port = Channel.control(
        ":SOURce{ch}:PSKey:PORT?",
        ":SOURce{ch}:PSKey:PORT %s",
        """Control Channel PSK Port (FRON/REAR)""",
        validator=strict_discrete_set,
        values={"FRON", "REAR"},
        cast=str
    )

    psk_source = Channel.control(
        ":SOURce{ch}:PSKey:SOURce?",
        ":SOURce{ch}:PSKey:SOURce %s",
        """Control Channel PSK source (INT/EXT)""",
        validator=strict_discrete_set,
        values={"INT", "EXT"},
        cast=str
    )

class DG5000Pro(SCPIMixin, Instrument):
    """Control the Rigol DG5000Pro waveform generator."""

    def __init__(self, adapter, name="DG5000Pro", **kwargs):
        super().__init__(adapter, name, **kwargs)

    channel_1 = Instrument.ChannelCreator(VoltageChannel, "1")
    channel_2 = Instrument.ChannelCreator(VoltageChannel, "2")
    channel_3 = Instrument.ChannelCreator(VoltageChannel, "3")
    channel_4 = Instrument.ChannelCreator(VoltageChannel, "4")
    channel_5 = Instrument.ChannelCreator(VoltageChannel, "5")
    channel_6 = Instrument.ChannelCreator(VoltageChannel, "6")
    channel_7 = Instrument.ChannelCreator(VoltageChannel, "7")
    channel_8 = Instrument.ChannelCreator(VoltageChannel, "8")
