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

import logging
from unittest import mock

import numpy as np
import pytest

from pymeasure.adapters import Adapter, FakeAdapter, ProtocolAdapter


@pytest.fixture()
def adapter():
    return Adapter()


@pytest.fixture()
def fake():
    return FakeAdapter()


def test_init(adapter):
    assert adapter.connection is None
    assert adapter.log == logging.getLogger("Adapter")


def test_init_log():
    adapter = Adapter(log=logging.getLogger("parent"))
    assert adapter.log == logging.getLogger("parent.Adapter")


def test_del(adapter):
    adapter.connection = mock.MagicMock()
    adapter.__del__()
    assert adapter.connection.method_calls == [mock.call.close()]


def test_write(fake):
    fake.write("abc")
    assert fake._buffer == "abc"


def test_write_bytes(fake):
    fake.write_bytes(b"abc")
    assert fake._buffer == "abc"


def test_read(fake):
    fake._buffer = "abc"
    assert fake.read() == "abc"


def test_read_bytes(fake):
    fake._buffer = "abc"
    assert fake.read_bytes(5) == b"abc"


@pytest.mark.parametrize("method, args", (['_write', ['5']],
                                          ['_read', []],
                                          ['_write_bytes', ['8']],
                                          ['_read_bytes', ['5', False]],
                                          ))
def test_not_implemented_methods(adapter, method, args):
    with pytest.raises(NotImplementedError):
        getattr(adapter, method)(*args)


@pytest.mark.parametrize("response, options, result", (
    ("1,2", dict(dtype=int, sep=","), [1, 2]),
    (b"\x01\x02", dict(dtype=np.uint8), [1, 2]),
    (b'\x01\x02\x03\x04\x05', dict(dtype=np.uint8, count=3), [1, 2, 3]),
    ("abcdefgh", {}, [1.6777999e+22, 4.371022e+24]),
))
def test_read_binary_values(response, options, result):
    a = ProtocolAdapter([(None, response)])
    assert list(a.read_binary_values(**options)) == pytest.approx(result)


def test_write_binary_values():
    """Test write_binary_values in the ieee header format."""
    a = ProtocolAdapter([(b'CMD#212\x00\x00\x80?\x00\x00\x00@\x00\x00@@\n', None)])
    a.write_binary_values("CMD", [1, 2, 3], termination="\n")


class TestLoggingForTestGenerator:
    """The test Generator relies on specific logging in the adapter, these tests ensure that."""
    message = b"some written message"

    @pytest.fixture
    def adapter(self, caplog):
        adapter = ProtocolAdapter()
        caplog.set_level(logging.DEBUG)
        return adapter

    def test_write(self, adapter, caplog):
        adapter.comm_pairs = [(self.message, None)]
        written = self.message.decode()
        adapter.write(written)
        record = caplog.records[0]
        assert record.msg == "WRITE:%s"
        assert record.args == (written,)

    def test_write_bytes(self, adapter, caplog):
        adapter.comm_pairs = [(self.message, None)]
        adapter.write(self.message)
        record = caplog.records[0]
        assert record.msg == "WRITE:%s"
        assert record.args == (self.message,)

    def test_read(self, adapter, caplog):
        adapter.comm_pairs = [(None, self.message)]
        read = adapter.read()
        assert read == self.message.decode()
        record = caplog.records[0]
        assert record.msg == "READ:%s"
        assert record.args == (read,)

    def test_read_bytes(self, adapter, caplog):
        adapter.comm_pairs = [(None, self.message)]
        read = adapter.read_bytes(-1)
        assert read == self.message
        record = caplog.records[0]
        assert record.msg == "READ:%s"
        assert record.args == (read,)
