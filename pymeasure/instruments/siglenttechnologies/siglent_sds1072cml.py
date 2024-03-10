#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_range,truncated_discrete_set,strict_range

class VoltageChannel(Channel):

    """ Implementation of a SIGLENT SDS1072CML Oscilloscope channel

    """

class SDS1072CML(Instrument):
    """ Represents the SIGLENT SDS1072CML Oscilloscope
    and provides a high-level for interacting with the instrument
    """
    def __init__(self, adapter, name="Siglent SDS1072CML Oscilloscope", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ch1 = Channel(self,1)
        self.ch2 = Channel(self,2)
    timeDiv=Instrument.control(
        ":TDIV?",":TDIV %s",
        "Sets the time division to the closest possible value,rounding downwards.",
        validator=truncated_discrete_set,
        values={5e-9:"5NS",
                1e-8:"1.00E-08S",2.5e-8:"2.50E-08S",5e-8:"5.00E-08S",
                1e-7:"1.00E-07S",2.5e-7:"2.50E-07S",5e-7:"5.00E-07S",
                1e-6:"1.00E-06S",2.5e-6:"2.50E-06S",5e-6:"5.00E-06S",
                1e-5:"1.00E-05S",2.5e-5:"2.50E-05S",5e-5:"5.00E-05S",
                1e-4:"1.00E-04S",2.5e-4:"2.50E-04S",5e-4:"5.00E-04S",
                1e-3:"1.00E-03S",2.5e-3:"2.50E-03S",5e-3:"5.00E-03S",
                1e-2:"1.00E-02S",2.5e-2:"2.50E-02S",5e-2:"5.00E-02S",
                1e-1:"1.00E-01S",2.5e-1:"2.50E-01S",5e-1:"5.00E-01S",
                1e0:"1.00E+00S",2.5e0:"2.50E+00S",5e0:"5.00E+00S",
                1e1:"1.00E+01S",2.5e1:"2.50E+01S",5e0:"5.00E+01S",
                },
                map_values=True,
                get_process=lambda v: v.split(" ",1)[-1]
    )
    status=Instrument.control(
        "SAST?",None,
        "Queries the sampling status of the scope (Stop, Ready, Trig'd, Armed)",
        get_process= lambda v : v.split(" ",1)[-1]
    )
    internalState=Instrument.control(
        "INR?",None,
        "Gets the scope's Internal state change register and clears it.",
        get_process= lambda v : v.split(" ",1)[-1]
    )

#        SOURCE_VALUES = ['CH1', 'CH2', 'MATH']
#
#        TYPE_VALUES = [
#            'FREQ', 'MEAN', 'PERI', 'PHA', 'PK2', 'CRM',
#            'MINI', 'MAXI', 'RIS', 'FALL', 'PWI', 'NWI'
#        ]
#
#        UNIT_VALUES = ['V', 's', 'Hz']
#
#        def __init__(self, parent, preamble="MEASU:IMM:"):
#            self.parent = parent
#            self.preamble = preamble
#
#        @property
#        def value(self):
#            return self.parent.values("%sVAL?" % self.preamble)
#
#        @property
#        def source(self):
#            return self.parent.ask("%sSOU?" % self.preamble).strip()
#
#        @source.setter
#        def source(self, value):
#            if value in TDS2000.Measurement.SOURCE_VALUES:
#                self.parent.write(f"{self.preamble}SOU {value}")
#            else:
#                raise ValueError("Invalid source ('{}') provided to {}".format(
#                    self.parent, value))
#
#        @property
#        def type(self):
#            return self.parent.ask("%sTYP?" % self.preamble).strip()
#
#        @type.setter
#        def type(self, value):
#            if value in TDS2000.Measurement.TYPE_VALUES:
#                self.parent.write(f"{self.preamble}TYP {value}")
#            else:
#                raise ValueError("Invalid type ('{}') provided to {}".format(
#                    self.parent, value))
#
#        @property
#        def unit(self):
#            return self.parent.ask("%sUNI?" % self.preamble).strip()
#
#        @unit.setter
#        def unit(self, value):
#            if value in TDS2000.Measurement.UNIT_VALUES:
#                self.parent.write(f"{self.preamble}UNI {value}")
#            else:
#                raise ValueError("Invalid unit ('{}') provided to {}".format(
#                    self.parent, value))
#