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

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set

class smu1(Instrument):
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "SMU1 of Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )

    channel_mode = Instrument.control(
        ":PAGE:CHAN:SMU1:MODE?",
        ":PAGE:CHAN:SMU1:MODE %s",
        """ A string property that controls the SMU1 channel mode,
        which can take the values 'V', 'I' or 'COMM'.
        VPULSE AND IPULSE are not yet supportedself.
        """,
        validator=strict_discrete_set,
        values=["V", "I", "COMM"],
        check_set_errors=True,
        check_get_errors=True,
    )

    channel_function = Instrument.control(
        ":PAGE:CHAN:SMU1:FUNC?",
        ":PAGE:CHAN:SMU1:FUNC %s",
        """ A string property that controls the SMU1 channel function,
        which can take the values 'VAR1', 'VAR2', 'VARD' or 'CONS'.
        """,
        validator=strict_discrete_set,
        values=["VAR1", "VAR2", "VARD", "COMM"],
        check_set_errors=True,
        check_get_errors=True,
    )

    @property
    def voltage_name(self):
        """ Gets the voltage name of the channel """
        return self.ask("PAGE:CHAN:SMU1:VNAME?").rstrip('\n')

    @voltage_name.setter
    def voltage_name(self, value):
        """ Sets the voltage name of the channel """
        value = smu1.__check_current_voltage_name(value)
        self.write(":PAGE:CHAN:SMU1:VNAME "'"%s"'"" % value)

    @property
    def current_name(self):
        """ Gets the current name of the channel """
        return self.ask("PAGE:CHAN:SMU1:INAME?").rstrip('\n')

    @current_name.setter
    def current_name(self, value):
        """ Sets the current name of the channel. """
        value = smu1.__check_current_voltage_name(value)
        self.write(":PAGE:CHAN:SMU1:INAME "'"%s"'"" % value)

    @staticmethod
    def __check_current_voltage_name(name):
        """ Checks if current and voltage names specified for channel
        conforms to the accepted naming scheme. Returns auto-corrected name
        starting with 'a' if name is unsuitable.
        """
        if (len(name) > 6) or not name[0].isalpha():
            new_name = 'a' + name[:5]
            log.info("Renaming %s to %s..." % (name, new_name))
            name = new_name
        return name
