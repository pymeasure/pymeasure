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
from pymeasure.instruments.agilent.agilent4156.channels import *
from pymeasure.instruments.agilent.agilent4156.variables import *
from pymeasure.instruments.validators import *
import numpy as np


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

        self.smu1 = smu1(self.adapter)
        self.var1 = var1(self.adapter)
        self.var2 = var2(self.adapter)
        self.vard = vard(self.adapter)

    analyzer_mode = Instrument.control(
        ":PAGE:CHAN:MODE?", ":PAGE:CHAN:MODE %s",
        """ A string property that controls the analyzer's operating mode,
        which can take the values 'SWEEP' or 'SAMPLING'.
        """,
        validator=strict_discrete_set,
        values={'SWEEP': 'SWE', 'SAMPLING': 'SAMP'},
        map_values=True,
        check_set_errors=True,
        check_get_errors=True
    )

    integration_time = Instrument.control(
        ":PAGE:MEAS:MSET:ITIM?", ":PAGE:MEAS:MSET:ITIM %s",
        """ A string property that controls the integration time,
        which can take the values 'SHORT', 'MEDIUM' or 'LONG'.
        """,
        validator=strict_discrete_set,
        values={'SHORT': 'SHOR', 'MEDIUM': 'MED', 'LONG': 'LONG'},
        map_values=True,
        check_set_errors=True,
        check_get_errors=True
    )

    delay_time = Instrument.control(
        ":PAGE:MEAS:DEL?", ":PAGE:MEAS:DEL %g",
        """ A floating point property that measurement delay time in seconds,
        which can take the values from 0 to 65s in 0.1s steps.
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 65.1, 0.1),
        check_set_errors=True,
        check_get_errors=True
    )

    hold_time = Instrument.control(
        ":PAGE:MEAS:HTIME?", ":PAGE:MEAS:HTIME %g",
        """ A floating point property that measurement hold time in seconds,
        which can take the values from 0 to 655s in 1s steps.
        """,
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
