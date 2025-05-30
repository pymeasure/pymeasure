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

import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.fluke import Fluke7341


def test_setpoint_getter():
    with expected_protocol(Fluke7341,
                           [("s", "set: 150.00 C")],
                           ) as inst:
        assert inst.set_point == 150


def test_setpoint_setter():
    with expected_protocol(Fluke7341,
                           [("s=150", None)],
                           ) as inst:
        inst.set_point = 150


def test_temperature_getter():
    with expected_protocol(Fluke7341,
                           [("t", "t: 55.69 C")],
                           ) as inst:
        assert inst.temperature == 55.69


def test_unit_getter():
    with expected_protocol(Fluke7341,
                           [("u", "u: C")],
                           ) as inst:
        assert inst.unit == "C"


@pytest.mark.parametrize("unit", ("c", "f"))
def test_unit_setter(unit):
    with expected_protocol(Fluke7341,
                           [(f"u={unit}", None)],
                           ) as inst:
        inst.unit = unit


def test_version_getter():
    with expected_protocol(Fluke7341,
                           [("*ver", "ver.7341,1.00")],
                           ) as inst:
        assert inst.id == "Fluke,7341,NA,1.00"
