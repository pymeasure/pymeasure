#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.inficon.sqm160 import calculate_checksum, SQM160


def test_checksum():
    """Verify the calculate_checksum function."""
    # test against values documented in the manual
    assert calculate_checksum(b'#@') == b'O7'
    assert calculate_checksum(b'$C?') == b'g/'


def test_firmware_version():
    """Verify the communication of the firmware version."""
    with expected_protocol(
            SQM160,
            [(b"!#@O7", b"!0AMON Ver 4.13Uw"), ],
    ) as inst:
        assert inst.firmware_version == "MON Ver 4.13"


def test_number_of_channels():
    """Verify the communication of the number of channels."""
    with expected_protocol(
            SQM160,
            [(b"!#JO8", b"!%A6v\x86"), ],
    ) as inst:
        assert inst.number_of_channels == 6


def test_average_rate():
    """Verify reading of the average rate."""
    with expected_protocol(
            SQM160,
            [(b"!#M\x8e\x8a", b"!*A 0.01 i?"), ],
    ) as inst:
        assert inst.average_rate == pytest.approx(0.01)


def test_average_thickness():
    """Verify reading of the average rate."""
    with expected_protocol(
            SQM160,
            [(b"!#O\x8f9", b"!+A 0.000 Jo"), ],
    ) as inst:
        assert inst.average_thickness == pytest.approx(0.0)


def test_channel_rate():
    """Verify reading of the rate of a channel."""
    with expected_protocol(
            SQM160,
            [(b"!%L1?\x85{", b"!*A 0.00 [d"), ],
    ) as inst:
        assert inst.sensor_1.rate == pytest.approx(0.0)


def test_channel_frequency():
    """Verify reading of the frequency of a channel."""
    with expected_protocol(
            SQM160,
            [(b"!$P1Z\x91", b"!/A5875830.230:X"), ],
    ) as inst:
        assert inst.sensor_1.frequency == pytest.approx(5875830.23)
