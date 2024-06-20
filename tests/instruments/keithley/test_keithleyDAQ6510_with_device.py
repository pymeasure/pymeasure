#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
import logging
from pymeasure.instruments.keithley import KeithleyDAQ6510

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


@pytest.fixture(scope="module")
def daq6510(connected_device_address):
    instr = KeithleyDAQ6510(connected_device_address)
    instr.adapter.connection.timeout = 10000
    return instr


@pytest.fixture
def reset_daq(daq6510):
    daq6510.clear()
    daq6510.reset()
    return daq6510


def test_correct_model_by_idn(reset_daq):
    assert "6510" in reset_daq.id.lower()


def test_beep(reset_daq):
    reset_daq.beep(440, 0.1)
    assert len(reset_daq.check_errors()) == 0


def test_mux(reset_daq):
    assert reset_daq.use_mux()


def test_rear(reset_daq):
    assert reset_daq.ask(":ROUT:TERM?") == "REAR\n"
