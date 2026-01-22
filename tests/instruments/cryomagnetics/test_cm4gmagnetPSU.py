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
from pymeasure.instruments.cryomagnetics import Cryomagnetics4G100


def test_init():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G')],
    ):
        pass  # Verify the expected communication.


def test_fast_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RATE? 5', b'0.0290')],
    ) as inst:
        assert inst.fast_rate == 0.029


def test_identity_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'*IDN?', b'ICE Oxford,4G,8423,1.67,324')],
    ) as inst:
        assert inst.identity == ['ICE Oxford', '4G', 8423.0, 1.67, 324.0]


def test_magnet_current_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'UNITS A;IMAG?', b'0.0000A')],
    ) as inst:
        assert inst.magnet_current == 0.0


def test_magnet_voltage_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'VMAG?', b'-0.001V')],
    ) as inst:
        assert inst.magnet_voltage == -0.001


def test_name_setter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'NAME BIG YELLOW MAGNET', None)],
    ) as inst:
        inst.name = 'BIG YELLOW MAGNET'


def test_name_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'NAME?', b'BIG YELLOW MAGNE')],
    ) as inst:
        assert inst.name == 'BIG YELLOW MAGNE'


def test_output_current_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'UNITS A;IOUT?', b'0.0000A')],
    ) as inst:
        assert inst.output_current == 0.0


def test_output_voltage_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'VOUT?', b'0.000V')],
    ) as inst:
        assert inst.output_voltage == 0.0


def test_persistent_switch_heater_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'PSHTR?', b'0')],
    ) as inst:
        assert inst.persistent_switch_heater == 'OFF'


def test_range_1_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RATE? 0', b'0.0010')],
    ) as inst:
        assert inst.range_1_rate == 0.001


def test_range_2_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RATE? 1', b'0.0010')],
    ) as inst:
        assert inst.range_2_rate == 0.001


def test_range_3_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RATE? 2', b'0.0010')],
    ) as inst:
        assert inst.range_3_rate == 0.001


def test_range_4_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RATE? 3', b'0.0010')],
    ) as inst:
        assert inst.range_4_rate == 0.001


def test_range_5_rate_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RATE? 4', b'0.0010')],
    ) as inst:
        assert inst.range_5_rate == 0.001


def test_range_boundary_0_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RANGE? 0', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_0 == 1.0


def test_range_boundary_1_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RANGE? 1', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_1 == 1.0


def test_range_boundary_2_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RANGE? 2', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_2 == 1.0


def test_range_boundary_3_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RANGE? 3', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_3 == 1.0


def test_range_boundary_4_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'RANGE? 4', b'1.0000')],
    ) as inst:
        assert inst.range_boundary_4 == 1.0


def test_sweep_lower_limit_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'UNITS A;LLIM?', b'-0.1000A')],
    ) as inst:
        assert inst.sweep_lower_limit == -0.1


def test_sweep_mode_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'SWEEP?', b'Standby')],
    ) as inst:
        assert inst.sweep_mode == 'STANDBY'


def test_sweep_upper_limit_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'UNITS A;ULIM?', b'0.1000A')],
    ) as inst:
        assert inst.sweep_upper_limit == 0.1


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
      (b'NAME?', b'CRYOMAGNETICS 4G'),
      (b'UNITS G', None)],
     'G'),
    ([(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
      (b'NAME?', b'CRYOMAGNETICS 4G'),
      (b'UNITS A', None)],
     'A'),
))
def test_units_setter(comm_pairs, value):
    with expected_protocol(
            Cryomagnetics4G100,
            comm_pairs,
    ) as inst:
        inst.units = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
      (b'NAME?', b'CRYOMAGNETICS 4G'),
      (b'UNITS?', b'kG')],
     'kG'),
    ([(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
      (b'NAME?', b'CRYOMAGNETICS 4G'),
      (b'UNITS?', b'A')],
     'A'),
))
def test_units_getter(comm_pairs, value):
    with expected_protocol(
            Cryomagnetics4G100,
            comm_pairs,
    ) as inst:
        assert inst.units == value


def test_usb_error_report_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'ERROR?', b'0')],
    ) as inst:
        assert inst.usb_error_report is False


def test_voltage_limit_getter():
    with expected_protocol(
            Cryomagnetics4G100,
            [(b'NAME Cryomagnetics 4G Magnet Power Supply', None),
             (b'NAME?', b'CRYOMAGNETICS 4G'),
             (b'VLIM?', b'5.000V')],
    ) as inst:
        assert inst.voltage_limit == 5.0
