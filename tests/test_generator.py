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
from pymeasure.instruments.hcp import TC038, TC038D

from generator import (write_test, write_parametrized_test, write_parametrized_method_test,
                       parse_stream, Generator, ByteStreamHandler)


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


def test_write_method(file):
    write_parametrized_method_test(file, "set_monitored_quantity", "TC038",
                                   [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
                                    [(b'\x0201010W0002\x03', b'\x020K\x03')]],
                                   [('temperature',), ()],
                                   [{}, {'quantity': 'temperature'}],
                                   [None, 7],
                                   "assert inst.set_monitored_quantity(*args, **kwargs) == value"
                                   )
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
            (b"WRITE:\x03ab\x04\nREAD:super\x05\n",
             [(b'\x03ab\x04', b'super\x05')]),
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
        generator.instantiate(TC038, adapter, "hcp")
        return generator

    def test_instantiate(self, generator):
        assert generator._incomm == [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")]

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

    def test_property(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")])
        assert generator.test_property_getter("temperature") == 20
        assert generator._getters == {'temperature': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')]],
            [20],
        )}

    def test_write_getter_tests(self, generator, file):
        generator._getters = {'temperature': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')]],
            [20],
        )}
        generator.write_getter_tests(file)
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
    def test_write_getter_tests_comparison(self, generator, file, value, test):
        """Test whether the comparison is changed to 'is', if the value is a boolean or None."""
        generator._getters = {'temperature': (
            [[]],
            [value],
        )}
        generator.write_getter_tests(file)
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

    def test_write_setter_tests(self, generator, file):
        generator._setters = {'setpoint': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')]],
            [20],
        )}
        generator.write_setter_tests(file)
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

    @pytest.mark.parametrize("args, kwargs, value, test", (
        (('temperature',), {}, None, "(*('temperature',), ) is None"),
        (('temperature',), {}, True, "(*('temperature',), ) is True"),
        ((), {'quantity': 'temperature'}, 7, "(**{'quantity': 'temperature'}) == 7"),
        ((), {'quantity': 'temperature'}, False, "(**{'quantity': 'temperature'}) is False"),
    ))
    def test_write_methods_single(self, generator, file, args, kwargs, value, test):
        generator._calls = {'set_monitored_quantity': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]],
            [args],
            [kwargs],
            [value],
        )}
        generator.write_method_tests(file)
        assert file.getvalue() == r"""

def test_set_monitored_quantity():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
    ) as inst:
        assert inst.set_monitored_quantity
"""[:-1] + test + "\n"

    def test_write_methods_multiple(self, generator, file):
        generator._calls = {'set_monitored_quantity': (
            [[(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
             [(b'\x0201010W0002\x03', b'\x020K\x03')]],
            [('temperature',), (),],
            [{}, {'quantity': 'temperature'}],
            [None, 7],
        )}
        generator.write_method_tests(file)
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
        generator.write_getter_tests(file)
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
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK0258\x03")])
        assert generator.test_property_getter("temperature") == 60

        return generator

    def test_multiple_getter(self, generator_multiple, file):
        generator_multiple.write_getter_tests(file)
        assert file.getvalue() == r"""

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

    def test_multiple_setter(self, generator_multiple, file):
        generator_multiple.write_setter_tests(file)
        assert file.getvalue() == r"""

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
"""
