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

import pytest

from pymeasure.test import expected_protocol
from pymeasure.adapters import FakeAdapter

from pymeasure.instruments.attocube import ANC300Controller
from pymeasure.instruments.attocube import anc300


@pytest.fixture(autouse=True)
def modding(monkeypatch):
    monkeypatch.setattr(anc300, "VISAAdapter", FakeAdapter)


def test_stepu():
    """Test a setting."""
    with expected_protocol(
            ANC300Controller,
            [(None, b"xy"),
             (b"passwd\r\n", b'xy\r\nAuthorization success\r\nOK'),
             (b"echo off\r\n", b"x\r\nOK"),
             (b"stepu 1 15\r\n", b"OK")],
            axisnames=["a", "b", "c"],
            passwd="passwd"
            ) as instr:
        instr.a.stepu = 15


def test_voltage():
    """Test a measurement."""
    with expected_protocol(
            ANC300Controller,
            [(None, b"xy"),
             (b"passwd\r\n", b'xy\r\nAuthorization success\r\nOK'),
             (b"echo off\r\n", b"x\r\nOK"),
             (b"geto 1\r\n", b"5\r\nOK")],
            axisnames=["a", "b", "c"],
            passwd="passwd"
            ) as instr:
        assert instr.a.output_voltage == 5
