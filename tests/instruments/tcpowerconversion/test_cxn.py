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
from pymeasure.instruments.tcpowerconversion import CXN


def test_id():
    """Verify the communication of the id property."""
    with expected_protocol(
        CXN,
        [
            (
                b"C\x00Gi\x00\x01\x00\x00\x00\xf4",
                b"\x2aR\x00\x00\x10\x00\x01AG 0313 GTC  \x00\x03\x10",
            ),
        ],
    ) as inst:
        assert inst.id == "AG 0313 GTC"


def test_power():
    """Verify processing the power measurement."""
    with expected_protocol(
        CXN,
        [
            (
                b"C\x00GP\x00\x00\x00\x00\x00\xda",
                b"\x2aR\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x58",
            ),
        ],
    ) as inst:
        assert inst.power == (0.0, 0.0, 0.0)


def test_temperature():
    """Verify processing the temperature measurement."""
    with expected_protocol(
        CXN,
        [
            (
                b"C\x00GS\x00\x00\x00\x00\x00\xdd",
                b"\x2aR\x00\x00\x08\x00\x10\x00\xdd\x00\x04\x00\x03\x01\x4e",
            ),
        ],
    ) as inst:
        assert inst.temperature == pytest.approx(22.1)


def test_status():
    """Verify processing the status IntFlag."""
    with expected_protocol(
        CXN,
        [
            (
                b"C\x00GS\x00\x00\x00\x00\x00\xdd",
                b"\x2aR\x00\x00\x08\x00\x11\x00\xdd\x00\x04\x00\x03\x01\x4f",
            ),
        ],
    ) as inst:
        status = inst.status
        assert CXN.Status.EXTERNAL_RFSOURCE in status
        assert CXN.Status.RF_ENABLED in status
        assert CXN.Status.RF_ENABLED | CXN.Status.EXTERNAL_RFSOURCE == status


def test_power_limit():
    """Verify processing the power limit property"""
    with expected_protocol(
        CXN,
        [
            (
                b"C\x00Gp\x00\x00\x00\x00\x00\xfa",
                b"\x2aR\x00\x00\x144\xf8\x0b\xb8\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                b"4\xf8\x02\xbc\x10\x33",
            ),
        ],
    ) as inst:
        assert inst.power_limit == pytest.approx(300.0)


def test_manual_mode():
    """Verify processing the manual mode property"""
    with expected_protocol(
        CXN,
        [
            (
                b"C\x00GT\x00\x00\x00\x00\x00\xde",
                b"\x2aR\x00\x00\n\x00\x01\x01\xa9\x02v\x00\x00\x00\x00\x01\x7f",
            ),
        ],
    ) as inst:
        assert inst.manual_mode is True


@pytest.mark.parametrize("channel", range(1, 10))
def test_load_capacity_preset(channel):
    """Verify processing the load capacity propert via a Channel"""
    # here we use '%' for formating since encoding from strings makes troubles
    # with some values (e.g. \xff)
    cmd = b"C\x00GU\x00%c\x00\x00" % (channel)
    cmd += CXN._checksum(cmd)
    response = b"R\x00\x00\n\x00%c\x00\x32\x00\x32\xff\xff\xff\xff" % (channel)
    response += CXN._checksum(response)
    with expected_protocol(
        CXN,
        [
            (cmd, b"\x2a" + response),
        ],
    ) as inst:
        assert inst.channels[channel].load_capacity == 50
