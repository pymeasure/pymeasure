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

# Call signature:
# $ pytest test_formfactorVelox_with_device.py --device-address "GPIB0::28::INSTR"
# Replace "GPIB0::28::INSTR" with your own device address.

#############################################
#          !!! ATTENTION !!!
# MAKE SURE THE WAFER PROBER IS CLEAR.
# THE TEST MOVES THE CHUCK TO CONTACT HEIGHT!
#############################################

import pytest
from time import sleep

from pymeasure.instruments.formfactor.velox import Velox


@pytest.fixture(scope="module")
def prober(connected_device_address,
           timeout=20000,
           ):
    instr = Velox(connected_device_address)
    instr.reset()
    instr.clear()
    return instr


class TestChuck:
    def test_move_contact(self, prober):
        assert "OK" == prober.chuck.move_contact()
        sleep(0.5)

    def test_move_align(self, prober):
        assert "OK" == prober.chuck.move_align(10)
        sleep(0.5)

    def test_move_separation(self, prober):
        assert "OK" == prober.chuck.move_separation()
        sleep(0.5)

    def test_index(self, prober):
        initial_index = tuple(prober.chuck.index)
        prober.chuck.index = (15000, 5000)
        assert [15000, 5000] == prober.chuck.index
        sleep(1)
        prober.chuck.index = initial_index

    def test_move_index(self, prober):
        assert "OK" == prober.chuck.move_index(0, 0, "center")
        sleep(0.5)

    def test_move(self, prober):
        assert "OK" == prober.chuck.move(100, 500, "relative")
        sleep(0.5)


class TestWafermap:
    def test_step_first_die(self, prober):
        if not prober.wafermap.enabled:
            pytest.skip("WaferMap module not loaded.")
        got = prober.wafermap.step_first_die()
        assert list is type(got)
        assert 4 == len(got)
        sleep(0.5)

    def test_step_next_die(self, prober):
        if not prober.wafermap.enabled:
            pytest.skip("WaferMap module not loaded.")
        got = prober.wafermap.step_next_die()
        assert list is type(got)
        assert 4 == len(got)

        sleep(0.5)


class TestVelox:
    def test_check_errors(self, prober):
        try:
            prober.ask("unknown_command")
        except ConnectionError:
            assert 509 == prober.error_code

    def test_id(self, prober):
        idn = prober.id
        assert type(idn) is str
        assert "Velox" in idn

    def test_version(self, prober):
        version = prober.version
        assert type(version) is str

    def test_options(self, prober):
        with pytest.raises(NotImplementedError):
            prober.options
