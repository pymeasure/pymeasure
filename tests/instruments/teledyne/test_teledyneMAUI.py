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

from pymeasure.instruments.teledyne.teledyne_oscilloscope import sanitize_source
from pymeasure.instruments.teledyne.teledyneMAUI import TeledyneMAUI
from pymeasure.test import expected_protocol

INVALID_CHANNELS = ["INVALID_SOURCE", "C1 C2", "C1 MATH", "C1234567", "CHANNEL"]
VALID_CHANNELS = [('C1', 'C1'), ('CHANNEL2', 'C2'), ('ch 3', 'C3'), ('chan 4', 'C4'),
                  ('\tC3\t', 'C3'), (' math ', 'MATH')]


def test_init():
    with expected_protocol(
            TeledyneMAUI,
            [(b"CHDR OFF", None)]
    ):
        pass  # Verify the expected communication.


def test_removed_property():
    """Verify that certain inherited properties are removed successfully.

    Some actions from the base class are not valid for this one.
    """
    with expected_protocol(TeledyneMAUI, [(b'CHDR OFF', None)]) as instr:
        props = ["timebase_hor_magnify"]
        for prop in props:
            with pytest.raises(AttributeError):
                _ = getattr(instr, prop)

        ch_props = ["trigger_level2", "skew_factor", "unit", "invert"]
        for prop in ch_props:
            with pytest.raises(AttributeError):
                _ = getattr(instr.ch(1), prop)


@pytest.mark.parametrize("channel", INVALID_CHANNELS)
def test_invalid_source(channel):
    with pytest.raises(ValueError):
        sanitize_source(channel)


@pytest.mark.parametrize("channel", VALID_CHANNELS)
def test_sanitize_valid_source(channel):
    assert sanitize_source(channel[0]) == channel[1]


def test_bwlimit():
    with expected_protocol(
            TeledyneMAUI,
            [(b"CHDR OFF", None),
             (b"BWL C1,OFF", None),
             (b"BWL?", b"C1,OFF"),
             (b"BWL C1,200MHZ", None),
             (b"BWL?", b"C1,200MHZ"),
             (b"BWL C1,ON", None),
             (b"BWL?", b"C1,ON"),
             ]
    ) as instr:
        instr.ch_1.bwlimit = "OFF"
        assert instr.bwlimit["C1"] == "OFF"
        instr.ch_1.bwlimit = "200MHZ"
        assert instr.bwlimit["C1"] == "200MHZ"
        instr.ch_1.bwlimit = "ON"
        assert instr.bwlimit["C1"] == "ON"


def test_offset():
    with expected_protocol(
            TeledyneMAUI,
            [(b"CHDR OFF", None),
             (b"C1:OFST 1.00E+00V", None),
             (b"C1:OFST?", b"1.00E+00")
             ]
    ) as instr:
        instr.ch_1.offset = 1.
        assert instr.ch_1.offset == 1.


def test_attenuation():
    with expected_protocol(
            TeledyneMAUI,
            [(b"CHDR OFF", None),
             (b"C1:ATTN 100", None),
             (b"C1:ATTN?", b"100"),
             (b"C1:ATTN 0.1", None),
             (b"C1:ATTN?", b"0.1")
             ]
    ) as instr:
        instr.ch_1.probe_attenuation = 100
        assert instr.ch_1.probe_attenuation == 100
        instr.ch_1.probe_attenuation = 0.1
        assert instr.ch_1.probe_attenuation == 0.1


if __name__ == '__main__':
    pytest.main()
