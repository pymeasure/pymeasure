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

from pymeasure.instruments import Instrument, discreteTruncate
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set, truncated_range

import numpy as np
import time
import re


class ThorlabsPro8000(Instrument):
    """Represents Thorlabs Pro 8000 modular laser driver"""
    SLOTS = range(1,9)
    LDC_POLARITIES = ['AG', 'CG']
    STATUS = ['ON','OFF']


    def __init__(self, resourceName, **kwargs):
        super(ThorlabsPro8000, self).__init__(
            resourceName,
            "Thorlabs Pro 8000",
            **kwargs
        )
        self.write(':SYST:ANSW VALUE')

    # Code for general purpose commands (mother board related)
    slot = Instrument.control(":SLOT?", ":SLOT %d",
                                "Slot selection. Allowed values are: {}""".format(SLOTS),
                                validator=strict_discrete_set,
                                values=SLOTS,
                                map_values=False)

    # Code for LDC-xxxx daughter boards (laser driver)
    LDCCurrent = Instrument.control(":ILD:SET?", ":ILD:SET %g",
                                """Laser current.""")
    LDCCurrentLimit = Instrument.control(":LIMC:SET?", ":LIMC:SET %g",
                                """Set Software current Limit (value must be lower than hardware current limit).""")
    LDCPolarity = Instrument.control(":LIMC:SET?", ":LIMC:SET %s",
                                """Set laser diode polarity. Allowed values are: {}""".format(LDC_POLARITIES),
                                validator=strict_discrete_set,
                                values=LDC_POLARITIES,
                                map_values=False)
    LDCStatus = Instrument.control(":LASER?", ":LASER %s",
                                """Set laser diode status. Allowed values are: {}""".format(STATUS),
                                validator=strict_discrete_set,
                                values=STATUS,
                                map_values=False)

    # Code for TED-xxxx daughter boards (TEC driver)
    TEDStatus = Instrument.control(":TEC?", ":TEC %s",
                                """Set TEC status. Allowed values are: {}""".format(STATUS),
                                validator=strict_discrete_set,
                                values=STATUS,
                                map_values=False)
    TEDSetTemperature = Instrument.control(":TEMP:SET?", ":TEMP:SET %g",
                                """Set TEC temperature""")
