#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
    """Verify the communication of the voltage getter."""
    with expected_protocol(
        MKS937B,
        [("@253PR1?", "@253ACK1.10e-9"),
         (None, b"FF")],
    ) as inst:
        inst.adapter.preprocess_reply = inst._extract_reply  # needed to workaround a bug
        assert inst.pressure1 == pytest.approx(1.1e-9)


def test_sensor_type():
    """Verify the communication of the voltage getter."""
    with expected_protocol(
        MKS937B,
        [("@253STB?", "@253ACKCP,NC"),
         (None, b"FF")],
    ) as inst:
        inst.adapter.preprocess_reply = inst._extract_reply  # needed to workaround a bug
        assert inst.sensor_typeB == ['Convection Pirani', 'no connection']


def test_ion_gauge_status():
    """Verify the communication of the voltage getter."""
    with expected_protocol(
        MKS937B,
        [("@253T1?", "@253ACKG"),
         (None, b"FF")],
    ) as inst:
        inst.adapter.preprocess_reply = inst._extract_reply  # needed to workaround a bug
        assert inst.ion_gauge_status1 == "Good"


def test_unit():
    """Verify the communication of the voltage getter."""
    with expected_protocol(
        MKS937B,
        [("@253U?", "@253ACKTORR"),
         (None, b"FF")],
    ) as inst:
        inst.adapter.preprocess_reply = inst._extract_reply  # needed to workaround a bug
        assert inst.unit == "Torr"


def test_power_enabled():
    """Verify the communication of the voltage getter."""
    with expected_protocol(
        MKS937B,
        [("@253CP1?", "@253ACKON"),
         (None, b"FF")],
    ) as inst:
        inst.adapter.preprocess_reply = inst._extract_reply  # needed to workaround a bug
        assert inst.power1_enabled is True
