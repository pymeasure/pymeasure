#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
# pyvirtualbench library: Copyright (c) 2015 Charles Armstrap <charles@armstrap.org>
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

from pymeasure.instruments.validators import (
    strict_discrete_set, strict_discrete_range,
    truncated_discrete_set, strict_range
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())






class EMCenter():
    """ Represents ETS-Lindgren EMCenter main frame.

    Subclasses implement the functionalities of the different modules:

        - Positioner card

       

    
    """

    def __init__(self, device_name='', name='EMCenter'):

   

    class EMCenterModule():
        def __init__(self, acquire_instr, reset,
                     instr_identifier, vb_name=''):
            """Initialize instrument 
            """
            # Parameters & Handle of VirtualBench Instance
            self._vb_handle = acquire_instr.__self__
            self._device_name = self._vb_handle.device_name
            self.name = (vb_name + " " + instr_identifier.upper()).strip()
            log.info("Initializing %s." % self.name)
            self._instrument_handle = acquire_instr(self._device_name, reset)
            self.isShutdown = False


    class PositionerCard(EMCenterModule):
        """ Position control card of EMCenter modular system.
        Allows for controll and feedback of the positioner card.
        """

        def __init__(self, virtualbench, lines, reset, vb_name=''):
        

   