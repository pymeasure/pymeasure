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
from pymeasure.test import expected_protocol


def test_bwlimit():
    with expected_protocol(
        T3DSO3024HD,
        [
            (":CHANnel1:BWLimit 20M", None),  # (send CMD, answer=None )
            (":CHANnel1:BWLimit?", "20M"),  # (query, simulated answer)
        ],
    ) as instr:
        instr.channel_1.bwlimit = "20M"
        assert instr.channel_1.bwlimit == "20M"


def test_impedance_limits_scale_range():
    with expected_protocol(
        T3DSO3024HD,
        [
            (":CHANnel1:IMPedance FIFT", None),
            (":CHANnel1:SCALe 5.00E-01", None),
        ],
    ) as instr:
        instr.channel_1.set_impedance(50.0)
        instr.channel_1.scale = 0.5

        with pytest.raises(ValueError):
            # should raise a value error since impedance was set to 50.0
            instr.channel_1.scale = 2.0


def test_invert_set_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert ON", None)],
    ) as instr:
        instr.channel_1.invert = True


def test_invert_set_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert OFF", None)],
    ) as instr:
        instr.channel_1.invert = False


def test_invert_get_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert?", "ON")],
    ) as instr:
        assert instr.channel_1.invert is True


def test_invert_get_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:INVert?", "OFF")],
    ) as instr:
        assert instr.channel_1.invert is False


def test_invert_invalid_value_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.invert = "YES"  # type: ignore


def test_label_set():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel:TEXT MyLabel", None)],
    ) as instr:
        instr.channel_1.label_text = "MyLabel"


def test_label_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel:TEXT?", "MyLabel")],
    ) as instr:
        assert instr.channel_1.label_text == "MyLabel"


def test_label_exact_max_length_allowed():
    label_20_chars = "A" * 20
    with expected_protocol(
        T3DSO3024HD,
        [(f":CHANnel1:LABel:TEXT {label_20_chars}", None)],
    ) as instr:
        instr.channel_1.label_text = label_20_chars


def test_label_too_long_rejected():
    label_21_chars = "A" * 21
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label_text = label_21_chars


def test_offset_set():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:OFFSet -3.800E+00", None)],
    ) as instr:
        instr.channel_1.offset = -3.8


def test_offset_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:OFFSet?", "-3.8E+00")],
    ) as instr:
        assert instr.channel_1.offset == -3.8


def test_probe_set():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:PROBe VALue,1.00E+02", None)],
    ) as instr:
        instr.channel_1.probe = 100


def test_probe_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:PROBe?", "1.00E+02")],
    ) as instr:
        assert instr.channel_1.probe == 100.0


def test_probe_out_of_range_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.probe = 2e6


def test_unit_set_voltage():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:UNIT V", None)],
    ) as instr:
        instr.channel_1.unit = "V"


def test_unit_set_current():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:UNIT A", None)],
    ) as instr:
        instr.channel_1.unit = "A"


def test_unit_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:UNIT?", "A")],
    ) as instr:
        assert instr.channel_1.unit == "A"


def test_unit_invalid_value_rejected():
    with (
            expected_protocol(
                T3DSO3024HD,
                [],
            ) as instr,
            pytest.raises(ValueError),
        ):
            instr.channel_1.unit = "OHM"


def test_coupling_set_dc():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:COUPling DC", None)],
    ) as instr:
        instr.channel_1.coupling = "DC"


def test_coupling_set_ac():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:COUPling AC", None)],
    ) as instr:
        instr.channel_1.coupling = "AC"


def test_coupling_set_gnd():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:COUPling GND", None)],
    ) as instr:
        instr.channel_1.coupling = "GND"


def test_coupling_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:COUPling?", "AC")],
    ) as instr:
        assert instr.channel_1.coupling == "AC"


def test_coupling_invalid_value_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.coupling = "ACDC"


def test_label_set_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel ON", None)],
    ) as instr:
        instr.channel_1.label = True


def test_label_set_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel OFF", None)],
    ) as instr:
        instr.channel_1.label = False


def test_label_get_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel?", "ON")],
    ) as instr:
        assert instr.channel_1.label is True


def test_label_get_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel?", "OFF")],
    ) as instr:
        assert instr.channel_1.label is False


def test_label_invalid_value_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label = "YES"


def test_skew_set():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SKEW 5.00E-08", None)],
    ) as instr:
        instr.channel_1.skew = 5e-8


def test_skew_set_negative():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SKEW -1.00E-07", None)],
    ) as instr:
        instr.channel_1.skew = -1e-7


def test_skew_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SKEW?", "5.00E-08")],
    ) as instr:
        assert instr.channel_1.skew == 5e-8


def test_skew_out_of_range_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.skew = 2e-7


def test_switch_set_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SWITch ON", None)],
    ) as instr:
        instr.channel_1.switch = True


def test_switch_set_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SWITch OFF", None)],
    ) as instr:
        instr.channel_1.switch = False


def test_switch_get_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SWITch?", "ON")],
    ) as instr:
        assert instr.channel_1.switch is True


def test_switch_get_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SWITch?", "OFF")],
    ) as instr:
        assert instr.channel_1.switch is False


def test_switch_invalid_value_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.switch = "MAYBE"


def test_visible_set_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:VISible ON", None)],
    ) as instr:
        instr.channel_1.visible = True


def test_visible_set_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:VISible OFF", None)],
    ) as instr:
        instr.channel_1.visible = False


def test_visible_get_true():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:VISible?", "ON")],
    ) as instr:
        assert instr.channel_1.visible is True


def test_visible_get_false():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:VISible?", "OFF")],
    ) as instr:
        assert instr.channel_1.visible is False


def test_visible_invalid_value_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.visible = "MAYBE"


def test_scale_set():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SCALe 2.00E+00", None)],
    ) as instr:
        instr.channel_1.scale = 2.0


def test_scale_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:SCALe?", "2.00E+00")],
    ) as instr:
        assert instr.channel_1.scale == 2.0


def test_scale_out_of_range_rejected():
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.scale = 20.0
