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

import logging
import serial

from pymeasure.adapters import SerialAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class TestSerialAdapter:
    def test_write(self):
        smock = mock.MagicMock(spec=serial.Serial)
        sa = SerialAdapter(smock)
        sa.write('ABCD?')
        smock.write.assert_called_once_with(b'ABCD?')


    @pytest.mark.parametrize("vset,vget", [
        (None, None), # None case
        ('\r', '\r'), # single char
        ('xa', 'xa'), # multichar
        (b'\r', '\r'), # byte should be converted to str
        ])
    def test_write_term_property_setter_getter(self, vset, vget):
        # write_term is a property, so test the set/get logic
        smock = mock.MagicMock(spec=serial.Serial)
        sa = SerialAdapter(smock)
        sa.write_term = vset
        assert sa.write_term == vget


    def test_write_with_term_None(self):
        smock = mock.MagicMock(spec=serial.Serial)
        sa = SerialAdapter(smock)
        sa.write_term = None
        sa.write('ABCD?')
        smock.write.assert_called_with(b'ABCD?')


    def test_write_with_term(self):
        smock = mock.MagicMock(spec=serial.Serial)
        sa = SerialAdapter(smock, write_term='\r')

        sa.write_term = '\r'
        sa.write('ABCD?')
        smock.write.assert_called_with(b'ABCD?\r')

        sa.write_term = ';\r'
        sa.write('ABCD?')
        smock.write.assert_called_with(b'ABCD?;\r')


    def test_read(self):
        smock = mock.MagicMock(spec=serial.Serial)
        smock.read.side_effect = [bytes([x]) for x in b"0.123456,0.987654\r1"]
        smock.readlines.return_value = [b"0.123456,0.987654", b"1"]
        sa = SerialAdapter(smock)

        assert sa.read() == "0.123456,0.987654\n1"


    @pytest.mark.parametrize("vset,vget", [
        (None, None), # None case
        (b't', b't'), # single character
        ('\r', b'\r'), # string converted to byte
        ])
    def test_write_term_property_setter_getter(self, vset, vget):
        # read_term is a property, so test the set/get logic
        smock = mock.MagicMock(spec=serial.Serial)
        sa = SerialAdapter(smock)
        sa.read_term = vset
        assert sa.read_term == vget


    def test_read_with_term_None(self):
        smock = mock.MagicMock(spec=serial.Serial)
        smock.read.side_effect = [bytes([x]) for x in b"0.123456,0.987654\r1"]
        smock.readlines.return_value = [b"0.123456,0.987654", b"1"]
        sa = SerialAdapter(smock)
        sa.read_term = None
        assert sa.read() == "0.123456,0.987654\n1"


    def test_read_with_term(self):
        smock = mock.MagicMock(spec=serial.Serial)
        smock.read.side_effect = [bytes([x]) for x in b"0.123456,0.987654\r1"]
        smock.readlines.return_value = [b"0.123456,0.987654", b"1"]
        sa = SerialAdapter(smock, read_term='\r')
        assert sa.read() == "0.123456,0.987654"
