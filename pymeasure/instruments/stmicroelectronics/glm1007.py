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
from pymeasure.adapters import VISAAdapter

class GLM1007(Instrument):
    """ Represents the RF switch for automatic measurement with 7 inputs
    """

    connect = Instrument.control("ROUTE:CONNECT?", "ROUTE:CONNECT %s",
                                 """ A `string` property to set the RF switch connection.
                                 The connection is expressed as a pair of letters, e.g. "AB".
                                 This property can be read.
                                 """,
                                 )
    
    disconnect = Instrument.setting("ROUTE:DISCONNECT %s",
                                    """ A `string` property to disable the RF switch connection.
                                    The connection is expressed as a pair of letters, e.g. "AB".
                                    """,
                                    )
    
    disconnect_all = Instrument.setting("ROUTE:OPEN:ALL",
                                        """ A `string` property to disable all the RF switch connection.
                                        """,
                                    )
    
    att_table_start_frequency = Instrument.measurement("ROUTE:ATTenuation:FREQuency:START?",
                                                       """ Read the start frequency for the attenuation table.
                                                       The unit is Hz.""",
                                                       )

    att_table_step_frequency = Instrument.measurement("ROUTE:ATTenuation:FREQuency:STEP?",
                                                       """ Read the step frequency for the attenuation table.
                                                       The unit is Hz.""",
                                                       )

    att_table_points = Instrument.measurement("ROUTE:ATTenuation:FREQuency:POINts?",
                                              """ Read the number of points frequency for the attenuation table.""",
                                              )
    
    def attenuation_table(self, path):
        tables = self.values("ROUTE:ATTenuation? {}".format(path))
        return [a/100 for a in tables]
        
    def attenuation(self, path, frequency):
        f1,a1,f2,a2 = self.values("ROUTE:ATTenuation? {},{}".format(path,frequency))
        weight = (frequency-f1)/(f2-f1)
        return (a1+weight*(a2-a1))/100
        
    def __init__(self, resource_name, **kwargs):
        super().__init__(
            resource_name,
            "GLM 1007",
#            write_termination = "\r\n",
            **kwargs
        )

        if isinstance(self.adapter, VISAAdapter):
            self.adapter.connection.baud_rate = 115200
