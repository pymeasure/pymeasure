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

from pymeasure.instruments.hp import HP54616B


def test_frequency():
    with expected_protocol(
            HP54616B,
            [(b":ACQ:COMP 100", None),
             (b":ACQ:COMP?", 100)],
    ) as instr:
        instr.acquire_complete = 100
        assert instr.acquire_complete == 100

def test_identity():
    with expected_protocol(
            HP54616B,
            [(b"*IDN?", "HEWLETT-PACKARD,54616B,0,A.02.30")],
    ) as instr:
        assert instr.id == "HEWLETT-PACKARD,54616B,0,A.02.30"

def test_channel_setup():
    with expected_protocol(
            HP54616B,
            [(b":CHAN1:SET?", "CHAN1:RANGE +1.60000000E-001;OFFSET -1.31250000E-002;COUP DC;BWLIMIT OFF;INVERT OFF;VERNIER OFF;PROBE X1;PMODE AUT;INPUT ONEM;PROTECT ON")],
    ) as instr:
        # Checking keys of channel config dict
        channel_dict = instr.ch1.current_configuration
        expected_channel_dict_keys = ["CHAN", 'RANGE', 'OFFSET', 'COUP', 'BWLIMIT', 'INVERT', 'VERNIER', 'PROBE', 'PMODE', 'INPUT', 'PROTECT']
        for key in channel_dict:
            assert key in expected_channel_dict_keys

def test_channel_voltage_offset():
    with expected_protocol(
            HP54616B,
            [(b":CHAN1:OFFS 5.00000E-01", None)],
    ) as instr:
        instr.ch1.offset = 0.5