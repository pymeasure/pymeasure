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
        waveform in Hz, from 500e-6 (500 uHz) to 5e+6 (5 MHz). Can be set. """,
        validator=strict_range,
        values=[500e-6, 5e+6],
    )

    voltage = Instrument.control(
        "VOLT?", "VOLT %f",
        """ A floating point property that controls the voltage amplitude of the
        output waveform in V, from 1e-3 V to 10 V. Can be set. """,
        validator=strict_range,
        values=[10e-3, 10],
    )

    voltage_offset = Instrument.control(
        "VOLT:OFFS?", "VOLT:OFFS %f",
        """ A floating point property that controls the voltage offset of the
        output waveform in V, from 0 V to 4.995 V, depending on the set
        voltage amplitude (maximum offset = (10 - voltage) / 2). Can be set.
        """,
        validator=strict_range,
        values=[-4.995, +4.995],
    )

    voltage_high = Instrument.control(
        "VOLT:HIGH?", "VOLT:HIGH %f",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -4.990 V to 5 V (must be higher than low
        voltage). Can be set. """,
        validator=strict_range,
        values=[-4.99, 5],
    )

    voltage_low = Instrument.control(
        "VOLT:LOW?", "VOLT:LOW %f",
        """ A floating point property that controls the lower voltage of the
        output waveform in V, from -5 V to 4.990 V (must be lower than high
        voltage). Can be set. """,
        validator=strict_range,
        values=[-5, 4.99],
    )

    square_dutycycle = Instrument.control(
        "FUNC:SQU:DCYCL?", "FUNC:SQU:DCYCL %f",
        """ A floating point property that controls the duty cycle of a square
        waveform function in percent. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    ramp_symmetry = Instrument.control(
        "FUNC:RAMP:SYMM?", "FUNC:RAMP:SYMM %f",
        """ A floating point property that controls the symmetry percentage
        for the ramp waveform. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %f",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from ... s to ... s. Can be set
        and overwrites the frequency for *all* waveforms. """,
        # validator=strict_range,
        # values=[0, 100],
    )

    pulse_hold = Instrument.control(
        "FUNC:PULS:HOLD?", "FUNC:PULS:HOLD %s",
        """ A string property that controls if either the pulse width or the
        duty cycle is retained when changing the period or frequency of the
        waveform. Can be set to: WIDT<H> or DCYCL<E>. """,
        validator=strict_discrete_set,
        values=["WIDT", "WIDTH", "DCYCL", "DCYCLE"],
    )

    pulse_width = Instrument.control(
        "FUNC:PULS:WIDT?", "FUNC:PULS:WIDT %f",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from ... s to ... s. Can be set.
        """,
        # validator=strict_range,
        # values=[0, 100],
    )

    pulse_dutycycle = Instrument.control(
        "FUNC:PULS:DCYCL?", "FUNC:PULS:DCYCL %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent. Can be set. """,
        validator=strict_range,
        values=[0, 100],
    )

    pulse_transition = Instrument.control(
        "FUNC:PULS:TRAN?", "FUNC:PULS:TRAN %f",
        """ A floating point property that controls the duty cycle of a pulse
        waveform function in percent. Can be set. """,
        # validator=strict_range,
        # values=[0, 100],
    )


# PULSe:PERiod
# FUNCtion:PULSe:HOLD {WIDTh/DCYCle}
# FUNCtion:PULSe:WIDTh <seconds>
# FUNCtion:PULSe:TRANsition <seconds>

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
