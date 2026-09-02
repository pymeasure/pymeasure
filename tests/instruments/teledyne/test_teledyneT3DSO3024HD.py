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

from pymeasure.instruments.teledyne.teledyneT3DSO3024HD import TeledyneT3DSO3024HD
from pymeasure.test import expected_protocol


def test_bwlimit():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":CHANnel1:BWLimit 20M", None),  # (send CMD, answer=None )
            (":CHANnel1:BWLimit?", "20M"),  # (query, simulated answer)
        ],
    ) as instr:
        instr.channel_1.bwlimit = "20M"
        assert instr.channel_1.bwlimit == "20M"


def test_high_impedance_enabled_limits_scale_range():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":CHANnel1:IMPedance FIFTy", None),
            (":CHANnel1:SCALe 5.00E-01", None),
        ],
    ) as instr:
        instr.channel_1.high_impedance_enabled = False
        instr.channel_1.scale = 0.5

        with pytest.raises(ValueError):
            # should raise a value error since impedance was set to 50.0
            instr.channel_1.scale = 2.0


def test_high_impedance_enabled_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:IMPedance?", "FIFTy")],
    ) as instr:
        assert not instr.channel_1.high_impedance_enabled


@pytest.mark.parametrize(
    "value, expected_command",
    [
        (True, "ON"),
        (False, "OFF"),
    ],
)
def test_invert_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":CHANnel1:INVert {expected_command}", None)],
    ) as instr:
        instr.channel_1.invert = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("ON", True),
        ("OFF", False),
    ],
)
def test_invert_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:INVert?", response)],
    ) as instr:
        assert instr.channel_1.invert is expected_value


def test_invert_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.invert = "YES"  # type: ignore


def test_label_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel:TEXT MyLabel", None)],
    ) as instr:
        instr.channel_1.label_text = "MyLabel"


def test_label_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel:TEXT?", "MyLabel")],
    ) as instr:
        assert instr.channel_1.label_text == "MyLabel"


def test_label_exact_max_length_allowed():
    label_20_chars = "A" * 20
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":CHANnel1:LABel:TEXT {label_20_chars}", None)],
    ) as instr:
        instr.channel_1.label_text = label_20_chars


def test_label_too_long_rejected():
    label_21_chars = "A" * 21
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label_text = label_21_chars


def test_offset_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:OFFSet -3.800E+00", None)],
    ) as instr:
        instr.channel_1.offset = -3.8


def test_offset_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:OFFSet?", "-3.8E+00")],
    ) as instr:
        assert instr.channel_1.offset == -3.8


def test_probe_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:PROBe VALue,1.00E+02", None)],
    ) as instr:
        instr.channel_1.probe = 100


def test_probe_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:PROBe?", "1.00E+02")],
    ) as instr:
        assert instr.channel_1.probe == 100.0


def test_probe_out_of_range_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.probe = 2e6


def test_unit_set_voltage():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:UNIT V", None)],
    ) as instr:
        instr.channel_1.unit = "V"


def test_unit_set_current():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:UNIT A", None)],
    ) as instr:
        instr.channel_1.unit = "A"


def test_unit_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:UNIT?", "A")],
    ) as instr:
        assert instr.channel_1.unit == "A"


def test_unit_invalid_value_rejected():
    with (
            expected_protocol(
                TeledyneT3DSO3024HD,
                [],
            ) as instr,
            pytest.raises(ValueError),
        ):
            instr.channel_1.unit = "OHM"


def test_coupling_set_dc():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling DC", None)],
    ) as instr:
        instr.channel_1.coupling = "DC"


def test_coupling_set_ac():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling AC", None)],
    ) as instr:
        instr.channel_1.coupling = "AC"


def test_coupling_set_gnd():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling GND", None)],
    ) as instr:
        instr.channel_1.coupling = "GND"


def test_coupling_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling?", "AC")],
    ) as instr:
        assert instr.channel_1.coupling == "AC"


def test_coupling_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.coupling = "ACDC"


def test_label_set_true():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel ON", None)],
    ) as instr:
        instr.channel_1.label = True


def test_label_set_false():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel OFF", None)],
    ) as instr:
        instr.channel_1.label = False


def test_label_get_true():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel?", "ON")],
    ) as instr:
        assert instr.channel_1.label is True


def test_label_get_false():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel?", "OFF")],
    ) as instr:
        assert instr.channel_1.label is False


def test_label_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label = "YES"


def test_skew_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SKEW 5.00E-08", None)],
    ) as instr:
        instr.channel_1.skew = 5e-8


def test_skew_set_negative():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SKEW -1.00E-07", None)],
    ) as instr:
        instr.channel_1.skew = -1e-7


def test_skew_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SKEW?", "5.00E-08")],
    ) as instr:
        assert instr.channel_1.skew == 5e-8


def test_skew_out_of_range_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.skew = 2e-7


def test_switch_set_true():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch ON", None)],
    ) as instr:
        instr.channel_1.switch = True


def test_switch_set_false():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch OFF", None)],
    ) as instr:
        instr.channel_1.switch = False


def test_switch_get_true():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch?", "ON")],
    ) as instr:
        assert instr.channel_1.switch is True


def test_switch_get_false():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch?", "OFF")],
    ) as instr:
        assert instr.channel_1.switch is False


def test_switch_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.switch = "MAYBE"


def test_visible_set_true():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible ON", None)],
    ) as instr:
        instr.channel_1.visible = True


def test_visible_set_false():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible OFF", None)],
    ) as instr:
        instr.channel_1.visible = False


def test_visible_get_true():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible?", "ON")],
    ) as instr:
        assert instr.channel_1.visible is True


def test_visible_get_false():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible?", "OFF")],
    ) as instr:
        assert instr.channel_1.visible is False


def test_visible_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.visible = "MAYBE"


def test_scale_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SCALe 2.00E+00", None)],
    ) as instr:
        instr.channel_1.scale = 2.0


def test_scale_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SCALe?", "2.00E+00")],
    ) as instr:
        assert instr.channel_1.scale == 2.0


def test_scale_out_of_range_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.scale = 20.0


@pytest.mark.parametrize(
    "mode",
    [
        "SLOW",
        "FAST",
    ],
)
def test_acquisition_rate_mode_set(mode):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":ACQuire:AMODe {mode}", None)],
    ) as instr:
        instr.acquisition_rate_mode = mode


@pytest.mark.parametrize(
    "mode",
    [
        "SLOW",
        "FAST",
    ],
)
def test_acquisition_rate_mode_get(mode):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:AMODe?", mode)],
    ) as instr:
        assert instr.acquisition_rate_mode == mode


def test_acquisition_rate_mode_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_rate_mode = "MEDIUM"


def test_clear_sweep():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:CSWeep", None)],
    ) as instr:
        instr.clear_sweep()


@pytest.mark.parametrize(
    "value, expected_command",
    [
        (True, "ON"),
        (False, "OFF"),
    ],
)
def test_interpolation_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":ACQuire:INTerpolation {expected_command}", None)],
    ) as instr:
        instr.interpolation = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("ON", True),
        ("OFF", False),
    ],
)
def test_interpolation_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:INTerpolation?", response)],
    ) as instr:
        assert instr.interpolation is expected_value


def test_interpolation_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.interpolation = "YES"  # type: ignore


@pytest.mark.parametrize("value", ["YT", "XY", "ROLL"])
def test_mode_set(value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":ACQuire:MODE {value}", None)],
    ) as instr:
        instr.mode = value


@pytest.mark.parametrize("value", ["YT", "XY", "ROLL"])
def test_mode_get(value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:MODE?", value)],
    ) as instr:
        assert instr.mode == value


def test_mode_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.mode = "ZY"


def test_memory_depth_single_channel_mode():
    # Only C1 is on -> single-channel mode -> full value set available
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":CHANnel1:SWITch?", "ON"),
            (":CHANnel2:SWITch?", "OFF"),
            (":CHANnel3:SWITch?", "OFF"),
            (":CHANnel4:SWITch?", "OFF"),
            (":ACQuire:MDEPth 400M", None),
        ],
    ) as instr:
        instr.memory_depth = 400e6


def test_memory_depth_dual_channel_mode():
    # One of C1/C2 and one of C3/C4 on -> dual-channel mode
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":CHANnel1:SWITch?", "ON"),
            (":CHANnel2:SWITch?", "OFF"),
            (":CHANnel3:SWITch?", "ON"),
            (":CHANnel4:SWITch?", "OFF"),
            (":ACQuire:MDEPth 200M", None),
        ],
    ) as instr:
        instr.memory_depth = 200e6


def test_memory_depth_quad_channel_mode():
    # Three channels on -> quad-channel mode
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":CHANnel1:SWITch?", "ON"),
            (":CHANnel2:SWITch?", "ON"),
            (":CHANnel3:SWITch?", "ON"),
            (":CHANnel4:SWITch?", "OFF"),
            (":ACQuire:MDEPth 100M", None),
        ],
    ) as instr:
        instr.memory_depth = 100e6


def test_memory_depth_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:MDEPth?", "10k")],
    ) as instr:
        assert instr.memory_depth == 10e3


def test_memory_depth_invalid_value_for_single_channel_mode_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [
                (":CHANnel1:SWITch?", "ON"),
                (":CHANnel2:SWITch?", "OFF"),
                (":CHANnel3:SWITch?", "OFF"),
                (":CHANnel4:SWITch?", "OFF"),
            ],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.memory_depth = 999e6


def test_points():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:POINts?", "1400")],
    ) as instr:
        assert instr.points == 1400.0


@pytest.mark.parametrize(
    "value, expected_command",
    [
        (True, "ON"),
        (False, "OFF"),
    ],
)
def test_sequence_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":ACQuire:SEQuence {expected_command}", None)],
    ) as instr:
        instr.sequence = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("ON", True),
        ("OFF", False),
    ],
)
def test_sequence_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SEQuence?", response)],
    ) as instr:
        assert instr.sequence is expected_value


def test_sequence_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.sequence = "YES"  # type: ignore


def test_sequence_count_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SEQuence:COUNt 10", None)],
    ) as instr:
        instr.sequence_count = 10


def test_sequence_count_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SEQuence:COUNt?", "10")],
    ) as instr:
        assert instr.sequence_count == 10


def test_sample_rate():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SRATe?", "2.0E+09")],
    ) as instr:
        assert instr.sample_rate == 2e9


def test_acquisition_type_get_normal():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "NORMal")],
    ) as instr:
        assert instr.acquisition_type == "NORMAL"


def test_acquisition_type_get_peak():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "PEAK")],
    ) as instr:
        assert instr.acquisition_type == "PEAK"


def test_acquisition_type_get_average():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "AVERage,16")],
    ) as instr:
        assert instr.acquisition_type == ("AVERAGE", 16.0)


def test_acquisition_type_get_eres():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "ERES,2.0")],
    ) as instr:
        assert instr.acquisition_type == ("ERES", 2.0)


def test_acquisition_type_set_normal():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE NORMal", None)],
    ) as instr:
        instr.acquisition_type = "NORMAL"


def test_acquisition_type_set_peak():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE PEAK", None)],
    ) as instr:
        instr.acquisition_type = "PEAK"


def test_acquisition_type_set_average():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE AVERage,16", None)],
    ) as instr:
        instr.acquisition_type = ("AVERAGE", 16)


def test_acquisition_type_set_eres():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE ERES,2.0", None)],
    ) as instr:
        instr.acquisition_type = ("ERES", 2.0)


def test_acquisition_type_average_missing_param_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = "AVERAGE"


def test_acquisition_type_eres_missing_param_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = "ERES"


def test_acquisition_type_normal_with_param_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = ("NORMAL", 16)


def test_acquisition_type_average_invalid_param_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = ("AVERAGE", 5)


def test_acquisition_type_invalid_type_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = "FOO"


def test_timebase_scale_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:SCALe 5.00E-03", None)],
    ) as instr:
        instr.timebase_scale = 5e-3


def test_timebase_scale_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:SCALe?", "5.00E-03")],
    ) as instr:
        assert instr.timebase_scale == 5e-3


def test_timebase_delay_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":TIMebase:SCALe?", "1.00E-03"),  # implicit read inside the setter
            (":TIMebase:DELay 1.00E-05", None),
        ],
    ) as instr:
        instr.timebase_delay = 1e-5


def test_timebase_delay_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:DELay?", "1.00E-05")],
    ) as instr:
        assert instr.timebase_delay == 1e-5


def test_timebase_delay_out_of_static_range_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [(":TIMebase:SCALe?", "1.00E-03")],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.timebase_delay = 6


@pytest.mark.parametrize(
    "value, expected_command",
    [
        (True, "ON"),
        (False, "OFF"),
    ],
)
def test_timebase_window_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TIMebase:WINDow {expected_command}", None)],
    ) as instr:
        instr.timebase_window = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("ON", True),
        ("OFF", False),
    ],
)
def test_timebase_window_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow?", response)],
    ) as instr:
        assert instr.timebase_window is expected_value


def test_timebase_window_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.timebase_window = "YES"


def test_timebase_window_delay_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:DELay 1.00E-03", None)],
    ) as instr:
        instr.timebase_window_delay = 1e-3


def test_timebase_window_delay_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:DELay?", "1.00E-03")],
    ) as instr:
        assert instr.timebase_window_delay == 1e-3


def test_timebase_window_scale_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:SCALe 1.00E-03", None)],
    ) as instr:
        instr.timebase_window_scale = 1e-3


def test_timebase_window_scale_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:SCALe?", "1.00E-03")],
    ) as instr:
        assert instr.timebase_window_scale == 1e-3


@pytest.mark.parametrize(
    "value, expected_command",
    [
        ("SINGLE", "SINGle"),
        ("NORMAL", "NORMal"),
        ("AUTO", "AUTO"),
    ],
)
def test_trigger_mode_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:MODE {expected_command}", None)],
    ) as instr:
        instr.trigger_mode = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("SINGle", "SINGLE"),
        ("NORMal", "NORMAL"),
        ("AUTO", "AUTO"),
    ],
)
def test_trigger_mode_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:MODE?", response)],
    ) as instr:
        assert instr.trigger_mode == expected_value


def test_trigger_mode_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_mode = "MANUAL"  # type: ignore


def test_trigger_run():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:RUN", None)],
    ) as instr:
        instr.trigger_run()


def test_trigger_status():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:STATus?", "Trig'd")],
    ) as instr:
        assert instr.trigger_status == "Trig'd"


def test_trigger_stop():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:STOP", None)],
    ) as instr:
        instr.trigger_stop()


@pytest.mark.parametrize(
    "value, expected_command",
    [
        ("EDGE", "EDGE"),
        ("PULSE", "PULSe"),
        ("SLOPE", "SLOPe"),
        ("INTERVAL", "INTerval"),
        ("PATTERN", "PATTern"),
        ("RUNT", "RUNT"),
        ("QUALIFIED", "QUALified"),
        ("WINDOW", "WINDow"),
        ("DROPOUT", "DROPout"),
        ("VIDEO", "VIDeo"),
        ("IIC", "IIC"),
        ("SPI", "SPI"),
        ("UART", "UART"),
        ("LIN", "LIN"),
        ("CAN", "CAN"),
        ("FLEXRAY", "FLEXray"),
        ("CANFD", "CANFd"),
        ("IIS", "IIS"),
    ],
)
def test_trigger_type_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:TYPE {expected_command}", None)],
    ) as instr:
        instr.trigger_type = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("EDGE", "EDGE"),
        ("PULSe", "PULSE"),
        ("SLOPe", "SLOPE"),
        ("CANFd", "CANFD"),
    ],
)
def test_trigger_type_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:TYPE?", response)],
    ) as instr:
        assert instr.trigger_type == expected_value


def test_trigger_type_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_type = "NOISE"  # type: ignore


@pytest.mark.parametrize(
    "value, expected_command",
    [
        ("DC", "DC"),
        ("AC", "AC"),
        ("LF_REJECT", "LFREJect"),
        ("HF_REJECT", "HFREJect"),
    ],
)
def test_trigger_edge_coupling_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:COUPling {expected_command}", None)],
    ) as instr:
        instr.trigger_edge_coupling = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("DC", "DC"),
        ("AC", "AC"),
        ("LFREJect", "LF_REJECT"),
        ("HFREJect", "HF_REJECT"),
    ],
)
def test_trigger_edge_coupling_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:COUPling?", response)],
    ) as instr:
        assert instr.trigger_edge_coupling == expected_value


def test_trigger_edge_coupling_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_coupling = "GND"  # type: ignore


def test_trigger_edge_holdoff_events_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDEVent 5", None)],
    ) as instr:
        instr.trigger_edge_holdoff_events = 5


def test_trigger_edge_holdoff_events_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDEVent?", "5")],
    ) as instr:
        assert instr.trigger_edge_holdoff_events == 5


def test_trigger_edge_holdoff_events_out_of_range_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_holdoff_events = 100000001


def test_trigger_edge_holdoff_time_set():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDTime 1.00E-03", None)],
    ) as instr:
        instr.trigger_edge_holdoff_time = 1e-3


def test_trigger_edge_holdoff_time_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDTime?", "1.00E-03")],
    ) as instr:
        assert instr.trigger_edge_holdoff_time == 1e-3


def test_trigger_edge_holdoff_time_out_of_range_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_holdoff_time = 31.0


@pytest.mark.parametrize(
    "value, expected_command",
    [
        ("OFF", "OFF"),
        ("EVENTS", "EVENts"),
        ("TIME", "TIME"),
    ],
)
def test_trigger_edge_holdoff_type_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:HOLDoff {expected_command}", None)],
    ) as instr:
        instr.trigger_edge_holdoff_type = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("OFF", "OFF"),
        ("EVENts", "EVENTS"),
        ("TIME", "TIME"),
    ],
)
def test_trigger_edge_holdoff_type_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HOLDoff?", response)],
    ) as instr:
        assert instr.trigger_edge_holdoff_type == expected_value


def test_trigger_edge_holdoff_type_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_holdoff_type = "NEVER"  # type: ignore


@pytest.mark.parametrize("value", ["LAST_TRIG", "ACQ_START"])
def test_trigger_edge_holdoff_start_set(value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:HSTart {value}", None)],
    ) as instr:
        instr.trigger_edge_holdoff_start = value


@pytest.mark.parametrize("value", ["LAST_TRIG", "ACQ_START"])
def test_trigger_edge_holdoff_start_get(value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HSTart?", value)],
    ) as instr:
        assert instr.trigger_edge_holdoff_start == value


def test_trigger_edge_holdoff_start_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_holdoff_start = "MIDDLE"  # type: ignore


def test_trigger_edge_level_set_channel_source():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":TRIGger:EDGE:SOURce?", "C1"),
            (":CHANnel1:SCALe?", "2.00E+00"),
            (":CHANnel1:OFFSet?", "0.000E+00"),
            (":TRIGger:EDGE:LEVel 5.00E+00", None),
        ],
    ) as instr:
        instr.trigger_edge_level = 5.0


def test_trigger_edge_level_set_different_channel_source():
    # scale=1.0, offset=0.5 -> valid range [-4.6, 3.6]
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":TRIGger:EDGE:SOURce?", "C3"),
            (":CHANnel3:SCALe?", "1.00E+00"),
            (":CHANnel3:OFFSet?", "5.000E-01"),
            (":TRIGger:EDGE:LEVel -1.00E+00", None),
        ],
    ) as instr:
        instr.trigger_edge_level = -1.0


def test_trigger_edge_level_get():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:LEVel?", "5.00E+00")],
    ) as instr:
        assert instr.trigger_edge_level == 5.0


@pytest.mark.parametrize(
    "value",
    [
        8.3,  # above upper bound: 4.1 * 2.0 - 0.0 = 8.2
        -8.3,  # below lower bound: -4.1 * 2.0 - 0.0 = -8.2
    ],
)
def test_trigger_edge_level_out_of_range_rejected_for_channel_source(value):
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [
                (":TRIGger:EDGE:SOURce?", "C1"),
                (":CHANnel1:SCALe?", "2.00E+00"),
                (":CHANnel1:OFFSet?", "0.000E+00"),
            ],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_level = value


@pytest.mark.parametrize("source", ["EX", "EX5", "LINE", "D0", "D15"])
def test_trigger_edge_level_set_unrestricted_for_non_channel_source(source):
    # Non-analog trigger sources have no scale/offset -> no extra queries,
    # and the value is not range-checked.
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":TRIGger:EDGE:SOURce?", source),
            (":TRIGger:EDGE:LEVel 1.00E+03", None),
        ],
    ) as instr:
        instr.trigger_edge_level = 1e3


@pytest.mark.parametrize(
    "value, expected_command",
    [
        (True, "ON"),
        (False, "OFF"),
    ],
)
def test_trigger_edge_noise_reject_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:NREJect {expected_command}", None)],
    ) as instr:
        instr.trigger_edge_noise_reject = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("ON", True),
        ("OFF", False),
    ],
)
def test_trigger_edge_noise_reject_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:NREJect?", response)],
    ) as instr:
        assert instr.trigger_edge_noise_reject is expected_value


def test_trigger_edge_noise_reject_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_noise_reject = "YES"  # type: ignore


@pytest.mark.parametrize(
    "value, expected_command",
    [
        ("RISING", "RISing"),
        ("FALLING", "FALLing"),
        ("ALTERNATE", "ALTernate"),
    ],
)
def test_trigger_edge_slope_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:SLOPe {expected_command}", None)],
    ) as instr:
        instr.trigger_edge_slope = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("RISing", "RISING"),
        ("FALLing", "FALLING"),
        ("ALTernate", "ALTERNATE"),
    ],
)
def test_trigger_edge_slope_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:SLOPe?", response)],
    ) as instr:
        assert instr.trigger_edge_slope == expected_value


def test_trigger_edge_slope_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_slope = "BOTH"  # type: ignore


@pytest.mark.parametrize(
    "value",
    [
        "C1", "C2", "C3", "C4",
        "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
        "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15",
        "EX", "EX5", "LINE",
    ],
)
def test_trigger_edge_source_set(value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:SOURce {value}", None)],
    ) as instr:
        instr.trigger_edge_source = value


@pytest.mark.parametrize("value", ["C1", "D0", "EX", "EX5", "LINE"])
def test_trigger_edge_source_get(value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:SOURce?", value)],
    ) as instr:
        assert instr.trigger_edge_source == value


def test_trigger_edge_source_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_source = "C5"  # type: ignore


@pytest.mark.parametrize(
    "value, expected_command",
    [
        (True, "ON"),
        (False, "OFF"),
    ],
)
def test_measure_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure {expected_command}", None)],
    ) as instr:
        instr.measure = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("ON", True),
        ("OFF", False),
    ],
)
def test_measure_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure?", response)],
    ) as instr:
        assert instr.measure is expected_value


def test_measure_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.measure = "YES"  # type: ignore


@pytest.mark.parametrize(
    "value, expected_command",
    [
        ("SIMPLE", "SIMPle"),
        ("ADVANCED", "ADVanced"),
    ],
)
def test_measure_mode_set(value, expected_command):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:MODE {expected_command}", None)],
    ) as instr:
        instr.measure_mode = value


@pytest.mark.parametrize(
    "response, expected_value",
    [
        ("SIMPle", "SIMPLE"),
        ("ADVanced", "ADVANCED"),
    ],
)
def test_measure_mode_get(response, expected_value):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:MODE?", response)],
    ) as instr:
        assert instr.measure_mode == expected_value


def test_measure_mode_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.measure_mode = "COMPLEX"


@pytest.mark.parametrize(
    "source", ["C1", "C4", "Z2", "F3", "D0", "D15", "ZD7", "REFA", "REFD"],
)
def test_measurement_simple_source_set(source):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:SIMPle:SOURce {source}", None)],
    ) as instr:
        instr.measurement_simple_source = source


@pytest.mark.parametrize(
    "source", ["C1", "Z2", "F3", "D15", "ZD7", "REFA"],
)
def test_measurement_simple_source_get(source):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:SIMPle:SOURce?", source)],
    ) as instr:
        assert instr.measurement_simple_source == source


def test_measurement_simple_source_invalid_value_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.measurement_simple_source = "C5"


@pytest.mark.parametrize(
    "parameter, scpi_param",
    [
        ("FREQUENCY", "FREQ"),
        ("AMPLITUDE", "AMPL"),
        ("RISE_TIME", "RISE"),
        ("PEAK_TO_PEAK", "PKPK"),
    ],
)
def test_set_measurement_item_enabled(parameter, scpi_param):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:SIMPle:ITEM {scpi_param},ON", None)],
    ) as instr:
        instr.set_measurement_item(parameter)


def test_set_measurement_item_disabled():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:SIMPle:ITEM FREQ,OFF", None)],
    ) as instr:
        instr.set_measurement_item("FREQUENCY", enabled=False)


def test_set_measurement_item_invalid_parameter_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.set_measurement_item("BANANA")


@pytest.mark.parametrize(
    "parameter, scpi_param",
    [
        ("FREQUENCY", "FREQ"),
        ("AMPLITUDE", "AMPL"),
    ],
)
def test_measurement_value(parameter, scpi_param):
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:SIMPle:VALue? {scpi_param}", "1.234E+03")],
    ) as instr:
        assert instr.measurement_value(parameter) == 1234.0


def test_measurement_value_all_returns_raw_string():
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:SIMPle:VALue? ALL", "1.234E+03,5.000E-01")],
    ) as instr:
        assert instr.measurement_value("ALL") == "1.234E+03,5.000E-01"


def test_measurement_value_invalid_parameter_rejected():
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.measurement_value("BANANA")
