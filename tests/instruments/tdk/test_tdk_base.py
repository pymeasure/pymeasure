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
from pymeasure.instruments.tdk.tdk_base import TDK_Lambda_Base


def test_init():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK")],
    ):
        pass  # Verify the expected communication.


def test_identity():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"IDN?", b'LAMBDA,GENX-Y'),
             (b"REV?", b"REV:1U:4.3")]
    ) as instr:
        assert instr.id == ["LAMBDA", "GENX-Y"]
        assert instr.version == "REV:1U:4.3"


def test_multidrop_capability():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"MDAV?", b'1')]
    ) as instr:
        assert instr.multidrop_capability is True


def test_remote():
    with expected_protocol(
            TDK_Lambda_Base,
            [(b"ADR 6", b"OK"),
             (b"RMT?", b"REM"),
             (b"RMT LOC", b"OK"),
             (b"RMT?", b"LOC"), ]
    ) as instr:
        assert instr.remote == "REM"
        instr.remote = 'LOC'
        assert instr.remote == "LOC"
