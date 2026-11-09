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

from pymeasure.instruments.purephotonics import PPCL300, OperationMode
from pymeasure.instruments.purephotonics.itla import checksum
from pymeasure.test import expected_protocol


def p(hex_string):
    """Convert a hex string like '54 00 00 10' to bytes."""
    return bytes.fromhex(hex_string)


def read(register):
    """Create the packet to read a register."""
    return PPCL300._packet(register)


def write(register, data):
    """Create the packet to write a register."""
    return PPCL300._packet(register, data, write=True)


def reply(register, data=0, status=0):
    """Create a valid answer packet of the module."""
    packet = bytearray([status | 0x04, register, (data >> 8) & 0xFF, data & 0xFF])
    packet[0] |= checksum(packet) << 4
    return bytes(packet)


def test_operation_mode_setter():
    """Example of the Pure Photonics operating guide (answer: command pending)."""
    with expected_protocol(PPCL300, [(p("A1 90 00 02"), p("B3 90 01 00"))]) as inst:
        inst.operation_mode = OperationMode.WHISPER


def test_operation_mode_getter():
    with expected_protocol(PPCL300, [(p("90 90 00 00"), p("D4 90 00 00"))]) as inst:
        assert inst.operation_mode == OperationMode.DITHER


def test_operation_mode_invalid():
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError):
        inst.operation_mode = 3


def test_sweep():
    """Example of the Pure Photonics operating guide."""
    with expected_protocol(
        PPCL300,
        [
            (p("41 E4 00 3C"), p("50 E4 00 3C")),
            (p("B1 E5 00 01"), p("A0 E5 00 01")),
            (p("A1 E5 00 00"), p("B0 E5 00 00")),
        ],
    ) as inst:
        inst.sweep_range = 60e9
        inst.sweep_enabled = True
        inst.sweep_enabled = False


@pytest.mark.parametrize("data, offset", [("00 1F", 3.1e9), ("FF E1", -3.1e9)])
def test_sweep_offset(data, offset):
    response = bytearray(p(f"04 E6 {data}"))
    response[0] |= checksum(response) << 4
    with expected_protocol(PPCL300, [(p("80 E6 00 00"), bytes(response))]) as inst:
        assert inst.sweep_offset == pytest.approx(offset)


def test_sweep_rate():
    with expected_protocol(PPCL300, [(write(0xF1, 20000), reply(0xF1, 20000))]) as inst:
        inst.sweep_rate = 20e9


def test_sweep_rate_invalid():
    with expected_protocol(PPCL300, []) as inst, pytest.raises(ValueError):
        inst.sweep_rate = -1


def test_firmware_version():
    """Release string of a PPCL300, read once and cached."""
    data = b"PV 2.0.0:HW 1.0.1:FW 8.0.9:AS C1:OT 2.2.0\x00"
    pairs = [(read(0x06), reply(0x06, len(data), status=2))]
    pairs += [
        (read(0x0B), reply(0x0B, int.from_bytes(data[i : i + 2].ljust(2, b"\x00"), "big")))
        for i in range(0, len(data), 2)
    ]
    with expected_protocol(PPCL300, pairs) as inst:
        assert inst.firmware_version == "8.0.9"
        assert inst.firmware_version == "8.0.9"
