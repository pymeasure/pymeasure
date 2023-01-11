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

from pymeasure.test import expected_protocol

from pymeasure.instruments.panasonic import PanasonicVP7722A


def test_init():
    with expected_protocol(
            PanasonicVP7722A,
            [],
            ):
        pass  # Verify the expected communication.


def test_frequency():
    with expected_protocol(
        PanasonicVP7722A,
        [("FR110000.00HZ", None),
         ("TM1", "10000E-01")]
    ) as inst:
        inst.frequency = 112000
        assert inst.frequency == 1000.0


def test_input():
    with expected_protocol(
        PanasonicVP7722A,
        [("TM2", "00634E-03\r\n"),
         ("TM3", "10000E-01,00634E-03\r\n"),
         ("TM7", "10000E-01,00634E-03,00133E-05\r\n")]
    ) as inst:
        assert inst.input_level == 0.634
        assert inst.frequency_and_input_level == [1000.0, 0.634]
        assert inst.frequency_and_input_level_and_measure_data == [1000.0, 0.634, 0.00133]
