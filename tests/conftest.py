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

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--device-address",
        action="store",
        default=None,
        dest="adapter",
        help=(
            "Pass an adapter string for connection to an instrument needed for a test, e.g. "
            "--device-address ASRL1::INSTR or --device-address TCPIP::192.168.0.123::INSTR"
        ),
    )


@pytest.fixture(scope="session")
def connected_device_address(pytestconfig):
    """
    Fixture to pass the address to a device for tests that require a connection to an instrument.

    Using this fixture in a test function will skip it when running pytest by default. The test will
    only run if a device address is provided with the --device-address option when invoking pytest.
    To run only relevant tests, use the -k option to select the desired tests.
    """
    address = pytestconfig.getoption("--device-address", skip=True)
    return address
