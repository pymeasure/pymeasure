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

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.teledyne.teledyneT3DSO3024HD import T3DSO3024HD

def test_bwlimit():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:BWLimit 20M", None),   # (send CMD, answer=None )
         (":CHANnel1:BWLimit?", "20M")],    # (query, simulated answer)
    ) as instr:
        instr.channel_1.bwlimit = "20M"
        assert instr.channel_1.bwlimit == "20M"
        
def test_impedance_limits_scale_range():
    with expected_protocol(
        T3DSO3024HD,
        [
            (":CHANnel1:IMPedance FIFT", None),
            (":CHANnel1:SCALe 5.000E-01", None),
        ],
    ) as instr:
        instr.channel_1.set_impedance(50.0)
        instr.channel_1.scale = 0.5

        with pytest.raises(ValueError):
            instr.channel_1.scale = 2.0   # should raise a value error since impedance was set to 50.0
            
def test_invert_set_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert ON", None)],
    ) as instr:
        instr.channel_1.invert = True


def test_invert_set_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert OFF", None)],
    ) as instr:
        instr.channel_1.invert = False


def test_invert_get_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert?", "ON")],
    ) as instr:
        assert instr.channel_1.invert is True


def test_invert_get_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert?", "OFF")],
    ) as instr:
        assert instr.channel_1.invert is False


def test_invert_invalid_value_rejected():
    with expected_protocol(
        T3DSO3024HD,
        [],
    ) as instr:
        with pytest.raises(ValueError):
            instr.channel_1.invert = "YES"