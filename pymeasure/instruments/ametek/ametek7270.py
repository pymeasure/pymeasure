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
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range

class Ametek7270(Instrument):
    """This is the class for the Ametek DSP 7270 lockin amplifier"""

    SENSITIVITIES = [
            0.0, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
            200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
            20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
            2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
            200.0e-3, 500.0e-3, 1.0
        ]

    TIME_CONSTANTS = [
            10.0e-6, 20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6,
            1.0e-3, 2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
            200.0e-3, 500.0e-3, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,
            100.0, 200.0, 500.0, 1.0e3, 2.0e3, 5.0e3, 10.0e3,
            20.0e3, 50.0e3, 100.0e3
        ]

    sensitivity = Instrument.control( # NOTE: only for IMODE = 1.
        "SEN.", "SEN %d",
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
    time_constant = Instrument.control( # NOTE: only for NOISEMODE = 0
        "TC.", "TC %d",
        """ A floating point property that controls the time constant
        in seconds, which takes values from 10 microseconds to 100,000
        seconds. This property can be set. """,
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True
    )
    # TODO: Figure out if this actually can send for X1. X2. Y1. Y2. or not.
    #       There's nothing in the manual about it but UtilMOKE sends these.
    x = Instrument.measurement("X.",
        """ Reads the X value in Volts """
    )
    y = Instrument.measurement("Y.",
        """ Reads the Y value in Volts """
    )
    x1 = Instrument.measurement("X1.",
        """ Reads the first harmonic X value in Volts """
    )
    y1 = Instrument.measurement("Y1.",
        """ Reads the first harmonic Y value in Volts """
    )
    x2 = Instrument.measurement("X2.",
        """ Reads the second harmonic X value in Volts """
    )
    y2 = Instrument.measurement("Y2.",
        """ Reads the second harmonic Y value in Volts """
    )
    xy = Instrument.measurement("XY.",
        """ Reads both the X and Y values in Volts """
    )
    mag = Instrument.measurement("MAG.",
        """ Reads the magnitude in Volts """
    )
    harmonic = Instrument.control(
        "REFN", "REFN %d",
        """ An integer property that represents the reference
        harmonic mode control, taking values from 1 to 127.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=list(range(1,128))
    )
    phase = Instrument.control(
        "REFP.", "REFP. %g",
        """ A floating point property that represents the reference
        harmonic phase in degrees. This property can be set. """,
        validator=modular_range,
        values=[0,360]
    )
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
        values=[-10,10]
    )
    dac2 = Instrument.control(
        "DAC. 2", "DAC. 2 %g",
        """ A floating point property that represents the output
        value on DAC2 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10,10]
    )
    dac3 = Instrument.control(
        "DAC. 3", "DAC. 3 %g",
        """ A floating point property that represents the output
        value on DAC3 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10,10]
    )
    dac4 = Instrument.control(
        "DAC. 4", "DAC. 4 %g",
        """ A floating point property that represents the output
        value on DAC4 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10,10]
    )
    adc1 = Instrument.measurement("ADC. 1",
        """ Reads the input value of ADC1 in Volts """
    )
    adc2 = Instrument.measurement("ADC. 2",
        """ Reads the input value of ADC2 in Volts """
    )
    adc3 = Instrument.measurement("ADC. 3",
        """ Reads the input value of ADC3 in Volts """
    )
    adc4 = Instrument.measurement("ADC. 4",
        """ Reads the input value of ADC4 in Volts """
    )
    id = Instrument.measurement("ID",
        """ Reads the instrument identification """
    )

    def __init__(self, resourceName, **kwargs):
        super(Ametek7270, self).__init__(
            resourceName,
            "Ametek DSP 7270",
            **kwargs
        )

    def set_voltage_mode(self):
        """ Sets instrument to voltage control mode """
        self.write("IMODE 0")

    def set_differential_mode(self, lineFiltering=True):
        """ Sets instrument to differential mode -- assuming it is in voltage mode """
        self.write("VMODE 3")
        self.write("LF %d 0" % 3 if lineFiltering else 0)

    def set_channel_A_mode(self):
        """ Sets instrument to channel A mode -- assuming it is in voltage mode """
        self.write("VMODE 1")

    @property
    def auto_gain(self):
        return (int(self.ask("AUTOMATIC")) == 1)

    @auto_gain.setter
    def auto_gain(self, setval):
        if setval:
            self.write("AUTOMATIC 1")
        else:
            self.write("AUTOMATIC 0")

    def shutdown(self):
        """ Ensures the instrument in a safe state """
        self.voltage = 0.
        self.isShutdown = True
        log.info("Shutting down %s" % self.name)
