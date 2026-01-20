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
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class APSIN12G(SCPIUnknownMixin, Instrument):
    """ Represents the Anapico APSIN12G Signal Generator with option 9K,
    HP and GPIB. """
    FREQ_LIMIT = [9e3, 12e9]
    POW_LIMIT = [-30, 27]

    def __init__(self, adapter, name="Anapico APSIN12G Signal Generator", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    power = Instrument.control(
        "SOUR:POW:LEV:IMM:AMPL?;", "SOUR:POW:LEV:IMM:AMPL %gdBm;",
        """Control the output power in dBm. (float)""",
        validator=strict_range,
        values=POW_LIMIT
    )
    frequency = Instrument.control(
        "SOUR:FREQ:CW?;", "SOUR:FREQ:CW %eHz;",
        """Control the output frequency in Hz. (float)""",
        validator=strict_range,
        values=FREQ_LIMIT
    )
    blanking = Instrument.control(
        ":OUTP:BLAN:STAT?", ":OUTP:BLAN:STAT %s",
        """Control the blanking of output power when frequency is changed. ON makes the output
        to be blanked (off) while changing frequency. """,
        validator=strict_discrete_set,
        values=['ON', 'OFF']
    )
    reference_output = Instrument.control(
        "SOUR:ROSC:OUTP:STAT?", "SOUR:ROSC:OUTP:STAT %s",
        """Control the 10MHz reference output from the synth. (str)""",
        validator=strict_discrete_set,
        values=['ON', 'OFF']
    )

    def enable_rf(self):
        """ Enables the RF output. """
        self.write("OUTP:STAT 1")

    def disable_rf(self):
        """ Disables the RF output. """
        self.write("OUTP:STAT 0")
