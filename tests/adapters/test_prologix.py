#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.adapters import PrologixAdapter
from pymeasure.test import expected_protocol


init_comm = [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None)]


def test_init():
    with expected_protocol(
            PrologixAdapter,
            init_comm,
    ):
        pass


def test_init_different_config():
    with expected_protocol(
            PrologixAdapter,
            [("++auto 1", None), ("++eoi 0", None), ("++eos 0", None)],
            auto=True, eoi=False, eos="\r\n",
    ):
        pass


@pytest.mark.parametrize("message, value", (("1", True), ("0", False)))
def test_auto(message, value):
    with expected_protocol(
            PrologixAdapter,
            init_comm + [("++auto", message)],
    ) as adapter:
        assert adapter.auto is value


def test_gpib_read_timeout():
    with expected_protocol(
            PrologixAdapter,
            init_comm + [
                ("++read_tmo_ms 700", None),
                ("++read_tmo_ms", 700)
            ],
    ) as adapter:
        adapter.gpib_read_timeout = 700
        assert adapter.gpib_read_timeout == 700


def test_write():
    with expected_protocol(
            PrologixAdapter,
            [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None),
             ("something", None)],
    ) as adapter:
        adapter.write("something")


def test_write_address():
    with expected_protocol(
            PrologixAdapter,
            [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None),
             ("++addr 5", None), ("something", None)],
            address=5,
    ) as adapter:
        adapter.write("something")


def test_read():
    with expected_protocol(
            PrologixAdapter,
            [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None),
             ("write", None), ("++read eoi", "response")],
    ) as adapter:
        adapter.write("write")
        assert adapter.read() == "response"


def test_write_bytes():
    with expected_protocol(
            PrologixAdapter,
            [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None),
             (b"something", None)],
    ) as adapter:
        adapter.write_bytes(b"something")


@pytest.mark.parametrize(
    "test_input,expected", [
        ([1, 2, 3], b'OUTP#13\x01\x02\x03\n'),
        ([43, 27, 10, 13, 97, 98, 99], b'OUTP#17\x1b\x2b\x1b\x1b\x1b\x0a\x1b\x0dabc\n'),
    ]
)
def test_write_binary_values(test_input, expected):
    with expected_protocol(
            PrologixAdapter,
            [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None),
             (expected, None)]
    ) as adapter:
        adapter.write_binary_values("OUTP", test_input, datatype='B')


def test_wait_for_srq():
    with expected_protocol(
            PrologixAdapter,
            [("++auto 0", None), ("++eoi 1", None), ("++eos 2", None),
             ("++srq", None), ("++read eoi", "0"), ("++srq", None), ("++read eoi", "1")]
    ) as adapter:
        adapter.wait_for_srq()
