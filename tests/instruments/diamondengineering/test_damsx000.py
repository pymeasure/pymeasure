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

import pytest
from pymeasure.instruments.diamondengineering.damsx000 import (DAMSx000,DAMSx000_DFSM,
                                                               ZeroPositionNotSet)
from pymeasure.instruments.fakes import FakeAdapter


class FakeDamsx000(FakeAdapter):
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self._buffer = []

    def read(self):
        """ Returns the last commands given after the
        last read call.
        """
        result = ""

        if len(self._buffer) > 0:
            result = self._buffer.pop(0)

        """ Answer given by real device is in lower casing
        """
        return result.lower()

    def write(self, command):
        """ Writes the command to a buffer, so that it can
        be read back.
        """

        if command[0] in ('X', 'Y'):
            axis = command[0]
            command = command[1:]
        if command == ("0RN+0") or command == ("0RN-0"):
            expected_responses = [f'{axis}0!']
        if command.startswith("0RN"):
            expected_responses = [f'{axis}0b', f'{axis}0f']
        elif command.startswith("0"):
            expected_responses = [f'{axis}0>']
        else:
            expected_responses = []

        self._buffer += expected_responses

    def __repr__(self):
        return "<FakeDamsx000>"


class TestXAxis:
    """
    Unit tests for X axis movement

    """
    x = DAMSx000(FakeDamsx000()).x

    def test_zero_position_not_set(self):
        with pytest.raises(ZeroPositionNotSet):
            self.x.angle

        with pytest.raises(ZeroPositionNotSet):
            self.x.angle = 30

        self.x.angle_rel(30)

    def test_shortest_path(self):
        # Always <= 180 degrees
        for angle in range(0, 3600, 5):
            steps_180 = self.x.degrees2steps(180)
            steps_p = self.x.degrees2steps(angle)
            steps_m = self.x.degrees2steps(-angle)
            assert (abs(steps_p) <= steps_180)
            assert (abs(steps_m) <= steps_180)

    def test_step_are_reversable(self):
        for angle in range(0, 360, 5):
            steps_p = self.x.degrees2steps(angle)
            steps_m = self.x.degrees2steps(-angle)
            if (angle != 180):
                assert (steps_p == -steps_m)

    def test_angle_approx_error(self):
        self.x.set_zero()

        for angle in range(0, 360):
            self.x.angle = angle
            assert(self.x.angle == pytest.approx(angle, abs=5e-3))

    def test_zero_steps(self):
        assert (self.x.angle_rel(0) == 0)

class TestRoll:
    """
    Unit tests for Roll movement on Y axis

    """
    y = DAMSx000_DFSM(FakeDamsx000()).y

    def test_zero_position_not_set(self):
        with pytest.raises(ZeroPositionNotSet):
            self.y.angle

        with pytest.raises(ZeroPositionNotSet):
            self.y.angle = 30

        self.y.angle_rel(30)

    def test_shortest_path(self):
        # Always <= 180 degrees
        for angle in range(0, 3600, 5):
            steps_180 = self.y.degrees2steps(180)
            steps_p = self.y.degrees2steps(angle)
            steps_m = self.y.degrees2steps(-angle)
            assert (abs(steps_p) <= steps_180)
            assert (abs(steps_m) <= steps_180)

    def test_step_are_reversable(self):
        for angle in range(0, 360, 5):
            steps_p = self.y.degrees2steps(angle)
            steps_m = self.y.degrees2steps(-angle)
            if (angle != 180):
                assert (steps_p == -steps_m)

    def test_angle_approx_error(self):
        self.y.set_zero()

        for angle in range(0, 360):
            self.y.angle = angle
            assert(self.y.angle == pytest.approx(angle, abs=5e-3))

    def test_zero_steps(self):
        assert (self.y.angle_rel(0) == 0)


class TestXAxisWithRoll:
    """
        Unit tests for X axis when Roll movement is on Y axis
        with no wrapping option.
    """
    x = DAMSx000_DFSM(FakeDamsx000()).x
    x.wrap = False

    def test_zero_position_not_set(self):
        with pytest.raises(ZeroPositionNotSet):
            self.x.angle

        with pytest.raises(ZeroPositionNotSet):
            self.x.angle = 30

        self.x.angle_rel(30)

    def test_longest_path(self):
        """
            Positioner must choose longest path to reach absolute position
            (keep cables from twisting)
        """
        self.x.set_zero()
        for angle in range(-3600, 3600, 5):
            angle_wrapped = angle % 360
            angle_rel = angle_wrapped - self.x.angle
            self.x.angle = angle
            steps = self.x.degrees2steps(angle_rel)
            if (angle % 360 == 0 and angle != 0):
                assert(steps <= 0)

    def test_step_are_reversable(self):
        for angle in range(0, 360, 5):
            steps_p = self.x.degrees2steps(angle)
            steps_m = self.x.degrees2steps(-angle)
            if (angle != 180):
                assert (steps_p == -steps_m)

    def test_angle_approx_error(self):
        self.x.set_zero()

        for angle in range(0, 360):
            self.x.angle = angle
            assert(self.x.angle == pytest.approx(angle, abs=5e-3))

    def test_zero_steps(self):
        assert (self.x.angle_rel(0) == 0)


class TestYAxis:
    """
    Unit tests for Y axis movement

    """

    lookup_table = {
        -45: 13575,
        -44: 13279,
        -43: 12981,
        -42: 12682,
        -41: 12380,
        -40: 12077,
        -39: 11773,
        -38: 11468,
        -37: 11161,
        -36: 10854,
        -35: 10546,
        -34: 10237,
        -33: 9928,
        -32: 9618,
        -31: 9308,
        -30: 8998,
        -29: 8688,
        -28: 8379,
        -27: 8069,
        -26: 7759,
        -25: 7450,
        -24: 7141,
        -23: 6833,
        -22: 6525,
        -21: 6218,
        -20: 5911,
        -19: 5606,
        -18: 5301,
        -17: 4996,
        -16: 4693,
        -15: 4391,
        -14: 4089,
        -13: 3789,
        -12: 3490,
        -11: 3192,
        -10: 2895,
        -9: 2599,
        -8: 2305,
        -7: 2012,
        -6: 1720,
        -5: 1430,
        -4: 1141,
        -3: 853,
        -2: 567,
        -1: 283,
        0: 0,
        1: -281,
        2: -561,
        3: -839,
        4: -1115,
        5: -1389,
        6: -1662,
        7: -1933,
        8: -2202,
        9: -2469,
        10: -2735,
        11: -2998,
        12: -3260,
        13: -3519,
        14: -3777,
        15: -4032,
        16: -4286,
        17: -4537,
        18: -4786,
        19: -5034,
        20: -5279,
        21: -5522,
        22: -5762,
        23: -6001,
        24: -6237,
        25: -6471,
        26: -6703,
        27: -6932,
        28: -7159,
        29: -7384,
        30: -7606,
        31: -7826,
        32: -8044,
        33: -8259,
        34: -8472,
        35: -8682,
        36: -8890,
        37: -9095,
        38: -9298,
        39: -9498,
        40: -9696,
        41: -9891,
        42: -10083,
        43: -10273,
        44: -10460,
        45: -10645,
    }

    y = DAMSx000(FakeDamsx000()).y

    def test_zero_position_not_set(self):
        with pytest.raises(ZeroPositionNotSet):
            self.y.angle

        with pytest.raises(ZeroPositionNotSet):
            self.y.angle = 30

        self.y.angle_rel(30)

    def test_limits(self):
        with pytest.raises(AssertionError):
            self.y.angle_rel(46)

        with pytest.raises(AssertionError):
            self.y.angle_rel(-46)

        self.y.set_zero()

        with pytest.raises(AssertionError):
            self.y.angle = -46

        with pytest.raises(AssertionError):
            self.y.angle = 46

    def test_angle_approx_error(self):
        self.y.set_zero()
        for angle in range(-45, 45):
            self.y.angle = angle
            assert(self.y.angle == pytest.approx(angle, abs=5e-3))

    def test_step_are_reversable(self):
        for angle in range(-45, 46, 1):
            self.y.set_zero()
            steps_p = self.y.degrees2steps(angle)
            self.y.angle = angle
            steps_m = self.y.degrees2steps(-angle)
            assert (steps_p == pytest.approx(-steps_m, abs=1))

    def test_steps_accuracy(self):
        self.y.set_zero()
        for angle in range(-45, 46, 1):
            steps = self.y.degrees2steps(angle)
            assert (steps == self.lookup_table[angle])

    def test_zero_steps(self):
        assert (self.y.angle_rel(0) == 0)


class TestDAMSx000:
    def test_init(self):
        dams = DAMSx000(FakeDamsx000())
        dams.elevation_rel(30)
        dams.azimuth_rel(30)
        dams.set_zero_position()
        dams.elevation = 0
