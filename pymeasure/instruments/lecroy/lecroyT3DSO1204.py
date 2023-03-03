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

import logging
import re
import sys
import time
from decimal import Decimal

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.teledyne.teledyne_oscilloscope import TeledyneOscilloscope,\
    TeledyneOscilloscopeChannel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, \
    strict_discrete_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LeCroyT3DSO1204Channel(TeledyneOscilloscopeChannel):
    """ Implementation of a LeCroy T3DSO1204 Oscilloscope channel.

    Implementation modeled on Channel object of Keysight DSOX1102G instrument.
    """
    pass


class LeCroyT3DSO1204(TeledyneOscilloscope):
    """ Represents the LeCroy T3DSO1204 Oscilloscope interface for interacting with the instrument.

    Refer to the LeCroy T3DSO1204 Oscilloscope Programmer's Guide for further details about
    using the lower-level methods to interact directly with the scope.

    Attributes:
        WRITE_INTERVAL_S: minimum time between two commands. If a command is received less than
        WRITE_INTERVAL_S after the previous one, the code blocks until at least WRITE_INTERVAL_S
        seconds have passed.
        Because the oscilloscope takes a non neglibile time to perform some operations, it might
        be needed for the user to tweak the sleep time between commands.
        The WRITE_INTERVAL_S is set to 10ms as default however its optimal value heavily depends
        on the actual commands and on the connection type, so it is impossible to give a unique
        value to fit all cases. An interval between 10ms and 500ms second proved to be good,
        depending on the commands and connection latency.

    .. code-block:: python

        scope = LeCroyT3DSO1204(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_waveform(source="C1", points=2000)
        # ...
        scope.shutdown()
    """

    _BOOLS = {True: "ON", False: "OFF"}

    WRITE_INTERVAL_S = 0.02  # seconds

    ch_1 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 1)

    ch_2 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 2)

    ch_3 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 3)

    ch_4 = Instrument.ChannelCreator(LeCroyT3DSO1204Channel, 4)

    def __init__(self, adapter, name="LeCroy T3DSO1204 Oscilloscope", **kwargs):
        super().__init__(adapter, name, **kwargs)
