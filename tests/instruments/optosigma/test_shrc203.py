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

from pymeasure.instruments.optosigma import SHRC203


def test_init():
    # Test the initialization of the instrument
    with expected_protocol(
            SHRC203, [], ):
        pass  # Verify the expected communication.


def test_open_loop():
    # Test the open loop setting
    with expected_protocol(
            SHRC203,
            [("F:10", "OK"),
             ("?:F1", "0")
             ],
    ) as instr:
        instr.ch_1.open_loop = 0
        assert instr.ch_1.open_loop == 0

def test_speed_slow():
    # Test the speed setting
    with expected_protocol(
            SHRC203,
            [("DS:1 20000", "OK"),
             ("?:DS1", "10000")
             ],
    ) as instr:
        instr.ch_1.speed_slow = 20000
        assert instr.ch_1.speed_slow == 10000


def test_motion_done():
    # Test the motion done setting
    with expected_protocol(
            SHRC203,
            [("!:1S", "R")],
    ) as instr:
        assert instr.ch_1.motion_done == "R"


def test_step():
    # Test the step setting
    with expected_protocol(
            SHRC203,
            [("?:P1", 1)],
    ) as instr:
        assert instr.ch_1.step == 1


def test_home():
    # Test the home setting
    with expected_protocol(
            SHRC203,
            [("H:1", "OK")],
    ) as instr:
        instr.ch_1.home()


def test_mode():
    # Test the mode setting
    with expected_protocol(
            SHRC203,
            [("MODE:MANUAL", "OK"),
             ("?:MODE", "HOST")],
    ) as instr:
        instr.mode = "MANUAL"
        assert instr.mode == "HOST"
