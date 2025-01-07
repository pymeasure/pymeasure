#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import truncated_discrete_set


class VoltageChannel(Channel):
    """Represents a channel of the signal generator."""

    output_enabled = Channel.control(
        ":OUTP{ch}?",
        ":OUTP{ch} %s",
        """Control the status of the channel.
         True if the channel is on and False if not.""",
        validator=truncated_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    load = Channel.control(
        ":OUTP{ch}:LOAD?",
        ":OUTP{ch}:LOAD %f",
        """Control the output impedance of a given channel.
         Returns 9.9e+37 for infinite impedance.""",
    )

    high_impedance = Channel.control(
        ":OUTP{ch}:IMP?",
        ":OUTP{ch}:IMP %s",
        """Control the output impedance to be HighZ.
        This means displayed voltages will be internally converted to
        correspond that seen by an infinite load, not 50 Ohms.
        See p. 82 of the manual for more information.""",
        validator=truncated_discrete_set,
        values={True: "INF", False: "50"},
        map_values=True,
    )

    frequency = Channel.control(
        ":SOUR{ch}:FREQ?", ":SOUR{ch}:FREQ %f", """ Control the output frequency (Hz)"""
    )

    sync_enabled = Channel.control(
        ":OUTP{ch}:SYNC?",
        ":OUTP{ch}:SYNC %s",
        """Control the synchronization flag.
          True if the channel triggers the synchronization connector and False if not """,
        validator=truncated_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    sine = Channel.setting(
        ":SOUR{ch}:APPL:SIN %f,%f,%f,%f",
        """
        Set the waveform generator to output a sine of specified parameters
        :param int freq: The frequency of the sine in Hz
        :param float ampl: The peak to peak amplitude of the sine in V
        :param float offset: The DC offset of the sine in V
        :param float phase: The phase offset of the sine in degrees
        """,
    )
    square = Channel.setting(
        ":SOUR{ch}:APPL:SQU %f,%f,%f,%f",
        """
        Set the waveform generator to output a square wave of specified parameters
        :param int freq: The frequency of the wave in Hz
        :param float ampl: The peak to peak amplitude of the wave in V
        :param float offset: The DC offset of the wave in V
        :param float phase: The phase offset of the wave in degrees
        """,
    )
    triangle = Channel.setting(
        ":SOUR{ch}:APPL:RAMP %f,%f,%f,%f",
        """
        Set the waveform generator to output a triangle wave of specified parameters
        :param int freq: The frequency of the wave in Hz
        :param float ampl: The peak to peak amplitude of the wave in V
        :param float offset: The DC offset of the wave in V
        :param float phase: The phase offset of the wave in degrees
        """,
    )
    pulse = Channel.setting(
        ":SOUR{ch}:APPL:PULS %f,%f,%f,%f",
        """
        Set the waveform generator to output a pulse wave of specified parameters
        Note that the duty cycle is specified using the duty_cycle method.
        :param int freq: The frequency of the wave in Hz
        :param float ampl: The peak to peak amplitude of the wave in V
        :param float offset: The DC offset of the wave in V
        :param float phase: The phase offset of the wave in degrees
        """,
    )

    duty_cycle = Channel.control(
        ":SOUR{ch}:PULS:DCYC?",
        ":SOUR{ch}:PULS:DCYC %f",
        """
        Control the duty cycle of pulses out of the waveform generator. (float)
        """,
    )

    pulse_width = Channel.control(
        ":SOUR{ch}:PULS:WIDT?",
        ":SOUR{ch}:PULS:WIDT %f",
        """
        Control the pulse width of pulses (in seconds) out of the waveform generator.
        """,
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
        ":SOUR1:FUNC %s",
        """Control the waveform type of the specified channel.""",
    )

    waveform = Channel.measurement(
        ":SOUR{ch}:APPL?", """Get a descriptor of the waveform applied."""
    )


class DG800(SCPIMixin, Instrument):
    """Represents a Rigol DG800-series waveform generator
    and provides a high-level for interacting with the instrument
    """

    def __init__(self, adapter, name="DG800", **kwargs):
        super().__init__(adapter, name, **kwargs)

    channel_1 = Instrument.ChannelCreator(VoltageChannel, "1")
    channel_2 = Instrument.ChannelCreator(VoltageChannel, "2")
