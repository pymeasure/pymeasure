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
import importlib.util

import pytest
import pyvisa

from pymeasure.adapters import VISAAdapter
from pymeasure.test import expected_protocol

# This uses a pyvisa-sim default instrument, we could also define our own.
SIM_RESOURCE = 'ASRL2::INSTR'

is_pyvisa_sim_installed = bool(importlib.util.find_spec('pyvisa_sim'))
if not is_pyvisa_sim_installed:
    pytest.skip('PyVISA tests require the pyvisa-sim library', allow_module_level=True)


@pytest.fixture
def adapter():
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim',
                          read_termination="\n",
                          # Large timeout allows very slow GitHub action runners to complete.
                          timeout=60,
                          )
    yield adapter
    # Empty the read buffer, as something might remain there after a test.
    # `clear` is not implemented in pyvisa-sim and `flush_read_buffer` seems to do nothing.
    adapter.timeout = 0
    try:
        adapter.read_bytes(-1)
    except pyvisa.errors.VisaIOError as exc:
        if not exc.args[0].startswith("VI_ERROR_TMO"):
            raise
    # Close the connection
    adapter.close()


def test_nested_adapter():
    a0 = VISAAdapter(SIM_RESOURCE, visa_library='@sim', read_termination="\n")
    a = VISAAdapter(a0)
    assert a.resource_name == SIM_RESOURCE
    assert a.connection == a0.connection
    assert a.manager == a0.manager


def test_nested_adapter_query_delay():
    query_delay = 10
    with pytest.warns(FutureWarning, match="query_delay"):
        a0 = VISAAdapter(SIM_RESOURCE, visa_library='@sim', read_termination="\n",
                         query_delay=query_delay)
        a = VISAAdapter(a0)
    assert a.resource_name == SIM_RESOURCE
    assert a.connection == a0.connection
    assert a.query_delay == query_delay


def test_ProtocolAdapter():
    with expected_protocol(
            VISAAdapter,
            [(b"some bytes written", b"Response")]
    ) as adapter:
        adapter.write_bytes(b"some bytes written")
        assert adapter.read_bytes(-1) == b"Response"


def test_correct_visa_asrl_kwarg():
    """Confirm that the asrl kwargs gets passed through to the VISA connection."""
    a = VISAAdapter(SIM_RESOURCE, visa_library='@sim',
                    asrl={'read_termination': "\rx\n"})
    assert a.connection.read_termination == "\rx\n"


def test_open_gpib():
    a = VISAAdapter(5, visa_library='@sim')
    assert a.resource_name == "GPIB0::5::INSTR"


class TestClose:
    @pytest.fixture
    def adapterC(self):
        return VISAAdapter(SIM_RESOURCE, visa_library='@sim')

    def test_connection_session_closed(self, adapterC):
        # Verify first, that it works before closing
        assert adapterC.connection.session is not None
        adapterC.close()
        with pytest.raises(pyvisa.errors.InvalidSession, match="Invalid session"):
            adapterC.connection.session

    def test_manager_session_closed(self, adapterC):
        # Verify first, that it works before closing
        assert adapterC.manager.session is not None
        adapterC.close()
        with pytest.raises(pyvisa.errors.InvalidSession, match="Invalid session"):
            adapterC.manager.session


def test_write_read(adapter):
    adapter.write(":VOLT:IMM:AMPL?")
    assert float(adapter.read()) == 1


def test_write_bytes_read_bytes(adapter):
    adapter.write_bytes(b"*IDN?\r\n")
    assert adapter.read_bytes(22) == b"SCPI,MOCK,VERSION_1.0\n"


def test_write_bytes_read(adapter):
    adapter.write_bytes(b"*IDN?\r\n")
    assert adapter.read() == "SCPI,MOCK,VERSION_1.0"


class TestReadBytes:
    @pytest.fixture()
    def adapterR(self, adapter):
        adapter.write("*IDN?")
        yield adapter

    def test_read_bytes(self, adapterR):
        assert adapterR.read_bytes(22) == b"SCPI,MOCK,VERSION_1.0\n"

    def test_read_all_bytes(self, adapterR):
        assert adapterR.read_bytes(-1) == b"SCPI,MOCK,VERSION_1.0\n"

    @pytest.mark.parametrize("count", (-1, 7))
    def test_read_break_on_termchar(self, adapterR, count):
        """Test read_bytes breaks on termchar."""
        adapterR.connection.read_termination = ","
        assert adapterR.read_bytes(count, break_on_termchar=True) == b"SCPI,"

    def test_read_no_break_on_termchar(self, adapterR):
        adapterR.connection.read_termination = ","
        # `break_on_termchar=False` is default value
        assert adapterR.read_bytes(-1) == b"SCPI,MOCK,VERSION_1.0\n"

    def test_read_no_break_on_newline(self, adapter):
        # write twice to have two newline characters in the read buffer
        adapter.write("*IDN?")
        adapter.write("*IDN?")
        # `break_on_termchar=False` is default value
        assert adapter.read_bytes(-1) == b"SCPI,MOCK,VERSION_1.0\nSCPI,MOCK,VERSION_1.0\n"


def test_visa_adapter(adapter):
    assert repr(adapter) == f"<VISAAdapter(resource='{SIM_RESOURCE}')>"

    with pytest.warns(FutureWarning):
        assert adapter.ask("*IDN?") == "SCPI,MOCK,VERSION_1.0"

    adapter.write("*IDN?")
    assert adapter.read() == "SCPI,MOCK,VERSION_1.0"


def test_visa_adapter_ask_values(adapter):
    with pytest.warns(FutureWarning):
        assert adapter.ask_values(":VOLT:IMM:AMPL?", separator=",") == [1.0]
