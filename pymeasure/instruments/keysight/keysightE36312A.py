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


import logging

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class VoltageChannel(Channel):
    voltage_setpoint = Channel.control(
        "VOLT? (@{ch})",
        "VOLT %g, (@{ch})",
        """Control the output voltage of this channel, range depends on channel.""",
        validator=strict_range,
        values=[0, 25],
        dynamic=True,
    )

    current_limit = Channel.control(
        "CURR? (@{ch})",
        "CURR %g, (@{ch})",
        """Control the current limit of this channel, range depends on channel.""",
        validator=strict_range,
        values=[0, 1],
        dynamic=True,
    )

    voltage = Channel.measurement(
        "MEASure:VOLTage? (@{ch})",
        """Measure actual voltage of this channel."""
    )

    current = Channel.measurement(
        "MEAS:CURRent? (@{ch})",
        """Measure the actual current of this channel."""
    )

    output_enabled = Channel.control(
        "OUTPut? (@{ch})",
        "OUTPut %d, (@{ch})",
        """Control whether the channel output is enabled (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )


class KeysightE36312A(SCPIMixin, Instrument):
    """ Represents the Keysight E36312A Power supply
    interface for interacting with the instrument.

    .. code-block:: python

        supply = KeysightE36312A(resource)
        supply.ch_1.voltage_setpoint=10
        supply.ch_1.current_setpoint=0.1
        supply.ch_1.output_enabled=True
        print(supply.ch_1.voltage)
    """

    ch_1 = Instrument.ChannelCreator(VoltageChannel, 1)

    ch_2 = Instrument.ChannelCreator(VoltageChannel, 2)

    ch_3 = Instrument.ChannelCreator(VoltageChannel, 3)

    def __init__(self, adapter, name="Keysight E36312A", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )
        self.channels[1].voltage_setpoint_values = [0, 6]
        self.channels[1].current_limit_values = [0, 5]
