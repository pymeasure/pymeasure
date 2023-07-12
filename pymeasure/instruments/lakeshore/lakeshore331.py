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

from pymeasure.instruments import Instrument
from pymeasure.instruments.lakeshore.lakeshore_base import LakeShoreTemperatureChannel, \
    LakeShoreHeaterChannel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LakeShore331(Instrument):
    """ Represents the Lake Shore 331 Temperature Controller and provides
    a high-level interface for interacting with the instrument. Note that the
    331 provides two input channels (A and B) and two output channels (1 and 2).
    This driver makes use of the :ref:`LakeShoreChannels`.

    .. code-block:: python

        controller = LakeShore331("GPIB::1")

        print(controller.output_1.setpoint)         # Print the current setpoint for loop 1
        controller.output_1.setpoint = 50           # Change the loop 1 setpoint to 50 K
        controller.output_1.heater_range = 'low'    # Change the heater range to low.
        controller.input_A.wait_for_temperature()   # Wait for the temperature to stabilize.
        print(controller.input_A.temperature)       # Print the temperature at sensor A.
    """
    input_A = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'A')

    input_B = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'B')

    output_1 = Instrument.ChannelCreator(LakeShoreHeaterChannel, 1)

    output_2 = Instrument.ChannelCreator(LakeShoreHeaterChannel, 2)

    def __init__(self, adapter, name="Lakeshore Model 336 Temperature Controller", **kwargs):
        kwargs.setdefault('read_termination', "\r\n")
        super().__init__(
            adapter,
            name,
            **kwargs
        )
