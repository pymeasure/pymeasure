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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set
from pymeasure.instruments.berkeleynucleonics.bn675 import BN675_AWG
from time import time, sleep
import numpy as np
from pyvisa.errors import VisaIOError



class BN685_AWG(BN675_AWG):
    """Represents the Berkeley nucleonics 685 high performance arbitrary waveform generator. WIP
    This AWG can switch between an AWG and an AFG. This driver is for the AWG. There
    is a SCPI command to switch between them but it is not implemented here.
    Each channel has its own sequencer, but to maintain synchronicity, the length of each
    channels' sequence must be the same. Because this is 2021, the AWG helpfully maintains
    a set of strategies to fix length mismatches from which you may choose. As such, the way
    AWG's are specified is "SEQ:ELEM[n]:WAV[m] wfname" where n is the n'th part in the sequence table and
    m is the channel to put the waveform with wfname.

    """

    sampling_frequency = Instrument.control(
        "AWGC:SRAT?", "AWGC:SRAT %e",
        """ A floating point property that controls AWG sampling frequency.
        This property can be set.""",
        validator=strict_range,
        values=[10e6, 6.16e9]
    )



    def __init__(self, adapter, **kwargs):
        super(BN685_AWG, self).__init__(
            adapter,
            **kwargs
        )
        self.default_dir = 'C:\\Users\\AWG5000\\Pictures\\Saved Pictures\\'

