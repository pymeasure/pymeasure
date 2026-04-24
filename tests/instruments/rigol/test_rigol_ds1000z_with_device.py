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

import pytest

from pymeasure.instruments.rigol import RigolDS1000Z


@pytest.fixture(scope="module")
def rigolDS1000Z(connected_device_address):
    instr = RigolDS1000Z(connected_device_address)
    return instr


def test_idn_responds(rigolDS1000Z: RigolDS1000Z):
    response = rigolDS1000Z.id
    assert isinstance(response, str)
    assert response
    print(f"Response: {response}")


def test_memory_depth_round_trip(rigolDS1000Z: RigolDS1000Z):
    rigolDS1000Z.memory_depth = "AUTO"
    rigolDS1000Z.memory_depth = 12_000
    assert rigolDS1000Z.memory_depth in ("AUTO", 12_000)


def test_autoscale_executes(rigolDS1000Z: RigolDS1000Z):
    rigolDS1000Z.autoscale()
