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
from pymeasure.instruments.thyracont import SmartlineV1
from pymeasure.instruments.thyracont.smartline_v1 import calculate_checksum


def test_calculate_checksum_basics():
    for i in range(0, 64):
        assert (i + 64) == ord(calculate_checksum(chr(i)))
    for i in range(64, 128):
        assert i == ord(calculate_checksum(chr(i)))


@pytest.mark.parametrize("msg, chksum", (
        ("001T", "e"),  # command from SmartlineV1
        ("001M982122", "V"),  # msg from SmartlineV1
        ("0010MV00", "D"),  # command from SmartlineV2
        ("0011MV079.734e2", "h"),  # msg from SmartlineV2
))
def test_calculate_checksum(msg, chksum):
    assert chksum == calculate_checksum(msg)


def test_pressure():
    """Verify the communication of the pressure getter."""
    with expected_protocol(
        SmartlineV1,
        [("001M^", "001M982122V"), ],
    ) as inst:
        assert inst.pressure == pytest.approx(982.1)


def test_device_type():
    """Verify the communication of the Instruments type getter."""
    with expected_protocol(
        SmartlineV1,
        [("001Te", "001TVSM207t"), ],
    ) as inst:
        assert inst.device_type == "VSM207"


def test_cathode_enable():
    """Verify the communication of the hot/cold cathode control."""
    with expected_protocol(
        SmartlineV1,
        [("001IZ", "001I1K"), ],
    ) as inst:
        assert inst.cathode_enabled is True


def test_cathode_enable_error():
    """Verify the raised error in case of a set error."""
    with expected_protocol(
        SmartlineV1,
        [("001i0j", "001NO_DEF\\"), ],
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.cathode_enabled = False


def test_display_unit():
    """Verify the communication of the unit property."""
    with expected_protocol(
        SmartlineV1,
        [("001Uf", "001U000000F"), ],
    ) as inst:
        assert inst.display_unit == "mbar"
