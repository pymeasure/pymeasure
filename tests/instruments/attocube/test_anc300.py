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

from pymeasure.instruments.attocube import ANC300Controller

# Note: This communication does not contain the first several device
# responses, as they are ignored due to `adapter.flush_read_buffer()`.
passwd = "passwd"
init_comm = [
    (passwd, "*" * len(passwd)),
    (None, "Authorization success"),
    ("echo off", "> echo off"),
    (None, "OK"),
]


def test_stepu():
    """Test a setting."""
    with expected_protocol(
        ANC300Controller,
        init_comm + [("setm 1 stp", "OK"), ("stepu 1 15", "OK"), ],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        instr.a.mode = "stp"
        with pytest.warns(FutureWarning):
            instr.a.stepu = 15


def test_continuous_move():
    """Test a continous move setting."""
    with expected_protocol(
        ANC300Controller,
        init_comm + [("setm 3 stp", "OK"), ("stepd 3 c", "OK"), ],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        instr.c.mode = "stp"
        instr.c.move_raw(float('-inf'))


def test_capacity():
    """Test a float measurement."""
    with expected_protocol(
        ANC300Controller,
        init_comm + [("getc 1", "capacitance = 998.901733 nF"), (None, "OK")],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        assert instr.a.capacity == 998.901733


def test_frequency():
    """Test an integer measurement."""
    with expected_protocol(
        ANC300Controller,
        # the \n in the following is indeed included in the return msg!
        init_comm + [("getf 1", "frequency = 111 Hz\n"), (None, "OK")],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        assert instr.a.frequency == 111


def test_measure_capacity():
    """Test triggering a capacity measurement."""
    with expected_protocol(
        ANC300Controller,
        init_comm + [
            ("setm 1 cap", "OK"),
            ("capw 1", "capacitance = 0.000000 nF"),
            (None, "OK"),
            ("getc 1", "capacitance = 1020.173401 nF"),
            (None, "OK"),
        ],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        assert instr.a.measure_capacity() == 1020.173401


def test_move_raw():
    """Test a raw movement."""
    with expected_protocol(
        ANC300Controller,
        init_comm + [
            ("stepd 2 18", "OK"),
        ],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        instr.b.move_raw(-18)


def test_move():
    """Test a movement."""
    with expected_protocol(
        ANC300Controller,
        init_comm + [
            ("setm 3 stp", "OK"),
            ("stepd 3 20", "OK"),
            ("getf 3", "frequency = 111 Hz\n"),
            (None, "OK"),
            ("stepw 3", "OK"),
        ],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        instr.c.move(-20, gnd=False)


def test_ground_all():
    """Test grounding of all axis"""
    with expected_protocol(
        ANC300Controller,
        init_comm + [
            ("setm 1 gnd", "OK"),
            ("setm 2 gnd", "OK"),
            ("setm 3 gnd", "OK"),
        ],
        axisnames=["a", "b", "c"],
        passwd=passwd,
    ) as instr:
        instr.ground_all()
