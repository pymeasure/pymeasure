#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
from unittest import mock

from pymeasure.adapters.fake_scpi import FakeScpiAdapter

class TestFakeScpiAdapter:
    def test_read_should_return_empty_string(self):
        a = FakeScpiAdapter()
        assert a.read() == ""

    def test_query_without_default_should_raise(self):
        a = FakeScpiAdapter()
        with pytest.raises(KeyError):
            a.write("ABCD?")

    def test_query_with_default_should_return_default(self):
        a = FakeScpiAdapter(default_value=8)
        assert a.ask("ABCD?") == "8\n"

    def test_preassigned_value(self):
        a = FakeScpiAdapter(default_value=8, QWER=3)
        assert a.ask("QWER?") == "3\n"

    def test_programmatic_set_value_should_return(self):
        a = FakeScpiAdapter(default_value=8)
        a.set_value('QWER', 10)
        assert a.ask("QWER?") == "10\n"

    def test_set_noargs_should_noop(self):
        a = FakeScpiAdapter()
        a.write('ABCD')
        assert a.read() == ""
        with pytest.raises(KeyError):
            a.write("ABCD?")

    def test_set_and_query_should_return(self):
        a = FakeScpiAdapter(default_value=8)
        a.write('QWER 5')
        assert a.ask("QWER?") == "5\n"

    def test_set_and_query_multiple_args(self):
        a = FakeScpiAdapter(default_value=8)
        a.write('ARRY 1,2,3,4')
        assert [x.strip() for x in a.ask("ARRY?").split(',')] == ["1", "2", "3", "4"]

    def test_set_arg_without_space(self): # regression test
        a = FakeScpiAdapter()
        a.write('BOOP66')
        assert a.ask('BOOP?') == '66\n'

    def test_query_partial_args(self):
        a = FakeScpiAdapter()
        a.write('MHMM 1,2,3')
        assert [x.strip() for x in a.ask("MHMM? 1").split(',')] == ["2", "3"]
        assert [x.strip() for x in a.ask("MHMM? 1,2").split(',')] == ["3"]
        with pytest.raises(KeyError):
            a.ask("MHMM? 3")

    def test_set_and_query_multiple_variables(self):
        a = FakeScpiAdapter()
        a.write('QWER 1')
        a.write('ASDF 2')
        assert a.ask('QWER?') == '1\n'
        assert a.ask('ASDF?') == '2\n'
        with pytest.raises(KeyError):
            a.ask('ZXCV?')

    def test_handler(self):
        a = FakeScpiAdapter()
        handler = mock.Mock(return_value="12")
        a.set_handler("BLAH", handler)
        assert a.ask("BLAH?") == "12\n"
        handler.assert_called_with(args=tuple(), query=True)

        handler.return_value = "42"
        assert a.ask("BLAH 1,2,3") == "42\n"
        handler.assert_called_with(args=(1, 2, 3), query=False)
