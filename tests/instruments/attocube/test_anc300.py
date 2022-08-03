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

from pymeasure.instruments.attocube import ANC300Controller
from pymeasure.instruments.attocube.adapters import Mock_TelnetAdapter, AttocubeConsoleAdapter

#############################################################################
# In order to run the tests, you have to change the superclass of the adapter
# from TelnetAdapter to Mock_TelnetAdapter
#############################################################################
if not issubclass(AttocubeConsoleAdapter, Mock_TelnetAdapter):
    pytest.skip("Not the right test adapter present.", allow_module_level=True)


@pytest.fixture
def instr():
    instr = ANC300Controller("123", ["a", "b", "c"], "passwd")
    yield instr
    protocol = instr.adapter
    assert protocol._index == len(protocol.comm_pairs), (
        "Unprocessed protocol definitions remain: "
        f"{protocol.comm_pairs[protocol._index:]}.")
    assert protocol._write_buffer == b"", (
        f"Non-empty write buffer: '{protocol._write_buffer}'.")
    assert protocol._read_buffer == b"", (
        f"Non-empty read buffer: '{protocol._read_buffer}'.")


def test_stepu(instr):
    """Test a setting."""
    instr.adapter.comm_pairs.extend([(b"stepu 1 15\r\n", b"OK")])
    instr.a.stepu = 15


def test_voltage(instr):
    """Test a measurement."""
    instr.adapter.comm_pairs.extend([(b"geto 1\r\n", b"5\r\nOK")])
    assert instr.a.output_voltage == 5
