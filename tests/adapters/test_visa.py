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
import importlib.util
import unittest.mock as mock

import pytest
import pyvisa

from pymeasure.adapters import VISAAdapter, ProtocolAdapter
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


def test_init_with_protocol_adapter():
    """VISAAdapter wraps a ProtocolAdapter, reusing its connection and aliasing methods."""
    proto = ProtocolAdapter()
    adapter = VISAAdapter(proto)
    assert adapter.connection is proto
    # write_raw aliased to write_bytes on the connection
    assert adapter.connection.write_raw == adapter.connection.write_bytes
    # read_bytes aliased to the protocol adapter's read_bytes
    assert adapter.read_bytes == proto.read_bytes


@pytest.mark.parametrize(
    "interface_kwargs, matching, expected",
    [
        # asrl kwargs match the ASRL interface of SIM_RESOURCE: dict applied
        ({"asrl": {"read_termination": "\rx\n"}}, True, "\rx\n"),
        # usb kwargs do not match (interface is asrl): dict not applied, default kept
        ({"usb": {"read_termination": "\rx\n"}}, False, None),
    ],
)
def test_init_interface_specific_kwargs(interface_kwargs, matching, expected):
    """Interface-specific kwargs are only applied when matching the interface type."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim', **interface_kwargs)
    try:
        assert adapter.connection.read_termination == expected
    finally:
        adapter.close()


def test_close_closes_manager_on_pyvisa_sim():
    """close() also closes the manager when using the pyvisa-sim library."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim')
    assert adapter.manager.visalib.library_path == "unset"
    assert adapter.manager.session is not None
    adapter.close()
    with pytest.raises(pyvisa.errors.InvalidSession, match="Invalid session"):
        adapter.manager.session


def test_read_bytes_negative_no_break_on_termchar():
    """read_bytes(-1) without break_on_termchar uses the byte-by-byte loop."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim', read_termination="\n",
                          timeout=50)
    try:
        adapter.write("*IDN?")
        # With a short timeout, the byte-by-byte loop returns what was buffered
        # before a timeout occurs.
        result = adapter.read_bytes(-1)
        assert result == b"SCPI,MOCK,VERSION_1.0\n"
    finally:
        adapter.close()


def test_read_bytes_negative_break_on_termchar():
    """read_bytes(-1, break_on_termchar=True) delegates to read_raw(None)."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim', read_termination="\n")
    try:
        adapter.write("*IDN?")
        with mock.patch.object(
            adapter.connection, "read_raw", wraps=adapter.connection.read_raw
        ) as spy:
            result = adapter.read_bytes(-1, break_on_termchar=True)
        assert result == b"SCPI,MOCK,VERSION_1.0\n"
        spy.assert_called_once_with(None)
    finally:
        adapter.close()


def test_wait_for_srq():
    """wait_for_srq passes the timeout (in ms) to the connection."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim')
    try:
        with mock.patch.object(adapter.connection, "wait_for_srq", create=True) as spy:
            adapter.wait_for_srq(timeout=3)
        spy.assert_called_once_with(3000)
    finally:
        adapter.close()


def test_flush_read_buffer_normal():
    """flush_read_buffer calls flush with discard_read_buffer and discard_receive_buffer."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim')
    try:
        with mock.patch.object(adapter.connection, "flush") as spy:
            adapter.flush_read_buffer()
        called_args = [call.args[0] for call in spy.call_args_list]
        assert pyvisa.constants.BufferOperation.discard_read_buffer in called_args
        assert pyvisa.constants.BufferOperation.discard_receive_buffer in called_args
    finally:
        adapter.close()


def test_flush_read_buffer_not_implemented_fallback():
    """flush_read_buffer falls back to read_bytes(-1) with timeout=0 on NotImplementedError."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim', read_termination="\n")
    try:
        def raising_flush(operation):
            raise NotImplementedError

        adapter.connection.flush = raising_flush
        original_timeout = adapter.connection.timeout
        with mock.patch.object(adapter, "read_bytes", wraps=adapter.read_bytes) as spy:
            adapter.flush_read_buffer()
        # read_bytes was called with -1 to drain the buffer
        assert any(call.args[0] == -1 for call in spy.call_args_list)
        # timeout was restored
        assert adapter.connection.timeout == original_timeout
    finally:
        adapter.close()


def test_repr():
    """repr of the adapter contains the resource name."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim')
    try:
        assert SIM_RESOURCE in repr(adapter)
        assert "VISAAdapter" in repr(adapter)
    finally:
        adapter.close()
