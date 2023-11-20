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

from pymeasure.instruments.hp import HP437B
from pymeasure.instruments.hp.hp437b import SensorType


def test_calibrate():
    with expected_protocol(
            HP437B,
            [("CL99.9PCT", None)],
    ) as instr:
        instr.calibrate(99.9)


def test_calibration_factor():
    with expected_protocol(
            HP437B,
            [("KB99.9PCT", None),
             ("ERR?", "000")],
    ) as instr:
        instr.calibration_factor = 99.9


def test_display_user_message():
    with expected_protocol(
            HP437B,
            [("DU TEST        ", None)],
    ) as instr:
        instr.display_user_message = "TEST"


def test_duty_cycle_enabled():
    with expected_protocol(
            HP437B,
            [("DC1", None),
             ("ERR?", "000"),
             ("SM", "AAaaBBCCccDDddEFGHIJKLMN1P")],
    ) as instr:
        instr.duty_cycle_enabled = True
        assert instr.duty_cycle_enabled is True


def test_duty_cycle():
    with expected_protocol(
            HP437B,
            [("DY99.999PCT", None),
             ("ERR?", "000")],
    ) as instr:
        instr.duty_cycle = 0.99999


def test_frequency():
    with expected_protocol(
            HP437B,
            [("FR099.9000GZ", None),
             ("ERR?", "000")],
    ) as instr:
        instr.frequency = 99.9e9


@pytest.mark.parametrize('resolution', [(1, 1), (0.1, 2), (0.01, 3)])
def test_resolution_linear(resolution):
    value, code = resolution
    with expected_protocol(
            HP437B,
            [("SM", "000000110017000A0002000000"),
             ("RE%dEN" % code, None),
             ("ERR?", "000")],
    ) as instr:
        instr.resolution = value


@pytest.mark.parametrize('resolution', [(0.1, 1), (0.01, 2), (0.001, 3)])
def test_resolution_logarithmic(resolution):
    value, code = resolution
    with expected_protocol(
            HP437B,
            [("SM", "000000110017001A0002000001"),
             ("RE%dEN" % code, None),
             ("ERR?", "000")],
    ) as instr:
        instr.resolution = value


@pytest.mark.parametrize('sensor_type', [e for e in SensorType])
def test_sensor_type(sensor_type):
    with expected_protocol(
            HP437B,
            [("SE%dEN" % int(sensor_type.value), None),
             ("ERR?", "000")],
    ) as instr:
        instr.sensor_type = sensor_type
