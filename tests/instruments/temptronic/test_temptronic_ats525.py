#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.instruments.temptronic.temptronic_ats525 import ATS525
from pymeasure.test import expected_protocol


def test_temperature_limit_air_low_model_limits():
    """The model-specific air low-limit [-60, 25] feeds the validator."""
    with expected_protocol(ATS525, [("LLIM -60", None)]) as inst:
        # -70 would be valid for the ATSBase range [-99, 25] but is silently
        # clipped to the model-specific lower bound -60 (truncated_range).
        inst.temperature_limit_air_low = -70


def test_system_current():
    with expected_protocol(ATS525, [("AMPS?", "12.5")]) as inst:
        assert inst.system_current == 12.5
