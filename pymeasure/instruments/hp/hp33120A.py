#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_discrete_set


class HP33120A(Instrument):
    """ Represents the Hewlett Packard 33120A Arbitrary Waveform
    Generator and provides a high-level interface for interacting
    with the instrument.
    """

    SHAPES = {
        'sinusoid':'SIN', 'square':'SQU', 'triangle':'TRI', 
        'ramp':'RAMP', 'noise':'NOIS', 'dc':'DC', 'user':'USER'
    }
    shape = Instrument.control(
        "SOUR:FUNC:SHAP?", "SOUR:FUNC:SHAP %s",
        """ A string property that controls the shape of the wave,
        which can take the values: sinusoid, square, triangle, ramp,
        noise, dc, and user. """,
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True
    )
    frequency = Instrument.control(
        "SOUR:FREQ?", "SOUR:FREQ %g",
        """ A floating point property that controls the frequency of the
        output in Hz. The allowed range depends on the waveform shape
        and can be queried with :attr:`~.max_frequency` and 
        :attr:`~.min_frequency`. """
    )
    max_frequency = Instrument.measurement(
        "SOUR:FREQ? MAX", 
        """ Reads the maximum :attr:`~.HP33120A.frequency` in Hz for the given shape """
    )
    min_frequency = Instrument.measurement(
        "SOUR:FREQ? MIN", 
        """ Reads the minimum :attr:`~.HP33120A.frequency` in Hz for the given shape """
    )
    amplitude = Instrument.control(
        "SOUR:VOLT?", "SOUR:VOLT %g",
        """ A floating point property that controls the voltage amplitude of the
        output signal. The default units are in  peak-to-peak Volts, but can be
        controlled by :attr:`~.amplitude_units`. The allowed range depends 
        on the waveform shape and can be queried with :attr:`~.max_amplitude`
        and :attr:`~.min_amplitude`. """
    )
    max_amplitude = Instrument.measurement(
        "SOUR:VOLT? MAX", 
        """ Reads the maximum :attr:`~.amplitude` in Volts for the given shape """
    )
    min_amplitude = Instrument.measurement(
        "SOUR:VOLT? MIN", 
        """ Reads the minimum :attr:`~.amplitude` in Volts for the given shape """
    )
    offset = Instrument.control(
        "SOUR:VOLT:OFFS?", "SOUR:VOLT:OFFS %g",
        """ A floating point property that controls the amplitude voltage offset
        in Volts. The allowed range depends on the waveform shape and can be
        queried with :attr:`~.max_offset` and :attr:`~.min_offset`. """
    )
    max_offset = Instrument.measurement(
        "SOUR:VOLT:OFFS? MAX", 
        """ Reads the maximum :attr:`~.offset` in Volts for the given shape """
    )
    min_offset = Instrument.measurement(
        "SOUR:VOLT:OFFS? MIN", 
        """ Reads the minimum :attr:`~.offset` in Volts for the given shape """
    )
    AMPLITUDE_UNITS = {'Vpp':'VPP', 'Vrms':'VRMS', 'dBm':'DBM', 'default':'DEF'}
    amplitude_units = Instrument.control(
        "SOUR:VOLT:UNIT?", "SOUR:VOLT:UNIT %s",
        """ A string property that controls the units of the amplitude,
        which can take the values Vpp, Vrms, dBm, and default.
        """,
        validator=strict_discrete_set,
        values=AMPLITUDE_UNITS,
        map_values=True
    )

    def __init__(self, resourceName, **kwargs):
        super(HP33120A, self).__init__(
            resourceName,
            "Hewlett Packard 33120A Function Generator",
            **kwargs
        )
        self.amplitude_units = 'Vpp'

    def beep(self):
        """ Causes a system beep. """
        self.write("SYST:BEEP")
