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

from pymeasure.instruments import Instrument, SCPIMixin


class SCPIDevice(SCPIMixin, Instrument):
    def __init__(self, adapter, name="SCPI Compatible Device", **kwargs):
        super().__init__(adapter, name, **kwargs)


@pytest.fixture(scope="module")
def scpi_device(connected_device_address):
    scpi_device = SCPIDevice(connected_device_address)
    scpi_device.clear()
    return scpi_device


def test_complete(scpi_device):
    assert scpi_device.complete == "1"


def test_status(scpi_device):
    assert scpi_device.status


def test_options(scpi_device):
    assert scpi_device.options


def test_id(scpi_device):
    assert scpi_device.id


def test_next_error(scpi_device):
    err = scpi_device.next_error
    assert int(err[0]) == 0


def test_reset(scpi_device):
    scpi_device.reset()
