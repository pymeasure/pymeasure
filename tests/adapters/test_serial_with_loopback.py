#
# Test the serial adapter using looped COM ports.
# This looping needs to be done outside this script. One suggestion is
# using the application `com0com`.
#

import pytest

from serial import Serial
from time import time
from pymeasure.adapters import SerialAdapter


ADAPTER_TIMEOUT = 3.0  # Seconds


@pytest.fixture()
def adapter(connected_device_address):
    """Call with `--device-address="COM3,COM4"` to select two devices."""
    device = connected_device_address.split(",")[0]
    return SerialAdapter(
        device,
        baudrate=19200,
        timeout=ADAPTER_TIMEOUT,
        read_termination=chr(0x0F),
    )


@pytest.fixture()
def loopback(connected_device_address):
    """See `adapter()`."""
    device = connected_device_address.split(",")[1]
    return Serial(device, baudrate=19200)


def test_read(adapter, loopback):
    """Regular read with fixed number of bytes."""
    loopback.write(b"abc")
    result = adapter.read_bytes(3)

    assert len(result) == 3


def test_read_all_short(adapter, loopback):
    """Read with unlimited number of bytes"""
    loopback.write(b"a")
    start = time()
    result = adapter.read_bytes(-1)
    elapsed = time() - start

    assert len(result) == 1
    assert ADAPTER_TIMEOUT == pytest.approx(elapsed, abs=0.1)


def test_read_all(adapter, loopback):
    loopback.write(b"aaaaabbbbbccccceeeee" * 50)
    start = time()
    result = adapter.read_bytes(-1)
    elapsed = time() - start

    assert len(result) == 20 * 50
    assert ADAPTER_TIMEOUT == pytest.approx(elapsed, abs=0.1)


def test_read_all_exact_chunck_size(adapter, loopback):
    loopback.write(b"a" * 256)
    start = time()
    result = adapter.read_bytes(-1)
    elapsed = time() - start

    assert len(result) == 256
    assert ADAPTER_TIMEOUT == pytest.approx(elapsed, abs=0.1)


def test_read_all_with_newline(adapter, loopback):
    data = b"aaaaabbbbb\nccccceeeee" * 50
    loopback.write(data)
    result = adapter.read_bytes(-1)

    assert len(result) == 21 * 50
