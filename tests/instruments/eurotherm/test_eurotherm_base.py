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

# Expected frames were generated with the minimalmodbus library.

import pytest

from pymeasure.instruments.eurotherm import EurothermBase
from pymeasure.instruments.eurotherm.eurotherm_base import crc16
from pymeasure.test import expected_protocol


def test_crc16():
    # Example from the Modbus over serial line specification.
    assert crc16(b"\x02\x07") == b"\x41\x12"


def test_init():
    with expected_protocol(EurothermBase, []):
        pass


def test_process_value():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x03\x80\x02\x00\x02L\x0b", b"\x01\x03\x04C\x96@\x00>[")],
    ) as inst:
        assert inst.process_value == 300.5


def test_target_setpoint_setter():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x10\x80\x04\x00\x02\x04C\x96@\x00W\xf2", b"\x01\x10\x80\x04\x00\x02)\xc9")],
    ) as inst:
        inst.target_setpoint = 300.5


def test_active_setpoint():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x03\x00\x0f\x00\x01\xb4\t", b"\x01\x03\x02\x00\x01y\x84")],
    ) as inst:
        assert inst.active_setpoint == 2


def test_active_setpoint_setter():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x10\x00\x0f\x00\x01\x02\x00\x01go", b"\x01\x10\x00\x0f\x00\x011\xca")],
    ) as inst:
        inst.active_setpoint = 2


def test_active_setpoint_invalid():
    with expected_protocol(EurothermBase, []) as inst, pytest.raises(ValueError):
        inst.active_setpoint = 3


def test_modbus_exception():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x03\x00\x0f\x00\x01\xb4\t", b"\x01\x83\x02\xc0\xf1")],
    ) as inst, pytest.raises(ValueError, match="Illegal data address"):
        _ = inst.active_setpoint


def test_crc_error():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x03\x00\x0f\x00\x01\xb4\t", b"\x01\x03\x02\x00\x01y\x85")],
    ) as inst, pytest.raises(ConnectionError, match="CRC"):
        _ = inst.active_setpoint


def test_set_error():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x10\x00\x0f\x00\x01\x02\x00\x01go", b"\x01\x90\x03\x0c\x01")],
    ) as inst, pytest.raises(ValueError, match="Illegal data value"):
        inst.active_setpoint = 2


def test_wrong_address():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x03\x00\x0f\x00\x01\xb4\t", b"\x02\x03")],
    ) as inst, pytest.raises(ConnectionError, match="unexpected address"):
        _ = inst.active_setpoint


def test_proportional_band_setter():
    with expected_protocol(
        EurothermBase,
        [(b"\x01\x10\x80\x0c\x00\x02\x04AH\x00\x00\x06\x16", b"\x01\x10\x80\x0c\x00\x02\xa8\x0b")],
    ) as inst:
        inst.proportional_band = 12.5
