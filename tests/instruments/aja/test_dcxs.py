#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.aja.dcxs import DCXS


def test_id():
    """
    Test DCXS identification property
    """
    with expected_protocol(
        DCXS,
        [("?", "DCXS750-4"), ],
    ) as inst:
        assert inst.id == "DCXS750-4"


@pytest.mark.parametrize("setpoint", [5, 97])
def test_setpoint(setpoint):
    """
    Test DCXS setpoint
    """
    with expected_protocol(
        DCXS,
        [
            (f"C{setpoint:04d}", None),
            ("b", f"{setpoint:04d}"),
        ],
    ) as inst:
        inst.setpoint = setpoint
        assert setpoint == inst.setpoint


def test_regulation_mode():
    """
    Test DCXS regulation mode
    """
    with expected_protocol(
        DCXS,
        [
            ("D0", None),
            ("c", 0),
        ],
    ) as inst:
        inst.regulation_mode = "power"
        assert "power" == inst.regulation_mode


def test_enabled():
    """
    Test DCXS enabled
    """
    with expected_protocol(
        DCXS,
        [
            ("A", None),
            ("a", "1"),
        ],
    ) as inst:
        inst.enabled = True
        assert inst.enabled is True


def test_material():
    """
    Test DCXS material name and its truncation
    """
    with expected_protocol(
        DCXS,
        [
            ("IALongNam", None),
            ("n", "ALongNam"),
        ],
    ) as inst:
        inst.material = "ALongNameWhichGetsTruncated"
        assert "ALongNam" == inst.material
