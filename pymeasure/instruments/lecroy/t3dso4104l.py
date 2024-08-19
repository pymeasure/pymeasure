#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import sleep, time
import struct
from pyvisa.errors import VisaIOError
from pymeasure.instruments.lecroy.t3dsobase import LecroyT3DSOBase, ChannelBase


class LecroyT3DSO4104L(LecroyT3DSOBase):
    """ Represents the Lecroy T3DSO4104L scope.

    .. code-block:: python

        scope = LecroyT3DSO4104L(resource)
        
        scope.shutdown()

    """

    BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, *args, **kwargs):
        super(LecroyT3DSO4104L, self).__init__(
            adapter, "LecroyT3DSO4104L", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.system_headers = False
        self.ch1 = ChannelBase(self, 1)
        self.ch2 = ChannelBase(self, 2)
        self.ch3 = ChannelBase(self, 3)
        self.ch4 = ChannelBase(self, 4)


    def trigger_edge_source(self, channel):
        #good
        """
        Function to set the edge trigger source. Does not implement Digital
        Line. 
        :param channel: Integer corresponding to a given channel (0 is aux)
        :return:
        """
        if channel == 0:
            source = 'EX'
        elif channel in [1, 2, 3, 4]:
            source = 'C%d' % channel
        else:
            raise ValueError(f'{channel} not a valid trigger source')
        self.write(f""":TRIGger:EDGE:SOURce %s""")


    ################
    # System Setup #
    ################


    def ch(self, channel_number):
        #good
        if not isinstance(channel_number, int):
            raise ValueError(f'Channel number must be an int, not {type(channel_number)}')
        if channel_number in [1,2,3,4]:
            return getattr(self, f'ch{channel_number}')
        else:
            raise ValueError(f"Invalid channel number: {channel_number}. Must be 1-4.")
