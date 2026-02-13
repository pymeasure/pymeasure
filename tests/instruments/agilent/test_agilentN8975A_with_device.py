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

# Call signature:
# $ pytest test_agilentN8975A_with_device.py --device-address "GPIB0::18::INSTR"
# The given device address is just an examples. Please exchanged it with your own.

# Requirements for the NFA:
# Connect a SNS noise source to the NFA input


import pytest
from pymeasure.instruments.agilent.agilentN8975A import AgilentN8975A


@pytest.fixture(scope="module")
def n8975a(connected_device_address,
           timeout=30000,
           ):
    instr = AgilentN8975A(connected_device_address, timeout=timeout)
    instr.reset()
    instr.clear()
    assert [] == instr.check_errors()
    return instr


@pytest.fixture(scope="module")
def n8975a_fixed(n8975a):
    n8975a.frequency.mode = "fixed"
    n8975a.clear()
    assert [] == n8975a.check_errors()
    return n8975a


@pytest.fixture(scope="module")
def n8975a_list(n8975a):
    n8975a.frequency.mode = "list"
    n8975a.clear()
    assert [] == n8975a.check_errors()
    return n8975a


@pytest.fixture(scope="module")
def n8975a_sweep(n8975a):
    n8975a.frequency.mode = "sweep"
    n8975a.clear()
    assert [] == n8975a.check_errors()
    return n8975a


class TestMain:
    def test_abort(self, n8975a):
        n8975a.abort()
        assert [] == n8975a.check_errors()

    @pytest.mark.parametrize("average", [999, 1])
    def test_average(self, n8975a, average):
        n8975a.average = average
        assert average == n8975a.average
        assert [] == n8975a.check_errors()

    @pytest.mark.parametrize("average_enabled", [True, False])
    def test_average_enabled(self, n8975a, average_enabled):
        n8975a.average_enabled = average_enabled
        assert average_enabled == n8975a.average_enabled
        assert [] == n8975a.check_errors()

    @pytest.mark.parametrize("bandwidth", [100e3, 200e3, 400e3, 1e6, 2e6, 4e6])
    def test_bandwidth(self, n8975a, bandwidth):
        n8975a.bandwidth = bandwidth
        assert bandwidth == n8975a.bandwidth
        assert [] == n8975a.check_errors()

    @pytest.mark.parametrize("continuous_mode_enabled", [True, False])
    def test_continuous_mode_enabled(self, n8975a, continuous_mode_enabled):
        n8975a.continuous_mode_enabled = continuous_mode_enabled
        assert continuous_mode_enabled == n8975a.continuous_mode_enabled
        assert [] == n8975a.check_errors()


class TestFixedMode:
    def test_mode(self, n8975a_fixed):
        assert "fixed" == n8975a_fixed.frequency.mode
        assert [] == n8975a_fixed.check_errors()

    def test_fixed_value(self, n8975a_fixed):
        n8975a_fixed.frequency.fixed_value = 10e9
        assert 10e9 == n8975a_fixed.frequency.fixed_value
        assert [] == n8975a_fixed.check_errors()

    def test_calibrate(self, n8975a_fixed):
        n8975a_fixed.bandwidth = 4e6  # highest bandwidth for fast execution
        assert [] == n8975a_fixed.check_errors()
        n8975a_fixed.calibrate()
        n8975a_fixed.complete

    def test_single(self, n8975a_fixed):
        n8975a_fixed.single()
        assert [] == n8975a_fixed.check_errors()

    def test_noise_figure(self, n8975a_fixed):
        nf = n8975a_fixed.noise_figure
        assert [] == n8975a_fixed.check_errors()
        assert list is type(nf)
        assert 1 == len(nf)

    def test_gain(self, n8975a_fixed):
        gain = n8975a_fixed.gain
        assert [] == n8975a_fixed.check_errors()
        assert list is type(gain)
        assert 1 == len(gain)


class TestListMode:
    def test_mode(self, n8975a_list):
        assert "list" == n8975a_list.frequency.mode
        assert [] == n8975a_list.check_errors()

    def test_list_data(self, n8975a_list):
        n8975a_list.frequency.list_data = [1e9, 21.35e9]
        assert [1e9, 21.35e9] == n8975a_list.frequency.list_data
        assert [] == n8975a_list.check_errors()

    def number_of_entries(self, n8975a_list):
        assert 2 == n8975a_list.frequency.number_of_entries
        assert [] == n8975a_list.check_errors()

    def test_calibrate(self, n8975a_list):
        n8975a_list.bandwidth = 4e6  # highest bandwidth for fast execution
        assert [] == n8975a_list.check_errors()
        n8975a_list.calibrate()
        n8975a_list.complete

    def test_single(self, n8975a_list):
        n8975a_list.single()
        assert [] == n8975a_list.check_errors()

    def test_noise_figure(self, n8975a_list):
        nf = n8975a_list.noise_figure
        assert [] == n8975a_list.check_errors()
        assert list is type(nf)
        assert 2 == len(nf)

    def test_gain(self, n8975a_list):
        gain = n8975a_list.gain
        assert [] == n8975a_list.check_errors()
        assert list is type(gain)
        assert 2 == len(gain)


class TestSweepMode:
    def test_mode(self, n8975a_sweep):
        assert "sweep" == n8975a_sweep.frequency.mode
        assert [] == n8975a_sweep.check_errors()

    def test_start_frequency(self, n8975a_sweep):
        n8975a_sweep.frequency.start_frequency = 3e9
        assert 3e9 == n8975a_sweep.frequency.start_frequency
        assert [] == n8975a_sweep.check_errors()

    def test_stop_frequency(self, n8975a_sweep):
        n8975a_sweep.frequency.stop_frequency = 5.5e9
        assert 5.5e9 == n8975a_sweep.frequency.stop_frequency
        assert [] == n8975a_sweep.check_errors()

    def test_number_of_points(self, n8975a_sweep):
        n8975a_sweep.frequency.number_of_points = 3
        assert 3 == n8975a_sweep.frequency.number_of_points
        assert [] == n8975a_sweep.check_errors()

    def test_calibrate(self, n8975a_sweep):
        n8975a_sweep.bandwidth = 4e6  # highest bandwidth for fast execution
        assert [] == n8975a_sweep.check_errors()
        n8975a_sweep.calibrate()
        n8975a_sweep.complete

    def test_single(self, n8975a_sweep):
        n8975a_sweep.single()
        assert [] == n8975a_sweep.check_errors()

    def test_noise_figure(self, n8975a_sweep):
        nf = n8975a_sweep.noise_figure
        assert [] == n8975a_sweep.check_errors()
        assert list is type(nf)
        assert 3 == len(nf)

    def test_gain(self, n8975a_sweep):
        gain = n8975a_sweep.gain
        assert [] == n8975a_sweep.check_errors()
        assert list is type(gain)
        assert 3 == len(gain)
