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
from unittest import mock

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


def test_deprecated_preprocess_reply():
    with pytest.warns(FutureWarning):
        adapter = Adapter(preprocess_reply=lambda v: v)
    assert adapter.preprocess_reply is not None


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


def test_ask_deprecation_warning():
    a = FakeAdapter()
    with pytest.warns(FutureWarning):
        assert a.ask("abc") == "abc"


@pytest.mark.parametrize("value, kwargs, result",
                         (("5,6,7", {}, [5, 6, 7]),
                          ("5.6.7", {'separator': '.'}, [5, 6, 7]),
                          ("5,6,7", {'cast': str}, ['5', '6', '7']),
                          ("X,Y,Z", {}, ['X', 'Y', 'Z']),
                          ("X,Y,Z", {'cast': str}, ['X', 'Y', 'Z']),
                          ("X.Y.Z", {'separator': '.'}, ['X', 'Y', 'Z']),
                          ("0,5,7.1", {'cast': bool}, [False, True, True]),
                          ))
def test_adapter_values(value, kwargs, result):
    a = FakeAdapter()
    with pytest.warns(FutureWarning):
        assert a.values(value, **kwargs) == result


def test_read_binary_values():
    a = ProtocolAdapter([(None, "1 2")])
    assert list(a.read_binary_values(dtype=int, sep=" ")) == pytest.approx([1, 2])


def test_write_binary_values():
    """Test write_binary_values in the ieee header format."""
    a = ProtocolAdapter([(b'CMD#212\x00\x00\x80?\x00\x00\x00@\x00\x00@@\n', None)])
    a.write_binary_values("CMD", [1, 2, 3], termination="\n")


def test_adapter_preprocess_reply():
    with pytest.warns(FutureWarning):
        a = FakeAdapter(preprocess_reply=lambda v: v[1:])
        assert str(a) == "<FakeAdapter>"
        assert a.values("R42.1") == [42.1]
        assert a.values("A4,3,2") == [4, 3, 2]
        assert a.values("TV 1", preprocess_reply=lambda v: v.split()[0]) == ['TV']
        assert a.values("15", preprocess_reply=lambda v: v) == [15]
        a = FakeAdapter()
        assert a.values("V 3.4", preprocess_reply=lambda v: v.split()[1]) == [3.4]


def test_binary_values_deprecation_warning():
    a = FakeAdapter()
    with pytest.warns(FutureWarning):
        a.binary_values("abcdefgh")


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
