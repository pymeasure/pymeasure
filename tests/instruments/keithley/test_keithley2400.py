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

from pymeasure.instruments.keithley import Keithley2400


def test_id():
    with expected_protocol(
        Keithley2400,
        [("*IDN?", "KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx, yyyyy/zzzzz /a/d")],
    ) as inst:
        assert inst.id == "KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx, yyyyy/zzzzz /a/d"


def test_next_error():
    with expected_protocol(Keithley2400,
                           [("SYST:ERR?", '-113, "Undefined header"')],
                           ) as inst:
        assert inst.next_error == [-113, ' "Undefined header"']


def test_enable_source():
    with expected_protocol(Keithley2400,
                           [("OUTPUT ON", None)],
                           ) as inst:
        inst.enable_source()
