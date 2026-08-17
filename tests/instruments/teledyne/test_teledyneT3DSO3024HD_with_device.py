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

import pytest

from pymeasure.instruments.teledyne.teledyneT3DSO3024HD import T3DSO3024HD


@pytest.fixture(scope="module")
def teledyneT3DSO3024HD(connected_device_address):
    instr = T3DSO3024HD(connected_device_address)
    return instr


@pytest.fixture()
def reseted_teledyneT3DSO3024HD(teledyneT3DSO3024HD):
    teledyneT3DSO3024HD.reset()
    instr = teledyneT3DSO3024HD
    return instr


def test_id(teledyneT3DSO3024HD):
    expected = "Teledyne Test Tools,T3DSO3024HD"
    res = teledyneT3DSO3024HD.id
    assert expected in res


@pytest.mark.parametrize("bwlimit_value", ["FULL", "200M", "20M"])
@pytest.mark.parametrize("channel", [1, 2, 3, 4])
def test_set_bw_limit(reseted_teledyneT3DSO3024HD, channel, bwlimit_value):
    channel_attr_name = f"channel_{channel}"
    channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
    channel_obj.bwlimit = bwlimit_value
    assert channel_obj.bwlimit == bwlimit_value


@pytest.mark.parametrize("scale", [500e-6, 500e-3, 1, 5, 10])
@pytest.mark.parametrize("channel", [1, 2, 3, 4])
def test_scale(teledyneT3DSO3024HD, channel, scale):
    channel_attr_name = f"channel_{channel}"
    channel_obj = getattr(teledyneT3DSO3024HD, channel_attr_name)
    channel_obj.scale = scale
    assert channel_obj.scale == scale
