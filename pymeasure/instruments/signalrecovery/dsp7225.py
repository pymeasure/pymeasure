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
import logging

# =============================================================================
# Logging
# =============================================================================

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# =============================================================================
# Instrument file
# =============================================================================


class DSP7225(DSPBase):
    """Represents the Signal Recovery DSP 7225 lock-in amplifier.

    Class inherits commands from the DSPBase parent class and utilizes dynamic
    properties for various properties.

    .. code-block:: python

        lockin7225 = DSP7225("GPIB0::12::INSTR")
        lockin7225.imode = "voltage mode"       # Set to measure voltages
        lockin7225.reference = "internal"       # Use internal oscillator
        lockin7225.fet = 1                      # Use FET pre-amp
        lockin7225.shield = 0                   # Ground shields
        lockin7225.coupling = 0                 # AC input coupling
        lockin7225.time_constant = 0.10         # Filter time set to 100 ms
        lockin7225.sensitivity = 2E-3           # Sensitivity set to 2 mV
        lockin7225.frequency = 100              # Set oscillator frequency to 100 Hz
        lockin7225.voltage = 1                  # Set oscillator amplitude to 1 V
        lockin7225.gain = 20                    # Set AC gain to 20 dB
        print(lockin7225.x)                     # Measure X channel voltage
        lockin7225.shutdown()                    # Instrument shutdown
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Dynamic values - Override base class validator values
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    frequency_values = [0.001, 1.2e5]
    harmonic_values = [1, 32]
    curve_buffer_bit_values = [1, 65535]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializer
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, adapter, name="Signal Recovery DSP 7225", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
