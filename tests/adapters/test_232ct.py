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
import importlib.util

import pytest
import pyvisa
import logging

from pymeasure.adapters import NI_GPIB_232
from pymeasure.instruments.hp import HP3478A
from pymeasure.log import console_log

log = logging.getLogger()
# console_log(log, level=logging.DEBUG)
console_log(log)

is_pyvisa_sim_installed = bool(importlib.util.find_spec('pyvisa_sim'))
if not is_pyvisa_sim_installed:
    pytest.skip('PyVISA tests require the pyvisa-sim library', allow_module_level=True)

SIM_RESOURCE = 'ASRL8::INSTR'
# init_comm = [(b'EOS D', None), (b'STAT', None), ("stat n", b'256\r\n0\r\n0\r\n0\r\n')]
# init_attrib = {'bytes_in_buffer': '14', 'resource_name': 'foo'}


@pytest.fixture
def aut():
    aut = NI_GPIB_232(SIM_RESOURCE,
                      visa_library='/home/robby/builds/pymeasure/tests/adapters/ni232.yaml@sim',
                      # Large timeout allows very slow GitHub action runners to complete.
                      timeout=60,
                      address=23,
                      )
    yield aut
    # Empty the read buffer, as something might remain there after a test.
    # `clear` is not implemented in pyvisa-sim and `flush_read_buffer` seems to do nothing.
    aut.timeout = 0
    try:
        aut.read_bytes(-1)
    except pyvisa.errors.VisaIOError as exc:
        if not exc.args[0].startswith("VI_ERROR_TMO"):
            raise
    # Close the connection
    aut.close()

@pytest.fixture
def dmm(aut):
    dmm = HP3478A(aut)
    dmm.resolution(3)
    assert dmm.resolution == 3

    
def test_write_read(aut):
    aut.write(":VOLT:IMM:AMPL?")
    assert float(aut.read()) == 1


# def test_read(aut):
#     """ simple read test """
#     aut.connection.write(b"abc")
#     result = aut.read_bytes(3)

#     assert len(result) == 3

# class Test_NI232CT:
#     """ Protocol test class for the NI232CT
#     """
#     # @pytest.fixture
#     # def adapter(self):
#     #     adapter = ProtocolAdapter(init_comm, connection_attributes=init_attrib)
#     #     return adapter

#     @pytest.fixture
#     def adapter(self):
#         aut = NI_GPIB_232(adapter, address=23,)
#         return aut
