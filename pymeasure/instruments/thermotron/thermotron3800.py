#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_discrete_set, strict_range

class Thermotron3800(Instrument):
    """ Represents the Thermotron 3800 Oven.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Thermotron 3800",
            **kwargs
        )

    id = Instrument.measurement(
        "IDEN?", """ Reads the instrument identification """
    )

    temperature = Instrument.measurement(
        "PVAR1?", """ Reads the current temperature of the oven 
        via built in thermocouple
        """
    )
    
    setpoint = Instrument.control(
        "SETP1?", "SETP1,%g",
        """ A loating point property that controls the setpoint 
        of the oven in Celsius. This property can be set. 
        """,
        validator=strict_range,
        values=[-55, 150]
    )

if __name__ == "__main__":
    thermotron = Thermotron3800("GPIB::1::INSTR")
    print(thermotron.id)
