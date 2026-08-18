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


@pytest.fixture(scope="class")
def reseted_teledyneT3DSO3024HD(teledyneT3DSO3024HD):
    teledyneT3DSO3024HD.reset()
    instr = teledyneT3DSO3024HD
    return instr


def test_id(teledyneT3DSO3024HD):
    expected = "Teledyne Test Tools,T3DSO3024HD"
    res = teledyneT3DSO3024HD.id
    assert expected in res


class TestSetBwLimit:
    @pytest.mark.parametrize("bwlimit_value", ["FULL", "200M", "20M"])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_set_bw_limit(self, reseted_teledyneT3DSO3024HD, channel, bwlimit_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.bwlimit = bwlimit_value
        assert channel_obj.bwlimit == bwlimit_value


class TestScale:
    @pytest.mark.parametrize("scale", [500e-6, 500e-3, 1, 5, 10])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_scale(self, reseted_teledyneT3DSO3024HD, channel, scale):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.switch = True
        channel_obj.scale = scale
        assert channel_obj.scale == scale


class TestCoupling:
    @pytest.mark.parametrize("coupling_value", ["DC", "AC", "GND"])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_coupling(self, reseted_teledyneT3DSO3024HD, channel, coupling_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.coupling = coupling_value
        assert channel_obj.coupling == coupling_value


class TestImpedance:
    @pytest.mark.parametrize("impedance_value", [50.0, 1e6])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_impedance(self, reseted_teledyneT3DSO3024HD, channel, impedance_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.impedance = impedance_value
        assert channel_obj.impedance == impedance_value


class TestInvert:
    @pytest.mark.parametrize("invert_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_invert(self, reseted_teledyneT3DSO3024HD, channel, invert_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.invert = invert_value
        assert channel_obj.invert == invert_value


class TestLabel:
    @pytest.mark.parametrize("label_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_label(self, reseted_teledyneT3DSO3024HD, channel, label_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.label = label_value
        assert channel_obj.label == label_value


class TestLabelText:
    @pytest.mark.parametrize("label_text_value", ["CH_TEST", "A" * 20])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_label_text(self, reseted_teledyneT3DSO3024HD, channel, label_text_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.label_text = label_text_value
        res = channel_obj.label_text[1:-1]
        res = res.strip()
        assert res == label_text_value


class TestSkew:
    @pytest.mark.parametrize("skew_value", [-1e-7, -5e-8, 0, 5e-8, 1e-7])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_skew(self, reseted_teledyneT3DSO3024HD, channel, skew_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.skew = skew_value
        assert channel_obj.skew == skew_value


class TestSwitch:
    @pytest.mark.parametrize("switch_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_switch(self, reseted_teledyneT3DSO3024HD, channel, switch_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.switch = switch_value
        assert channel_obj.switch == switch_value


class TestOffset:
    @pytest.mark.parametrize("offset_value", [-1, -0.5, 0, 0.5, 1])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_offset(self, reseted_teledyneT3DSO3024HD, channel, offset_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.switch = True
        channel_obj.scale = 1
        channel_obj.offset = offset_value
        assert channel_obj.offset == offset_value


class TestUnit:
    @pytest.mark.parametrize("unit_value", ["V", "A"])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_unit(self, reseted_teledyneT3DSO3024HD, channel, unit_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.unit = unit_value
        assert channel_obj.unit == unit_value


class TestProbe:
    @pytest.mark.parametrize("probe_value", [1e-6, 1, 10, 100, 1e6])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_probe(self, reseted_teledyneT3DSO3024HD, channel, probe_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.probe = probe_value
        assert channel_obj.probe == probe_value


class TestVisible:
    @pytest.mark.parametrize("visible_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_visible(self, reseted_teledyneT3DSO3024HD, channel, visible_value):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.visible = visible_value
        assert channel_obj.visible == visible_value
