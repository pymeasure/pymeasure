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

import pytest
import serial

from pymeasure.adapters import PrologixAdapter

prefix = "\n".join(["++auto 0", "++eoi 1", "++eos 2"]) + "\n"


def make_adapter(**kwargs):
    return PrologixAdapter(serial.serial_for_url("loop://", **kwargs))


@pytest.mark.parametrize("test_input,expected", [("OUTP", prefix + "OUTP\n"),
                                                 ("POWER 22 dBm", prefix + "POWER 22 dBm\n")])
def test_adapter_write(test_input, expected):
    adapter = make_adapter(timeout=0.2)
    adapter.write(test_input)
    assert(adapter.connection.read(len(expected) + 10) == expected.encode())


@pytest.mark.parametrize(
    "test_input,expected", [
        ([1, 2, 3], prefix.encode() + b'OUTP#13\x01\x02\x03' + b"\n"),
        ([43, 27, 10, 13, 97, 98, 99], prefix.encode() +
         b'OUTP#17\x1b\x2b\x1b\x1b\x1b\x0a\x1b\x0dabc' + b"\n")
    ]
)
def test_adapter_write_binary_values(test_input, expected):
    adapter = make_adapter(timeout=0.2)
    adapter.write_binary_values("OUTP", test_input, datatype='B')
    # Add 10 bytes more, just to check that no extra bytes are present
    assert(adapter.connection.read(len(expected) + 10) == expected)
