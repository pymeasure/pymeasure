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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range, modular_range, modular_range_bidirectional, strict_discrete_set

from time import sleep
import numpy as np


class DSP7265(Instrument):
    """This is the class for the DSP 7265 lockin amplifier"""
    # TODO: add regultors on most of these

    SENSITIVITIES = [
            0.0, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
            200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
            20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
            2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
            200.0e-3, 500.0e-3, 1.0
        ]

    TIME_CONSTANTS = [
            10.0e-6, 20.0e-6, 40.0e-6, 80.0e-6, 160.0e-6, 320.0e-6,
            640.0e-6, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
            200.0e-3, 500.0e-3, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,
            100.0, 200.0, 500.0, 1.0e3, 2.0e3, 5.0e3, 10.0e3,
            20.0e3, 50.0e3
        ]
    REFERENCES = ['internal', 'external rear', 'external front']

    voltage = Instrument.control(
        "OA.", "OA. %g",
        """ A floating point property that represents the voltage
        in Volts. This property can be set. """,
        validator=truncated_range,
        values=[0,5]
    )
    frequency = Instrument.control(
        "OF.", "OF. %g",
        """ A floating point property that represents the lock-in
        frequency in Hz. This property can be set. """,
        validator=truncated_range,
        values=[0,2.5e5]
    )
    dac1 = Instrument.control(
        "DAC. 1", "DAC. 1 %g",
        """ A floating point property that represents the output
        value on DAC1 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12,12]
    )
    dac2 = Instrument.control(
        "DAC. 2", "DAC. 2 %g",
        """ A floating point property that represents the output
        value on DAC2 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12,12]
    )
    dac3 = Instrument.control(
        "DAC. 3", "DAC. 3 %g",
        """ A floating point property that represents the output
        value on DAC3 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12,12]
    )
    dac4 = Instrument.control(
        "DAC. 4", "DAC. 4 %g",
        """ A floating point property that represents the output
        value on DAC4 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-12,12]
    )
    harmonic = Instrument.control(
        "REFN", "REFN %d",
        """ An integer property that represents the reference
        harmonic mode control, taking values from 1 to 65535.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=list(range(65535))
    )
    phase = Instrument.control(
        "REFP.", "REFP. %g",
        """ A floating point property that represents the reference
        harmonic phase in degrees. This property can be set. """,
        validator=modular_range_bidirectional,
        values=[0,360]
    )
    x = Instrument.measurement("X.",
        """ Reads the X value in Volts """
    )
    y = Instrument.measurement("Y.",
        """ Reads the Y value in Volts """
    )
    xy = Instrument.measurement("X.Y.",
        """ Reads both the X and Y values in Volts """
    )
    mag = Instrument.measurement("MAG.",
        """ Reads the magnitude in Volts """
    )
    adc1 = Instrument.measurement("ADC. 1",
        """ Reads the input value of ADC1 in Volts """
    )
    adc2 = Instrument.measurement("ADC. 2",
        """ Reads the input value of ADC2 in Volts """
    )
    id = Instrument.measurement("ID",
        """ Reads the instrument identification """
    )
    reference = Instrument.control(
        "IE", "IE %d",
        """Controls the oscillator reference. Can be "internal",
        "external rear" or "external front" """,
        validator=strict_discrete_set,
        values=REFERENCES,
        map_values=True
    )
    sensitivity = Instrument.control(
        "SEN", "SEN %d",
        """ A floating point property that controls the sensitivity
        range in Volts, which can take discrete values from 2 nV to
        1 V. This property can be set. """,
        validator=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True
    )
    slope = Instrument.control(
        "SLOPE", "SLOPE %d",
        """ A integer property that controls the filter slope in
        dB/octave, which can take the values 6, 12, 18, or 24 dB/octave.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=[6, 12, 18, 24],
        map_values=True
    )
    time_constant = Instrument.control(
        "TC", "TC %d",
        """ A floating point property that controls the time constant
        in seconds, which takes values from 10 microseconds to 50,000
        seconds. This property can be set. """,
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True
    )

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

    def values(self, command):
        """ Rewrite the method because of extra character in return string."""
        result = self.ask(command).strip()
        result = result.replace('\x00','') # Remove extra unicode character
        try:
            return [float(x) for x in result.split(",")]
        except:
            return result


    def set_voltage_mode(self):
        self.write("IMODE 0")

    def setDifferentialMode(self, lineFiltering=True):
        """Sets lockin to differential mode, measuring A-B"""
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

    def shutdown(self):
        log.info("Shutting down %s." % self.name)
        self.voltage = 0.
        self.isShutdown = True
