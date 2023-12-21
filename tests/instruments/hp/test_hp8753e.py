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

from contextlib import contextmanager

from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.hp import HP8753E


@contextmanager
def init_prologix_adapter():
    try:
        prologix = PrologixAdapter(resource_name="ASRL4::INSTR", address=16, visa_library="@py")
        prologix.auto = 1
        prologix.connection.query_delay = 0
        prologix.gpib_read_timeout = 500
        prologix.connection.timeout = 700
        prologix.eoi = 1
        prologix.eos = "\n"
        prologix.connection.read_termination = prologix.eos
        # prologix.connection.read_termination = "\r\n"
        prologix.write("++eot_enable 0")
        prologix.flush_read_buffer()
        prologix.write("FORM4")
        prologix.flush_read_buffer()
        yield prologix

    finally:
        del prologix


@contextmanager
def init_HP8753E():
    try:
        with init_prologix_adapter() as prologix:
            vna = HP8753E(adapter=prologix)
            yield vna

    finally:
        del vna


def test_sanity():
    assert 1 + 1 == 2

def test_init_prologix_adapter():
    init_prologix_adapter()

def test_init_HP8753E():
    init_HP8753E()

def test_hp8753e_id():
    assert 1 == 0

def test_hp8753e_sn():
    assert 1 == 0

def test_hp8753e_options():
    assert 1 == 0

def test_hp8753e_fw():
    assert 1 == 0

# def test_hp8753e_id():
#     assert 1 == 0

# def test_hp8753e_id():
#     assert 1 == 0

# def test_hp8753e_id():
#     assert 1 == 0

# def test_hp8753e_id():
#     assert 1 == 0

# def test_hp8753e_id():
#     assert 1 == 0

# def test_hp8753e_id():
#     assert 1 == 0

# def test_hp8753e_power():
#     assert 1 == 0

# def test_hp8753e_stop_frequency():
#     assert 1 == 0

def test_hp8753e_start_frequency():
    with init_HP8753E() as hp8753e:
        hp8753e.start_frequency = 30_000.0
        assert hp8753e.start_frequency == 30_000.0
        hp8753e.start_frequency = 30_600.0
        assert hp8753e.start_frequency == 30_600.0
        hp8753e.start_frequency = 4_000_000.0
        assert hp8753e.start_frequency == 4_000_000.0
