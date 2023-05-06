import pytest

from serial import Serial
from time import time
from pymeasure.adapters import SerialAdapter


class TestSerialLoopback:
    """Test serial adapter with two real but looped COM ports.

    A pair of COM ports that are looped will read the written data from the other.
    This looping needs to be done outside this script. One suggestion is using the application
    `com0com <https://com0com.sourceforge.net/>`_.
    Alternatively two UART adapters could be used, that have their RX/TX physically connected.

    Call PyTest with the argument``--device-address="COM1,COM2"`` to specify the serial addresses,
    minding the comma for the separation of the two ports.
    """

    ADAPTER_TIMEOUT = 1.0  # Seconds

    @pytest.fixture()
    def adapter(self, connected_device_address):
        device = connected_device_address.split(",")[0]
        return SerialAdapter(
            device,
            baudrate=19200,
            timeout=self.ADAPTER_TIMEOUT,
            read_termination=chr(0x0F),
        )

    @pytest.fixture()
    def loopback(self, connected_device_address):
        """See `adapter()`."""
        device = connected_device_address.split(",")[1]
        return Serial(device, baudrate=19200)

    def test_read(self, adapter, loopback):
        """Regular read with fixed number of bytes."""
        loopback.write(b"abc")
        result = adapter.read_bytes(3)

        assert len(result) == 3

    @pytest.mark.parametrize("data", [
        b"a",                               # Short data
        b"aaaaabbbbbccccceeeee" * 50,       # A lot data
        b"a" * 256,                         # Exactly one chunk size
        b"aaaaabbbbb\nccccceeeee" * 50,     # With a newline (should be ignored)
    ])
    def test_read_all(self, adapter, loopback, data):
        """Read with undefined number of bytes - also confirm timeout duration is correct."""
        loopback.write(data)
        start = time()
        result = adapter.read_bytes(-1)
        elapsed = time() - start

        assert result == data
        assert self.ADAPTER_TIMEOUT == pytest.approx(elapsed, abs=0.1)

    @pytest.mark.parametrize("chunk", [1, 256, 10000])
    def test_read_varied_chunk_size(self, adapter, loopback, chunk):
        """Read with undefined number of bytes with non-default chunk size."""
        data = b"abcde" * 10
        loopback.write(data)
        result = adapter.read_bytes(-1)

        assert result == data
