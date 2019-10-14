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

class Channel(object):
        SHAPES={
            'sinusoidal':'SIN',
            'square':'SQU',
            'pulse':'PULS',
            'ramp':'RAMP',
            'prnoise':'PRN',
            'dc':'DC',
            'sinc':'SINC',
            'gaussian':'GAUS',
            'lorentz':'LOR',
            'erise':'ERIS',
            'edecay':'EDEC',
            'haversine':'HAV'
        }
        FREQ_LIMIT=[1e-6,150e6] #Frequeny limit for sinusoidal function

        shape=Instrument.control(
            "function:shape?","function:shape %s",
            """ A string property that controls the shape of the output.
            This property can be set.""",
            validator=strict_discrete_set,
            values=SHAPES,
            map_values=True
        )

        amplitude=Instrument.control(
            "voltage:amplitude?","voltage:amplitude %e",
            """ A floating point property tha t read the output power
            in Vpp, Vrms or dBm. This property can be set."""
        )

        offset=Instrument.control(
            "voltage:offset?","voltage:offset %e",
            """ A floating point property that represents the output power
            in V. This property can be set."""
        )

        frequency=Instrument.control(
            "frequency:fixed?","frequency:fixed %e",
            """ A floating point property that represents the frequency.
            This property can be set.""",
            validator=strict_range,
            values=FREQ_LIMIT
        )
        duty=Instrument.control(
            "pulse:dcycle?","pulse:dcycle %d",
            """ A floating point property that represents the duty cycle of pulse.
            This property can be set.""",
            validator=strict_range,
            values=[0.001,99.999]
        )

        def __init__(self, instrument, number):
            self.instrument=instrument
            self.number=number

        def write(self, command):
            self.instrument.write("source%d:%s" %(self.number, command))

        def ask(self, command):
            self.instrument.ask("source%d:%s" %(self.number, command))

        def read(self):
            self.instrument.read()

        def enable(self):
            self.instrument.write("output%d:state on" %self.number)

        def disable(self):
            self.instrument.write("output%d:state off" %self.number)

        def waveform(self,shape='SIN',frequency=1e6,units='VPP',amplitude=1,offset=0):
            """General setting method for a complete wavefunction"""
            self.instrument.write("source%d:function:shape %s" %(self.number,shape))
            self.instrument.write("source%d:frequency:fixed %e" %(self.number,frequency))
            self.instrument.write("source%d:voltage:unit %s" %(self.number,units))
            self.instrument.write("source%d:voltage:amplitude %e%s" %(self.number,amplitude,units))
            self.instrument.write("source%d:voltage:offset %eV" %(self.number,offset))

        def values(self, command, **kwargs):
            """ Reads a set of values from the instrument through the adapter,
            passing on any key-word arguments.
            """
            return self.instrument.values("source%d:%s" %(self.number, command), **kwargs)

class AFG3152C(Instrument):
    """Represents the Tektronix AFG 3000 series arbitrary function generator
    and provides a high-level for interacting with the instrument
    .. code-block:: python

        afg = AFG3152C("GPIB::1")
        afg.ch1.shapes='sin'
        afg.ch1.amplitude=1            # Sets the CH1 level to 1 VPP
        afg.ch1.frequency=1e3          # Sets the CH1 frequency to 1KHz
        afg.ch1.enable                  # Enables the output from CH1

    """

    def __init__(self, adapter, **kwargs):
        super(AFG3152C, self).__init__(
            adapter,
            "Tektronix AFG3152C arbitrary function generator",
            **kwargs
        )
        self.ch1=Channel(self,1)
        self.ch2=Channel(self,2)
