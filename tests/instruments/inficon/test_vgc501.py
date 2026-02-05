#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from pymeasure.instruments.inficon import VGC501


def test_init():
    with expected_protocol(
            VGC501,
            [],
    ):
        pass  # Verify the expected communication.


def test_error_status_getter():
    with expected_protocol(
            VGC501,
            [(b'ERR', b'\x06\r\n0000')],
    ) as inst:
        assert inst.error_status == 0.0


def test_information_getter():
    with expected_protocol(
            VGC501,
            [(b'AYT', b'\x06\r\nVGC501,398-481,3658,1.07,1.0')],
    ) as inst:
        assert inst.information == ['VGC501', '398-481', 3658.0, 1.07, 1.0]


def test_pressure_1_getter():
    with expected_protocol(
            VGC501,
            [(b'PR1', b'\x06\r\n0,+7.5500E-02')],
    ) as inst:
        assert inst.pressure == [0.0, 0.0755]
