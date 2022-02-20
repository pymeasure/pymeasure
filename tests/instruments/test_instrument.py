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

from pymeasure.instruments import Instrument
from pymeasure.instruments.fakes import FakeInstrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


def test_fake_instrument():
    fake = FakeInstrument()
    fake.write("Testing")
    assert fake.read() == "Testing"
    assert fake.read() == ""
    assert fake.values("5") == [5]


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_doc(dynamic):
    doc = """ X property """

    class Fake(Instrument):
        x = Instrument.control(
            "", "%d", doc,
            dynamic=dynamic
        )

    expected_doc = doc + "(dynamic)" if dynamic else doc
    assert Fake.x.__doc__ == expected_doc


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_validator(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=range(10),
            dynamic=dynamic
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '5'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError):
        fake.x = 20


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_validator_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=[4, 5, 6, 7],
            map_values=True,
            dynamic=dynamic
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError):
        fake.x = 20


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_dict_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={5: 1, 10: 2, 20: 3},
            map_values=True,
            dynamic=dynamic
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    fake.x = 20
    assert fake.read() == '3'


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_dict_str_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
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


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_process(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_range,
            values=[5e-3, 120e-3],
            get_process=lambda v: v * 1e-3,
            set_process=lambda v: v * 1e3,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = 10e-3
    assert fake.read() == '10'
    fake.x = 30e-3
    assert fake.x == 30e-3


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_get_process(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "JUNK%d", "",
            validator=strict_range,
            values=[0, 10],
            get_process=lambda v: int(v.replace('JUNK', '')),
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    fake.x = 5
    assert fake.x == 5


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_preprocess_reply_property(dynamic):
    # test setting preprocess_reply at property-level
    class Fake(FakeInstrument):
        x = Instrument.control(
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
    # called inside Adapter.values()
    fake.x = 5
    assert fake.x == 5
    fake.x = 5
    assert type(fake.x) == int


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_preprocess_reply_adapter(dynamic):
    # test setting preprocess_reply at Adapter-level
    class Fake(FakeInstrument):
        def __init__(self):
            super().__init__(preprocess_reply=lambda v: v.replace('JUNK', ''))

        x = Instrument.control(
            "", "JUNK%d", "",
            dynamic=dynamic,
            cast=int
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    # notice that read returns the full reply since preprocess_reply is only
    # called inside Adapter.values()
    fake.x = 5
    assert fake.x == 5


@pytest.mark.parametrize("dynamic", [False, True])
def test_measurement_dict_str_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.measurement(
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


@pytest.mark.parametrize("dynamic", [False, True])
def test_setting_process(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.setting(
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
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d,%d", "",
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = (5, 6)
    assert fake.read() == '5,6'


@pytest.mark.parametrize(
    'set_command, given, expected, dynamic',
    [("%d", 5, 5, False),
     ("%d", 5, 5, True),
     ("%d, %d", (5, 6), [5, 6], False),  # input has to be a tuple, not a list
     ("%d, %d", (5, 6), [5, 6], True),  # input has to be a tuple, not a list
     ])
def test_fakeinstrument_control(set_command, given, expected, dynamic):
    """FakeInstrument's custom simple control needs to process values correctly.
    """
    class Fake(FakeInstrument):
        x = FakeInstrument.control(
            "", set_command, "",
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = given
    assert fake.x == expected


def test_with_statement():
    """ Test the with-statement-behaviour of the instruments. """
    with FakeInstrument() as fake:
        # Check if fake is an instance of FakeInstrument
        assert isinstance(fake, FakeInstrument)

        # Check whether the shutdown function is already called
        assert fake.isShutdown is False

    # Check whether the shutdown function is called upon
    assert fake.isShutdown is True


class GenericInstrument(FakeInstrument):
    #  Use truncated_range as this easily lets us test for the range boundaries
    fake_ctrl = Instrument.control(
        "", "%d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_setting = Instrument.setting(
        "%d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_measurement = Instrument.measurement(
        "", "docs",
        values={'X': 1, 'Y': 2, 'Z': 3},
        map_values=True,
        dynamic=True,
    )


class ExtendedInstrument(GenericInstrument):
    # Keep values unchanged, just derive another instrument, e.g. to add more properties
    pass


class StrictExtendedInstrument(ExtendedInstrument):
    # Use strict instead of truncated range validator
    fake_ctrl_validator = strict_range
    fake_setting_validator = strict_range


class NewRangeInstrument(GenericInstrument):
    # Choose different properties' values, like you would for another device model
    fake_ctrl_values = (10, 20)
    fake_setting_values = (10, 20)
    fake_measurement_values = {'X': 4, 'Y': 5, 'Z': 6}


def test_dynamic_property_unchanged_by_inheritance():
    generic = GenericInstrument()
    extended = ExtendedInstrument()

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
    strict = StrictExtendedInstrument()

    with pytest.raises(ValueError):
        strict.fake_ctrl = 50
    with pytest.raises(ValueError):
        strict.fake_setting = 50


def test_dynamic_property_values_update_in_subclass():
    newrange = NewRangeInstrument()

    newrange.fake_ctrl = 50
    assert newrange.fake_ctrl == 20

    newrange.fake_setting = 50
    assert newrange.read() == '20'

    newrange.write('4')
    assert newrange.fake_measurement == 'X'


def test_dynamic_property_values_update_in_instance():
    generic = GenericInstrument()

    generic.fake_ctrl_values = (0, 33)
    generic.fake_ctrl = 50
    assert generic.fake_ctrl == 33

    generic.fake_setting_values = (0, 33)
    generic.fake_setting = 50
    assert generic.read() == '33'

    generic.fake_measurement_values = {'X': 7}
    generic.write('7')
    assert generic.fake_measurement == 'X'


def test_dynamic_property_values_update_in_one_instance_leaves_other_unchanged():
    generic1 = GenericInstrument()
    generic2 = GenericInstrument()

    generic1.fake_ctrl_values = (0, 33)
    generic1.fake_ctrl = 50
    generic2.fake_ctrl = 50
    assert generic1.fake_ctrl == 33
    assert generic2.fake_ctrl == 10


def test_dynamic_property_reading_special_attributes_forbidden():
    generic = GenericInstrument()
    with pytest.raises(AttributeError):
        generic.fake_ctrl_validator
