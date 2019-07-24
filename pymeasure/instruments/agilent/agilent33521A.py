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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from .agilent33500 import Agilent33500


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Agilent33521A(Agilent33500):
    """Represents the Agilent 33521A Function/Arbitrary Waveform Generator.
    This documentation page shows only methods different from the parent class :doc:`Agilent33500 <agilent33500>`.

    """

    def __init__(self, adapter, **kwargs):
        super(Agilent33521A, self).__init__(
            adapter,
            **kwargs
        )

    frequency = Instrument.control(
        "FREQ?", "FREQ %f",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1 uHz to 30 MHz, depending on the specified function.
        Can be set. """,
        validator=strict_range,
        values=[1e-6, 30e+6],
    )

    arb_srate = Instrument.control(
        "FUNC:ARB:SRAT?", "FUNC:ARB:SRAT %f",
        """ An floating point property that sets the sample rate of the currently selected 
        arbitrary signal. Valid values are 1 µSa/s to 250 MSa/s. This can be set. """,
        validator=strict_range,
        values=[1e-6, 250e6],
    )