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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.lakeshore.lakeshore_base import LakeShoreTemperatureChannel, \
    LakeShoreHeaterChannel


class LakeShore3xx(SCPIMixin, Instrument):
    """ Represents a Lake Shore Temperature Controller of the 3xx-Series and provides
    a high-level interface for interacting with the instrument.
    Multiple input-and output options are implemented.
    Not all channels exist in all device versions!
    Some devices can host input option cards to add more input channels.

    The LS 331 and 335 has two input channels (A and B) and two output channels (1 and 2).
    The LS 336  has four input channels (A, B, C and D) and four output channels (1, 2, 3 and 4).

    The LS 340 has two input channels (A and B) and one output channel (1).
    Following extension cards can be used:
    * 3465 Single Capacitance Input Option Card adds one channel (C).
    * 3462 Dual Standard Input Option Card adds two channels (C and D).
    * 3464 Dual Thermocouple Input Option Card adds two channels (C and D).
    * 3468 Eight Channel Input Option Card adds eight channels (C1-C4, D1-D4).

    The LS 350 has four input channels (A, B, C and D) and four output channels (1, 2, 3 and 4).
    Following extension card can be used:
    * 3062 4-Channel Scanner option adds 4 additional channels (D2, D3, D4, and D5).

    This driver makes use of the :ref:`LakeShoreChannels`.

    .. code-block:: python

        controller = LakeShore3xx("GPIB::1")

        print(controller.output_1.setpoint)         # Print the current setpoint for loop 1
        controller.output_1.setpoint = 50           # Change the loop 1 setpoint to 50 K
        controller.output_1.heater_range = 'low'    # Change the heater range to low.
        controller.input_A.wait_for_temperature()   # Wait for the temperature to stabilize.
        print(controller.input_A.kelvin)            # Print the temperature at sensor A.
    """
    input_A = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'A')
    input_B = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'B')
    input_C = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'C')
    input_D = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'D')
    input_C1 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'C1')
    input_C2 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'C2')
    input_C3 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'C3')
    input_C4 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'C4')
    input_D1 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'D1')
    input_D2 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'D2')
    input_D3 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'D3')
    input_D4 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'D4')
    input_D5 = Instrument.ChannelCreator(LakeShoreTemperatureChannel, 'D5')
    output_1 = Instrument.ChannelCreator(LakeShoreHeaterChannel, 1)
    output_2 = Instrument.ChannelCreator(LakeShoreHeaterChannel, 2)
    output_3 = Instrument.ChannelCreator(LakeShoreHeaterChannel, 3)
    output_4 = Instrument.ChannelCreator(LakeShoreHeaterChannel, 4)

    def __init__(self,
                 adapter,
                 name="Lakeshore Model 3xx Temperature Controller",
                 read_termination="\r\n",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            **kwargs
        )
