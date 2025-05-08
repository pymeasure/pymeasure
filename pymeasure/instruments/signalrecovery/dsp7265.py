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

# =============================================================================
# Libraries / modules
# =============================================================================

from .dsp_base import DSPBase
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
import logging
from time import sleep

# =============================================================================
# Logging
# =============================================================================

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# =============================================================================
# Instrument file
# =============================================================================


class DSP7265(DSPBase):
    """Represents the Signal Recovery DSP 7265 lock-in amplifier.

    Class inherits commands from the DSPBase parent class and utilizes dynamic
    properties for various properties and includes additional functionality.

    .. code-block:: python

        lockin7265 = DSP7265("GPIB0::12::INSTR")
        lockin7265.imode = "voltage mode"       # Set to measure voltages
        lockin7265.reference = "internal"       # Use internal oscillator
        lockin7265.fet = 1                      # Use FET pre-amp
        lockin7265.shield = 0                   # Ground shields
        lockin7265.coupling = 0                 # AC input coupling
        lockin7265.time_constant = 0.10         # Filter time set to 100 ms
        lockin7265.sensitivity = 2E-3           # Sensitivity set to 2 mV
        lockin7265.frequency = 100              # Set oscillator frequency to 100 Hz
        lockin7265.voltage = 1                  # Set oscillator amplitude to 1 V
        lockin7265.gain = 20                    # Set AC gain to 20 dB
        print(lockin7265.x)                     # Measure X channel voltage
        lockin7265.shutdown()                   # Instrument shutdown

    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Dynamic values - Override base class validator values
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    frequency_values = [0.001, 2.5e5]
    harmonic_values = [1, 65535]
    curve_buffer_bit_values = [1, 2097151]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Constants
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    CURVE_BITS = ['x', 'y', 'magnitude', 'phase', 'sensitivity', 'adc1',
                  'adc2', 'adc3', 'dac1', 'dac2', 'noise', 'ratio', 'log ratio',
                  'event', 'frequency part 1', 'frequency part 2',
                  # Dual modes
                  'x2', 'y2', 'magnitude2', 'phase2', 'sensitivity2']

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializer
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, adapter, name="Signal Recovery DSP 7265", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Additional properties
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    dac3 = Instrument.control(
        "DAC. 3", "DAC. 3 %g",
        """Control the voltage of the DAC3 output on the rear panel.

        Valid values are floating point numbers between -12 to 12 V.
        """,
        validator=strict_range,
        values=[-12, 12]
    )

    dac4 = Instrument.control(
        "DAC. 4", "DAC. 4 %g",
        """Control the voltage of the DAC4 output on the rear panel.

        Valid values are floating point numbers between -12 to 12 V.
        """,
        validator=strict_range,
        values=[-12, 12]
    )

    @property
    def adc3(self):
        """Measure the ADC3 input voltage."""
        # 50,000 for 1V signal over 1 s
        integral = self.values("ADC 3")[0]
        return integral / (50000.0 * self.adc3_time)

    @property
    def adc3_time(self):
        """Control the ADC3 sample time in seconds."""
        # Returns time in seconds
        return self.values("ADC3TIME")[0] / 1000.0

    @adc3_time.setter
    def adc3_time(self, value):
        # Takes time in seconds
        self.write("ADC3TIME %g" % int(1000 * value))
        sleep(value * 1.2)
