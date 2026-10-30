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

from pymeasure.instruments import AdapterType, Instrument
from pymeasure.instruments.validators import strict_range

from .agilent33500 import Agilent33500, Agilent33500Channel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Voltage ranges for a high impedance load, the widest possible
AMPLITUDE_RANGE = [1e-3, 20]
OFFSET_RANGE = [-10, 10]
VOLTAGE_HIGH_RANGE = [-9.999, 10]
VOLTAGE_LOW_RANGE = [-10, 9.999]
PULSE_PERIOD_RANGE = [10e-9, 1e6]
PULSE_WIDTH_RANGE = [5e-9, 1e6]
PULSE_TRANSITION_RANGE = [2.9e-9, 1e-6]
BURST_NCYCLES_RANGE = range(1, 100_000_001)
ARB_SRATE_RANGE = [1e-6, 1e9]


class Agilent33622AChannel(Agilent33500Channel):
    """A channel of the Agilent 33622A waveform generator."""

    amplitude_values = AMPLITUDE_RANGE
    offset_values = OFFSET_RANGE
    voltage_high_values = VOLTAGE_HIGH_RANGE
    voltage_low_values = VOLTAGE_LOW_RANGE
    pulse_period_values = PULSE_PERIOD_RANGE
    pulse_width_values = PULSE_WIDTH_RANGE
    pulse_transition_values = PULSE_TRANSITION_RANGE
    burst_ncycles_values = BURST_NCYCLES_RANGE

    arb_srate = Instrument.control(
        "SOUR{ch}:FUNC:ARB:SRAT?",
        "SOUR{ch}:FUNC:ARB:SRAT %f",
        """Control the sample rate of the currently selected arbitrary signal in Sa/s
        (float strictly from 1e-6 to 1e9).

        The maximum sample rate is 250 MSa/s if the arbitrary waveform filter is 'OFF'.""",
        validator=strict_range,
        values=ARB_SRATE_RANGE,
    )


class Agilent33622A(Agilent33500):
    """Represent the Agilent 33622A Waveform Generator.

    .. code-block:: python

        generator = Agilent33622A("TCPIP::192.168.0.10::INSTR")

        generator.channels[1].shape = "SIN"
        generator.channels[1].frequency = 100e6     # 100 MHz
        generator.channels[1].amplitude = 1e-3      # 1 mVpp
        generator.channels[1].output = True
    """

    def __init__(self, adapter: AdapterType, name: str = "Agilent 33622A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    ch_1 = Instrument.ChannelCreator(Agilent33622AChannel, 1)
    ch_2 = Instrument.ChannelCreator(Agilent33622AChannel, 2)

    amplitude_values = AMPLITUDE_RANGE
    offset_values = OFFSET_RANGE
    voltage_high_values = VOLTAGE_HIGH_RANGE
    voltage_low_values = VOLTAGE_LOW_RANGE
    pulse_period_values = PULSE_PERIOD_RANGE
    pulse_width_values = PULSE_WIDTH_RANGE
    pulse_transition_values = PULSE_TRANSITION_RANGE
    burst_ncycles_values = BURST_NCYCLES_RANGE

    arb_srate = Instrument.control(
        "FUNC:ARB:SRAT?",
        "FUNC:ARB:SRAT %f",
        """Control the sample rate of the currently selected arbitrary signal in Sa/s
        (float strictly from 1e-6 to 1e9).

        The maximum sample rate is 250 MSa/s if the arbitrary waveform filter is 'OFF'.""",
        validator=strict_range,
        values=ARB_SRATE_RANGE,
    )
