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


class TestHP11713A:
    def test_s9(self):
        with expected_protocol(
                HP11713A,
                [("A9", None),
                 ("B9", None)],
        ) as instr:
            instr.s9 = True
            instr.s9 = False

    def test_s0(self):
        with expected_protocol(
                HP11713A,
                [("A0", None),
                 ("B0", None)],
        ) as instr:
            instr.s0 = True
            instr.s0 = False

    def test_x(self):
        with expected_protocol(
                HP11713A,
                [("A1234", None),
                 ("B1234", None),
                 ("A12B34", None),
                 ("A34B12", None)],
        ) as instr:
            instr.x(True, True, True, True)
            instr.x(False, False, False, False)
            instr.x(True, True, False, False)
            instr.x(False, False, True, True)

    def test_y(self):
        with expected_protocol(
                HP11713A,
                [("A5678", None),
                 ("B5678", None),
                 ("A56B78", None),
                 ("A78B56", None)
                 ],
        ) as instr:
            instr.y(True, True, True, True)
            instr.y(False, False, False, False)
            instr.y(True, True, False, False)
            instr.y(False, False, True, True)

    def test_attenuation_x(self):
        with expected_protocol(
                HP11713A,
                [("A1B234", None),
                 ("A1234", None)],
        ) as instr:
            instr.ATTENUATOR_X = Attenuator_110dB
            instr.attenuation_x(10)
            instr.attenuation_x(110)

    def test_attenuation_y(self):
        with expected_protocol(
                HP11713A,
                [("A5B678", None),
                 ("A5678", None)],
        ) as instr:
            instr.ATTENUATOR_Y = Attenuator_110dB
            instr.attenuation_y(10)
            instr.attenuation_y(110)

    def test_attenuation_x_rounding(self):
        with expected_protocol(
                HP11713A,
                [("A1B234", None),
                 ("A1234", None)],
        ) as instr:
            instr.ATTENUATOR_X = Attenuator_110dB
            instr.attenuation_x(12.5)
            instr.attenuation_x(109)
