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
from pymeasure.instruments.lecroy.maui import ChannelBase, LecroyMAUIBase
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import sleep, time
from pyvisa.errors import VisaIOError

MAX_SAMPLING = 10e9

class Channel(ChannelBase):
    """ Implementation of a Lecroy HDO4000 Oscilloscope channel.
     """

    def __init__(self, *args, **kwargs):
        """
        No deviations from base MAUI
        """
        super(Channel, self).__init__(*args, **kwargs)



class LecroyHDO4000(LecroyMAUIBase):
    """ Represents the Lecroy HDO4000 Oscilloscope interface for interacting
    with the instrument. Make sure you set the communication to LXI
    and not TCPIP (VICP) on the scope if you want this code to work out of the box.
    You'll get a message of "Warning: Remote Interface is TCPIP" if you forget.
    Also, when passing strings in a write command using the vbs system, the string arguments
    need to be inside double quotes. This is because the scope executes the sent command locally
    so it needs to be correctly delimited inside the SCPI style string. String-ception.

    .. code-block:: python

        scope = LecroyHDO4000(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="channel1", points=2000)
        # ...
        scope.shutdown()

    """


    def __init__(self, adapter, **kwargs):
        super(LecroyHDO4000, self).__init__(
            adapter, "Lecroy HDO4000 Oscilloscope", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.system_headers = False
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)

    def trigger_edge_source(self, channel):
        # good
        """
        Function to set the edge trigger source
        :param channel: Integer corresponding to a given channel (0 is aux)
        :return:
        """
        if channel == 0:
            source = 'Ext'
        elif channel in [1, 2, 3, 4]:
            source = 'C%d' % channel
        else:
            raise ValueError(f'{channel} not a valid trigger source')
        self.write(f"""VBS 'app.Acquisition.trigger.edge.Source ="{source}"'""")

    def ch(self, channel_number):
        # good
        if not isinstance(channel_number, int):
            raise ValueError(
                f'Channel number must be an int, not {type(channel_number)}')
        if channel_number in [1, 2, 3, 4]:
            return getattr(self, f'ch{channel_number}')
        else:
            raise ValueError(f"Invalid channel number: {channel_number}. Must be 1-4.")

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Lecroy HDO4000: %s: %s" % (err[0], err[1])
                log.error(errmsg + "\n")
            else:
                break