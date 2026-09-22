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

import struct

import numpy as np
import pytest

from pymeasure.instruments.teledyne.teledyneT3DSO3024HD import TeledyneT3DSO3024HD
from pymeasure.test import expected_protocol


def test_bwlimit():
    """Verify that :attr:`bwlimit` can be set and read back correctly."""
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
    """Verify that changing :attr:`high_impedance_enabled` updates the allowed range of a
    dependent property."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":CHANnel1:IMPedance FIFTy", None),
            (":CHANnel1:IMPedance?", "FIFTy"),
            (":CHANnel1:SCALe 5.00E-01", None),
        ],
    ) as instr:
        instr.channel_1.high_impedance_enabled = False
        instr.channel_1.scale = 0.5

        with pytest.raises(ValueError):
            # should raise a value error since impedance was set to 50.0
            instr.channel_1.scale = 2.0


def test_high_impedance_enabled_get():
    """Verify that reading :attr:`high_impedance_enabled` parses the simulated instrument
    response correctly."""
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
    """Verify that setting :attr:`invert` sends the expected SCPI command."""
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
    """Verify that reading :attr:`invert` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:INVert?", response)],
    ) as instr:
        assert instr.channel_1.invert is expected_value


def test_invert_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`invert` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.invert = "YES"  # type: ignore


def test_label_set():
    """Verify that setting :attr:`label_text` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(':CHANnel1:LABel:TEXT "MyLabel"', None)],
    ) as instr:
        instr.channel_1.label_text = "MyLabel"


def test_label_get():
    """Verify that reading :attr:`label_text` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel:TEXT?", "MyLabel")],
    ) as instr:
        assert instr.channel_1.label_text == "MyLabel"


def test_label_exact_max_length_allowed():
    """Verify that a value at the maximum allowed length/limit for :attr:`label_text`
    is accepted."""
    label_20_chars = "A" * 20
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f':CHANnel1:LABel:TEXT "{label_20_chars}"', None)],
    ) as instr:
        instr.channel_1.label_text = label_20_chars


def test_label_no_string():
    """Verify that a value of none string in :attr:`label_text` is not accepted."""
    label = 21
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(TypeError),
    ):
        instr.channel_1.label_text = label  # type: ignore


def test_label_quote():
    """Verify that a value with a quote in :attr:`label_text` is not accepted."""
    label = 'Hi""H'
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label_text = label  # type: ignore


def test_label_too_long_rejected():
    """Verify that assigning an invalid value to :attr:`label_text` raises a ``ValueError``."""
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
    """Verify that setting :attr:`offset` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:OFFSet -3.800E+00", None)],
    ) as instr:
        instr.channel_1.offset = -3.8


def test_offset_get():
    """Verify that reading :attr:`offset` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:OFFSet?", "-3.8E+00")],
    ) as instr:
        assert instr.channel_1.offset == -3.8


def test_probe_set():
    """Verify that setting :attr:`probe` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:PROBe VALue,1.00E+02", None)],
    ) as instr:
        instr.channel_1.probe = 100


def test_probe_get():
    """Verify that reading :attr:`probe` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:PROBe?", "1.00E+02")],
    ) as instr:
        assert instr.channel_1.probe == 100.0


def test_probe_out_of_range_rejected():
    """Verify that assigning an invalid value to :attr:`probe` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.probe = 2e6


def test_unit_set_voltage():
    """Verify that setting :attr:`unit` to 'voltage' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:UNIT V", None)],
    ) as instr:
        instr.channel_1.unit = "V"


def test_unit_set_current():
    """Verify that setting :attr:`unit` to 'current' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:UNIT A", None)],
    ) as instr:
        instr.channel_1.unit = "A"


def test_unit_get():
    """Verify that reading :attr:`unit` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:UNIT?", "A")],
    ) as instr:
        assert instr.channel_1.unit == "A"


def test_unit_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`unit` raises a ``ValueError``."""
    with (
            expected_protocol(
                TeledyneT3DSO3024HD,
                [],
            ) as instr,
            pytest.raises(ValueError),
        ):
            instr.channel_1.unit = "OHM"


def test_coupling_set_dc():
    """Verify that setting :attr:`coupling` to 'dc' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling DC", None)],
    ) as instr:
        instr.channel_1.coupling = "DC"


def test_coupling_set_ac():
    """Verify that setting :attr:`coupling` to 'ac' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling AC", None)],
    ) as instr:
        instr.channel_1.coupling = "AC"


def test_coupling_set_gnd():
    """Verify that setting :attr:`coupling` to 'gnd' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling GND", None)],
    ) as instr:
        instr.channel_1.coupling = "GND"


def test_coupling_get():
    """Verify that reading :attr:`coupling` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:COUPling?", "AC")],
    ) as instr:
        assert instr.channel_1.coupling == "AC"


def test_coupling_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`coupling` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.coupling = "ACDC"


def test_label_set_true():
    """Verify that setting :attr:`label` to ``True`` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel ON", None)],
    ) as instr:
        instr.channel_1.label = True


def test_label_set_false():
    """Verify that setting :attr:`label` to ``False`` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel OFF", None)],
    ) as instr:
        instr.channel_1.label = False


def test_label_get_true():
    """Verify that :attr:`label` reads back as ``True`` for the corresponding
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel?", "ON")],
    ) as instr:
        assert instr.channel_1.label is True


def test_label_get_false():
    """Verify that :attr:`label` reads back as ``False`` for the corresponding
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:LABel?", "OFF")],
    ) as instr:
        assert instr.channel_1.label is False


def test_label_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`label` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label = "YES"


def test_skew_set():
    """Verify that setting :attr:`skew` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SKEW 5.00E-08", None)],
    ) as instr:
        instr.channel_1.skew = 5e-8


def test_skew_set_negative():
    """Verify that setting :attr:`skew` to a negative value sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SKEW -1.00E-07", None)],
    ) as instr:
        instr.channel_1.skew = -1e-7


def test_skew_get():
    """Verify that reading :attr:`skew` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SKEW?", "5.00E-08")],
    ) as instr:
        assert instr.channel_1.skew == 5e-8


def test_skew_out_of_range_rejected():
    """Verify that assigning an invalid value to :attr:`skew` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.skew = 2e-7


def test_switch_set_true():
    """Verify that setting :attr:`switch` to ``True`` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch ON", None)],
    ) as instr:
        instr.channel_1.switch = True


def test_switch_set_false():
    """Verify that setting :attr:`switch` to ``False`` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch OFF", None)],
    ) as instr:
        instr.channel_1.switch = False


def test_switch_get_true():
    """Verify that :attr:`switch` reads back as ``True`` for the corresponding
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch?", "ON")],
    ) as instr:
        assert instr.channel_1.switch is True


def test_switch_get_false():
    """Verify that :attr:`switch` reads back as ``False`` for the corresponding
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SWITch?", "OFF")],
    ) as instr:
        assert instr.channel_1.switch is False


def test_switch_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`switch` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.switch = "MAYBE"


def test_visible_set_true():
    """Verify that setting :attr:`visible` to ``True`` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible ON", None)],
    ) as instr:
        instr.channel_1.visible = True


def test_visible_set_false():
    """Verify that setting :attr:`visible` to ``False`` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible OFF", None)],
    ) as instr:
        instr.channel_1.visible = False


def test_visible_get_true():
    """Verify that :attr:`visible` reads back as ``True`` for the corresponding
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible?", "ON")],
    ) as instr:
        assert instr.channel_1.visible is True


def test_visible_get_false():
    """Verify that :attr:`visible` reads back as ``False`` for the corresponding
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:VISible?", "OFF")],
    ) as instr:
        assert instr.channel_1.visible is False


def test_visible_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`visible` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.visible = "MAYBE"


def test_scale_set():
    """Verify that setting :attr:`scale` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SCALe 2.00E+00", None)],
    ) as instr:
        instr.channel_1.scale = 2.0


def test_scale_get():
    """Verify that reading :attr:`scale` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":CHANnel1:SCALe?", "2.00E+00")],
    ) as instr:
        assert instr.channel_1.scale == 2.0


def test_scale_out_of_range_rejected():
    """Verify that assigning an invalid value to :attr:`scale` raises a ``ValueError``."""
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
    """Verify that setting :attr:`acquisition_rate_mode` sends the expected SCPI command."""
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
    """Verify that reading :attr:`acquisition_rate_mode` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:AMODe?", mode)],
    ) as instr:
        assert instr.acquisition_rate_mode == mode


def test_acquisition_rate_mode_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`acquisition_rate_mode
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_rate_mode = "MEDIUM"


def test_clear_sweep():
    """Verify that :attr:`clear sweep` can be set and read back correctly."""
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
    """Verify that setting :attr:`interpolation` sends the expected SCPI command."""
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
    """Verify that reading :attr:`interpolation` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:INTerpolation?", response)],
    ) as instr:
        assert instr.interpolation is expected_value


def test_interpolation_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`interpolation` raises a ``ValueError``."""
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
    """Verify that setting :attr:`mode` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":ACQuire:MODE {value}", None)],
    ) as instr:
        instr.mode = value


@pytest.mark.parametrize("value", ["YT", "XY", "ROLL"])
def test_mode_get(value):
    """Verify that reading :attr:`mode` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:MODE?", value)],
    ) as instr:
        assert instr.mode == value


def test_mode_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`mode` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.mode = "ZY"


def test_memory_depth_single_channel_mode():
    """Verify that :attr:`memory_depth` can be set and read back correctly."""
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
    """Verify that :attr:`memory_depth` can be set and read back correctly."""
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
    """Verify that :attr:`memory_depth` can be set and read back correctly."""
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
    """Verify that reading :attr:`memory_depth` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:MDEPth?", "10k")],
    ) as instr:
        assert instr.memory_depth == 10e3


def test_memory_depth_invalid_value_for_single_channel_mode_rejected():
    """Verify that assigning an invalid value to :attr:`memory_depth` raises a ``ValueError``."""
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
    """Verify that :attr:`points` can be set and read back correctly."""
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
    """Verify that setting :attr:`sequence` sends the expected SCPI command."""
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
    """Verify that reading :attr:`sequence` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SEQuence?", response)],
    ) as instr:
        assert instr.sequence is expected_value


def test_sequence_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`sequence` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.sequence = "YES"  # type: ignore


def test_sequence_count_set():
    """Verify that setting :attr:`sequence_count` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SEQuence:COUNt 10", None)],
    ) as instr:
        instr.sequence_count = 10


def test_sequence_count_get():
    """Verify that reading :attr:`sequence_count` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SEQuence:COUNt?", "10")],
    ) as instr:
        assert instr.sequence_count == 10


def test_sample_rate():
    """Verify that :attr:`sample_rate` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:SRATe?", "2.0E+09")],
    ) as instr:
        assert instr.sample_rate == 2e9


def test_acquisition_type_get_normal():
    """Verify that reading :attr:`acquisition_type` correctly parses the 'normal'
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "NORMal")],
    ) as instr:
        assert instr.acquisition_type == "NORMAL"


def test_acquisition_type_get_peak():
    """Verify that reading :attr:`acquisition_type` correctly parses the 'peak'
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "PEAK")],
    ) as instr:
        assert instr.acquisition_type == "PEAK"


def test_acquisition_type_get_average():
    """Verify that reading :attr:`acquisition_type` correctly parses the 'average'
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "AVERage,16")],
    ) as instr:
        assert instr.acquisition_type == ("AVERAGE", 16.0)


def test_acquisition_type_get_eres():
    """Verify that reading :attr:`acquisition_type` correctly parses the 'eres'
    instrument response."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE?", "ERES,2.0")],
    ) as instr:
        assert instr.acquisition_type == ("ERES", 2.0)


def test_acquisition_type_set_normal():
    """Verify that setting :attr:`acquisition_type` to 'normal' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE NORMal", None)],
    ) as instr:
        instr.acquisition_type = "NORMAL"


def test_acquisition_type_set_peak():
    """Verify that setting :attr:`acquisition_type` to 'peak' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE PEAK", None)],
    ) as instr:
        instr.acquisition_type = "PEAK"


def test_acquisition_type_set_average():
    """Verify that setting :attr:`acquisition_type` to 'average' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE AVERage,16", None)],
    ) as instr:
        instr.acquisition_type = ("AVERAGE", 16)


def test_acquisition_type_set_eres():
    """Verify that setting :attr:`acquisition_type` to 'eres' sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":ACQuire:TYPE ERES,2.0", None)],
    ) as instr:
        instr.acquisition_type = ("ERES", 2.0)


def test_acquisition_type_average_missing_param_rejected():
    """Verify that assigning an invalid value to :attr:`acquisition_type`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = "AVERAGE"


def test_acquisition_type_eres_missing_param_rejected():
    """Verify that assigning an invalid value to :attr:`acquisition_type`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = "ERES"


def test_acquisition_type_normal_with_param_rejected():
    """Verify that assigning an invalid value to :attr:`acquisition_type`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = ("NORMAL", 16)


def test_acquisition_type_average_invalid_param_rejected():
    """Verify that assigning an invalid value to :attr:`acquisition_type`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = ("AVERAGE", 5)


def test_acquisition_type_invalid_type_rejected():
    """Verify that setting :attr:`timebase_scale` sends the expected SCPI command."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.acquisition_type = "FOO"


def test_timebase_scale_set():
    """Verify that setting :attr:`timebase_scale` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:SCALe 5.00E-03", None)],
    ) as instr:
        instr.timebase_scale = 5e-3


def test_timebase_scale_get():
    """Verify that reading :attr:`timebase_scale` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:SCALe?", "5.00E-03")],
    ) as instr:
        assert instr.timebase_scale == 5e-3


def test_timebase_delay_set():
    """Verify that setting :attr:`timebase_delay` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":TIMebase:SCALe?", "1.00E-03"),  # implicit read inside the setter
            (":TIMebase:DELay 1.00E-05", None),
        ],
    ) as instr:
        instr.timebase_delay = 1e-5


def test_timebase_delay_get():
    """Verify that reading :attr:`timebase_delay` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:DELay?", "1.00E-05")],
    ) as instr:
        assert instr.timebase_delay == 1e-5


def test_timebase_delay_out_of_static_range_rejected():
    """Verify that assigning an invalid value to :attr:`timebase_delay` raises a ``ValueError``."""
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
    """Verify that setting :attr:`timebase_window` sends the expected SCPI command."""
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
    """Verify that reading :attr:`timebase_window` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow?", response)],
    ) as instr:
        assert instr.timebase_window is expected_value


def test_timebase_window_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`timebase_window` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.timebase_window = "YES"


def test_timebase_window_delay_set():
    """Verify that setting :attr:`timebase_window_delay` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:DELay 1.00E-03", None)],
    ) as instr:
        instr.timebase_window_delay = 1e-3


def test_timebase_window_delay_get():
    """Verify that reading :attr:`timebase_window_delay` parses the simulated
    instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:DELay?", "1.00E-03")],
    ) as instr:
        assert instr.timebase_window_delay == 1e-3


def test_timebase_window_scale_set():
    """Verify that setting :attr:`timebase_window_scale` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TIMebase:WINDow:SCALe 1.00E-03", None)],
    ) as instr:
        instr.timebase_window_scale = 1e-3


def test_timebase_window_scale_get():
    """Verify that reading :attr:`timebase_window_scale` parses the simulated instrument
    response correctly."""
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
    """Verify that setting :attr:`trigger_mode` sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_mode` parses the simulated instrument response
    correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:MODE?", response)],
    ) as instr:
        assert instr.trigger_mode == expected_value


def test_trigger_mode_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_mode` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_mode = "MANUAL"  # type: ignore


def test_trigger_run():
    """Verify that :attr:`trigger run` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:RUN", None)],
    ) as instr:
        instr.trigger_run()


def test_trigger_status():
    """Verify that :attr:`trigger_status` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:STATus?", "Trig'd")],
    ) as instr:
        assert instr.trigger_status == "Trig'd"


def test_trigger_stop():
    """Verify that :attr:`trigger stop` can be set and read back correctly."""
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
    """Verify that setting :attr:`trigger_type` sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_type` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:TYPE?", response)],
    ) as instr:
        assert instr.trigger_type == expected_value


def test_trigger_type_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_type` raises a ``ValueError``."""
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
    """Verify that setting :attr:`trigger_edge_coupling` sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_edge_coupling` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:COUPling?", response)],
    ) as instr:
        assert instr.trigger_edge_coupling == expected_value


def test_trigger_edge_coupling_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_coupling`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_coupling = "GND"  # type: ignore


def test_trigger_edge_holdoff_events_set():
    """Verify that setting :attr:`trigger_edge_holdoff_events` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDEVent 5", None)],
    ) as instr:
        instr.trigger_edge_holdoff_events = 5


def test_trigger_edge_holdoff_events_get():
    """Verify that reading :attr:`trigger_edge_holdoff_events` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDEVent?", "5")],
    ) as instr:
        assert instr.trigger_edge_holdoff_events == 5


def test_trigger_edge_holdoff_events_out_of_range_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_holdoff_events`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_holdoff_events = 100000001


def test_trigger_edge_holdoff_time_set():
    """Verify that setting :attr:`trigger_edge_holdoff_time` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDTime 1.00E-03", None)],
    ) as instr:
        instr.trigger_edge_holdoff_time = 1e-3


def test_trigger_edge_holdoff_time_get():
    """Verify that reading :attr:`trigger_edge_holdoff_time` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HLDTime?", "1.00E-03")],
    ) as instr:
        assert instr.trigger_edge_holdoff_time == 1e-3


def test_trigger_edge_holdoff_time_out_of_range_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_holdoff_time`
    raises a ``ValueError``."""
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
    """Verify that setting :attr:`trigger_edge_holdoff_type` sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_edge_holdoff_type` parses the simulated
    instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HOLDoff?", response)],
    ) as instr:
        assert instr.trigger_edge_holdoff_type == expected_value


def test_trigger_edge_holdoff_type_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_holdoff_type`
    raises a ``ValueError``."""
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
    """Verify that setting :attr:`trigger_edge_holdoff_start` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:HSTart {value}", None)],
    ) as instr:
        instr.trigger_edge_holdoff_start = value


@pytest.mark.parametrize("value", ["LAST_TRIG", "ACQ_START"])
def test_trigger_edge_holdoff_start_get(value):
    """Verify that reading :attr:`trigger_edge_holdoff_start` parses the
    simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:HSTart?", value)],
    ) as instr:
        assert instr.trigger_edge_holdoff_start == value


def test_trigger_edge_holdoff_start_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_holdoff_start`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_holdoff_start = "MIDDLE"  # type: ignore


def test_trigger_edge_level_set_channel_source():
    """Verify that setting :attr:`trigger_edge_level` to 'channel_source' sends
    the expected SCPI command."""
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
    """Verify that setting :attr:`trigger_edge_level` to 'different_channel_source'
    sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_edge_level` parses the simulated instrument
    response correctly."""
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
    """Verify that assigning an invalid value to :attr:`trigger_edge_level`
    raises a ``ValueError``."""
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


@pytest.mark.parametrize(("source", "value"), [("EX", 6.11E-1), ("EX5", 0.3051E1)],)
def test_trigger_edge_level_out_of_range_rejected_for_non_channel_source(source, value):
    """Verify that assigning an invalid value to :attr:`trigger_edge_level`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [
                (":TRIGger:EDGE:SOURce?", source),
                (":TRIGger:EDGE:SOURce?", source),
            ],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.trigger_edge_level = value


@pytest.mark.parametrize("source", ["LINE", "D0", "D15"])
def test_trigger_edge_level_set_unrestricted_for_non_channel_source(source):
    """Verify that setting :attr:`trigger_edge_level` to 'unrestricted_for_non_channel_source'
    sends the expected SCPI command."""
    # Non-analog trigger sources have no scale/offset -> no extra queries,
    # and the value is not range-checked.
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":TRIGger:EDGE:SOURce?", source),
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
    """Verify that setting :attr:`trigger_edge_noise_reject` sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_edge_noise_reject` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:NREJect?", response)],
    ) as instr:
        assert instr.trigger_edge_noise_reject is expected_value


def test_trigger_edge_noise_reject_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_noise_reject`
    raises a ``ValueError``."""
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
    """Verify that setting :attr:`trigger_edge_slope` sends the expected SCPI command."""
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
    """Verify that reading :attr:`trigger_edge_slope` parses the
    simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:SLOPe?", response)],
    ) as instr:
        assert instr.trigger_edge_slope == expected_value


def test_trigger_edge_slope_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_slope` raises
    a ``ValueError``."""
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
    """Verify that setting :attr:`trigger_edge_source` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":TRIGger:EDGE:SOURce {value}", None)],
    ) as instr:
        instr.trigger_edge_source = value


@pytest.mark.parametrize("value", ["C1", "D0", "EX", "EX5", "LINE"])
def test_trigger_edge_source_get(value):
    """Verify that reading :attr:`trigger_edge_source` parses the simulated instrument response
    correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":TRIGger:EDGE:SOURce?", value)],
    ) as instr:
        assert instr.trigger_edge_source == value


def test_trigger_edge_source_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`trigger_edge_source` raises a
    ``ValueError``."""
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
    """Verify that setting :attr:`measure` sends the expected SCPI command."""
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
    """Verify that reading :attr:`measure` parses the simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure?", response)],
    ) as instr:
        assert instr.measure is expected_value


def test_measure_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`measure` raises a ``ValueError``."""
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
    """Verify that setting :attr:`measure_mode` sends the expected SCPI command."""
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
    """Verify that reading :attr:`measure_mode` parses the simulated
    instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:MODE?", response)],
    ) as instr:
        assert instr.measure_mode == expected_value


def test_measure_mode_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`measure_mode` raises a ``ValueError``."""
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
    """Verify that setting :attr:`measurement_simple_source` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:SIMPle:SOURce {source}", None)],
    ) as instr:
        instr.measurement_simple_source = source


@pytest.mark.parametrize(
    "source", ["C1", "Z2", "F3", "D15", "ZD7", "REFA"],
)
def test_measurement_simple_source_get(source):
    """Verify that reading :attr:`measurement_simple_source` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:SIMPle:SOURce?", source)],
    ) as instr:
        assert instr.measurement_simple_source == source


def test_measurement_simple_source_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`measurement_simple_source`
    raises a ``ValueError``."""
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
    """Verify that :attr:`set measurement item enabled` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:SIMPle:ITEM {scpi_param},ON", None)],
    ) as instr:
        instr.set_measurement_item(parameter)


def test_set_measurement_item_disabled():
    """Verify that :attr:`set measurement item disabled` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:SIMPle:ITEM FREQ,OFF", None)],
    ) as instr:
        instr.set_measurement_item("FREQUENCY", enabled=False)


def test_set_measurement_item_invalid_parameter_rejected():
    """Verify that assigning an invalid value to :attr:`set measurement item` raises a
    ``ValueError``."""
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
    """Verify that :attr:`measurement_value` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":MEASure:SIMPle:VALue? {scpi_param}", "1.234E+03")],
    ) as instr:
        assert instr.measurement_value(parameter) == 1234.0


def test_measurement_value_all_returns_raw_string():
    """Verify that :attr:`measurement_value` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":MEASure:SIMPle:VALue? ALL", "1.234E+03,5.000E-01")],
    ) as instr:
        assert instr.measurement_value("ALL") == "1.234E+03,5.000E-01"


def test_measurement_value_invalid_parameter_rejected():
    """Verify that assigning an invalid value to :attr:`measurement value`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.measurement_value("BANANA")


@pytest.mark.parametrize("value", ["C1", "D0", "F1"])
def test_waveform_source_set(value):
    """Verify that setting :attr:`waveform_source` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":WAVeform:SOURce {value}", None)],
    ) as instr:
        instr.waveform_source = value


@pytest.mark.parametrize("value", ["C1", "D0", "F1"])
def test_waveform_source_get(value):
    """Verify that reading :attr:`waveform_source` parses the simulated instrument
    response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:SOURce?", value)],
    ) as instr:
        assert instr.waveform_source == value


def test_waveform_source_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`waveform_source` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.waveform_source = "C5"  # type: ignore


def test_waveform_start_set():
    """Verify that setting :attr:`waveform_start` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:STARt 100", None)],
    ) as instr:
        instr.waveform_start = 100


def test_waveform_start_get():
    """Verify that reading :attr:`waveform_start` parses the simulated instrument response
    correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:STARt?", "100")],
    ) as instr:
        assert instr.waveform_start == 100


def test_waveform_interval_set():
    """Verify that setting :attr:`waveform_interval` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:INTerval 2", None)],
    ) as instr:
        instr.waveform_interval = 2


def test_waveform_interval_get():
    """Verify that reading :attr:`waveform_interval` parses the
    simulated instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:INTerval?", "2")],
    ) as instr:
        assert instr.waveform_interval == 2


def test_waveform_points_set():
    """Verify that setting :attr:`waveform_points` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:POINt 1400", None)],
    ) as instr:
        instr.waveform_points = 1400


def test_waveform_points_get():
    """Verify that reading :attr:`waveform_points` parses the simulated instrument response
    correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:POINt?", "1400")],
    ) as instr:
        assert instr.waveform_points == 1400


def test_waveform_max_points():
    """Verify that :attr:`waveform_max_points` can be set and read back correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:MAXPoint?", "14000000")],
    ) as instr:
        assert instr.waveform_max_points == 14000000


@pytest.mark.parametrize("value", ["BYTE", "WORD"])
def test_waveform_format_set(value):
    """Verify that setting :attr:`waveform_format` sends the expected SCPI command."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(f":WAVeform:WIDTh {value}", None)],
    ) as instr:
        instr.waveform_format = value


@pytest.mark.parametrize("value", ["BYTE", "WORD"])
def test_waveform_format_get(value):
    """Verify that reading :attr:`waveform_format` parses the simulated
    instrument response correctly."""
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:WIDTh?", value)],
    ) as instr:
        assert instr.waveform_format == value


def test_waveform_format_invalid_value_rejected():
    """Verify that assigning an invalid value to :attr:`waveform_format` raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.waveform_format = "FLOAT"  # type: ignore


def build_preamble_bytes(
    wave_array_count=1400,
    first_point=0,
    sparse_factor=1,
    vertical_gain_raw=0.04,
    vertical_offset_raw=0.1,
    code_per_div=480.0,
    adc_bits=16,
    horizontal_interval=1e-9,
    horizontal_offset=-2.5e-6,
    timebase_index=0,
    vertical_coupling_index=0,
    custom_probe_attenuation=None,
    probe_index=0,
    bandwidth_index=0,
    source_index=0,
):
    """Build preamble bytes."""
    buf = bytearray(345+11)
    struct.pack_into("<i", buf, 0x74, wave_array_count)
    struct.pack_into("<i", buf, 0x84, first_point)
    struct.pack_into("<i", buf, 0x88, sparse_factor)
    struct.pack_into("<f", buf, 0x9C, vertical_gain_raw)
    struct.pack_into("<f", buf, 0xA0, vertical_offset_raw)
    struct.pack_into("<f", buf, 0xA4, code_per_div)
    struct.pack_into("<h", buf, 0xAC, adc_bits)
    struct.pack_into("<f", buf, 0xB0, horizontal_interval)
    struct.pack_into("<d", buf, 0xB4, horizontal_offset)
    struct.pack_into("<h", buf, 0x144, timebase_index)
    struct.pack_into("<h", buf, 0x146, vertical_coupling_index)
    if custom_probe_attenuation is not None:
        struct.pack_into("<f", buf, 0x148, float(custom_probe_attenuation))
    else:
        struct.pack_into("<i", buf, 0x148, int(probe_index))
    struct.pack_into("<h", buf, 0x14E, bandwidth_index)
    struct.pack_into("<h", buf, 0x158, source_index)
    header = f"#9{len(buf):09d}".encode()
    return header + bytes(buf)


def build_data_block(payload: bytes) -> bytes:
    """Build data block."""
    length_str = str(len(payload)).encode()
    header = b"#" + str(len(length_str)).encode() + length_str
    return header + payload + b"\n\n"


def test_waveform_preamble_source_index_none():
    """Verify that :attr:`approx` can be set and read back correctly."""
    raw = build_preamble_bytes(
        wave_array_count=1400,
        first_point=0,
        sparse_factor=1,
        vertical_gain_raw=0.04,
        vertical_offset_raw=0.1,
        horizontal_interval=1e-9,
        horizontal_offset=-2.5e-6,
        timebase_index=0,
        vertical_coupling_index=1,  # AC
        probe_index=0,  # index 0 -> standard probe
        bandwidth_index=2,  # 200M
        source_index=12,  # 12 is not a valid source_index
    )

    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:PREamble?", raw),
            (":WAVeform:SOURce?", "C1")
         ],
    ) as instr:
        preamble = instr.waveform_preamble()

    assert preamble["points"] == 1400
    assert preamble["first_point"] == 0
    assert preamble["sparse_factor"] == 1
    assert preamble["vertical_gain"] == pytest.approx(0.04 * 0.1, rel=1e-6)
    assert preamble["vertical_offset"] == pytest.approx(0.1 * 0.1, rel=1e-6)
    assert preamble["code_per_div"] == pytest.approx(480.0)
    assert preamble["adc_bits"] == pytest.approx(16)
    assert preamble["horizontal_interval"] == pytest.approx(1e-9, rel=1e-6)
    assert preamble["horizontal_offset"] == pytest.approx(-2.5e-6)
    assert preamble["timebase"] == 200e-12
    assert preamble["probe_attenuation"] == 0.1
    assert preamble["vertical_coupling"] == "AC"
    assert preamble["bandwidth_limit"] == "200M"
    assert preamble["source"] == "C1"
    assert preamble["source_index_raw"] == 12


def test_waveform_preamble_standard_probe():
    """Verify that :attr:`approx` can be set and read back correctly."""
    raw = build_preamble_bytes(
        wave_array_count=1400,
        first_point=0,
        sparse_factor=1,
        vertical_gain_raw=0.04,
        vertical_offset_raw=0.1,
        horizontal_interval=1e-9,
        horizontal_offset=-2.5e-6,
        timebase_index=0,
        vertical_coupling_index=1,  # AC
        probe_index=0,  # index 0 -> standard probe
        bandwidth_index=2,  # 200M
        source_index=0,
    )

    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:PREamble?", raw)],
    ) as instr:
        preamble = instr.waveform_preamble()

    assert preamble["points"] == 1400
    assert preamble["first_point"] == 0
    assert preamble["sparse_factor"] == 1
    assert preamble["vertical_gain"] == pytest.approx(0.04 * 0.1, rel=1e-6)
    assert preamble["vertical_offset"] == pytest.approx(0.1 * 0.1, rel=1e-6)
    assert preamble["code_per_div"] == pytest.approx(480.0)
    assert preamble["adc_bits"] == pytest.approx(16)
    assert preamble["horizontal_interval"] == pytest.approx(1e-9, rel=1e-6)
    assert preamble["horizontal_offset"] == pytest.approx(-2.5e-6)
    assert preamble["timebase"] == 200e-12
    assert preamble["probe_attenuation"] == 0.1
    assert preamble["vertical_coupling"] == "AC"
    assert preamble["bandwidth_limit"] == "200M"
    assert preamble["source"] == "C1"
    assert preamble["source_index_raw"] == 0


def test_waveform_preamble_custom_probe_attenuation():
    """Verify that :attr:`approx` can be set and read back correctly."""
    custom_attenuation = 2.5
    raw = build_preamble_bytes(custom_probe_attenuation=custom_attenuation, source_index=0)

    with expected_protocol(
        TeledyneT3DSO3024HD,
        [(":WAVeform:PREamble?", raw)],
    ) as instr:
        preamble = instr.waveform_preamble()

    assert preamble["probe_attenuation"] == pytest.approx(custom_attenuation)


def test_waveform_preamble_unexpected_header_rejected():
    """Verify that assigning an invalid value to :attr:`waveform preamble unexpected header`
    raises a ``ValueError``."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [(":WAVeform:PREamble?", b"NOTABLOCK" + b"\x00" * 350)],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.waveform_preamble()


def test_waveform_data_byte_format():
    """Verify that :attr:`waveform_format` can be set and read back correctly."""
    payload = bytes([10, 251, 127, 128])  # -> 10, -5, 127, -128
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:WIDTh?", "BYTE"),
            (":WAVeform:DATA?", build_data_block(payload)),
            (":WAVeform:WIDTh?", "BYTE"),
        ],
    ) as instr:
        assert instr.waveform_format == "BYTE"
        codes = instr.waveform_data()

    assert list(codes) == [10, -5, 127, -128]


def test_waveform_data_word_format():
    """Verify that :attr:`waveform_format` can be set and read back correctly."""
    payload = struct.pack("<HH", 40000, 1000)
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:WIDTh?", "WORD"),
            (":WAVeform:DATA?", build_data_block(payload)),
            (":WAVeform:WIDTh?", "WORD"),
        ],
    ) as instr:
        assert instr.waveform_format == "WORD"
        codes = instr.waveform_data()

    assert list(codes) == [40000 - 65536, 1000]


def test_waveform_digital_data():
    """Verify that :attr:`waveform digital data` can be set and read back correctly."""
    payload = bytes([0b10110001])
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:POINt?", "8"),
            (":WAVeform:DATA?", build_data_block(payload))],
    ) as instr:
        bits = instr.waveform_digital_data()

    expected_bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="little")
    assert list(bits) == list(expected_bits)


def test_get_waveform_digital_source():
    """Verify that :attr:`get waveform digital source` can be set and read back correctly."""
    preamble_raw = build_preamble_bytes(
        wave_array_count=4,
        first_point=0,
        sparse_factor=1,
        horizontal_interval=1e-9,
        horizontal_offset=0.0,
        timebase_index=10,
        probe_index=20
    )
    payload = bytes([0b00001101])  # 8 bits
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:SOURce D0", None),
            (":WAVeform:SOURce?", "D0"),
            (":WAVeform:PREamble?", preamble_raw),
            (":WAVeform:POINt?", "8"),
            (":WAVeform:DATA?", build_data_block(payload)),
        ],
    ) as instr:
        time, logic = instr.get_waveform(source="D0")

    expected_logic = np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="little")
    assert list(logic) == list(expected_logic)

    timebase = 500e-9
    expected_time = -0.0 - (timebase * 10 / 2) + np.arange(len(expected_logic)) * 1e-9
    np.testing.assert_allclose(time, expected_time)


def test_get_waveform_analog_source():
    """Verify that :attr:`get waveform analog source` can be set and read back correctly."""
    preamble_raw = build_preamble_bytes(
        wave_array_count=2,
        first_point=0,
        sparse_factor=1,
        vertical_gain_raw=0.04,
        vertical_offset_raw=0.0,
        horizontal_interval=1e-9,
        horizontal_offset=0.0,
        timebase_index=10,
        probe_index=0,
        source_index=0,
    )
    payload = bytes([10, 20])
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:SOURce C1", None),
            (":WAVeform:SOURce?", "C1"),
            (":WAVeform:PREamble?", preamble_raw),
            (":WAVeform:DATA?", build_data_block(payload)),
            (":WAVeform:WIDTh?", "BYTE"),
            (":WAVeform:WIDTh?", "BYTE"),
        ],
    ) as instr:
        code_per_div = instr.channel_1.CODE_PER_DIV
        time, voltage = instr.get_waveform(source="C1")

    probe_attenuation = 0.1
    vertical_gain = 0.04 * probe_attenuation
    codes = np.array([10, 20], dtype=np.int16)
    expected_voltage = codes * (vertical_gain / code_per_div) - 0.0
    np.testing.assert_allclose(voltage, expected_voltage, rtol=1e-5)

    timebase = 500e-9
    expected_time = -0.0 - (timebase * 10 / 2) + np.arange(len(codes)) * 1e-9
    np.testing.assert_allclose(time, expected_time)


def test_get_waveform_analog_source_word():
    """Verify that :attr:`get waveform analog source word` can be set and read back correctly."""
    preamble_raw = build_preamble_bytes(
        wave_array_count=2,
        first_point=0,
        sparse_factor=1,
        vertical_gain_raw=0.04,
        vertical_offset_raw=0.0,
        horizontal_interval=1e-9,
        horizontal_offset=0.0,
        timebase_index=10,
        probe_index=0,
        source_index=0,
    )
    payload = struct.pack("<2h", 10, 20)
    with expected_protocol(
        TeledyneT3DSO3024HD,
        [
            (":WAVeform:SOURce C1", None),
            (":WAVeform:SOURce?", "C1"),
            (":WAVeform:PREamble?", preamble_raw),
            (":WAVeform:DATA?", build_data_block(payload)),
            (":WAVeform:WIDTh?", "WORD"),
            (":WAVeform:WIDTh?", "WORD"),
        ],
    ) as instr:
        code_per_div = instr.channel_1.CODE_PER_DIV
        time, voltage = instr.get_waveform(source="C1")

    probe_attenuation = 0.1
    vertical_gain = 0.04 * probe_attenuation
    codes = np.array([10, 20], dtype=np.int16)
    expected_voltage = codes * (vertical_gain / code_per_div) - 0.0
    np.testing.assert_allclose(voltage, expected_voltage, rtol=1e-5)

    timebase = 500e-9
    expected_time = -0.0 - (timebase * 10 / 2) + np.arange(len(codes)) * 1e-9
    np.testing.assert_allclose(time, expected_time)


def test_waveform_data_invalid_header():
    """Verify that :attr:`waveform data invalid header` can be set and read back correctly."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [
                (":WAVeform:DATA?", b'12'),
            ],
        ) as instr,
        pytest.raises(ValueError)
    ):
        instr.waveform_data()


def test_waveform_data_invalid_length():
    """Verify that :meth:`waveform_data` raises ValueError on a payload/length mismatch."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [
                (":WAVeform:DATA?", b'#15AAA'),
                (None, b'XX'),
            ],
        ) as instr,
        pytest.raises(ValueError)
    ):
        instr.waveform_data()


def test_get_waveform_f_source():
    """Verify that :attr:`get waveform function source is raising `NotImplementedError`."""
    with (
        expected_protocol(
            TeledyneT3DSO3024HD,
            [
                 (":WAVeform:SOURce?", "F1"),
            ],
        ) as instr,
        pytest.raises(NotImplementedError)
    ):
        instr.get_waveform()
