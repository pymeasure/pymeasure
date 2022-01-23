#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

from time import sleep
import logging

import pytest
from pymeasure.instruments.diamondengineering.damsx000 import DAMSx000, XAxis, YAxis, ZeroPositionNotSet
from pymeasure.instruments.instrument import FakeInstrument, FakeAdapter

class TestXAxis:
    """
    Unit tests for X axis movement

    """
    x = XAxis(FakeInstrument("DummyPort"))
    
    def test_failures(self):
        with pytest.raises(ZeroPositionNotSet):
            angle = self.x.angle

        with pytest.raises(ZeroPositionNotSet):
            self.x.angle = 30

        self.x.angle_rel = 30

        self.x.set_zero()

        for angle in range(-1000, 1000):
            self.x.angle = angle
            assert(self.x.angle == pytest.approx(angle,abs=5e-3))

class TestYAxis:
    """
    Unit tests for Y axis movement

    """

    y = YAxis(FakeInstrument("DummyPort"))
    
    def test_failures(self):
        with pytest.raises(ZeroPositionNotSet):
            angle = self.y.angle

        with pytest.raises(ZeroPositionNotSet):
            self.y.angle = 30

        self.y.angle_rel(30)

        with pytest.raises(AssertionError):
            self.y.angle_rel(46)

        with pytest.raises(AssertionError):
            self.y.angle_rel(-46)

        self.y.angle_rel(-45)

        self.y.set_zero()

        assert(self.y.angle == 0)

        with pytest.raises(AssertionError):
            self.y.angle = 46

        for angle in range(-45, 45):
            self.y.angle = angle
            assert(self.y.angle == pytest.approx(angle,abs=5e-3))
            
            


class TestDAMSx000:
    def test_init(self):
        adapter= YAxis(FakeAdapter("DummyPort"))
        dams = DAMSx000(adapter)
        dams.elevation_rel(30)
        dams.azimuth_rel(30)
        dams.set_zero_position()
        dams.elevation
