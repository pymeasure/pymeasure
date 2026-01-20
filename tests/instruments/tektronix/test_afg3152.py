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
from pymeasure.instruments.tektronix.afg3152c import AFG3152C


def test_shape():
    # Demonstrate message prefix identifying the channel
    # Note how the implementation of the shape property does not show that
    # prefix (it is added in the Channel class)
    with expected_protocol(
        AFG3152C,
        [("source1:function:shape?", "LOR"),
         ("source2:function:shape HAV", None),
         ],
    ) as inst:
        assert inst.ch1.shape == 'lorentz'
        inst.ch2.shape = 'haversine'


def test_beep():
    # A message common to all channels does not have a prefix
    with expected_protocol(
        AFG3152C,
        [("system:beep", None)],
    ) as inst:
        inst.beep()
