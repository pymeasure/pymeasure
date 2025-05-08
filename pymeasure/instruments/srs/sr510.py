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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, truncated_discrete_set


class SR510(Instrument):
    TIME_CONSTANTS = {1e-3: 1, 3e-3: 2, 10e-3: 3, 30e-3: 4, 100e-3: 5,
                      300e-3: 6, 1: 7, 3: 8, 10: 9, 30: 10, 100: 11, }

    SENSITIVITIES = {10e-9: 1, 20e-9: 2, 50e-9: 3, 100e-9: 4, 200e-9: 5, 500e-9: 6,
                     1e-6: 7, 2e-6: 8, 5e-6: 9, 10e-6: 10, 20e-6: 11, 50e-6: 12, 100e-6: 13,
                     200e-6: 14, 500e-6: 15, 1e-3: 16, 2e-3: 17, 5e-3: 18, 10e-3: 19, 20e-3: 20,
                     50e-3: 21, 100e-3: 22, 200e-3: 23, 500e-3: 24, }

    phase = Instrument.control(
        "P", "P %g",
        """A float property that represents the SR510 reference to input
        phase offset in degrees. Queries return values between -180 and
        180 degrees. This property can be set with a range of values
        between -999 to 999 degrees. Set values are mapped internal in the
        lockin to -180 and 180 degrees.""",
        validator=truncated_range,
        values=[-999, 999],
    )

    time_constant = Instrument.control(
        "T1", "T1,%d",
        """A float property that represents the SR510 PRE filter time constant.
        This property can be set.""",
        validator=truncated_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True,
    )

    sensitivity = Instrument.control(
        "G", "G%d",
        """A float property that represents the SR510 sensitivity value.
           This property can be set.""",
        validator=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True,
    )

    frequency = Instrument.measurement(
        "F",
        """A float property representing the SR510 input reference frequency""",
    )

    status = Instrument.measurement(
        "Y",
        """A string property representing the bits set within the SR510 status byte""",
        get_process=lambda s: bin(int(s))[2:],
    )

    output = Instrument.measurement(
        "Q",
        """A float property that represents the SR510 output voltage in Volts.""",
    )

    def __init__(self, adapter, name="Stanford Research Systems SR510 Lock-in amplifier",
                 **kwargs):
        kwargs.setdefault('write_termination', '\r')
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs,
        )
