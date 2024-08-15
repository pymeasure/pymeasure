#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.srs.sr830 import SR830


def test_id():
    """Verify the communication of the device type."""
    with expected_protocol(
        SR830,
        [("*IDN?", "Stanford_Research_Systems,SR830,s/n12345,ver1.07"),],
    ) as inst:
        assert inst.id == "Stanford_Research_Systems,SR830,s/n12345,ver1.07"


@pytest.mark.parametrize("number, value", (
        ("0", 2e-9),
        ("14", 100e-6),
        ("25", 0.5),
))
def test_sensitivity(number, value):
    """Verify the communication of the sensitivity getter."""
    with expected_protocol(
        SR830,
        [("SENS?", number),],
    ) as inst:
        assert inst.sensitivity == pytest.approx(value)


def test_frequency():
    """Verify the communication of the frequency getter."""
    with expected_protocol(
        SR830,
        [("FREQ?", "121.98"),],
    ) as inst:
        assert inst.frequency == pytest.approx(121.98)


def test_snap():
    """Verify the communication of the measurement values."""
    with expected_protocol(
        SR830,
        [("SNAP? 1,2", "-4.17234e-007,-5.9605e-007"),],
    ) as inst:
        xy = inst.xy
        assert len(xy) == 2
        assert xy[0] == pytest.approx(-4.17234e-007)
        assert xy[1] == pytest.approx(-5.9605e-007)


def test_get_scaling():
    """Verify the communication of the X channel scaling settings."""
    with expected_protocol(
        SR830,
        [("OEXP? 1", "9.7,1"),],
    ) as inst:
        offset, expand = inst.get_scaling("X")
        assert offset == pytest.approx(9.7)
        assert expand == pytest.approx(10)


def test_output_conversion():
    """Verify the communication of the X channel value with conversion."""
    with expected_protocol(
        SR830,
        [("OEXP? 1", "10,1"),
         ("SENS?", "19"),
         ("OUTP?1", "-0.000500266"),
         ],
    ) as inst:
        conv = inst.output_conversion("X")
        assert conv(inst.x) == pytest.approx(-2.66e-7)
