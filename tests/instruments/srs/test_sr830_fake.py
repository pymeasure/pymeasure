#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
import time
from unittest import mock

from math import sqrt

from pymeasure.instruments.srs import FakeSR830Adapter, FakeSR830DUT

class TestDUT:
    def test_dut_fmax_is_3db(self):
        d = FakeSR830DUT(fmin=5, fmax=1024)
        d.configure(frequency=1024, tau=10e-6)
        time.sleep(0.01)
        assert 0.99/sqrt(2) <= d.r() <= 1.01*sqrt(2)
        assert -90*1.01 <= d.theta() <= -90*0.99

    def test_dut_fmin_is_3db(self):
        d = FakeSR830DUT(fmin=5, fmax=1024)
        d.configure(frequency=5, tau=10e-6)
        time.sleep(0.01)
        assert 0.99/sqrt(2) <= d.r() <= 1.01*sqrt(2)
        assert 90*0.99 <= d.theta() <= 90*1.01

    def test_dut_midband_unity_gain(self):
        d = FakeSR830DUT(fmin=1, fmax=10000)
        d.configure(frequency=100, tau=10e-6)
        time.sleep(0.01)
        assert 0.999 <= d.r() <= 1.001
        assert -0.001 <= d.theta() <= 0.001

    def test_dut_initial_value(self):
        d = FakeSR830DUT(fmin=1, fmax=10000)
        d.configure(frequency=1, tau=10)
        assert abs(d.r()) <= 0.1
        assert 89.9 <= d.theta() <= 90.1

    def test_dut_transient(self):
        d = FakeSR830DUT(fmin=1, fmax=10000)

        r = []
        t = []

        d.configure(frequency=1, tau=10e-3)

        for _ in range(0, 100):
            r.append(d.r())
            t.append(d.theta())
            time.sleep(0.001)

        assert max(r) > 1.05/sqrt(2) # overshoots
        assert min(t) < 85 # undershoots

    def test_dut_larger_tau_should_have_longer_transient(self):
        d1 = FakeSR830DUT(fmin=1, fmax=10000)

        r1 = []
        t1 = []

        d1.configure(frequency=1, tau=10e-3)
        for _ in range(0, 100):
            r1.append(d1.r())
            t1.append(d1.theta())
            time.sleep(0.001)

        d2 = FakeSR830DUT(fmin=1, fmax=10000)

        r2 = []
        t2 = []

        d2.configure(frequency=1, tau=30e-3)
        for _ in range(0, 100):
            r2.append(d2.r())
            t2.append(d2.theta())
            time.sleep(0.001)

        assert r2.index(max(r2)) > r1.index(max(r1))
        assert t2.index(min(t2)) > t1.index(min(t1))

    def test_dut_multiple_configures_should_converge(self):
        d = FakeSR830DUT(fmin=1, fmax=10000)

        r = []
        t = []

        d.configure(frequency=1, tau=3e-3)
        time.sleep(0.1)

        d.configure(frequency=10000, tau=3e-3)
        time.sleep(0.1)

        assert 0.99/sqrt(2) <= d.r() <= 1.01*sqrt(2)
        assert -90*1.01 <= d.theta() <= -90*0.99


class TestFakeSR830:
    def test_freq_write_read(self):
        dut = mock.Mock()
        a = FakeSR830Adapter(dut)
        a._tau = 0  # to check dut.configure call
        a.write('FREQ 123.4')
        dut.configure.assert_called_with(123.4, 0)
        assert a.ask('FREQ?') == '123.4\n'

    def test_tau_write_read(self):
        dut = mock.Mock()
        a = FakeSR830Adapter(dut)
        a._freq = 0  # to check dut.configure call
        a.write('OFLT 2')
        dut.configure.assert_called_with(0, 100e-6)
        assert a.ask('OFLT?') == '2\n'

    def test_meas_x(self):
        dut = mock.Mock()
        dut.r.return_value = 0.5
        dut.theta.return_value = 30

        a = FakeSR830Adapter(dut)
        assert 0.433012 <= float(a.ask('OUTP? 1').strip()) <= 0.433013
        assert 0.249999 <= float(a.ask('OUTP? 2').strip()) <= 0.250000
        assert float(a.ask('OUTP? 3').strip()) == 0.5
        assert float(a.ask('OUTP? 4').strip()) == 30.0
