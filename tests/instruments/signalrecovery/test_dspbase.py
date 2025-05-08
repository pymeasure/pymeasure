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

from pymeasure.instruments.signalrecovery.dsp_base import DSPBase


@pytest.mark.parametrize("index, reference", [(idx, i) for idx, i in enumerate(DSPBase.REFERENCES)])
def test_reference(index, reference):
    with expected_protocol(
            DSPBase,
            [(f"IE {index}", None)],
    ) as instr:
        instr.reference = reference


@pytest.mark.parametrize("index, imode", [(idx, i) for idx, i in enumerate(DSPBase.IMODES)])
def test_imode(index, imode):
    with expected_protocol(
            DSPBase,
            [(f"IMODE {index}", None)],
    ) as instr:
        instr.imode = imode


@pytest.mark.parametrize("reading, value",
                         [(b"-12\x00", -12), (b"0\x00", 0), (b"5", 5), (b"12", 12)])
def test_dac1(reading, value):
    with expected_protocol(
            DSPBase,
            [("DAC. 1", reading)],
    ) as instr:
        assert instr.dac1 == value


@pytest.mark.parametrize("reading, value",
                         [(b'-2.14E-07\r\n', -2.14e-07),
                          (b'-0.0E+00\x00\r\n', 0.0),
                          (b'1.2E-07\r\n', 1.2e-07),
                          (b'6.44E-07\r\n', 6.44e-07),
                          ])
def test_x(reading, value):
    with expected_protocol(
            DSPBase,
            [('X.', reading)],
    ) as instr:
        assert instr.x == value
