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

import time
from unittest import mock

import pytest

from pymeasure.units import ureg
from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument
from pymeasure.instruments.instrument import DynamicProperty
from pymeasure.adapters import FakeAdapter, ProtocolAdapter
from pymeasure.instruments.fakes import FakeInstrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


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


@pytest.fixture()
def generic():
    return GenericInstrument()


class NewRangeInstrument(GenericInstrument):
    # Choose different properties' values, like you would for another device model
    fake_ctrl_values = (10, 20)
    fake_setting_values = (10, 20)
    fake_measurement_values = {'X': 4, 'Y': 5, 'Z': 6}


def test_fake_instrument():
    fake = FakeInstrument()
    fake.write("Testing")
    assert fake.read() == "Testing"
    assert fake.read() == ""
    assert fake.values("5") == [5]


@pytest.mark.parametrize("adapter", (("COM1", 87, "USB")))
def test_init_visa(adapter):
    Instrument(adapter, "def", visa_library="@sim")
    pass  # Test that no error is raised


@pytest.mark.xfail()  # I do not know, when this error is raised
def test_init_visa_fail():
    with pytest.raises(Exception, match="Invalid adapter"):
        Instrument("abc", "def", visa_library="@xyz")


def test_instrument_in_context():
    with Instrument("abc", "def", visa_library="@sim") as instr:
        pass
    assert instr.isShutdown is True


class TestInstrumentCommunication:
    @pytest.fixture()
    def instr(self):
        a = mock.MagicMock(return_value="5")
        return Instrument(a, "abc")

    def test_write(self, instr):
        instr.write("abc")
        assert instr.adapter.method_calls == [mock.call.write('abc')]

    def test_read(self, instr):
        instr.read()
        assert instr.adapter.method_calls == [mock.call.read()]

    def test_write_bytes(self, instr):
        instr.write_bytes(b"abc")
        assert instr.adapter.method_calls == [mock.call.write_bytes(b"abc")]

    def test_read_bytes(self, instr):
        instr.read_bytes(5)
        assert instr.adapter.method_calls == [mock.call.read_bytes(5)]

    def test_write_binary_values(self, instr):
        instr.write_binary_values("abc", [5, 6, 7])
        assert instr.adapter.method_calls == [mock.call.write_binary_values("abc", [5, 6, 7])]


class TestWaiting:
    @pytest.fixture()
    def instr(self):
        class Faked(Instrument):
            def wait_for(self, query_delay=0):
                self.waited = query_delay
        return Faked(ProtocolAdapter(), name="faked")

    def test_waiting(self):
        instr = Instrument(ProtocolAdapter(), "faked")
        stop = time.perf_counter() + 100
        instr.wait_for(0.1)
        assert time.perf_counter() < stop

    def test_ask_calls_wait(self, instr):
        instr.adapter.comm_pairs = [("abc", "resp")]
        instr.ask("abc")
        assert instr.waited == 0

    def test_ask_calls_wait_with_delay(self, instr):
        instr.adapter.comm_pairs = [("abc", "resp")]
        instr.ask("abc", query_delay=10)
        assert instr.waited == 10

    def test_binary_values_calls_wait(self, instr):
        instr.adapter.comm_pairs = [("abc", "abcdefgh")]
        instr.binary_values("abc")
        assert instr.waited == 0


@pytest.mark.parametrize("method, write, reply", (("id", "*IDN?", "xyz"),
                                                  ("complete", "*OPC?", "1"),
                                                  ("status", "*STB?", "189"),
                                                  ("options", "*OPT?", "a9"),
                                                  ))
def test_SCPI_properties(method, write, reply):
    with expected_protocol(
            Instrument,
            [(write, reply)],
            name="test") as instr:
        assert getattr(instr, method) == reply


@pytest.mark.parametrize("method, write", (("clear", "*CLS"),
                                           ("reset", "*RST")
                                           ))
def test_SCPI_write_commands(method, write):
    with expected_protocol(
            Instrument,
            [(write, None)],
            name="test") as instr:
        getattr(instr, method)()


def test_instrument_check_errors():
    with expected_protocol(
            Instrument,
            [("SYST:ERR?", "17,funny stuff"),
             ("SYST:ERR?", "0")],
            name="test") as instr:
        assert instr.check_errors() == [[17, "funny stuff"]]


@pytest.mark.parametrize("method", ("id", "complete", "status", "options",
                                    "clear", "reset", "check_errors"
                                    ))
def test_SCPI_false_raises_errors(method):
    with pytest.raises(NotImplementedError):
        getattr(Instrument(FakeAdapter(), "abc", includeSCPI=False), method)()


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
    instr = Instrument(FakeAdapter(), "test")
    assert instr.values(value, **kwargs) == result


# Testing Instrument.control
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


def test_control_check_errors_get(generic):
    generic.fake_ctrl_check_get_errors = True

    def checking():
        generic.error = True
    generic.check_errors = checking
    generic.fake_ctrl
    assert generic.error is True


def test_control_check_errors_set(generic):
    generic.fake_ctrl_check_set_errors = True

    def checking():
        generic.error = True
    generic.check_errors = checking
    generic.fake_ctrl = 7
    assert generic.error is True


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


def test_value_not_in_map(generic):
    generic.adapter._buffer = "123"
    with pytest.raises(KeyError, match="not found in mapped values"):
        generic.fake_measurement


def test_control_invalid_values_get():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            values=b"abasdfe", map_values=True)
    with pytest.raises(ValueError, match="Values of type"):
        Fake().x


def test_control_invalid_values_set():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            values=b"abasdfe", map_values=True)
    with pytest.raises(ValueError, match="Values of type"):
        Fake().x = 7


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
    # called inside Instrument.values()
    fake.x = 5
    assert fake.x == 5
    fake.x = 5
    assert type(fake.x) == int


@pytest.mark.parametrize("cast, expected", ((float, 5.5),
                                            (ureg.Quantity, ureg.Quantity(5.5)),
                                            (str, "5.5"),
                                            (lambda v: int(float(v)), 5)
                                            ))
def test_measurement_cast(cast, expected):
    class Fake(Instrument):
        x = Instrument.measurement(
            "x", "doc", cast=cast)
    with expected_protocol(Fake, [("x", "5.5")], name="test") as instr:
        assert instr.x == expected


def test_measurement_cast_int():
    class Fake(Instrument):
        def __init__(self, adapter, **kwargs):
            super().__init__(adapter, "test", **kwargs)
        x = Instrument.measurement(
            "x", "doc", cast=int)
    with expected_protocol(Fake, [("x", "5")]) as instr:
        y = instr.x
        assert y == 5
        assert type(y) is int


def test_measurement_unitful_property():
    class Fake(Instrument):
        def __init__(self, adapter, **kwargs):
            super().__init__(adapter, "test", **kwargs)
        x = Instrument.measurement(
            "x", "doc", get_process=lambda v: ureg.Quantity(v, ureg.m))
    with expected_protocol(Fake, [("x", "5.5")]) as instr:
        y = instr.x
        assert y.m_as(ureg.m) == 5.5


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


def test_measurement_set(generic):
    with pytest.raises(LookupError, match="Instrument property can not be set."):
        generic.fake_measurement = 7


def test_setting_get(generic):
    with pytest.raises(LookupError, match="Instrument property can not be read."):
        generic.fake_setting


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


def test_dynamic_property_fget_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="Unreadable attribute"):
        d.__get__(5)


def test_dynamic_property_fset_unset():
    d = DynamicProperty()
    with pytest.raises(AttributeError, match="set attribute"):
        d.__set__(5, 7)


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
