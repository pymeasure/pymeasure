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

import logging
from contextlib import contextmanager
from time import sleep

import pytest
from pyvisa.errors import VisaIOError

from pymeasure.adapters import PrologixAdapter
from pymeasure.test import expected_protocol
from pymeasure.generator import Generator
from pymeasure.instruments.hp import HP8753E

# pytest.skip("Only work with connected hardware", allow_module_level=True)


@contextmanager
def init_prologix_adapter():
    try:
        prologix = PrologixAdapter(resource_name="ASRL4::INSTR", address=16, visa_library="@py")
        # prologix.auto = 1
        # prologix.connection.query_delay = 0
        # prologix.gpib_read_timeout = 500
        # prologix.connection.timeout = 700
        # prologix.eoi = 1
        # prologix.eos = "\n"
        # prologix.connection.read_termination = prologix.eos
        # # prologix.connection.read_termination = "\r\n"
        # prologix.write("++eot_enable 0")
        # prologix.flush_read_buffer()
        # prologix.write("FORM4")
        # prologix.flush_read_buffer()
        yield prologix

    finally:
        pass  # del prologix


@contextmanager
def init_HP8753E():
    try:
        with init_prologix_adapter() as prologix:
            vna = HP8753E(adapter=prologix)
            yield vna

    finally:
        pass  # del vna

def test_voltage_read():
    with expected_protocol(
        HP8753E,
        [("*IDN?", "HEWLETT PACKARD,8753E,0,7.10")],
    ) as inst:
        assert inst.id == ["HEWLETT PACKARD", "8753E", "0", "7.10"]


def test_generate_deviceless_tests():
    generator = Generator()
    # prologix = PrologixAdapter(resource_name="ASRL4::INSTR", address=16, visa_library="@py")
    vna = generator.instantiate(
        HP8753E,
        PrologixAdapter,
        "hp",
        {"resource_name": "ASRL4::INSTR", "address": 16, "visa_library": "@py"},
    )
    assert vna.id == ["HEWLETT PACKARD", "8753E", "0", "7.10"]
    generator.write_file("test_hp8753e_id.py")
    prologix.close()


def test_sanity():
    assert 1 + 1 == 2


def test_init_prologix_adapter():
    with init_prologix_adapter() as prologix:
        test_sanity()


def test_init_HP8753E():
    with init_HP8753E() as hp8753e:
        test_sanity()


def test_hp8753e_id():
    with init_HP8753E() as hp8753e:
        assert hp8753e.id == ["HEWLETT PACKARD", "8753E", "0", "7.10"]
        assert hp8753e.fw == "7.10"
        assert hp8753e.manu == "HEWLETT PACKARD"


def test_hp8753e_fw():
    with init_HP8753E() as hp8753e:
        assert hp8753e.fw == "7.10"


def test_hp8753e_manu():
    with init_HP8753E() as hp8753e:
        assert hp8753e.manu == "HEWLETT PACKARD"


def test_hp8753e_model():
    with init_HP8753E() as hp8753e:
        assert hp8753e.model == "8753E"


def test_hp8753e_sn():
    with init_HP8753E() as hp8753e:
        assert hp8753e.sn == "US37390178"


def test_hp8753e_options():
    with init_HP8753E() as hp8753e:
        assert hp8753e.options == "1D5 002 006 010"


def test_hp8753e_scan_points():
    assert 1 == 0


def test_hp8753e_ifbw():
    assert 1 == 0


def test_hp8753e_start_frequency():
    with init_HP8753E() as hp8753e:
        hp8753e.start_frequency = 30_000.0
        assert hp8753e.start_frequency == 30_000.0
        hp8753e.start_frequency = 30_600.0
        assert hp8753e.start_frequency == 30_600.0
        hp8753e.start_frequency = 4_000_000.0
        assert hp8753e.start_frequency == 4_000_000.0


def test_hp8753e_stop_frequency():
    with init_HP8753E() as hp8753e:
        hp8753e.stop_frequency = 130_000.0
        assert hp8753e.stop_frequency == 130_000.0
        hp8753e.stop_frequency = 130_600.0
        assert hp8753e.stop_frequency == 130_600.0
        hp8753e.stop_frequency = 14_000_000.0
        assert hp8753e.stop_frequency == 14_000_000.0


def test_hp8753e_set_fixed_frequency():
    assert 1 == 0


def test_hp8753e_scan():
    with init_HP8753E() as hp8753e:
        hp8753e.scan_single()
        assert False  # Need to import numpy test to compare numpy arrays
        assert hp8753e.data_complex.all() == ["1"]


def test_hp8753e_reset():
    assert 1 == 0


def test_hp8753e_averages():
    assert 1 == 0


def test_hp8753e_averaging_enabled():
    assert 1 == 0
