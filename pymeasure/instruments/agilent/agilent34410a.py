#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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

class Agilent34410A(Instrument):
    """
    Represent the multimiters HP/Agilent/Keysight 34410A, and related
    Implemented measuremets:
        voltage_dc, voltage_ac, current_dc, current_ac, resistance, resistance_4w
    """
    #only the most simple functions are implemented
    voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage")
    
    voltage_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF", "AC voltage")
    
    current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC voltage")
    
    current_ac = Instrument.measurement("MEAS:CURR:AC? DEF,DEF", "AC voltage")
    
    resistance = Instrument.measurement("MEAS:RES? DEF,DEF", "AC voltage")
    
    resistance_4w = Instrument.measurement("MEAS:FRES? DEF,DEF", "AC voltage")
    
    def __init__(self, adapter, delay=0.02, **kwargs):
        super(Agilent34410A, self).__init__(
            adapter, "HP/Agilent/Keysight 34410A Multimiter", **kwargs
        )
