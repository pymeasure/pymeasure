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

class Keithley179A(Instrument):
    """ 
    Represent the Keithley 179A DMM
    Read value Keithley 179A
    no units, the Keithley 179A can not cange any mode or range,
    only manuel set on DMM
        
    Read value Keithley 179A no units
    Unit has no own SCPI commandos. 
    """  
    
    
    #fake IDN, Datron1071, no internal 'IDN' command
    #program check @ Datron FW from 1981
    id = "Keithley179A" 
    
    
    readval = Instrument.measurement("RDX",
    """ 
    Read value Keithley 179A no units
    """  
    )

   

    def __init__(self, resourceName,includeSCPI=False, **kwargs):
        super().__init__(
            resourceName,
            "Keithley 179A",
            **kwargs
        )


