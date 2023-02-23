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

from time import sleep

from pymeasure.instruments.teledyne import TeledyneHDO6xxx


class TestTeledyneHDO6xxx:
    """
    Unit tests for TeledyneHDO6xxx class.

    This test suite, needs the following setup to work properly:
        - A TeledyneHDO6xxx device should be connected to the computer;
        - The device's address must be set in the RESOURCE constant;
        - A probe on Channel 1 must be connected to the Demo output of the oscilloscope.
    """

    ############
    # FIXTURES #
    ############

    @pytest.fixture(scope="module")
    def instrument(self, connected_device_address):
        return TeledyneHDO6xxx(connected_device_address)

    #########
    # TESTS #
    #########

    def test_instrument_connection(self, connected_device_address):
        instrument = TeledyneHDO6xxx(connected_device_address)
        channel = instrument.ch(1)
        return

    def test_channel_autoset(self, instrument):
        instrument.ch(1).autoscale()
        sleep(0.1)

    def test_channel_measure_parameter(self, instrument):
        instrument.ch(1).measure_parameter("RMS")
        sleep(0.1)
