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

# Expected Modbus TCP frames were generated with the pymodbus library.

import pytest

from pymeasure.instruments.eurotherm import EurothermEPC3000
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(EurothermEPC3000, [], tcp=True):
        pass


def test_process_value():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\x06\x01\x03\x80\x02\x00\x02",
          b"\x00\x01\x00\x00\x00\x07\x01\x03\x04C\x96@\x00")],
        tcp=True,
    ) as inst:
        assert inst.process_value == 300.5


def test_transaction_increments():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\x06\x01\x03\x06\x89\x00\x01",
          b"\x00\x01\x00\x00\x00\x05\x01\x03\x02\x00\x01"),
         (b"\x00\x02\x00\x00\x00\x0b\x01\x10\x80\x04\x00\x02\x04C\x96@\x00",
          b"\x00\x02\x00\x00\x00\x06\x01\x10\x80\x04\x00\x02")],
        tcp=True,
    ) as inst:
        assert inst.ramp_done is True
        inst.target_setpoint = 300.5


def test_standby_enabled_setter():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\t\x01\x10\x04=\x00\x01\x02\x00\x01",
          b"\x00\x01\x00\x00\x00\x06\x01\x10\x04=\x00\x01")],
        tcp=True,
    ) as inst:
        inst.standby_enabled = True


def test_modbus_exception():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\x06\x01\x03\x06\x89\x00\x01",
          b"\x00\x01\x00\x00\x00\x03\x01\x83\x02")],
        tcp=True,
    ) as inst, pytest.raises(ValueError, match="Illegal data address"):
        _ = inst.ramp_done


def test_unexpected_transaction():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\x06\x01\x03\x06\x89\x00\x01",
          b"\x00\x05\x00\x00\x00\x05\x01")],
        tcp=True,
    ) as inst, pytest.raises(ConnectionError, match="transaction"):
        _ = inst.ramp_done


def test_remote_setpoint_setter():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\x0b\x01\x10\x82*\x00\x02\x04C\x16\x00\x00",
          b"\x00\x01\x00\x00\x00\x06\x01\x10\x82*\x00\x02")],
        tcp=True,
    ) as inst:
        inst.remote_setpoint = 150


def test_ramp_units():
    with expected_protocol(
        EurothermEPC3000,
        [(b"\x00\x01\x00\x00\x00\x06\x01\x03\x02\x13\x00\x01",
          b"\x00\x01\x00\x00\x00\x05\x01\x03\x02\x00\x01")],
        tcp=True,
    ) as inst:
        assert inst.ramp_units == "mins"
