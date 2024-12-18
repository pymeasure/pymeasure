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
from pymeasure.instruments.validators import strict_range, strict_discrete_set, truncated_range


class BK894(Instrument):
    """ Represents the BK Precision 894 LCR Meter for interacting with
    the instrument. """



    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "BK Precision 894 LCR Meter", **kwargs
        )

    frequency = Instrument.control(":FREQuency?", ":FREQuency %g",
                                   "AC frequency (range depending on model), in Hertz",
                                   validator=strict_range,
                                   values=[20, 5e5])


    ac_voltage = Instrument.control(":VOLTage?", ":VOLTage %g",
                                    "AC voltage measurement level, in Volts",
                                    validator=strict_range,
                                    values=[5e-3, 2])

    ac_current = Instrument.control(":CURRent?", ":CURRent %g",
                                    "AC current measurement level, in Amps",
                                    validator=strict_range,
                                    values=[5e-5, 6.67e-3])

    ac_amplitude_alc = Instrument.control(":AMPLitude:ALC?", ":AMPLitude:ALC %d",
                                    "AC current measurement level, in Amps",
                                    validator=strict_discrete_set,
                                    values=[0, 1])

    dc_bias_state = Instrument.control(":BIAS:STATe?", ":BIAS:STATe %s",
                                    "DC Bias State in T/F",
                                    validator=strict_range,
                                    values=["ON", "OFF"])
    
    dc_bias_volt = Instrument.control(":BIAS:VOLTage?", ":BIAS:VOLTage %g",
                                    "DC Bias Voltage in V",
                                    validator=strict_range,
                                    values=[-5, 5])

    dc_bias_curr = Instrument.control(":BIAS:CURRent?", ":BIAS:CURRent %g",
                                    "DC Bias Current in Amps",
                                    validator=strict_range,
                                    values=[-5e-2, 5e-2])


    measurement_mode = Instrument.control(":FUNCTion:IMPedance?", ":FUNCTion:IMPedance %s",
                                    "Sets the Impedance Mode of the Instrument",
                                    validator=strict_discrete_set,
                                    values=["CPD","CPQ", "CPG", "CPRP",  "CSD", "CSQ", "CSRS" ,
                                            "LPQ", "LPD", "LPG", "LPRP",  "LSD", "LSQ", "LSRS",  "RX", "ZTD", 
                                            "ZTR", "GB", "YTD", "YTR" ])

    impedance_range = Instrument.control(":FUNCTion:IMPedance:RANGe?", ":FUNCTion:IMPedance:RANGe %d",
                                    "Impedance Range in Ohms",
                                    validator=strict_discrete_set,
                                    values=[10, 30, 100, 300,1000,3000,10000,30000, 100000])
    def display_measure(self):
        self.write('DISP:PAGE MEAS')

    def display_list(self):
        self.write('DISP:PAGE LIST')

    def clear(self):
        self.write('*CLS')

    def reset(self):
        self.write('*RST')
    
    impedance_range_auto = Instrument.control(":FUNCTion:IMPedance:RANGe?", ":FUNCTion:IMPedance:RANGe:AUTO %d",
                                    "Impedance Auto Ranging?",
                                    validator=strict_discrete_set,
                                    values=[0,1])

   
    list_mode = Instrument.control(":LIST:MODE?", ":LIST:MODE %s",
                                    "List Mode?",
                                    validator=strict_discrete_set,
                                    values=["SEQuence","STEPped"])

    def list_frequencies(self, freqs):
        formatted = ""
        for f in freqs:
            if f > 5e5 or f < 20:
                raise ValueError(f'frequencies must be 20 Hz < v < 500 kHz, got {f}')
            formatted += format(f, '.1e') + ', '
        self.write(f':LIST:FREQuency {formatted} ')

    def list_voltage(self, voltages):
        formatted = ""
        for v in voltages:
            if v > 2 or v < 0.005:
                raise ValueError(f'AC voltages must be 0.005 < v < 2, got {v}')
            formatted += format(v, '.1e') + ', '
        self.write(f':LIST:VOLTage {formatted} ')

    def list_bias_voltage(self, bias_voltages):
        formatted = ""
        for v in bias_voltages:
            if v > 5 or v < -5:
                raise ValueError(f'bias voltages must be -5 < v < 5, got {v}')
            formatted += format(v, '.1e') + ', '
        self.display_measure()
        self.write(f':LIST:BIAS:VOLTage {formatted} ')
    
    def aperture(self, averages, speed = "MED"):
        self.write(f':APERture {speed}, {averages} ')
        
    def trigger(self):
        self.write("TRIGger")

    def get_latest_measurement(self):
        return self.ask('FETch?')

    trigger_source = Instrument.control(":TRIGger:SOURce?", ":TRIGger:SOURce %s",
                                    "Aperture/Averaging speed",
                                    validator=strict_discrete_set,
                                    values=["INTernal","EXTernal", "BUS", "HOLD"])
