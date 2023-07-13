#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range
from pymeasure.adapters.visa import VISAAdapter
from pyvisa import constants

import numpy as np
import time


class Lotus_DAT(Instrument):
    """ Represents the RC_DAT programmable attenuator and provides a high level
    interface to the SCPI commands. Requires that the mcl_RUDAT_NET45 be in the path
    or same directory as the running code. You may need to unblock the dll by right clicking
    and opening the properties.

    """

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "Lotus Systems Digital step Attenuator",
            **kwargs
        )
        self.adapter.connection.flow_control = constants.VI_ASRL_FLOW_XON_XOFF

    attenuation = Instrument.control(
        "ATT?", "ATT %g",
        """ Set or gets the attenuation. Range is 0, 31.75 dB in .5 dB steps """,
        validator=strict_range,
        values=[0,31.75],
    )


    def set_mode(self, mode):
        """Sets the attenuator mode to FIX, Sweep, or List"""
        self.ask(f'ATTM {mode}')

    def save_to_flash(self):
        """Save current settings to flash"""
        self.write('SAVE')