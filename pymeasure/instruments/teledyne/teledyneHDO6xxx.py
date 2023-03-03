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

import re

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments.teledyne.teledyneMAUI import TeledyneMAUI, TeledyneMAUIChannel


class TeledyneHDO6xxxChannel(TeledyneMAUIChannel):
    """Extended Channel object for :class:`TeledyneHDO6xxx`."""
    pass


class TeledyneHDO6xxx(TeledyneMAUI):
    """Reference to the Teledyne-Lecroy HDo6xxx class of oscilloscopes.

    Most functionality is inherited from :class:`LeCroyT3DSO1204`.

    It is unclear which manual details the exact API of the oscilloscope, but
    this file seems very close: "WavePro Remote Control Manual" (`link`_).
    The file is from 2002, but it still seems to apply to this model.

    .. _: https://cdn.teledynelecroy.com/files/manuals/wp_rcm_revc.pdf
    """

    channels = Instrument.ChannelCreator(TeledyneHDO6xxxChannel, (1, 2, 3, 4))

    @staticmethod
    def get_channel_cls():
        return TeledyneHDO6xxxChannel
