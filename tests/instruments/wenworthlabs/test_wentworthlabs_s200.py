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
from pymeasure.instruments.wenworthlabs.s200 import S200


def test_theta_position():
    """Verify the communication of the theta position setter."""
    with expected_protocol(
            S200,
            [("GTTH 0", "INF 000"),
             ("GTTH 120000", "INF 000"),
             ("PSTH", "PSTH 10000")],
    ) as inst:
        inst.theta_position = 0
        inst.theta_position = 120000
        assert inst.theta_position == 10000


def test_lamp():
    """Verify the control on/off of the lamp."""
    with expected_protocol(
            S200,
            [("LI1", "INF 000"),
             ("LI0", "INF 000")],
    ) as inst:
        inst.lamp_on = True
        inst.lamp_on = False


def test_chuck_lift():
    """Verify the lift's control (up/down) of the main chuck of the probe station."""
    with expected_protocol(
            S200,
            [("CUP", "INF 000"),
             ("CDW", "INF 000")],
    ) as inst:
        inst.chuck_lift = True
        inst.chuck_lift = False


def test_chuck_gross_lift():
    """Verify the gross lift's control (up/down) of the main chuck of the probe station."""
    with expected_protocol(
            S200,
            [("GUP", "INF 000"),
             ("GDW", "INF 000")],
    ) as inst:
        inst.chuck_gross_lift = True
        inst.chuck_gross_lift = False


def test_chuck_override():
    """Verify the override's control (on/off) of the main chuck of the probe station."""
    with expected_protocol(
            S200,
            [("CO1", "INF 000"),
             ("CO0", "INF 000")],
    ) as inst:
        inst.chuck_override = True
        inst.chuck_override = False


def test_x_position():
    """Verify the x's position control of the main chuck of the probe station."""
    with expected_protocol(
            S200,
            [("PSS X", "PSS 20000"),
             ("GTS X,20000", "INF 000")],
    ) as inst:
        assert inst.x_position == 20000
        inst.x_position = 20000


def test_y_position():
    """Verify the y's position control of the main chuck of the probe station."""
    with expected_protocol(
            S200,
            [("PSS Y", "PSS 20000"),
             ("GTS Y,20000", "INF 000")],
    ) as inst:
        assert inst.y_position == 20000
        inst.y_position = 20000
