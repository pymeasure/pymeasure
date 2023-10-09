#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def get_process_generator_search(keyword, unit, type):
    """Generate a get_process method searching for keyword, stripping unit"""

    def selector(values):
        if keyword in values:
            try:
                return type(values[values.index(keyword) + 1].strip(unit))
            except (ValueError, IndexError):
                # Something went quite wrong if the keyword exists but the value doesn't
                return None
        else:
            # Wrong wavetype for this keyword
            return None

    return selector


class SignalChannel(Channel):
    output_enabled = Channel.control(
        "C{ch}:OUTPut?",
        "C{ch}:OUTPut %s",
        """Control whether the channel output is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ON', False: 'OFF'},
        # Replace ON and OFF with True and False in both get and set
        get_process=lambda x: True if x[0].split(' ')[1] == 'ON' else False,
    )

    wavetype = Channel.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV WVTP,%s",
        """Control the type of waveform to be output.
        Options are: {'SINE', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'ARB', 'DC', 'PRBS', 'IQ'}
        """,
        validator=strict_discrete_set,
        values=['SINE', 'SQUARE', 'RAMP', 'PULSE', 'NOISE', 'ARB', 'DC', 'PRBS', 'IQ'],
        get_process=lambda x: x[1],
    )

    frequency = Channel.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV FRQ,%g",
        """Control the frequency of waveform to be output in Hertz.
        Has no effect when WVTP is NOISE or DC.""",
        validator=strict_range,
        values=[0, 350e6],
        get_process=get_process_generator_search('FRQ', 'HZ', float),
        dynamic=True,
        check_set_errors=True,
    )

    amplitude = Channel.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV AMP,%g",
        """Control the amplitude of waveform to be output in volts peak-to-peak.
        Has no effect when WVTP is NOISE or DC.
        Max amplitude depends on offset, frequency, and load.
        Amplitude is also limited by the channel max output amplitude.""",
        validator=strict_range,
        values=[-5, 5],
        get_process=get_process_generator_search('AMP', 'V', float),
        dynamic=True,
        check_set_errors=True,
    )

    offset = Channel.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV OFST,%g",
        """Control the offset of waveform to be output in volts.
        Has no effect when WVTP is NOISE.
        Max offset depends on amplitude, frequency, and load.
        Offset is also limited by the channel max output amplitude.""",
        validator=strict_range,
        values=[-5, 5],
        get_process=get_process_generator_search('OFST', 'V', float),
        dynamic=True,
        check_set_errors=True,
    )

    max_output_amplitude = Channel.control(
        "C{ch}:BSWV?",
        "C{ch}:BSWV MAX_OUTPUT_AMP,%g",
        """Control the maximum output amplitude of the channel in volts peak to peak.""",
        validator=strict_range,
        values=[0, 20],
        get_process=get_process_generator_search('MAX_OUTPUT_AMP', 'V', float),
        dynamic=True,
    )


class TeledyneT3AFG(Instrument):
    """Represents the Teledyne T3AFG series of arbitrary waveform
    generator interface for interacting with the instrument.

    Initially targeting T3AFG80, some features may not be available on
    lower end models and features from higher end models are not
    included here yet.

    Future improvements (help welcomed):

    - Add other OUTPut related controls like Load and Polarity
    - Add other Basic Waveform related controls like Period
    - Add frequency ranges per model
    - Add channel coupling control

    .. code-block: python

        # Example assumes Ethernet (TCPIP) interface
        generator=TeledyneT3AFG('TCPIP0::xxx.xxx.xxx.xxx::pppp::SOCKET')
        generator.reset()
        generator.ch_1.wavetype='SINE'
        generator.ch_1.amplitude=2
        generator.ch_1.output_enabled=True
    """

    ch_1 = Instrument.ChannelCreator(SignalChannel, 1)

    ch_2 = Instrument.ChannelCreator(SignalChannel, 2)

    def __init__(self, adapter, name="Teledyne T3AFG", **kwargs):
        super().__init__(
            adapter, name, includeSCPI=True,
            tcpip={'read_termination': '\n'},
            **kwargs
        )
