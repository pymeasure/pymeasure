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

from pymeasure.instruments import Instrument

class Agilent34970A(Instrument):
    """
    Represent the HP/Agilent/Keysight 34970A Data Acquisition /Switch Unit.

    Implemented measurements: resistance
    """
    #only the most simple functions are implemented

    
    def __init__(self, adapter, delay=0.02, **kwargs):
        super(Agilent34970A, self).__init__(
            adapter, "HP/Agilent/Keysight Agilent34970A Data Acquisition /Switch Unit", **kwargs
        )
    
    def set_resistance_2W(self, channel):
        cmd = f"RES:OCOM ON, (@{channel})"
        self.write(cmd)

    def meas_resistance(self, channel):
        cmd = f"MEAS:RES? (@{channel})"
        # print(cmd)
        res2W_str = self.ask(cmd)
        return float(res2W_str)


    def set_temperature_TC_K(self, channel):
        # configures channel 301 for a K-type thermocouple measurement
        cmd = "CONF:TEMP TC, K, (@%s)" % channel
        self.write(cmd)
        cmd = "UNIT:TEMPerature C, (@%s)" % channel
        self.write(cmd)
        # set a fixed reference junction temperature of internal
        cmd = "SENSe:TEMP:TRANS:TC:RJUN:TYPE INT,(@%s)" % channel
        self.write(cmd)
        

    def meas_temperature_TC_K(self, channel):
        cmd = "MEAS:TEMP? TC, J,(@%s)" % channel
        # print(cmd)
        temp_str = self.ask(cmd)
        return float(temp_str)

    def get_scan(self):
        cmd = "ROUT:SCAN?"
        print(cmd)
        ask_str = self.ask(cmd)
        return ask_str

    def set_scan(self, start_channel, end_channel):
        cmd = f"ROUT:SCAN (@{start_channel}:{end_channel})"
        print(cmd)
        self.write(cmd)
        
    def close(self):
        self.adapter.connection.close()
        
#    def __del__(self):
#        self.adapter.connection.close()
