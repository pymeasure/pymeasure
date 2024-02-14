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
from pymeasure.instruments.mksinst.mks974b import MKS974B, Unit


def test_device_type():
    """Verify the communication of the device type."""
    with expected_protocol(
        MKS974B,
        [("@253DT?", "@253ACKQUADMAG"),
         (None, b"FF")],
    ) as inst:
        assert inst.device_type == "QUADMAG"


def test_status():
    """Verify the communication of the status."""
    with expected_protocol(
        MKS974B,
        [("@253T?", "@253ACKO"),
         (None, b"FF")],
    ) as inst:
        assert inst.status == "Ok"


def test_pressure():
    """Verify the communication of the pressure getter."""
    with expected_protocol(
        MKS974B,
        [("@253PR4?", "@253ACK1.234E-3"),
         (None, b"FF")],
    ) as inst:
        assert inst.pressure == pytest.approx(1.234e-3)


def test_pirani_pressure():
    """Verify the communication of the pirani pressure getter."""
    with expected_protocol(
        MKS974B,
        [("@253PR1?", "@253ACK1.23E-3"),
         (None, b"FF")],
    ) as inst:
        assert inst.pirani_pressure == pytest.approx(1.23e-3)


def test_unit_setter():
    """Verify the communication of the unit setter."""
    with expected_protocol(
        MKS974B,
        [("@253U!PASCAL", "@253ACKPASCAL"),
         (None, b"FF")],
    ) as inst:
        inst.unit = Unit.Pa


def test_unit_getter():
    """Verify the communication of the unit getter."""
    with expected_protocol(
        MKS974B,
        [("@253U?", "@253ACKTORR"),
         (None, b"FF")],
    ) as inst:
        assert inst.unit == Unit.Torr


def test_switch_enabled():
    """Verify the communication of the user swith getter."""
    with expected_protocol(
        MKS974B,
        [("@253SW?", "@253ACKON"),
         (None, b"FF")],
    ) as inst:
        assert inst.switch_enabled is True


def test_relay_value():
    """Verify the communication of the relay setpoint getter."""
    with expected_protocol(
        MKS974B,
        [("@253SP1?", "@253ACK2.00E+1"),
         (None, b"FF")],
    ) as inst:
        assert inst.relay_1.setpoint == pytest.approx(2.00e1)


def test_relay_direction():
    """Verify the communication of the relay direction."""
    with expected_protocol(
        MKS974B,
        [("@253SD2?", "@253ACKBELOW"),
         (None, b"FF")],
    ) as inst:
        assert inst.relay_2.direction == "BELOW"


def test_relay_enabled():
    """Verify the communication of the relay enabled property."""
    with expected_protocol(
        MKS974B,
        [("@253EN3?", "@253ACKPIR"),
         (None, b"FF")],
    ) as inst:
        assert inst.relay_3.enabled == "pirani"
