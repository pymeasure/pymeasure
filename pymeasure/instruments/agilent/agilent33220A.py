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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Agilent33220A(Instrument):
    function = Instrument.control(
        "FUNC?", "FUNC %s",
        """ A string property that controls the output waveform. Can be set to:
        SIN<USOID>, SQU<ARE>, RAMP, PULS<E>, NOIS<E>, DC, USER. """,
        validator=strict_discrete_set,
        values=["SINUSOID", "SIN", "SQUARE", "SQU", "RAMP",
                "PULSE", "PULS", "NOISE", "NOIS", "DC", "USER"],
    )

    frequency = Instrument.control(
        "FREQ?", "FREQ %s",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from ... to .... Can be set. """,
        # validator=strict_range,
        # values=[..., ...]
    )

    voltage = Instrument.control(
        "VOLT?", "VOLT %f",
        """ A floating point property that controls the voltage amplitude of the output
        waveform in V, from ... to .... Can be set. """,
        # validator=strict_range,
        # values=[..., ...]
    )

    voltage_offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the output
        waveform in V, from ... to .... Can be set. """,
        # validator=strict_range,
        # values=[..., ...]
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the output
        waveform in V, from ... to .... Can be set. """,
        # validator=strict_range,
        # values=[..., ...]
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the output
        waveform in V, from ... to .... Can be set. """,
        # validator=strict_range,
        # values=[..., ...]
    )

# FUCNtion:SQUare:DCYCLe
# FUNCtion:RAMP:SYMMetry
# FUNCtion:PULSe:WIDTh <seconds>
# FUNCtion:PULSe:DCYCLe <percent>
# FUNCtion:PULSe:TRANsition <seconds>
# FUNCtion:PULSe:
# OUTPut
# OUTPut:LOAD ???
# OUTPut:POLarity {NORMal / INVerted}

# BURSt:MODE {TRIGgered / GATed}
# BURSt:NCYCLes

# TRIG
# OUTput:TRIGger {OFF / ON}

# SYSTem:LOCal
# SYSTem:REMote

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values("SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 33220A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
            else:
                break
