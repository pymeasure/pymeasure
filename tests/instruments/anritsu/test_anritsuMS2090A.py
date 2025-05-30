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

from pymeasure.instruments.anritsu import AnritsuMS2090A


def test_init():
    with expected_protocol(
            AnritsuMS2090A,
            [],
            ):
        pass  # Verify the expected communication.


def test_freq_conf():
    with expected_protocol(
            AnritsuMS2090A,
            [(b"FREQuency:CENTer 9000", None), (b"FREQuency:CENTer?", 9000)],
            ) as instr:
        instr.frequency_center = 9000
        assert instr.frequency_center == 9000


def test_preamp():
    with expected_protocol(
            AnritsuMS2090A,
            [(b"POWer:RF:GAIN:STATe ON", None), (b"POWer:RF:GAIN:STATe?", 'ON')],
            ) as instr:
        instr.preamp = True
        assert instr.preamp is True
