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
    """Return a :class:`TeledyneT3DSO3024HD` instance connected to the configured test device."""
    instr = TeledyneT3DSO3024HD(connected_device_address)
    return instr


@pytest.fixture(scope="class")
def reseted_teledyneT3DSO3024HD(teledyneT3DSO3024HD):
    """Return the shared instrument fixture after issuing a ``*RST`` reset."""
    teledyneT3DSO3024HD.reset()
    instr = teledyneT3DSO3024HD
    return instr


def test_id(teledyneT3DSO3024HD):
    """Verify that :attr:`id` can be set and read back correctly."""
    expected = "Teledyne Test Tools,T3DSO3024HD"
    res = teledyneT3DSO3024HD.id
    assert expected in res


class TestSetBwLimit:
    @pytest.mark.parametrize("bwlimit_value", ["FULL", "200M", "20M"])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_set_bw_limit(self, reseted_teledyneT3DSO3024HD, channel, bwlimit_value):
        """[TestSetBwLimit] Verify that :attr:`bwlimit` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.bwlimit = bwlimit_value
        assert channel_obj.bwlimit == bwlimit_value


class TestScale:
    @pytest.mark.parametrize("scale", [500e-6, 500e-3, 1, 5, 10])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_scale(self, reseted_teledyneT3DSO3024HD, channel, scale):
        """[TestScale] Verify that :attr:`switch` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.switch = True
        channel_obj.scale = scale
        assert channel_obj.scale == scale


class TestCoupling:
    @pytest.mark.parametrize("coupling_value", ["DC", "AC", "GND"])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_coupling(self, reseted_teledyneT3DSO3024HD, channel, coupling_value):
        """[TestCoupling] Verify that :attr:`coupling` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.coupling = coupling_value
        assert channel_obj.coupling == coupling_value


class TestImpedance:
    @pytest.mark.parametrize("high_impedance_enabled", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_high_impedance_enabled(self, reseted_teledyneT3DSO3024HD, channel,
                                    high_impedance_enabled):
        """[TestImpedance] Verify that :attr:`high_impedance_enabled` can be set
        and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.high_impedance_enabled = high_impedance_enabled
        assert channel_obj.high_impedance_enabled == high_impedance_enabled


class TestInvert:
    @pytest.mark.parametrize("invert_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_invert(self, reseted_teledyneT3DSO3024HD, channel, invert_value):
        """[TestInvert] Verify that :attr:`invert` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.invert = invert_value
        assert channel_obj.invert == invert_value


class TestLabel:
    @pytest.mark.parametrize("label_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_label(self, reseted_teledyneT3DSO3024HD, channel, label_value):
        """[TestLabel] Verify that :attr:`label` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.label = label_value
        assert channel_obj.label == label_value


class TestLabelText:
    @pytest.mark.parametrize("label_text_value", ["CH_TEST", "A" * 20])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_label_text(self, reseted_teledyneT3DSO3024HD, channel, label_text_value):
        """[TestLabelText] Verify that :attr:`label_text` can be set and read back correctly."""
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
        """[TestSkew] Verify that :attr:`skew` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.skew = skew_value
        time.sleep(0.1)
        assert channel_obj.skew == skew_value


class TestSwitch:
    @pytest.mark.parametrize("switch_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_switch(self, reseted_teledyneT3DSO3024HD, channel, switch_value):
        """[TestSwitch] Verify that :attr:`switch` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.switch = switch_value
        assert channel_obj.switch == switch_value


class TestOffset:
    @pytest.mark.parametrize("offset_value", [-1, -0.5, 0, 0.5, 1])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_offset(self, reseted_teledyneT3DSO3024HD, channel, offset_value):
        """[TestOffset] Verify that :attr:`switch` can be set and read back correctly."""
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
        """[TestUnit] Verify that :attr:`unit` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.unit = unit_value
        assert channel_obj.unit == unit_value


class TestProbe:
    @pytest.mark.parametrize("probe_value", [1e-6, 1, 10, 100, 1e6])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_probe(self, reseted_teledyneT3DSO3024HD, channel, probe_value):
        """[TestProbe] Verify that :attr:`probe` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.probe = probe_value
        assert channel_obj.probe == probe_value


class TestVisible:
    @pytest.mark.parametrize("visible_value", [True, False])
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_visible(self, reseted_teledyneT3DSO3024HD, channel, visible_value):
        """[TestVisible] Verify that :attr:`visible` can be set and read back correctly."""
        channel_attr_name = f"channel_{channel}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.visible = visible_value
        assert channel_obj.visible == visible_value


class TestAcquisitionRateMode:
    @pytest.mark.parametrize("acquisition_rate_mode_value", ["FAST", "SLOW"])
    def test_acquisition_rate_mode(self, reseted_teledyneT3DSO3024HD, acquisition_rate_mode_value):
        """[TestAcquisitionRateMode] Verify that :attr:`acquisition_rate_mode` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.acquisition_rate_mode = acquisition_rate_mode_value
        assert reseted_teledyneT3DSO3024HD.acquisition_rate_mode == acquisition_rate_mode_value


class TestInterpolation:
    @pytest.mark.parametrize("interpolation_value", [True, False])
    def test_interpolation(self, reseted_teledyneT3DSO3024HD, interpolation_value):
        """[TestInterpolation] Verify that :attr:`interpolation` can be set and
        read back correctly."""
        reseted_teledyneT3DSO3024HD.interpolation = interpolation_value
        assert reseted_teledyneT3DSO3024HD.interpolation == interpolation_value


class TestMode:
    @pytest.mark.parametrize("mode_value", ["YT", "XY", "ROLL"])
    def test_mode(self, reseted_teledyneT3DSO3024HD, mode_value):
        """[TestMode] Verify that :attr:`mode` can be set and read back correctly."""
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
        """[TestMode] Verify that :attr:`acquisition_type` can be set and read back correctly."""
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
        """[TestMemoryDepthDual] Verify that :attr:`acquisition_type` can be set
        and read back correctly."""
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
        """[TestMemoryDepthQuad] Verify that :attr:`acquisition_type` can be
        set and read back correctly."""
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
        """[TestSequence] Verify that :attr:`sequence` can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.sequence = sequence_value
        assert reseted_teledyneT3DSO3024HD.sequence == sequence_value


class TestSequenceCount:
    @pytest.mark.parametrize("sequence_count_value", [5, 3])
    def test_sequence_count(self, reseted_teledyneT3DSO3024HD, sequence_count_value):
        """[TestSequenceCount] Verify that :attr:`sequence_count` can be set and
        read back correctly."""
        reseted_teledyneT3DSO3024HD.sequence_count = sequence_count_value
        assert reseted_teledyneT3DSO3024HD.sequence_count == sequence_count_value


class TestAcquisitionTypeNormal:
    def test_acquisition_type_normal(self, reseted_teledyneT3DSO3024HD):
        """[TestAcquisitionTypeNormal] Verify that :attr:`acquisition_type` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.acquisition_type = "NORMAL"
        assert reseted_teledyneT3DSO3024HD.acquisition_type == "NORMAL"


class TestAcquisitionTypePeak:
    def test_acquisition_type_peak(self, reseted_teledyneT3DSO3024HD):
        """[TestAcquisitionTypePeak] Verify that :attr:`acquisition_type` can be set and
        read back correctly."""
        reseted_teledyneT3DSO3024HD.acquisition_type = "PEAK"
        assert reseted_teledyneT3DSO3024HD.acquisition_type == "PEAK"


class TestAcquisitionTypeAverage:
    @pytest.mark.parametrize("acquisition_type_average_value", [4, 16, 32, 64, 128, 256, 512, 1024])
    def test_acquisition_type_peak(self, reseted_teledyneT3DSO3024HD,
                                    acquisition_type_average_value):
        """[TestAcquisitionTypeAverage] Verify that :attr:`acquisition_type` can be set and read
        back correctly."""
        reseted_teledyneT3DSO3024HD.acquisition_type = ("AVERAGE", acquisition_type_average_value)
        assert reseted_teledyneT3DSO3024HD.acquisition_type == ("AVERAGE",
                                                               acquisition_type_average_value)


class TestAcquisitionTypeEres:
    @pytest.mark.parametrize("acquisition_type_eres_value", [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    def test_acquisition_type_peak(self, reseted_teledyneT3DSO3024HD,
                                    acquisition_type_eres_value):
        """[TestAcquisitionTypeEres] Verify that :attr:`acquisition_type` can be set and
        read back correctly."""
        reseted_teledyneT3DSO3024HD.acquisition_type = ("ERES", acquisition_type_eres_value)
        assert reseted_teledyneT3DSO3024HD.acquisition_type == ("ERES",
                                                               acquisition_type_eres_value)


class TestTimebaseScale:
    @pytest.mark.parametrize(
        "timebase_scale_value", [5e-8, 5e-7, 5e-6, 5e-5, 5e-4, 5e-3, 5e-2, 1e-1]
    )
    def test_timebase_scale(self, reseted_teledyneT3DSO3024HD, timebase_scale_value):
        """[TestTimebaseScale] Verify that :attr:`timebase_scale` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.timebase_scale = timebase_scale_value
        assert reseted_teledyneT3DSO3024HD.timebase_scale == pytest.approx(
            timebase_scale_value, rel=1e-3)


class TestTimebaseDelay:
    # the legal range depends on the current timebase_scale: [-5 * scale, 5 * scale]
    @pytest.mark.parametrize("timebase_scale_value", [5e-7, 5e-6, 5e-5])
    @pytest.mark.parametrize("delay_factor", [-5, -1, 0, 5])
    def test_timebase_delay(self, reseted_teledyneT3DSO3024HD, timebase_scale_value,
                             delay_factor):
        """[TestTimebaseDelay] Verify that :attr:`timebase_scale` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.timebase_scale = timebase_scale_value
        delay_value = delay_factor * timebase_scale_value
        reseted_teledyneT3DSO3024HD.timebase_delay = delay_value
        assert reseted_teledyneT3DSO3024HD.timebase_delay == pytest.approx(
            delay_value, rel=1e-3
        )


class TestTimebaseWindow:
    @pytest.mark.parametrize("timebase_window_value", [True, False])
    def test_timebase_window(self, reseted_teledyneT3DSO3024HD, timebase_window_value):
        """[TestTimebaseWindow] Verify that :attr:`timebase_window` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.timebase_window = timebase_window_value
        assert reseted_teledyneT3DSO3024HD.timebase_window == timebase_window_value


class TestTimebaseWindowScale:
    def test_timebase_window_scale_within_main_scale(self, reseted_teledyneT3DSO3024HD):
        """[TestTimebaseWindowScale] Verify that :attr:`timebase_scale` can be set and
        read back correctly."""
        reseted_teledyneT3DSO3024HD.timebase_scale = 5e-3
        reseted_teledyneT3DSO3024HD.timebase_window = True
        reseted_teledyneT3DSO3024HD.timebase_window_scale = 5e-4
        assert reseted_teledyneT3DSO3024HD.timebase_window_scale == pytest.approx(
            5e-4, rel=1e-3
        )

    def test_timebase_window_scale_clamped_to_main_scale(self, reseted_teledyneT3DSO3024HD):
        """[TestTimebaseWindowScale] Verify that :attr:`timebase_scale` can be
        set and read back correctly."""
        # setting a window scale greater than the main scale must be clamped by the
        # instrument to the main window's scale rather than rejected
        reseted_teledyneT3DSO3024HD.timebase_scale = 5e-4
        reseted_teledyneT3DSO3024HD.timebase_window = True
        reseted_teledyneT3DSO3024HD.timebase_window_scale = 5e-3
        assert reseted_teledyneT3DSO3024HD.timebase_window_scale == pytest.approx(
            5e-4, rel=1e-3
        )


class TestTimebaseWindowDelay:
    def test_timebase_window_delay_within_range(self, reseted_teledyneT3DSO3024HD):
        """[TestTimebaseWindowDelay] Verify that :attr:`timebase_scale` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.timebase_scale = 5e-3
        reseted_teledyneT3DSO3024HD.timebase_window = True
        reseted_teledyneT3DSO3024HD.timebase_window_scale = 1e-4
        reseted_teledyneT3DSO3024HD.timebase_window_delay = 1e-4
        assert reseted_teledyneT3DSO3024HD.timebase_window_delay == pytest.approx(
            1e-4, abs=1e-9
        )

    def test_timebase_window_delay_out_of_range_is_clamped(self, reseted_teledyneT3DSO3024HD):
        """[TestTimebaseWindowDelay] Verify that assigning an invalid value to
        :attr:`timebase_scale` raises a ``ValueError``."""
        # an out-of-range value must be clamped by the instrument to the nearest
        # legal value (within the main sweep range) rather than rejected
        reseted_teledyneT3DSO3024HD.timebase_scale = 5e-6
        reseted_teledyneT3DSO3024HD.timebase_window = True
        reseted_teledyneT3DSO3024HD.timebase_window_delay = 1
        clamped = reseted_teledyneT3DSO3024HD.timebase_window_delay
        assert clamped != pytest.approx(1, rel=1e-3)


class TestTriggerMode:
    @pytest.mark.parametrize("mode_value", ["SINGLE", "NORMAL", "AUTO"])
    def test_trigger_mode(self, reseted_teledyneT3DSO3024HD, mode_value):
        """[TestTriggerMode] Verify that :attr:`trigger_mode` can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_mode = mode_value
        assert reseted_teledyneT3DSO3024HD.trigger_mode == mode_value


class TestTriggerRunStop:
    def test_trigger_run_and_stop(self, reseted_teledyneT3DSO3024HD):
        """[TestTriggerRunStop] Verify that :attr:`trigger_status` can be set and
        read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_run()
        assert reseted_teledyneT3DSO3024HD.trigger_status in (
            "Arm", "Ready", "Auto", "Trig'd", "Stop", "Roll"
        )
        reseted_teledyneT3DSO3024HD.trigger_stop()
        assert reseted_teledyneT3DSO3024HD.trigger_status == "Stop"


class TestTriggerType:
    # only EDGE is fully supported by this class (see trigger_edge_* attributes);
    # the other types are still checked here for the plain set/get round-trip
    @pytest.mark.parametrize(
        "trigger_type_value",
        ["EDGE", "PULSE", "SLOPE", "INTERVAL", "PATTERN", "RUNT", "QUALIFIED",
         "WINDOW", "DROPOUT", "VIDEO"],
    )
    def test_trigger_type(self, reseted_teledyneT3DSO3024HD, trigger_type_value):
        """[TestTriggerType] Verify that :attr:`trigger_type` can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = trigger_type_value
        assert reseted_teledyneT3DSO3024HD.trigger_type == trigger_type_value


class TestTriggerEdgeCoupling:
    @pytest.mark.parametrize("coupling_value", ["DC", "AC", "LF_REJECT", "HF_REJECT"])
    def test_trigger_edge_coupling(self, reseted_teledyneT3DSO3024HD, coupling_value):
        """[TestTriggerEdgeCoupling] Verify that :attr:`trigger_type`
        can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_coupling = coupling_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_coupling == coupling_value


class TestTriggerEdgeHoldoffEvents:
    @pytest.mark.parametrize("holdoff_events_value", [1, 5, 1000, 100000000])
    def test_trigger_edge_holdoff_events(self, reseted_teledyneT3DSO3024HD,
                                          holdoff_events_value):
        """[TestTriggerEdgeHoldoffEvents] Verify that :attr:`trigger_type`
        can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_type = "EVENTS"
        reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_events = holdoff_events_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_events == holdoff_events_value


class TestTriggerEdgeHoldoffTime:
    @pytest.mark.parametrize("holdoff_time_value", [8e-9, 1e-6, 1e-3, 1, 30])
    def test_trigger_edge_holdoff_time(self, reseted_teledyneT3DSO3024HD,
                                        holdoff_time_value):
        """[TestTriggerEdgeHoldoffTime] Verify that :attr:`trigger_type` can
        be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_type = "TIME"
        reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_time = holdoff_time_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_time == pytest.approx(
            holdoff_time_value, rel=1e-3)


class TestTriggerEdgeHoldoffType:
    @pytest.mark.parametrize("holdoff_type_value", ["OFF", "EVENTS", "TIME"])
    def test_trigger_edge_holdoff_type(self, reseted_teledyneT3DSO3024HD,
                                        holdoff_type_value):
        """[TestTriggerEdgeHoldoffType] Verify that :attr:`trigger_type`
        can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_type = holdoff_type_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_type == holdoff_type_value


class TestTriggerEdgeHoldoffStart:
    @pytest.mark.parametrize("holdoff_start_value", ["LAST_TRIG", "ACQ_START"])
    def test_trigger_edge_holdoff_start(self, reseted_teledyneT3DSO3024HD,
                                         holdoff_start_value):
        """[TestTriggerEdgeHoldoffStart] Verify that :attr:`trigger_type` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_start = holdoff_start_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_holdoff_start == holdoff_start_value


class TestTriggerEdgeNoiseReject:
    @pytest.mark.parametrize("noise_reject_value", [True, False])
    def test_trigger_edge_noise_reject(self, reseted_teledyneT3DSO3024HD,
                                        noise_reject_value):
        """[TestTriggerEdgeNoiseReject] Verify that :attr:`trigger_type` can be
        set and read back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_noise_reject = noise_reject_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_noise_reject == noise_reject_value


class TestTriggerEdgeSlope:
    @pytest.mark.parametrize("slope_value", ["RISING", "FALLING", "ALTERNATE"])
    def test_trigger_edge_slope(self, reseted_teledyneT3DSO3024HD, slope_value):
        """[TestTriggerEdgeSlope] Verify that :attr:`trigger_type` can be set and read
        back correctly."""
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_slope = slope_value
        assert reseted_teledyneT3DSO3024HD.trigger_edge_slope == slope_value


class TestTriggerEdgeSource:
    @pytest.mark.parametrize("source_value", [("C1", 1), ("C2", 2), ("C3", 3), ("C4", 4)])
    def test_trigger_edge_source(self, reseted_teledyneT3DSO3024HD, source_value):
        """[TestTriggerEdgeSource] Verify that :attr:`switch` can be set and read back correctly."""
        channel_attr_name = f"channel_{source_value[1]}"
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, channel_attr_name)
        channel_obj.switch = True
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_source = source_value[0]
        assert reseted_teledyneT3DSO3024HD.trigger_edge_source == source_value[0]


class TestTriggerEdgeLevel:
    # the legal range depends on the vertical scale/offset of the current
    # trigger source channel: [-4.1 * scale - offset, 4.1 * scale - offset]
    @pytest.mark.parametrize("channel", [1, 2, 3, 4])
    def test_trigger_edge_level_within_range(self, reseted_teledyneT3DSO3024HD, channel):
        """[TestTriggerEdgeLevel] Verify that :attr:`switch` can be set and read back correctly."""
        channel_obj = getattr(reseted_teledyneT3DSO3024HD, f"channel_{channel}")
        channel_obj.switch = True
        channel_obj.scale = 1
        channel_obj.offset = 0
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_source = f"C{channel}"
        reseted_teledyneT3DSO3024HD.trigger_edge_level = 2.0  # within [-4.1, 4.1]
        assert reseted_teledyneT3DSO3024HD.trigger_edge_level == pytest.approx(2.0, rel=1e-3)

    def test_trigger_edge_level_range_updates_with_channel_scale(
            self, reseted_teledyneT3DSO3024HD):
        """[TestTriggerEdgeLevel] Verify that :attr:`switch` can be set and read back correctly."""
        # a wider channel scale must widen the legal trigger level range
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_1.high_impedance_enabled = True
        reseted_teledyneT3DSO3024HD.channel_1.scale = 5
        reseted_teledyneT3DSO3024HD.channel_1.offset = 0
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_source = "C1"
        reseted_teledyneT3DSO3024HD.trigger_edge_level = 15  # within [-20.5, 20.5]
        assert reseted_teledyneT3DSO3024HD.trigger_edge_level == pytest.approx(15, rel=1e-3)

    def test_trigger_edge_level_range_accounts_for_channel_offset(
            self, reseted_teledyneT3DSO3024HD):
        """[TestTriggerEdgeLevel] Verify that :attr:`switch` can be set and read back correctly."""
        # channel offset shifts the legal range: [-4.1*scale - offset, 4.1*scale - offset]
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_1.scale = 1
        reseted_teledyneT3DSO3024HD.channel_1.offset = 0.5
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_source = "C1"
        reseted_teledyneT3DSO3024HD.trigger_edge_level = -1.0  # within [-4.6, 3.6]
        assert reseted_teledyneT3DSO3024HD.trigger_edge_level == pytest.approx(-1.0, rel=1e-3)

    def test_trigger_edge_level_out_of_range_rejected(self, reseted_teledyneT3DSO3024HD):
        """[TestTriggerEdgeLevel] Verify that assigning an invalid value to :attr:`switch`
        raises a ``ValueError``."""
        # values outside [-4.1*scale - offset, 4.1*scale - offset] must be
        # rejected client-side (strict_range), before anything is sent
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_1.scale = 1
        reseted_teledyneT3DSO3024HD.channel_1.offset = 0
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_source = "C1"
        with pytest.raises(ValueError):
            reseted_teledyneT3DSO3024HD.trigger_edge_level = 10  # > 4.1 * 1 - 0

    @pytest.mark.parametrize("source_value", ["EX", "EX5", "LINE"])
    def test_trigger_edge_level_unrestricted_for_non_channel_source(
            self, reseted_teledyneT3DSO3024HD, source_value):
        """[TestTriggerEdgeLevel] Verify that :attr:`trigger_type` can be set and read
        back correctly."""
        # non-analog sources have no scale/offset, so the level is not range-checked
        reseted_teledyneT3DSO3024HD.trigger_type = "EDGE"
        reseted_teledyneT3DSO3024HD.trigger_edge_source = source_value
        reseted_teledyneT3DSO3024HD.trigger_edge_level = 0.61
        assert reseted_teledyneT3DSO3024HD.trigger_edge_level == pytest.approx(0.61, rel=2e-2)


class TestMeasure:
    @pytest.mark.parametrize("measure_value", [True, False])
    def test_measure(self, reseted_teledyneT3DSO3024HD, measure_value):
        """[TestMeasure] Verify that :attr:`measure` can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.measure = measure_value
        assert reseted_teledyneT3DSO3024HD.measure == measure_value


class TestMeasureMode:
    @pytest.mark.parametrize("measure_mode_value", ["SIMPLE", "ADVANCED"])
    def test_measure_mode(self, reseted_teledyneT3DSO3024HD, measure_mode_value):
        """[TestMeasureMode] Verify that :attr:`measure_mode` can be set and read back correctly."""
        reseted_teledyneT3DSO3024HD.measure_mode = measure_mode_value
        assert reseted_teledyneT3DSO3024HD.measure_mode == measure_mode_value


class TestMeasurementSimpleSource:
    @pytest.mark.parametrize("source_value", ["C1", "C2", "C3", "C4"])
    def test_measurement_simple_source_channel(self, reseted_teledyneT3DSO3024HD,
                                                source_value):
        """[TestMeasurementSimpleSource] Verify that :attr:`measurement_simple_source` can be set
        and read back correctly."""
        reseted_teledyneT3DSO3024HD.measurement_simple_source = source_value
        assert reseted_teledyneT3DSO3024HD.measurement_simple_source == source_value


@pytest.mark.skip(reason="No Signal applied")
class TestSetMeasurementItem:
    # NOTE: This test requires a real sine signal applied to channel 1. The sine
    # needs to have an amplitude of 1V and a frequency of 20kHz with 0° phase shift and 0.2V offset.

    def test_set_measurement(self, reseted_teledyneT3DSO3024HD):
        """[TestSetMeasurementItem] Verify that :attr:`switch` can be set and read back
        correctly."""
        measurements = [("FREQUENCY", 20e3, 1e-2), ("AMPLITUDE", 2.0, 1e-2), ("RMS", 0.735, 1e-2),
                        ("MEAN", 0.2, 1e-1)]
        reseted_teledyneT3DSO3024HD.channel_1.switch = True
        reseted_teledyneT3DSO3024HD.channel_1.high_impedance_enabled = True
        reseted_teledyneT3DSO3024HD.channel_1.scale = 0.5
        reseted_teledyneT3DSO3024HD.timebase_scale = 20e-6
        reseted_teledyneT3DSO3024HD.measure = True
        reseted_teledyneT3DSO3024HD.measurement_simple_source = "C1"

        for parameter in measurements:
            reseted_teledyneT3DSO3024HD.set_measurement_item(parameter[0], True)
            time.sleep(0.2)
            result = reseted_teledyneT3DSO3024HD.measurement_value(parameter[0])
            print(f"{parameter[0]}: {result} ")
            assert result == pytest.approx(parameter[1], rel=parameter[2])
            reseted_teledyneT3DSO3024HD.set_measurement_item(parameter[0], False)


@pytest.mark.skip(reason="No Signal applied")
class TestWaveformPreamble:
    """[TestWaveformPreamble] Verify that :attr:`waveform preamble`
    can be set and read back correctly."""
    def test_waveform_preamble(self, teledyneT3DSO3024HD):
        result = teledyneT3DSO3024HD.waveform_preamble()
        print(result)


@pytest.mark.skip(reason="No Signal applied")
class TestWaveformData:
    def test_waveform_data(self, teledyneT3DSO3024HD):
        """[TestWaveformData] Verify that :attr:`waveform_points` can be set and
        read back correctly."""
        import matplotlib.pyplot as plt
        teledyneT3DSO3024HD.waveform_points = 2000000
        teledyneT3DSO3024HD.waveform_interval = 1
        # teledyneT3DSO3024HD.waveform_format = 'BYTE'
        teledyneT3DSO3024HD.waveform_format = 'WORD'
        time, voltage = teledyneT3DSO3024HD.get_waveform("C1")
        _fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(time * 1e3, voltage)   # Sec -> Milisec
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Voltage (V)")
        ax.set_title("Waveform C1")
        ax.grid(True)
        plt.show()


@pytest.mark.skip(reason="No Signal applied")
class TestWaveformDataDigital:
    def test_waveform_data_digital(self, teledyneT3DSO3024HD):
        """[TestWaveformDataDigital] Verify that :attr:`waveform_points` can be set and
        read back correctly."""
        import matplotlib.pyplot as plt
        teledyneT3DSO3024HD.waveform_points = 1000000
        teledyneT3DSO3024HD.waveform_interval = 500000
        # teledyneT3DSO3024HD.waveform_format = 'BYTE'
        teledyneT3DSO3024HD.waveform_format = 'WORD'
        time, voltage = teledyneT3DSO3024HD.get_waveform("D0")
        _fig, ax = plt.subplots(figsize=(10, 4))
        print(len(time))
        ax.plot(time, voltage)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Voltage (V)")
        ax.set_title("Waveform D0")
        ax.grid(True)
        plt.show()
