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
from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import strict_range, strict_discrete_set
from math import sqrt,log10

class Channel(object):

        SOURCE_VALUES= [1,2]
        FREQ_LIMIT=[1e-6,150e6] #Frequeny limit for sinusoidal function


        amplitude=Instrument.control(
            "voltage:amplitude?","voltage:amplitude %e"
            """ A floating point property that read the output power
            in Vpp, Vrms or dBm for ch1."""
        )

        offset=Instrument.control(
            "source1:voltage:offset?","source1:voltage:offset %e",
            """ A floating point property that represents the output power
            in V for ch1. This property can be set."""
        )

        frequency=Instrument.control(
            "source1:frequency:fixed?","source1:frequency:fixed %e",
            """ A floating point property that represents the frequency of ch1.
            This property can be set.""",
            validator=strict_range,
            values=FREQ_LIMIT
        )

        def __init__(self, instrument, number):
            self.instrument=instrument
            if number in self.SOURCE_VALUES:
                self.number=number
            else:
                raise ValueError("%d: invalid input source provided" %number)

        def write(self, command):
            self.instrument.write("source%d:%s" %(self.number, command))

        def ask(self, command):
            self.instrument.ask("source%d:%s" %(self.number, command))

        """def read(self, command):
            self.instrument.read("source%d:%s?" %(self.number,command))"""
        def enable(self):
            self.instrument.write("output%d:state on" %self.number)

        def disable(self):
            self.instrument.write("output%d:state off" %self.number)

class AFG3152C(Instrument):
    """Represents the Tektronix AFG 3000 series arbitrary function generator
    and provides a high-level for interacting with the instrument
    .. code-block:: python

        afg = AFG3152C("GPIB::1")

        afg.unint_ch1='VPP'            # Sets units for CH1
        afg.amplitude_ch1 = 1          # Sets the CH1 level to 1 VPP
        afg.frequency_ch1=1e3          # Sets the CH1 frequency to 1KHz
        afg.enable(1)                  # Enables the output from CH1

    """

    def __init__(self, adapter, **kwargs):
        super(AFG3152C, self).__init__(
            adapter,
            "Tektronix AFG3152C arbitrary function generator",
            **kwargs
        )

    self.ch1=Channel(self,1)
    self.ch2=Channel(self,2)
