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

from pymeasure.test import expected_protocol
from pymeasure.instruments.srs.sr860 import SR860


@pytest.mark.parametrize("channel, cmd", (
    ("aux_out_1", "AUXV 0, %g"),
    ("aux_out_2", "AUXV 1, %g"),
    ("aux_out_3", "AUXV 2, %g"),
    ("aux_out_4", "AUXV 3, %g"),
))
@pytest.mark.parametrize("value", (1e-9, 1e-7, -1e-7, 0.5, 1.5, -10.5, 10.5))
def test_aux_out_small_values(channel, cmd, value):
    """Verify that aux outputs transmit sub-microvolt values without truncation.

    Using %f would silently round values smaller than 1e-6 to zero.
    """
    with expected_protocol(
        SR860,
        [(cmd % value, None)],
    ) as inst:
        setattr(inst, channel, value)
