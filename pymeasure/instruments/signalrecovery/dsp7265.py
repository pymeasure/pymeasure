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

from time import sleep
import numpy as np


class DSP7265(Instrument):
    """This is the class for the DSP 7265 lockin amplifier"""

    TIME_CONSTANTS = [
        10.0e-6, 20.0e-6, 40.0e-6, 80.0e-6, 160.0e-6, 320.0e-6,
        640.0e-6, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,
        100.0, 200.0, 500.0, 1.0e3, 2.0e3, 5.0e3, 10.0e3,
        20.0e3, 50.0e3
    ]

    SENSITIVITIES = [
        0.0, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
        200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
        20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
        2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0
    ]

    SLOPES = [6, 12, 18, 24]

    def __init__(self, resourceName, **kwargs):
        super(DSP7265, self).__init__(
            resourceName,
            "Signal Recovery DSP 7265",
            **kwargs
        )
        self.curve_bits = {
            'x': 1,
            'y': 2,
            'mag': 4,
            'phase': 8,
            'ADC1': 32,
            'ADC2': 64,
            'ADC3': 128
        }
        
        # Pre-condition
        self.adapter.config(datatype = 'str', converter = 's')
        
        # Simple parameter controls go here
        self.add_control("voltage",   "OA.",    "OA. %g")
        self.add_control("frequency", "OF.",    "OF. %g")
        self.add_control("dac1",      "DAC. 1", "DAC. 1 %g")
        self.add_control("dac2",      "DAC. 2", "DAC. 2 %g")
        self.add_control("dac3",      "DAC. 3", "DAC. 3 %g")
        self.add_control("dac4",      "DAC. 4", "DAC. 4 %g")
        self.add_control("harmonic",  "REFN",   "REFN %d")
        self.add_control("phase",     "REFP.",  "REFP. %g")

        # Simple measurements go here
        self.add_measurement("x", "X.")
        self.add_measurement("y", "Y.")
        self.add_measurement("xy", "X.Y.")
        self.add_measurement("mag", "Mag.")
        self.add_measurement("adc1", "ADC. 1")
        self.add_measurement("adc2", "ADC. 2")

        # Override the base method since the DSP is dumb about this one...
        self.add_measurement("id", "ID")

    def values(self, command):
        """ Rewrite the method because of extra character in return string."""
        result = self.ask(command).strip()
        result = result.replace('\x00','') # Remove extra unicode character
        try:
            return [float(x) for x in result.split(",")]
        except:
            return result
        
    def setDifferentialMode(self, lineFiltering=True):
        self.write("VMODE 3")
        self.write("LF %d 0" % 3 if lineFiltering else 0)

    def setChannelAMode(self):
        self.write("VMODE 1")

    @property
    def adc3(self):
        # 50,000 for 1V signal over 1 s
        integral = self.values("ADC 3")
        return float(integral)/(50000.0*self.adc3_time)

    @property
    def adc3_time(self):
        # Returns time in seconds
        return self.values("ADC3TIME")/1000.0

    @adc3_time.setter
    def adc3_time(self, value):
        # Takes time in seconds
        self.write("ADC3TIME %g" % int(1000*value))
        sleep(value*1.2)

    @property
    def time_constant(self):
        return self.values("TC.")

    @time_constant.setter
    def time_constant(self, value):
        ind = next(i for i, v in enumerate(self.TIME_CONSTANTS)
                   if v >= (value-1.0e-9))
        self.write("TC %d" % ind)

    @property
    def sensitivity(self):
        return self.values("SEN.")

    @sensitivity.setter
    def sensitivity(self, value):
        ind = next(i for i, v in enumerate(self.SENSITIVITIES)
                   if v >= (value-1.0e-9))
        self.write("SEN %d" % ind)

    @property
    def slope(self):
        return self.SLOPES[int(self.values("SLOPE"))]

    @slope.setter
    def slope(self, value):
        ind = next(i for i, v in enumerate(self.SLOPES) if v >= (value-1.0e-9))
        self.write("SLOPE %d" % ind)

    @property
    def auto_gain(self):
        return (int(self.values("AUTOMATIC")) == 1)

    @auto_gain.setter
    def auto_gain(self, value):
        if value:
            self.write("AUTOMATIC 1")
        else:
            self.write("AUTOMATIC 0")

    def auto_sensitivity(self):
        self.write("AS")

    def auto_phase(self):
        self.write("AQN")

    @property
    def gain(self):
        return self.values("ACGAIN")

    @gain.setter
    def gain(self, value):
        self.write("ACGAIN %d" % int(value/10.0))

    @property
    def reference(self):
        return "external" if int(self.ask("IE")) == 2 else "internal"

    @reference.setter
    def reference(self, value):
        if value == "internal":
            val = 0
        elif value == "external":
            val = 2
        else:
            raise Exception("Incorrect value for reference type."
                            " Must be either internal or extenal.")
        self.write("IE %d" % val)

    def set_buffer(self, points, quantities=['x'], interval=10.0e-3):
        num = 0
        for q in quantities:
            num += self.curve_bits[q]
        self.points = points
        self.write("CBD %d" % int(num))
        self.write("LEN %d" % int(points))
        # interval in increments of 5ms
        interval = int(float(interval)/5.0e-3)
        self.write("STR %d" % interval)
        self.write("NC")

    def start_buffer(self):
        self.write("TD")

    def get_buffer(self, quantity='x', timeout=1.00, average=False):
        count = 0
        maxCount = int(timeout/0.05)
        failed = False
        while int(self.values("M")) != 0:
            # Sleeping
            sleep(0.05)
            if count > maxCount:
                # Count reached max value, wait longer before asking!
                failed = True
                break
        if not failed:
            data = []
            # Getting data
            for i in range(self.length):
                val = self.values("DC. %d" % self.curve_bits[quantity])
                data.append(val)
            if average:
                return np.mean(data)
            else:
                return data
        else:
            return [0.0]
