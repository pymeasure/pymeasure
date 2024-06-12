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

import logging

import pytest

from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.keysight import KeysightE5071C

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


@pytest.fixture(scope="module")
def keysighte5071c(connected_device_address):
    try:
        # This allows a PrologixAdapter to be used for running the tests as well
        #  `pytest --device-address PrologixAdapter,ASRL3::INSTR,17 -k
        # "test_keysightE5071C_with_device"`

        if "PrologixAdapter" not in connected_device_address:
            vna = KeysightE5071C(connected_device_address)
        else:
            _, prologix_address, gpib_address, *other_address_info = connected_device_address.split(
                ","
            )

            prologix = PrologixAdapter(
                resource_name=prologix_address,
                visa_library="@py",
                auto=1,
                address=int(gpib_address),
            )

            # need to ensure `eot_enable` is set to zero otherwise you will have to read twice to
            # get rid of the extra new line character
            prologix.write("++eot_enable 0")
            vna = KeysightE5071C(adapter=prologix)

    except IOError:
        print("Not able to connect to vna")
        assert False

    yield vna
    del vna


def test_keysightE5071C_with_device_reset(keysighte5071c):
    keysighte5071c.reset()


def test_keysightE5071C_with_device_id(keysighte5071c):
    # Not sure if Keysight E5071C have updated the firmware to reflect the Keysight name.
    assert keysighte5071c.id == ["Agilent Technologies", "E5071C", "SG46500441", "B.13.10"]
    assert keysighte5071c.manu == "Agilent Technologies"
    assert keysighte5071c.model == "E5071C"
    assert keysighte5071c.fw == "B.13.10"
    assert keysighte5071c.sn == "SG46500441"
    # options


def test_keysightE5071C_with_device_channels(keysighte5071c):
    assert keysighte5071c.ch_1.get_active_channel == 1


def test_keysightE5071C_with_device_scan_points(keysighte5071c):
    assert keysighte5071c.ch_1.scan_points == 201


def test_keysightE5071C_with_device_averaging(keysighte5071c):
    assert keysighte5071c.ch_1.averaging_enabled is False


# def test_keysightE5071C_with_device_frequencies(keysighte5071c):


# def test_keysightE5071C_with_device_scan(keysighte5071c):


# def test_keysightE5071C_with_device_data_complex(keysighte5071c):


# def test_keysightE5071C_with_device_shutdown(keysighte5071c):


# def test_keysightE5071C_with_device_warmup_complete(keysighte5071c):


# def test_keysightE5071C_with_device_emit_beeps(keysighte5071c):


# def test_keysightE5071C_with_device_output_power(keysighte5071c):


# def test_keysightE5071C_with_device_triggering(keysighte5071c):


# def test_keysightE5071C_with_device_windows(keysighte5071c):


# def test_keysightE5071C_with_device_sweep(keysighte5071c):
