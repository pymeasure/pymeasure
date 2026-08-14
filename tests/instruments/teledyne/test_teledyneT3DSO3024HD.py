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
            (":CHANnel1:SCALe 5.000E-01", None),
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
        instr.channel_1.label = "MyLabel"


def test_label_get():
    with expected_protocol(
        T3DSO3024HD,
        [(":CHANnel1:LABel:TEXT?", "MyLabel")],
    ) as instr:
        assert instr.channel_1.label == "MyLabel"


def test_label_exact_max_length_allowed():
    label_20_chars = "A" * 20
    with expected_protocol(
        T3DSO3024HD,
        [(f":CHANnel1:LABel:TEXT {label_20_chars}", None)],
    ) as instr:
        instr.channel_1.label = label_20_chars


def test_label_too_long_rejected():
    label_21_chars = "A" * 21
    with (
        expected_protocol(
            T3DSO3024HD,
            [],
        ) as instr,
        pytest.raises(ValueError),
    ):
        instr.channel_1.label = label_21_chars


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
