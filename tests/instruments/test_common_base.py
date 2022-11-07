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


import pytest

from pymeasure.units import ureg
from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.common_base import DynamicProperty, CommonBase
from pymeasure.adapters import FakeAdapter, ProtocolAdapter
from pymeasure.instruments.fakes import FakeInstrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


class CommonBaseTesting(CommonBase):
    """Add read/write methods in order to use the ProtocolAdapter."""

    def __init__(self, adapter, name=""):
        super().__init__()
        self.adapter = adapter

    def wait_for(self, query_delay=0):
        pass

    def write(self, command):
        self.adapter.write(command)

    def read(self):
        return self.adapter.read()


def test_dynamic_property_fget_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="Unreadable attribute"):
        d.__get__(5)


def test_dynamic_property_fset_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="set attribute"):
        d.__set__(5, 7)



@pytest.mark.parametrize("value, kwargs, result",
                         (("5,6,7", {}, [5, 6, 7]),
                          ("5.6.7", {'separator': '.'}, [5, 6, 7]),
                          ("5,6,7", {'cast': str}, ['5', '6', '7']),
                          ("X,Y,Z", {}, ['X', 'Y', 'Z']),
                          ("X,Y,Z", {'cast': str}, ['X', 'Y', 'Z']),
                          ("X.Y.Z", {'separator': '.'}, ['X', 'Y', 'Z']),
                          ("0,5,7.1", {'cast': bool}, [False, True, True]),
                          ("x5x", {'preprocess_reply': lambda v: v.strip("x")}, [5])
                          ))
def test_values(value, kwargs, result):
    cb = CommonBaseTesting(FakeAdapter(), "test")
    assert cb.values(value, **kwargs) == result
