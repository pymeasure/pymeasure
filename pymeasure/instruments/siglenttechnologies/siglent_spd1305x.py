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
from pymeasure.instruments.instrument import Instrument
from pymeasure.instruments.siglenttechnologies.siglent_spdbase import (SPDSingleChannelBase,
                                                                       SPDChannel)


class SPD1305X(SPDSingleChannelBase):
    """Represent the Siglent SPD1305X Power Supply.
    """

    voltage_range = [0, 30]
    current_range = [0, 5]
    ch_1 = Instrument.ChannelCreator(SPDChannel, 1,
                                     voltage_range=voltage_range,
                                     current_range=current_range)

    def __init__(self, adapter, name="Siglent Technologies SPD1305X Power Supply", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.ch_1.voltage_setpoint_values = self.voltage_range
        self.ch_1.current_limit_values = self.current_range
