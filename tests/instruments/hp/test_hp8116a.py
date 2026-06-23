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

from pymeasure.instruments.hp import HP8116A
from pymeasure.instruments.hp.hp8116a import Status


class HP8116AWithMockStatus(HP8116A):
    @property
    def status(self):
        return Status(5)


init_comm = [(b"CST", b"x" * 87 + b' ,\r\n')]  # communication during init


def test_init():
    with expected_protocol(
            HP8116AWithMockStatus,
            init_comm,
    ):
        pass  # Verify the expected communication.


def test_duty_cycle():
    with expected_protocol(
            HP8116AWithMockStatus,
            init_comm + [(b"IDTY", b"00000035")],
    ) as instr:
        assert instr.duty_cycle == 35


def test_duty_cycle_setter():
    with expected_protocol(
            HP8116AWithMockStatus,
            init_comm + [(b"DTY 34.5 %", None)],
    ) as instr:
        instr.duty_cycle = 34.5


def test_sweep_time():
    with expected_protocol(HP8116AWithMockStatus, init_comm + [("SWT 5 S", None)]) as inst:
        # This test tests also the generate_1_2_5_sequence method and truncation.
        inst.sweep_time = 3


def test_limit_enabled():
    with expected_protocol(HP8116AWithMockStatus, init_comm + [("L1", None)]) as inst:
        inst.limit_enabled = True


def test_limit_enabled_getter():
    with expected_protocol(
        HP8116AWithMockStatus,
        init_comm
        + [
            (
                "CST",
                "M1,CT0,T1,W1,H0,A0,L0,C0,D1,B"
                # HACK do not show full response due to implementation details.
                # "UR 001 #,RPT 100 MS,STA 1.00 KHZ,STP 100 KHZ,"
                # "SWT 50.0 MS,MRK 1.00 KHZ,FRQ 1.00 KHZ,DTY 50 %,WID 100 US,AMP 1.00V,OFS 100 MV",
            ),
        ],
    ) as inst:
        assert inst.limit_enabled is False
