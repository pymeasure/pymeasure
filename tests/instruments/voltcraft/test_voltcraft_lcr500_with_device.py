#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

# Test generator for the Voltcraft LCR-500 instrument.
# Connects to a real device, exercises all properties, and writes
# protocol-based unit tests to test_voltcraft_lcr500.py.
#
# Usage:
# $ pytest tests/instruments/voltcraft/testgenerator_voltcraft_lcr500.py \
#     --device-address "USB0::0x0483::0x5740::48EF5468374B::INSTR"

import os
from time import sleep

import pytest
from pymeasure.generator import Generator
from pymeasure.instruments.voltcraft import LCR500

TEST_FREQUENCIES = [100, 120, 400, 1_000, 4_000, 10_000, 40_000, 50_000, 75_000, 100_000]
MAIN_PARAMETERS = ["r", "l", "c", "z", "auto"]
SECONDARY_PARAMETERS = ["x", "q", "d", "esr", "theta"]
MEASUREMENT_RANGES = ["auto", 10, 100, 1_000, 10_000, 100_000]
SIGNAL_LEVELS = [300, 600]


@pytest.fixture(scope="module")
def generator():
    return Generator()


@pytest.fixture(scope="module")
def lcr500(connected_device_address, generator):
    instr = generator.instantiate(
        LCR500,
        connected_device_address,
        "voltcraft",
        adapter_kwargs={},
    )
    return instr


def test_id(lcr500):
    assert lcr500.id is not None


@pytest.mark.parametrize("freq", TEST_FREQUENCIES)
def test_frequency(lcr500, freq):
    lcr500.frequency = freq
    assert lcr500.frequency == freq


@pytest.mark.parametrize("param", MAIN_PARAMETERS)
def test_main_parameter(lcr500, param):
    lcr500.main_parameter = param
    assert lcr500.main_parameter == param


@pytest.mark.parametrize("param", SECONDARY_PARAMETERS)
def test_secondary_parameter(lcr500, param):
    lcr500.secondary_parameter = param
    assert lcr500.secondary_parameter == param


@pytest.mark.parametrize("rng", MEASUREMENT_RANGES)
def test_measurement_range(lcr500, rng):
    lcr500.measurement_range = rng
    assert lcr500.measurement_range == rng


@pytest.mark.parametrize("level", SIGNAL_LEVELS)
def test_level(lcr500, level):
    lcr500.level = level
    assert lcr500.level == level


@pytest.mark.parametrize("mode", [True, False])
def test_equivalent_circuit_serial_enabled(lcr500, mode):
    lcr500.equivalent_circuit_serial_enabled = mode
    assert lcr500.equivalent_circuit_serial_enabled == mode


def test_fetch(lcr500):
    sleep(0.5)  # Make sure system is ready for measurement
    value = lcr500.fetch
    assert isinstance(value, list)
    assert len(value) == 3
    assert all(isinstance(v, float) for v in value)


def test_write_protocol_tests(lcr500, generator):
    """Write the generated protocol-based unit tests to file."""
    output_path = os.path.join(os.path.dirname(__file__), "test_voltcraft_lcr500.py")
    generator.write_file(output_path)
