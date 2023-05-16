#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.test import expected_protocol
from pymeasure.instruments.tektronix.tek371A import Tektronix371A

def test_collector_supply_polarity():
    """Verify the communication of the collector supply polarity."""
    with expected_protocol(
            Tektronix371A,
            [("CSPol NPN", None),
             ("CSPol?", "CSPOL NPN")],
    ) as inst:
        inst.cs_polarity = "NPN"
        assert inst.cs_polarity == "CSPOL NPN"


def test_collector_supply():
    """Verify the communication of the collector supply."""
    with expected_protocol(
            Tektronix371A,
            [("VCSpply 1.2", None),
             ("VCSpply?", 1.2)],
    ) as inst:
        inst.cs_collector_supply = 1.2
        assert inst.cs_collector_supply == 1.2


def test_cursor_dot():
    """Verify the communication of the cursor dot."""
    with expected_protocol(
            Tektronix371A,
            [("DOT?", 512)],
    ) as inst:
        assert inst.cursor_dot == 512


def test_cursor_dot_vvalue():
    """Verify the communication of the cursor dot."""
    with expected_protocol(
            Tektronix371A,
            [("REAdout? SCientific", 10.2)],
    ) as inst:
        assert inst.cursor_dot_vvalue == 10.2


def test_get_curve_points():
    """Verify the communication of the curve."""
    with expected_protocol(
            Tektronix371A,
            [(None, [(1.2, 0.1), (1.3, 0.2), (1.4, 0.3), (1.5, 0.4)])],
    ) as inst:
        assert inst.get_curve.points == [(1.2, 0.1), (1.3, 0.2), (1.4, 0.3), (1.5, 0.4)]
