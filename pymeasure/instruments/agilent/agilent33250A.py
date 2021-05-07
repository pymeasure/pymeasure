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

import logging
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set
from .agilent33220A import Agilent33220A


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Agilent33250A(Agilent33220A):
    """Represents the Agilent 33250A Function/Arbitrary Waveform Generator.
    This documentation page shows only methods different from the parent class :doc:`Agilent33220A <agilent33220A>`.

    """

    def __init__(self, adapter, **kwargs):
        super(Agilent33250A, self).__init__(
            adapter,
            **kwargs
        )

    frequency = Instrument.control(
        "FREQ?", "FREQ %g",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1 uHz to 80 MHz, depending on the specified function.
        Can be set. """,
        validator=strict_range,
        values=[1e-6, 80e+6],
    )

    pulse_width = Instrument.control(
        "PULS:WIDT?", "PULS:WIDT %g",
        """ A floating point property that controls the width of a pulse
        waveform function in seconds, ranging from 20 ns to 2000 s, within a
        set of restrictions depending on the period. Can be set. """,
        validator=strict_range,
        values=[8e-9, 2e3],
    )

    pulse_transition = Instrument.control(
        "PULS:TRAN?", "PULS:TRAN %g",
        """ A floating point property that controls the the edge time in
        seconds for both the rising and falling edges. It is defined as the
        time between 0.1 and 0.9 of the threshold. Valid values are between
        5 ns to 100 ns. Can be set. """,
        validator=strict_range,
        values=[5e-9, 100e-9],
    )

    pulse_period = Instrument.control(
        "PULS:PER?", "PULS:PER %f",
        """ A floating point property that controls the period of a pulse
        waveform function in seconds, ranging from 200 ns to 2000 s. Can be set
        and overwrites the frequency for *all* waveforms. If the period is
        shorter than the pulse width + the edge time, the edge time and pulse
        width will be adjusted accordingly. """,
        validator=strict_range,
        values=[20e-9, 2e3],
    )

    polarity = Instrument.control(
        "OUTPut:POLarity?", "OUTPut:POLarity %s",
        """ A string property controlling the output polarity. 'NORM' or 'INV'.""",
        validator = strict_range,
        values = ['NORM', 'INV']
    )

    burst_ncycles = Instrument.control(
        "BURS:NCYC?", "BURS:NCYC %d",
        """ An integer property that sets the number of cycles to be output
        when a burst is triggered. Valid values are 1 to 100000. This can be
        set. """,
        validator=strict_discrete_set,
        values=range(1, 1000000),
    )