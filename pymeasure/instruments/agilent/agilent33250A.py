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
from pymeasure.instruments.validators import strict_range
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
        "FREQ?", "FREQ %f",
        """ A floating point property that controls the frequency of the output
        waveform in Hz, from 1 uHz to 80 MHz, depending on the specified function.
        Can be set. """,
        validator=strict_range,
        values=[1e-6, 80e+6],
    )