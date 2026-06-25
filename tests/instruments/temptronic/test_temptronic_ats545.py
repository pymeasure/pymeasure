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

import pytest

from pymeasure.instruments.temptronic.temptronic_ats545 import ATS545
from pymeasure.test import expected_protocol


def test_next_setpoint_raises():
    with expected_protocol(ATS545, []) as inst, pytest.raises(NotImplementedError):
        inst.next_setpoint()


def test_mode_model_values():
    """The ATS545 ``mode_values`` mapping replaces the ATSBase one.

    Base maps only {'manual': 5, 'program': 6}; replies 10 / 0 / 63 only map
    with the model-specific {'manual': 10, 'program': 0, 'initial': 63}.
    """
    with expected_protocol(
        ATS545,
        [("WHAT?", "10"),
         ("WHAT?", "0"),
         ("WHAT?", "63")],
    ) as inst:
        assert inst.mode == "manual"
        assert inst.mode == "program"
        assert inst.mode == "initial"


def test_temperature_limit_air_low_model_limits():
    """The model-specific air low-limit [-80, 25] feeds the validator."""
    with expected_protocol(ATS545, [("LLIM -80", None)]) as inst:
        # -85 would be valid for the ATSBase range [-99, 25] but is silently
        # clipped to the model-specific lower bound -80 (truncated_range).
        inst.temperature_limit_air_low = -85
