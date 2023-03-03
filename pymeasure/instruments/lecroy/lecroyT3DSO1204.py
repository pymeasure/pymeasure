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

    _BANDWIDTH_LIMITS = ["OFF", "ON"]

    _TRIGGER_SLOPES = {"negative": "NEG", "positive": "POS", "window": "WINDOW"}

    bwlimit = Instrument.control(
        "BWL?", "BWL %s",
        """ Toggles the 20 MHz internal low-pass filter. (strict bool)""",
        validator=strict_discrete_set,
        values=TeledyneOscilloscopeChannel._BOOLS,
        map_values=True
    )

    invert = Instrument.control(
        "INVS?", "INVS %s",
        """ Toggles the inversion of the input signal. (strict bool)""",
        validator=strict_discrete_set,
        values=TeledyneOscilloscopeChannel._BOOLS,
        map_values=True
    )

    skew_factor = Instrument.control(
        "SKEW?", "SKEW %.2ES",
        """ Channel-to-channel skew factor for the specified channel. Each analog channel can be
        adjusted + or -100 ns for a total of 200 ns difference between channels. You can use
        the oscilloscope's skew control to remove cable-delay errors between channels.
        """,
        validator=strict_range,
        values=[-1e-7, 1e-7],
        preprocess_reply=lambda v: v.rstrip('S')
    )

    trigger_level2 = Instrument.control(
        "TRLV2?", "TRLV2 %.2EV",
        """ A float parameter that sets the lower trigger level voltage for the specified source.
        Higher and lower trigger levels are used with runt/slope triggers.
        When setting the trigger level it must be divided by the probe attenuation. This is
        not documented in the datasheet and it is probably a bug of the scope firmware.
        An out-of-range value will be adjusted to the closest legal value.
        """
    )

    unit = Instrument.control(
        "UNIT?", "UNIT %s",
        """ Unit of the specified trace. Measurement results, channel sensitivity, and trigger
        level will reflect the measurement units you select. ("A" for Amperes, "V" for Volts).""",
        validator=strict_discrete_set,
        values=["A", "V"]
    )


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

    ##################
    # Timebase Setup #
    ##################

    timebase_hor_magnify = Instrument.control(
        "HMAG?", "HMAG %.2ES",
        """ A float parameter that sets the zoomed (delayed) window horizontal scale (
        seconds/div). The main sweep scale determines the range for this command. """,
        validator=strict_range,
        values=[1e-9, 20e-3]
    )

    timebase_hor_position = Instrument.control(
        "HPOS?", "HPOS %.2ES",
        """ A string parameter that sets the horizontal position in the zoomed (delayed) view of
        the main sweep. The main sweep range and the main sweep horizontal position determine
        the range for this command. The value for this command must keep the zoomed view window
        within the main sweep range.""",
    )

    @property
    def timebase(self):
        """ Read timebase setup as a dict containing the following keys:
            - "timebase_scale": horizontal scale in seconds/div (float)
            - "timebase_offset": interval in seconds between the trigger and the reference
            position (float)
            - "timebase_hor_magnify": horizontal scale in the zoomed window in seconds/div (float)
            - "timebase_hor_position": horizontal position in the zoomed window in seconds
            (float)"""
        tb_setup = {
            "timebase_scale": self.timebase_scale,
            "timebase_offset": self.timebase_offset,
            "timebase_hor_magnify": self.timebase_hor_magnify,
            "timebase_hor_position": self.timebase_hor_position
        }
        return tb_setup

    def timebase_setup(self, scale=None, offset=None, hor_magnify=None, hor_position=None):
        """ Set up timebase. Unspecified parameters are not modified. Modifying a single parameter
        might impact other parameters. Refer to oscilloscope documentation and make multiple
        consecutive calls to timebase_setup if needed.

        :param scale: interval in seconds between the trigger event and the reference position.
        :param offset: horizontal scale per division in seconds/div.
        :param hor_magnify: horizontal scale in the zoomed window in seconds/div.
        :param hor_position: horizontal position in the zoomed window in seconds."""

        if scale is not None:
            self.timebase_scale = scale
        if offset is not None:
            self.timebase_offset = offset
        if hor_magnify is not None:
            self.timebase_hor_magnify = hor_magnify
        if hor_position is not None:
            self.timebase_hor_position = hor_position
