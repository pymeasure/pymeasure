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

import io
import logging
import pytest

from pymeasure.adapters import ProtocolAdapter
from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.hcp import TC038, TC038D

from pymeasure.generator import (write_test, write_parametrized_test,
                                 write_parametrized_method_test,
                                 parse_stream, Generator, ByteStreamHandler)


class FakeChildChannel(Channel):

    channel_control = Channel.control("G{{ch}}.{ch}", "S{{ch}}{ch} %f",
                                      "Control something. (float)")


class FakeChannel(Channel):

    port = Channel.ChannelCreator(FakeChildChannel, id=1)

    channel_control = Channel.control("G{ch}", "S{ch} %f", "Control something. (float)")

    def funny_method(self, value=7):
        """Some method for testing purposes."""
        return float(self.ask("M{ch} " + str(value)))


class FakeTestInstrument(Instrument):

    ch_A = Instrument.ChannelCreator(FakeChannel, id="A")

    def __init__(self, adapter, name="Fake"):
        super().__init__(adapter, name)

    i_control = Instrument.control("G", "S %f", "Control instrument. (float)")


@pytest.fixture
def file():
    s = io.StringIO()
    yield s
    s.close()


class Test_write_test:
    def test_write(self, file):
        write_test(file, "init", "Super", [(b"sent", b"received")],
                   "pass  # Verify the expected communication.")
        assert file.getvalue() == """

def test_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received')],
    ):
        pass  # Verify the expected communication.
"""

    def test_write_multiple_comm_pairs(self, file):
        write_test(file, "init", "Super", [(b"sent", b"received"),
                                           (b"sent2", b'rec2')], "pass")
        assert file.getvalue() == """

def test_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received'),
             (b'sent2', b'rec2')],
    ):
        pass
"""

    def test_write_init_kwargs(self, file):
        write_test(file, "init", "Super", [(b"sent", b"received")],
                   "pass  # Verify the expected communication.",
                   {'address': 7, 'name': "my name", 'bool': True})
        assert file.getvalue() == """

def test_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received')],
            address=7,
            name='my name',
            bool=True,
    ):
        pass  # Verify the expected communication.
"""

    def test_write_bytes(self, file):
        write_test(file, "init", "Super",
                   [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
                   "del instr")
        assert file.getvalue() == r"""

def test_init():
    with expected_protocol(
            Super,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
    ) as inst:
        del instr
"""

    def test_write_replaces_period_with_underscore_in_name(self, file):
        write_test(file, "ch.init", "Super", [(b"sent", b"received")],
                   "pass  # Verify the expected communication.")
        assert file.getvalue() == """

def test_ch_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received')],
    ):
        pass  # Verify the expected communication.
"""


class Test_write_parametrized_test:
    def test_write(self, file):
        write_parametrized_test(file, "init", "Super", [[(b"sent", b"received")]], [None],
                                "assert inst.xyz == value")
        assert file.getvalue() == """

@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'sent', b'received')],
     None),
))
def test_init(comm_pairs, value):
    with expected_protocol(
            Super,
            comm_pairs,
    ) as inst:
        assert inst.xyz == value
"""

    def test_write_multiple_comm_pairs(self, file):
        write_parametrized_test(file, "init", "Super",
                                [[(b"sent", b"received"), (b"sent2", b'rec2')]], [None],
                                "pass")
        assert file.getvalue() == """

@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'sent', b'received'),
      (b'sent2', b'rec2')],
     None),
))
def test_init(comm_pairs, value):
    with expected_protocol(
            Super,
            comm_pairs,
    ):
        pass
"""

    def test_write_replaces_period_with_underscore_in_name(self, file):
        write_parametrized_test(file, "ch.init", "Super", [[(b"sent", b"received")]], [None],
                                "assert inst.xyz == value")
        assert file.getvalue() == """

@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'sent', b'received')],
     None),
))
def test_ch_init(comm_pairs, value):
    with expected_protocol(
            Super,
            comm_pairs,
    ) as inst:
        assert inst.xyz == value
"""


def test_write_parametrized_method(file):
    """Test also, that a period in the name is changed to underscore."""
    write_parametrized_method_test(file, "set_monitored.quantity", "TC038",
                                   [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
                                    [(b'\x0201010W0002\x03', b'\x020K\x03')]],
                                   [('temperature',), ()],
                                   [{}, {'quantity': 'temperature'}],
                                   [None, "'xyz'"],
                                   "assert inst.set_monitored_quantity(*args, **kwargs) == value"
                                   )
    assert file.getvalue() == r"""

@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
     ('temperature',), {}, None),
    ([(b'\x0201010W0002\x03', b'\x020K\x03')],
     (), {'quantity': 'temperature'}, 'xyz'),
))
def test_set_monitored_quantity(comm_pairs, args, kwargs, value):
    with expected_protocol(
            TC038,
            comm_pairs,
    ) as inst:
        assert inst.set_monitored_quantity(*args, **kwargs) == value
"""


class Test_parse_stream:
    @pytest.mark.parametrize(
        "text, comms", (
            (b"WRITE:abc\n", [(b"abc", None)]),
            (b"READ:def\n", [(None, b"def")]),
            (b"READ:a\nREAD:bc\n", [(None, b"abc")]),
            (b"WRITE:abc\nREAD:def\n", [(b"abc", b"def")]),
            (b"WRITE:abc\nREAD:d\nREAD:ef\n", [(b"abc", b"def")]),
            (b"WRITE:abc\nREAD:def\nWRITE:ghi\nREAD:jkl\n",
             [(b"abc", b"def"), (b"ghi", b"jkl")]),
            (b"WRITE:abc\nWRITE:def\n", [(b"abc", None), (b"def", None)]),
            (b"WRITE:\x03ab\x04\nREAD:super\x05\n",  # test for non ASCII byte values
             [(b'\x03ab\x04', b'super\x05')]),
            (b"WRITE:ho\n 9\nWRITE:\n hey\nREAD:7\n9\n",  # test for additional newline chars
             [(b"ho\n 9", None), (b"\n hey", b"7\n9")]),
        ))
    def test_parsing(self, text, comms):
        with io.BytesIO(text) as buf:
            assert parse_stream(buf) == comms


class Test_generator:
    @pytest.fixture
    def generator(self):
        generator = Generator()
        adapter = ProtocolAdapter(
            [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")])
        TC038.string_test = TC038.control("test?", "test %s",  # type: ignore
                                          "Control some string.", cast=str,  # type: ignore
                                          get_process=lambda v: v[7:-1])
        generator.instantiate(TC038, adapter, "hcp")
        return generator

    def test_instantiate(self, generator):
        assert generator._init_comm_pairs == [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")]

    def test_write_init_test(self, generator, file):
        generator.write_init_test(file)
        assert file.getvalue() == r"""import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.hcp import TC038


def test_init():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
    ):
        pass  # Verify the expected communication.
"""

    def test_instantiate_with_kwargs(self, file):
        generator = Generator()
        adapter = ProtocolAdapter(
            [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")])
        # add a control with a str for test purposes.
        TC038.string_test = TC038.control("test?", "test %s",  # type: ignore
                                          "Control some string.",  cast=str,  # type: ignore
                                          get_process=lambda v: v[7:-1])
        generator.instantiate(TC038, adapter, "hcp", some_kwarg=5.7, other_kwarg=True,
                              str_kwarg="abc")
        generator.write_init_test(file)
        assert file.getvalue() == r"""import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.hcp import TC038


def test_init():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
            some_kwarg=5.7,
            other_kwarg=True,
            str_kwarg='abc',
    ):
        pass  # Verify the expected communication.
"""

    def test_property(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")])
        assert generator.test_property_getter("temperature") == 20
        assert generator._getters == {'temperature': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')]],
            [20],
        )}

    def test_property_with_test_instrument(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")])
        assert generator.test_inst.temperature == 20
        assert generator._getters == {'temperature': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')]],
            [20],
        )}

    def test_property_string(self, generator):
        """Ensure that a returned string is encapsulated by single ticks."""
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010test?\x03", b"\x020101OKall fine\x03")])
        assert generator.test_property_getter("string_test") == "all fine"
        assert generator._getters == {'string_test': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b"\x0201010test?\x03", b"\x020101OKall fine\x03")]],
            ["'all fine'"],
        )}

    def test_write_getter_test(self, generator, file):
        generator.write_getter_test(file, 'temperature', (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')]],
            [20],
        ))
        assert file.getvalue() == r"""

def test_temperature_getter():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')],
    ) as inst:
        assert inst.temperature == 20
"""

    @pytest.mark.parametrize("value, test", (
        (None, "is None"),
        (True, "is True"),
        (False, "is False"),
        (7, "== 7"),
        (12.34, "== 12.34"),
    ))
    def test_write_getter_test_comparison(self, generator, file, value, test):
        """Test whether the comparison is changed to 'is', if the value is a boolean or None."""
        generator.write_getter_test(file, 'temperature', (
            [[]],
            [value],
        ))
        assert file.getvalue().endswith(test + "\n")

    def test_property_setter(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")])
        generator.test_property_setter("setpoint", 20)
        assert generator._setters == {'setpoint': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')]],
            [20],
        )}

    def test_property_setter_with_test_instrument(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")])
        generator.test_inst.setpoint = 20
        assert generator._setters == {'setpoint': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')]],
            [20],
        )}

    def test_property_setter_string(self, generator):
        """Ensure that a string value is encapsulated by single ticks."""
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010test xy\x03", b"\x020101OK\x03")])
        generator.test_property_setter("string_test", "xy")
        assert generator._setters == {'string_test': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010test xy\x03', None)]],
            ["'xy'"],
        )}

    def test_write_setter_test(self, generator, file):
        generator.write_setter_test(file, 'setpoint', (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')]],
            [20],
        ))
        assert file.getvalue() == r"""

def test_setpoint_setter():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')],
    ) as inst:
        inst.setpoint = 20
"""

    @pytest.mark.parametrize("args, kwargs", (
        (('temperature',), {}),
        ((), {'quantity': 'temperature'})
    ))
    def test_method_arg(self, generator, args, kwargs):
        generator.inst.adapter.comm_pairs.extend(
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')])
        generator.test_method("set_monitored_quantity", *args, **kwargs)
        assert generator._calls == {'set_monitored_quantity': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]],
            [args],
            [kwargs],
            [None],
        )}

    @pytest.mark.parametrize("args, kwargs", (
        (('temperature',), {}),
        ((), {'quantity': 'temperature'})
    ))
    def test_method_arg_with_test_instrument(self, generator, args, kwargs):
        generator.inst.adapter.comm_pairs.extend(
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')])
        generator.test_inst.set_monitored_quantity(*args, **kwargs)
        assert generator._calls == {'set_monitored_quantity': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]],
            [args],
            [kwargs],
            [None],
        )}

    @pytest.mark.parametrize("args, kwargs, value, test", (
        (('temperature',), {}, None, "(*('temperature',), ) is None"),
        (('temperature',), {}, True, "(*('temperature',), ) is True"),
        ((), {'quantity': 'temperature'}, 7, "(**{'quantity': 'temperature'}) == 7"),
        ((), {'quantity': 'temperature'}, False, "(**{'quantity': 'temperature'}) is False"),
    ))
    def test_write_method_single(self, generator, file, args, kwargs, value, test):
        generator.write_method_test(file, 'set_monitored_quantity', (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]],
            [args],
            [kwargs],
            [value],
        ))
        assert file.getvalue() == r"""

def test_set_monitored_quantity():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
    ) as inst:
        assert inst.set_monitored_quantity
"""[:-1] + test + "\n"

    def test_write_method_parametrized(self, generator, file):
        generator.write_method_test(file, 'set_monitored_quantity', (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
             [(b'\x0201010W0002\x03', b'\x020K\x03')]],
            [('temperature',), (), ],
            [{}, {'quantity': 'temperature'}],
            [None, 7],
        ))
        assert file.getvalue() == r"""

@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
     ('temperature',), {}, None),
    ([(b'\x0201010W0002\x03', b'\x020K\x03')],
     (), {'quantity': 'temperature'}, 7),
))
def test_set_monitored_quantity(comm_pairs, args, kwargs, value):
    with expected_protocol(
            TC038,
            comm_pairs,
    ) as inst:
        assert inst.set_monitored_quantity(*args, **kwargs) == value
"""

    def test_bytes_communication(self, file):
        generator = Generator()
        a = ProtocolAdapter([(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
                              b"\x01\x03\x04\x00\x00\x03\xE8\xFA\x8D")])
        a.log.addHandler(ByteStreamHandler(generator._stream))
        a.log.setLevel(logging.DEBUG)
        generator.inst = TC038D(a)
        generator._class = "TC038D"
        assert generator.test_property_getter("temperature") == 100
        assert generator._getters == {'temperature': (
            [[(b'\x01\x03\x00\x00\x00\x02\xc4\x0b', b'\x01\x03\x04\x00\x00\x03\xe8\xfa\x8d')]],
            [100.0],
        )}

    def test_write_bytes_communication(self, generator, file):
        generator._getters = {'temperature': (
            [[(b'\x01\x03\x00\x00\x00\x02\xc4\x0b', b'\x01\x03\x04\x00\x00\x03\xe8\xfa\x8d')]],
            [100.0],
        )}
        generator._class = "TC038D"
        generator.write_property_tests(file)
        assert file.getvalue() == r"""

def test_temperature_getter():
    with expected_protocol(
            TC038D,
            [(b'\x01\x03\x00\x00\x00\x02\xc4\x0b', b'\x01\x03\x04\x00\x00\x03\xe8\xfa\x8d')],
    ) as inst:
        assert inst.temperature == 100.0
"""

    @pytest.fixture
    def generator_multiple(self, generator):
        """Test an interweaved mix of getters and setters."""
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")])
        generator.test_property_setter("setpoint", 20)

        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")])
        assert generator.test_property_getter("temperature") == 20

        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WWRD0120,01,0258\x03", b"\x020101OK\x03")])
        generator.test_property_setter("setpoint", 60)

        generator.inst.adapter.comm_pairs.extend(
            [(b'\x0201010INF6\x03', b'\x020101OKUT150333 V01.R001111222233334444\x03')])
        assert generator.test_property_getter("information") == "UT150333 V01.R001111222233334444"

        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK0258\x03")])
        assert generator.test_property_getter("temperature") == 60

        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0120,01\x03", b"\x020101OK00C8\x03")])
        assert generator.test_property_getter("setpoint") == 20

        return generator

    def test_write_property_tests(self, generator_multiple, file):
        """Test that they are sorted alphabetically and collected in a single, parametrized test."""
        generator_multiple.write_property_tests(file)
        assert file.getvalue() == r"""

def test_information_getter():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010INF6\x03', b'\x020101OKUT150333 V01.R001111222233334444\x03')],
    ) as inst:
        assert inst.information == 'UT150333 V01.R001111222233334444'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
      (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')],
     20),
    ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
      (b'\x0201010WWRD0120,01,0258\x03', b'\x020101OK\x03')],
     60),
))
def test_setpoint_setter(comm_pairs, value):
    with expected_protocol(
            TC038,
            comm_pairs,
    ) as inst:
        inst.setpoint = value


def test_setpoint_getter():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0120,01\x03', b'\x020101OK00C8\x03')],
    ) as inst:
        assert inst.setpoint == 20.0


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
      (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')],
     20.0),
    ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
      (b'\x0201010WRDD0002,01\x03', b'\x020101OK0258\x03')],
     60.0),
))
def test_temperature_getter(comm_pairs, value):
    with expected_protocol(
            TC038,
            comm_pairs,
    ) as inst:
        assert inst.temperature == value
"""


class TestTestInstrument:
    @pytest.fixture(scope="function")
    def inst(self):
        generator = Generator()
        adapter = ProtocolAdapter()
        inst = generator.instantiate(FakeTestInstrument, adapter, "fake")
        return inst

    def test_channel_setter(self, inst):
        inst.adapter.comm_pairs.extend([("SA 15.000000", None)])
        inst.ch_A.channel_control = 15
        assert inst._generator._setters == {'ch_A.channel_control':
                                            ([[(b"SA 15.000000", None)]], [15])}

    def test_channel_getter(self, inst):
        inst.adapter.comm_pairs.extend([("GA", "123.5")])
        assert inst.ch_A.channel_control == 123.5
        assert inst._generator._getters == {'ch_A.channel_control':
                                            ([[(b"GA", b"123.5")]], [123.5])}

    def test_write_channel_getter_test(self, inst, file):
        """Importantly, this test checks also, that the test name does not contain a period."""
        inst.adapter.comm_pairs.extend([("GA", "123.5")])
        assert inst.ch_A.channel_control == 123.5
        inst._generator.write_property_tests(file)
        assert file.getvalue() == r"""

def test_ch_A_channel_control_getter():
    with expected_protocol(
            FakeTestInstrument,
            [(b'GA', b'123.5')],
    ) as inst:
        assert inst.ch_A.channel_control == 123.5
"""

    def test_channel_method(self, inst):
        inst.adapter.comm_pairs.extend([("MA 9", "11")])
        assert inst.ch_A.funny_method(9) == 11
        assert inst._generator._calls == {'ch_A.funny_method':
                                          ([[(b"MA 9", b"11")]], [(9,)], [{}], [11.])}

    def test_child_channel(self, inst):
        """Whether the child of a channel can be accessed as expected."""
        inst.adapter.comm_pairs.extend([("GA.1", "7")])
        assert inst.ch_A.port.channel_control == 7
        assert inst._generator._getters == {'ch_A.port.channel_control':
                                            ([[(b"GA.1", b"7")]], [7])}
