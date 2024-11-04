#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.keithley import KeithleyDAQ6510


def test_init():
    with expected_protocol(
        KeithleyDAQ6510,
        [],
    ):
        pass


def test_current_range_set():
    with expected_protocol(
            KeithleyDAQ6510,
            [(b':SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG 1', None)],
    ) as inst:
        inst.current_range = 1.0


def test_current_range_get():
    with expected_protocol(
            KeithleyDAQ6510,
            [(b':SENS:CURR:RANG?', b'1.0\n')],
    ) as inst:
        assert inst.current_range == 1.0


def test_current_nplc_set():
    with expected_protocol(
            KeithleyDAQ6510,
            [(b':SENS:CURR:NPLC 2', None)],
    ) as inst:
        inst.current_nplc = 2


def test_current_nplc_get():
    with expected_protocol(
            KeithleyDAQ6510,
            [(b':SENS:CURR:NPLC?', b'2\n')],
    ) as inst:
        assert inst.current_nplc == 2.0


def test_id():
    with expected_protocol(
            KeithleyDAQ6510,
            [(b'*IDN?', b'KEITHLEY INSTRUMENTS,MODEL DAQ6510,04591126,1.7.12b\n')],
    ) as inst:
        assert inst.id == 'KEITHLEY INSTRUMENTS,MODEL DAQ6510,04591126,1.7.12b'


def test_reset():
    with expected_protocol(
            KeithleyDAQ6510,
            [(b'*RST', None)],
    ) as inst:
        assert inst.reset() is None
