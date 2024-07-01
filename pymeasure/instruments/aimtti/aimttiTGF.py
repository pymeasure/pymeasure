#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from pymeasure.instruments import Instrument, Channel, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class TGF4000Channel(Channel):
    """A channel of AimTTI TGF4000 series function generator.

    Channels of the function generator. The channels are number from right-to-left, starting at 1.
    """
    WAVE = ['SINE', 'SQUARE', 'RAMP', 'TRIANG', 'PULSE', 'NOISE',
            'PRBSPN7', 'PRBSPN9', 'PRBSPN11', 'PRBSPN15', 'PRBSPN20', 'PRBSPN23', 'PRBSPN29', 'PRBSPN31',
            'ARB']

    def __init__(self, parent, id, voltage_range: list = None, current_range: list = None):
        super().__init__(parent, id)

        # self.voltage_setpoint_values = voltage_range
        # self.current_limit_values = current_range

    # Continuos carrier wave commands
    select_wave = Channel.setting(
        "WAVE %s",
        """ Control the output waveform for the current channel.""",
        validator=strict_discrete_set,
        values=WAVE
    )

    # FREQ < NRF >
    # PER < NRF >
    # AMPLRNG < CPD >
    # AMPL < NRF >
    # HILVL < NRF >
    # LOLVL < NRF >
    # DCOFFS < NRF >
    # OUTPUT < CPD >
    # ZLOAD < CPD >
    # SQRSYMM < NRF >
    # RMPSYMM < NRF >
    # SYNCOUT < CPD >
    # SYNCTYPE < CPD >
    # CHN2CONFIG < CPD >
    # PHASE < NRF >
    # ALIGN

    # Pulse generator commands
    set_pulse_freq = Channel.setting(
        "PULSFREQ %g",
        """Set the pulse waveform frequency to <NRF> Hz""",
        validator=strict_range,
        values=[0, 80e6]
    )

    set_pulse_period = Channel.setting(
        "PULSPER %g",
        """Set the pulse waveform period to <NRF> sec""",
    )

    set_pulse_width = Channel.setting(
        "PULSWID %g",
        """Set the pulse waveform width to <NRF> sec""",
    )

    set_pulse_width = Channel.setting(
        "PULSSYMM %g",
        """Set the pulse waveform symmetry to <NRF> %""",
        validator=strict_range,
        values=[0, 100]
    )

    set_pulse_edge = Channel.setting(
        "PULSEDGE %g",
        """Set the pulse waveform edges (positive and negative edge) to <NRF> sec""",
    )

    set_pulse_rise = Channel.setting(
        "PULSRISE %g",
        """Set the pulse waveform positive edge to <NRF> sec""",
    )

    set_pulse_fall = Channel.setting(
        "PULSFALL %g",
        """Set the pulse waveform negative edge to <NRF> sec""",
    )

    set_pulse_delay = Channel.setting(
        "PULSDLY %g",
        """Set the pulse waveform delay to <NRF> sec""",
    )

    # PRBS generator commands
    # PRBSBITRATE <NRF>

    # Arbitrary waveform commands





class TGF4000Base(SCPIUnknownMixin, Instrument):
    """Control AimTTI TGF4000 Base series function generator.

    Documentation:
        https://resources.aimtti.com/manuals/TGF4000_Series_Instruction_Manual-Iss3.pdf
    TGF4000-series devices:
        https://www.aimtti.com/product-category/function-generators/aim-tgf4000

    The default value for the timeout argument is set to 5000ms.

    .. code-block:: python

        fun = TGF4082("ASRL7::INSTR")
        # psu.reset()
        # psu.ch_2.voltage = 1.2
        # psu.ch_2.output_enabled = True
        # ...
        # psu.ch_2.output_enabled = False
        # psu.local()

    """

    def __init__(self, adapter, name="AimTTI PL", **kwargs):
        kwargs.setdefault("timeout", 5000)
        super().__init__(adapter, name, **kwargs)

    select_channel = Instrument.control(
        "CHN?",
        "CHN{ch}",
        "Set channel as the destination for subsequent commands. Can be 1 or 2.",
        validator=strict_discrete_set,
        values=[1, 2]
    )

    def local(self):
        """Go to local. Make sure all output are disabled first."""
        self.write("LOCAL")


class TGF4082(TGF4000Base):
    ch_1: TGF4000Channel = Instrument.ChannelCreator(
        TGF4000Channel, "1",
    )
    ch_2: TGF4000Channel = Instrument.ChannelCreator(
        TGF4000Channel, "2",
    )

    def __init__(self, adapter, name="AimTTI TGF4082", **kwargs):
        super().__init__(adapter, name, **kwargs)
