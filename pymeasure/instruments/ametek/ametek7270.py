#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def check_read_not_empty(value):
    """Called by some properties to check if the reply is not an empty string
    that would mean the properties is currently invalid (probably because the reference mode
    is on single or dual)"""
    if value == '':
        raise ValueError('Invalid response from measurement call, '
                         'probably because the reference mode is set on single or dual')
    else:
        return value


class Ametek7270(SCPIUnknownMixin, Instrument):
    """This is the class for the Ametek DSP 7270 lockin amplifier

    In this instrument, some measurements are defined only for specific modes,
    called Reference modes, see :meth:`set_reference_mode` and will raise errors
    if called incorrectly
    """

    SENSITIVITIES = [
        0.0, 2.0e-9, 5.0e-9, 10.0e-9, 20.0e-9, 50.0e-9, 100.0e-9,
        200.0e-9, 500.0e-9, 1.0e-6, 2.0e-6, 5.0e-6, 10.0e-6,
        20.0e-6, 50.0e-6, 100.0e-6, 200.0e-6, 500.0e-6, 1.0e-3,
        2.0e-3, 5.0e-3, 10.0e-3, 20.0e-3, 50.0e-3, 100.0e-3,
        200.0e-3, 500.0e-3, 1.0
    ]

    SENSITIVITIES_IMODE = {0: SENSITIVITIES,
                           1: [sen * 1e-6 for sen in SENSITIVITIES],
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
        """Control the sensitivity range in Volts (float truncated to values from 2 nV to 1 V).""",
        validator=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True,
        check_set_errors=True,
        dynamic=True,
    )

    slope = Instrument.control(
        "SLOPE", "SLOPE %d",
        """Control the filter slope in dB/octave (integer truncated to values 6, 12, 18, 24).""",
        validator=truncated_discrete_set,
        values=[6, 12, 18, 24],
        map_values=True,
        check_set_errors=True,
    )

    time_constant = Instrument.control(  # NOTE: only for NOISEMODE = 0
        "TC", "TC %d",
        """Control the time constant in seconds
        (float truncated to values from 10 microseconds to 100,000 seconds).""",
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True,
        check_set_errors=True,
    )

    x = Instrument.measurement(
        "X.",
        """Get X value in Volts (float).""",
        get_process=check_read_not_empty,
    )

    y = Instrument.measurement(
        "Y.",
        """Get Y value in Volts (float).""",
        get_process=check_read_not_empty,
    )

    x1 = Instrument.measurement(
        "X1.",
        """Get first harmonic X value in Volts (float).""",
        get_process=check_read_not_empty,
    )

    y1 = Instrument.measurement(
        "Y1.",
        """Get first harmonic Y value in Volts (float).""",
        get_process=check_read_not_empty,
    )

    x2 = Instrument.measurement(
        "X2.",
        """Get second harmonic X value in Volts (float).""",
        get_process=check_read_not_empty,
    )

    y2 = Instrument.measurement(
        "Y2.",
        """Get second harmonic Y value in Volts (float).""",
        get_process=check_read_not_empty,
    )

    xy = Instrument.measurement(
        "XY.",
        """Get both X and Y values in Volts (float, tuple).""",
        get_process=check_read_not_empty,
    )

    mag = Instrument.measurement(
        "MAG.",
        """Get magnitude in Volts (float).""",
        get_process=check_read_not_empty,
    )

    theta = Instrument.measurement(
        "PHA.",
        """Get signal phase in degrees (float).""",
        get_process=check_read_not_empty,
    )

    harmonic = Instrument.control(
        "REFN", "REFN %d",
        """Control the reference harmonic mode (integer truncated to values from 1 to 127).""",
        validator=truncated_discrete_set,
        values=list(range(1, 128)),
        check_set_errors=True,
    )

    phase = Instrument.control(
        "REFP.", "REFP. %g",
        """Control the reference harmonic phase in degrees
        (float, modular_range, values from 0 to 360).""",
        validator=modular_range,
        values=[0, 360],
        check_set_errors=True,
    )

    voltage = Instrument.control(
        "OA.", "OA. %g",
        """Control the voltage in Volts (float, truncated_range, values from 0 to 5).""",
        validator=truncated_range,
        values=[0, 5],
        check_set_errors=True,
    )

    frequency = Instrument.control(
        "OF.", "OF. %g",
        """Control the lock-in frequency in Hz (float, truncated_range, values from 0 to 2.5e5).""",
        validator=truncated_range,
        values=[0, 2.5e5],
        check_set_errors=True,
    )

    dac1 = Instrument.control(
        "DAC. 1", "DAC. 1 %g",
        """Control the output value on DAC1 in Volts (float truncated to values from -10 to 10).""",
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True,
    )

    dac2 = Instrument.control(
        "DAC. 2", "DAC. 2 %g",
        """Control the output value on DAC2 in Volts (float truncated to values from -10 to 10).""",
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True,
    )

    dac3 = Instrument.control(
        "DAC. 3", "DAC. 3 %g",
        """Control the output value on DAC3 in Volts (float truncated to values from -10 to 10).""",
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True,
    )

    dac4 = Instrument.control(
        "DAC. 4", "DAC. 4 %g",
        """Control the output value on DAC4 in Volts (float truncated to values from -10 to 10).""",
        validator=truncated_range,
        values=[-10, 10],
        check_set_errors=True,
    )

    adc1 = Instrument.measurement(
        "ADC. 1",
        """Get the input value of ADC1 in Volts (float).""",
        get_process=check_read_not_empty,
    )

    adc2 = Instrument.measurement(
        "ADC. 2",
        """Get the input value of ADC2 in Volts (float).""",
        get_process=check_read_not_empty,
    )

    adc3 = Instrument.measurement(
        "ADC. 3",
        """Get the input value of ADC3 in Volts (float).""",
        get_process=check_read_not_empty,
    )

    adc4 = Instrument.measurement(
        "ADC. 4",
        """Get the input value of ADC4 in Volts (float).""",
        get_process=check_read_not_empty,
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
            **kwargs)

    def check_set_errors(self):
        """mandatory to be used for property setter

        The Ametek protocol expect the default null character to be read to check the property
        has been correctly set. With default termination character set as Null character,
        this turns out as an empty string to be read.
        """
        if self.read() == '':
            return []
        else:
            return ['Incorrect return from previously set property']

    def ask(self, command, query_delay=None):
        """Send a command and read the response, stripping white spaces.

        Usually the properties use the
        :meth:`~pymeasure.instruments.common_base.CommonBase.values`
        method that adds a strip call, however several methods use directly the result from ask to
        be cast into some other types. It should therefore also add the strip here, as all responses
        end with a newline character.
        """
        return super().ask(command, query_delay).strip()

    def set_reference_mode(self, mode: int = 0):
        """Set the instrument in Single, Dual or harmonic mode.

        :param mode: the integer specifying the mode: 0 for Single, 1 for Dual harmonic, and 2 for
            Dual reference.

        """
        if mode not in [0, 1, 2]:
            raise ValueError('Invalid reference mode')
        self.ask(f'REFMODE {mode}')

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

    @property
    def id(self):
        """Get the instrument ID and firmware version"""
        return f"{self.ask('ID')}/{self.ask('VER')}"

    @property
    def auto_gain(self):
        """Control whether automatic gain is enabled (bool)."""
        return int(self.ask("AUTOMATIC")) == 1

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
