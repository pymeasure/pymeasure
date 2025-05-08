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

from pymeasure.test import expected_protocol


from pymeasure.instruments.oxfordinstruments.ips120_10 import IPS120_10


def test_version():
    with expected_protocol(IPS120_10,
                           [("V", "IPS120-10 Version 3.04 @ Oxford Instruments 1996")]
                           ) as inst:
        assert inst.version == "IPS120-10 Version 3.04 @ Oxford Instruments 1996"


def test_activity_getter():
    with expected_protocol(IPS120_10,
                           [("X", "X00A0C0M00P00")]
                           ) as inst:
        assert inst.activity == "hold"


def test_activity_setter():
    with expected_protocol(IPS120_10,
                           [("A0", "A")]
                           ) as inst:
        inst.activity = "hold"


def test_current_setpoint_getter():
    with expected_protocol(IPS120_10,
                           [("R0", "R+1.3")]
                           ) as inst:
        assert inst.current_setpoint == 1.3


def test_current_setpoint_setter():
    with expected_protocol(IPS120_10,
                           [("I1.300000", "I")]
                           ) as inst:
        inst.current_setpoint = 1.3


def test_control_mode_getter():
    with expected_protocol(IPS120_10,
                           [("X", "X00A0C1M00P00")]
                           ) as inst:
        assert inst.control_mode == "RL"


def test_control_mode_setter():
    with expected_protocol(IPS120_10,
                           [("C1", "C")]
                           ) as inst:
        inst.control_mode = "RL"
