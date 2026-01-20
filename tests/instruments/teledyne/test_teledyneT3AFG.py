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
from pymeasure.instruments.teledyne.teledyneT3AFG import TeledyneT3AFG


def test_output_enabled():
    """Verify the output enable setter and getter."""
    with expected_protocol(
        TeledyneT3AFG,
        [("C1:OUTPut ON", None),
         ("C1:OUTPut?", "C1:OUTP OFF,LOAD,HZ,PLRT,NOR")],
    ) as inst:
        inst.ch_1.output_enabled = True
        assert inst.ch_1.output_enabled is False


def test_wavetype():
    """Verify the wavetype setter and getter for ramp or sine wavetype."""
    with expected_protocol(
        TeledyneT3AFG,
        [("C1:BSWV WVTP,RAMP", None),
         ("C1:BSWV?", "C1:BSWV WVTP,SINE,FRQ,0.3HZ,PERI,3.33333S,AMP,0.08V,"
          "AMPVRMS,0.02828Vrms,MAX_OUTPUT_AMP,4.6V,OFST,-2V,HLEV,-1.96V,LLEV,-2.04V,PHSE,0")],
    ) as inst:
        inst.ch_1.wavetype = 'RAMP'
        assert inst.ch_1.wavetype == "SINE"


def test_frequency():
    """Verify the frequency setter and getter for ramp or sine wavetype."""
    with expected_protocol(
        TeledyneT3AFG,
        [("C1:BSWV FRQ,1000", None),
         ("SYST:ERR?", "-0, No errors"),
         ("C1:BSWV?", "C1:BSWV WVTP,SINE,FRQ,0.3HZ,PERI,3.33333S,AMP,0.08V,"
          "AMPVRMS,0.02828Vrms,MAX_OUTPUT_AMP,4.6V,OFST,-2V,HLEV,-1.96V,LLEV,-2.04V,PHSE,0")],
    ) as inst:
        inst.ch_1.frequency = 1000
        assert inst.ch_1.frequency == 0.3


def test_frequency_getter_error():
    """Verify the frequency getter for DC wavetype with no frequency value."""
    with expected_protocol(
        TeledyneT3AFG,
        [("C1:BSWV?", "C1:BSWV WVTP,DC,MAX_OUT_AMP,4.6V,OFST,0V")],
    ) as inst:
        assert inst.ch_1.frequency is None


def test_amplitude():
    """Verify the amplitude setter and getter for ramp or sine wavetype."""
    with expected_protocol(
        TeledyneT3AFG,
        [("C1:BSWV AMP,1", None),
         ("SYST:ERR?", "-0, No errors"),
         ("C1:BSWV?", "C1:BSWV WVTP,SINE,FRQ,0.3HZ,PERI,3.33333S,AMP,0.08V,"
          "AMPVRMS,0.02828Vrms,MAX_OUTPUT_AMP,4.6V,OFST,-2V,HLEV,-1.96V,LLEV,-2.04V,PHSE,0")],
    ) as inst:
        inst.ch_1.amplitude = 1
        assert inst.ch_1.amplitude == 0.08


def test_offset():
    """Verify the offset setter and getter for DC wavetype."""
    with expected_protocol(
        TeledyneT3AFG,
        [("C1:BSWV OFST,1", None),
         ("SYST:ERR?", "-0, No errors"),
         ("C1:BSWV?", "C1:BSWV WVTP,DC,MAX_OUT_AMP,4.6V,OFST,0V")],
    ) as inst:
        inst.ch_1.offset = 1
        assert inst.ch_1.offset == 0
