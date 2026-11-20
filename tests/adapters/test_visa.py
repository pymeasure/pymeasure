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
from types import SimpleNamespace
from typing import Any, cast
from unittest import mock

import pytest
import pyvisa

from pymeasure.adapters import ProtocolAdapter, VISAAdapter
from pymeasure.adapters.visa import visa_resource
from pymeasure.test import expected_protocol

# This uses a pyvisa-sim default instrument, we could also define our own.
SIM_RESOURCE = 'ASRL2::INSTR'

is_pyvisa_sim_installed = bool(importlib.util.find_spec('pyvisa_sim'))
if not is_pyvisa_sim_installed:
    pytest.skip('PyVISA tests require the pyvisa-sim library', allow_module_level=True)


def _resource(adapter: VISAAdapter) -> pyvisa.resources.MessageBasedResource:
    """Return the adapter's connection narrowed to a PyVISA resource."""
    connection = adapter.connection
    assert isinstance(connection, pyvisa.resources.MessageBasedResource)
    return connection


def _drain_read_buffer(adapter: VISAAdapter, timeout: int = 50) -> None:
    """Empty the read buffer of the process-wide pyvisa-sim backend.

    The simulated backend is cached per process, so all adapters sharing a simulated
    resource share one device buffer. A zero timeout does not consume any bytes, because
    pyvisa-sim's read loop never runs in that case; a short nonzero timeout drains them.
    """
    previous_timeout = adapter.timeout
    adapter.timeout = timeout
    try:
        # The byte-by-byte loop of `read_bytes(-1)` swallows the terminal timeout.
        adapter.read_bytes(-1)
    finally:
        adapter.timeout = previous_timeout


@pytest.fixture
def adapter():
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim',
                          read_termination="\n",
                          # Large timeout allows very slow GitHub action runners to complete.
                          timeout=60,
                          )
    # Start from an empty shared simulator buffer, independent of earlier tests.
    _drain_read_buffer(adapter)
    yield adapter
    # Leave the process-wide simulator buffer empty for the next test and always close.
    try:
        _drain_read_buffer(adapter)
    finally:
        adapter.close()


@pytest.fixture
def make_visa_adapter():
    """Return a factory creating VISAAdapter instances against the pyvisa-sim
    resource; any adapter created during the test is closed again on teardown.

    Every factory adapter starts with an empty shared simulator buffer, so tests
    do not depend on the order in which they run."""
    created = []

    def _make(**kwargs):
        adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim', **kwargs)
        created.append(adapter)
        _drain_read_buffer(adapter)
        return adapter

    yield _make
    for adapter in created:
        try:
            _drain_read_buffer(adapter)
        except pyvisa.errors.InvalidSession:
            # The test may have closed this adapter itself; still close it below.
            pass
        finally:
            adapter.close()


def test_nested_adapter():
    a0 = VISAAdapter(SIM_RESOURCE, visa_library='@sim', read_termination="\n")
    a = VISAAdapter(a0)
    assert a.resource_name == SIM_RESOURCE
    assert a.connection == a0.connection
    assert a.manager == a0.manager


def test_timeout_roundtrip(make_visa_adapter):
    """The timeout property reads and writes the PyVISA timeout in integer milliseconds."""
    adapter = make_visa_adapter(timeout=1000)
    adapter.timeout = 1500
    assert adapter.timeout == 1500
    assert isinstance(adapter.timeout, int)
    assert isinstance(adapter.connection, pyvisa.resources.MessageBasedResource)
    assert adapter.connection.timeout == 1500


def test_timeout_fractional_resource_value_is_reported_as_int(make_visa_adapter):
    """A fractional value stored by PyVISA is reported as integer milliseconds."""
    adapter = make_visa_adapter()
    with mock.patch(
        "pymeasure.adapters.visa.visa_resource",
        return_value=SimpleNamespace(timeout=1500.7),
    ):
        assert adapter.timeout == 1500
        assert isinstance(adapter.timeout, int)


def test_timeout_none_maps_to_infinite(make_visa_adapter):
    """``None`` means no timeout and is translated to PyVISA's ``float("inf")``."""
    adapter = make_visa_adapter()
    adapter.timeout = None
    assert adapter.timeout is None
    assert _resource(adapter).timeout == float("inf")


def test_timeout_infinite_maps_to_none(make_visa_adapter):
    """PyVISA's infinite timeout is reported as ``None``."""
    adapter = make_visa_adapter()
    _resource(adapter).timeout = float("inf")
    assert adapter.timeout is None


def test_timeout_with_protocol_adapter_roundtrip():
    """Values pass through unchanged on a ProtocolAdapter connection, without inf translation."""
    protocol = ProtocolAdapter(connection_attributes={"timeout": 250})
    adapter = VISAAdapter(protocol)
    assert adapter.timeout == 250
    adapter.timeout = None
    assert adapter.timeout is None
    assert protocol.connection.timeout is None
    adapter.timeout = 500
    assert adapter.timeout == 500
    assert protocol.connection.timeout == 500


def test_ProtocolAdapter():
    with expected_protocol(
            VISAAdapter,  # type: ignore
            [(b"some bytes written", b"Response")]
    ) as adapter:
        adapter.write_bytes(b"some bytes written")
        assert adapter.read_bytes(-1) == b"Response"


def test_correct_visa_asrl_kwarg():
    """Confirm that the asrl kwargs gets passed through to the VISA connection."""
    a = VISAAdapter(SIM_RESOURCE, visa_library='@sim',
                    asrl={'read_termination': "\rx\n"})
    assert _resource(a).read_termination == "\rx\n"


def test_open_gpib():
    a = VISAAdapter(5, visa_library='@sim')
    assert a.resource_name == "GPIB0::5::INSTR"


class TestClose:
    @pytest.fixture
    def adapterC(self):
        return VISAAdapter(SIM_RESOURCE, visa_library='@sim')

    def test_connection_session_closed(self, adapterC):
        # Verify first, that it works before closing
        assert _resource(adapterC).session is not None
        adapterC.close()
        with pytest.raises(pyvisa.errors.InvalidSession, match="Invalid session"):
            _ = _resource(adapterC).session

    def test_manager_session_closed(self, adapterC):
        # Verify first, that it works before closing
        assert adapterC.manager.session is not None
        adapterC.close()
        with pytest.raises(pyvisa.errors.InvalidSession, match="Invalid session"):
            _ = adapterC.manager.session


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
        _resource(adapterR).read_termination = ","
        assert adapterR.read_bytes(count, break_on_termchar=True) == b"SCPI,"

    def test_read_no_break_on_termchar(self, adapterR):
        _resource(adapterR).read_termination = ","
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
    connection = adapter.connection
    assert isinstance(connection, ProtocolAdapter)
    assert connection is proto
    # VISAAdapter aliases write_raw to write_bytes on the connection dynamically
    assert cast(Any, connection).write_raw == connection.write_bytes
    # read_bytes aliased to the protocol adapter's read_bytes
    assert adapter.read_bytes == proto.read_bytes


def test_visa_resource_passes_protocol_adapter_through():
    """visa_resource is a typing-only cast and must not reject a ProtocolAdapter connection."""
    proto = ProtocolAdapter()
    adapter = VISAAdapter(proto)
    assert visa_resource(adapter) is proto


@pytest.mark.parametrize(
    "interface_kwargs, matching, expected",
    [
        # asrl kwargs match the ASRL interface of SIM_RESOURCE: dict applied
        ({"asrl": {"read_termination": "\rx\n"}}, True, "\rx\n"),
        # usb kwargs do not match (interface is asrl): dict not applied, default kept
        ({"usb": {"read_termination": "\rx\n"}}, False, None),
    ],
)
def test_init_interface_specific_kwargs(interface_kwargs, matching, expected, make_visa_adapter):
    """Interface-specific kwargs are only applied when matching the interface type."""
    adapter = make_visa_adapter(**interface_kwargs)
    assert _resource(adapter).read_termination == expected


def test_close_closes_manager_on_pyvisa_sim():
    """close() also closes the manager when using the pyvisa-sim library."""
    adapter = VISAAdapter(SIM_RESOURCE, visa_library='@sim')
    assert adapter.manager.visalib.library_path == "unset"
    assert adapter.manager.session is not None
    adapter.close()
    with pytest.raises(pyvisa.errors.InvalidSession):
        _ = adapter.manager.session


def test_read_bytes_negative_no_break_on_termchar(make_visa_adapter):
    """read_bytes(-1) without break_on_termchar uses the byte-by-byte loop."""
    adapter = make_visa_adapter(read_termination="\n", timeout=50)
    adapter.write("*IDN?")
    # With a short timeout, the byte-by-byte loop returns what was buffered
    # before a timeout occurs.
    result = adapter.read_bytes(-1)
    assert result == b"SCPI,MOCK,VERSION_1.0\n"


def test_read_bytes_negative_break_on_termchar(make_visa_adapter):
    """read_bytes(-1, break_on_termchar=True) delegates to read_raw(None)."""
    adapter = make_visa_adapter(read_termination="\n")
    adapter.write("*IDN?")
    connection = _resource(adapter)
    with mock.patch.object(connection, "read_raw", wraps=connection.read_raw) as spy:
        result = adapter.read_bytes(-1, break_on_termchar=True)
    assert result == b"SCPI,MOCK,VERSION_1.0\n"
    spy.assert_called_once_with(None)


def test_read_break_on_termchar_after_partial_read(make_visa_adapter):
    """A partial termchar read must not leak its remaining bytes into a fresh adapter."""
    first = make_visa_adapter(read_termination="\n")
    first.write("*IDN?")
    _resource(first).read_termination = ","
    assert first.read_bytes(-1, break_on_termchar=True) == b"SCPI,"

    second = make_visa_adapter()
    second.write("*IDN?")
    _resource(second).read_termination = ","
    assert second.read_bytes(7, break_on_termchar=True) == b"SCPI,"


def test_read_all_bytes_after_partial_read(make_visa_adapter):
    """read_bytes(-1) on a fresh adapter must return only its own buffered response."""
    first = make_visa_adapter(read_termination="\n")
    first.write("*IDN?")
    _resource(first).read_termination = ","
    assert first.read_bytes(-1, break_on_termchar=True) == b"SCPI,"

    # The byte-by-byte drain waits for its timeout once the buffer is empty;
    # a short timeout keeps that terminal read fast.
    second = make_visa_adapter(timeout=50)
    second.write("*IDN?")
    assert second.read_bytes(-1) == b"SCPI,MOCK,VERSION_1.0\n"


def test_make_visa_adapter_teardown_tolerates_closed_adapter(make_visa_adapter):
    """Teardown drains every factory adapter even if the test has closed it already."""
    adapter = make_visa_adapter()
    adapter.close()
    # Touching a closed session fails; the fixture's teardown below must swallow
    # that InvalidSession instead of letting it escape as a test error.
    with pytest.raises(pyvisa.errors.InvalidSession):
        _ = _resource(adapter).session


def test_wait_for_srq(make_visa_adapter):
    """wait_for_srq passes the timeout (in ms) to the connection."""
    adapter = make_visa_adapter()
    with mock.patch.object(adapter.connection, "wait_for_srq", create=True) as spy:
        adapter.wait_for_srq(timeout=3)
    spy.assert_called_once_with(3000)


def test_flush_read_buffer_normal(make_visa_adapter):
    """flush_read_buffer calls flush with discard_read_buffer and discard_receive_buffer."""
    adapter = make_visa_adapter()
    with mock.patch.object(_resource(adapter), "flush") as spy:
        adapter.flush_read_buffer()
    called_args = [call.args[0] for call in spy.call_args_list]
    assert pyvisa.constants.BufferOperation.discard_read_buffer in called_args
    assert pyvisa.constants.BufferOperation.discard_receive_buffer in called_args


def test_flush_read_buffer_not_implemented_fallback(make_visa_adapter):
    """flush_read_buffer falls back to read_bytes(-1) with timeout=0 on NotImplementedError."""
    adapter = make_visa_adapter(read_termination="\n")

    original_timeout = adapter.timeout
    with mock.patch.object(
        _resource(adapter), "flush", side_effect=NotImplementedError
    ), mock.patch.object(adapter, "read_bytes", wraps=adapter.read_bytes) as spy:
        adapter.flush_read_buffer()
    # read_bytes was called with -1 to drain the buffer
    assert any(call.args[0] == -1 for call in spy.call_args_list)
    # timeout was restored
    assert adapter.timeout == original_timeout


def test_repr(make_visa_adapter):
    """repr of the adapter contains the resource name."""
    adapter = make_visa_adapter()
    assert SIM_RESOURCE in repr(adapter)
    assert "VISAAdapter" in repr(adapter)
