#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from pymeasure.instruments.signal_generator import SignalGenerator

class AgilentE4438C(SignalGenerator):
    POWER_RANGE_MIN_dBm = -130.0
    POWER_RANGE_MAX_dBm = 30.0
    POWER_RANGE_dBm = [POWER_RANGE_MIN_dBm, POWER_RANGE_MAX_dBm]

    FREQUENCY_MIN_Hz = 250e3
    FREQUENCY_MAX_Hz = 6e9
    FREQUENCY_RANGE_Hz = [FREQUENCY_MIN_Hz, FREQUENCY_MAX_Hz]

    def __init__(self, resourceName, **kwargs):
        super(AgilentE4440A, self).__init__(
            resourceName,
            "Agilent E4438C Signal Generator",
            **kwargs
        )
