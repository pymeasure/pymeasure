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
from pymeasure.instruments.common_base import DynamicProperty, CommonBase, ChildDescriptor
from pymeasure.adapters import FakeAdapter, ProtocolAdapter
from pymeasure.instruments.validators import truncated_range


class CommonBaseTesting(CommonBase):
    """Add read/write methods in order to use the ProtocolAdapter."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__()
        self.parent = parent
        self.args = args
        self.kwargs = kwargs

    def wait_for(self, query_delay=0):
        pass

    def write(self, command):
        self.parent.write(command)

    def read(self):
        return self.parent.read()


class GenericBase(CommonBaseTesting):

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


class Child(CommonBase):
    """A child, which accepts parent and id arguments."""

    def __init__(self, *args, **kwargs):
        super().__init__()


class Parent(CommonBaseTesting):
    """A Base as a parent"""
    channels = CommonBase.children(GenericBase, ("A", "B", "C"))
    analog = CommonBase.children(GenericBase, [1, 2], prefix="an_", test=True)
    function = CommonBase.children(Child, prefix=None)
    test = ChildDescriptor(Child, "a", prefix=None)


# Test dynamic properties
def test_dynamic_property_fget_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="Unreadable attribute"):
        d.__get__(5)


def test_dynamic_property_fset_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="set attribute"):
        d.__set__(5, 7)


# Test CommonBase Children management
class TestInitWithChildren:
    @pytest.fixture()
    def parent(self):
        return Parent(ProtocolAdapter())

    def test_channels(self, parent):
        assert len(parent.channels) == 3
        assert isinstance(parent.ch_A, GenericBase)

    def test_function(self, parent):
        assert isinstance(parent.function, Child)

    def test_directDescriptor(self, parent):
        assert isinstance(parent.test, Child)
        assert parent.test._name == "test"


class TestAddChild:
    """Test the `add_child` method"""
    @pytest.fixture()
    def parent(self):
        parent = CommonBaseTesting(ProtocolAdapter())
        parent.add_child(GenericBase, "A")
        parent.add_child(GenericBase, "B")
        parent.add_child(GenericBase, prefix=None, collection="function")
        return parent

    def test_correct_class(self, parent):
        assert isinstance(parent.ch_A, GenericBase)

    def test_arguments(self, parent):
        assert parent.channels[0].args == ("A",)

    def test_attribute_access(self, parent):
        assert parent.ch_B == parent.channels[1]

    def test_len(self, parent):
        assert len(parent.channels) == 2

    def test_attributes(self, parent):
        assert parent.ch_A._name == "ch_A"
        assert parent.ch_B._collection == "channels"

    def test_overwriting_list_raises_error(self, parent):
        """A single channel is only allowed, if there is no list of that name."""
        with pytest.raises(ValueError, match="already exists"):
            parent.add_child(GenericBase, prefix=None)

    def test_single_channel(self, parent):
        """Test, that id=None creates a single channel."""
        assert isinstance(parent.function, GenericBase)
        assert parent.function._name == "function"

    def test_evaluating_false_id_creates_channels(self, parent):
        """Test that an id evaluating false (e.g. 0) creates a channels list."""
        parent.add_child(GenericBase, 0, collection="special")
        assert isinstance(parent.special, list)


class TestRemoveChild:
    @pytest.fixture()
    def parent_without_children(self):
        parent = CommonBaseTesting(ProtocolAdapter())
        parent.add_child(GenericBase, "A")
        parent.add_child(GenericBase, "B")
        parent.add_child(GenericBase, prefix=None, collection="function")
        parent.remove_child(parent.ch_A)
        parent.remove_child(parent.channels[0])
        parent.remove_child(parent.function)
        return parent

    def test_remove_child_leaves_channels_empty(self, parent_without_children):
        assert parent_without_children.channels == []

    def test_remove_child_clears_attributes(self, parent_without_children):
        assert getattr(parent_without_children, "ch_A", None) is None
        assert getattr(parent_without_children, "ch_B", None) is None
        assert getattr(parent_without_children, "function", None) is None


# Test CommonBase communication
def test_ask_writes_and_reads():
    with expected_protocol(CommonBaseTesting, [("Sent", "Received")]) as inst:
        assert inst.ask("Sent") == "Received"


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


# Test CommonBase property creators
@pytest.mark.parametrize("dynamic", [False, True])
def test_control_doc(dynamic):
    doc = """ X property """

    class Fake(CommonBaseTesting):
        x = CommonBase.control(
            "", "%d", doc,
            dynamic=dynamic
        )

    expected_doc = doc + "(dynamic)" if dynamic else doc
    assert Fake.x.__doc__ == expected_doc


# Test ChildDescriptor
@pytest.mark.parametrize("args, pairs, kwargs", (
    ((Child, ["A", "B"]), [(Child, "A"), (Child, "B")], {'prefix': "ch_"}),
    (((Child, GenericBase, Child), (1, 2, 3)), [(Child, 1), (GenericBase, 2), (Child, 3)], {'prefix': "ch_"}),
    ((Child, "mm", None), [(Child, "mm")], {'prefix': None}),
))
def test_ChildDescriptor(args, pairs, kwargs):
    """Test whether the descriptor receives the right arguments."""
    d = CommonBase.children(*args)
    assert list(d.pairs) == pairs
    assert d.kwargs == kwargs


def test_ChildDescriptor_different_list_lengths():
    with pytest.raises(AssertionError, match="Lengths"):
        CommonBase.children(("A", "B", "C"), (Child,) * 2)


def test_ChildDescriptor_invalid_input():
    with pytest.raises(ValueError, match="Invalid"):
        CommonBase.children("A", {})
