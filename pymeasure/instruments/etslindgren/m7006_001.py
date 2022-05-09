
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers

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
import re
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set, strict_discrete_range,
    truncated_discrete_set, strict_range
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())



class M7006_001(Instrument):
    """ Position control card of EMCenter modular system.
        Allows for controll and feedback of the positioner card.
        Comunication happes transparently through the EMCenter mainframe.
        devices share the resource name of the mainframe, and 
        are identified by the slot number and the device number(if applicable to the modual).
    """

    def __init__(self,resource_name, slot, device, **kwargs):

        kwargs.setdefault('write_termination', '\n')
        super().__init__(
            resource_name,
            "test",
            **kwargs
        )
        self._slot = slot
        self._device = device
    