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
from pymeasure.instruments import Instrument
from .keysightN7744C import KeysightN7744C, MPPMChannel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KeysightN7745C(KeysightN7744C):
    """
    This represents the Keysight N7745C Optical Multiport Power Meter interface.

    .. code-block:: python

        mppm = KeysightN7745C(address)

    """

    def __init__(self, adapter, name="N7745C Optical Multiport Power Meter", **kwargs):
        super().__init__(
            adapter, name, **kwargs)

    channel_5 = Instrument.ChannelCreator(MPPMChannel, 5)
    channel_6 = Instrument.ChannelCreator(MPPMChannel, 6)
    channel_7 = Instrument.ChannelCreator(MPPMChannel, 7)
    channel_8 = Instrument.ChannelCreator(MPPMChannel, 8)
