#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

import ctypes
import logging
import math
# from collections import namedtuple
from enum import IntFlag
# from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8


class HP6632A(Instrument):
    """ Represents the Hewlett Packard 6632A system power supply
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "HP6632A PSU",
            includeSCPI=False,
            send_end=True,
            read_termination="\r\n",
            **kwargs,
        )

    voltage = Instrument.control(
        "VOUT?", "VSET %g",
        """
        A floating point proptery that controls the output voltage of the device.

        """,
        validator=strict_range,
        values=[0, 20.475],
        )

    voltage_limit = Instrument.setting(
        "OVSET %g",
        """
        A floationg point property that sets the OVP threshold.

        """,
        validator=strict_range,
        values=[0, 22.0],
        )

    current = Instrument.control(
        "IOUT?", "ISET %g",
        """
        A floating point proptery that controls the output current of the device.

        """,
        validator=strict_range,
        values=[0, 5.1188],
        )

    id = Instrument.measurement(
        "ID?",
        """
        Reads the ID of the instrument and returns this value for now
        
        """, 
        )
    
    rom_Version = Instrument.measurement(
        "ROM?",
        """
        Reads the ROM id (software version) of the instrument and returns this value for now
        
        """, 
        )