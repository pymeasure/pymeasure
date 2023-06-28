#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.test import expected_protocol
from pymeasure.instruments.mksinst.mks937b import MKS937B


def test_pressure():
    """Verify the communication of the pressure getter."""
    with expected_protocol(
        MKS937B,
        [("@253PR1?", "@253ACK1.10e-9"),
         (None, b"FF")],
    ) as inst:
        assert inst.ch_1.pressure == pytest.approx(1.1e-9)


def test_ion_gauge_status():
    """Verify the communication of the ion gauge status getter."""
    with expected_protocol(
        MKS937B,
        [("@253T1?", "@253ACKG"),
         (None, b"FF")],
    ) as inst:
        assert inst.ch_1.ion_gauge_status == "Good"


def test_ion_gauge_status_invalid_channel():
    """Ion gauge status does not exist on all channels."""
    with expected_protocol(
        MKS937B,
        [],
    ) as inst:
        with pytest.raises(AttributeError):
            inst.ch_2.ion_gauge_status


def test_unit_setter():
    """Verify the communication of the unit setter."""
    with expected_protocol(
        MKS937B,
        [("@253U!TORR", "@253ACKTORR"),
         (None, b"FF")],
    ) as inst:
        inst.unit = "Torr"


def test_unit_getter():
    """Verify the communication of the unit getter."""
    with expected_protocol(
        MKS937B,
        [("@253U?", "@253ACKTORR"),
         (None, b"FF")],
    ) as inst:
        assert inst.unit == "Torr"


def test_power_enabled():
    """Verify the communication of the channel power getter."""
    with expected_protocol(
        MKS937B,
        [("@253CP1?", "@253ACKON"),
         (None, b"FF")],
    ) as inst:
        assert inst.ch_1.power_enabled is True
