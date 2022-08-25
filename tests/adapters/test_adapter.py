#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from unittest import mock

import pytest

from pymeasure.adapters import Adapter, FakeAdapter


@pytest.fixture()
def adapter():
    return Adapter(preprocess_reply=lambda v: v)


def test_init(adapter):
    assert adapter.preprocess_reply is not None
    assert adapter.connection is None


def test_del(adapter):
    adapter.connection = mock.MagicMock()
    adapter.__del__()
    assert adapter.connection.method_calls == [mock.call.close()]


@pytest.mark.parametrize("method, args", (['write', ['5']], ['read', []], ['binary_values', ['8']]))
def test_not_implemented_methods(adapter, method, args):
    with pytest.raises(NameError):
        getattr(adapter, method)(*args)


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
    assert a.values(value, **kwargs) == result


def test_adapter_preprocess_reply():
    a = FakeAdapter(preprocess_reply=lambda v: v[1:])
    assert str(a) == "<FakeAdapter>"
    assert a.values("R42.1") == [42.1]
    assert a.values("A4,3,2") == [4, 3, 2]
    assert a.values("TV 1", preprocess_reply=lambda v: v.split()[0]) == ['TV']
    assert a.values("15", preprocess_reply=lambda v: v) == [15]
    a = FakeAdapter()
    assert a.values("V 3.4", preprocess_reply=lambda v: v.split()[1]) == [3.4]
