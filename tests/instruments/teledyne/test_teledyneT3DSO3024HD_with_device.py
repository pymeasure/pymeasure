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

import time

import pytest

from pymeasure.instruments.teledyne.teledyneT3DSO3024HD import TeledyneT3DSO3024HD


@pytest.fixture(scope="module")
def teledyneT3DSO3024HD(connected_device_address):
    instr = TeledyneT3DSO3024HD(connected_device_address)
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
    @pytest.mark.parametrize("high_impedance_enabled", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_high_impedance_enabled(self, reseted_teledyneT3DSO3024HD, channel,
                                    high_impedance_enabled):
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.high_impedance_enabled = high_impedance_enabled
        assert channel_obj.high_impedance_enabled == high_impedance_enabled


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
        time.sleep(0.1)
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


class TestAcquisitionRateMode:
    @pytest.mark.parametrize("acquisition_rate_mode_value", ["FAST", "SLOW"])
    def test_acquisition_rate_mode(self, reseted_teledyneT3DSO3024HD, acquisition_rate_mode_value):
        reseted_teledyneT3DSO3024HD.acquisition_rate_mode = acquisition_rate_mode_value
        assert reseted_teledyneT3DSO3024HD.acquisition_rate_mode == acquisition_rate_mode_value


class TestInterpolation:
    @pytest.mark.parametrize("interpolation_value", [True, False])
    def test_interpolation(self, reseted_teledyneT3DSO3024HD, interpolation_value):
        reseted_teledyneT3DSO3024HD.interpolation = interpolation_value
        assert reseted_teledyneT3DSO3024HD.interpolation == interpolation_value


class TestMode:
    @pytest.mark.parametrize("mode_value", ["YT", "XY", "ROLL"])
    def test_mode(self, reseted_teledyneT3DSO3024HD, mode_value):
        reseted_teledyneT3DSO3024HD.mode = mode_value
        assert reseted_teledyneT3DSO3024HD.mode == mode_value

    # (memory_depth_value, timebase_scale_value, expected_sample_rate)
    MEMORY_DEPTH_TIMEBASE_TABLE = [
        (2e3, 5e-8, 2e9),
        (10e3, 5e-7, 2e9),
        (20e3, 5e-7, 4e9),
        (100e3, 5e-6, 2e9),
        (200e3, 5e-6, 4e9),
        (1e6, 5e-5, 2e9),
        (2e6, 5e-5, 4e9),
        (10e6, 5e-4, 2e9),
        (20e6, 5e-4, 4e9),
        (100e6, 5e-3, 2e9),
        (200e6, 5e-3, 4e9),
        (400e6, 1e-2, 4e9),
    ]

    @pytest.mark.parametrize(
        "memory_depth_value, timebase_scale_value, expected_sample_rate",
        MEMORY_DEPTH_TIMEBASE_TABLE,
        ids=[f"depth={d:g}_tdiv={t:g}" for d, t, _ in MEMORY_DEPTH_TIMEBASE_TABLE],
    )
    def test_memory_depth_single(self, reseted_teledyneT3DSO3024HD, memory_depth_value,
                                  timebase_scale_value, expected_sample_rate):
        reseted_teledyneT3DSO3024HD.acquisition_type = "NORMAL"
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_2.switch = False
        reseted_teledyneT3DSO3024HD.channel_3.switch = False
        reseted_teledyneT3DSO3024HD.channel_4.switch = False

        reseted_teledyneT3DSO3024HD.timebase_scale = timebase_scale_value
        reseted_teledyneT3DSO3024HD.memory_depth = memory_depth_value

        assert reseted_teledyneT3DSO3024HD.memory_depth == memory_depth_value
        # informational cross-check: confirms we landed on the intended
        # sample rate rather than some other clamped combination that
        # happens to also report the right memory_depth.
        assert reseted_teledyneT3DSO3024HD.sample_rate == pytest.approx(
            expected_sample_rate, rel=0.01
        )


class TestMemoryDepthDual:
    @pytest.mark.parametrize(
        "memory_depth_value", [2e3, 10e3, 20e3, 100e3, 200e3,  1e6, 2e6, 10e6, 20e6, 100e6, 200e6])
    def test_memory_depth_dual(self, reseted_teledyneT3DSO3024HD, memory_depth_value):
        reseted_teledyneT3DSO3024HD.acquisition_type = "NORMAL"
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_2.switch = False
        reseted_teledyneT3DSO3024HD.channel_3.switch = True
        reseted_teledyneT3DSO3024HD.channel_4.switch = False
        reseted_teledyneT3DSO3024HD.memory_depth = memory_depth_value
        assert reseted_teledyneT3DSO3024HD.memory_depth == memory_depth_value


class TestMemoryDepthQuad:
    @pytest.mark.parametrize(
        "memory_depth_value", [1e3, 5e3, 10e3, 50e3, 100e3, 500e3, 1e6, 5e6, 10e6, 50e6, 100e6])
    def test_memory_depth_quad(self, reseted_teledyneT3DSO3024HD, memory_depth_value):
        reseted_teledyneT3DSO3024HD.acquisition_type = "NORMAL"
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_2.switch = True
        reseted_teledyneT3DSO3024HD.channel_3.switch = False
        reseted_teledyneT3DSO3024HD.channel_4.switch = False
        reseted_teledyneT3DSO3024HD.memory_depth = memory_depth_value
        assert reseted_teledyneT3DSO3024HD.memory_depth == memory_depth_value


class TestSequence:
    @pytest.mark.parametrize("sequence_value", [True, False])
    def test_sequence(self, reseted_teledyneT3DSO3024HD, sequence_value):
        reseted_teledyneT3DSO3024HD.sequence = sequence_value
        assert reseted_teledyneT3DSO3024HD.sequence == sequence_value


class TestSequenceCount:
    @pytest.mark.parametrize("sequence_count_value", [5, 3])
    def test_sequence_count(self, reseted_teledyneT3DSO3024HD, sequence_count_value):
        reseted_teledyneT3DSO3024HD.sequence_count = sequence_count_value
        assert reseted_teledyneT3DSO3024HD.sequence_count == sequence_count_value


class TestAcquisitionTypeNormal:
    def test_acquisition_type_normal(self, reseted_teledyneT3DSO3024HD):
       reseted_teledyneT3DSO3024HD.acquisition_type = "NORMAL"
       assert reseted_teledyneT3DSO3024HD.acquisition_type == "NORMAL"


class TestAcquisitionTypePeak:
    def test_acquisition_type_peak(self, reseted_teledyneT3DSO3024HD):
       reseted_teledyneT3DSO3024HD.acquisition_type = "PEAK"
       assert reseted_teledyneT3DSO3024HD.acquisition_type == "PEAK"


class TestAcquisitionTypeAverage:
    @pytest.mark.parametrize("acquisition_type_average_value", [4, 16, 32, 64, 128, 256, 512, 1024])
    def test_acquisition_type_peak(self, reseted_teledyneT3DSO3024HD,
                                    acquisition_type_average_value):
       reseted_teledyneT3DSO3024HD.acquisition_type = ("AVERAGE", acquisition_type_average_value)
       assert reseted_teledyneT3DSO3024HD.acquisition_type == ("AVERAGE",
                                                               acquisition_type_average_value)


class TestAcquisitionTypeEres:
    @pytest.mark.parametrize("acquisition_type_eres_value", [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    def test_acquisition_type_peak(self, reseted_teledyneT3DSO3024HD,
                                    acquisition_type_eres_value):
       reseted_teledyneT3DSO3024HD.acquisition_type = ("ERES", acquisition_type_eres_value)
       assert reseted_teledyneT3DSO3024HD.acquisition_type == ("ERES",
                                                               acquisition_type_eres_value)


class TestTimebaseScale:
    @pytest.mark.parametrize(
        "timebase_scale_value", [5e-8, 5e-7, 5e-6, 5e-5, 5e-4, 5e-3, 5e-2, 1e-1]
    )
    def test_timebase_scale(self, reseted_teledyneT3DSO3024HD, timebase_scale_value):
        reseted_teledyneT3DSO3024HD.timebase_scale = timebase_scale_value
        assert reseted_teledyneT3DSO3024HD.timebase_scale == pytest.approx(
            timebase_scale_value, rel=1e-3)


class TestTimebaseDelay:
    # the legal range depends on the current timebase_scale: [-5 * scale, 5 * scale]
    @pytest.mark.parametrize("timebase_scale_value", [5e-7, 5e-6, 5e-5])
    @pytest.mark.parametrize("delay_factor", [-5, -1, 0, 5])
    def test_timebase_delay(self, reseted_teledyneT3DSO3024HD, timebase_scale_value,
                             delay_factor):
        reseted_teledyneT3DSO3024HD.timebase_scale = timebase_scale_value
        delay_value = delay_factor * timebase_scale_value
        reseted_teledyneT3DSO3024HD.timebase_delay = delay_value
        assert reseted_teledyneT3DSO3024HD.timebase_delay == pytest.approx(
            delay_value, rel=1e-3
        )
