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
from unittest.mock import MagicMock

from pymeasure.test import expected_protocol

from pymeasure.instruments.optosigma import SBIS26


def test_init():
    # Test initialization of the instrument
    with expected_protocol(
            SBIS26,
            [("#CONNECT", None), ],
    ):
        pass  # Verify the expected communication.


def test_position():
    # Test the position setting
    with expected_protocol(
            SBIS26,
            [("#CONNECT", None),
             ("Q:D,1", "D,1,-1000"),
             ],
    ) as instr:
        assert instr.ch_1.position == -1000

def test_speed():
    # Test the speed setting
    with expected_protocol(
        SBIS26,
        [("#CONNECT", None),
         ("?:D,1,D", "10000,100000,200"),
         ("D:D,1,10000,100000,200", None),
         ],
    ) as instr:
        assert instr.ch_1.speed == [10000, 100000, 200]
        instr.ch_1.speed = (10000,100000,200)
