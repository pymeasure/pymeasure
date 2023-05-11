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
import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Instrument(Instrument):

    def check_errors(self):
        if self.read() == '':
            return []
        else:
            return ['Incorrect return from previously set property']

    def ask(self, command, query_delay=0):
        return super().ask(command, query_delay).strip()


class Ametek7270(Instrument):
    """This is the class for the Ametek DSP 7270 lockin amplifier"""

    SENSITIVITIES = [
        0.0, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
        200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
        20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
        2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0
    ]

    SENSITIVITIES_IMODE = {0: SENSITIVITIES,
                           1: list(np.array(SENSITIVITIES) * 1e-6),
                           2: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2e-15, 5e-15, 10e-15,
                               20e-15, 50e-15, 100e-15, 200e-15, 500e-15, 1e-12, 2e-12]}

    TIME_CONSTANTS = [
        10.0e-6, 20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6,
        1.0e-3, 2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0,
        100.0, 200.0, 500.0, 1.0e3, 2.0e3, 5.0e3, 10.0e3,
        20.0e3, 50.0e3, 100.0e3
    ]

    sensitivity = Instrument.control(  # NOTE: only for IMODE = 1.
        "SEN", "SEN %d",
        """ A floating point property that controls the sensitivity
        range in Volts, which can take discrete values from 2 nV to
        1 V. This property can be set. """,
        validator=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True,
        check_set_errors=True,
        dynamic=True,

    )

    slope = Instrument.control(
        "SLOPE", "SLOPE %d",
        """ A integer property that controls the filter slope in
        dB/octave, which can take the values 6, 12, 18, or 24 dB/octave.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=[6, 12, 18, 24],
        map_values=True,
        check_set_errors=True
    )
    time_constant = Instrument.control(  # NOTE: only for NOISEMODE = 0
        "TC", "TC %d",
        """ A floating point property that controls the time constant
        in seconds, which takes values from 10 microseconds to 100,000
        seconds. This property can be set. """,
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True,
        check_set_errors=True
    )

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

    theta = Instrument.measurement("PHA.",
                                   """ Reads the signal phase in degrees """
                                   )

    harmonic = Instrument.control(
        "REFN", "REFN %d",
        """ An integer property that represents the reference
        harmonic mode control, taking values from 1 to 127.
        This property can be set. """,
        validator=truncated_discrete_set,
        values=list(range(1, 128)),
        check_set_errors=True
    )
    phase = Instrument.control(
        "REFP.", "REFP. %g",
        """ A floating point property that represents the reference
        harmonic phase in degrees. This property can be set. """,
        validator=modular_range,
        values=[0, 360],
        check_set_errors=True
    )
    voltage = Instrument.control(
        "OA.", "OA. %g",
        """ A floating point property that represents the voltage
        in Volts. This property can be set. """,
        validator=truncated_range,
        values=[0, 5],
        check_set_errors=True
    )
    frequency = Instrument.control(
        "OF.", "OF. %g",
        """ A floating point property that represents the lock-in
        frequency in Hz. This property can be set. """,
        validator=truncated_range,
        values=[0, 2.5e5],
        check_set_errors=True
    )
    dac1 = Instrument.control(
        "DAC. 1", "DAC. 1 %g",
        """ A floating point property that represents the output
        value on DAC1 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True
    )
    dac2 = Instrument.control(
        "DAC. 2", "DAC. 2 %g",
        """ A floating point property that represents the output
        value on DAC2 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True
    )
    dac3 = Instrument.control(
        "DAC. 3", "DAC. 3 %g",
        """ A floating point property that represents the output
        value on DAC3 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True
    )
    dac4 = Instrument.control(
        "DAC. 4", "DAC. 4 %g",
        """ A floating point property that represents the output
        value on DAC4 in Volts. This property can be set. """,
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True
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
                                """ Reads the instrument identification """,
                                cast=str
                                )

    def __init__(self, adapter, name="Ametek DSP 7270",
                 read_termination='\x00',
                 write_termination='\x00',
                 **kwargs):

        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            write_termination=write_termination,
            **kwargs
        )

    def set_voltage_mode(self):
        """ Sets instrument to voltage control mode """
        self.ask("IMODE 0")
        self.sensitivity_values = self.SENSITIVITIES_IMODE[0]

    def set_differential_mode(self, lineFiltering=True):
        """ Sets instrument to differential mode -- assuming it is in voltage mode """
        self.ask("VMODE 3")
        self.ask("LF %d 0" % 3 if lineFiltering else 0)

    def set_current_mode(self, low_noise=False):
        """ Sets instrument to current control mode with either low noise or high bandwidth"""
        if low_noise:
            self.ask("IMODE 2")
            self.sensitivity_values = self.SENSITIVITIES_IMODE[2]
        else:
            self.ask("IMODE 1")
            self.sensitivity_values = self.SENSITIVITIES_IMODE[1]

    def set_channel_A_mode(self):
        """ Sets instrument to channel A mode -- assuming it is in voltage mode """
        self.ask("VMODE 1")

    def identification(self):
        """Get the instrument ID and firmware version"""
        return f"{self.id}/{self.ask('VER')}"

    @property
    def auto_gain(self):
        return (int(self.ask("AUTOMATIC")) == 1)

    @auto_gain.setter
    def auto_gain(self, setval):
        if setval:
            self.ask("AUTOMATIC 1")
        else:
            self.ask("AUTOMATIC 0")

    def shutdown(self):
        """ Ensures the instrument in a safe state """
        log.info("Shutting down %s" % self.name)
        self.voltage = 0.
        super().shutdown()
