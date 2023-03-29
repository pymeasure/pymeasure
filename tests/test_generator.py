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

import io
import logging
import pytest

from pymeasure.adapters import ProtocolAdapter
from pymeasure.instruments.hcp import TC038, TC038D

from generator import write_test, parse_binary_string, parse_stream, Generator, ByteStreamHandler


class Test_write_test:
    @pytest.fixture
    def file(self):
        s = io.StringIO()
        yield s
        s.close()

    def test_write(self, file):
        write_test(file, "init", "Super", [(b"sent", b"received")], ["pass"])
        assert file.getvalue() == """

def test_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received')]
            ):
        pass  # Verify the expected communication.
"""

    def test_write_multiple_comm_pairs(self, file):
        write_test(file, "init", "Super", [(b"sent", b"received"),
                                           (b"sent2", b'rec2')], ["pass"])
        assert file.getvalue() == """

def test_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received'),
             (b'sent2', b'rec2')]
            ):
        pass  # Verify the expected communication.
"""

    def test_write_multiple_tests(self, file):
        write_test(file, "init", "Super", [(b"sent", b"received")],
                   ["inst.xy = 5", "assert inst.xy == 5"])
        assert file.getvalue() == """

def test_init():
    with expected_protocol(
            Super,
            [(b'sent', b'received')]
            ) as inst:
        inst.xy = 5
        assert inst.xy == 5
"""

    def test_write_bytes(self, file):
        write_test(file, "init", "Super",
                   [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
                   ["del instr"])
        assert file.getvalue() == r"""

def test_init():
    with expected_protocol(
            Super,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]
            ) as inst:
        del instr
"""


class Test_parse_bytes:
    @pytest.mark.parametrize(
        "text, bytedata", (
            ("b'ascii\tonly\ntsuper xy'", b'ascii\tonly\ntsuper xy'),
            ("b'abc\ts\\x15dfa\\x00'", b'abc\ts\x15dfa\x00'),
            (r'b"\x01\x10\x01\x0A\x00\x04\x08\x00"',
             b"\x01\x10\x01\x0A\x00\x04\x08\x00"),
        ))
    def test_parsing(self, text, bytedata):
        assert parse_binary_string(text) == bytedata


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
    def bare_generator(self):
        s = io.StringIO()
        yield Generator(s)
        s.close()

    @pytest.fixture
    def generator(self, bare_generator):
        adapter = ProtocolAdapter(
            [(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")])
        adapter.log.addHandler(ByteStreamHandler(bare_generator._stream))
        adapter.log.setLevel(logging.DEBUG)
        bare_generator.inst = TC038(adapter)
        bare_generator._class = "TC038"
        return bare_generator

    def test_instantiate(self, bare_generator):
        generator = bare_generator
        a = ProtocolAdapter([(b"\x0201010WRS01D0002\x03", b"\x020101OK\x03")])
        generator.instantiate(TC038, a, "hcp")
        assert generator._file.getvalue() == r"""from pymeasure.test import expected_protocol
from pymeasure.instruments.hcp import TC038


def test_init():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]
            ):
        pass  # Verify the expected communication.
"""

    def test_property(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WRDD0002,01\x03", b"\x020101OK00C8\x03")])
        assert generator.test_property("temperature") == 20
        assert generator._file.getvalue() == r"""

def test_temperature():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRDD0002,01\x03', b'\x020101OK00C8\x03')]
            ) as inst:
        assert inst.temperature == 20.0
"""

    def test_property_setter(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b"\x0201010WWRD0120,01,00C8\x03", b"\x020101OK\x03")])
        generator.test_property_setter("setpoint", 20)
        assert generator._file.getvalue() == r"""

def test_setpoint_setter():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')]
            ) as inst:
        inst.setpoint = 20
"""

    def test_method(self, generator):
        generator.inst.adapter.comm_pairs.extend(
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')])
        generator.test_method("set_monitored_quantity", "temperature")
        assert generator._file.getvalue() == r"""

def test_set_monitored_quantity():
    with expected_protocol(
            TC038,
            [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
             (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')]
            ) as inst:
        assert inst.set_monitored_quantity(*('temperature',), ) == None
"""

    def test_bytes(self, bare_generator):
        generator = bare_generator
        a = ProtocolAdapter([(b"\x01\x03\x00\x00\x00\x02\xC4\x0B",
                              b"\x01\x03\x04\x00\x00\x03\xE8\xFA\x8D")])
        a.log.addHandler(ByteStreamHandler(bare_generator._stream))
        a.log.setLevel(logging.DEBUG)
        bare_generator.inst = TC038D(a)
        bare_generator._class = "TC038D"
        assert generator.test_property("temperature") == 100
        assert generator._file.getvalue() == r"""

def test_temperature():
    with expected_protocol(
            TC038D,
            [(b'\x01\x03\x00\x00\x00\x02\xc4\x0b', b'\x01\x03\x04\x00\x00\x03\xe8\xfa\x8d')]
            ) as inst:
        assert inst.temperature == 100.0
"""
