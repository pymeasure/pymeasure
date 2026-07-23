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
from pymeasure.test import expected_protocol
from pymeasure.instruments.keysight import KeysightE3640A, KeysightE3643A, KeysightE3649A


# Protocol tests for single channel devices
def test_single_init():
    with expected_protocol(
            KeysightE3643A,
            [(b'VOLT:RANG P35V', None)],
    ):
        pass  # Verify the expected communication.


def test_single_current_limit_setter():
    with expected_protocol(
            KeysightE3643A,
            [(b'VOLT:RANG P35V', None),
             (b'CURR 0.6', None)],
    ) as inst:
        inst.current_limit = 0.6


def test_single_current_limit_getter():
    with expected_protocol(
            KeysightE3643A,
            [(b'VOLT:RANG P35V', None),
             (b'CURR?', b'+6.00000000E-01\n')],
    ) as inst:
        assert inst.current_limit == 0.6


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT:RANG P35V', None),
      (b'OUTP 1', None)],
     True),
    ([(b'VOLT:RANG P35V', None),
      (b'OUTP 0', None)],
     False),
))
def test_single_output_enabled_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3643A,
            comm_pairs,
    ) as inst:
        inst.output_enabled = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT:RANG P35V', None),
      (b'OUTP?', b'1\n')],
     True),
    ([(b'VOLT:RANG P35V', None),
      (b'OUTP?', b'0\n')],
     False),
))
def test_single_output_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3643A,
            comm_pairs,
    ) as inst:
        assert inst.output_enabled == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT:RANG P35V', None),
      (b'VOLT:RANG P35V', None)],
     'LOW'),
    ([(b'VOLT:RANG P35V', None),
      (b'VOLT:RANG P60V', None)],
     'HIGH'),
))
def test_single_range_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3643A,
            comm_pairs,
    ) as inst:
        inst.range = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT:RANG P35V', None),
      (b'VOLT:RANG?', b'P35V\n')],
     'LOW'),
    ([(b'VOLT:RANG P35V', None),
      (b'VOLT:RANG?', b'P60V\n')],
     'HIGH'),
))
def test_single_range_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3643A,
            comm_pairs,
    ) as inst:
        assert inst.range == value


def test_single_voltage_setpoint_setter():
    with expected_protocol(
            KeysightE3643A,
            [(b'VOLT:RANG P35V', None),
             (b'VOLT 15', None)],
    ) as inst:
        inst.voltage_setpoint = 15.0


def test_single_voltage_setpoint_getter():
    with expected_protocol(
            KeysightE3643A,
            [(b'VOLT:RANG P35V', None),
             (b'VOLT?', b'+1.50000000E+01\n')],
    ) as inst:
        assert inst.voltage_setpoint == 15.0


# Protocol tests for dual channel devices
def test_dual_init():
    with expected_protocol(
            KeysightE3649A,
            [(b'INST:NSEL 1;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:VOLT:RANG P35V', None)],
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'INST:NSEL 1;:VOLT:RANG P35V', None)],
     'LOW'),
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'INST:NSEL 1;:VOLT:RANG P60V', None)],
     'HIGH'),
))
def test_dual_range_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3649A,
            comm_pairs,
    ) as inst:
        inst.ch_1.range = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'INST:NSEL 1;:VOLT:RANG?', b'P35V\n')],
     'LOW'),
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'INST:NSEL 1;:VOLT:RANG?', b'P60V\n')],
     'HIGH'),
))
def test_dual_range_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3649A,
            comm_pairs,
    ) as inst:
        assert inst.ch_1.range == value


def test_dual_voltage_setpoint_setter():
    with expected_protocol(
            KeysightE3649A,
            [(b'INST:NSEL 1;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:VOLT:RANG P35V', None),
             (b'INST:NSEL 1;:VOLT 15', None)],
    ) as inst:
        inst.ch_1.voltage_setpoint = 15.0


def test_dual_voltage_setpoint_getter():
    with expected_protocol(
            KeysightE3649A,
            [(b'INST:NSEL 1;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:VOLT:RANG P35V', None),
             (b'INST:NSEL 1;:VOLT?', b'+1.50000000E+01\n')],
    ) as inst:
        assert inst.ch_1.voltage_setpoint == 15.0


def test_dual_current_limit_setter():
    with expected_protocol(
            KeysightE3649A,
            [(b'INST:NSEL 1;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:CURR 0.6', None)],
    ) as inst:
        inst.ch_2.current_limit = 0.6


def test_dual_current_limit_getter():
    with expected_protocol(
            KeysightE3649A,
            [(b'INST:NSEL 1;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:VOLT:RANG P35V', None),
             (b'INST:NSEL 2;:CURR?', b'+6.00000000E-01\n')],
    ) as inst:
        assert inst.ch_2.current_limit == 0.6


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'OUTP 1', None)],
     True),
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'OUTP 0', None)],
     False),
))
def test_dual_output_enabled_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3649A,
            comm_pairs,
    ) as inst:
        inst.output_enabled = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'OUTP?', b'1\n')],
     True),
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b'OUTP?', b'0\n')],
     False),
))
def test_dual_output_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3649A,
            comm_pairs,
    ) as inst:
        assert inst.output_enabled == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b':OUTP:TRAC 1', None)],
     True),
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b':OUTP:TRAC 0', None)],
     False),
))
def test_tracking_enabled_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3649A,
            comm_pairs,
    ) as inst:
        inst.tracking_enabled = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b':OUTP:TRAC?', b'1\n')],
     True),
    ([(b'INST:NSEL 1;:VOLT:RANG P35V', None),
      (b'INST:NSEL 2;:VOLT:RANG P35V', None),
      (b':OUTP:TRAC?', b'0\n')],
     False),
))
def test_tracking_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3649A,
            comm_pairs,
    ) as inst:
        assert inst.tracking_enabled == value


# Protocol tests for range mapping of low voltage devices
def test_low_voltage_init():
    with expected_protocol(
            KeysightE3640A,
            [(b'VOLT:RANG P8V', None)],
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT:RANG P8V', None),
      (b'VOLT:RANG P8V', None)],
     'LOW'),
    ([(b'VOLT:RANG P8V', None),
      (b'VOLT:RANG P20V', None)],
     'HIGH'),
))
def test_low_voltage_range_setter(comm_pairs, value):
    with expected_protocol(
            KeysightE3640A,
            comm_pairs,
    ) as inst:
        inst.range = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT:RANG P8V', None),
      (b'VOLT:RANG?', b'P8V\n')],
     'LOW'),
    ([(b'VOLT:RANG P8V', None),
      (b'VOLT:RANG?', b'P20V\n')],
     'HIGH'),
))
def test_low_voltage_range_getter(comm_pairs, value):
    with expected_protocol(
            KeysightE3640A,
            comm_pairs,
    ) as inst:
        assert inst.range == value
