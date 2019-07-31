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
    DELAY=0.2
    SOURCE_VALUES= [1,2]
    UNITS=['VPP','VRMS','DBM']
    AMPLITUDE_LIMIT={
        'VPP':[20e-3,10],
        'VRMS':list(map(lambda x: round(x/2/sqrt(2),3),[20e-3,10])),
        'DBM':list(map(lambda x: round(20*log10(x/2/sqrt(0.1)),2),[20e-3,10]))
    } #Vpp, Vrms and dBm limits
    FREQ_LIMIT=[1e-6,150e6] #Frequeny limit for sinusoidal function
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


    #######
    # CH1 #
    #######
    amplitude_ch1=Instrument.measurement(
        "source1:voltage:amplitude?",
        """ A floating point property that read the output power
        in Vpp, Vrms or dBm for ch1."""
    )

    unit_ch1=Instrument.control(
        "source1:voltage:unit?","source1:voltage:unit %s",
        """ A string property that represents the units of ch1.
        This property can be set.""",
        validator=strict_discrete_set,
        values=UNITS
    )

    offset_ch1=Instrument.control(
        "source1:voltage:offset?","source1:voltage:offset %e",
        """ A floating point property that represents the output power
        in V for ch1. This property can be set."""
    )

    frequency_ch1=Instrument.control(
        "source1:frequency:fixed?","source1:frequency:fixed %e",
        """ A floating point property that represents the frequency of ch1.
        This property can be set.""",
        validator=strict_range,
        values=FREQ_LIMIT
    )

    shape_ch1=Instrument.control(
        "source1:function:shape?","source1:function:shape %s",
        """ A string property that controls the shape of the CH1 output.
        This property can be set.""",
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True
    )

    #######
    # CH2 #
    #######

    amplitude_ch2=Instrument.measurement(
        "source2:voltage:amplitude?",
        """ A floating point property that read the output power
        in Vpp, Vrms or dBm for ch1."""
    )

    unit_ch2=Instrument.control(
        "source2:voltage:unit?","source2:voltage:unit %s",
        """ A string property that represents the units of ch1.
        This property can be set.""",
        validator=strict_discrete_set,
        values=UNITS
    )

    offset_ch2=Instrument.control(
        "source2:voltage:offset?","source2:voltage:offset %e",
        """ A floating point property that represents the output power
        in V for ch1. This property can be set."""
    )

    frequency_ch2=Instrument.control(
        "source2:frequency:fixed?","source2:frequency:fixed %e",
        """ A floating point property that represents the frequency of ch1.
        This property can be set.""",
        validator=strict_range,
        values=FREQ_LIMIT
    )

    shape_ch2=Instrument.control(
        "source2:function:shape?","source2:function:shape %s",
        """ A string property that controls the shape of the CH1 output.
        This property can be set.""",
        validator=strict_discrete_set,
        values=SHAPES,
        map_values=True
    )


    def __init__(self, resourceName, **kwargs):
        super(AFG3152C, self).__init__(
            resourceName,
            "Tektronix AFG3152C arbitrary function generator",
            **kwargs
        )

    def unit(self, source):
        source=strict_discrete_set(source,self.SOURCE_VALUES)
        return self.ask("source%s:voltage:unit?" %source)[:-1]

    def amplitude(self, source, value):
        source=strict_discrete_set(source,self.SOURCE_VALUES)
        value=strict_range(value,self.AMPLITUDE_LIMIT[self.unit(source)])
        self.write("source%s:voltage:amplitude %e" %(source,value))

    def enable(self,source):
        """Enable channel output"""
        if source in self.SOURCE_VALUES:
            self.write("output%s:state on" %source)
        else:
            raise ValueError("%s: invalid input source provided" %source)

    def disable(self,source):
        """Disable channel output"""
        if source in self.SOURCE_VALUES:
            self.write("output%s:state off" %source)
        else:
            raise ValueError("%s: invalid input source provided" %source)

    def waveform(self,source,shape='SIN',frequency=1e6,units='VPP',amplitude=1,offset=0):
        """General setting method for a complete wavefunction"""
        if source in self.SOURCE_VALUES:
            self.write("source%s:function:shape %s" %(source,shape))
            self.write("source%s:frequency:fixed %e" %(source,frequency))
            self.write("source%s:voltage:unit %s" %(source,units))
            self.write("source%s:voltage:amplitude %e%s" %(source,amplitude,units))
            self.write("source%s:voltage:offset %eV" %(source,offset))
        else:
            raise ValueError("%s: invalid input source provided" %source)
