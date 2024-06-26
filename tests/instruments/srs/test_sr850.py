#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments.srs.sr850 import SR850


def test_init():
    with expected_protocol(
            SR850,
            [],
    ):
        pass  # Verify the expected communication.


def test_channel1_setter():
    with expected_protocol(
            SR850,
            [(b'FOUT1,3', None)],
    ) as inst:
        inst.channel1 = 'Trace 1'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FOUT?1', b'0\n')],
     'X'),
    ([(b'FOUT?1', b'3\n')],
     'Trace 1'),
))
def test_channel1_getter(comm_pairs, value):
    with expected_protocol(
            SR850,
            comm_pairs,
    ) as inst:
        assert inst.channel1 == value


def test_channel2_setter():
    with expected_protocol(
            SR850,
            [(b'FOUT2,3', None)],
    ) as inst:
        inst.channel2 = 'Trace 1'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FOUT?2', b'2\n')],
     'Theta'),
    ([(b'FOUT?2', b'3\n')],
     'Trace 1'),
))
def test_channel2_getter(comm_pairs, value):
    with expected_protocol(
            SR850,
            comm_pairs,
    ) as inst:
        assert inst.channel2 == value


def test_id_getter():
    with expected_protocol(
            SR850,
            [(b'*IDN?', b'Stanford_Research_Systems,SR850,s/n26887,ver1.03 \n')],
    ) as inst:
        assert inst.id == 'Stanford_Research_Systems,SR850,s/n26887,ver1.03'


def test_input_gain_setter():
    with expected_protocol(
            SR850,
            [(b'IGAN 1', None)],
    ) as inst:
        inst.input_gain = '100 MOhm'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'IGAN?', b'0\n')],
     '1 MOhm'),
))
def test_input_gain_getter(comm_pairs, value):
    with expected_protocol(
            SR850,
            comm_pairs,
    ) as inst:
        assert inst.input_gain == value


def test_output_interface_getter():
    with expected_protocol(
            SR850,
            [(b'OUTX?', b'1\n')],
    ) as inst:
        assert inst.output_interface == 'GPIB'


def test_reference_source_setter():
    with expected_protocol(
            SR850,
            [(b'FMOD 0', None)],
    ) as inst:
        inst.reference_source = 'Internal'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FMOD?', b'2\n')],
     'External'),
    ([(b'FMOD?', b'0\n')],
     'Internal'),
))
def test_reference_source_getter(comm_pairs, value):
    with expected_protocol(
            SR850,
            comm_pairs,
    ) as inst:
        assert inst.reference_source == value


def test_snap():
    with expected_protocol(
            SR850,
            [(b'SNAP? 1,2,4,3,10', b'0,0,0,0,0\n')],
    ) as inst:
        assert inst.snap(*('x', 'y', 'theta', 'r', 'trace 1'), ) == [0.0, 0.0, 0.0, 0.0, 0.0]
