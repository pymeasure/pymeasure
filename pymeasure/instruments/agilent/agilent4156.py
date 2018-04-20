#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

from pymeasure.instruments import Instrument, discreteTruncate, RangeException

import numpy as np
import re
from io import BytesIO


class Agilent4156(Instrument):
    """ Represents the Agilent 4155/4156 Semiconductor Parameter Analyzer
    and provides a high-level interface for taking I-V measurements.
    """

    SMU_CHANNELS = ["SMU1", "SMU2", "SMU3", "SMU4"]
    VSU_CHANNELS = ["VSU1", "VSU2"]
    VMU_CHANNELS = ["VMU1", "VMU2"]

    CHANNELS = SMU_CHANNELS + VSU_CHANNELS + VMU_CHANNELS

    def __init__(self, resourceName, **kwargs):
        super(Agilent4156, self).__init__(
            resourceName,
            "Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )

    analyzer_mode = Instrument.control(
        ":PAGE:CHAN:MODE?", ":PAGE:CHAN:MODE %s",
        """ A string property that controls the analyzer's operating mode,
        which can take the values 'sweep' or 'sampling'.""",
        validator=strict_discrete_set,
        values=['SWE', 'SAMP'],
        check_set_errors=True,
        check_get_errors=True
    )

    @staticmethod
    def send_to_channel(channel):
        """ Creates the command string corresponding to the channel """
        try:
            any(channel.upper() in x for x in CHANNELS)
        except:
            raise KeyError('Invalid channel name.')
        else:
            return ':PAGE:CHAN:' + channel.upper() + ':'

    @staticmethod
    def check_current_voltage_name(name):
        """ Checks if current and voltage names specified for channel
        conforms to the accepted naming scheme. Returns auto-corrected name
        starting with 'a' if name is unsuitable."""
        if (len(name) > 6) or not name[0].isalpha():
            name = 'a' + name[:5]
        return name

    @staticmethod
    def channel_in_group(ch, chlist):
        """ Checks that the specified channel belongs to a list of
        channels defined by chlist """
        if ch not in chlist:
            return False
        else:
            return True

    def save_in_display_list(self, name):
        """ Save the voltage or current in the instrument display list """
        self.write(':PAGE:DISP:MODE LIST')
        self.write(':PAGE:DISP:LIST ' + name)

    def save_in_variable_list(self, name):
        """ Save the voltage or current in the instrument variable list """
        self.write(':PAGE:DISP:MODE LIST')
        self.write(':PAGE:DISP:DVAR ' + name)

    def channel_mode(ch):
        return Instrument.control(
            send_to_channel(ch) + "MODE?", send_to_channel(ch) + ":MODE %s",
            """ A string property that controls the channel mode,
            which can take the values 'V', 'I' or 'COMM'.
            VPULSE AND IPULSE are not yet supported""",
            validator=strict_discrete_set,
            values=["V", "I", "COMM"],
            check_set_errors=True,
            check_get_errors=True
        )

    def channel_function(ch):
        if channel_in_group(ch, VMU_CHANNELS):
            raise ValueError("Cannot set channel function for VMU.")
        else:
            return Instrument.control(
            send_to_channel(ch) + "FUNC?", send_to_channel(ch) + ":FUNC %s",
            """ A string property that controls the channel function,
            which can take the values 'VAR1', 'VAR2', 'VARD' or 'CONS'.""",
            validator=strict_discrete_set,
            values=["VAR1", "VAR2", "VARD", "CONS"],
            check_set_errors=True,
            check_get_errors=True
        )

    @property
    def voltage_name(self, ch):
        """ Gets the voltage name of the analyzer channel """
        return self.ask(send_to_channel(ch) + "VNAM?")

    @voltage_name.setter
    def voltage_name(self, ch, name):
        """ Sets the voltage name of the analyzer channel.
        Checks to see that the name is acceptable by instrument """
        name = check_current_voltage_name(name)
        self.write(send_to_channel(ch) + "VNAM %s" % name)

    @property
    def current_name(self, ch):
        """ Gets the current name of the analyzer channel """
        if channel_in_group(ch, SMU_CHANNELS) is True:
            return self.ask(send_to_channel(ch) + "INAM?")
        else:
            return None

    @current_name.setter
    def current_name(self, ch, name):
        """ Sets the current name of the analyzer channel.
        Checks to see that the name is acceptable by instrument """
        if channel_in_group(ch, SMU_CHANNELS) is True:
            name = check_current_voltage_name(name)
            self.write(send_to_channel(ch) + "INAM %s" % name)
        else:
            raise ValueError("Cannot set current name for non-SMU units")
