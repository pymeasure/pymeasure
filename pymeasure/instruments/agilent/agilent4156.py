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

from pymeasure.instruments import (Instrument, strict_discrete_set,
truncated_discrete_set, RangeException)
import numpy as np

class Common(object):
    """
    Collection of common internal functions used by the instrument driver.
    """

    def __init__(self):
        pass

    @staticmethod
    def __send_to_channel(channel):
        """ Creates the command string corresponding to the channel """
        return ':PAGE:CHAN:' + channel + ':'

    @staticmethod
    def __check_current_voltage_name(name):
        """ Checks if current and voltage names specified for channel
        conforms to the accepted naming scheme. Returns auto-corrected name
        starting with 'a' if name is unsuitable."""
        if (len(name) > 6) or not name[0].isalpha():
            name = 'a' + name[:5]
        return name

class SmuChannel(Instrument, Common):
    """ Base class to handle all operations related to a particular
    SMU channel on the instrument. Objects of this class are created by
    the main Agilent4156 class. It must not be used independently of
    the main class.
    """

    SMU_CHANNELS = ["SMU1", "SMU2", "SMU3", "SMU4"]

    def __init__(self, smu, **kwargs):
        super().__init__(
            self.resourceName,
            "SMU channel of Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )
        self.channel = smu

    channel_mode = Instrument.control(
        Common.__send_to_channel(self.channel) + "MODE?",
        Common.__send_to_channel(self.channel) + ":MODE %s",
        """ A string property that controls the channel mode,
        which can take the values 'V', 'I' or 'COMM'.
        VPULSE AND IPULSE are not yet supported""",
        validator=strict_discrete_set,
        values=["V", "I", "COMM"],
        check_set_errors=True,
        check_get_errors=True
    )

    channel_function = Instrument.control(
        Common.__send_to_channel(self.channel) + "FUNC?",
        Common.__send_to_channel(self.channel) + ":FUNC %s",
        """ A string property that controls the channel function,
        which can take the values 'VAR1', 'VAR2', 'VARD' or 'CONS'.""",
        validator=strict_discrete_set,
        values=["VAR1", "VAR2", "VARD", "CONS"],
        check_set_errors=True,
        check_get_errors=True
    )

    disable = Instrument.setting(
        Common.__send_to_channel(self.channel) + ":DIS",
        """ Disables the SMU Channel.""",
    )

    @property
    def voltage_name(self):
        """ Gets the voltage name of the SMU channel """
        return self.ask(Common.__send_to_channel(self.channel) + "VNAM?")

    @voltage_name.setter
    def voltage_name(self, name):
        """ Sets the voltage name of the SMU channel.
        Checks to see that the name is acceptable by instrument """
        name = Common.__check_current_voltage_name(name)
        self.write(Common.__send_to_channel(self.channel) "VNAM %s" % name)

    @property
    def current_name(self, ch):
        """ Gets the current name of the analyzer channel """
        return self.ask(Common.__send_to_channel(ch) + "INAM?")

    @current_name.setter
    def current_name(self, ch, name):
        """ Sets the current name of the analyzer channel.
        Checks to see that the name is acceptable by instrument """
        name = Common.__check_current_voltage_name(name)
        self.write(Common.__send_to_channel(ch) + "INAM %s" % name)

class Agilent4156(Instrument):
    """ Represents the Agilent 4155/4156 Semiconductor Parameter Analyzer
    and provides a high-level interface for taking I-V measurements.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )

        self.resourceName = resourceName

        for channel in SmuChannel.SMU_CHANNELS:
            self.channel = SmuChannel("%s" % channel)

        # for channel in VmuChannel.VMU_CHANNELS:
        #     self.channel = VmuChannel("%s" % channel)
        #
        # for channel in VsuChannel.VSU_CHANNELS:
        #     self.channel = VsuChannel("%s" % channel)

    analyzer_mode = Instrument.control(
        ":PAGE:CHAN:MODE?", ":PAGE:CHAN:MODE %s",
        """ A string property that controls the analyzer's operating mode,
        which can take the values 'SWEEP' or 'SAMPLING'.""",
        validator=strict_discrete_set,
        values={'SWEEP':'SWE', 'SAMPLING':'SAMP'},
        map_values = True,
        check_set_errors=True,
        check_get_errors=True
    )

    integration_time = Instrument.control(
        ":PAGE:MEAS:MSET:ITIM?", ":PAGE:MEAS:MSET:ITIM %s",
        """ A string property that controls the integration time,
        which can take the values 'SHORT', 'MEDIUM' or 'LONG'.""",
        validator=strict_discrete_set,
        values={'SHORT':'SHOR', 'MEDIUM':'MED', 'LONG':'LONG'},
        map_values = True,
        check_set_errors=True,
        check_get_errors=True
    )

    delay_time = Instrument.control(
        ":PAGE:MEAS:DEL?", ":PAGE:MEAS:DEL %g",
        """ A floating point property that measurement delay time in seconds,
        which can take the values from 0 to 65s in 0.1s steps.""",
        validator=truncated_discrete_set,
        values=np.arange(0, 65.1, 0.1),
        check_set_errors=True,
        check_get_errors=True
    )

    hold_time = Instrument.control(
        ":PAGE:MEAS:HTIME?", ":PAGE:MEAS:HTIME %g",
        """ A floating point property that measurement hold time in seconds,
        which can take the values from 0 to 655s in 1s steps.""",
        validator=truncated_discrete_set,
        values=np.arange(0, 655, 1),
        check_set_errors=True,
        check_get_errors=True
    )

    def save_in_display_list(self, name):
        """ Save the voltage or current in the instrument display list """
        self.write(':PAGE:DISP:MODE LIST')
        self.write(':PAGE:DISP:LIST ' + name)

    def save_in_variable_list(self, name):
        """ Save the voltage or current in the instrument variable list """
        self.write(':PAGE:DISP:MODE LIST')
        self.write(':PAGE:DISP:DVAR ' + name)
        if channel_in_group(ch, SMU_CHANNELS) is True:
            name = check_current_voltage_name(name)
            self.write(send_to_channel(ch) + "INAM %s" % name)
        else:
            raise ValueError("Cannot set current name for non-SMU units")
