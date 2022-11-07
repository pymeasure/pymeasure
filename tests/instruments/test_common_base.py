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

from pymeasure.test import expected_protocol
from pymeasure.instruments.common_base import DynamicProperty, CommonBase
from pymeasure.adapters import FakeAdapter, ProtocolAdapter
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


class GenericBase(CommonBaseTesting):

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    #  Use truncated_range as this easily lets us test for the range boundaries
    fake_ctrl = CommonBase.control(
        "C{ch}:control?", "C{ch}:control %d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_setting = CommonBase.setting(
        "C{ch}:setting %d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_measurement = CommonBase.measurement(
        "C{ch}:measurement?", "docs",
        values={'X': 1, 'Y': 2, 'Z': 3},
        map_values=True,
        dynamic=True,
    )
    special_control = CommonBase.control(
        "SOUR{ch}:special?", "OUTP{ch}:special %s",
        """A special control with different channel specifiers for get and set.""",
        cast=str,
    )


class Parent(CommonBaseTesting):
    """A Base as a parent"""

    def __init__(self, adapter, name="ChannelInstrument", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.add_child(GenericBase, "A")
        self.add_child(GenericBase, "B")


# Test dynamic properties
def test_dynamic_property_fget_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="Unreadable attribute"):
        d.__get__(5)


def test_dynamic_property_fset_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="set attribute"):
        d.__set__(5, 7)


# Test CommonBase
@pytest.fixture()
def parent():
    parent = CommonBaseTesting(ProtocolAdapter())
    parent.add_child(GenericBase, "A")
    parent.add_child(GenericBase, "B")
    return parent


class TestAddChild:
    def test_correct_class(self, parent):
        assert isinstance(parent.ch_A, GenericBase)

    def test_arguments(self, parent):
        assert parent.channels[0].args == (parent, "A")

    def test_attribute_access(self, parent):
        assert parent.ch_B == parent.channels[1]

    def test_len(self, parent):
        assert len(parent.channels) == 2

    def test_attributes(self, parent):
        assert parent.ch_A._name == "ch_A"
        assert parent.ch_B._collection == "channels"


@pytest.fixture()
def parent_without_children(parent):
    parent.remove_child(parent.ch_A)
    parent.remove_child(parent.channels[0])
    return parent


def test_remove_child_leaves_channels_empty(parent_without_children):
    assert parent_without_children.channels == []


def test_remove_child_clears_attributes(parent_without_children):
    assert getattr(parent_without_children, "ch_A", None) is None
    assert getattr(parent_without_children, "ch_B", None) is None


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
