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


import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class SFM(Instrument):
    """ Represents the Rohde&Schwarz SFM TV test transmitter
    interface for interacting with the instrument.

    .. code-block:: python

    """

    def __init__(self, resourceName, **kwargs):
        super(SFM, self).__init__(
            resourceName,
            "Rohde&Schwarz SFM",
            includeSCPI = True,
            **kwargs
        )
            # send_end = True,
            # read_termination = "\r\n",

    #TODO add CALIBRATION related entries

    output = Instrument.control(
        "OUTP?",
        "OUTP %s",
        """ A bool property that controls the output stage,
        False => output disabled,
        True => output enabled
        """,
        validator = strict_discrete_set,
        values={False:"OFF", True:"ON"},
        map_values = True,
        )

    #TODO add READ related entries

    #TODO check if ROUTE is also supported on SFM

    #TODO check if SENSE is also supported on SFM

    #TODO put more from the SOURCE subsystem in

    cw_frequency = Instrument.control(
        "SOUR:FREQ?",
        "SOUR:FRE:CW %g",
        """A float property controlling the frequency in Hz for fixed mode op,
        Minimum 5 MHz, Maximum 1 GHz""",
        validator = strict_range(5E6, 1E9),

        )


    modulation = Instrument.control(
        "SOUR:MOD?",
        "SOUR:MOD %s",
        """ A bool property that controls the modulation status,
        False => modulation disabled,
        True => modulation enabled
        """,
        validator = strict_discrete_set,
        values={False:"OFF", True:"ON"},
        map_values = True,
        )

    level = Instrument.control(
        "SOUR:POW:LEV:AMP?",
        "SOUR:FRE:LEV:AMP %g DBM",
        """A float property controlling the output level in dBm,
        Minimum -60dBm, Maximum 15dBm (To be verified)""",
        validator = strict_range(-60, 15),

        )

    #TODO add STATUS entries

    #TODO add SYSTEM entries


    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "R&S SFM: %s: %s" % (err[0],err[1])
                log.error(errmsg + '\n')
            else:
                break
