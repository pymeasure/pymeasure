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

from pymeasure.instruments.hp.hp11713a import HP11713A, Attenuator_110dB

import pytest


class TestHP11713A:
    @pytest.mark.parametrize("channel", list(range(0, 9)))
    def test_channels(self, channel):
        with expected_protocol(
                HP11713A,
                [(f"A{channel}", None),
                 (f"B{channel}", None)],
        ) as instr:
            ch = getattr(instr, f"ch_{channel}")
            ch.enabled = True
            ch.enabled = False

    def test_attenuation_x(self):
        with expected_protocol(
                HP11713A,
                [("A1", None),
                 ("B2", None),
                 ("B3", None),
                 ("B4", None),
                 ("A1", None),
                 ("A2", None),
                 ("A3", None),
                 ("A4", None)],
        ) as instr:
            instr.ATTENUATOR_X = Attenuator_110dB
            instr.attenuation_x(10)
            instr.attenuation_x(110)

    def test_attenuation_y(self):
        with expected_protocol(
                HP11713A,
                [("A5", None),
                 ("B6", None),
                 ("B7", None),
                 ("B8", None),
                 ("A5", None),
                 ("A6", None),
                 ("A7", None),
                 ("A8", None)],
        ) as instr:
            instr.ATTENUATOR_Y = Attenuator_110dB
            instr.attenuation_y(10)
            instr.attenuation_y(110)

    def test_attenuation_x_rounding(self):
        with expected_protocol(
                HP11713A,
                [("A1", None),
                 ("B2", None),
                 ("B3", None),
                 ("B4", None),
                 ("A1", None),
                 ("A2", None),
                 ("A3", None),
                 ("A4", None)],
        ) as instr:
            instr.ATTENUATOR_X = Attenuator_110dB
            instr.attenuation_x(12.5)
            instr.attenuation_x(109)

    def test_deactivate_all(self):
        with expected_protocol(
                HP11713A,
                [("B1234567890", None)],
        ) as instr:
            instr.deactivate_all()
