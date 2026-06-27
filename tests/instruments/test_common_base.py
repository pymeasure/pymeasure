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

import logging
from typing import TYPE_CHECKING, Any

import pytest
try:
    from typing_extensions import assert_type
    TYPING_EXTENSION = True
except ImportError:
    TYPING_EXTENSION = False

from pymeasure.units import ureg
from pymeasure.test import expected_protocol
from pymeasure.instruments.common_base import (
    DynamicProperty, CommonBase, IdType, InstrumentProperty, cast_or_str, identity,
)
from pymeasure.adapters import Adapter, FakeAdapter, ProtocolAdapter
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


class CommonBaseTesting(CommonBase):
    """Add read/write methods in order to use the ProtocolAdapter."""

    parent: CommonBase | Adapter
    id: IdType

    def __init__(self, parent: CommonBase | Adapter, id: IdType = None, *args, **kwargs):
        if "test" in kwargs:
            self.test = kwargs.pop("test")
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.id = id
        self._name: str = ""
        self._protected: bool = False
        self._collection: str = ""
        self.args = args
        self.kwargs = kwargs

    def wait_for(self, query_delay=0):
        pass

    def write(self, command, **kwargs):
        self.parent.write(command, **kwargs)

    def read(self, **kwargs):
        return self.parent.read(**kwargs)


class GenericBase(CommonBaseTesting):
    parent: CommonBase
    id: IdType = 1

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


class FakeBase(CommonBaseTesting):
    def __init__(self, *args, **kwargs):
        super().__init__(FakeAdapter(), *args, **kwargs)

    fake_ctrl = CommonBase.control(
        "", "%d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_setting = CommonBase.setting(
        "%d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_measurement = CommonBase.measurement(
        "", "docs",
        values={'X': 1, 'Y': 2, 'Z': 3},
        map_values=True,
        dynamic=True,
    )
    fake_ctrl_errors = CommonBase.control(
        "ge", "se %d", "Fake control for getting errors after getting/setting values.",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
        check_get_errors=True,
        check_set_errors=True,
        cast=str,
    )


@pytest.fixture()
def fake():
    return FakeBase()


class ExtendedBase(FakeBase):
    # Keep values unchanged, just derive another instrument, e.g. to add more properties
    fake_ctrl2 = CommonBase.control(
        "", "%d", "docs",
        validator=strict_range,
        values=(1, 10),
        dynamic=True,
    )

    fake_ctrl2_values = (5, 20)


class StrictExtendedBase(ExtendedBase):
    # Use strict instead of truncated range validator
    fake_ctrl_validator = strict_range
    fake_setting_validator = strict_range


class NewRangeBase(FakeBase):
    # Choose different properties' values, like you would for another device model
    fake_ctrl_values = (10, 20)
    fake_setting_values = (10, 20)
    fake_measurement_values = {'X': 4, 'Y': 5, 'Z': 6}


class ChildChannel(CommonBase):
    """A child, which accepts parent and id arguments."""

    parent: CommonBase
    id: IdType

    def __init__(self, parent: CommonBase, id: IdType = None, *args, **kwargs):
        self.parent = parent
        self.id = id
        self._name: str = ""
        self._protected: bool = False
        self._collection: str = ""
        super().__init__()


class MultiChannelParent(CommonBaseTesting):
    """A Base as a parent"""
    channels = CommonBase.MultiChannelCreator(GenericBase, ("A", "B", "C"))
    analog = CommonBase.MultiChannelCreator(GenericBase, [1, 2], prefix="an_", test=True)


class SingleChannelParent(CommonBaseTesting):
    """A Base as a parent"""
    ch_A = CommonBase.ChannelCreator(GenericBase, "A")
    ch_B = CommonBase.ChannelCreator(GenericBase, "B")
    ch_C = CommonBase.ChannelCreator(GenericBase, "C")
    an_1 = CommonBase.ChannelCreator(GenericBase, 1, collection="analog", test=True)
    an_2 = CommonBase.ChannelCreator(GenericBase, 2, collection="analog", test=True)
    function = CommonBase.ChannelCreator(ChildChannel)


class MixChannelParent(CommonBaseTesting):
    """A Base as a parent"""
    channels = CommonBase.MultiChannelCreator(GenericBase, ("A", "B", "C"))
    ch_D = CommonBase.ChannelCreator(GenericBase, "D")
    output_Z = CommonBase.ChannelCreator(GenericBase, "Z")
    analog = CommonBase.MultiChannelCreator(GenericBase, list(range(0, 10)), prefix="an_",
                                            test=True)


# Test dynamic properties
def test_dynamic_property_fget_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="Unreadable attribute"):
        d.__get__(5)


def test_dynamic_property_fset_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="set attribute"):
        d.__set__(5, 7)


# Test CommonBase.MultipleChannelCreator child management
class TestInitWithMultipleChannelCreator:
    @pytest.fixture()
    def parent(self) -> MultiChannelParent:
        return MultiChannelParent(ProtocolAdapter())

    def test_channels(self, parent: MultiChannelParent):
        assert len(parent.channels) == 3
        assert parent.ch_A == parent.channels['A']
        assert isinstance(parent.ch_A, GenericBase)

    def test_analog(self, parent: MultiChannelParent):
        assert len(parent.analog) == 2
        assert parent.an_1 == parent.analog[1]
        assert isinstance(parent.analog[1], GenericBase)

    def test_removal_of_protected_children_fails(self, parent: MultiChannelParent):
        with pytest.raises(TypeError, match="cannot remove channels defined at class"):
            parent.remove_child(parent.ch_A)

    def test_channel_creation_works_more_than_once(self):
        """A zipper object works just once, ensure that a class may be used more often."""
        p1 = MultiChannelParent(ProtocolAdapter())  # first instance of that class
        assert isinstance(p1.analog[1], GenericBase)  # verify that it worked once
        p2 = MultiChannelParent(ProtocolAdapter())  # second instance of that class
        assert isinstance(p2.analog[1], GenericBase)  # verify that it worked a second time

    def test_channel_pairs_length(self, parent: MultiChannelParent):
        assert len(parent.get_channel_pairs()) == 5

    def test_channel_creator_remains_unchanged_as_class_attribute(self, parent):
        assert isinstance(parent.__class__.channels, CommonBase.MultiChannelCreator)


# Test CommonBase.ChannelCreator child management
class TestInitWithChannelCreator:
    @pytest.fixture()
    def parent(self) -> SingleChannelParent:
        return SingleChannelParent(ProtocolAdapter())

    def test_channels(self, parent: SingleChannelParent):
        assert len(parent.channels) == 3
        assert parent.ch_A == parent.channels['A']
        assert isinstance(parent.ch_A, GenericBase)

    def test_analog(self, parent: SingleChannelParent):
        assert len(parent.analog) == 2
        assert parent.an_1 == parent.analog[1]
        assert isinstance(parent.analog[1], GenericBase)

    def test_function(self, parent: SingleChannelParent):
        assert isinstance(parent.function, ChildChannel)

    def test_removal_of_protected_children_fails(self, parent: SingleChannelParent):
        with pytest.raises(TypeError, match="cannot remove channels defined at class"):
            parent.remove_child(parent.ch_A)

    def test_removal_of_protected_single_children_fails(self, parent: SingleChannelParent):
        with pytest.raises(TypeError, match="cannot remove channels defined at class"):
            parent.remove_child(parent.function)

    def test_channel_creation_works_more_than_once(self):
        """A zipper object works just once, ensure that a class may be used more often."""
        p1 = SingleChannelParent(ProtocolAdapter())  # first instance of that class
        assert isinstance(p1.analog[1], GenericBase)  # verify that it worked once
        p2 = SingleChannelParent(ProtocolAdapter())  # second instance of that class
        assert isinstance(p2.analog[1], GenericBase)  # verify that it worked a second time

    def test_channel_pairs_length(self, parent: SingleChannelParent):
        assert len(parent.get_channel_pairs()) == 6

    def test_channel_creator_remains_unchanged_as_class_attribute(self, parent):
        assert isinstance(parent.__class__.ch_A, CommonBase.ChannelCreator)
        assert isinstance(parent.__class__.an_1, CommonBase.ChannelCreator)
        assert isinstance(parent.__class__.function, CommonBase.ChannelCreator)


# Test combination CommonBase.MultipleChannelCreator and CommonBase.ChannelCreator
# child management
class TestInitWithMixChannelCreator:
    @pytest.fixture()
    def parent(self) -> MixChannelParent:
        return MixChannelParent(ProtocolAdapter())

    def test_channels(self, parent: MixChannelParent):
        assert len(parent.channels) == 5
        assert parent.ch_A == parent.channels['A']
        assert parent.output_Z == parent.channels['Z']
        assert isinstance(parent.ch_A, GenericBase)
        assert isinstance(parent.output_Z, GenericBase)

    def test_analog(self, parent: MixChannelParent):
        assert len(parent.analog) == 10
        assert parent.an_1 == parent.analog[1]
        assert isinstance(parent.analog[1], GenericBase)

    def test_removal_of_protected_children_fails(self, parent: MixChannelParent):
        with pytest.raises(TypeError, match="cannot remove channels defined at class"):
            parent.remove_child(parent.ch_A)

    def test_channel_creation_works_more_than_once(self):
        """A zipper object works just once, ensure that a class may be used more often."""
        p1 = MixChannelParent(ProtocolAdapter())  # first instance of that class
        assert isinstance(p1.analog[1], GenericBase)  # verify that it worked once
        assert isinstance(p1.output_Z, GenericBase)
        p2 = MixChannelParent(ProtocolAdapter())  # second instance of that class
        assert isinstance(p2.analog[1], GenericBase)  # verify that it worked a second time
        assert isinstance(p2.output_Z, GenericBase)

    def test_channel_pairs_length(self, parent: MixChannelParent):
        assert len(parent.get_channel_pairs()) == 15

    def test_channel_creator_remains_unchanged_as_class_attribute(self, parent):
        assert isinstance(parent.__class__.channels, CommonBase.MultiChannelCreator)
        assert isinstance(parent.__class__.analog, CommonBase.MultiChannelCreator)
        assert isinstance(parent.__class__.output_Z, CommonBase.ChannelCreator)


class TestAddChild:
    """Test the `add_child` method"""

    @pytest.fixture()
    def parent(self) -> CommonBaseTesting:
        parent = CommonBaseTesting(ProtocolAdapter())
        parent.add_child(GenericBase, "A", test=5)
        parent.add_child(GenericBase, "B")
        parent.add_child(GenericBase, prefix=None, collection="function")
        return parent

    def test_correct_class(self, parent: CommonBaseTesting):
        assert isinstance(parent.ch_A, GenericBase)

    def test_arguments(self, parent: CommonBaseTesting):
        assert parent.channels["A"].id == "A"
        assert parent.channels["A"].test == 5

    def test_attribute_access(self, parent: CommonBaseTesting):
        assert parent.ch_B == parent.channels["B"]

    def test_len(self, parent: CommonBaseTesting):
        assert len(parent.channels) == 2

    def test_attributes(self, parent: CommonBaseTesting):
        assert parent.ch_A._name == "ch_A"
        assert parent.ch_B._collection == "channels"

    def test_overwriting_list_raises_error(self, parent: CommonBaseTesting):
        """A single channel is only allowed, if there is no list of that name."""
        with pytest.raises(ValueError, match="already exists"):
            parent.add_child(GenericBase, prefix=None)

    def test_single_channel(self, parent: CommonBaseTesting):
        """Test, that id=None creates a single channel."""
        assert isinstance(parent.function, GenericBase)
        assert parent.function._name == "function"

    def test_evaluating_false_id_creates_channels(self, parent: CommonBaseTesting):
        """Test that an id evaluating false (e.g. 0) creates a channels list."""
        parent.add_child(GenericBase, 0, collection="special")
        assert isinstance(parent.special, dict)


class TestRemoveChild:
    @pytest.fixture()
    def parent_without_children(self) -> CommonBaseTesting:
        parent = CommonBaseTesting(ProtocolAdapter())
        parent.add_child(GenericBase, "A")
        parent.add_child(GenericBase, "B")
        parent.add_child(GenericBase, prefix=None, collection="function")
        parent.remove_child(parent.ch_A)
        parent.remove_child(parent.channels["B"])
        parent.remove_child(parent.function)
        return parent

    def test_remove_child_leaves_channels_empty(self, parent_without_children):
        assert parent_without_children.channels == {}

    def test_remove_child_clears_attributes(self, parent_without_children):
        assert getattr(parent_without_children, "ch_A", None) is None
        assert getattr(parent_without_children, "ch_B", None) is None
        assert getattr(parent_without_children, "function", None) is None


class TestInheritanceWithChildren:
    class InstrumentSubclass(MultiChannelParent):
        """Override one channel group, inherit other groups."""
        function = CommonBase.ChannelCreator(GenericBase, "overridden", prefix=None)

    @pytest.fixture()
    def parent(self) -> InstrumentSubclass:
        return self.InstrumentSubclass(ProtocolAdapter())

    def test_inherited_children_are_present(self, parent: InstrumentSubclass):
        assert isinstance(parent.ch_A, GenericBase)

    def test_ChannelCreator_is_replaced_by_channel_collection(self, parent: InstrumentSubclass):
        assert not isinstance(parent.channels, CommonBase.ChannelCreator)

    def test_overridden_child_is_present(self, parent: InstrumentSubclass):
        assert parent.function.id == "overridden"


# Test MultiChannelCreator
@pytest.mark.parametrize("args, pairs, kwargs", (
        ((ChildChannel, ["A", "B"]), [(ChildChannel, "A"), (ChildChannel, "B")], {'prefix': "ch_"}),
        (((ChildChannel, GenericBase, ChildChannel), (1, 2, 3)),
         [(ChildChannel, 1), (GenericBase, 2), (ChildChannel, 3)], {'prefix': "ch_"}),
))
def test_MultiChannelCreator(args, pairs, kwargs):
    """Test whether the channel creator receives the right arguments."""
    d = CommonBase.MultiChannelCreator(*args)
    i = 0
    for pair in d.pairs:
        assert pair == pairs[i]
        i += 1
    assert d.kwargs == kwargs


def test_MultiChannelCreator_different_list_lengths():
    with pytest.raises(AssertionError, match="Lengths"):
        CommonBase.MultiChannelCreator(id=("A", "B", "C"), cls=(ChildChannel,) * 2)


def test_ChannelCreator_invalid_input():
    with pytest.raises(ValueError, match="Invalid"):
        CommonBase.ChannelCreator("A", {}) # type: ignore


# Test CommonBase communication
def test_ask_writes_and_reads():
    with expected_protocol(CommonBaseTesting, [("Sent", "Received")]) as inst:  # type: ignore[arg-type]
        assert inst.ask("Sent") == "Received"


@pytest.mark.parametrize("value, kwargs, result",
                         (("5,6,7", {}, [5, 6, 7]),
                          ("5.1,6,x", {"cast": cast_or_str(float)}, [5.1, 6, "x"]),
                          ("5,6,x", {"cast": cast_or_str(int)}, [5, 6, "x"]),
                          ("5.6.7", {'separator': '.'}, [5, 6, 7]),
                          ("5,6,7", {'cast': str}, ['5', '6', '7']),
                          ("X,Y,Z", {"cast": str}, ['X', 'Y', 'Z']),
                          ("X,Y,Z", {'cast': str}, ['X', 'Y', 'Z']),
                          ("X.Y.Z", {"separator": ".", "cast":str}, ["X", "Y", "Z"]),
                          ("0,5,7.1", {'cast': bool}, [False, True, True]),
                          ("x5x", {'preprocess_reply': lambda v: v.strip("x")}, [5]),
                          ("X,Y,Z", {'maxsplit': 1, "cast": str}, ["X", "Y,Z"]),
                          ("X,Y,Z", {'maxsplit': 0, "cast": str}, ["X,Y,Z"]),
                          ))
def test_values(value, kwargs, result):
    cb = CommonBaseTesting(FakeAdapter(), "test")
    assert cb.values(value, **kwargs) == result


def test_values_fallback_emits_futurewarning():
    cb = CommonBaseTesting(FakeAdapter(), "test")
    with pytest.warns(FutureWarning, match=r"Cannot cast.*In a future version"):
        result = cb.values("X,Y,Z")
    assert result == ["X", "Y", "Z"]

def test_values_fallback_raises_futurewarning_in_pymeasure():
    cb = CommonBaseTesting(FakeAdapter(), "test")
    # "match" should match pyproject.toml error raising
    with pytest.raises(FutureWarning, match=r"Cannot cast.*In a future version"):
        cb.values("X,Y,Z")


def test_binary_values(fake):
    fake.read_binary_values = fake.read
    assert fake.binary_values("123") == "123"


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


def test_check_errors_not_implemented(fake):
    with pytest.raises(NotImplementedError):
        fake.check_errors()


def test_check_get_errors_not_implemented(fake):
    with pytest.raises(NotImplementedError):
        fake.check_get_errors()


def test_control_check_get_errors(fake, caplog):
    def checking():
        fake.error = True
        return [(7, "some error")]

    fake.check_get_errors = checking
    fake.fake_ctrl_errors
    assert fake.error is True
    assert caplog.record_tuples[-1] == (
        "pymeasure.instruments.common_base",
        logging.ERROR,
        "Error received after trying to get a property with the command 'ge': '(7, 'some error')'."
    )


def test_control_check_get_errors_multiple_errors(fake, caplog):
    def checking():
        fake.error = True
        return [15, (19, "x")]

    fake.check_get_errors = checking
    fake.fake_ctrl_errors
    assert caplog.record_tuples[-1] == (
        "pymeasure.instruments.common_base",
        logging.ERROR,
        "Error received after trying to get a property with the command 'ge': '15', '(19, 'x')'."  # noqa: E501
    )


def test_control_check_get_errors_log_exception(fake, caplog):
    with pytest.raises(NotImplementedError):
        fake.fake_ctrl_errors
    assert caplog.record_tuples[-1] == (
        "pymeasure.instruments.common_base",
        logging.ERROR,
        "Exception raised while getting a property with the command 'ge': 'Implement it in a subclass.'."  # noqa: E501
    )


def test_check_set_errors_not_implemented(fake):
    with pytest.raises(NotImplementedError):
        fake.check_set_errors()


def test_control_check_set_errors(fake, caplog):
    def checking():
        fake.error = True
        return [(7, "Error!")]

    fake.check_set_errors = checking
    fake.fake_ctrl_errors = 7
    assert fake.error is True
    assert caplog.record_tuples[-1] == (
        "pymeasure.instruments.common_base",
        logging.ERROR,
        "Error received after trying to set a property with the command 'se 7': '(7, 'Error!')'."
    )


def test_control_check_set_errors_log_exception(fake, caplog):
    with pytest.raises(NotImplementedError):
        fake.fake_ctrl_errors = 7
    assert caplog.record_tuples[-1] == (
        "pymeasure.instruments.common_base",
        logging.ERROR,
        "Exception raised while setting a property with the command 'se 7': 'Implement it in a subclass.'."  # noqa: E501
    )


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_validator(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=range(10),
            dynamic=dynamic
        )

    fake = Fake()
    fake.x_validator = truncated_range  # works only if dynamic
    fake.x = 5
    assert fake.read() == '5'
    fake.x = 5
    assert fake.x == 5
    if not dynamic:
        with pytest.raises(ValueError):
            fake.x = 20
    else:
        fake.x = 20


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_validator_map(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=[4, 5, 6, 7],
            map_values=True,
            dynamic=dynamic
        )

    fake = Fake()
    fake.x_map_values = False  # works only if dynamic
    fake.x = 5
    if dynamic:
        assert fake.read() == '5'  # no mapping
    else:
        assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError):
        fake.x = 20


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_dict_map(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={5: 1, 10: 2, 20: 3},
            map_values=True,
            dynamic=dynamic
        )

    fake = Fake()
    fake.x_values = {1: 1, 20: 2, 5: 3}
    fake.x = 5
    if dynamic:
        assert fake.read() == '3'
    else:
        assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    fake.x = 20
    if dynamic:
        assert fake.read() == '2'
    else:
        assert fake.read() == '3'


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_dict_str_map(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values=True,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = 'X'
    assert fake.read() == '1'
    fake.x = 'Y'
    assert fake.x == 'Y'
    fake.x = 'Z'
    assert fake.read() == '3'


def test_value_not_in_map(fake):
    fake.parent._buffer = "123"
    with pytest.raises(KeyError, match="not found in mapped values"):
        fake.fake_measurement


def test_control_invalid_values_get():
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            values=b"abasdfe", map_values=True, cast=str)

    with pytest.raises(ValueError, match="Values of type"):
        Fake().x


def test_control_invalid_values_set():
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            values=b"abasdfe", map_values=True)

    with pytest.raises(ValueError, match="Values of type"):
        Fake().x = 7


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_process(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d", "",
            validator=strict_range,
            values=[5e-3, 120e-3],
            get_process=lambda v: v * 1e-3,
            set_process=lambda v: v * 1e3,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x_get_process = lambda v: v
    fake.x_set_process = lambda v: v
    fake.x = 10e-3
    if dynamic:
        assert fake.read() == '0'
    else:
        assert fake.read() == '10'
    fake.x = 30e-3
    if dynamic:
        assert fake.x == 0
    else:
        assert fake.x == 30e-3


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_get_process(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "JUNK%d", "",
            validator=strict_range,
            values=[0, 10],
            get_process=lambda v: int(v.replace('JUNK', '')),
            dynamic=dynamic,
            cast=str,
        )

    fake = Fake()
    fake.x_get_process = lambda v: v  # works only if dynamic
    fake.x = 5
    assert fake.read() == 'JUNK5'
    fake.x = 6
    if dynamic:
        assert fake.x == 'JUNK6'
    else:
        assert fake.x == 6


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_get_process_list(dynamic):
    class Fake(CommonBaseTesting):
        x = CommonBase.control(
            "G", "%d", "doc",
            get_process_list=lambda v: [v[0] + 1, *v, len(v)],
            dynamic=dynamic,
        )

    # override get_process_list should only work when dynamic
    Fake.x_get_process_list = lambda v: [0, "2"]  # type: ignore[attr-defined]

    with expected_protocol(Fake, [("G", "0, 1, 2, 3.4")]) as inst:  # type: ignore[arg-type]
        if dynamic:
            assert inst.x == [0, "2"]
        else:
            assert inst.x == [1, 0, 1, 2, 3.4, 4]


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_preprocess_reply_property(dynamic):
    # test setting preprocess_reply at property-level
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "JUNK%d",
            "",
            preprocess_reply=lambda v: v.replace('JUNK', ''),
            dynamic=dynamic,
            cast=int,
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    # notice that read returns the full reply since preprocess_reply is only
    # called inside CommonBase.values()
    fake.x = 5
    assert fake.x == 5
    fake.x = 5
    assert type(fake.x) is int


def test_control_parameters_for_values():
    """Test how to hand a parameter to `values` method."""

    class Fake(FakeBase):
        x = CommonBase.control(
            "", "JUNK%d",
            "",
            preprocess_reply=lambda v: v.replace('JUNK', ''),
            cast=int,
            values_kwargs={'testing': True},
        )

        def values(self, cmd, testing=False, **kwargs): # type: ignore[override]
            self.testing = testing
            return super().values(cmd, **kwargs)

    fake = Fake()
    fake.x = 5
    fake.x
    assert fake.testing is True


def test_measurement_parameters_for_values():
    """Test how to hand a parameter to `values` method."""

    class Fake(FakeBase):
        x = CommonBase.measurement(
            "JUNK%d",
            "",
            preprocess_reply=lambda v: v.replace('JUNK', ''),
            cast=cast_or_str(int),
            values_kwargs={'testing': True},
        )

        def values(self, command, testing=False, **kwargs): # type: ignore[override]
            self.testing = testing
            return super().values(command, **kwargs)

    fake = Fake()
    fake.write("5")
    fake.x
    assert fake.testing is True


@pytest.mark.parametrize("cast, expected", ((float, 5.5),
                                            (ureg.Quantity, ureg.Quantity(5.5)),
                                            (str, "5.5"),
                                            (lambda v: int(float(v)), 5)
                                            ))
def test_measurement_cast(cast, expected):
    class Fake(CommonBaseTesting):
        x = CommonBase.measurement(
            "x", "doc", cast=cast)

    with expected_protocol(Fake, [("x", "5.5")]) as instr:  # type: ignore[arg-type]
        assert instr.x == expected


def test_measurement_cast_int():
    class Fake(CommonBaseTesting):
        def __init__(self, adapter, **kwargs):
            super().__init__(adapter, "test", **kwargs)

        x = CommonBase.measurement(
            "x", "doc", cast=int)

    with expected_protocol(Fake, [("x", "5")]) as instr:  # type: ignore[arg-type]
        y = instr.x
        assert y == 5
        assert type(y) is int


def test_measurement_unitful_property():
    class Fake(CommonBaseTesting):
        def __init__(self, adapter, **kwargs):
            super().__init__(adapter, "test", **kwargs)

        x = CommonBase.measurement(
            "x", "doc", get_process=lambda v: ureg.Quantity(v, ureg.m))

    with expected_protocol(Fake, [("x", "5.5")]) as instr:  # type: ignore[arg-type]
        y = instr.x
        assert y.m_as(ureg.m) == 5.5


@pytest.mark.parametrize("dynamic", [False, True])
def test_measurement_dict_str_map(dynamic):
    class Fake(FakeBase):
        x = CommonBase.measurement(
            "", "",
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values=True,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.write('1')
    assert fake.x == 'X'
    fake.write('2')
    assert fake.x == 'Y'
    fake.write('3')
    assert fake.x == 'Z'


def test_measurement_set(fake):
    with pytest.raises(LookupError, match="Property can not be set."):
        fake.fake_measurement = 7


def test_setting_get(fake):
    with pytest.raises(LookupError, match="Property can not be read."):
        fake.fake_setting


@pytest.mark.parametrize("dynamic", [False, True])
def test_setting_process(dynamic):
    class Fake(FakeBase):
        x = CommonBase.setting(
            "OUT %d", "",
            set_process=lambda v: int(bool(v)),
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = False
    assert fake.read() == 'OUT 0'
    fake.x = 2
    assert fake.read() == 'OUT 1'


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_multivalue(dynamic):
    class Fake(FakeBase):
        x = CommonBase.control(
            "", "%d,%d", "",
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = (5, 6)  # type: ignore[assignment]
    assert fake.read() == '5,6'


@pytest.mark.parametrize(
    'set_command, given, expected, dynamic',
    [("%d", 5, 5, False),
     ("%d", 5, 5, True),
     ("%d, %d", (5, 6), [5, 6], False),  # input has to be a tuple, not a list
     ("%d, %d", (5, 6), [5, 6], True),  # input has to be a tuple, not a list
     ])
def test_FakeBase_control(set_command, given, expected, dynamic):
    """FakeBase's custom simple control needs to process values correctly.
    """

    class Fake(FakeBase):
        x = FakeBase.control(
            "", set_command, "",
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = given
    assert fake.x == expected


def test_dynamic_property_unchanged_by_inheritance():
    generic = FakeBase()
    extended = ExtendedBase()

    generic.fake_ctrl = 50
    assert generic.fake_ctrl == 10
    extended.fake_ctrl = 50
    assert extended.fake_ctrl == 10

    generic.fake_setting = 50
    assert generic.read() == '10'
    extended.fake_setting = 50
    assert extended.read() == '10'

    generic.write('1')
    assert generic.fake_measurement == 'X'
    extended.write('1')
    assert extended.fake_measurement == 'X'


def test_dynamic_property_strict_raises():
    # Tests also that dynamic properties can be changed at class level.
    strict = StrictExtendedBase()

    with pytest.raises(ValueError):
        strict.fake_ctrl = 50
    with pytest.raises(ValueError):
        strict.fake_setting = 50


def test_dynamic_property_values_update_in_subclass():
    newrange = NewRangeBase()

    newrange.fake_ctrl = 50
    assert newrange.fake_ctrl == 20

    newrange.fake_setting = 50
    assert newrange.read() == '20'

    newrange.write('4')
    assert newrange.fake_measurement == 'X'


def test_dynamic_property_values_update_in_instance(fake):
    fake.fake_ctrl_values = (0, 33)
    fake.fake_ctrl = 50
    assert fake.fake_ctrl == 33

    fake.fake_setting_values = (0, 33)
    fake.fake_setting = 50
    assert fake.read() == '33'

    fake.fake_measurement_values = {'X': 7}
    fake.write('7')
    assert fake.fake_measurement == 'X'


def test_dynamic_property_values_update_in_one_instance_leaves_other_unchanged():
    generic1 = FakeBase()
    generic2 = FakeBase()

    generic1.fake_ctrl_values = (0, 33)
    generic1.fake_ctrl = 50
    generic2.fake_ctrl = 50
    assert generic1.fake_ctrl == 33
    assert generic2.fake_ctrl == 10


def test_dynamic_property_reading_special_attributes_forbidden(fake):
    with pytest.raises(AttributeError):
        fake.fake_ctrl_validator


def test_dynamic_property_with_inheritance():
    inst = ExtendedBase()
    # Test for inherited attribute
    with pytest.raises(AttributeError):
        inst.fake_ctrl_validator
    # Test for new attribute
    with pytest.raises(AttributeError):
        inst.fake_ctrl2_validator


def test_dynamic_property_values_defined_at_superclass_level():
    """Test whether a dynamic property can be changed a superclass level"""
    inst = StrictExtendedBase()
    # Test whether the change of values from (1, 10) to (5, 20) succeeded:
    inst.fake_ctrl2 = 17  # should raise an error if change unsuccessful
    with pytest.raises(ValueError):
        inst.fake_ctrl2 = 2  # should not raise an error if change unsuccessful

class ExampleControlTypes(CommonBase):
    """Verify via type checker whether control types typing works.

    Properties without explicit type annotations so that the type checker
    infers the return type of ``CommonBase.control``. The expected types
    are then checked with ``assert_type`` in the ``TYPE_CHECKING`` block
    below, which catches cases where the inferred type is ``Any``
    (a bare annotation would shadow that).
    """
    @staticmethod
    def return_int(value: Any) -> int:
        return 5

    @staticmethod
    def int_validator(value: int, values: Any) -> Any:
        pass

    no_arguments = CommonBase.control(
        "g",
        "s",
        "d",
    )

    cast_only = CommonBase.control(
        "g",
        "s",
        "d",
        cast=int,
    )

    cast_function = CommonBase.control(
        "g",
        "s",
        "d",
        cast=return_int,
    )

    get_process_with_cast = CommonBase.control(
        "g",
        "s",
        "d",
        cast=int,
        get_process=identity,
    )

    get_process_with_cast_func = CommonBase.control(
        "g",
        "s",
        "d",
        cast=return_int,
        get_process=identity,
    )

    get_process_list_with_cast = CommonBase.control(
        "g",
        "s",
        "d",
        cast=int,
        get_process_list=identity,
    )

    get_process_and_get_process_list = CommonBase.control(
        "g",
        "s",
        "d",
        get_process=identity,
        get_process_list=identity,
    )

    get_process_and_get_process_list_with_cast = CommonBase.control(
        "g",
        "s",
        "d",
        cast=int,
        get_process=identity,
        get_process_list=identity,
    )

    get_process_and_get_process_list_with_cast_function = CommonBase.control(
        "g",
        "s",
        "d",
        cast=lambda v: int(v),
        get_process=identity,
        get_process_list=identity,
    )

    map_values = CommonBase.control(
        "g",
        "s",
        "d",
        cast=int,
        get_process=identity,
        map_values=True,
    )

    map_values_validator = CommonBase.control(
        "g",
        "s",
        "d",
        cast=int,
        get_process=identity,
        map_values=True,
        validator=int_validator,
    )



if TYPE_CHECKING and TYPING_EXTENSION:
    assert_type(ExampleControlTypes.no_arguments, InstrumentProperty[float])
    assert_type(ExampleControlTypes.cast_only, InstrumentProperty[int])
    assert_type(ExampleControlTypes.cast_function, InstrumentProperty[int])
    assert_type(ExampleControlTypes.get_process_with_cast, InstrumentProperty[int])
    assert_type(ExampleControlTypes.get_process_list_with_cast, InstrumentProperty[list[int]])
    assert_type(
        ExampleControlTypes.get_process_and_get_process_list,
        InstrumentProperty[list[float] | float],
    )
    assert_type(
        ExampleControlTypes.get_process_and_get_process_list_with_cast,
        InstrumentProperty[list[int] | int],
    )
    assert_type(
        ExampleControlTypes.get_process_and_get_process_list_with_cast_function,
        InstrumentProperty[list[int] | int],
    )
    assert_type(ExampleControlTypes.map_values, InstrumentProperty[Any])
    assert_type(ExampleControlTypes.map_values_validator, InstrumentProperty[int])


class ExampleMeasurementTypes(CommonBase):
    """Verify via type checker whether measurement types typing works."""

    @staticmethod
    def return_int(value: Any) -> int:
        return 5

    no_arguments = CommonBase.measurement(
        "g",
        "d",
    )

    cast_only = CommonBase.measurement(
        "g",
        "d",
        cast=int,
    )

    cast_function = CommonBase.measurement(
        "g",
        "d",
        cast=return_int,
    )

    get_process_with_cast = CommonBase.measurement(
        "g",
        "d",
        cast=int,
        get_process=identity,
    )

    get_process_list_with_cast = CommonBase.measurement(
        "g",
        "d",
        cast=int,
        get_process_list=identity,
    )

    get_process_and_get_process_list = CommonBase.measurement(
        "g",
        "d",
        get_process=identity,
        get_process_list=identity,
    )

    get_process_and_get_process_list_with_cast = CommonBase.measurement(
        "g",
        "d",
        cast=int,
        get_process=identity,
        get_process_list=identity,
    )

    get_process_and_get_process_list_with_cast_function = CommonBase.measurement(
        "g",
        "d",
        cast=lambda v: int(v),
        get_process=identity,
        get_process_list=identity,
    )

    map_values = CommonBase.measurement(
        "g",
        "d",
        cast=int,
        get_process=identity,
        map_values=True,
    )


if TYPE_CHECKING and TYPING_EXTENSION:
    assert_type(ExampleMeasurementTypes.no_arguments, InstrumentProperty[float])
    assert_type(ExampleMeasurementTypes.cast_only, InstrumentProperty[int])
    assert_type(ExampleMeasurementTypes.cast_function, InstrumentProperty[int])
    assert_type(ExampleMeasurementTypes.get_process_with_cast, InstrumentProperty[int])
    assert_type(ExampleMeasurementTypes.get_process_list_with_cast, InstrumentProperty[list[int]])
    assert_type(
        ExampleMeasurementTypes.get_process_and_get_process_list,
        InstrumentProperty[list[float] | float],
    )
    assert_type(
        ExampleMeasurementTypes.get_process_and_get_process_list_with_cast,
        InstrumentProperty[list[int] | int],
    )
    assert_type(
        ExampleMeasurementTypes.get_process_and_get_process_list_with_cast_function,
        InstrumentProperty[list[int] | int],
    )
    assert_type(ExampleMeasurementTypes.map_values, InstrumentProperty[Any])


class ExampleSettingTypes(CommonBase):
    """Verify via type checker whether setting types typing works."""

    @staticmethod
    def int_validator(value: int, values: Any) -> Any:
        pass

    @staticmethod
    def int_set_process(value: int) -> Any:
        pass

    default = CommonBase.setting(
        "s %d",
        "d",
    )

    validator = CommonBase.setting(
        "s %d",
        "d",
        validator=int_validator,
        set_process=lambda v: v,
    )

    validator_untyped = CommonBase.setting(
        "s %d",
        "d",
        validator=strict_discrete_set,
    )

    set_process = CommonBase.setting(
        "c",
        "d",
        set_process=int_set_process,
    )


if TYPE_CHECKING and TYPING_EXTENSION:
    assert_type(ExampleSettingTypes.default, InstrumentProperty[Any])
    assert_type(ExampleSettingTypes.validator, InstrumentProperty[int])
    assert_type(ExampleSettingTypes.validator_untyped, InstrumentProperty[Any])
    assert_type(ExampleSettingTypes.set_process, InstrumentProperty[int])
